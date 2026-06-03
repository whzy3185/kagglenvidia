from __future__ import annotations

from collections import defaultdict


def category_breakdown(rows: list[dict]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "correct": 0})
    for row in rows:
        category = row.get("category", "unknown")
        result[category]["total"] += 1
        result[category]["correct"] += int(bool(row.get("correct")))
    return dict(result)
