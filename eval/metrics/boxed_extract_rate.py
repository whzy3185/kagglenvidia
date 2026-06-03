from __future__ import annotations

import re


BOXED_RE = re.compile(r"\\boxed\{([^{}]+)\}")


def extract_boxed(text: str) -> str | None:
    match = BOXED_RE.search(text or "")
    return match.group(1).strip() if match else None


def boxed_extract_rate(outputs: list[str]) -> float:
    if not outputs:
        return 0.0
    return sum(1 for output in outputs if extract_boxed(output) is not None) / len(outputs)
