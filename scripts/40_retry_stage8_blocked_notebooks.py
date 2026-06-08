from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_CONFIG = PROJECT_ROOT / "configs" / "stage8_tomorrow_submission_packages.yaml"
RETRY_CONFIG = PROJECT_ROOT / "configs" / "stage8_retry_submission_packages.yaml"
REPORT_PATH = PROJECT_ROOT / "reports" / "STAGE8_RETRY_BLOCKED_NOTEBOOKS.md"

RETRY_SLUGS = {
    "nemotron-s8-attn-mamba-no-lmhead-v1": "nemotron-s8-attn-mamba-no-lmhead-run2",
    "nemotron-s8-mlp-mamba-no-lmhead-v1": "nemotron-s8-mlp-mamba-no-lmhead-run2",
    "nemotron-s8-rank-stable-alpha64-v1": "nemotron-s8-rank-stable-alpha64-run2",
}


def main() -> int:
    payload = json.loads(SOURCE_CONFIG.read_text(encoding="utf-8"))
    retry_candidates = []
    for candidate in payload.get("candidates", []):
        if candidate["slug"] not in RETRY_SLUGS:
            continue
        retry_candidates.append(copy_candidate(candidate, RETRY_SLUGS[candidate["slug"]]))
    if len(retry_candidates) != len(RETRY_SLUGS):
        raise RuntimeError(f"Expected {len(RETRY_SLUGS)} retry candidates, found {len(retry_candidates)}")
    retry_payload = {
        "stage": "8_retry",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "competition_submission_executed": False,
        "candidates": retry_candidates,
    }
    RETRY_CONFIG.write_text(json.dumps(retry_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(retry_candidates)
    for item in retry_candidates:
        print(f"{item['slug']}: {item['kernel_dir']}")
    print(f"config={RETRY_CONFIG.relative_to(PROJECT_ROOT)}")
    print(f"report={REPORT_PATH.relative_to(PROJECT_ROOT)}")
    return 0


def copy_candidate(candidate: dict[str, Any], new_remote_slug: str) -> dict[str, Any]:
    source_dir = PROJECT_ROOT / candidate["kernel_dir"]
    if not source_dir.exists():
        raise FileNotFoundError(source_dir)
    source_notebook = PROJECT_ROOT / candidate["notebook_path"]
    source_metadata = PROJECT_ROOT / candidate["metadata_path"]
    new_folder = new_remote_slug.replace("-", "_")
    dest_dir = PROJECT_ROOT / "kaggle_kernels" / new_folder
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_notebook_name = f"{new_folder}.ipynb"
    dest_notebook = dest_dir / dest_notebook_name
    dest_metadata = dest_dir / "kernel-metadata.json"
    shutil.copyfile(source_notebook, dest_notebook)
    metadata = json.loads(source_metadata.read_text(encoding="utf-8"))
    metadata["id"] = f"muelsyse111/{new_remote_slug}"
    metadata["title"] = metadata.get("title", new_remote_slug).replace(" V1", " Run2")
    metadata["code_file"] = dest_notebook_name
    metadata.pop("id_no", None)
    dest_metadata.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        **candidate,
        "slug": new_remote_slug,
        "kernel_id": metadata["id"],
        "kernel_dir": str(dest_dir.relative_to(PROJECT_ROOT)),
        "metadata_path": str(dest_metadata.relative_to(PROJECT_ROOT)),
        "notebook_path": str(dest_notebook.relative_to(PROJECT_ROOT)),
        "push_command": f'kaggle kernels push -p "{dest_dir.relative_to(PROJECT_ROOT)}"',
        "source_candidate": candidate["slug"],
        "competition_submit_called": False,
    }


def write_report(candidates: list[dict[str, Any]]) -> None:
    rows = [
        "# Stage 8 Retry Blocked Notebooks",
        "",
        f"- generated_at: {datetime.now().isoformat(timespec='seconds')}",
        "- reason: original remote slugs returned Kaggle `Notebook not found` after GPU-blocked push attempts",
        "- competition_submission_executed: false",
        "",
        "| retry candidate | source candidate | kernel | command |",
        "|---|---|---|---|",
    ]
    for item in candidates:
        rows.append(
            f"| `{item['slug']}` | `{item['source_candidate']}` | `{item['kernel_id']}` | `{item['push_command']}` |"
        )
    rows.extend(
        [
            "",
            "These retry notebooks preserve the same code path and only change the remote Kaggle slug/code filename.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(rows), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
