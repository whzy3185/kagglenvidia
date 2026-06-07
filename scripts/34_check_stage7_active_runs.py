from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "reports" / "STAGE7_ACTIVE_RUNS.md"
ACTIVE_KERNELS = [
    {
        "kernel_id": "muelsyse111/nemotron-s7-protected-rehearsal-v2",
        "mechanism": "protected_category_loss_reweighting",
        "resource": "RTX Pro 6000",
    },
    {
        "kernel_id": "muelsyse111/nemotron-s7-muon-full-training-v5",
        "mechanism": "muon_optimizer_microbatch1_effective_batch16",
        "resource": "RTX Pro 6000",
    },
    {
        "kernel_id": "muelsyse111/nemotron-s7-muon-v5-audit",
        "mechanism": "muon_v5_structural_audit_and_repack",
        "resource": "CPU",
    },
    {
        "kernel_id": "muelsyse111/nemotron-s7-delta-space-svd-r32",
        "mechanism": "effective_delta_qr_svd_rank32_recompression",
        "resource": "CPU",
    },
    {
        "kernel_id": "muelsyse111/nemotron-s7-modulewise-delta-svd-r32",
        "mechanism": "module_family_weighted_delta_qr_svd_rank32",
        "resource": "CPU",
    },
    {
        "kernel_id": "muelsyse111/nemotron-s7-norm-balanced-delta-svd-r32",
        "mechanism": "per_module_delta_norm_balanced_qr_svd_rank32",
        "resource": "CPU",
    },
    {
        "kernel_id": "muelsyse111/nemotron-s7-weak-protected-curriculum-v2",
        "mechanism": "weak_category_plus_protected_interleaving",
        "resource": "RTX Pro 6000",
    },
    {
        "kernel_id": "muelsyse111/nemotron-s7-mamba-inproj-specialist-v2",
        "mechanism": "selective_mamba_in_proj_adaptation",
        "resource": "RTX Pro 6000",
    },
]


def main() -> int:
    results = [inspect(item) for item in ACTIVE_KERNELS]
    write_report(results)
    for item in results:
        print(f"{item['kernel_id']}: {item['state']}")
    print(f"report={REPORT_PATH.relative_to(PROJECT_ROOT)}")
    return 1 if any(item["state"] == "failed" for item in results) else 0


def inspect(item: dict[str, str]) -> dict[str, Any]:
    files = run(["kaggle", "kernels", "files", item["kernel_id"], "-v", "--page-size", "100"])
    logs = run(["kaggle", "kernels", "logs", item["kernel_id"]])
    text = decode_logs(logs["stdout"]) + "\n" + logs["stderr"]
    output_visible = "submission.zip" in files["stdout"]
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
    elif text.strip():
        state = "running_or_finalizing"
    else:
        state = "queued_no_logs"
    step_matches = re.findall(r"step\s+(\d+)\s*/\s*(\d+)", text, re.IGNORECASE)
    last_step = f"{step_matches[-1][0]}/{step_matches[-1][1]}" if step_matches else ""
    return {
        **item,
        "state": state,
        "output_visible": output_visible,
        "success_marker": success,
        "last_step": last_step,
        "cuda_available": extract(text, r"cuda_available:\s*(\S+)"),
        "zip_sha256": extract(
            text,
            r'(?:submission_zip_sha256["\s:]+)([0-9a-f]{64})',
        ),
        "zip_size_bytes": extract(
            text,
            r'(?:submission_zip_size_bytes["\s:]+)(\d+)',
        ),
        "error_excerpt": error_excerpt(text),
    }


def run(command: list[str]) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    completed = subprocess.run(
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
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


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
    return "\n".join(lines[start : indexes[-1] + 12])[:3000]


def write_report(results: list[dict[str, Any]]) -> None:
    rows = [
        "# Stage 7 Active Runs",
        "",
        f"- updated_at: {datetime.now().isoformat(timespec='seconds')}",
        "- status_source: Kaggle kernel files and logs",
        "- competition submission executed: false",
        "",
        "| kernel | resource | mechanism | state | step | CUDA | output | SHA256 |",
        "|---|---|---|---|---|---|---:|---|",
    ]
    for item in results:
        rows.append(
            f"| `{item['kernel_id']}` | {item['resource']} | `{item['mechanism']}` | "
            f"`{item['state']}` | `{item['last_step'] or 'n/a'}` | "
            f"`{item['cuda_available'] or 'n/a'}` | {str(item['output_visible']).lower()} | "
            f"`{item['zip_sha256'][:12] or 'n/a'}` |"
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
            "## Interpretation",
            "",
            "- `queued_no_logs`: Kaggle accepted the version but has not started notebook execution.",
            "- `running_or_finalizing`: logs exist and no terminal success/error marker is present.",
            "- `output_ready`: `submission.zip` is visible and the notebook printed the success marker.",
            "- `failed`: logs contain a terminal Python or Papermill exception.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(rows), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
