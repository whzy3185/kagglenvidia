from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.submission_packer import pack_submission  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter-dir", required=True)
    args = parser.parse_args()
    result = pack_submission(Path(args.adapter_dir), PROJECT_ROOT)
    print(f"status: {result['status']}")
    print(f"submission_zip: {result.get('zip_path')}")
    if result["packed"]:
        print(f"manifest: {result['manifest_path']}")
        print(f"pack_report: {result['pack_report_path']}")
        return 0
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
