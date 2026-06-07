# Stage 7 Modulewise Delta-Space SVD Rank-32

- kernel: `muelsyse111/nemotron-s7-modulewise-delta-svd-r32`
- mechanism: module-family source weighting in effective LoRA delta space
- base model loaded: false
- GPU required: false
- competition submission executed: false

## Main Change

The global delta-SVD candidate uses one source-weight vector for every module.
This candidate uses distinct vectors for attention, Mamba, experts, and
`lm_head`, then recompresses each effective update to rank 32.

## Evidence

- Competition discussion on category trade-offs:
  https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/703240
- TIES-Merging: https://arxiv.org/abs/2306.01708
- LoRA: https://arxiv.org/abs/2106.09685
- PEFT merging: https://huggingface.co/docs/peft/developer_guides/model_merging

The weights are heuristic and therefore high risk. Remote output must pass the
same structural, size, SHA256, and rank gates before it becomes a submission
candidate.
