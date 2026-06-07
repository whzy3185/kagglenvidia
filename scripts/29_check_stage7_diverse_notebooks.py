from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "configs" / "stage7_diverse_notebook_candidates.yaml"
REPORT_PATH = PROJECT_ROOT / "reports" / "STAGE7_DIVERSE_REMOTE_STATUS.md"


def main() -> int:
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    candidates = payload.get("candidates", [])
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    results = []
    for index, candidate in enumerate(candidates, start=1):
        kernel_id = candidate["kernel_id"]
        print(f"[{index}/{len(candidates)}] checking {kernel_id}", flush=True)
        status = run(["kaggle", "kernels", "status", kernel_id], env, timeout=20)
        files = run(
            ["kaggle", "kernels", "files", kernel_id, "-v", "--page-size", "100"],
            env,
            timeout=60,
        )
        logs = run(["kaggle", "kernels", "logs", kernel_id], env, timeout=90)
        result = classify(candidate, status, files, logs)
        results.append(result)
        print(f"  remote_state={result['remote_state']}", flush=True)
        write_report(results, len(candidates))
    return 0


def run(command: list[str], env: dict[str, str], timeout: int) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "returncode": 124,
            "stdout": text(exc.stdout),
            "stderr": "timeout: " + text(exc.stderr),
        }


def text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def classify(
    candidate: dict[str, Any],
    status: dict[str, Any],
    files: dict[str, Any],
    logs: dict[str, Any],
) -> dict[str, Any]:
    combined = "\n".join(
        [
            status["stdout"],
            status["stderr"],
            files["stdout"],
            files["stderr"],
            logs["stdout"],
            logs["stderr"],
        ]
    )
    lower = combined.lower()
    success_marker = "ok: /kaggle/working/submission.zip is ready." in lower
    if "submission.zip" in files["stdout"] and success_marker:
        state = "output_ready"
    elif "submission.zip" in files["stdout"]:
        state = "output_visible_unverified"
    elif any(marker in lower for marker in ["papermillexecutionerror", "traceback (most recent call last)", "nameerror:", "runtimeerror:"]):
        state = "failed"
    elif "complete" in lower:
        state = "complete_without_submission_zip"
    elif "running" in lower:
        state = "running"
    elif "queued" in lower or "pending" in lower:
        state = "queued"
    else:
        state = "uploaded_status_unknown"
    return {
        "kernel_id": candidate["kernel_id"],
        "mechanism": candidate["mechanism"],
        "route_type": candidate["route_type"],
        "remote_state": state,
        "submission_zip_visible": "submission.zip" in files["stdout"],
        "success_marker_visible": success_marker,
        "submission_zip_sha256": extract_json_value(combined, "submission_zip_sha256"),
        "submission_zip_size_bytes": extract_json_value(combined, "submission_zip_size_bytes"),
        "status_returncode": status["returncode"],
        "files_returncode": files["returncode"],
        "logs_returncode": logs["returncode"],
        "status_excerpt": tail(status["stdout"] + "\n" + status["stderr"], 1500),
        "files_excerpt": tail(files["stdout"] + "\n" + files["stderr"], 1500),
        "logs_excerpt": tail(logs["stdout"] + "\n" + logs["stderr"], 5000),
    }


def extract_json_value(value: str, key: str) -> str:
    normalized = value.replace('\\"', '"')
    match = re.search(
        rf'"{re.escape(key)}"\s*:\s*"?(?P<value>[A-Za-z0-9._-]+)"?',
        normalized,
    )
    if not match:
        match = re.search(
            rf"(?m)^{re.escape(key)}:\s*(?P<value>[A-Za-z0-9._-]+)\s*$",
            normalized,
        )
    return match.group("value") if match else ""


def tail(value: str, limit: int) -> str:
    value = value.strip()
    return value[-limit:] if len(value) > limit else value


def write_report(results: list[dict[str, Any]], expected: int) -> None:
    counts: dict[str, int] = {}
    for item in results:
        counts[item["remote_state"]] = counts.get(item["remote_state"], 0) + 1
    rows = [
        "# Stage 7 Diverse Remote Status",
        "",
        f"- updated_at: {datetime.now().isoformat(timespec='seconds')}",
        f"- expected_candidates: {expected}",
        f"- checked_candidates: {len(results)}",
        f"- state_counts: `{json.dumps(counts, sort_keys=True)}`",
        "- competition_submission_executed: false",
        "",
        "| kernel | route | mechanism | remote state | output | success marker | SHA256 |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for item in results:
        rows.append(
            f"| `{item['kernel_id']}` | {item['route_type']} | `{item['mechanism']}` | "
            f"{item['remote_state']} | {str(item['submission_zip_visible']).lower()} | "
            f"{str(item['success_marker_visible']).lower()} | "
            f"`{item['submission_zip_sha256'][:12] or 'n/a'}` |"
        )
    rows.extend(["", "## Diagnostics", ""])
    for item in results:
        rows.extend(
            [
                f"### {item['kernel_id']}",
                "",
                f"- remote_state: `{item['remote_state']}`",
                f"- status_returncode: `{item['status_returncode']}`",
                f"- files_returncode: `{item['files_returncode']}`",
                f"- logs_returncode: `{item['logs_returncode']}`",
                "",
                "```text",
                item["status_excerpt"] or "(no status text)",
                item["files_excerpt"] or "(no files text)",
                item["logs_excerpt"] or "(no logs text)",
                "```",
                "",
            ]
        )
    REPORT_PATH.write_text("\n".join(rows), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
