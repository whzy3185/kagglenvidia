# Stage 7 Full Replay Hardmix V2 Failure Triage

Checked at: 2026-06-06

## Kernel

```yaml
kernel_id: muelsyse111/nemotron-stage7-full-replay-hardmix-v2
kernel_version: 1
purpose: full 1000-step replay hardmix training
competition_submission_executed: false
submission_zip_generated: false
```

## Current Status

The Kaggle notebook failed before training started.

Remote output files:

```text
none
```

No `submission.zip` was generated.

## Error

Kaggle log reports:

```text
PapermillExecutionError
Exception encountered at "In [11]"
NameError: name 'run_training' is not defined
```

The final trigger cell still calls:

```python
if IS_KAGGLE:
    run_training()
```

but the cell defining `run_training()` is absent from the generated notebook.

## Root Cause

The local generator script is:

```text
scripts/25_make_stage7_full_training_notebook.py
```

It drops any source cell containing:

```python
"KAGGLE_API_TOKEN"
```

The Mohamed source notebook has `def run_training()` in cells that also contain non-Kaggle Modal/Kaggle-dataset upload branches with `KAGGLE_API_TOKEN`. Therefore the generator removed the entire training function cell.

Observed locally:

```yaml
source_notebook:
  training_cells_with_def_run_training:
    - cell_16
    - cell_17
  those_cells_contain_KAGGLE_API_TOKEN: true

generated_notebook:
  contains_run_training_definition: false
  contains_run_training_call: true
```

## What This Failure Is Not

This is not a competition evaluation error.

This is not a GPU capacity failure.

This is not caused by reducing training size. The generated notebook still had:

```yaml
MAX_SEQ_LEN: 8192
NUM_STEPS: 1000
TARGET_REPLAY_ANSWER_TOKENS: 2000000
BATCH_SIZE: 32
MICRO_BATCH_SIZE: 4
LEARNING_RATE: 3.5e-4
```

The failure happened before `run_training()` could start.

## Related Older Official Submission Errors

Older official `SubmissionStatus.ERROR` entries are from Huikang/Tong repack attempts:

```text
53352307
53351317
53350464
53329563
```

Those notebooks did generate structurally valid `submission.zip` files. Their failure occurred in the official competition evaluator, not during notebook execution.

## Required Fix

Patch the generator so it:

1. Keeps the first cell containing `def run_training()`.
2. Removes only the non-Kaggle Modal upload branch or token-writing code from inside that cell.
3. Drops only the separate Modal glue cell.
4. Regenerates a new kernel slug, for example:

```text
nemotron-stage7-full-replay-hardmix-v3
```

5. Pushes v3 to Kaggle.
6. Checks logs until the notebook reaches:

```text
Training: 1000 steps
OK: /kaggle/working/submission.zip is ready.
```

Do not submit the competition until `submission.zip` exists and a submit confirmation card is generated.
