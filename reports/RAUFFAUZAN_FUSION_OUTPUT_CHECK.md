# Rauffauzan Fusion Output Check

- kernel_id: `muelsyse111/nemotron-repack-rauffauzan-fusion`
- source_kernel: `rauffauzanrambe/lora-adapter-fusion-and-rank-compression-pipeline`
- route: `public_kernel_output_repack`
- kernel_status: `COMPLETE`
- no_training: true
- no_base_model_loading: true
- no_competition_submit_by_script: true

## Output Evidence

- selected_existing_submission_zip: `/kaggle/input/notebooks/rauffauzanrambe/lora-adapter-fusion-and-rank-compression-pipeline/submission.zip`
- source_zip_namelist: `['adapter_config.json', 'adapter_model.safetensors']`
- repack_mode: `exact_adapter_files_only`
- zip_namelist: `['adapter_config.json', 'adapter_model.safetensors']`
- final_peft_type: `LORA`
- final_r: `32`
- final_target_modules: `['down_proj', 'in_proj', 'k_proj', 'lm_head', 'o_proj', 'out_proj', 'q_proj', 'up_proj', 'v_proj']`
- final_base_model_name_or_path: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16`
- submission_zip_path: `/kaggle/working/submission.zip`
- submission_zip_size_bytes: `3554385867`
- submission_zip_sha256: `af996be0175b08c1d0a403410a30c4ca6f9b727c2d2c1bd6047a62f6df7f02dc`

## Submit Status

Submitted through Kaggle CLI as a remote kernel-output submission. This avoided downloading and re-uploading the 3.55 GB output zip locally.

- submitted: true
- submission_id: `53383735`
- submission_message: `20260605_slot3_rauffauzan_fusion_output_af996be0`
- submission_status: `SubmissionStatus.COMPLETE`
- public_score: `0.86`
- submit_command_shape: `kaggle competitions submit <competition> -k muelsyse111/nemotron-repack-rauffauzan-fusion -f submission.zip -v 1 -m <message>`

```yaml
NEXT_ACTION:
  status: keep_as_verified_086_reference
  action: "compare against 0.87 public routes before submitting another variant"
  reason: "This route reached 0.86 but did not break the 0.87 leaderboard tier."
```
