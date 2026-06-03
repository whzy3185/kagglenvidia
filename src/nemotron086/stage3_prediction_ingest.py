from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .provenance import ensure_dir, write_json
from .proxy_eval import (
    evaluate_predictions,
    load_proxy_set,
    write_proxy_eval_report,
    write_stage3_completion_report,
)
from .reporting import markdown_table, write_text


def ingest_predictions(
    project_root: Path,
    samples_path: Path,
    predictions_path: Path,
    stage2_manifest_path: Path,
) -> dict[str, Any]:
    samples, dataset_issues = load_proxy_set(samples_path)
    stage2_manifest = read_optional_json(stage2_manifest_path)
    predictions, parse_issues, parse_stats = parse_prediction_file(predictions_path)
    coverage = validate_prediction_coverage(samples, predictions)
    all_issues = [*dataset_issues, *parse_issues, *coverage["blocking_issues"]]
    can_evaluate = predictions_path.exists() and not dataset_issues and not parse_issues and coverage["missing_count"] == 0

    result = None
    if can_evaluate:
        result = evaluate_predictions(samples, predictions)
        write_proxy_eval_report(project_root, result, predictions_path=predictions_path)
        completion = write_stage3_completion_report(project_root, samples, dataset_issues, result, predictions_path, stage2_manifest)
        write_json(project_root / "artifacts" / "stage3" / "proxy_eval_manifest.json", completion)
    else:
        completion = write_stage3_completion_report(project_root, samples, dataset_issues, None, None, stage2_manifest)
        write_json(project_root / "artifacts" / "stage3" / "proxy_eval_manifest.json", completion)

    payload = {
        "stage": 3,
        "status": "ready_to_evaluate" if can_evaluate else "blocked",
        "predictions_path": predictions_path.relative_to(project_root).as_posix(),
        "predictions_file_exists": predictions_path.exists(),
        "sample_count": len(samples),
        "prediction_count": len(predictions),
        "parse_stats": parse_stats,
        "dataset_issues": dataset_issues,
        "parse_issues": parse_issues,
        "coverage": coverage,
        "can_evaluate": can_evaluate,
        "proxy_eval_result": result,
        "stage3_completion": completion,
        "next_action": build_next_action(can_evaluate, predictions_path.exists(), all_issues),
    }
    write_json(project_root / "artifacts" / "stage3" / "prediction_ingest_manifest.json", payload)
    write_text(project_root / "reports" / "STAGE3_PREDICTION_INGEST.md", render_prediction_ingest(payload))
    return payload


def parse_prediction_file(path: Path) -> tuple[dict[str, str], list[str], dict[str, Any]]:
    predictions: dict[str, str] = {}
    issues: list[str] = []
    stats = {
        "format": None,
        "rows_seen": 0,
        "duplicate_ids": [],
        "rows_without_id": 0,
        "rows_without_output_field": 0,
        "empty_outputs": 0,
    }
    if not path.exists():
        return predictions, [f"prediction file missing: {path}"], stats

    try:
        if path.suffix.lower() == ".jsonl":
            stats["format"] = "jsonl"
            rows = []
            with path.open("r", encoding="utf-8") as handle:
                for line_number, line in enumerate(handle, start=1):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    try:
                        row = json.loads(stripped)
                    except json.JSONDecodeError as exc:
                        issues.append(f"line {line_number} is not valid JSON: {exc.msg}")
                        continue
                    rows.append(row)
            collect_prediction_rows(rows, predictions, issues, stats)
            return predictions, issues, stats

        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return predictions, [f"prediction file is not valid JSON: {exc.msg}"], stats

    if isinstance(data, dict):
        stats["format"] = "json_object"
        stats["rows_seen"] = len(data)
        for sample_id, output in data.items():
            output_text = str(output)
            if not output_text.strip():
                stats["empty_outputs"] += 1
            predictions[str(sample_id)] = output_text
        return predictions, issues, stats
    if isinstance(data, list):
        stats["format"] = "json_list"
        collect_prediction_rows(data, predictions, issues, stats)
        return predictions, issues, stats

    return predictions, ["predictions must be JSONL rows, a JSON object, or a JSON list"], stats


def collect_prediction_rows(
    rows: list[Any],
    predictions: dict[str, str],
    issues: list[str],
    stats: dict[str, Any],
) -> None:
    seen: set[str] = set()
    stats["rows_seen"] = len(rows)
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            issues.append(f"row {index} is not an object")
            continue
        sample_id = row.get("id")
        if not sample_id:
            stats["rows_without_id"] += 1
            issues.append(f"row {index} missing id")
            continue
        sample_id = str(sample_id)
        output_marker = next((key for key in ("output", "prediction", "response") if key in row), None)
        if output_marker is None:
            stats["rows_without_output_field"] += 1
            issues.append(f"row {index} missing output/prediction/response")
            continue
        if sample_id in seen:
            stats["duplicate_ids"].append(sample_id)
            issues.append(f"duplicate prediction id: {sample_id}")
            continue
        seen.add(sample_id)
        output = str(row.get(output_marker, ""))
        if not output.strip():
            stats["empty_outputs"] += 1
        predictions[sample_id] = output


