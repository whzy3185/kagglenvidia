# Stage 7 Blocked Notebook Retry

- updated_at: 2026-06-07T03:36:33
- source_candidate: `nemotron-s7-muon-full`
- source_kernel_id: `muelsyse111/nemotron-s7-muon-full-training`
- retry_kernel_id: `muelsyse111/nemotron-s7-muon-full-training-v4`
- retry_kernel_dir: `kaggle_kernels\nemotron_s7_muon_full_v4`
- full_training_amount_preserved: true
- push_requested: true
- run_started: true
- final_status: failed
- failure_reason: CUDA OOM on first backward pass with micro-batch 2
- gpu_session_blocked: false
- competition_submission_executed: false

## Command

`kaggle kernels push -p E:\Jitter\nemotron_086plus_repro\kaggle_kernels\nemotron_s7_muon_full_v4`

## Output

```text
Kernel version 1 successfully pushed.  Please check progress at https://www.kaggle.com/code/muelsyse111/nemotron-s7-muon-full-training-v4
```

See `STAGE7_MUON_V4_FAILURE_TRIAGE.md`. The full-quantity memory-scheduling fix
was published as v5.
