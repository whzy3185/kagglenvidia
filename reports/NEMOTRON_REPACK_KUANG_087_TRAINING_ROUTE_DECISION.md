# Public Kernel Output Route

- status: prepared
- selected_source_kernel: `kuangyicheng/nemotron-087-training`
- new_kernel_id: `muelsyse111/nemotron-repack-kuang-087-training`
- kernel_dir: `kaggle_kernels/nemotron_repack_kuang_087_training`
- route_type: `public_kernel_output_repack`
- no_training: true
- no_base_model_loading: true
- no_competition_submit_in_notebook: true

## Generate

```powershell
python scripts\25_make_kaggle_repack_public_kernel_output.py --kaggle-user muelsyse111 --source-kernel kuangyicheng/nemotron-087-training --kernel-slug nemotron-repack-kuang-087-training --output-dir "kaggle_kernels/nemotron_repack_kuang_087_training"
```

## Push

```powershell
python scripts\21_push_kaggle_notebook.py --kernel-dir "kaggle_kernels/nemotron_repack_kuang_087_training"
```

## Check

```powershell
kaggle kernels status muelsyse111/nemotron-repack-kuang-087-training
kaggle kernels files muelsyse111/nemotron-repack-kuang-087-training
kaggle kernels logs muelsyse111/nemotron-repack-kuang-087-training
```

## Submit Boundary

Only submit after logs show:

```text
OK: /kaggle/working/submission.zip is ready.
OK: public kernel output route was used.
```
