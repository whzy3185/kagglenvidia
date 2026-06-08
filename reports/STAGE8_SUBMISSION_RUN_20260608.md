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

| slot | submission id | candidate | kernel | mechanism | hash prefix | status at last poll |
|---:|---:|---|---|---|---|---|
| 1 | 53467616 | `nemotron-s8-guarded-weak-replay-v1` | `muelsyse111/nemotron-s8-guarded-weak-replay-v1` | guarded weak-category replay | `6b54462e` | `PENDING` |
| 2 | 53467618 | `nemotron-s8-answer-tail-512-v1` | `muelsyse111/nemotron-s8-answer-tail-512-v1` | answer-tail 512 loss focus | `b79e16fc` | `PENDING` |
| 3 | 53467674 | `nemotron-s7-weak-protected-curriculum-v2` | `muelsyse111/nemotron-s7-weak-protected-curriculum-v2` | weak/protected interleaving fallback | `631a2bfb` | `PENDING` |
| 4 | 53467675 | `nemotron-s7-seed-stability-replay` | `muelsyse111/nemotron-s7-seed-stability-replay` | deterministic replay fallback | `f5dde9e0` | `PENDING` |
| 5 | 53467676 | `nemotron-s7-ties-sign-merge` | `muelsyse111/nemotron-s7-ties-sign-merge` | TIES sign merge fallback | `b03e975e` | `PENDING` |

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

## Next Check

```powershell
cd E:\Jitter\nemotron_086plus_repro
kaggle competitions submissions nvidia-nemotron-model-reasoning-challenge -v
```

If any result returns displayed `0.86`, check public rank before treating it as an improvement. If all results are below `0.86`, the next stage should wait for weekly GPU quota and prioritize the three Stage8 module-allocation run2 notebooks.
