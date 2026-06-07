# Stage 7 Full Training Queue Plan 2026-06-06

## Correction

The prior fast-training idea is canceled. The user requested early upload and Kaggle-side training, not a smaller training run.

## Goal

Start a full Kaggle GPU training job early so the long 30B LoRA training can run remotely while other analysis continues.

No competition submission is performed in this step.

## Candidate

```yaml
candidate: stage7_full_replay_hardmix_v2
base_route: mohamed_replay_data_0_86
kernel_id: muelsyse111/nemotron-stage7-full-replay-hardmix-v2
source_notebook: mohamedamr992/nemotron-replay-data-0-86
gpu: NvidiaRtxPro6000
base_model: metric/nemotron-3-nano-30b-a3b-bf16
```

## Training Amount

The training amount is intentionally not reduced.

```yaml
max_seq_len: 8192
num_steps: 1000
target_replay_answer_tokens: 2000000
batch_size: 32
micro_batch_size: 4
learning_rate: 3.5e-4
lora_rank: 32
lora_alpha: 32
moe_tie_weights: true
```

## Actual Change

Only the ordering/mixing report is changed:

```yaml
main_change: full_replay_hardmix_v2
description:
  - preserve full token and step budget
  - move high-unmasked target/replay examples earlier in the training order
  - keep original examples after the hard prefix to preserve full coverage
  - add output diagnostics and zip SHA256
```

This is not a short run and not an LR sweep.

## Why It May Help

The current best routes are Mohamed/Taha style full training outputs at `0.86`. Public output repacks and quick fusion did not improve rank. A full training variant with a single data-ordering mechanism can create a new adapter hash while keeping the strong full-training recipe.

## Expected Runtime

The source notebook metadata shows a long full run. This job is expected to take substantial Kaggle GPU time. The purpose of pushing now is to start the remote run early, not to shorten it.

## Commands

Generate:

```powershell
python scripts\25_make_stage7_full_training_notebook.py
```

Push and start Kaggle run:

```powershell
kaggle kernels push -p "kaggle_kernels\nemotron_stage7_full_replay_hardmix_v2"
```

Push result:

```yaml
push_status: success
kernel_version: 1
kernel_url: https://www.kaggle.com/code/muelsyse111/nemotron-stage7-full-replay-hardmix-v2
last_run_time_from_kaggle_list: "2026-06-06 14:45:17.593000 UTC"
status_api: "500 from kaggle kernels status at first check"
files_after_initial_push: []
logs_after_initial_push: ""
```

Check:

```powershell
kaggle kernels logs muelsyse111/nemotron-stage7-full-replay-hardmix-v2
kaggle kernels files muelsyse111/nemotron-stage7-full-replay-hardmix-v2 -v --page-size 100
```

## Submission Gate

Do not submit unless all are true:

```yaml
output_submission_zip_exists: true
logs_contain_ok_ready: true
zip_namelist:
  - adapter_config.json
  - adapter_model.safetensors
rank_lte_32: true
sha256_recorded: true
competition_submit_user_confirmed: true
```

## Boundary

- Do not call `kaggle competitions submit` in this step.
- Do not download the 30B base model locally.
- Do not commit `.safetensors` or `submission.zip`.
- Do not reduce training amount for this candidate.

## Next Check

The run is long. Poll files/logs instead of submitting:

```powershell
kaggle kernels logs muelsyse111/nemotron-stage7-full-replay-hardmix-v2
kaggle kernels files muelsyse111/nemotron-stage7-full-replay-hardmix-v2 -v --page-size 100
```
