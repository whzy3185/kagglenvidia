from __future__ import annotations


def numeric_exact_or_tolerance(predicted: str, expected: str, tolerance: float = 1e-6) -> bool:
    try:
        return abs(float(predicted) - float(expected)) <= tolerance
    except (TypeError, ValueError):
        return str(predicted).strip() == str(expected).strip()
