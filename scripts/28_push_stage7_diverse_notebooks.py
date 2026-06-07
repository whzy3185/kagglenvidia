from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "configs" / "stage7_diverse_notebook_candidates.yaml"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "STAGE7_DIVERSE_NOTEBOOK_VALIDATION.md"
REPORT_PATH = PROJECT_ROOT / "reports" / "STAGE7_DIVERSE_NOTEBOOK_PUSH_REPORT.md"


def main() -> int:
    if not CONFIG_PATH.exists():
        raise SystemExit("Missing candidate config. Run scripts/27_make_stage7_diverse_notebooks.py first.")
    if not VALIDATION_PATH.exists() or "| false |" in VALIDATION_PATH.read_text(encoding="utf-8"):
        raise SystemExit("Static validation is missing or contains failures.")

    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    candidates = payload.get("candidates", [])
    if len(candidates) < 10:
        raise SystemExit(f"Expected at least 10 candidates, found {len(candidates)}")

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    results: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates, start=1):
        kernel_dir = PROJECT_ROOT / candidate["kernel_dir"]
        command = ["kaggle", "kernels", "push", "-p", str(kernel_dir)]
        print(f"[{index}/{len(candidates)}] pushing {candidate['kernel_id']}", flush=True)
        completed = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=300,
            check=False,
        )
        output = (completed.stdout + "\n" + completed.stderr).strip()
        run_started = "successfully pushed" in output.lower() and "kernel push error" not in output.lower()
        created_but_run_blocked = "maximum batch gpu session count" in output.lower()
        result = {
            "kernel_id": candidate["kernel_id"],
            "kernel_dir": candidate["kernel_dir"],
            "returncode": completed.returncode,
            "success": run_started,
            "notebook_created_run_blocked": created_but_run_blocked,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
        results.append(result)
        print(
            f"  success={str(result['success']).lower()} returncode={completed.returncode}",
            flush=True,
        )
        write_report(results, len(candidates))

    succeeded = sum(1 for item in results if item["success"])
    created = sum(
        1
        for item in results
        if item["success"] or item.get("notebook_created_run_blocked")
    )
    print(f"push_succeeded={succeeded}")
    print(f"notebooks_created={created}")
    print(f"push_attempted={len(results)}")
    print(f"report={REPORT_PATH}")
    return 0 if succeeded >= 10 else 2


def write_report(results: list[dict[str, Any]], expected: int) -> None:
    succeeded = sum(1 for item in results if item["success"])
    created = sum(
        1
        for item in results
        if item["success"] or item.get("notebook_created_run_blocked")
    )
    rows = [
        "# Stage 7 Diverse Notebook Push Report",
        "",
        f"- updated_at: {datetime.now().isoformat(timespec='seconds')}",
        f"- expected_candidates: {expected}",
        f"- push_attempted: {len(results)}",
        f"- kernel_runs_started: {succeeded}",
        f"- notebooks_created_or_updated: {created}",
        "- competition_submission_executed: false",
        "",
        "| kernel | run started | created but GPU-blocked | return code |",
        "|---|---:|---:|---:|",
    ]
    for item in results:
        rows.append(
            f"| `{item['kernel_id']}` | {str(item['success']).lower()} | "
            f"{str(item.get('notebook_created_run_blocked', False)).lower()} | {item['returncode']} |"
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
