from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.reporting import write_text  # noqa: E402


def main() -> int:
    stage2 = read_json(PROJECT_ROOT / "artifacts" / "stage2" / "tong_full_repro" / "stage2_manifest.json")
    stage3 = read_json(PROJECT_ROOT / "artifacts" / "stage3" / "proxy_eval_manifest.json")
    score_gate = read_json(PROJECT_ROOT / "reports" / "SCORE_GATE_RESULT.json")

    validated_adapters = 1 if stage2.get("structural_valid") else 0
    proxy_eval_complete = bool(stage3.get("complete"))
    score_gate_allowed = bool(score_gate.get("allowed"))
    license_ok = stage2.get("license_status") not in {"unknown", None}
    can_start_stage4 = validated_adapters >= 1 and proxy_eval_complete and score_gate_allowed and license_ok
    blocked_reasons = []
    if validated_adapters < 1:
        blocked_reasons.append("no_validated_adapter")
    if not proxy_eval_complete:
        blocked_reasons.append("proxy_eval_not_complete")
    if not score_gate_allowed:
        blocked_reasons.append("score_gate_not_allowed")
    if not license_ok:
        blocked_reasons.append("license_unknown")

    next_action = build_next_action(can_start_stage4, blocked_reasons)
    payload = {
        "stage": 4,
        "status": "ready" if can_start_stage4 else "blocked",
        "can_start_stage4": can_start_stage4,
        "validated_adapters": validated_adapters,
        "proxy_eval_complete": proxy_eval_complete,
        "score_gate_allowed": score_gate_allowed,
        "license_ok": license_ok,
        "blocked_reasons": blocked_reasons,
        "no_fusion_created": True,
        "no_daily_runner_created": True,
        "next_action": next_action,
    }
    write_text(PROJECT_ROOT / "reports" / "STAGE4_READINESS.md", render_report(payload))
    (PROJECT_ROOT / "reports" / "STAGE4_READINESS.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("report: reports/STAGE4_READINESS.md")
    print(f"can_start_stage4: {can_start_stage4}")
    print(f"NEXT_ACTION: {next_action['action']}")
    return 0 if can_start_stage4 else 6


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_next_action(can_start_stage4: bool, blocked_reasons: list[str]) -> dict:
    if can_start_stage4:
        return {
            "status": "enter_stage4",
            "action": "select one distinct candidate mechanism for Stage 4 experimentation",
            "reason": "Stage 4 prerequisites are satisfied.",
        }
    if blocked_reasons == ["proxy_eval_not_complete"]:
        return {
            "status": "blocked",
            "action": "run the staged proxy eval kernel on Kaggle GPU, then ingest proxy_predictions.jsonl locally",
            "reason": "Stage 4 requires completed proxy eval before fusion or daily runner work.",
        }
    if "license_unknown" in blocked_reasons:
        return {
            "status": "blocked",
            "action": "complete license review and generate proxy predictions on an approved GPU environment",
            "reason": "Stage 4 requires reviewed provenance and completed proxy eval before fusion or daily runner work.",
        }
    return {
        "status": "blocked",
        "action": "resolve Stage 4 readiness blockers listed above",
        "reason": "Stage 4 prerequisites are not satisfied.",
    }


def render_report(payload: dict) -> str:
    reasons = "\n".join(f"- {reason}" for reason in payload["blocked_reasons"]) if payload["blocked_reasons"] else "- null"
    next_action = payload["next_action"]
    return f"""# Stage 4 Readiness

Stage 4 was checked but not executed beyond readiness gating.

- can_start_stage4: {payload['can_start_stage4']}
- validated_adapters: {payload['validated_adapters']}
- proxy_eval_complete: {payload['proxy_eval_complete']}
- score_gate_allowed: {payload['score_gate_allowed']}
- license_ok: {payload['license_ok']}
- no_fusion_created: true
- no_daily_runner_created: true

## Blocked Reasons

{reasons}

NEXT_ACTION:
  status: {next_action['status']}
  action: "{next_action['action']}"
  reason: "{next_action['reason']}"
"""


if __name__ == "__main__":
    raise SystemExit(main())
