from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.stage3_prediction_ingest import ingest_predictions  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", default="eval/proxy_set")
    parser.add_argument("--predictions", default="artifacts/stage3/proxy_predictions.jsonl")
    parser.add_argument("--stage2-manifest", default="artifacts/stage2/tong_full_repro/stage2_manifest.json")
    args = parser.parse_args()

    payload = ingest_predictions(
        PROJECT_ROOT,
        PROJECT_ROOT / args.samples,
        PROJECT_ROOT / args.predictions,
        PROJECT_ROOT / args.stage2_manifest,
    )
    print("report: reports/STAGE3_PREDICTION_INGEST.md")
    print(f"status: {payload['status']}")
    if payload["can_evaluate"]:
        print("proxy_eval_report: reports/PROXY_EVAL_REPORT.md")
        return 0
    if not payload["predictions_file_exists"]:
        return 5
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
