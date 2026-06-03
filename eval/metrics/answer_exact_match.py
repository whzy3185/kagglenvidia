from __future__ import annotations


def exact_match(predicted: str, expected: str) -> bool:
    return str(predicted).strip() == str(expected).strip()
