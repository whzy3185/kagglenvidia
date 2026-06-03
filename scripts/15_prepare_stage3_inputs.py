from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.provenance import ensure_dir, read_json, write_json  # noqa: E402
from nemotron086.proxy_eval import load_proxy_set  # noqa: E402
from nemotron086.reporting import markdown_table, write_text  # noqa: E402


ROUTE = "tong_full_repro"
STAGE2_MANIFEST = PROJECT_ROOT / "artifacts" / "stage2" / ROUTE / "stage2_manifest.json"
VALIDATION_REPORT = PROJECT_ROOT / "artifacts" / "stage2" / ROUTE / "validation" / "validate_report.json"
PACK_MANIFEST = PROJECT_ROOT / "artifacts" / "stage2" / ROUTE / "submission" / "manifest.json"
ADAPTER_DIR = PROJECT_ROOT / "artifacts" / "stage2" / ROUTE / "adapter"
SUBMISSION_ZIP = PROJECT_ROOT / "artifacts" / "stage2" / ROUTE / "submission" / "submission.zip"
PROXY_SET_DIR = PROJECT_ROOT / "eval" / "proxy_set"
STAGE3_DIR = PROJECT_ROOT / "artifacts" / "stage3"
PROXY_SET_ZIP = STAGE3_DIR / "proxy_set.zip"
MODEL_METADATA = STAGE3_DIR / "tong_model_metadata" / "model-metadata.json"
INSTANCE_METADATA = STAGE3_DIR / "tong_model_instance_metadata" / "model-instance-metadata.json"
RUN_CONFIG = PROJECT_ROOT / "configs" / "stage3_proxy_eval_run.yaml"
INPUT_MANIFEST = STAGE3_DIR / "proxy_eval_inputs_manifest.json"
LICENSE_REVIEW = PROJECT_ROOT / "reports" / "LICENSE_REVIEW_TONG_ADAPTER.md"
GPU_BUNDLE_REPORT = PROJECT_ROOT / "reports" / "STAGE3_GPU_INPUT_BUNDLE.md"


def main() -> int:
    ensure_dir(STAGE3_DIR)
    stage2 = read_json(STAGE2_MANIFEST)
    validation = read_json(VALIDATION_REPORT)
    pack_manifest = read_json(PACK_MANIFEST)
    model_metadata = read_optional_json(MODEL_METADATA)
    instance_metadata = read_optional_json(INSTANCE_METADATA)

    samples, issues = load_proxy_set(PROXY_SET_DIR)
    proxy_files = sorted(PROXY_SET_DIR.glob("*.jsonl"))
    write_proxy_zip(proxy_files, PROXY_SET_ZIP)

    license_name = instance_metadata.get("licenseName") or "unknown"
    license_status = license_name if license_name != "unknown" else "unknown"
    if license_status != "unknown":
        stage2["license_status"] = license_status
        provenance = stage2.setdefault("provenance", {})
        provenance["license_status"] = license_status
        provenance["license_review_status"] = "reviewed_from_kaggle_model_instance_metadata"
        provenance["license_source"] = relative(INSTANCE_METADATA)
        provenance["license_name"] = license_name
        provenance["allowed_use_before_submission"] = "structural_validation_packaging_and_proxy_eval_staging"
        provenance["submission_requires_final_manual_compliance_review"] = True
        write_json(STAGE2_MANIFEST, stage2)

    manifest = build_input_manifest(
        samples=samples,
        issues=issues,
        proxy_files=proxy_files,
        validation=validation,
        pack_manifest=pack_manifest,
        stage2=stage2,
        model_metadata=model_metadata,
        instance_metadata=instance_metadata,
        license_status=license_status,
    )
    write_json(INPUT_MANIFEST, manifest)
    write_text(RUN_CONFIG, render_run_config(manifest))
    write_text(LICENSE_REVIEW, render_license_review(manifest))
    write_text(GPU_BUNDLE_REPORT, render_gpu_bundle(manifest))

    print(f"config: {relative(RUN_CONFIG)}")
    print(f"manifest: {relative(INPUT_MANIFEST)}")
    print(f"license_review: {relative(LICENSE_REVIEW)}")
    print(f"gpu_bundle_report: {relative(GPU_BUNDLE_REPORT)}")
    print(f"license_status: {license_status}")
    print(f"proxy_samples: {len(samples)}")
    return 0 if not issues else 3


def read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return read_json(path)


def write_proxy_zip(proxy_files: list[Path], output_path: Path) -> None:
    ensure_dir(output_path.parent)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in proxy_files:
            archive.write(path, arcname=path.name)


