# Stage 4 Candidate Plan

This is a planning report only. It does not create fusion assets, train, submit, or run a daily runner.

- can_start_stage4: False
- selected_stage4_route: null
- no_training: true
- no_submission: true
- no_fusion_created: true
- no_daily_runner_created: true

## Current Blockers

- proxy_eval_not_complete

## Candidate Mechanisms

| name | kind | priority | allowed_now | blocked_reason | first_safe_step |
| --- | --- | --- | --- | --- | --- |
| compressed_tong_trace | single_adapter_specialist_delta | high_after_proxy_eval | false | proxy_eval_not_complete | inspect proxy category weaknesses and choose one data transformation |
| numeric_rate_first_trace | specialist_candidate | high_if_numeric_or_unit_conversion_is_weak | false | proxy_eval_not_complete | build a small generator spec for numeric/unit conversion failures |
| cipher_mapping_trace | specialist_candidate | medium_if_cipher_is_weak | false | proxy_eval_not_complete | build a rule-generator spec for cipher mapping failures |
| bit_operation_trace | specialist_candidate | medium_if_bit_manipulation_is_weak | false | proxy_eval_not_complete | build a verifier-backed generator spec for bit-operation failures |
| lora_fusion_rank32 | fusion_candidate | later_only | false | requires_proxy_eval_and_two_or_more_valid_adapters | wait until a second structurally valid adapter exists |

NEXT_ACTION:
  status: stay_stage3
  action: "run the staged proxy eval kernel on Kaggle GPU, then ingest proxy_predictions.jsonl locally"
  reason: "Stage 4 candidate execution is blocked until proxy eval is complete."
