from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.kaggle_cli import check_kaggle_cli  # noqa: E402


def main() -> int:
    report = check_kaggle_cli(PROJECT_ROOT)
    print(f"report: {report['report_path']}")
    if not report["kaggle_version_ok"]:
        return 1
    if not report["submissions_query_ok"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
