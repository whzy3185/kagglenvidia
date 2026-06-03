from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.proxy_eval import (  # noqa: E402
    evaluate_predictions,
    load_predictions,
    load_proxy_set,
    write_stage3_completion_report,
    write_proxy_eval_readiness,
    write_proxy_eval_report,
)
from nemotron086.provenance import write_json  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", default="eval/proxy_set")
    parser.add_argument("--predictions", required=False)
    parser.add_argument("--stage2-manifest", default="artifacts/stage2/tong_full_repro/stage2_manifest.json")
    args = parser.parse_args()

    samples_path = PROJECT_ROOT / args.samples
    samples, issues = load_proxy_set(samples_path)
    stage2_manifest_path = PROJECT_ROOT / args.stage2_manifest
    stage2_manifest = {}
    if stage2_manifest_path.exists():
        import json

        stage2_manifest = json.loads(stage2_manifest_path.read_text(encoding="utf-8"))

    if not args.predictions:
        write_proxy_eval_readiness(
            PROJECT_ROOT,
            samples,
            issues,
            stage2_manifest,
            "missing predictions file; no local base model inference was run",
        )
        completion = write_stage3_completion_report(PROJECT_ROOT, samples, issues, None, None, stage2_manifest)
        write_json(PROJECT_ROOT / "artifacts" / "stage3" / "proxy_eval_manifest.json", completion)
        print("report: reports/PROXY_EVAL_READINESS.md")
        print("status: blocked_by_missing_predictions")
        return 5

    predictions_path = PROJECT_ROOT / args.predictions
    predictions = load_predictions(predictions_path)
    result = evaluate_predictions(samples, predictions)
    write_proxy_eval_report(PROJECT_ROOT, result, predictions_path=predictions_path)
    completion = write_stage3_completion_report(PROJECT_ROOT, samples, issues, result, predictions_path, stage2_manifest)
    write_json(PROJECT_ROOT / "artifacts" / "stage3" / "proxy_eval_manifest.json", completion)
    print("report: reports/PROXY_EVAL_REPORT.md")
    return 0 if result["missing_predictions"] == 0 else 4


if __name__ == "__main__":
    raise SystemExit(main())
