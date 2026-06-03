from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.asset_audit import audit_assets  # noqa: E402
from nemotron086.kaggle_cli import check_kaggle_cli, query_submission_history  # noqa: E402
from nemotron086.reporting import write_text  # noqa: E402
from nemotron086.safety import ensure_stage1_safety  # noqa: E402
from nemotron086.submission_packer import pack_submission  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter-dir")
    args = parser.parse_args()

    safety = ensure_stage1_safety(PROJECT_ROOT)
    kaggle = check_kaggle_cli(PROJECT_ROOT)
    assets = audit_assets(PROJECT_ROOT)
    history = query_submission_history(PROJECT_ROOT)

    validation_status = "skipped_no_adapter_dir"
    pack_status = "not_generated"
    zip_path = None
    pack_result: dict[str, Any] | None = None
    if args.adapter_dir:
        pack_result = pack_submission(Path(args.adapter_dir), PROJECT_ROOT)
        validation_status = "passed" if pack_result["validation"]["structural_valid"] else "failed"
        pack_status = "generated" if pack_result["packed"] else pack_result["status"]
        zip_path = pack_result.get("zip_path")

    parsed = history["parsed"]
    can_enter_stage2, reason = _stage2_gate(safety, kaggle, assets, pack_result)
    next_action = _next_action(can_enter_stage2, args.adapter_dir, kaggle, assets, validation_status)
    report = render_dry_run_report(
        safety=safety,
        kaggle=kaggle,
        parsed=parsed,
        assets=assets,
        validation_status=validation_status,
        pack_status=pack_status,
        zip_path=zip_path,
        can_enter_stage2=can_enter_stage2,
        cannot_reason=reason,
        next_action=next_action,
    )
    write_text(PROJECT_ROOT / "reports" / "STAGE1_DRY_RUN.md", report)
    print("report: reports/STAGE1_DRY_RUN.md")
    print(f"NEXT_ACTION: {next_action['action']}")

    if not safety["stage1_safety_valid"]:
        return 3
    if not kaggle["kaggle_version_ok"]:
        return 1
    if not kaggle["submissions_query_ok"]:
        return 2
    if args.adapter_dir and validation_status != "passed":
        return 4
    if not args.adapter_dir:
        return 5
    if not can_enter_stage2:
        return 6
    return 0


def _stage2_gate(
    safety: dict[str, Any],
    kaggle: dict[str, Any],
    assets: dict[str, Any],
    pack_result: dict[str, Any] | None,
) -> tuple[bool, str]:
    if not safety["stage1_safety_valid"]:
        return False, "stage1 safety violations found"
    if not kaggle["kaggle_version_ok"] or not kaggle["submissions_query_ok"]:
        return False, "Kaggle CLI or submission history query is not healthy"
    if pack_result is not None and not pack_result.get("packed"):
        return False, "adapter validation or structural packaging failed"
    return True, "null"


def _next_action(
    can_enter_stage2: bool,
    adapter_dir: str | None,
    kaggle: dict[str, Any],
    assets: dict[str, Any],
    validation_status: str,
) -> dict[str, str]:
    if can_enter_stage2:
        if assets["candidate_adapter_found"]:
            return {
                "status": "enter_stage2",
                "action": "run Stage 2 single-baseline reproduction prompt after confirming the candidate adapter provenance",
                "reason": "Kaggle API authentication is fixed and Stage 1 minimal loop is complete.",
            }
        return {
            "status": "enter_stage2",
            "action": "run Stage 2 single-baseline reproduction prompt after providing or confirming one reproducible baseline asset",
            "reason": "Kaggle API authentication is fixed and Stage 1 minimal loop is complete, but no candidate adapter exists yet.",
        }
    if not kaggle["kaggle_version_ok"]:
        return {
            "status": "blocked",
            "action": "install kaggle cli",
            "reason": "Kaggle CLI is not available in this shell.",
        }
    if not kaggle["submissions_query_ok"]:
        return {
            "status": "blocked",
            "action": "kaggle auth login",
            "reason": "Kaggle submission history query reports authentication is required.",
        }
    if adapter_dir and validation_status == "failed":
        return {
            "status": "stay_stage1",
            "action": "fix adapter_config.json or adapter_model.safetensors",
            "reason": "adapter structural validation failed.",
        }
    if not assets["candidate_adapter_found"]:
        return {
            "status": "stay_stage1",
            "action": "manually fill url fields in configs/public_baselines.yaml",
            "reason": "all 0.86 routes are currently asset-unknown.",
        }
    return {
        "status": "stay_stage1",
        "action": "run python scripts/05_stage1_dry_run.py --adapter-dir path/to/adapter",
        "reason": "Stage 1 needs a local adapter before structural packaging.",
    }


def render_dry_run_report(
    safety: dict[str, Any],
    kaggle: dict[str, Any],
    parsed: dict[str, Any],
    assets: dict[str, Any],
    validation_status: str,
    pack_status: str,
    zip_path: str | None,
    can_enter_stage2: bool,
    cannot_reason: str,
    next_action: dict[str, str],
) -> str:
    summary = assets["summary"]
    return f"""# Stage 1 Dry Run

Stage: 1 - asset_audit_and_minimal_submission_loop
Kaggle CLI status: {_status(kaggle['kaggle_version_ok'])}
Submission history query status: {_status(kaggle['submissions_query_ok'])}
Submission history query success: {parsed['submission_history_query_success']}
Submission history query parse status: {parsed['submission_history_query_status']}
Authentication status: {parsed['authentication_status']}
Raw submission result: {parsed['raw_result'] or 'unknown'}
Today submission count parse status: {parsed['today_submission_count_parse_status']}
Today submission count: {parsed['today_submission_count']}
Today remaining quota: {parsed['today_remaining_quota']}
Asset audit summary: {summary}
Trainable baselines: {summary.get('trainable_baseline', 0)}
Conversion-only baselines: {summary.get('conversion_only', 0)}
Candidate adapters: {summary.get('candidate_adapter', 0)}
Idea-only routes: {summary.get('idea_only', 0)}
Blocked routes: {summary.get('blocked', 0)}
Adapter validation status: {validation_status}
Submission zip generated: {pack_status == 'generated'}
Submission zip path: {zip_path}
Official format confirmed: false
Can enter Stage 2: {can_enter_stage2}
Cannot enter Stage 2 reason: {cannot_reason}
Stage 1 safety valid: {safety['stage1_safety_valid']}

NEXT_ACTION:
  status: {next_action['status']}
  action: "{next_action['action']}"
  reason: "{next_action['reason']}"
"""


def _status(ok: bool) -> str:
    return "success" if ok else "failed"


if __name__ == "__main__":
    raise SystemExit(main())
