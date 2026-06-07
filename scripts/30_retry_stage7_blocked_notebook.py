from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "configs" / "stage7_diverse_notebook_candidates.yaml"
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish one GPU-blocked Stage 7 notebook under a fresh retry slug."
    )
    parser.add_argument("--candidate", required=True, help="Local candidate slug from the Stage 7 config.")
    parser.add_argument("--suffix", default="v2", help="Fresh remote slug suffix.")
    parser.add_argument("--push", action="store_true", help="Push the generated retry notebook to Kaggle.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    candidates = {item["slug"]: item for item in payload.get("candidates", [])}
    if args.candidate not in candidates:
        raise SystemExit(f"Unknown candidate: {args.candidate}")

    candidate = candidates[args.candidate]
    if candidate["route_type"] not in {"full_training", "muon_training"}:
        raise SystemExit("Retry helper is limited to GPU training candidates.")

    source_dir = PROJECT_ROOT / candidate["kernel_dir"]
    source_metadata = json.loads((source_dir / "kernel-metadata.json").read_text(encoding="utf-8"))
    retry_slug = f"{candidate['kernel_id'].split('/', 1)[1]}-{args.suffix}"
    retry_dir = source_dir.with_name(f"{source_dir.name}_{args.suffix}")
    if retry_dir.exists():
        shutil.rmtree(retry_dir)
    shutil.copytree(source_dir, retry_dir)

    retry_metadata_path = retry_dir / "kernel-metadata.json"
    retry_metadata = dict(source_metadata)
    retry_metadata["id"] = f"muelsyse111/{retry_slug}"
    retry_metadata["title"] = f"{source_metadata['title']} {args.suffix.upper()}"
    retry_metadata_path.write_text(
        json.dumps(retry_metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    report_path = (
        PROJECT_ROOT
        / "reports"
        / f"STAGE7_BLOCKED_NOTEBOOK_RETRY_{args.candidate}_{args.suffix}.md"
    )

    command = ["kaggle", "kernels", "push", "-p", str(retry_dir)]
    completed = None
    if args.push:
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
            timeout=300,
            check=False,
        )

    output = ""
    if completed is not None:
        output = (completed.stdout + "\n" + completed.stderr).strip()
    run_started = "successfully pushed" in output.lower() and "kernel push error" not in output.lower()
    gpu_blocked = "maximum batch gpu session count" in output.lower()
    rows = [
        "# Stage 7 Blocked Notebook Retry",
        "",
        f"- updated_at: {datetime.now().isoformat(timespec='seconds')}",
        f"- source_candidate: `{candidate['slug']}`",
        f"- source_kernel_id: `{candidate['kernel_id']}`",
        f"- retry_kernel_id: `{retry_metadata['id']}`",
        f"- retry_kernel_dir: `{retry_dir.relative_to(PROJECT_ROOT)}`",
        f"- full_training_amount_preserved: true",
        f"- push_requested: {str(args.push).lower()}",
        f"- run_started: {str(run_started).lower()}",
        f"- gpu_session_blocked: {str(gpu_blocked).lower()}",
        "- competition_submission_executed: false",
        "",
        "## Command",
        "",
        f"`{' '.join(command)}`",
        "",
        "## Output",
        "",
        "```text",
        output or "(not pushed)",
        "```",
        "",
    ]
    report_path.write_text("\n".join(rows), encoding="utf-8")
    print(f"retry_kernel_id={retry_metadata['id']}")
    print(f"retry_kernel_dir={retry_dir}")
    print(f"run_started={str(run_started).lower()}")
    print(f"gpu_session_blocked={str(gpu_blocked).lower()}")
    print(f"report={report_path}")
    if not args.push:
        return 0
    return 0 if run_started else 2


if __name__ == "__main__":
    raise SystemExit(main())
