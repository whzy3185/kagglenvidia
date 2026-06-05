from __future__ import annotations

import csv
import re
import subprocess
from datetime import date, datetime
from io import StringIO
from pathlib import Path
from typing import Any

from .provenance import ensure_dir, today_stamp, write_json
from .reporting import markdown_table, write_text
from .safety import redact_sensitive


DEFAULT_COMPETITION = "nvidia-nemotron-model-reasoning-challenge"
DAILY_LIMIT = 5
COMMAND_TIMEOUT_SECONDS = 180


def run_command(args: list[str], cwd: Path | None = None) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            args,
            cwd=str(cwd) if cwd else None,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
            check=False,
        )
        return {
            "args": args,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "ok": completed.returncode == 0,
            "error": None,
        }
    except FileNotFoundError as exc:
        return {"args": args, "returncode": None, "stdout": "", "stderr": "", "ok": False, "error": str(exc)}
    except subprocess.TimeoutExpired as exc:
        return {
            "args": args,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "ok": False,
            "error": f"timeout_after_{COMMAND_TIMEOUT_SECONDS}s",
        }


def check_kaggle_cli(project_root: Path, competition: str = DEFAULT_COMPETITION) -> dict[str, Any]:
    logs_dir = ensure_dir(project_root / "logs")
    reports_dir = ensure_dir(project_root / "reports")
    version_result = run_command(["kaggle", "--version"], cwd=project_root)
    query_result = query_submissions_raw(project_root, competition, force=True)
    parsed = parse_submissions(query_result["raw_text"])
    parsed_path = logs_dir / f"submissions_parsed_{today_stamp()}.json"
    write_json(parsed_path, parsed)

    report = {
        "competition": competition,
        "kaggle_version_ok": version_result["ok"],
        "kaggle_version_output": redact_sensitive((version_result["stdout"] or version_result["stderr"]).strip()),
        "submissions_query_ok": query_result["command_ok"],
        "submission_history_query_status": parsed["submission_history_query_status"],
        "submission_history_query_success": parsed["submission_history_query_success"],
        "authentication_status": parsed["authentication_status"],
        "raw_result": parsed["raw_result"],
        "raw_submission_rows_saved": query_result["raw_path"].relative_to(project_root).as_posix(),
        "parsed_output": parsed_path.relative_to(project_root).as_posix(),
        "today_submission_count_parse_status": parsed["today_submission_count_parse_status"],
        "today_submission_count_timezone_assumption": parsed["today_submission_count_timezone_assumption"],
        "today_submission_count": parsed["today_submission_count"],
        "today_remaining_quota": parsed["today_remaining_quota"],
        "submissions_rows_parsed": len(parsed["submissions"]),
        "submissions_query_error": redact_sensitive(query_result.get("error") or ""),
    }
    report_path = reports_dir / "kaggle_cli_check.md"
    write_text(report_path, render_kaggle_cli_report(report))
    report["report_path"] = report_path.relative_to(project_root).as_posix()
    return report


def query_submissions_raw(project_root: Path, competition: str = DEFAULT_COMPETITION, force: bool = False) -> dict[str, Any]:
    logs_dir = ensure_dir(project_root / "logs")
    raw_path = logs_dir / f"submissions_raw_{today_stamp()}.txt"
    if raw_path.exists() and raw_path.stat().st_size > 0 and not force:
        raw_text = raw_path.read_text(encoding="utf-8", errors="replace")
        cached_ok = _raw_looks_like_no_submissions(raw_text) or not _raw_looks_like_query_failure(raw_text)
        return {
            "raw_path": raw_path,
            "raw_text": raw_text,
            "command_ok": cached_ok,
            "from_cache": True,
            "error": None if cached_ok else _first_error_line(raw_text),
        }

    command = ["kaggle", "competitions", "submissions", competition, "-v"]
    result = run_command(command, cwd=project_root)
    raw_text = result["stdout"]
    if result["stderr"]:
        raw_text = raw_text + ("\n" if raw_text else "") + result["stderr"]
    raw_path.write_text(raw_text, encoding="utf-8", newline="\n")
    error = result["error"]
    no_submissions = _raw_looks_like_no_submissions(raw_text)
    command_ok = result["ok"] or no_submissions
    if no_submissions:
        error = None
    if not command_ok and not error:
        error = (result["stderr"] or result["stdout"] or "unknown_kaggle_cli_error").strip()
    return {
        "raw_path": raw_path,
        "raw_text": raw_text,
        "command_ok": command_ok,
        "from_cache": False,
        "error": error,
        "returncode": result["returncode"],
    }


