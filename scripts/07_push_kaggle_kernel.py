from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
KERNEL_DIR = PROJECT_ROOT / "kernels" / "baseline_repro"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--yes", action="store_true", help="Actually run kaggle kernels push")
    args = parser.parse_args()
    if not args.yes:
        write_failure("dry_run", "Refusing to push without --yes.")
        print("dry_run: add --yes to push after reviewing kernel metadata")
        return 5
    if not (KERNEL_DIR / "kernel-metadata.json").exists():
        write_failure("missing_kernel", "Run scripts/06_build_baseline_kernel.py first.")
        return 4
    result = subprocess.run(["kaggle", "kernels", "push", "-p", str(KERNEL_DIR)], cwd=str(PROJECT_ROOT), text=True, capture_output=True)
    (PROJECT_ROOT / "logs" / "kernel_push.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode != 0:
        write_failure("push_failed", result.stderr or result.stdout)
    return result.returncode


def write_failure(kind: str, detail: str) -> None:
    (PROJECT_ROOT / "reports" / "KERNEL_PUSH_FAILURE.md").write_text(f"# Kernel Push Failure\n\n- kind: {kind}\n- detail: `{detail}`\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
