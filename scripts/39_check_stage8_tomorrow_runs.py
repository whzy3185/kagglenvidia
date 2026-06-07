from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "configs" / "stage8_tomorrow_submission_packages.yaml"
REPORT_PATH = PROJECT_ROOT / "reports" / "STAGE8_TOMORROW_REMOTE_STATUS.md"


def main() -> int:
    if not CONFIG_PATH.exists():
        raise SystemExit("Missing Stage 8 config. Run scripts/37_make_stage8_tomorrow_notebooks.py first.")
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    results = [inspect(candidate) for candidate in payload.get("candidates", [])]
    write_report(results)
    for item in results:
        print(f"{item['kernel_id']}: {item['state']} {item['last_step'] or ''}".rstrip())
    print(f"report={REPORT_PATH.relative_to(PROJECT_ROOT)}")
    return 1 if any(item["state"] == "failed" for item in results) else 0


def inspect(candidate: dict[str, Any]) -> dict[str, Any]:
    files = run(["kaggle", "kernels", "files", candidate["kernel_id"], "-v", "--page-size", "100"])
    logs = run(["kaggle", "kernels", "logs", candidate["kernel_id"]])
    log_text = decode_logs(logs.stdout)
    diagnostic_text = logs.stderr
    text = log_text + "\n" + diagnostic_text
    output_visible = "submission.zip" in files.stdout
    success = "OK: /kaggle/working/submission.zip is ready." in text
    failed = any(
        marker in text
        for marker in [
            "PapermillExecutionError",
            "Traceback (most recent call last)",
            "RuntimeError:",
            "NotImplementedError:",
            "NameError:",
        ]
    )
    if output_visible and success:
        state = "output_ready"
    elif failed:
        state = "failed"
    elif log_text.strip():
        state = "running_or_finalizing"
    elif "404 Client Error" in files.stderr + logs.stderr:
        state = "created_not_started_or_no_output"
    else:
        state = "queued_no_logs"
    step_matches = re.findall(r"step\s+(\d+)\s*/\s*(\d+)", text, re.IGNORECASE)
    return {
        "kernel_id": candidate["kernel_id"],
        "slug": candidate["slug"],
        "mechanism": candidate["mechanism"],
        "state": state,
        "output_visible": output_visible,
        "success_marker": success,
        "last_step": f"{step_matches[-1][0]}/{step_matches[-1][1]}" if step_matches else "",
        "zip_sha256": extract(text, r'(?:submission_zip_sha256["\s:]+)([0-9a-f]{64})'),
        "zip_size_bytes": extract(text, r'(?:submission_zip_size_bytes["\s:]+)(\d+)'),
        "error_excerpt": error_excerpt(text),
        "files_returncode": files.returncode,
        "logs_returncode": logs.returncode,
    }


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=120,
        check=False,
    )


def decode_logs(raw: str) -> str:
    try:
        records = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if not isinstance(records, list):
        return raw
    return "".join(str(item.get("data") or "") for item in records if isinstance(item, dict))


def extract(text: str, pattern: str) -> str:
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else ""


def error_excerpt(text: str) -> str:
    lines = text.splitlines()
    indexes = [
        index
        for index, line in enumerate(lines)
        if any(
            marker in line
            for marker in [
                "PapermillExecutionError",
                "Traceback (most recent call last)",
                "RuntimeError:",
                "NotImplementedError:",
                "NameError:",
            ]
        )
    ]
    if not indexes:
        return ""
    start = max(0, indexes[-1] - 2)
    return "\n".join(lines[start : indexes[-1] + 16])[:3000]


def write_report(results: list[dict[str, Any]]) -> None:
    rows = [
        "# Stage 8 Tomorrow Remote Status",
        "",
        f"- updated_at: {datetime.now().isoformat(timespec='seconds')}",
        "- status_source: Kaggle kernel files and logs",
        "- competition_submission_executed: false",
        "",
        "| kernel | mechanism | state | step | output | SHA256 | size bytes |",
        "|---|---|---|---|---:|---|---:|",
    ]
    for item in results:
        rows.append(
            f"| `{item['kernel_id']}` | `{item['mechanism']}` | `{item['state']}` | "
            f"`{item['last_step'] or 'n/a'}` | {str(item['output_visible']).lower()} | "
            f"`{item['zip_sha256'][:12] or 'n/a'}` | {item['zip_size_bytes'] or 'n/a'} |"
        )
    failures = [item for item in results if item["state"] == "failed"]
    if failures:
        rows.extend(["", "## Failures", ""])
        for item in failures:
            rows.extend(
                [
                    f"### {item['kernel_id']}",
                    "",
                    "```text",
                    item["error_excerpt"],
                    "```",
                    "",
                ]
            )
    rows.extend(
        [
            "",
            "## Next Actions",
            "",
            "- `output_ready`: can be converted into a tomorrow confirmation card after quota resets.",
            "- `running_or_finalizing`: keep polling; do not submit.",
            "- `created_not_started_or_no_output`: push again later if GPU session slots free.",
            "- `failed`: inspect failure before rerun; do not blindly submit.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(rows), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