def _raw_looks_like_query_failure(raw_text: str) -> bool:
    if _raw_looks_like_no_submissions(raw_text):
        return False
    lower = raw_text.lower()
    failure_markers = [
        "authentication required to call the kaggle api",
        "403 - forbidden",
        "401 - unauthorized",
        "could not find competition",
        "invalid api credentials",
    ]
    return any(marker in lower for marker in failure_markers)


def _raw_looks_like_auth_failure(raw_text: str) -> bool:
    lower = raw_text.lower()
    auth_markers = [
        "authentication required to call the kaggle api",
        "401 - unauthorized",
        "invalid api credentials",
    ]
    return any(marker in lower for marker in auth_markers)


def _raw_looks_like_no_submissions(raw_text: str) -> bool:
    return any(line.strip().lower() == "no submissions found" for line in raw_text.splitlines())


def _first_error_line(raw_text: str) -> str:
    for line in raw_text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return "unknown_kaggle_cli_error"


def query_submission_history(project_root: Path, competition: str = DEFAULT_COMPETITION, force: bool = False) -> dict[str, Any]:
    raw = query_submissions_raw(project_root, competition, force=force)
    parsed = parse_submissions(raw["raw_text"])
    parsed_path = project_root / "logs" / f"submissions_parsed_{today_stamp()}.json"
    write_json(parsed_path, parsed)
    scorecard_path = project_root / "reports" / "SCORECARD.md"
    write_text(scorecard_path, render_scorecard(raw, parsed, project_root))
    return {
        "raw": raw,
        "parsed": parsed,
        "parsed_path": parsed_path,
        "scorecard_path": scorecard_path,
        "query_ok": raw["command_ok"],
    }


def parse_submissions(raw_text: str) -> dict[str, Any]:
    lines = [line.rstrip("\n") for line in raw_text.splitlines()]
    raw_result = raw_text.strip()
    no_submissions = _raw_looks_like_no_submissions(raw_text)
    rows, parse_mode = _parse_csv_rows(lines)
    if rows is None:
        rows, parse_mode = _parse_table_rows(lines)
    if rows is None:
        rows = [] if no_submissions else []
        parse_status = "success" if no_submissions else "failed"
        parse_mode = "no_submissions" if no_submissions else "unknown"
    else:
        parse_status = "success"

    normalized_rows = [_normalize_row(row) for row in rows]
    count_result = _count_today(normalized_rows)
    if parse_status != "success":
        count_result = {
            "today_submission_count_parse_status": "failed",
            "today_submission_count": None,
            "today_remaining_quota": None,
            "today_submission_count_timezone_assumption": "unknown",
        }
    authentication_status = "failed" if _raw_looks_like_auth_failure(raw_text) else "success" if parse_status == "success" else "unknown"
    submission_history_query_status = "success" if parse_status == "success" else "authentication_failed" if authentication_status == "failed" else "failed"

    return {
        "submission_history_query_status": submission_history_query_status,
        "submission_history_query_success": submission_history_query_status == "success",
        "raw_result": raw_result,
        "submissions": normalized_rows,
        "authentication_status": authentication_status,
        "parse_status": parse_status,
        "parse_mode": parse_mode,
        "rows": normalized_rows,
        **count_result,
    }


def _parse_csv_rows(lines: list[str]) -> tuple[list[dict[str, str]] | None, str | None]:
    for index, line in enumerate(lines):
        lower = line.lower()
        if "," in line and "date" in lower and ("status" in lower or "score" in lower):
            candidate = "\n".join(lines[index:])
            try:
                reader = csv.DictReader(StringIO(candidate))
                rows = [dict(row) for row in reader if any((value or "").strip() for value in row.values())]
            except csv.Error:
                return None, None
            return rows, "csv"
    return None, None


def _parse_table_rows(lines: list[str]) -> tuple[list[dict[str, str]] | None, str | None]:
    header_index = None
    for index, line in enumerate(lines):
        lower = line.lower()
        if "date" in lower and ("status" in lower or "public" in lower) and re.search(r"\s{2,}", line):
            header_index = index
            break
    if header_index is None:
        return None, None

    headers = [part.strip() for part in re.split(r"\s{2,}", lines[header_index].strip()) if part.strip()]
    rows: list[dict[str, str]] = []
    for line in lines[header_index + 1 :]:
        if not line.strip() or re.fullmatch(r"[-\s]+", line):
            continue
        values = [part.strip() for part in re.split(r"\s{2,}", line.strip())]
        if len(values) < 2:
            continue
        if len(values) < len(headers):
            values.extend([""] * (len(headers) - len(values)))
        rows.append(dict(zip(headers, values[: len(headers)])))
    return rows, "fixed_width_table"


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    lowered = {_normalize_key(key): value for key, value in row.items()}
    return {
        "submission_id": _first(lowered, ["submissionid", "submission_id", "id", "ref"]),
        "file_name": _first(lowered, ["filename", "file", "name"]),
        "date": _first(lowered, ["date", "submitted", "submittedat", "created"]),
        "description": _first(lowered, ["description", "desc"]),
        "status": _first(lowered, ["status"]),
        "public_score": _first(lowered, ["publicscore", "public_score", "score"]),
        "private_score": _first(lowered, ["privatescore", "private_score"]),
        "raw": row,
    }


