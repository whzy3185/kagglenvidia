from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "configs" / "stage8_tomorrow_submission_packages.yaml"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "STAGE8_TOMORROW_NOTEBOOK_VALIDATION.md"
REPORT_PATH = PROJECT_ROOT / "reports" / "STAGE8_TOMORROW_PUSH_REPORT.md"


def main() -> int:
    if not CONFIG_PATH.exists():
        raise SystemExit("Missing Stage 8 config. Run scripts/37_make_stage8_tomorrow_notebooks.py first.")
    if not VALIDATION_PATH.exists() or "| false |" in VALIDATION_PATH.read_text(encoding="utf-8"):
        raise SystemExit("Stage 8 static validation is missing or contains failures.")

    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    candidates = payload.get("candidates", [])
    if len(candidates) != 5:
        raise SystemExit(f"Expected exactly 5 tomorrow candidates, found {len(candidates)}")

    results: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates, start=1):
        kernel_dir = PROJECT_ROOT / candidate["kernel_dir"]
        command = ["kaggle", "kernels", "push", "-p", str(kernel_dir)]
        print(f"[{index}/5] pushing {candidate['kernel_id']}", flush=True)
        completed = run(command, timeout=300)
        output = f"{completed.stdout}\n{completed.stderr}"
        lower = output.lower()
        result = {
            "kernel_id": candidate["kernel_id"],
            "kernel_dir": candidate["kernel_dir"],
            "mechanism": candidate["mechanism"],
            "returncode": completed.returncode,
            "run_started": "successfully pushed" in lower and "kernel push error" not in lower,
            "gpu_blocked": "maximum batch gpu session count" in lower,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
        results.append(result)
        print(
            f"  run_started={str(result['run_started']).lower()} "
            f"gpu_blocked={str(result['gpu_blocked']).lower()} "
            f"returncode={completed.returncode}",
            flush=True,
        )
        write_report(results, len(candidates))

    started = sum(1 for item in results if item["run_started"])
    accepted = sum(1 for item in results if item["run_started"] or item["gpu_blocked"])
    print(f"kernel_runs_started={started}")
    print(f"notebooks_accepted_or_started={accepted}")
    print("competition_submission_executed=false")
    print(f"report={REPORT_PATH.relative_to(PROJECT_ROOT)}")
    return 0 if accepted == len(candidates) else 2


def run(command: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
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
        timeout=timeout,
        check=False,
    )


def write_report(results: list[dict[str, Any]], expected: int) -> None:
    started = sum(1 for item in results if item["run_started"])
    accepted = sum(1 for item in results if item["run_started"] or item["gpu_blocked"])
    rows = [
        "# Stage 8 Tomorrow Notebook Push Report",
        "",
        f"- updated_at: {datetime.now().isoformat(timespec='seconds')}",
        f"- expected_candidates: {expected}",
        f"- push_attempted: {len(results)}",
        f"- kernel_runs_started: {started}",
        f"- notebooks_accepted_or_started: {accepted}",
        "- competition_submission_executed: false",
        "- competition_quota_consumed: false",
        "",
        "| kernel | mechanism | run started | GPU blocked | return code |",
        "|---|---|---:|---:|---:|",
    ]
    for item in results:
        rows.append(
            f"| `{item['kernel_id']}` | `{item['mechanism']}` | "
            f"{str(item['run_started']).lower()} | {str(item['gpu_blocked']).lower()} | {item['returncode']} |"
        )
    rows.extend(["", "## Command Output", ""])
    for item in results:
        rows.extend(
            [
                f"### {item['kernel_id']}",
                "",
                "```text",
                item["stdout"] or "(no stdout)",
                item["stderr"] or "(no stderr)",
                "```",
                "",
            ]
        )
    rows.extend(
        [
            "## Safety",
            "",
            "This script only calls `kaggle kernels push`. It never calls `kaggle competitions submit` and does not consume competition submission quota.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(rows), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
