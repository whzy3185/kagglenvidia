from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.adapter_validator import validate_adapter  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter-dir", required=True)
    args = parser.parse_args()
    report = validate_adapter(Path(args.adapter_dir), PROJECT_ROOT)
    print(f"json_report: {report['json_report_path']}")
    print(f"markdown_report: {report['markdown_report_path']}")
    print(f"structural_valid: {report['structural_valid']}")
    return 0 if report["structural_valid"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