def _normalize_key(key: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(key).strip().lower())


def _first(row: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return None


def _count_today(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "today_submission_count_parse_status": "success",
            "today_submission_count": 0,
            "today_remaining_quota": DAILY_LIMIT,
            "today_submission_count_timezone_assumption": "local_system",
        }

    today = date.today()
    count = 0
    dated_rows = 0
    for row in rows:
        parsed_date = _parse_row_date(row.get("date"))
        if parsed_date is None:
            continue
        dated_rows += 1
        if parsed_date == today:
            count += 1
    if dated_rows == 0:
        return {
            "today_submission_count_parse_status": "failed",
            "today_submission_count": None,
            "today_remaining_quota": None,
            "today_submission_count_timezone_assumption": "unknown",
        }
    return {
        "today_submission_count_parse_status": "success",
        "today_submission_count": count,
        "today_remaining_quota": max(DAILY_LIMIT - count, 0),
        "today_submission_count_timezone_assumption": "local_system",
    }


def _parse_row_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    match = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if match:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(text[: len(datetime.now().strftime(fmt))], fmt).date()
        except ValueError:
            continue
    return None


def render_kaggle_cli_report(report: dict[str, Any]) -> str:
    error = report["submissions_query_error"] or "null"
    error_summary = error.splitlines()[0] if error else "null"
    return f"""# Kaggle CLI Check

- competition: `{report['competition']}`
- kaggle_version_ok: {report['kaggle_version_ok']}
- kaggle_version_output: `{report['kaggle_version_output'] or 'unknown'}`
- submissions_query_ok: {report['submissions_query_ok']}
- submission_history_query_status: {report['submission_history_query_status']}
- submission_history_query_success: {report['submission_history_query_success']}
- authentication_status: {report['authentication_status']}
- raw_result: `{redact_sensitive(str(report['raw_result'])) or 'unknown'}`
- raw_submission_rows_saved: `{report['raw_submission_rows_saved']}`
- parsed_output: `{report['parsed_output']}`
- today_submission_count_parse_status: {report['today_submission_count_parse_status']}
- today_submission_count_timezone_assumption: {report['today_submission_count_timezone_assumption']}
- today_submission_count: {report['today_submission_count']}
- today_remaining_quota: {report['today_remaining_quota']}
- submissions_rows_parsed: {report['submissions_rows_parsed']}
- submissions_query_error: `{error_summary}`

Note: today's submission count is parsed conservatively from Kaggle CLI output.
If the output format cannot be parsed, this report will not fabricate a count.
"""


def render_scorecard(raw: dict[str, Any], parsed: dict[str, Any], project_root: Path) -> str:
    rows = [
        [
            row.get("submission_id"),
            row.get("date"),
            row.get("description"),
            row.get("status"),
            row.get("public_score"),
        ]
        for row in parsed["rows"]
    ]
    table = markdown_table(["submission_id", "date", "description", "status", "public_score"], rows) if rows else "No parsed submission rows."
    raw_path = raw["raw_path"].relative_to(project_root).as_posix()
    return f"""# Scorecard

- raw_submission_rows_saved: `{raw_path}`
- query_ok: {raw['command_ok']}
- submission_history_query_status: {parsed['submission_history_query_status']}
- submission_history_query_success: {parsed['submission_history_query_success']}
- authentication_status: {parsed['authentication_status']}
- raw_result: `{redact_sensitive(parsed['raw_result']) or 'unknown'}`
- parse_status: {parsed['parse_status']}
- today_submission_count_parse_status: {parsed['today_submission_count_parse_status']}
- today_submission_count_timezone_assumption: {parsed['today_submission_count_timezone_assumption']}
- today_submission_count: {parsed['today_submission_count']}
- today_remaining_quota: {parsed['today_remaining_quota']}

{table}
"""
