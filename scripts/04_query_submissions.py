from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.kaggle_cli import query_submission_history  # noqa: E402
from nemotron086.score_db import upsert_submissions  # noqa: E402


def main() -> int:
    result = query_submission_history(PROJECT_ROOT)
    parsed = result["parsed"]
    db_path = PROJECT_ROOT / "logs" / "score.db"
    db_rows = upsert_submissions(db_path, parsed["rows"])
    print(f"scorecard: {result['scorecard_path'].relative_to(PROJECT_ROOT).as_posix()}")
    print(f"score_db: {db_path.relative_to(PROJECT_ROOT).as_posix()}")
    print(f"score_db_rows_upserted: {db_rows}")
    print(f"parse_status: {parsed['parse_status']}")
    print(f"today_submission_count_parse_status: {parsed['today_submission_count_parse_status']}")
    print(f"today_submission_count: {parsed['today_submission_count']}")
    return 0 if result["query_ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
