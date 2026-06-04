# Manual Submission Checklist

Kernel id:

```text
muelsyse111/nemotron-repack-huikang-v27
```

## Before Manual Submit

- Notebook run is complete.
- Output contains `submission.zip`.
- Notebook log contains `OK: /kaggle/working/submission.zip is ready.`
- Zip contents are exactly:
  - `adapter_config.json`
  - `adapter_model.safetensors`
- Adapter rank `r <= 32`.
- No script executed competition submit automatically.
- Kaggle competition submission quota is sufficient.
- The notebook mounted `huikang/nemotron-adapter/Transformers/default/27`.

## Manual Submit Path

```text
Kaggle Notebook -> Output -> submission.zip -> Submit to Competition
```

## After Submit Record

- submission id:
- message:
- status:
- public score:
- error message:
- enter Stage 6: yes/no

## If Submission Errors

- Do not repeat-submit immediately.
- Check zip root structure.
- Check adapter rank.
- Check adapter file completeness.
- Check notebook output logs.
- Confirm the mounted model source is the intended Huikang v27 adapter.
