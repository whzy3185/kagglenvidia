# Public Kernel Output Route

- status: prepared
- selected_source_kernel: `rauffauzanrambe/lora-adapter-fusion-and-rank-compression-pipeline`
- new_kernel_id: `muelsyse111/nemotron-repack-rauffauzan-fusion`
- kernel_dir: `kaggle_kernels/nemotron_repack_rauffauzan_fusion`
- route_type: `public_kernel_output_repack`
- no_training: true
- no_base_model_loading: true
- no_competition_submit_in_notebook: true

## Generate

```powershell
python scripts\25_make_kaggle_repack_public_kernel_output.py --kaggle-user muelsyse111 --source-kernel rauffauzanrambe/lora-adapter-fusion-and-rank-compression-pipeline --kernel-slug nemotron-repack-rauffauzan-fusion --output-dir "kaggle_kernels/nemotron_repack_rauffauzan_fusion"
```

## Push

```powershell
python scripts\21_push_kaggle_notebook.py --kernel-dir "kaggle_kernels/nemotron_repack_rauffauzan_fusion"
```

## Check

```powershell
kaggle kernels status muelsyse111/nemotron-repack-rauffauzan-fusion
kaggle kernels files muelsyse111/nemotron-repack-rauffauzan-fusion
kaggle kernels logs muelsyse111/nemotron-repack-rauffauzan-fusion
```

## Submit Boundary

Only submit after logs show:

```text
OK: /kaggle/working/submission.zip is ready.
OK: public kernel output route was used.
```
