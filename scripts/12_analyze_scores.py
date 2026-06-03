from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.kaggle_cli import query_submission_history  # noqa: E402
from nemotron086.score_db import fetch_scores, upsert_submissions  # noqa: E402
from nemotron086.reporting import markdown_table  # noqa: E402


def main() -> int:
    history = query_submission_history(PROJECT_ROOT)
    db_path = PROJECT_ROOT / "logs" / "score.db"
    upsert_submissions(db_path, history["parsed"]["rows"])
    rows = fetch_scores(db_path)
    table = markdown_table(["submitted_at", "description", "status", "public_score"], [[r["submitted_at"], r["description"], r["status"], r["public_score"]] for r in rows])
    (PROJECT_ROOT / "reports" / "SCORE_ANALYSIS.md").write_text("# Score Analysis\n\n" + table + "\n", encoding="utf-8")
    print("report: reports/SCORE_ANALYSIS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
