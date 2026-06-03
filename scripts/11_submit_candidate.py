from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.kaggle_cli import DEFAULT_COMPETITION, query_submission_history  # noqa: E402
from nemotron086.provenance import sha256_file, write_json  # noqa: E402
from nemotron086.reporting import write_text  # noqa: E402
from nemotron086.score_gate import evaluate_candidate  # noqa: E402
from nemotron086.safety import redact_sensitive  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True)
    parser.add_argument("--candidate-manifest", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=5400)
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args()
    zip_path = PROJECT_ROOT / args.zip
    attempt = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "competition": DEFAULT_COMPETITION,
        "zip_path": str(zip_path),
        "zip_exists": zip_path.exists(),
        "zip_sha256": sha256_file(zip_path) if zip_path.exists() else None,
        "candidate_manifest": str(PROJECT_ROOT / args.candidate_manifest),
        "message": args.message,
        "dry_run": not args.yes,
        "submitted": False,
        "returncode": None,
        "stdout": "",
        "stderr": "",
        "pre_submit_today_count": None,
        "pre_submit_remaining_quota": None,
        "score_gate_allowed": False,
        "score_gate_reasons": [],
        "post_submit_history_refreshed": False,
    }
    if not zip_path.exists():
        attempt["failure_reason"] = "submission_zip_missing"
        write_attempt_reports(attempt)
        print("submission_zip_missing")
        return 3
    history = query_submission_history(PROJECT_ROOT)
    today = history["parsed"]["today_submission_count"]
    attempt["pre_submit_today_count"] = today
    attempt["pre_submit_remaining_quota"] = history["parsed"]["today_remaining_quota"]
    if today is None or today >= 5:
        attempt["failure_reason"] = "daily_quota_unavailable_or_exhausted"
        write_attempt_reports(attempt)
        print("daily_quota_unavailable_or_exhausted")
        return 6
    gate = evaluate_candidate(PROJECT_ROOT, PROJECT_ROOT / args.candidate_manifest)
    attempt["score_gate_allowed"] = gate["allowed"]
    attempt["score_gate_reasons"] = gate["reasons"]
    if not gate["allowed"]:
        attempt["failure_reason"] = "score_gate_rejected"
        write_attempt_reports(attempt)
        print("score_gate_rejected")
        return 4
    if not args.yes:
        attempt["failure_reason"] = "dry_run_requires_yes"
        write_attempt_reports(attempt)
        print("dry_run: add --yes to submit after final review")
        return 5
    command = ["kaggle", "competitions", "submit", DEFAULT_COMPETITION, "-f", str(zip_path), "-m", args.message]
    attempt["timeout_seconds"] = args.timeout_seconds
    process = subprocess.Popen(
        command,
        cwd=str(PROJECT_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        stdout, stderr = process.communicate(timeout=args.timeout_seconds)
        attempt["returncode"] = process.returncode
        attempt["stdout"] = redact_sensitive(stdout or "")
        attempt["stderr"] = redact_sensitive(stderr or "")
        attempt["submitted"] = process.returncode == 0
        attempt["failure_reason"] = None if process.returncode == 0 else "kaggle_submit_failed"
    except subprocess.TimeoutExpired as exc:
        kill_process_tree(process.pid)
        stdout, stderr = process.communicate()
        attempt["returncode"] = None
        attempt["stdout"] = redact_sensitive((exc.stdout or "") + (stdout or ""))
        attempt["stderr"] = redact_sensitive((exc.stderr or "") + (stderr or ""))
        attempt["submitted"] = False
        attempt["failure_reason"] = "kaggle_submit_timeout"
    (PROJECT_ROOT / "logs" / "submit_candidate.log").write_text(attempt["stdout"] + attempt["stderr"], encoding="utf-8")
    post_history = query_submission_history(PROJECT_ROOT)
    attempt["post_submit_history_refreshed"] = post_history["query_ok"]
    attempt["post_submit_today_count"] = post_history["parsed"]["today_submission_count"]
    attempt["post_submit_remaining_quota"] = post_history["parsed"]["today_remaining_quota"]
    write_attempt_reports(attempt)
    return attempt["returncode"] if isinstance(attempt["returncode"], int) else 7


def write_attempt_reports(attempt: dict) -> None:
    write_json(PROJECT_ROOT / "reports" / "SUBMISSION_ATTEMPT.json", attempt)
    stdout = first_lines(attempt.get("stdout") or "")
    stderr = first_lines(attempt.get("stderr") or "")
    report = f"""# Submission Attempt

- timestamp: {attempt['timestamp']}
- competition: `{attempt['competition']}`
- zip_path: `{attempt['zip_path']}`
- zip_exists: {attempt['zip_exists']}
- zip_sha256: `{attempt['zip_sha256'] or 'null'}`
- dry_run: {attempt['dry_run']}
- pre_submit_today_count: {attempt['pre_submit_today_count']}
- pre_submit_remaining_quota: {attempt['pre_submit_remaining_quota']}
- score_gate_allowed: {attempt['score_gate_allowed']}
- submitted: {attempt['submitted']}
- returncode: {attempt['returncode']}
- failure_reason: {attempt.get('failure_reason')}
- post_submit_history_refreshed: {attempt['post_submit_history_refreshed']}
- post_submit_today_count: {attempt.get('post_submit_today_count')}
- post_submit_remaining_quota: {attempt.get('post_submit_remaining_quota')}

## Message

```text
{attempt['message']}
```

## Score Gate Reasons

{lines_or_null(attempt['score_gate_reasons'])}

## Kaggle Stdout

```text
{stdout or 'null'}
```

## Kaggle Stderr

```text
{stderr or 'null'}
```
"""
    write_text(PROJECT_ROOT / "reports" / "SUBMISSION_ATTEMPT.md", report)


def kill_process_tree(pid: int) -> None:
    if sys.platform.startswith("win"):
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], text=True, capture_output=True, check=False)
    else:
        try:
            subprocess.run(["pkill", "-TERM", "-P", str(pid)], text=True, capture_output=True, check=False)
        finally:
            subprocess.run(["kill", "-TERM", str(pid)], text=True, capture_output=True, check=False)


def lines_or_null(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- null"


def first_lines(text: str, limit: int = 40) -> str:
    return "\n".join(text.splitlines()[:limit])


if __name__ == "__main__":
    raise SystemExit(main())
