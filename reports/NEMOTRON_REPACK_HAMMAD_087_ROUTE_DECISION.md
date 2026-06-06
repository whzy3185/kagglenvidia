# Public Kernel Output Route

- status: prepared
- selected_source_kernel: `hammadfarooq470/agi-for-medal-0-87`
- new_kernel_id: `muelsyse111/nemotron-repack-hammad-087`
- kernel_dir: `kaggle_kernels/nemotron_repack_hammad_087`
- route_type: `public_kernel_output_repack`
- no_training: true
- no_base_model_loading: true
- no_competition_submit_in_notebook: true

## Generate

```powershell
python scripts\25_make_kaggle_repack_public_kernel_output.py --kaggle-user muelsyse111 --source-kernel hammadfarooq470/agi-for-medal-0-87 --kernel-slug nemotron-repack-hammad-087 --output-dir "kaggle_kernels/nemotron_repack_hammad_087"
```

## Push

```powershell
python scripts\21_push_kaggle_notebook.py --kernel-dir "kaggle_kernels/nemotron_repack_hammad_087"
```

## Check

```powershell
kaggle kernels status muelsyse111/nemotron-repack-hammad-087
kaggle kernels files muelsyse111/nemotron-repack-hammad-087
kaggle kernels logs muelsyse111/nemotron-repack-hammad-087
```

## Submit Boundary

Only submit after logs show:

```text
OK: /kaggle/working/submission.zip is ready.
OK: public kernel output route was used.
```
