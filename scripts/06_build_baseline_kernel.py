from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.adapter_validator import validate_adapter  # noqa: E402
from nemotron086.provenance import ensure_dir, write_json  # noqa: E402
from nemotron086.reporting import write_text  # noqa: E402
from nemotron086.safety import redact_sensitive  # noqa: E402
from nemotron086.submission_packer import pack_submission  # noqa: E402


ROUTE = "tong_full_repro"
SOURCE_URL = "https://www.kaggle.com/models/huikang/nemotron-adapter"
MODEL_VERSION_REF = "huikang/nemotron-adapter/Transformers/default/27"
ARTIFACT_ROOT = PROJECT_ROOT / "artifacts" / "stage2" / ROUTE
ADAPTER_DIR = ARTIFACT_ROOT / "adapter"
SUBMISSION_DIR = ARTIFACT_ROOT / "submission"
VALIDATION_DIR = ARTIFACT_ROOT / "validation"
MANIFEST_PATH = ARTIFACT_ROOT / "stage2_manifest.json"
EXPECTED_FILES = ["adapter_config.json", "adapter_model.safetensors"]


def main() -> int:
    ensure_dir(ADAPTER_DIR)
    ensure_dir(SUBMISSION_DIR)
    ensure_dir(VALIDATION_DIR)
    write_selected_config()
    write_decision_report()

    manifest = base_manifest()
    help_status = check_kaggle_model_download_support()
    manifest["cli_help_status"] = help_status
    if not help_status["supported"]:
        manifest["fetch_status"] = "unsupported"
        manifest["next_action"] = "manually download Tong adapter into artifacts/stage2/tong_full_repro/adapter"
        finish(manifest, None, None)
        return 3

    fetch = ensure_adapter_files()
    manifest["fetch_status"] = fetch["status"]
    manifest["fetch_detail"] = fetch
    update_file_flags(manifest)
    if fetch["status"] != "success":
        manifest["next_action"] = "manually download Tong adapter into artifacts/stage2/tong_full_repro/adapter"
        finish(manifest, None, None)
        return 4

    validation = validate_adapter(ADAPTER_DIR, PROJECT_ROOT, output_dir=VALIDATION_DIR, write_reports=True)
    manifest["structural_valid"] = validation["structural_valid"]
    manifest["rank_lte_32"] = validation["rank_lte_32"]
    manifest["safetensors_opened"] = validation["safetensors_opened"]
    manifest["validation_report"] = {
        "json": str((VALIDATION_DIR / "validate_report.json").relative_to(PROJECT_ROOT).as_posix()),
        "markdown": str((VALIDATION_DIR / "validate_report.md").relative_to(PROJECT_ROOT).as_posix()),
    }
    if not validation["structural_valid"]:
        manifest["next_action"] = "fix selected adapter files before packaging"
        finish(manifest, validation, None)
        return 4

    with tempfile.TemporaryDirectory(prefix="stage2_pack_source_") as temp_dir:
        pack_source = Path(temp_dir)
        for filename in EXPECTED_FILES:
            shutil.copy2(ADAPTER_DIR / filename, pack_source / filename)
        pack_result = pack_submission(
            pack_source,
            PROJECT_ROOT,
            output_dir=SUBMISSION_DIR,
            write_validation_reports=False,
        )

    manifest["submission_zip_generated"] = bool(pack_result.get("packed"))
    manifest["submission_zip_path"] = str(pack_result.get("zip_path") or "")
    manifest["pack_manifest"] = str((SUBMISSION_DIR / "manifest.json").relative_to(PROJECT_ROOT).as_posix())
    manifest["official_format_confirmed"] = False
    if manifest["submission_zip_generated"]:
        manifest["next_action"] = "run score gate and manual license review before any optional submit"
    else:
        manifest["next_action"] = "fix packaging failure before any optional submit"
    finish(manifest, validation, pack_result)
    return 0 if manifest["submission_zip_generated"] else 4


def write_selected_config() -> None:
    content = f"""stage: 2
route: {ROUTE}
selected_type: candidate_adapter
source_url: {SOURCE_URL}
model_version_ref: {MODEL_VERSION_REF}
adapter_dir: artifacts/stage2/{ROUTE}/adapter
submission_dir: artifacts/stage2/{ROUTE}/submission
expected_files:
  - adapter_config.json
  - adapter_model.safetensors
license_status: unknown
official_format_confirmed: false
score_claim_status: public_report_claim_not_locally_verified
"""
    write_text(PROJECT_ROOT / "configs" / "stage2_selected_baseline.yaml", content)


def write_decision_report() -> None:
    content = f"""# Stage 2 Baseline Decision

selected_route:
  name: {ROUTE}
  classification: candidate_adapter
  source_url: {SOURCE_URL}
  model_version_ref: {MODEL_VERSION_REF}
  reason: "Research reports and Kaggle CLI file listing confirm adapter_config.json and adapter_model.safetensors are available."
  evidence:
    - e:/deep-research-report.md
    - e:/NVIDIA Nemotron 推理挑战公开高分方案研究报告 (1).docx
    - kaggle models instances versions files {MODEL_VERSION_REF}
  risks:
    - license_status_unknown
    - official_format_not_confirmed_by_submission
    - public_score_claim_not_locally_verified
  can_validate_and_pack: true
"""
    write_text(PROJECT_ROOT / "reports" / "STAGE2_BASELINE_DECISION.md", content)


