# Stage 8 Submission Run 2026-06-08

- competition: `nvidia-nemotron-model-reasoning-challenge`
- team: `muelsyse111`
- execution_date: `2026-06-08`
- submission_count: 5
- remaining_quota: 0
- competition_submission_executed: true
- local_base_model_loaded: false
- local_training_executed: false

## Submitted Packages

| slot | submission id | candidate | kernel | mechanism | hash prefix | final status | public score | decision |
|---:|---:|---|---|---|---|---|
| 1 | 53467616 | `nemotron-s8-guarded-weak-replay-v1` | `muelsyse111/nemotron-s8-guarded-weak-replay-v1` | guarded weak-category replay | `6b54462e` | `COMPLETE` | 0.84 | reject |
| 2 | 53467618 | `nemotron-s8-answer-tail-512-v1` | `muelsyse111/nemotron-s8-answer-tail-512-v1` | answer-tail 512 loss focus | `b79e16fc` | `COMPLETE` | 0.27 | hard reject |
| 3 | 53467674 | `nemotron-s7-weak-protected-curriculum-v2` | `muelsyse111/nemotron-s7-weak-protected-curriculum-v2` | weak/protected interleaving fallback | `631a2bfb` | `COMPLETE` | 0.85 | reject |
| 4 | 53467675 | `nemotron-s7-seed-stability-replay` | `muelsyse111/nemotron-s7-seed-stability-replay` | deterministic replay fallback | `f5dde9e0` | `COMPLETE` | 0.85 | reject |
| 5 | 53467676 | `nemotron-s7-ties-sign-merge` | `muelsyse111/nemotron-s7-ties-sign-merge` | TIES sign merge fallback | `b03e975e` | `COMPLETE` | 0.84 | reject |

## Official Result Summary

- best_today_public_score: 0.85
- current_best_public_score_remains: 0.86
- quota_used: 5/5
- 0.87_reached: false
- rank_improvement_evidence: none

The 2026-06-08 run did not improve the current best. Both primary Stage8 routes underperformed, and the fallback routes stayed below the known 0.86 family.

## Why Slots 3-5 Used Fallbacks

The intended Stage8 slots 3-5 were:

- `nemotron-s8-attn-mamba-no-lmhead-v1`
- `nemotron-s8-mlp-mamba-no-lmhead-v1`
- `nemotron-s8-rank-stable-alpha64-v1`

They could not be produced before submission because Kaggle returned:

```text
Maximum weekly GPU quota of 30.00 hours reached.
```

The original blocked remote slugs also returned `Notebook not found` on retry, so replacement run2 notebooks were generated:

- `muelsyse111/nemotron-s8-attn-mamba-no-lmhead-run2`
- `muelsyse111/nemotron-s8-mlp-mamba-no-lmhead-run2`
- `muelsyse111/nemotron-s8-rank-stable-alpha64-run2`

Those run2 notebooks preserve the same code and only change the remote Kaggle slug/code filename. They still cannot run until weekly GPU quota is available again.

## Technical Direction

Today's two primary Stage8 submissions test training-objective corrections after the 2026-06-07 failures:

- `guarded_weak_category_replay`: fixes the protected-only 0.85 route by boosting both weak and guard categories instead of isolating guard categories.
- `answer_tail_512_loss_focus`: shifts gradient toward decisive answer-tail tokens to reduce long-trace over-imitation.

The three fallback submissions were chosen because they already had structurally valid `submission.zip` outputs and distinct hashes. They are lower confidence than the blocked Stage8 module-allocation candidates.

## What Failed

- `answer_tail_512_loss_focus` collapsed to 0.27, so aggressive tail-only objective masking is destructive for this competition format.
- `guarded_weak_category_replay` returned 0.84, meaning weak/guard reweighting did not preserve the 0.86 baseline behavior.
- `weak_protected_curriculum` and `seed_stability_replay` both returned 0.85, so replay ordering alone is insufficient.
- `TIES sign merge` returned 0.84, confirming that the current merge-only family is not a productive short-term path.

## Next Technical Direction

Do not repeat today's five hashes. The next viable path should wait for Kaggle weekly GPU quota and prioritize the module-allocation notebooks that could not run:

- `nemotron-s8-attn-mamba-no-lmhead-run2`
- `nemotron-s8-mlp-mamba-no-lmhead-run2`
- `nemotron-s8-rank-stable-alpha64-run2`

If those also fail, return to known 0.86 routes and search for a materially different public adapter or training data source instead of more replay-order or merge-only variants.

## Next Check

```powershell
cd E:\Jitter\nemotron_086plus_repro
kaggle competitions submissions nvidia-nemotron-model-reasoning-challenge -v
```

All 2026-06-08 results are below `0.86`; the next stage should wait for weekly GPU quota and prioritize the three Stage8 module-allocation run2 notebooks.
