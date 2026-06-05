# Kien Notebook Output Check

- kernel_id: `muelsyse111/nemotron-repack-kien-output`
- kernel_status: `COMPLETE`
- pushed_version: `3`
- source_kernel: `kienngx/nvidia-nemotron-training-copy-run-instantly`
- route: `kien_public_training_output`
- no_training: true
- no_base_model_loading: true
- no_competition_submit_by_script: true

## Output Evidence

- selected_existing_submission_zip: `/kaggle/input/notebooks/kienngx/nvidia-nemotron-training-copy-run-instantly/submission.zip`
- source_zip_namelist: `['README.md', 'chat_template.jinja', 'tokenizer.json', 'adapter_config.json', 'tokenizer_config.json', 'adapter_model.safetensors']`
- repack_mode: `exact_adapter_files_only`
- zip_namelist: `['adapter_config.json', 'adapter_model.safetensors']`
- final_peft_type: `LORA`
- final_r: `32`
- final_target_modules: `['up_proj', 'q_proj', 'out_proj', 'k_proj', 'o_proj', 'down_proj', 'v_proj', 'in_proj']`
- final_base_model_name_or_path: `/kaggle/input/models/metric/nemotron-3-nano-30b-a3b-bf16/transformers/default/1`
- submission_zip_path: `/kaggle/working/submission.zip`
- submission_zip_size_bytes: `3537300666`
- submission_zip_sha256: `f7fe88446ed05bd5402fdfc1d0d7eb7e5324ddfb372c991611577cbea8b1fafa`

## Current Quota State

- today_submission_count: `4`
- today_remaining_quota: `1`
- pending_submission_id: `53355919`
- pending_submission_date_utc: `2026-06-04 08:32:03.250000`

## Decision

Kien strict two-file Kaggle-side output is ready as the next distinct candidate, but do not use the last remaining daily quota while submission `53355919` is still pending.

```yaml
NEXT_ACTION:
  status: wait_pending_result
  action: "kaggle competitions submissions nvidia-nemotron-model-reasoning-challenge -v"
  reason: "A previous official submission is still pending, and today only one submission remains."
```
