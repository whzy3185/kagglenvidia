# Stage 7 Blocked Notebook Retry Index

- `nemotron-s7-protected-rehearsal-v2`: run started; output pending.
- `nemotron-s7-muon-full-training-v2`: notebook created; run blocked by the two-session GPU limit.
- `nemotron-s7-muon-full-training-v3`: run started but failed because the inherited Docker image exposed no CUDA device.
- `nemotron-s7-muon-full-training-v4`: CUDA worked, but micro-batch 2 OOMed on the first backward pass.
- `nemotron-s7-muon-full-training-v5`: full-epoch retry started with micro-batch 1 and effective batch 16 preserved.
- competition submission executed: false.

Detailed reports:

- `STAGE7_BLOCKED_NOTEBOOK_RETRY_nemotron-s7-protected-rehearsal_v2.md`
- `STAGE7_BLOCKED_NOTEBOOK_RETRY_nemotron-s7-muon-full_v2.md`
- `STAGE7_BLOCKED_NOTEBOOK_RETRY_nemotron-s7-muon-full_v3.md`
- `STAGE7_BLOCKED_NOTEBOOK_RETRY_nemotron-s7-muon-full_v4.md`
- `STAGE7_BLOCKED_NOTEBOOK_RETRY_nemotron-s7-muon-full_v5.md`
