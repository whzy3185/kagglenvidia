from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from .provenance import ensure_dir


def write_text(path: Path, content: str) -> Path:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
        if not content.endswith("\n"):
            handle.write("\n")
    return path


def yes_no_unknown(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    return str(value)


def markdown_table(headers: list[str], rows: Iterable[Iterable[Any]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(_cell(value) for value in row) + " |")
    return "\n".join([header, separator, *body])


def _cell(value: Any) -> str:
    text = yes_no_unknown(value)
    return text.replace("\n", " ").replace("|", "\\|")
