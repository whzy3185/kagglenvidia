# Public Kernel Output Route

- status: prepared
- selected_source_kernel: `dedquoc/nvidia-nmrc-low-rank-svd-lora-adapter-fusion`
- new_kernel_id: `muelsyse111/nemotron-repack-dedquoc-svd-fusion`
- kernel_dir: `kaggle_kernels/nemotron_repack_dedquoc_svd_fusion`
- route_type: `public_kernel_output_repack`
- no_training: true
- no_base_model_loading: true
- no_competition_submit_in_notebook: true

## Generate

```powershell
python scripts\25_make_kaggle_repack_public_kernel_output.py --kaggle-user muelsyse111 --source-kernel dedquoc/nvidia-nmrc-low-rank-svd-lora-adapter-fusion --kernel-slug nemotron-repack-dedquoc-svd-fusion --output-dir "kaggle_kernels/nemotron_repack_dedquoc_svd_fusion"
```

## Push

```powershell
python scripts\21_push_kaggle_notebook.py --kernel-dir "kaggle_kernels/nemotron_repack_dedquoc_svd_fusion"
```

## Check

```powershell
kaggle kernels status muelsyse111/nemotron-repack-dedquoc-svd-fusion
kaggle kernels files muelsyse111/nemotron-repack-dedquoc-svd-fusion
kaggle kernels logs muelsyse111/nemotron-repack-dedquoc-svd-fusion
```

## Submit Boundary

Only submit after logs show:

```text
OK: /kaggle/working/submission.zip is ready.
OK: public kernel output route was used.
```
