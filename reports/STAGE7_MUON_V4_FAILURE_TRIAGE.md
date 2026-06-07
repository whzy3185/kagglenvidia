# Stage 7 Muon v4 Failure Triage

- kernel: `muelsyse111/nemotron-s7-muon-full-training-v4`
- CUDA available: true
- GPU: NVIDIA RTX PRO 6000 Blackwell Server Edition
- failure stage: first backward pass
- competition submission executed: false

## Root Cause

The runtime and model load were healthy. The first training step failed with:

```text
CUDA out of memory. Tried to allocate 6.79 GiB.
GPU capacity: 94.97 GiB.
Free at failure: 6.54 GiB.
```

The public Muon notebook used micro-batch 2 at sequence length 8192. That peak
does not fit reliably with this patched Nemotron/Unsloth runtime.

## v5 Fix

- `per_device_train_batch_size`: 2 -> 1
- `gradient_accumulation_steps`: 8 -> 16
- effective batch size remains 16
- dataset remains complete
- epochs remain 1
- sequence length remains 8192
- LoRA rank remains 32
- enable expandable CUDA allocator segments
- remove an unused second CPU copy of the base model

The fix changes memory scheduling, not training quantity.
