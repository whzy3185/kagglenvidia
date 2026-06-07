# Stage 7 Norm-Balanced Delta-Space SVD Rank-32

- kernel: `muelsyse111/nemotron-s7-norm-balanced-delta-svd-r32`
- mechanism: per-module effective-delta norm balancing plus rank-32 SVD
- base model loaded: false
- GPU required: false
- competition submission executed: false

## Main Change

For each LoRA module, this route computes the exact Frobenius norm of `B @ A`
using only rank-sized Gram matrices. Source updates are normalized toward the
module median norm before weighted task arithmetic and rank-32 recompression.

This tests a different hypothesis from fixed global weights: adapter scale, not
only direction, may be causing destructive dominance during fusion.

## Sources

- LoRA: https://arxiv.org/abs/2106.09685
- Task arithmetic: https://arxiv.org/abs/2212.04089
- TIES-Merging: https://arxiv.org/abs/2306.01708
- PEFT merging: https://huggingface.co/docs/peft/developer_guides/model_merging

Remote output must pass the exact zip-root, rank, size, SHA256, pair-count, and
retained-singular-mass checks before it is considered structurally valid.
