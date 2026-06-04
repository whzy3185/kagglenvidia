# Kaggle-side Notebook Workflow

## Purpose

The local `submission.zip` is about 1.3 GB, so uploading it from the local machine is slow and fragile. This workflow uploads only a small Kaggle Notebook project. Kaggle mounts the public adapter model and creates `submission.zip` in `/kaggle/working`.

## Stages

1. notebook-only: generate `kernel-metadata.json` and the repack notebook locally.
2. push-notebook: push the small notebook project to Kaggle with Kaggle CLI.
3. manual-submit: open the Kaggle Notebook output and manually submit `submission.zip`.

## Generate Notebook

```powershell
python scripts\20_make_kaggle_repack_notebook.py --kaggle-user muelsyse111
```

Generated directory:

```text
kaggle_kernels/nemotron_repack_huikang_v27
```

## Push Notebook

```powershell
python scripts\21_push_kaggle_notebook.py --kernel-dir "kaggle_kernels/nemotron_repack_huikang_v27"
```

Equivalent Kaggle CLI command:

```powershell
kaggle kernels push -p "kaggle_kernels/nemotron_repack_huikang_v27"
```

## Check Status

```powershell
kaggle kernels status muelsyse111/nemotron-repack-huikang-v27
```

## Check Output Files

```powershell
kaggle kernels files muelsyse111/nemotron-repack-huikang-v27
```

Expected output includes:

```text
submission.zip
```

## Manual Submit

Open the Kaggle Notebook page, then use:

```text
Notebook -> Output -> submission.zip -> Submit to Competition
```

This manual action is the only step that should consume competition submission quota.

## Safety Boundaries

- Does not call competition submit.
- Does not consume submission quota during notebook generation or push.
- Does not store tokens.
- Does not upload `kaggle.json`.
- Does not train.
- Does not load the base model.
- Does not use GPU.
- Does not upload the local 1.3 GB `submission.zip`.

## Failure Checks

- Add Input did not mount `huikang/nemotron-adapter/Transformers/default/27`.
- `model_sources` did not take effect.
- `adapter_config.json` or `adapter_model.safetensors` was not found under `/kaggle/input`.
- Zip root contains nested directories or unexpected files.
- Adapter rank `r` is greater than 32.
- Kaggle CLI is not logged in.
- `kaggle kernels push` failed.
