# Stage 8 Tomorrow Submission Package Plan

- generated_at: 2026-06-07T21:14:39
- target: improve displayed 0.86 family toward 0.87 / rank movement
- tomorrow_package_count: 5
- competition_submission_executed: false
- local_base_model_loaded: false
- local_training_executed: false

## Today's Result-Derived Fix

- 2026-06-07 slot1 protected rehearsal: 0.85.
- 2026-06-07 slot2 delta-space SVD: 0.85.
- 2026-06-07 slot3 modulewise delta SVD: 0.85.
- 2026-06-07 slot4 Muon audit/repack: 0.84.
- 2026-06-07 slot5 mamba in-proj specialist: pending at generation time.

Conclusion: tomorrow's primary queue should move away from pure SVD/Muon reuse and test training-objective and target-module changes.

## Evidence Chain

- [Kaggle CLI current results](local reports/SCORECARD.md): 2026-06-07 SVD-family slots returned 0.85 and Muon audit returned 0.84, so tomorrow should not spend all slots on SVD/Muon variants.
- [bankoglu/hard-families-cot](https://www.kaggle.com/datasets/bankoglu/hard-families-cot): small MIT-licensed hard-family CoT dataset exposes weak-family prompts and generated traces for later corpus preprocessing.
- [Hugging Face PEFT model merging](https://huggingface.co/docs/peft/developer_guides/model_merging): adapter merging can be useful, but today's SVD results suggest merge-only candidates should be backups.
- [TIES-Merging](https://arxiv.org/abs/2306.01708): interference-aware merging remains a reserve, not the primary tomorrow path after two SVD-family failures.
- [DoRA / AdaLoRA / LoRA-GA family](https://arxiv.org/abs/2402.09353): rank and module capacity allocation are stronger next levers than another plain 0.86 repack.

## Five Packages for Tomorrow

| slot | candidate | kernel | mechanism | technical path | validation |
|---:|---|---|---|---|---:|
| 1 | `nemotron-s8-guarded-weak-replay-v1` | `muelsyse111/nemotron-s8-guarded-weak-replay-v1` | `guarded_weak_category_replay` | today's protected route scored 0.85, so this variant weakly boosts both weak and guard families instead of protecting only guard families. | true |
| 2 | `nemotron-s8-answer-tail-512-v1` | `muelsyse111/nemotron-s8-answer-tail-512-v1` | `answer_tail_512_loss_focus` | targets the long-trace over-imitation risk without shortening training or changing the submission format. | true |
| 3 | `nemotron-s8-attn-mamba-no-lmhead-v1` | `muelsyse111/nemotron-s8-attn-mamba-no-lmhead-v1` | `attention_mamba_without_lm_head` | today's full-target variants underperformed; this tests a narrower adaptation surface instead of another data-only tweak. | true |
| 4 | `nemotron-s8-mlp-mamba-no-lmhead-v1` | `muelsyse111/nemotron-s8-mlp-mamba-no-lmhead-v1` | `mlp_mamba_without_attention_lm_head` | pairs with the attention+mamba candidate as a module-allocation ablation rather than a small scalar sweep. | true |
| 5 | `nemotron-s8-rank-stable-alpha64-v1` | `muelsyse111/nemotron-s8-rank-stable-alpha64-v1` | `rank32_high_alpha_capacity_test` | tests whether the 0.85 plateau is under-adaptation rather than data selection; rank remains <=32. | true |

## Submission Policy

- These notebooks may be pushed to Kaggle to generate remote `submission.zip` outputs.
- They must not be submitted to the competition until tomorrow's quota is available and the current pending slot5 result has been reviewed.
- Any candidate returning `0.86` should trigger a leaderboard rank check before spending the next slot.
- Do not commit generated `submission.zip`, `.safetensors`, or external cache files.
