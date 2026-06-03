from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from .provenance import ensure_dir


def init_score_db(path: Path) -> Path:
    ensure_dir(path.parent)
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
              submission_id TEXT PRIMARY KEY,
              submitted_at TEXT,
              description TEXT,
              status TEXT,
              public_score TEXT,
              private_score TEXT,
              source TEXT
            )
            """
        )
        conn.commit()
    return path


def upsert_submissions(path: Path, rows: list[dict[str, Any]], source: str = "kaggle_cli") -> int:
    init_score_db(path)
    with sqlite3.connect(path) as conn:
        for row in rows:
            submission_id = str(row.get("submission_id") or row.get("date") or row.get("description") or len(rows))
            conn.execute(
                """
                INSERT INTO submissions
                  (submission_id, submitted_at, description, status, public_score, private_score, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(submission_id) DO UPDATE SET
                  submitted_at=excluded.submitted_at,
                  description=excluded.description,
                  status=excluded.status,
                  public_score=excluded.public_score,
                  private_score=excluded.private_score,
                  source=excluded.source
                """,
                (
                    submission_id,
                    row.get("date"),
                    row.get("description"),
                    row.get("status"),
                    row.get("public_score"),
                    row.get("private_score"),
                    source,
                ),
            )
        conn.commit()
    return len(rows)


def fetch_scores(path: Path) -> list[dict[str, Any]]:
    init_score_db(path)
    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM submissions ORDER BY submitted_at DESC").fetchall()
    return [dict(row) for row in rows]
