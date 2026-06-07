# Stage 7 Delta-Space SVD Rank-32

- kernel: `muelsyse111/nemotron-s7-delta-space-svd-r32`
- mechanism: effective LoRA delta merge plus rank-32 recompression
- GPU required: false
- base model loaded: false
- competition submission executed: false

## Why This Differs

Directly averaging LoRA A and B factors generally does not equal averaging their
effective model updates. This experiment merges `B @ A` updates and uses a
low-rank QR/SVD identity to avoid materializing large dense matrices.

## Sources

- LoRA: https://arxiv.org/abs/2106.09685
- TIES-Merging: https://arxiv.org/abs/2306.01708
- PEFT model merging: https://huggingface.co/docs/peft/developer_guides/model_merging
- Rauffauzan rank-compression route:
  https://www.kaggle.com/code/rauffauzanrambe/lora-adapter-fusion-and-rank-compression-pipeline

## Gate

The output is only structurally valid after the remote notebook prints the
success marker, exact zip root, size, SHA256, LoRA pair count, and retained
singular-mass diagnostic.
