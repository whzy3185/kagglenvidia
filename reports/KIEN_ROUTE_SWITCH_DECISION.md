# Kien Route Switch Decision

- status: scored_low_do_not_repeat
- previous_route: `huikang_v27`
- previous_route_status: `official_evaluator_failed`
- selected_route: `kien_public_training_output`
- selected_kernel_source: `kienngx/nvidia-nemotron-training-copy-run-instantly`
- new_kernel_id: `muelsyse111/nemotron-repack-kien-output`
- kernel_dir: `kaggle_kernels/nemotron_repack_kien_output`
- no_training: true
- no_base_model_loading: true
- no_competition_submit: true

## Reason

Huikang v27 raw and normalized packages failed official evaluation. Kien's public notebook/model family is a separate public 0.86-style route and exposes adapter outputs from a public training notebook.

## Evidence

- `kaggle kernels files kienngx/nvidia-nemotron-training-copy-run-instantly` lists `adapter_config.json` and `adapter_model.safetensors`.
- The public notebook metadata is `is_private: false`.
- The public notebook uses competition source `nvidia-nemotron-model-reasoning-challenge`.
- This repack notebook mounts the public notebook as `kernel_sources`, not as a private dataset.

## Generate

```powershell
python scripts\24_make_kaggle_repack_kien_output.py --kaggle-user muelsyse111
```

## Push Notebook

```powershell
python scripts\21_push_kaggle_notebook.py --kernel-dir "kaggle_kernels/nemotron_repack_kien_output"
```

## Check

```powershell
kaggle kernels status muelsyse111/nemotron-repack-kien-output
kaggle kernels files muelsyse111/nemotron-repack-kien-output
kaggle kernels logs muelsyse111/nemotron-repack-kien-output
```

## Submit Boundary

Do not submit until notebook logs show:

```text
OK: /kaggle/working/submission.zip is ready.
OK: Kien public notebook output route was used.
```

## Current Output

- kernel_status: `COMPLETE`
- repack_mode: `exact_adapter_files_only`
- zip_namelist: `['adapter_config.json', 'adapter_model.safetensors']`
- final_r: `32`
- submission_zip_size_bytes: `3537300666`
- submission_zip_sha256: `f7fe88446ed05bd5402fdfc1d0d7eb7e5324ddfb372c991611577cbea8b1fafa`

## Current Score

- submission_id: `53355919`
- submission_status: `SubmissionStatus.COMPLETE`
- public_score: `0.63`

Do not repeat this exact package. It is useful only as a low-score control and as evidence that structural validity does not imply competitive public score.
