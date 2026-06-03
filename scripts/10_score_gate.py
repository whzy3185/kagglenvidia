from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.score_gate import evaluate_candidate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-manifest", required=True)
    args = parser.parse_args()
    result = evaluate_candidate(PROJECT_ROOT, PROJECT_ROOT / args.candidate_manifest)
    print(f"allowed: {result['allowed']}")
    print("report: reports/SCORE_GATE_RESULT.md")
    return 0 if result["allowed"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
