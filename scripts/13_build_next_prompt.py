from __future__ import annotations

import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    stage1 = PROJECT_ROOT / "reports" / "STAGE1_DRY_RUN.md"
    stage2 = PROJECT_ROOT / "artifacts" / "stage2" / "tong_full_repro" / "stage2_manifest.json"
    stage3 = PROJECT_ROOT / "artifacts" / "stage3" / "proxy_eval_manifest.json"
    stage4 = PROJECT_ROOT / "reports" / "STAGE4_READINESS.json"
    submit_attempt = PROJECT_ROOT / "reports" / "SUBMISSION_ATTEMPT.json"
    submit_retry_pid = PROJECT_ROOT / "logs" / "submit_retry.pid"
    gate = PROJECT_ROOT / "reports" / "SCORE_GATE_RESULT.md"
    if not stage1.exists():
        prompt = "Run Stage 1 dry-run and fix Kaggle CLI or asset audit failures."
    elif submit_retry_pid.exists() and process_running(submit_retry_pid):
        prompt = "Wait for the active Kaggle submit retry to finish, then refresh submissions with python scripts/04_query_submissions.py."
    elif submit_attempt.exists() and read_json(submit_attempt).get("failure_reason") == "kaggle_submit_timeout_no_submission_recorded":
        prompt = (
            "If no submit retry is running, switch Stage 3 to Kaggle deployment: "
            "python scripts/18_stage3_kaggle_deploy.py --create-dataset --yes; "
            "python scripts/18_stage3_kaggle_deploy.py --push-kernel --yes"
        )
    elif stage4.exists() and not read_json(stage4).get("can_start_stage4"):
        prompt = (
            "Run the staged proxy eval kernel on Kaggle GPU, download proxy_predictions.jsonl, "
            "then run: python scripts/16_stage3_ingest_predictions.py --predictions artifacts/stage3/proxy_predictions.jsonl"
        )
    elif stage3.exists() and not read_json(stage3).get("complete"):
        prompt = (
            "Complete Stage 3 by generating proxy_predictions.jsonl on Kaggle GPU and ingesting it locally "
            "with scripts/16_stage3_ingest_predictions.py."
        )
    elif stage2.exists() and not read_json(stage2).get("structural_valid"):
        prompt = "Fix Stage 2 adapter validation before proxy eval or submission work."
    elif gate.exists():
        prompt = "Review score gate result and either fix rejected candidate or prepare one approved submit command."
    else:
        prompt = "If a candidate adapter exists, validate and package it; otherwise run one baseline reproduction route."
    (PROJECT_ROOT / "reports" / "NEXT_PROMPT.md").write_text(prompt + "\n", encoding="utf-8")
    print("report: reports/NEXT_PROMPT.md")
    return 0


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def process_running(pid_path: Path) -> bool:
    try:
        pid = int(pid_path.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return False
    if not pid:
        return False
    command = f"Get-Process -Id {pid} -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Id"
    completed = subprocess.run(["powershell", "-NoProfile", "-Command", command], text=True, capture_output=True)
    return completed.returncode == 0 and completed.stdout.strip() == str(pid)


if __name__ == "__main__":
    raise SystemExit(main())