def build_input_manifest(
    *,
    samples: list[dict[str, Any]],
    issues: list[str],
    proxy_files: list[Path],
    validation: dict[str, Any],
    pack_manifest: dict[str, Any],
    stage2: dict[str, Any],
    model_metadata: dict[str, Any],
    instance_metadata: dict[str, Any],
    license_status: str,
) -> dict[str, Any]:
    categories = Counter(str(row.get("category", "unknown")) for row in samples)
    adapter_files = validation.get("files", {})
    return {
        "stage": 3,
        "route": ROUTE,
        "status": "ready_for_kaggle_gpu_predictions" if not issues else "proxy_set_has_issues",
        "no_training_local": True,
        "no_submission": True,
        "no_local_base_model_loading": True,
        "proxy_set": {
            "dir": relative(PROXY_SET_DIR),
            "zip_path": relative(PROXY_SET_ZIP),
            "zip_sha256": sha256_file(PROXY_SET_ZIP) if PROXY_SET_ZIP.exists() else None,
            "sample_count": len(samples),
            "category_counts": dict(sorted(categories.items())),
            "files": [
                {
                    "path": relative(path),
                    "sha256": sha256_file(path),
                    "size": path.stat().st_size,
                }
                for path in proxy_files
            ],
            "issues": issues,
        },
        "candidate_adapter": {
            "source_url": stage2.get("source_url"),
            "model_version_ref": stage2.get("model_version_ref"),
            "adapter_dir": relative(ADAPTER_DIR),
            "adapter_config_exists": (ADAPTER_DIR / "adapter_config.json").exists(),
            "adapter_model_exists": (ADAPTER_DIR / "adapter_model.safetensors").exists(),
            "adapter_config_sha256": adapter_files.get("adapter_config.json", {}).get("sha256"),
            "adapter_model_sha256": adapter_files.get("adapter_model.safetensors", {}).get("sha256"),
            "rank_lte_32": validation.get("rank_lte_32"),
            "safetensors_opened": validation.get("safetensors_opened"),
            "structural_valid": validation.get("structural_valid"),
            "submission_zip_path": relative(SUBMISSION_ZIP),
            "submission_zip_sha256": pack_manifest.get("sha256"),
            "official_format_confirmed": stage2.get("official_format_confirmed", False),
            "official_score_verified_locally": False,
        },
        "license_review": {
            "status": license_status,
            "source": relative(INSTANCE_METADATA) if INSTANCE_METADATA.exists() else None,
            "model_metadata_path": relative(MODEL_METADATA) if MODEL_METADATA.exists() else None,
            "instance_metadata_path": relative(INSTANCE_METADATA) if INSTANCE_METADATA.exists() else None,
            "model_is_private": model_metadata.get("isPrivate"),
            "license_name": instance_metadata.get("licenseName"),
            "usage": instance_metadata.get("usage", ""),
            "overview": instance_metadata.get("overview", ""),
            "training_data": instance_metadata.get("trainingData", []),
            "submission_requires_final_manual_compliance_review": True,
        },
        "kaggle_gpu_run": {
            "kernel_dir": "kernels/proxy_eval_kernel",
            "kernel_code": "kernels/proxy_eval_kernel/eval_candidate.py",
            "enable_inference_env": "ENABLE_PROXY_INFERENCE=1",
            "required_env": {
                "ENABLE_PROXY_INFERENCE": "1",
                "PROXY_SET_DIR": "/kaggle/input/<proxy-set-input-dir>",
                "ADAPTER_DIR": "/kaggle/input/<adapter-input-dir-containing-adapter-files>",
                "BASE_MODEL": "nvidia/NVIDIA-Nemotron-3-Nano-30B-v2",
            },
            "expected_outputs": [
                "proxy_predictions.jsonl",
                "proxy_eval_kernel_report.json",
            ],
        },
        "next_action": {
            "status": "stay_stage3",
            "action": "run the staged proxy eval kernel on Kaggle GPU, bring back proxy_predictions.jsonl, then run the ingest script",
            "reason": "Stage 4 remains blocked until proxy predictions are evaluated locally.",
        },
    }


