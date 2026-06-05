# Akihiko LoRA Submission Report

- route: `akihiko_lora_exp1_lr1e4_r32`
- source_dataset: `akihikokatsumata/nemotron-lora-exp1-lr1e4-r32`
- source_license: `CC0-1.0`
- adapter_dir: `artifacts/stage5/akihiko_lora_exp1_lr1e4_r32/adapter`
- submission_zip: `artifacts/submissions/20260604_215019/submission.zip`
- submission_zip_sha256: `48680a7535ae19e8d7ffce301cd925a00d777dcfbb1dbd7b44094bb6f21bade8`
- zip_structure_status: `structural_valid`
- structural_valid: true
- rank_lte_32: true
- safetensors_opened: true
- base_model_loaded: false
- official_format_confirmed: false
- submitted: true
- submission_id: `53364584`
- submission_message: `20260604_slot2_akihiko_lora_exp1_lr1e4_r32_48680a75`
- latest_status: `SubmissionStatus.COMPLETE`
- public_score: `0.50`

## Decision

This is a small, distinct, directly downloadable CC0 adapter route. The official score was only `0.50`, so it is not a competitive candidate.

```yaml
NEXT_ACTION:
  status: do_not_repeat
  action: "keep only as a low-score control"
  reason: "The route is structurally valid but scored 0.50."
```
