from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.provenance import ensure_dir, write_json  # noqa: E402
from nemotron086.reporting import write_text  # noqa: E402
from nemotron086.safety import redact_sensitive  # noqa: E402
from nemotron086.stage3_prediction_ingest import ingest_predictions  # noqa: E402


DEFAULT_KERNEL_REF = "muelsyse111/nemotron-0-86-proxy-eval"
OUTPUT_DIR = PROJECT_ROOT / "artifacts" / "stage3" / "kaggle_proxy_kernel_output"
PREDICTIONS_PATH = PROJECT_ROOT / "artifacts" / "stage3" / "proxy_predictions.jsonl"
REPORT_PATH = PROJECT_ROOT / "reports" / "STAGE3_PROXY_OUTPUT_FETCH.md"
MANIFEST_PATH = PROJECT_ROOT / "artifacts" / "stage3" / "proxy_output_fetch_manifest.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kernel-ref", default=DEFAULT_KERNEL_REF)
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args()

    status = run_command(["kaggle", "kernels", "status", args.kernel_ref])
    files = run_command(["kaggle", "kernels", "files", args.kernel_ref])
    output = {"ok": False, "status": "dry_run_requires_yes"}
    copied = False
    ingest_payload: dict[str, Any] | None = None

    if args.yes:
        if OUTPUT_DIR.exists():
            shutil.rmtree(OUTPUT_DIR)
        ensure_dir(OUTPUT_DIR)
        output = run_command(["kaggle", "kernels", "output", args.kernel_ref, "-p", str(OUTPUT_DIR)])
        candidate = OUTPUT_DIR / "proxy_predictions.jsonl"
        if candidate.exists():
            shutil.copy2(candidate, PREDICTIONS_PATH)
            copied = True
            ingest_payload = ingest_predictions(
                PROJECT_ROOT,
                PROJECT_ROOT / "eval" / "proxy_set",
                PREDICTIONS_PATH,
                PROJECT_ROOT / "artifacts" / "stage2" / "tong_full_repro" / "stage2_manifest.json",
            )

    payload = {
        "stage": 3,
        "kernel_ref": args.kernel_ref,
        "status_command": status,
        "files_command": files,
        "output_command": output,
        "output_dir": OUTPUT_DIR.relative_to(PROJECT_ROOT).as_posix(),
        "downloaded_files": list_downloaded_files(),
        "predictions_copied": copied,
        "predictions_path": PREDICTIONS_PATH.relative_to(PROJECT_ROOT).as_posix(),
        "ingest_payload": ingest_payload,
        "next_action": build_next_action(copied, ingest_payload),
    }
    write_json(MANIFEST_PATH, payload)
    write_text(REPORT_PATH, render_report(payload))
    print(f"report: {REPORT_PATH.relative_to(PROJECT_ROOT).as_posix()}")
    print(f"predictions_copied: {copied}")
    print(f"NEXT_ACTION: {payload['next_action']['action']}")
    return 0 if copied and ingest_payload and ingest_payload.get("can_evaluate") else 5


def run_command(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=str(PROJECT_ROOT), text=True, capture_output=True, timeout=600)
    return {
        "command": command,
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": redact_sensitive(completed.stdout),
        "stderr": redact_sensitive(completed.stderr),
    }


def build_next_action(copied: bool, ingest_payload: dict[str, Any] | None) -> dict[str, str]:
    if copied and ingest_payload and ingest_payload.get("can_evaluate"):
        return {
            "status": "enter_stage4_readiness_check",
            "action": "python scripts/14_stage4_readiness.py && python scripts/17_stage4_candidate_plan.py",
            "reason": "Proxy predictions were downloaded and ingested successfully.",
        }
    return {
        "status": "stay_stage3",
        "action": "wait for the Kaggle proxy eval kernel to finish, then rerun this fetch script with --yes",
        "reason": "Stage 3 needs proxy_predictions.jsonl before it can complete.",
    }


def render_report(payload: dict[str, Any]) -> str:
    next_action = payload["next_action"]
    downloaded = "\n".join(f"- {item['name']} ({item['size']} bytes)" for item in payload.get("downloaded_files", [])) or "- null"
    return f"""# Stage 3 Proxy Output Fetch

- kernel_ref: `{payload['kernel_ref']}`
- status_ok: {payload['status_command']['ok']}
- files_ok: {payload['files_command']['ok']}
- output_ok: {payload['output_command'].get('ok')}
- output_dir: `{payload['output_dir']}`
- predictions_copied: {payload['predictions_copied']}
- predictions_path: `{payload['predictions_path']}`

## Downloaded Files

{downloaded}

## Kernel Status Stdout

```text
{payload['status_command']['stdout'] or 'null'}
```

## Kernel Files Stdout

```text
{payload['files_command']['stdout'] or 'null'}
```

## Output Command Stderr

```text
{payload['output_command'].get('stderr') or 'null'}
```

NEXT_ACTION:
  status: {next_action['status']}
  action: "{next_action['action']}"
  reason: "{next_action['reason']}"
"""


def list_downloaded_files() -> list[dict[str, Any]]:
    if not OUTPUT_DIR.exists():
        return []
    return [
        {"name": item.name, "size": item.stat().st_size}
        for item in sorted(OUTPUT_DIR.iterdir())
        if item.is_file()
    ]


if __name__ == "__main__":
    raise SystemExit(main())
