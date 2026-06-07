# Stage 7 Reference Submission List

- updated_at: 2026-06-07T14:21:48
- current_best_displayed_score: 0.86
- today_submission_count: 0
- today_remaining_quota: 5
- competition_submission_executed: false
- selection_metric: public rank movement after official evaluation

## Output-Ready Candidates

| order | candidate | mechanism | package | SHA256 | risk | source chain |
|---:|---|---|---|---|---|---|
| slot1 | `muelsyse111/nemotron-s7-protected-rehearsal-v2` | `protected_category_loss_reweighting` | ready, 1.28 GiB | `641c57f33c72` | medium-high: full training targets category forgetting, but public-distribution transfer is unmeasured | https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/703240<br>https://arxiv.org/abs/1909.08383 |
| slot2 | `muelsyse111/nemotron-s7-delta-space-svd-r32` | `effective_delta_qr_svd_rank32_recompression` | ready, 3.31 GiB | `b31b987c290f` | medium-high: mathematically coherent delta merge, but source weights remain uncalibrated | https://arxiv.org/abs/2106.09685<br>https://arxiv.org/abs/2306.01708<br>https://huggingface.co/docs/peft/developer_guides/model_merging<br>https://www.kaggle.com/code/rauffauzanrambe/lora-adapter-fusion-and-rank-compression-pipeline |
| slot3 | `muelsyse111/nemotron-s7-modulewise-delta-svd-r32` | `module_family_weighted_delta_qr_svd_rank32` | ready, 3.31 GiB | `00d6bd3faafb` | high: coherent delta merge, but module-family weights are heuristic | https://arxiv.org/abs/2106.09685<br>https://arxiv.org/abs/2306.01708<br>https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/703240<br>https://huggingface.co/docs/peft/developer_guides/model_merging |
| slot4 | `muelsyse111/nemotron-s7-muon-v5-audit` | `muon_optimizer_full_epoch_microbatch1_effective_batch16` | ready, 3.57 GiB | `2d42d0adb258` | high: full-epoch optimizer change is distinct, but the public reference scored below the current best | https://www.kaggle.com/code/pkuszboi/0-85-lb-training-with-muon<br>https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/704491<br>https://github.com/KellerJordan/Muon |
| slot5 | `muelsyse111/nemotron-s7-norm-balanced-delta-svd-r32` | `per_module_delta_norm_balanced_qr_svd_rank32` | ready, 3.31 GiB | `aec7776ecde0` | high: norm balancing limits dominant deltas, but may suppress genuinely useful specialist signal | https://arxiv.org/abs/2106.09685<br>https://arxiv.org/abs/2212.04089<br>https://arxiv.org/abs/2306.01708<br>https://huggingface.co/docs/peft/developer_guides/model_merging |
| reserve1 | `muelsyse111/nemotron-s7-seed-stability-replay` | `deterministic_seed_and_reproducible_shuffle` | ready, 1.28 GiB | `f5dde9e053d7` | medium: full training completed, but seed control alone may reproduce rather than improve the 0.86 family | https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/704491<br>https://www.kaggle.com/code/pkuszboi/0-85-lb-training-with-muon |
| reserve2 | `muelsyse111/nemotron-s7-ties-sign-merge` | `ties_trim_elect_sign_merge` | ready, 3.31 GiB | `b03e975ea48d` | medium-high: sign consensus may remove useful minority deltas | https://arxiv.org/abs/2306.01708<br>https://github.com/prateeky2806/ties-merging |
| reserve3 | `muelsyse111/nemotron-s7-dare-merge` | `dare_drop_and_rescale_merge` | ready, 3.31 GiB | `4f37c3377e93` | high: stochastic sparsification may degrade a saturated 0.86 anchor | https://arxiv.org/abs/2311.03099<br>https://huggingface.co/docs/peft/developer_guides/model_merging |
| reserve4 | `muelsyse111/nemotron-s7-layerwise-adapter-soup` | `module_aware_layerwise_weighted_soup` | ready, 3.31 GiB | `4480e232def3` | high: heuristic module weights have no proxy calibration | https://arxiv.org/abs/2203.05482<br>https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/704473<br>https://huggingface.co/docs/peft/developer_guides/model_merging |

These 9 packages have distinct hashes and exact two-file zip roots. They are structurally valid only; no official score is claimed.

## Training / Queue Order

| priority | candidate | remote kernel | state | mechanism | evidence |
|---:|---|---|---|---|---|
| 1 | `nemotron-s7-weak-protected-curriculum` | `muelsyse111/nemotron-s7-weak-protected-curriculum-v2` | `run_accepted_output_pending` | `weak_category_plus_protected_interleaving` | https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/703240<br>https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/698293 |
| 2 | `nemotron-s7-mamba-inproj-specialist` | `muelsyse111/nemotron-s7-mamba-inproj-specialist-v2` | `run_accepted_output_pending` | `selective_mamba_in_proj_adaptation` | https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/687961<br>selective parameter-efficient adaptation |
| 3 | `nemotron-s7-category-roundrobin` | `muelsyse111/nemotron-s7-category-round-robin` | `created_gpu_blocked` | `category_balanced_round_robin_curriculum` | https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/703240<br>https://github.com/tonghuikang/nemotron |
| 4 | `nemotron-s7-answer-tail-objective` | `muelsyse111/nemotron-s7-answer-tail-objective` | `created_gpu_blocked` | `tail_focused_loss_masking` | https://github.com/tonghuikang/nemotron<br>reasoning trace compression |
| 5 | `nemotron-s7-length-stratified` | `muelsyse111/nemotron-s7-length-stratified-curriculum` | `created_gpu_blocked` | `alternating_long_short_sequence_curriculum` | https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/687961<br>curriculum learning |

## Evidence Chain

- [Kaggle discussion 704491](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/704491): training and evaluation variance are material; fixed seed, logging, and optimizer stability matter.
- [Kaggle discussion 703240](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/703240): cryptarithm gains can be cancelled by forgetting in bit, gravity, numeral, and unit conversion.
- [Kaggle discussion 687961](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/687961): rank-32, length-8192 training is feasible on Kaggle RTX Pro 6000 with fused CE and careful microbatching.
- [Kaggle discussion 698293](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/698293): symbolic solvers are useful as distillation/data oracles, not inference-time shortcuts.
- TIES-Merging: https://arxiv.org/abs/2306.01708
- DARE: https://arxiv.org/abs/2311.03099
- Model soups: https://arxiv.org/abs/2203.05482
- PEFT model merging: https://huggingface.co/docs/peft/developer_guides/model_merging
- Public Muon notebook: https://www.kaggle.com/code/pkuszboi/0-85-lb-training-with-muon
- Muon implementation: https://github.com/KellerJordan/Muon

## Recommended Use of Today's Quota

1. Protected rehearsal is first because it is a full-training route that directly targets observed category forgetting.
2. Delta-space SVD is the strongest coherent merge because it combines effective LoRA updates before legal rank-32 recompression.
3. Modulewise delta-SVD tests whether module-family specialization improves the same coherent merge.
4. Audited Muon v5 is optimizer-distinct and uses the full training set, but remains high risk because the public reference was below the current best.
5. Norm-balanced delta-SVD is the fifth mechanism-distinct candidate; seed stability, TIES, DARE and raw-factor soup remain reserves.

No candidate may be submitted until its confirmation card is reviewed and the user explicitly confirms the submission.
