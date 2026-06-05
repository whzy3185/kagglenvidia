# Kaggle-side Notebook V2 Adjustment

- status: prepared
- kernel_id: `muelsyse111/nemotron-repack-huikang-v27-normalized`
- kernel_dir: `kaggle_kernels/nemotron_repack_huikang_v27_normalized`
- model_source: `huikang/nemotron-adapter/Transformers/default/27`
- competition: `nvidia-nemotron-model-reasoning-challenge`
- no_competition_submit: true
- no_base_model_loading: true
- no_training: true

## Why V2 Exists

Two official submissions built from the raw Kaggle-side repack failed with `Evaluation metric raised an unexpected error`. The raw notebook successfully mounted the adapter and produced a large `submission.zip`, so the failure is more likely an official evaluator loading or metadata compatibility issue than a notebook resource issue.

## V2 Changes

1. Reads the safetensors header with Python standard library only.
2. Derives explicit LoRA `target_modules` from nonzero LoRA tensor names instead of leaving `target_modules` as `all-linear`.
3. Sets missing `base_model_name_or_path` to `nvidia/Nemotron-3-Nano-30B-A3B-BF16`.
4. Sets `inference_mode` to `true`.
5. Removes zero-size safetensors entries before packaging. The local header audit found zero-size `w3` LoRA tensors in the raw adapter.
6. Uses `ZIP_DEFLATED` instead of `ZIP_STORED` to reduce output size.
7. Deletes temporary normalized files after zipping so Kaggle Output only exposes `submission.zip`.

## Generate

```powershell
python scripts\23_make_kaggle_repack_notebook_v2.py --kaggle-user muelsyse111
```

## Push Notebook Only

```powershell
python scripts\21_push_kaggle_notebook.py --kernel-dir "kaggle_kernels/nemotron_repack_huikang_v27_normalized"
```

## Check Output

```powershell
kaggle kernels status muelsyse111/nemotron-repack-huikang-v27-normalized
kaggle kernels files muelsyse111/nemotron-repack-huikang-v27-normalized
kaggle kernels logs muelsyse111/nemotron-repack-huikang-v27-normalized
```

## Manual Submit Boundary

Only submit manually from Kaggle Notebook Output after confirming the v2 log contains:

```text
OK: normalized adapter config and zero-tensor-stripped safetensors were used.
```

Do not submit the v1 raw repack again.
