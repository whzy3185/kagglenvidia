from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kernel_ref", nargs="?", default="username/nemotron-086plus-baseline-repro")
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args()
    if not args.yes:
        write_report("dry_run", "Refusing to download kernel output without --yes.")
        return 5
    out_dir = PROJECT_ROOT / "artifacts" / "kernel_output"
    out_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(["kaggle", "kernels", "output", args.kernel_ref, "-p", str(out_dir)], cwd=str(PROJECT_ROOT), text=True, capture_output=True)
    (PROJECT_ROOT / "logs" / "kernel_output_download.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    has_adapter = (out_dir / "adapter_config.json").exists() and (out_dir / "adapter_model.safetensors").exists()
    write_report("success" if result.returncode == 0 else "failed", f"has_adapter={has_adapter}")
    return result.returncode if result.returncode != 0 else 0 if has_adapter else 4


def write_report(status: str, detail: str) -> None:
    (PROJECT_ROOT / "reports" / "KERNEL_OUTPUT_STATUS.md").write_text(f"# Kernel Output Status\n\n- status: {status}\n- detail: `{detail}`\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
