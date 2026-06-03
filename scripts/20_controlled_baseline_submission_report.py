from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.provenance import today_stamp, write_json  # noqa: E402
from nemotron086.reporting import write_text  # noqa: E402


COMPETITION = "nvidia-nemotron-model-reasoning-challenge"
SUBMISSION_ZIP = PROJECT_ROOT / "artifacts" / "stage2" / "tong_full_repro" / "submission" / "submission.zip"
SUBMISSION_MANIFEST = PROJECT_ROOT / "artifacts" / "stage2" / "tong_full_repro" / "submission" / "manifest.json"
STAGE2_MANIFEST = PROJECT_ROOT / "artifacts" / "stage2" / "tong_full_repro" / "stage2_manifest.json"
PARSED_SUBMISSIONS = PROJECT_ROOT / "logs" / f"submissions_parsed_{today_stamp()}.json"
REPORT_MD = PROJECT_ROOT / "reports" / "CONTROLLED_BASELINE_SUBMISSION.md"
REPORT_JSON = PROJECT_ROOT / "reports" / "CONTROLLED_BASELINE_SUBMISSION.json"


def main() -> int:
    parsed = read_json(PARSED_SUBMISSIONS)
    stage2 = read_json(STAGE2_MANIFEST)
    pack_manifest = read_json(SUBMISSION_MANIFEST)
    active_submit = find_active_submit_processes()
    submissions = parsed.get("submissions") or parsed.get("rows") or []
    latest = submissions[0] if submissions else None
    public_score = normalize_score(latest.get("public_score")) if latest else None
    status = build_status(active_submit, latest, public_score)
    success_086 = public_score is not None and public_score >= 0.86
    payload = {
        "competition": COMPETITION,
        "submission_zip_path": str(SUBMISSION_ZIP),
        "submission_zip_exists": SUBMISSION_ZIP.exists(),
        "submission_zip_sha256": pack_manifest.get("sha256"),
        "zip_structure_status": pack_manifest.get("zip_structure_status"),
        "zip_files": pack_manifest.get("files", []),
        "adapter_structural_valid": stage2.get("structural_valid"),
        "rank_lte_32": stage2.get("rank_lte_32"),
        "license_status": stage2.get("license_status"),
        "official_format_confirmed": stage2.get("official_format_confirmed", False),
        "submission_attempted": bool(active_submit) or bool(latest),
        "manual_submit_process_active": bool(active_submit),
        "active_submit_processes": active_submit,
        "submission_status": status,
        "latest_submission": latest,
        "public_score": public_score,
        "success_086_reproduced": success_086,
        "proxy_eval_waived": True,
        "waiver_reason": "Kaggle Notebook proxy inference failed due to Mamba/CUDA kernel compatibility; official competition evaluator is used instead.",
        "proxy_eval_complete": False,
        "today_submission_count": parsed.get("today_submission_count"),
        "today_remaining_quota": parsed.get("today_remaining_quota"),
        "next_action": build_next_action(active_submit, latest, public_score),
    }
    write_json(REPORT_JSON, payload)
    write_text(REPORT_MD, render_report(payload))
    print(f"report: {REPORT_MD.relative_to(PROJECT_ROOT).as_posix()}")
    print(f"submission_status: {payload['submission_status']}")
    print(f"public_score: {payload['public_score']}")
    return 0


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def find_active_submit_processes() -> list[dict[str, Any]]:
    command = (
        "Get-CimInstance Win32_Process | "
        "Where-Object { $_.CommandLine -like '*kaggle*competitions submit*nvidia-nemotron-model-reasoning-challenge*' } | "
        "Select-Object ProcessId,ParentProcessId,Name,CreationDate,CommandLine | ConvertTo-Json -Compress"
    )
    completed = subprocess.run(["powershell", "-NoProfile", "-Command", command], text=True, capture_output=True)
    text = completed.stdout.strip()
    if not text:
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    rows = data if isinstance(data, list) else [data]
    return [
        {
            "process_id": row.get("ProcessId"),
            "parent_process_id": row.get("ParentProcessId"),
            "name": row.get("Name"),
            "creation_date": row.get("CreationDate"),
            "command_line": row.get("CommandLine"),
        }
        for row in rows
        if "20_controlled_baseline_submission_report.py" not in str(row.get("CommandLine"))
    ]


def normalize_score(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).strip())
    except ValueError:
        return None


def build_status(active_submit: list[dict[str, Any]], latest: dict[str, Any] | None, public_score: float | None) -> str:
    if active_submit:
        return "upload_in_progress"
    if latest and public_score is not None:
        return "scored"
    if latest:
        return str(latest.get("status") or "submitted_score_pending")
    return "no_submission_recorded"


def build_next_action(active_submit: list[dict[str, Any]], latest: dict[str, Any] | None, public_score: float | None) -> dict[str, str]:
    if active_submit:
        return {
            "status": "wait",
            "action": "wait for the active Kaggle CLI upload to finish, then run python scripts/04_query_submissions.py and this report script again",
            "reason": "The competition submission upload is still in progress.",
        }
    if latest and public_score is None:
        return {
            "status": "wait_score",
            "action": "poll kaggle submissions every 3 minutes until public_score is available",
            "reason": "The submission exists but public score is not available yet.",
        }
    if public_score is not None:
        return {
            "status": "review_score",
            "action": "compare public score against 0.86 target and decide whether to continue Stage 4 planning",
            "reason": "Official competition evaluator has produced a public score.",
        }
    return {
        "status": "stay_controlled_submission",
        "action": "complete one controlled upload of the structural-valid adapter package",
        "reason": "No Kaggle submission record exists yet.",
    }


def render_report(payload: dict[str, Any]) -> str:
    next_action = payload["next_action"]
    latest = json.dumps(payload["latest_submission"], ensure_ascii=False, indent=2) if payload["latest_submission"] else "null"
    return f"""# Controlled Baseline Submission

- competition: `{payload['competition']}`
- submission_zip_path: `{payload['submission_zip_path']}`
- submission_zip_exists: {payload['submission_zip_exists']}
- submission_zip_sha256: `{payload['submission_zip_sha256']}`
- zip_structure_status: {payload['zip_structure_status']}
- adapter_structural_valid: {payload['adapter_structural_valid']}
- rank_lte_32: {payload['rank_lte_32']}
- license_status: {payload['license_status']}
- official_format_confirmed: {payload['official_format_confirmed']}
- submission_attempted: {payload['submission_attempted']}
- manual_submit_process_active: {payload['manual_submit_process_active']}
- submission_status: {payload['submission_status']}
- public_score: {payload['public_score']}
- success_086_reproduced: {payload['success_086_reproduced']}
- proxy_eval_waived: true
- proxy_eval_complete: false
- waiver_reason: {payload['waiver_reason']}
- today_submission_count: {payload['today_submission_count']}
- today_remaining_quota: {payload['today_remaining_quota']}

## Latest Submission

```json
{latest}
```

NEXT_ACTION:
  status: {next_action['status']}
  action: "{next_action['action']}"
  reason: "{next_action['reason']}"
"""


if __name__ == "__main__":
    raise SystemExit(main())
