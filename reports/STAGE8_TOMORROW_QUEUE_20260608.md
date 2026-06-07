# Stage 8 Tomorrow Queue 2026-06-08

- generated_at: 2026-06-07
- target: move beyond the current displayed 0.86 family toward 0.87 / better public rank
- competition_submission_executed: false
- local_base_model_loaded: false
- local_training_executed: false

## Today's Official Feedback

| slot | candidate | official public score | decision |
|---:|---|---:|---|
| 1 | protected rehearsal | 0.85 | do not repeat |
| 2 | delta-space SVD | 0.85 | demote SVD-only family |
| 3 | modulewise delta-SVD | 0.85 | demote SVD-only family |
| 4 | Muon v5 audited repack | 0.84 | do not submit audit/repack path again |
| 5 | mamba in-proj specialist v2 | 0.81 | do not repeat narrow in-proj-only path |

Conclusion: tomorrow should not spend quota on pure SVD, audited Muon repack, or in-proj-only specialization. The next useful attempts need broader training-objective or target-module changes.

## Primary Five Packages

These five notebook packages have been generated locally and pushed to Kaggle. They are not competition submissions. They become tomorrow submission packages only after Kaggle produces `submission.zip` in the notebook output and the hash is recorded.

| tomorrow slot | candidate | kernel | current package state | technical path | why this fixes today's result |
|---:|---|---|---|---|---|
| 1 | `nemotron-s8-guarded-weak-replay-v1` | `muelsyse111/nemotron-s8-guarded-weak-replay-v1` | queued/no logs yet | weak-category replay with guard-family weighting | protected-only weighting scored 0.85; this weakly boosts both weak and guard families to reduce forgetting without isolating one group |
| 2 | `nemotron-s8-answer-tail-512-v1` | `muelsyse111/nemotron-s8-answer-tail-512-v1` | queued/no logs yet | 512-token answer-tail loss focus | aims at over-imitation of long traces while preserving full training length and rank 32 |
| 3 | `nemotron-s8-attn-mamba-no-lmhead-v1` | `muelsyse111/nemotron-s8-attn-mamba-no-lmhead-v1` | created but GPU-blocked | attention + Mamba target modules, no lm_head/MLP adapter | tests whether full-target updates overfit output head or MLP modules |
| 4 | `nemotron-s8-mlp-mamba-no-lmhead-v1` | `muelsyse111/nemotron-s8-mlp-mamba-no-lmhead-v1` | created but GPU-blocked | MLP + Mamba target modules, no attention/lm_head adapter | pairs with slot 3 as a module-allocation ablation |
| 5 | `nemotron-s8-rank-stable-alpha64-v1` | `muelsyse111/nemotron-s8-rank-stable-alpha64-v1` | created but GPU-blocked | rank-32 high-alpha capacity test | tests whether the 0.85 plateau is under-adaptation rather than bad data selection |

## Open-Source / Public Evidence Chain

- Kaggle `bankoglu/hard-families-cot`: MIT hard-family CoT data source for future weak-family preprocessing.
- Hugging Face PEFT model merging docs: adapter merging remains useful, but today's SVD failures make it a backup path.
- TIES-Merging and DARE papers: interference-aware merge methods remain reserve options, not tomorrow's primary queue.
- DoRA / AdaLoRA / LoRA-GA family: supports the next focus on rank/module capacity allocation rather than another plain repack.

## Fallback Ready Packages

Use these only if the primary Stage8 training notebooks do not produce enough output packages before tomorrow's quota window. They are structurally ready but lower confidence after today's results.

| fallback order | candidate | reason to keep | reason not primary |
|---:|---|---|---|
| F1 | `nemotron-s7-weak-protected-curriculum-v2` | completed full training, distinct from submitted protected-only route | related family underperformed at 0.85 and mamba v2 scored 0.81 |
| F2 | `nemotron-s7-seed-stability-replay` | completed full training, deterministic replay baseline | likely close to the already-known Mohamed 0.86 family |
| F3 | `nemotron-s7-ties-sign-merge` | interference-aware merge, already output-ready | merge/SVD family underperformed today |
| F4 | `nemotron-s7-dare-merge` | stochastic drop-rescale merge, already output-ready | merge-only path remains weak evidence |
| F5 | `nemotron-s7-layerwise-adapter-soup` | module-aware soup, already output-ready | heuristic merge without public feedback |

## Commands

Check Stage8 remote outputs:

```powershell
cd E:\Jitter\nemotron_086plus_repro
python scripts\39_check_stage8_tomorrow_runs.py
```

If slots 3-5 are still GPU-blocked after slots 1-2 finish, rerun push:

```powershell
python scripts\38_push_stage8_tomorrow_notebooks.py
```

Refresh quota and current submissions before any real submit:

```powershell
python scripts\04_query_submissions.py
python scripts\22_make_daily_submission_plan.py
```

## Submit Rule

Do not submit any Stage8 package until all of these are true:

- tomorrow quota is available;
- `submission.zip` is visible in the selected kernel output;
- notebook logs contain `OK: /kaggle/working/submission.zip is ready.`;
- zip root is exactly `adapter_config.json` and `adapter_model.safetensors`;
- SHA256 is recorded;
- the current pending/day result has been reviewed;
- no duplicate hash was already submitted.
