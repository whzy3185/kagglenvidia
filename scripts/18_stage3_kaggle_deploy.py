from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.provenance import ensure_dir, sha256_file, write_json  # noqa: E402
from nemotron086.reporting import markdown_table, write_text  # noqa: E402
from nemotron086.safety import redact_sensitive  # noqa: E402


USERNAME = "muelsyse111"
DATASET_SLUG = "nemotron-086plus-proxy-set"
KERNEL_SLUG = "nemotron-0-86-proxy-eval"
ADAPTER_MODEL_SOURCE = "huikang/nemotron-adapter/Transformers/default/27"
BASE_MODEL_CANDIDATE = "metric/nemotron-3-nano-30b-a3b-bf16"
BASE_MODEL_SOURCE = "metric/nemotron-3-nano-30b-a3b-bf16/transformers/default/1"
PROXY_SOURCE_DIR = PROJECT_ROOT / "eval" / "proxy_set"
DATASET_DIR = PROJECT_ROOT / "artifacts" / "stage3" / "kaggle_proxy_set_dataset"
KERNEL_DIR = PROJECT_ROOT / "kernels" / "proxy_eval_kernel"
REPORT_PATH = PROJECT_ROOT / "reports" / "STAGE3_KAGGLE_DEPLOYMENT.md"
MANIFEST_PATH = PROJECT_ROOT / "artifacts" / "stage3" / "kaggle_deployment_manifest.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--create-dataset", action="store_true")
    parser.add_argument("--push-kernel", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--kernel-timeout", type=int, default=7200)
    parser.add_argument("--accelerator", default="gpu")
    args = parser.parse_args()

    dataset_manifest = prepare_dataset_dir()
    kernel_manifest = prepare_kernel_files()
    actions: list[dict[str, Any]] = []
    if args.create_dataset:
        actions.append(run_guarded(args.yes, "create_dataset", ["kaggle", "datasets", "create", "-p", str(DATASET_DIR), "-r", "skip"]))
    if args.push_kernel:
        actions.append(
            run_guarded(
                args.yes,
                "push_kernel",
                [
                    "kaggle",
                    "kernels",
                    "push",
                    "-p",
                    str(KERNEL_DIR),
                    "-t",
                    str(args.kernel_timeout),
                    "--accelerator",
                    args.accelerator,
                ],
            )
        )

    payload = {
        "stage": 3,
        "status": "prepared",
        "username": USERNAME,
        "dataset_ref": f"{USERNAME}/{DATASET_SLUG}",
        "kernel_ref": f"{USERNAME}/{KERNEL_SLUG}",
        "adapter_model_source": ADAPTER_MODEL_SOURCE,
        "base_model_candidate": BASE_MODEL_CANDIDATE,
        "base_model_source": BASE_MODEL_SOURCE,
        "dataset_manifest": dataset_manifest,
        "kernel_manifest": kernel_manifest,
        "actions": actions,
        "no_local_base_model_loading": True,
        "no_training": True,
        "no_submission": True,
        "next_action": build_next_action(actions),
    }
    write_json(MANIFEST_PATH, payload)
    write_text(REPORT_PATH, render_report(payload))
    print(f"report: {REPORT_PATH.relative_to(PROJECT_ROOT).as_posix()}")
    print(f"dataset_ref: {payload['dataset_ref']}")
    print(f"kernel_ref: {payload['kernel_ref']}")
    print(f"NEXT_ACTION: {payload['next_action']['action']}")
    return 0 if all(action.get("ok", True) for action in actions) else 4


def prepare_dataset_dir() -> dict[str, Any]:
    ensure_dir(DATASET_DIR)
    files = []
    for source in sorted(PROXY_SOURCE_DIR.glob("*.jsonl")):
        target = DATASET_DIR / source.name
        shutil.copy2(source, target)
        files.append(
            {
                "path": target.relative_to(PROJECT_ROOT).as_posix(),
                "sha256": sha256_file(target),
                "size": target.stat().st_size,
            }
        )
    metadata = {
        "title": "Nemotron 0.86 Plus Proxy Set",
        "id": f"{USERNAME}/{DATASET_SLUG}",
        "licenses": [{"name": "CC0-1.0"}],
    }
    (DATASET_DIR / "dataset-metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "dir": DATASET_DIR.relative_to(PROJECT_ROOT).as_posix(),
        "metadata": (DATASET_DIR / "dataset-metadata.json").relative_to(PROJECT_ROOT).as_posix(),
        "files": files,
        "file_count": len(files),
    }


def prepare_kernel_files() -> dict[str, Any]:
    config = {
        "enable_proxy_inference": True,
        "proxy_set_dir": "",
        "adapter_dir": "",
        "base_model": "nvidia/NVIDIA-Nemotron-3-Nano-30B-v2",
        "notes": "Kernel auto-detects proxy JSONL, adapter files, and a mounted base-model directory under /kaggle/input when available.",
    }
    (KERNEL_DIR / "proxy_eval_kernel_config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    metadata = {
        "id": f"{USERNAME}/{KERNEL_SLUG}",
        "title": "Nemotron 0.86+ Proxy Eval",
        "code_file": "eval_candidate.py",
        "language": "python",
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": True,
        "enable_internet": True,
        "dataset_sources": [f"{USERNAME}/{DATASET_SLUG}"],
        "model_sources": [ADAPTER_MODEL_SOURCE, BASE_MODEL_SOURCE],
        "competition_sources": ["nvidia-nemotron-model-reasoning-challenge"],
    }
    (KERNEL_DIR / "kernel-metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "dir": KERNEL_DIR.relative_to(PROJECT_ROOT).as_posix(),
        "metadata": (KERNEL_DIR / "kernel-metadata.json").relative_to(PROJECT_ROOT).as_posix(),
        "config": (KERNEL_DIR / "proxy_eval_kernel_config.json").relative_to(PROJECT_ROOT).as_posix(),
        "dataset_sources": metadata["dataset_sources"],
        "model_sources": metadata["model_sources"],
        "base_model_candidate": BASE_MODEL_CANDIDATE,
        "base_model_source": BASE_MODEL_SOURCE,
        "base_model_source_status": "attached_in_kernel_metadata",
    }


def run_guarded(yes: bool, name: str, command: list[str]) -> dict[str, Any]:
    if not yes:
        return {"name": name, "ok": False, "status": "dry_run_requires_yes", "command": command}
    completed = subprocess.run(command, cwd=str(PROJECT_ROOT), text=True, capture_output=True, timeout=7200)
    log_path = PROJECT_ROOT / "logs" / f"stage3_{name}.log"
    log_path.write_text(redact_sensitive(completed.stdout + completed.stderr), encoding="utf-8")
    return {
        "name": name,
        "ok": completed.returncode == 0,
        "status": "success" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "command": command,
        "log_path": log_path.relative_to(PROJECT_ROOT).as_posix(),
        "stdout_head": redact_sensitive("\n".join(completed.stdout.splitlines()[:20])),
        "stderr_head": redact_sensitive("\n".join(completed.stderr.splitlines()[:20])),
    }


def build_next_action(actions: list[dict[str, Any]]) -> dict[str, str]:
    failed = [action for action in actions if not action.get("ok", False)]
    if failed:
        return {
            "status": "stay_stage3",
            "action": "review reports/STAGE3_KAGGLE_DEPLOYMENT.md and fix failed Kaggle deployment action",
            "reason": "Stage 3 proxy predictions require a successful Kaggle GPU kernel run.",
        }
    if actions:
        return {
            "status": "stay_stage3",
            "action": "wait for Kaggle kernel completion, then download proxy_predictions.jsonl",
            "reason": "Proxy eval cannot complete until the Kaggle kernel output is available locally.",
        }
    return {
        "status": "stay_stage3",
        "action": "create the private proxy dataset and push the proxy eval kernel after the active submit retry finishes",
        "reason": "Deployment files are prepared, but no Kaggle deployment action was requested.",
    }


def render_report(payload: dict[str, Any]) -> str:
    dataset_rows = [
        [item["path"], item["size"], item["sha256"]]
        for item in payload["dataset_manifest"]["files"]
    ]
    actions = payload["actions"] or []
    action_rows = [
        [action["name"], action["status"], action.get("returncode"), action.get("log_path"), action.get("stderr_head")]
        for action in actions
    ]
    action_table = markdown_table(["name", "status", "returncode", "log_path", "stderr_head"], action_rows) if action_rows else "- null"
    next_action = payload["next_action"]
    return f"""# Stage 3 Kaggle Deployment

This prepares the Kaggle-side proxy eval deployment. It does not train locally, submit a competition file, or load a base model locally.

- dataset_ref: `{payload['dataset_ref']}`
- kernel_ref: `{payload['kernel_ref']}`
- adapter_model_source: `{payload['adapter_model_source']}`
- base_model_candidate: `{payload['base_model_candidate']}`
- base_model_source: `{payload['base_model_source']}`
- base_model_source_status: {payload['kernel_manifest']['base_model_source_status']}
- no_local_base_model_loading: true
- no_training: true
- no_submission: true
- enable_internet: true

## Proxy Dataset Files

{markdown_table(['path', 'size', 'sha256'], dataset_rows)}

## Kernel Inputs

- dataset_sources: `{payload['kernel_manifest']['dataset_sources']}`
- model_sources: `{payload['kernel_manifest']['model_sources']}`
- kernel_metadata: `{payload['kernel_manifest']['metadata']}`
- kernel_config: `{payload['kernel_manifest']['config']}`

## Kaggle Actions

{action_table}

## Caveat

The adapter model source and base model source are attached in kernel metadata. The kernel still auto-detects mounted paths under `/kaggle/input` because Kaggle input mount names can vary.

NEXT_ACTION:
  status: {next_action['status']}
  action: "{next_action['action']}"
  reason: "{next_action['reason']}"
"""


if __name__ == "__main__":
    raise SystemExit(main())
