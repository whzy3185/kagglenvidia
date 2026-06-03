from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.provenance import write_json  # noqa: E402
from nemotron086.reporting import markdown_table, write_text  # noqa: E402


READINESS_PATH = PROJECT_ROOT / "reports" / "STAGE4_READINESS.json"
OUTPUT_JSON = PROJECT_ROOT / "artifacts" / "stage4_candidate_plan.json"
OUTPUT_REPORT = PROJECT_ROOT / "reports" / "STAGE4_CANDIDATE_PLAN.md"


def main() -> int:
    readiness = read_json(READINESS_PATH)
    candidates = build_candidates(readiness)
    selected = select_candidate(readiness, candidates)
    next_action = build_next_action(readiness, selected)
    payload = {
        "stage": 4,
        "status": "planned_only",
        "can_start_stage4": bool(readiness.get("can_start_stage4")),
        "selected_stage4_route": selected,
        "candidates": candidates,
        "no_training": True,
        "no_submission": True,
        "no_fusion_created": True,
        "no_daily_runner_created": True,
        "next_action": next_action,
    }
    write_json(OUTPUT_JSON, payload)
    write_text(OUTPUT_REPORT, render_report(payload, readiness))
    print("report: reports/STAGE4_CANDIDATE_PLAN.md")
    print(f"selected_stage4_route: {selected['name'] if selected else None}")
    print(f"NEXT_ACTION: {next_action['action']}")
    return 0


def build_candidates(readiness: dict[str, Any]) -> list[dict[str, Any]]:
    can_start = bool(readiness.get("can_start_stage4"))
    proxy_eval_complete = bool(readiness.get("proxy_eval_complete"))
    validated_adapters = int(readiness.get("validated_adapters") or 0)
    return [
        {
            "name": "compressed_tong_trace",
            "kind": "single_adapter_specialist_delta",
            "priority": "high_after_proxy_eval",
            "required_before_execution": [
                "proxy_eval_complete",
                "baseline_category_breakdown_available",
                "one targeted data transformation selected",
            ],
            "allowed_now": can_start and proxy_eval_complete,
            "blocked_reason": None if can_start and proxy_eval_complete else "proxy_eval_not_complete",
            "first_safe_step": "inspect proxy category weaknesses and choose one data transformation",
        },
        {
            "name": "numeric_rate_first_trace",
            "kind": "specialist_candidate",
            "priority": "high_if_numeric_or_unit_conversion_is_weak",
            "required_before_execution": [
                "proxy_eval_complete",
                "numeric_or_unit_conversion_regression_cases_exist",
            ],
            "allowed_now": can_start and proxy_eval_complete,
            "blocked_reason": None if can_start and proxy_eval_complete else "proxy_eval_not_complete",
            "first_safe_step": "build a small generator spec for numeric/unit conversion failures",
        },
        {
            "name": "cipher_mapping_trace",
            "kind": "specialist_candidate",
            "priority": "medium_if_cipher_is_weak",
            "required_before_execution": [
                "proxy_eval_complete",
                "cipher_regression_cases_exist",
            ],
            "allowed_now": can_start and proxy_eval_complete,
            "blocked_reason": None if can_start and proxy_eval_complete else "proxy_eval_not_complete",
            "first_safe_step": "build a rule-generator spec for cipher mapping failures",
        },
        {
            "name": "bit_operation_trace",
            "kind": "specialist_candidate",
            "priority": "medium_if_bit_manipulation_is_weak",
            "required_before_execution": [
                "proxy_eval_complete",
                "bit_manipulation_regression_cases_exist",
            ],
            "allowed_now": can_start and proxy_eval_complete,
            "blocked_reason": None if can_start and proxy_eval_complete else "proxy_eval_not_complete",
            "first_safe_step": "build a verifier-backed generator spec for bit-operation failures",
        },
        {
            "name": "lora_fusion_rank32",
            "kind": "fusion_candidate",
            "priority": "later_only",
            "required_before_execution": [
                "proxy_eval_complete",
                "two_or_more_valid_adapters",
                "merge_report_template",
                "rank_32_compression_plan",
            ],
            "allowed_now": can_start and proxy_eval_complete and validated_adapters >= 2,
            "blocked_reason": None
            if can_start and proxy_eval_complete and validated_adapters >= 2
            else "requires_proxy_eval_and_two_or_more_valid_adapters",
            "first_safe_step": "wait until a second structurally valid adapter exists",
        },
    ]


def select_candidate(readiness: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not readiness.get("can_start_stage4"):
        return None
    for candidate in candidates:
        if candidate["allowed_now"] and candidate["name"] != "lora_fusion_rank32":
            return candidate
    return None


def build_next_action(readiness: dict[str, Any], selected: dict[str, Any] | None) -> dict[str, str]:
    if selected:
        return {
            "status": "enter_stage4",
            "action": f"start Stage 4 planning for {selected['name']} without submitting",
            "reason": "Stage 4 prerequisites are satisfied and a single mechanism was selected.",
        }
    if "proxy_eval_not_complete" in readiness.get("blocked_reasons", []):
        return {
            "status": "stay_stage3",
            "action": "run the staged proxy eval kernel on Kaggle GPU, then ingest proxy_predictions.jsonl locally",
            "reason": "Stage 4 candidate execution is blocked until proxy eval is complete.",
        }
    return {
        "status": "blocked",
        "action": "resolve Stage 4 readiness blockers",
        "reason": "No Stage 4 candidate can be selected until readiness is true.",
    }


def render_report(payload: dict[str, Any], readiness: dict[str, Any]) -> str:
    rows = [
        [
            item["name"],
            item["kind"],
            item["priority"],
            item["allowed_now"],
            item["blocked_reason"],
            item["first_safe_step"],
        ]
        for item in payload["candidates"]
    ]
    selected = payload["selected_stage4_route"]
    next_action = payload["next_action"]
    blockers = readiness.get("blocked_reasons") or []
    blocker_text = "\n".join(f"- {item}" for item in blockers) if blockers else "- null"
    selected_text = selected["name"] if selected else "null"
    return f"""# Stage 4 Candidate Plan

This is a planning report only. It does not create fusion assets, train, submit, or run a daily runner.

- can_start_stage4: {payload['can_start_stage4']}
- selected_stage4_route: {selected_text}
- no_training: true
- no_submission: true
- no_fusion_created: true
- no_daily_runner_created: true

## Current Blockers

{blocker_text}

## Candidate Mechanisms

{markdown_table(['name', 'kind', 'priority', 'allowed_now', 'blocked_reason', 'first_safe_step'], rows)}

NEXT_ACTION:
  status: {next_action['status']}
  action: "{next_action['action']}"
  reason: "{next_action['reason']}"
"""


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
