# Stage 7 Diverse Notebook Candidates

These candidates were designed after reviewing current competition discussions, public training notebooks, adapter-merge papers, and prior failed submissions. They are mechanism-diverse rather than small hyperparameter variants.

## Evidence Chain

- [Kaggle discussion 704491](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/704491): training and evaluation variance are material; fixed seed, logging, and optimizer stability matter.
- [Kaggle discussion 703240](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/703240): cryptarithm gains can be cancelled by forgetting in bit, gravity, numeral, and unit conversion.
- [Kaggle discussion 687961](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/687961): rank-32, length-8192 training is feasible on Kaggle RTX Pro 6000 with fused CE and careful microbatching.
- [Kaggle discussion 698293](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/698293): symbolic solvers are useful as distillation/data oracles, not inference-time shortcuts.

Additional implementation sources:

- `mohamedamr992/nemotron-replay-data-0-86`: our verified 0.86 training family.
- `pkuszboi/0-85-lb-training-with-muon`: public Muon training implementation.
- `tonghuikang/nemotron`: training, loss, corpus, and schedule reference.
- `lkevincc0/kaggle-nemotron-equation-symbolic`: symbolic data-oracle reference.
- TIES-Merging, DARE, AdaLoRA, and model-soup literature for merge/rank/interference control.

## Candidate List

| # | Kernel | Route | Mechanism | Hypothesis |
|---:|---|---|---|---|
| 1 | `muelsyse111/nemotron-s7-seed-stability-replay` | full_training | `deterministic_seed_and_reproducible_shuffle` | reduce run-to-run training variance while preserving the full Mohamed replay recipe |
| 2 | `muelsyse111/nemotron-s7-category-round-robin` | full_training | `category_balanced_round_robin_curriculum` | avoid long same-category runs and reduce catastrophic forgetting across the nine task families |
| 3 | `muelsyse111/nemotron-s7-protected-rehearsal` | full_training | `protected_category_loss_reweighting` | protect bit, gravity, numeral, and unit conversion while retaining weak-category replay |
| 4 | `muelsyse111/nemotron-s7-weak-protected-curriculum` | full_training | `weak_category_plus_protected_interleaving` | learn cryptarithm/equation weaknesses without placing weak-category gradients in an isolated block |
| 5 | `muelsyse111/nemotron-s7-answer-tail-objective` | full_training | `tail_focused_loss_masking` | reduce verbose trace imitation and concentrate rank-32 capacity on decisive reasoning and boxed answers |
| 6 | `muelsyse111/nemotron-s7-length-stratified-curriculum` | full_training | `alternating_long_short_sequence_curriculum` | avoid optimization being dominated by either short easy traces or long hard traces |
| 7 | `muelsyse111/nemotron-s7-mamba-inproj-specialist` | full_training | `selective_mamba_in_proj_adaptation` | constrain updates to Mamba input projections to reduce cross-task interference under rank 32 |
| 8 | `muelsyse111/nemotron-s7-muon-full-training` | muon_training | `muon_optimizer_training` | use the public Muon implementation reported by a rank-45 competitor as a more stable optimizer path |
| 9 | `muelsyse111/nemotron-s7-ties-sign-merge` | adapter_merge | `ties_trim_elect_sign_merge` | reduce destructive interference between several 0.86-class adapter anchors |
| 10 | `muelsyse111/nemotron-s7-dare-merge` | adapter_merge | `dare_drop_and_rescale_merge` | sparsify conflicting adapter deltas before combining them |
| 11 | `muelsyse111/nemotron-s7-layerwise-adapter-soup` | adapter_merge | `module_aware_layerwise_weighted_soup` | use different anchor emphasis for attention, Mamba, expert, and output modules |

## Reference Submission Order

This is a preparation order, not permission to submit. Official submission still requires a completed kernel, a valid output package, a unique SHA256, quota availability, and explicit user confirmation.

1. `nemotron-s7-protected-rehearsal` - directly addresses observed category forgetting.
2. `nemotron-s7-muon-full` - optimizer/stability mechanism backed by a public competition notebook.
3. `nemotron-s7-ties-sign-merge` - interference-aware merge over 0.86-class anchors.
4. `nemotron-s7-weak-protected-curriculum` - balances weak and saturated categories.
5. `nemotron-s7-mamba-inproj-specialist` - structurally constrained adaptation.
6. `nemotron-s7-category-roundrobin` - category order balancing.
7. `nemotron-s7-answer-tail-objective` - objective/loss-mask change.
8. `nemotron-s7-dare-merge` - sparse delta merge.
9. `nemotron-s7-layerwise-soup` - module-aware weighted merge.
10. `nemotron-s7-length-stratified` - sequence-difficulty curriculum.
11. `nemotron-s7-seed-stability-replay` - reproducibility control candidate.

No `kaggle competitions submit` command is executed by the generator or notebooks.
