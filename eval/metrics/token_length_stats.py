from __future__ import annotations


def token_length_stats(outputs: list[str]) -> dict[str, float]:
    lengths = [len((output or "").split()) for output in outputs]
    if not lengths:
        return {"count": 0, "avg": 0.0, "max": 0.0}
    return {"count": len(lengths), "avg": sum(lengths) / len(lengths), "max": max(lengths)}