def render_run_config(manifest: dict[str, Any]) -> str:
    license_review = manifest["license_review"]
    proxy_set = manifest["proxy_set"]
    adapter = manifest["candidate_adapter"]
    return f"""stage: 3
route: {ROUTE}
status: {manifest['status']}
no_training_local: true
no_submission: true
no_local_base_model_loading: true

candidate_adapter:
  source_url: {adapter['source_url']}
  model_version_ref: {adapter['model_version_ref']}
  adapter_dir: {adapter['adapter_dir']}
  submission_zip_path: {adapter['submission_zip_path']}
  structural_valid: {str(adapter['structural_valid']).lower()}
  rank_lte_32: {str(adapter['rank_lte_32']).lower()}
  safetensors_opened: {str(adapter['safetensors_opened']).lower()}
  official_format_confirmed: {str(adapter['official_format_confirmed']).lower()}
  official_score_verified_locally: false

license_review:
  status: {license_review['status']}
  license_name: {license_review['license_name']}
  source: {license_review['source']}
  submission_requires_final_manual_compliance_review: true

proxy_set:
  dir: {proxy_set['dir']}
  zip_path: {proxy_set['zip_path']}
  sample_count: {proxy_set['sample_count']}

kaggle_gpu_env:
  ENABLE_PROXY_INFERENCE: "1"
  PROXY_SET_DIR: "/kaggle/input/<proxy-set-input-dir>"
  ADAPTER_DIR: "/kaggle/input/<adapter-input-dir-containing-adapter-files>"
  BASE_MODEL: "nvidia/NVIDIA-Nemotron-3-Nano-30B-v2"

expected_outputs:
  - proxy_predictions.jsonl
  - proxy_eval_kernel_report.json

post_gpu_local_command: "python scripts/16_stage3_ingest_predictions.py --predictions artifacts/stage3/proxy_predictions.jsonl"
"""


def render_license_review(manifest: dict[str, Any]) -> str:
    license_review = manifest["license_review"]
    adapter = manifest["candidate_adapter"]
    rows = [
        ["source_url", adapter["source_url"]],
        ["model_version_ref", adapter["model_version_ref"]],
        ["model_is_private", license_review["model_is_private"]],
        ["license_name", license_review["license_name"]],
        ["metadata_source", license_review["source"]],
        ["usage_text_present", bool(license_review["usage"])],
        ["overview_text_present", bool(license_review["overview"])],
        ["training_data_entries", len(license_review["training_data"])],
    ]
    return f"""# License Review: Tong Adapter

This review is based on Kaggle CLI model-instance metadata only. It is not a legal opinion and does not confirm an official Kaggle score.

{markdown_table(['field', 'value'], rows)}

## Decision

- license_status: {license_review['status']}
- provenance_status: metadata_reviewed
- allowed_current_use: structural validation, packaging, and proxy-eval staging
- still_required_before_submission: final manual compliance review and score-gate review
- official_format_confirmed: {str(adapter['official_format_confirmed']).lower()}
- official_score_verified_locally: false
"""


def render_gpu_bundle(manifest: dict[str, Any]) -> str:
    proxy_set = manifest["proxy_set"]
    adapter = manifest["candidate_adapter"]
    category_rows = [[category, count] for category, count in proxy_set["category_counts"].items()]
    issues_text = "\n".join(f"- {issue}" for issue in proxy_set["issues"]) if proxy_set["issues"] else "- null"
    return f"""# Stage 3 GPU Input Bundle

This bundle stages proxy evaluation only. It does not train, submit, or run local base-model inference.

## Local Inputs

- proxy_set_dir: `{proxy_set['dir']}`
- proxy_set_zip: `{proxy_set['zip_path']}`
- proxy_set_zip_sha256: `{proxy_set['zip_sha256']}`
- sample_count: {proxy_set['sample_count']}
- adapter_dir: `{adapter['adapter_dir']}`
- submission_zip_path: `{adapter['submission_zip_path']}`
- submission_zip_sha256: `{adapter['submission_zip_sha256']}`
- structural_valid: {adapter['structural_valid']}
- rank_lte_32: {adapter['rank_lte_32']}
- safetensors_opened: {adapter['safetensors_opened']}
- official_format_confirmed: {adapter['official_format_confirmed']}

## Category Coverage

{markdown_table(['category', 'samples'], category_rows)}

## Dataset Issues

{issues_text}

## Kaggle GPU Run

Use `kernels/proxy_eval_kernel/eval_candidate.py` only in an approved Kaggle GPU environment after manually attaching the proxy set input and an adapter input directory containing `adapter_config.json` and `adapter_model.safetensors`.

Required environment variables:

```text
ENABLE_PROXY_INFERENCE=1
PROXY_SET_DIR=/kaggle/input/<proxy-set-input-dir>
ADAPTER_DIR=/kaggle/input/<adapter-input-dir-containing-adapter-files>
BASE_MODEL=nvidia/NVIDIA-Nemotron-3-Nano-30B-v2
```

Expected Kaggle output:

```text
proxy_predictions.jsonl
proxy_eval_kernel_report.json
```

After downloading `proxy_predictions.jsonl` to `artifacts/stage3/proxy_predictions.jsonl`, run:

```powershell
python scripts/16_stage3_ingest_predictions.py --predictions artifacts/stage3/proxy_predictions.jsonl
```

NEXT_ACTION:
  status: stay_stage3
  action: "run the staged proxy eval kernel on Kaggle GPU, bring back proxy_predictions.jsonl, then run the ingest script"
  reason: "Stage 4 remains blocked until proxy predictions are evaluated locally."
"""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