def base_manifest() -> dict[str, Any]:
    return {
        "stage": 2,
        "route": ROUTE,
        "source_url": SOURCE_URL,
        "model_version_ref": MODEL_VERSION_REF,
        "fetch_status": "failed",
        "adapter_config_exists": False,
        "adapter_model_exists": False,
        "structural_valid": False,
        "rank_lte_32": False,
        "safetensors_opened": False,
        "submission_zip_generated": False,
        "submission_zip_path": "",
        "official_format_confirmed": False,
        "no_training": True,
        "no_submission": True,
        "base_model_loaded": False,
        "score_claim_status": "public_report_claim_not_locally_verified",
        "license_status": "unknown",
        "provenance": {
            "source_name": "nemotron-adapter",
            "author": "Tong Hui Kang",
            "source_url": SOURCE_URL,
            "model_version_ref": MODEL_VERSION_REF,
            "local_research_inputs": [
                "e:/deep-research-report.md",
                "e:/NVIDIA Nemotron 推理挑战公开高分方案研究报告 (1).docx",
            ],
            "license_status": "unknown",
            "allowed_use_before_license_review": "structural_validation_and_reference_only",
        },
        "next_action": "",
    }


def check_kaggle_model_download_support() -> dict[str, Any]:
    help_result = run_command(["kaggle", "models", "instances", "versions", "download", "--help"], timeout=60)
    return {
        "supported": help_result["ok"] and "model_instance_version" in help_result["stdout"],
        "returncode": help_result["returncode"],
    }


def ensure_adapter_files() -> dict[str, Any]:
    if expected_files_exist():
        return {"status": "success", "message": "adapter files already present; download skipped"}
    command = [
        "kaggle",
        "models",
        "instances",
        "versions",
        "download",
        MODEL_VERSION_REF,
        "-p",
        str(ADAPTER_DIR),
        "--untar",
        "-q",
    ]
    result = run_command(command, timeout=3600)
    if not result["ok"]:
        return {
            "status": "failed",
            "message": "kaggle model adapter download failed",
            "returncode": result["returncode"],
            "stderr": redact_sensitive(result["stderr"]),
        }
    if not expected_files_exist():
        return {
            "status": "manual_required",
            "message": "download completed but expected adapter files are missing",
            "returncode": result["returncode"],
        }
    return {"status": "success", "message": "adapter files downloaded successfully", "returncode": result["returncode"]}


def expected_files_exist() -> bool:
    return all((ADAPTER_DIR / filename).is_file() for filename in EXPECTED_FILES)


def update_file_flags(manifest: dict[str, Any]) -> None:
    manifest["adapter_config_exists"] = (ADAPTER_DIR / "adapter_config.json").is_file()
    manifest["adapter_model_exists"] = (ADAPTER_DIR / "adapter_model.safetensors").is_file()


def run_command(args: list[str], timeout: int) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        completed = subprocess.run(
            args,
            cwd=str(PROJECT_ROOT),
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": str(exc)}


def finish(manifest: dict[str, Any], validation: dict[str, Any] | None, pack_result: dict[str, Any] | None) -> None:
    update_file_flags(manifest)
    write_json(MANIFEST_PATH, manifest)
    write_text(PROJECT_ROOT / "reports" / "STAGE2_REPRO_REPORT.md", render_repro_report(manifest, validation, pack_result))
    print("report: reports/STAGE2_REPRO_REPORT.md")
    print(f"submission_zip_generated: {manifest['submission_zip_generated']}")
    print(f"NEXT_ACTION: {manifest['next_action']}")


def render_repro_report(
    manifest: dict[str, Any],
    validation: dict[str, Any] | None,
    pack_result: dict[str, Any] | None,
) -> str:
    validation_errors = validation.get("errors", []) if validation else []
    zip_files = pack_result.get("manifest", {}).get("files", []) if pack_result else []
    return f"""# Stage 2 Reproduction Report

Stage: 2
Route: {manifest['route']}
Source URL: {manifest['source_url']}
Fetch status: {manifest['fetch_status']}
Adapter config exists: {manifest['adapter_config_exists']}
Adapter model exists: {manifest['adapter_model_exists']}
Structural valid: {manifest['structural_valid']}
Rank <= 32: {manifest['rank_lte_32']}
Safetensors opened: {manifest['safetensors_opened']}
Submission zip generated: {manifest['submission_zip_generated']}
Submission zip path: {manifest['submission_zip_path'] or 'null'}
Official format confirmed: false
No training: true
No submission: true
Base model loaded: false

This package is structural-valid only when validation passes. It is not official-valid.

## Zip Files

{json.dumps(zip_files, ensure_ascii=False)}

## Validation Errors

{json.dumps(validation_errors, ensure_ascii=False)}

NEXT_ACTION:
  status: {"stay_stage2" if manifest['submission_zip_generated'] else "blocked"}
  action: "{manifest['next_action']}"
  reason: "{'adapter is structurally valid and packaged, but license and official-format review are still required' if manifest['submission_zip_generated'] else 'Stage 2 could not complete without valid adapter files'}"
"""


if __name__ == "__main__":
    raise SystemExit(main())
