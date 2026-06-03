from __future__ import annotations


def trace_validity(text: str) -> bool:
    stripped = (text or "").strip()
    return bool(stripped) and "hidden test" not in stripped.lower()