def validate_prediction_coverage(samples: list[dict[str, Any]], predictions: dict[str, str]) -> dict[str, Any]:
    sample_ids = {str(sample["id"]) for sample in samples}
    prediction_ids = set(predictions)
    missing_ids = sorted(sample_ids - prediction_ids)
    extra_ids = sorted(prediction_ids - sample_ids)
    empty_output_ids = sorted(sample_id for sample_id, output in predictions.items() if sample_id in sample_ids and not output.strip())
    blocking_issues = []
    if missing_ids:
        blocking_issues.append(f"missing predictions for {len(missing_ids)} samples")
    category_missing = Counter(str(sample.get("category", "unknown")) for sample in samples if str(sample["id"]) in missing_ids)
    return {
        "sample_count": len(samples),
        "prediction_count": len(predictions),
        "missing_count": len(missing_ids),
        "extra_count": len(extra_ids),
        "empty_output_count": len(empty_output_ids),
        "missing_ids": missing_ids[:50],
        "extra_ids": extra_ids[:50],
        "empty_output_ids": empty_output_ids[:50],
        "missing_by_category": dict(sorted(category_missing.items())),
        "blocking_issues": blocking_issues,
    }


def render_prediction_ingest(payload: dict[str, Any]) -> str:
    coverage = payload["coverage"]
    result = payload.get("proxy_eval_result") or {}
    missing_rows = [[category, count] for category, count in coverage["missing_by_category"].items()]
    missing_table = markdown_table(["category", "missing"], missing_rows) if missing_rows else "- null"
    dataset_issues = lines_or_null(payload["dataset_issues"])
    parse_issues = lines_or_null(payload["parse_issues"])
    blocking_issues = lines_or_null(coverage["blocking_issues"])
    next_action = payload["next_action"]
    eval_section = (
        f"""## Proxy Eval Summary

- total: {result.get('total')}
- overall_exact_rate: {result.get('overall_exact_rate')}
- boxed_extract_rate: {result.get('boxed_extract_rate')}
- trace_validity_rate: {result.get('trace_validity_rate')}
- missing_predictions: {result.get('missing_predictions')}
"""
        if result
        else "## Proxy Eval Summary\n\n- not_run\n"
    )
    return f"""# Stage 3 Prediction Ingest

This report validates returned proxy predictions before marking Stage 3 complete. It does not claim an official Kaggle score.

- status: {payload['status']}
- predictions_file_exists: {payload['predictions_file_exists']}
- predictions_path: `{payload['predictions_path']}`
- sample_count: {payload['sample_count']}
- prediction_count: {payload['prediction_count']}
- can_evaluate: {payload['can_evaluate']}
- missing_count: {coverage['missing_count']}
- extra_count: {coverage['extra_count']}
- empty_output_count: {coverage['empty_output_count']}

## Dataset Issues

{dataset_issues}

## Parse Issues

{parse_issues}

## Blocking Issues

{blocking_issues}

## Missing By Category

{missing_table}

{eval_section}
NEXT_ACTION:
  status: {next_action['status']}
  action: "{next_action['action']}"
  reason: "{next_action['reason']}"
"""


def build_next_action(can_evaluate: bool, predictions_file_exists: bool, issues: list[str]) -> dict[str, str]:
    if can_evaluate:
        return {
            "status": "enter_stage4_readiness_check",
            "action": "python scripts/14_stage4_readiness.py",
            "reason": "Proxy predictions were ingested and evaluated locally.",
        }
    if not predictions_file_exists:
        return {
            "status": "stay_stage3",
            "action": "run the staged proxy eval kernel on Kaggle GPU and save proxy_predictions.jsonl under artifacts/stage3",
            "reason": "Stage 3 cannot complete until Kaggle GPU predictions are returned locally.",
        }
    action = "run the staged proxy eval kernel on Kaggle GPU and save proxy_predictions.jsonl under artifacts/stage3"
    if issues:
        action = "fix the prediction file issues listed above, then rerun this ingest script"
    return {
        "status": "stay_stage3",
        "action": action,
        "reason": "Stage 3 cannot complete until every proxy sample has one parseable prediction.",
    }


def lines_or_null(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- null"


def read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
