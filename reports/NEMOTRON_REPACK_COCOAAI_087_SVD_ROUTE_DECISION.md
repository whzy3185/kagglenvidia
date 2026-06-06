# Public Kernel Output Route

- status: prepared
- selected_source_kernel: `cocoaai/nvidia-nemotron-huikang-0-87-svd-submit`
- new_kernel_id: `muelsyse111/nemotron-repack-cocoaai-087-svd`
- kernel_dir: `kaggle_kernels/nemotron_repack_cocoaai_087_svd`
- route_type: `public_kernel_output_repack`
- no_training: true
- no_base_model_loading: true
- no_competition_submit_in_notebook: true

## Generate

```powershell
python scripts\25_make_kaggle_repack_public_kernel_output.py --kaggle-user muelsyse111 --source-kernel cocoaai/nvidia-nemotron-huikang-0-87-svd-submit --kernel-slug nemotron-repack-cocoaai-087-svd --output-dir "kaggle_kernels/nemotron_repack_cocoaai_087_svd"
```

## Push

```powershell
python scripts\21_push_kaggle_notebook.py --kernel-dir "kaggle_kernels/nemotron_repack_cocoaai_087_svd"
```

## Check

```powershell
kaggle kernels status muelsyse111/nemotron-repack-cocoaai-087-svd
kaggle kernels files muelsyse111/nemotron-repack-cocoaai-087-svd
kaggle kernels logs muelsyse111/nemotron-repack-cocoaai-087-svd
```

## Submit Boundary

Only submit after logs show:

```text
OK: /kaggle/working/submission.zip is ready.
OK: public kernel output route was used.
```
