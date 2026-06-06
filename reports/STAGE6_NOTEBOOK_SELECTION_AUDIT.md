# Stage 6 Notebook Selection Audit

## Rank Baseline

- current_best_displayed_score: `0.86`
- current_public_rank: `393`
- leaderboard_snapshot: `logs/leaderboard_20260606/nvidia-nemotron-model-reasoning-challenge.zip`
- decision_metric: `public_rank_delta`
- improvement_rule: `new_rank < 393`

## Candidate Audit

| route | author | source_type | source_url_or_kernel | claimed_score | claimed_rank | rank_evidence | our_verified_score | our_verified_rank | mechanism | same_as_current_best | duplicate_hash | output_available | adapter_rank_lte_32 | zip_structure_known | submit_priority | next_action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hammad_agi_for_medal_087 | hammadfarooq470 | notebook_output | `hammadfarooq470/agi-for-medal-0-87` | `0.87` | unknown | notebook title + public output + source code | null | null | `block_topk_floor4_model` over Huikang v20, forced fused rank 32, candidate zip emitted by notebook | false | unknown | true | true | true | P0 | push local repack notebook and wait for output |
| kuangyicheng_nemotron_087_training | kuangyicheng | notebook_output | `kuangyicheng/nemotron-087-training` | `0.87-0.88` | unknown | notebook title + public output + source code | null | null | Huikang v27 warmstart + synthetic data + 240-step finetune + flat submission packaging | false | unknown | true | true | true | P1 | keep as slot2 candidate after one Hammad result |
| dedquoc_svd_fusion_repack | dedquoc | notebook_output | `dedquoc/nvidia-nmrc-low-rank-svd-lora-adapter-fusion` | null | unknown | source code only | null | null | QR-trick SVD fusion over Huikang v20 with forced rank 32 | false | unknown | true | true | true | P2 | keep as fallback if 0.87 routes fail |
| cocoaai_huikang_087_svd_submit | cocoaai | notebook_output | `cocoaai/nvidia-nemotron-huikang-0-87-svd-submit` | `0.87` | unknown | derivative notebook title + output | null | null | public repack around Hammad family zip, not a clearly new mechanism | false | likely_same_family | true | true | true | P3 | use only if Hammad route has structural issue |

## Selection

- selected_candidate: `hammad_agi_for_medal_087`
- reason:
  - It has public output and a concrete compression mechanism, not just a score claim.
  - It is not one of the already-submitted 0.86 routes from 2026-06-05.
  - It is cheaper to validate than retraining Kuang's route while still offering `0.87` evidence.
- rejected_as_slot1:
  - `kuangyicheng_nemotron_087_training`: promising, but training-derived route is heavier and better used after one simpler high-evidence candidate.
  - `dedquoc_svd_fusion_repack`: structurally good fallback, but lacks stronger-than-0.86 evidence.
  - `cocoaai_huikang_087_svd_submit`: too derivative of the Hammad family for the first slot.

## Tuning Direction

- preferred family: `hammad_agi_for_medal_087`
- single-variable axis: `candidate spec selection`
- first variant: `block_topk_floor4_model`
- later variants:
  - `block_topk_floor4_x_bias_model`
  - `block_topk_floor4_model_no_lm_head`
  - `dense_svd_model`
- rule: do not open a second variant until the first official result is known
