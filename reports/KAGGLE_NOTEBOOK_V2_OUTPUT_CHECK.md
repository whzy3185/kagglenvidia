# Kaggle Notebook V2 Output Check

- timestamp: 2026-06-04
- kernel_id: `muelsyse111/nemotron-repack-huikang-v27-normalized`
- kernel_status: `KernelWorkerStatus.COMPLETE`
- competition_submit_called: false
- submission_quota_consumed_by_check: false
- official_submission_id: `53352307`
- official_submission_status: `SubmissionStatus.ERROR`
- official_public_score: null

## Output File List

Kaggle CLI `kernels files` shows:

```text
submission.zip
```

The CLI file-list size display is not reliable for this large output, so the notebook log is the source of truth for size and hash.

## Notebook Log Evidence

```text
selected_adapter_dir: /kaggle/input/models/huikang/nemotron-adapter/transformers/default/27
original_r: 32
original_target_modules: all-linear
zero_tensor_count: 46
derived_target_modules: ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'out_proj', 'x_proj', 'w1', 'w2', 'up_proj', 'down_proj', 'lm_head']
normalized_base_model_name_or_path: nvidia/Nemotron-3-Nano-30B-A3B-BF16
normalized_inference_mode: True
kept_tensor_count: 372
removed_zero_tensor_count: 46
normalized_model_size_bytes: 1544342304
zip_namelist: ['adapter_config.json', 'adapter_model.safetensors']
submission_zip_size_bytes: 1415445929
submission_zip_sha256: 467e60ee8fb8f9d641d0e2ed5efcbc604a7cc7a54e6f2aa6ce447738bc308d97
working_output_files_after_cleanup: ['submission.zip']
OK: /kaggle/working/submission.zip is ready.
OK: normalized adapter config and zero-tensor-stripped safetensors were used.
```

## Conformance Result

The current V2 notebook-generated `submission.zip` conforms to the expected structural checks:

- zip exists in Kaggle Output.
- zip root contains exactly `adapter_config.json` and `adapter_model.safetensors`.
- LoRA rank is 32.
- temporary normalized files are removed from `/kaggle/working`.
- Kaggle Output exposes only `submission.zip` as the user-facing output file.
- no base model was loaded.
- no training was run.
- no competition submission was made by script.

## Remaining Risk

This V2 package is structurally valid but not official-valid. Manual official submission `53352307` returned `SubmissionStatus.ERROR`. Do not submit this V2 package again unless the Kaggle website exposes a concrete error and a targeted fix is made.

## Manual Submit Boundary

Only submit manually from:

```text
Kaggle Notebook -> Output -> submission.zip -> Submit to Competition
```

Do not submit the older raw v1 notebook output again.
