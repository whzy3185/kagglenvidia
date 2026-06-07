# Stage 7 Muon v3 Failure Triage

- kernel: `muelsyse111/nemotron-s7-muon-full-training-v3`
- result: failed before model loading
- competition submission executed: false
- training amount reduced: false

## Root Cause

The notebook inherited the public Muon notebook's standard CPU-oriented Docker
image. Metadata requested `NvidiaRtxPro6000`, but the runtime reported no CUDA
accelerator and Unsloth raised:

```text
NotImplementedError: Unsloth cannot find any torch accelerator? You need a GPU.
```

This was an execution-environment mismatch, not an adapter, dataset, or model
failure.

## Fix

- Reuse the same Kaggle BYOD Docker image that completed
  `nemotron-s7-seed-stability-replay` on RTX Pro 6000.
- Add an explicit `torch.cuda.is_available()` preflight before importing
  Unsloth.
- Preserve the public Muon notebook's full dataset, one epoch, rank 32, and
  sequence length 8192.
- Publish the repaired notebook as
  `muelsyse111/nemotron-s7-muon-full-training-v4`.
