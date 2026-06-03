from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .provenance import ensure_dir
from .reporting import markdown_table, write_text


BOXED_RE = re.compile(r"\\boxed\{([^{}]+)\}")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_proxy_set(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    files = sorted(path.glob("*.jsonl")) if path.is_dir() else [path]
    samples: list[dict[str, Any]] = []
    issues: list[str] = []
    seen_ids: set[str] = set()
    required = {"id", "category", "prompt", "expected_answer", "verifier_type", "metadata"}
    for file_path in files:
        for row in load_jsonl(file_path):
            missing = sorted(required - set(row))
            if missing:
                issues.append(f"{file_path.relative_to(path if path.is_dir() else path.parent)} missing {missing} for row {row.get('id')}")
                continue
            sample_id = str(row["id"])
            if sample_id in seen_ids:
                issues.append(f"duplicate sample id: {sample_id}")
                continue
            seen_ids.add(sample_id)
            samples.append(row)
    return samples, issues


def load_predictions(path: Path) -> dict[str, str]:
    if path.suffix.lower() == ".jsonl":
        predictions: dict[str, str] = {}
        for row in load_jsonl(path):
            sample_id = row.get("id")
            output = row.get("output", row.get("prediction", row.get("response", "")))
            if sample_id:
                predictions[str(sample_id)] = str(output)
        return predictions
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return {str(key): str(value) for key, value in data.items()}
    if isinstance(data, list):
        predictions = {}
        for row in data:
            if not isinstance(row, dict):
                continue
            sample_id = row.get("id")
            output = row.get("output", row.get("prediction", row.get("response", "")))
            if sample_id:
                predictions[str(sample_id)] = str(output)
        return predictions
    raise ValueError("predictions must be a JSON object, JSON list, or JSONL rows")


def extract_answer(text: str) -> str | None:
    match = BOXED_RE.search(text or "")
    if match:
        return match.group(1).strip()
    stripped = (text or "").strip()
    return stripped or None


def verify_answer(sample: dict[str, Any], answer: str | None) -> bool:
    if answer is None:
        return False
    expected = str(sample.get("expected_answer", "")).strip()
    verifier_type = str(sample.get("verifier_type", "exact"))
    if verifier_type in {"numeric_tolerance", "python_eval"}:
        try:
            return abs(float(answer) - float(expected)) <= 1e-6
        except ValueError:
            return answer.strip() == expected
    return answer.strip().lower() == expected.lower()


def trace_is_valid(output: str) -> bool:
    stripped = (output or "").strip()
    if not stripped:
        return False
    lower = stripped.lower()
    forbidden = ["hidden test", "leaderboard", "kaggle score", "public score"]
    return not any(token in lower for token in forbidden)


def evaluate_predictions(samples: list[dict[str, Any]], predictions: dict[str, str]) -> dict[str, Any]:
    by_category: dict[str, Counter] = defaultdict(Counter)
    regressions = []
    boxed = 0
    exact = 0
    trace_valid = 0
    total = len(samples)
    lengths = []
    missing_predictions = 0
    for sample in samples:
        sample_id = sample["id"]
        category = sample.get("category", "unknown")
        expected = str(sample.get("expected_answer", "")).strip()
        output = predictions.get(sample_id, "")
        if sample_id not in predictions:
            missing_predictions += 1
        answer = extract_answer(output)
        if answer is not None and "\\boxed" in output:
            boxed += 1
            by_category[category]["boxed"] += 1
        valid_trace = trace_is_valid(output)
        if valid_trace:
            trace_valid += 1
            by_category[category]["trace_valid"] += 1
        ok = verify_answer(sample, answer)
        if ok:
            exact += 1
            by_category[category]["exact"] += 1
        else:
            regressions.append({"id": sample_id, "category": category, "expected": expected, "answer": answer})
        by_category[category]["total"] += 1
        lengths.append(len(output.split()))

    category_rows = []
    for category, counts in sorted(by_category.items()):
        total_cat = counts["total"]
        category_rows.append(
            {
                "category": category,
                "exact": counts["exact"],
                "total": total_cat,
                "exact_rate": counts["exact"] / total_cat if total_cat else 0.0,
                "boxed_rate": counts["boxed"] / total_cat if total_cat else 0.0,
                "trace_validity_rate": counts["trace_valid"] / total_cat if total_cat else 0.0,
            }
        )

    return {
        "total": total,
        "exact": exact,
        "overall_exact_rate": exact / total if total else 0.0,
        "boxed_extract_rate": boxed / total if total else 0.0,
        "trace_validity_rate": trace_valid / total if total else 0.0,
        "average_output_length": sum(lengths) / len(lengths) if lengths else 0.0,
        "missing_predictions": missing_predictions,
        "category_breakdown": category_rows,
        "regression_cases": regressions,
    }


def write_proxy_eval_report(project_root: Path, result: dict[str, Any], predictions_path: Path | None = None) -> None:
    reports_dir = ensure_dir(project_root / "reports")
    rows = [
        [
            row["category"],
            row["exact"],
            row["total"],
            f"{row['exact_rate']:.4f}",
            f"{row['boxed_rate']:.4f}",
            f"{row['trace_validity_rate']:.4f}",
        ]
        for row in result["category_breakdown"]
    ]
    report = f"""# Proxy Eval Report

Proxy eval is not the Kaggle score. It is a local pre-submit gate signal only.

- total: {result['total']}
- overall_exact_rate: {result['overall_exact_rate']:.4f}
- boxed_extract_rate: {result['boxed_extract_rate']:.4f}
- trace_validity_rate: {result['trace_validity_rate']:.4f}
- average_output_length: {result['average_output_length']:.2f}
- missing_predictions: {result['missing_predictions']}
- predictions_path: `{predictions_path.relative_to(project_root).as_posix() if predictions_path else 'unknown'}`

{markdown_table(['category', 'exact', 'total', 'exact_rate', 'boxed_rate', 'trace_validity_rate'], rows)}
"""
    write_text(reports_dir / "PROXY_EVAL_REPORT.md", report)
    with (reports_dir / "category_breakdown.csv").open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("category,exact,total,exact_rate,boxed_rate,trace_validity_rate\n")
        for row in result["category_breakdown"]:
            handle.write(
                f"{row['category']},{row['exact']},{row['total']},{row['exact_rate']:.6f},"
                f"{row['boxed_rate']:.6f},{row['trace_validity_rate']:.6f}\n"
            )
    with (reports_dir / "regression_cases.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for row in result["regression_cases"]:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_proxy_eval_readiness(
    project_root: Path,
    samples: list[dict[str, Any]],
    issues: list[str],
    stage2_manifest: dict[str, Any],
    reason: str,
) -> None:
    reports_dir = ensure_dir(project_root / "reports")
    categories = Counter(str(row.get("category", "unknown")) for row in samples)
    rows = [[category, count] for category, count in sorted(categories.items())]
    issues_text = "\n".join(f"- {issue}" for issue in issues) if issues else "- null"
    report = f"""# Stage 3 Proxy Eval Readiness

Stage 3 builds a proxy-eval gate. It does not claim Kaggle score equivalence.

- status: blocked_by_missing_predictions
- reason: {reason}
- stage2_route: {stage2_manifest.get('route')}
- stage2_structural_valid: {stage2_manifest.get('structural_valid')}
- stage2_submission_zip_generated: {stage2_manifest.get('submission_zip_generated')}
- base_model_loaded_locally: false
- inference_run_locally: false
- total_proxy_samples: {len(samples)}

## Category Coverage

{markdown_table(['category', 'samples'], rows)}

## Dataset Issues

{issues_text}

NEXT_ACTION:
  status: stay_stage3
  action: "generate proxy predictions for artifacts/stage2/tong_full_repro/submission/submission.zip on an approved GPU environment"
  reason: "proxy eval metrics require model outputs and this local run did not load the base model"
"""
    write_text(reports_dir / "PROXY_EVAL_READINESS.md", report)
    write_text(reports_dir / "STAGE3_PROXY_EVAL_STATUS.md", report)


def write_stage3_completion_report(
    project_root: Path,
    samples: list[dict[str, Any]],
    issues: list[str],
    result: dict[str, Any] | None,
    predictions_path: Path | None,
    stage2_manifest: dict[str, Any],
) -> dict[str, Any]:
    reports_dir = ensure_dir(project_root / "reports")
    complete = (
        bool(stage2_manifest.get("structural_valid"))
        and bool(stage2_manifest.get("submission_zip_generated"))
        and not issues
        and result is not None
        and result.get("missing_predictions") == 0
    )
    status = "complete" if complete else "blocked"
    reason = "proxy eval completed with candidate predictions" if complete else "proxy predictions are missing or incomplete"
    payload = {
        "stage": 3,
        "status": status,
        "complete": complete,
        "reason": reason,
        "proxy_samples": len(samples),
        "dataset_issues": issues,
        "predictions_path": predictions_path.relative_to(project_root).as_posix() if predictions_path else None,
        "stage2_structural_valid": stage2_manifest.get("structural_valid"),
        "stage2_submission_zip_generated": stage2_manifest.get("submission_zip_generated"),
        "proxy_eval_result": result,
        "can_enter_stage4": complete,
    }
    report = f"""# Stage 3 Completion Report

- stage: 3
- status: {status}
- complete: {complete}
- reason: {reason}
- proxy_samples: {len(samples)}
- predictions_path: `{payload['predictions_path'] or 'null'}`
- can_enter_stage4: {complete}

Stage 3 proxy eval is not the Kaggle score. It is only a local gate signal.
"""
    write_text(reports_dir / "STAGE3_COMPLETION_REPORT.md", report)
    return payload
