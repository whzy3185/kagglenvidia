# Stage 7 Round Review 2026-06-06

## Baseline

```yaml
BASELINE:
  team: muelsyse111
  best_public_score_before: 0.86
  best_public_rank_before: 393
  target_public_rank: "<100"
  leaderboard_snapshot: logs/leaderboard_20260606_after_stage7/nvidia-nemotron-model-reasoning-challenge.zip
  primary_metric: public_rank_delta
```

## Submissions

| slot | submission_id | candidate | source | main_change | status | public_score | candidate_score_tier_rank_range | team_rank_after | result_class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| slot1 | `53416566` | `hammad_agi_for_medal_087` | `hammadfarooq470/agi-for-medal-0-87` | Public output repack of Huikang v20 block-topk floor4 rank-32 compression | COMPLETE | `0.85` | `1405-1885` | `393` | worse |
| slot2 | `53416809` | `dedquoc_svd_fusion` | `dedquoc/nvidia-nmrc-low-rank-svd-lora-adapter-fusion` | Public output repack of QR-trick SVD fusion, rank 32 | COMPLETE | `0.78` | `2201-2207` | `393` | worse |
| slot3 | `53417126` | `kuang_087_training` | `kuangyicheng/nemotron-087-training` | Public output repack of warmstart training route | COMPLETE | `0.63` | `2908-2976` | `393` | worse |

## Skipped Candidate

```yaml
SKIPPED:
  candidate: cocoaai_huikang_087_svd
  reason: "same SHA256 as Hammad output"
  sha256: 945fe257b6222b471aff3d62f5c33edf1e64b0e8570691c9d9fd4ace6c5d75fa
  action: "do not submit duplicate hash"
```

## Evaluation

```yaml
ROUND_RESULT:
  best_public_score_after: 0.86
  best_public_rank_after: 393
  rank_delta: 0
  submissions_used_today: 3
  remaining_quota: 2
  result_class: no_improvement
```

The public-output repack path did not improve rank. The key failure is not zip structure or rank compliance: all submitted outputs were structurally valid. The failure is candidate quality. Notebook titles and claimed `0.87` labels were not reliable predictors of official score.

## What Worked

- Kaggle-side output submission workflow worked.
- Remote output submissions were registered correctly.
- Duplicate hash filtering prevented submitting CocoaAI, which was identical to Hammad.
- The round produced useful negative evidence quickly.

## What Failed

- Hammad scored `0.85`, below the existing `0.86` best.
- Dedquoc scored `0.78`, much worse than expected for a fusion/SVD route.
- Kuang scored `0.63`, indicating its exposed output is not competitive despite the notebook title.
- Continuing to submit public output repacks is unlikely to move rank toward `<100`.

## Next Direction

```yaml
NEXT_DIRECTION:
  status: require_real_delta_before_more_submissions
  do_not_submit:
    - public_output_repack_without_modification
    - same_hash_duplicate
    - title_claim_only_087
    - Huikang_v27_raw_or_normalized
    - Kien_0_63_family_without_new_training_change
    - Akihiko_0_50_family
  priority:
    1: "modify a known 0.86 route with one real variable"
    2: "train a fresh rank<=32 adapter on Kaggle GPU using Mohamed/Taha style recipe"
    3: "build a fusion variant from two known 0.86 adapters, not from lower-score public outputs"
    4: "use remaining quota only after a submit confirm card and explicit user confirmation"
```

## Candidate Experiments For Remaining Quota

```yaml
REMAINING_QUOTA_PLAN:
  remaining_quota: 2
  submit_now: false
  reason: "No prepared candidate currently has a real mechanism distinct from failed public-output repacks."
  candidate_1:
    name: mohamed_lr_3e4_or_2p5e4_variant
    type: Kaggle GPU training variant
    main_variable: learning_rate
    base_route: mohamedamr992/nemotron-replay-data-0-86
    expected_effect: "May move within the 0.86 plateau if training route is reproducible."
    requirement: "Build/run notebook first; submit only after output and submit confirm card."
  candidate_2:
    name: taha_replay_mix_variant
    type: Kaggle GPU training/data mix variant
    main_variable: replay or hard-case data ratio
    base_route: tahaalam2009/end-to-end-finetuning-for-lb-0-86-custom-repo
    expected_effect: "May improve within 0.86 tier if data mix changes task behavior."
    requirement: "Build/run notebook first; submit only after output and submit confirm card."
```

## Decision

```yaml
DECISION:
  current_best_rank: 393
  current_best_score: 0.86
  target_rank: "<100"
  next_action: "prepare one real training or fusion-delta candidate, then ask user before submission"
  reason: "Three public output repacks failed to improve rank; remaining quota should be reserved for candidates with actual mechanism changes."
```
