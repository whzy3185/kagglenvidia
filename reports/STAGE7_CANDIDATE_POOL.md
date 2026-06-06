# Stage 7 Candidate Pool

## Selection Rule

Prioritize candidates with:

- total score >= 24,
- rank_gain_potential >= 3,
- asset_availability >= 3,
- Kaggle resource fit >= 3,
- one real mechanism change,
- no duplicate hash,
- no direct repeat of known low-score public outputs.

## Ranked Candidates

| Rank | Candidate | Priority | Total | Main change | Resource | Next action |
|---:|---|---|---:|---|---|---|
| 1 | `keithtyser_anchor_ties_svd_rank32` | P0 | 27 | merge six 0.86-class rank32 anchors with TIES/DARE/weighted SVD | Kaggle notebook | inventory model files, then prepare merge notebook |
| 2 | `mohamed_replay_lr_3e4` | P1 | 26 | single LR change on known 0.86 replay route | Kaggle GPU training | build smoke/full training notebook |
| 3 | `taha_replay_mix_variant` | P1 | 25 | one replay/hard-case ratio or sample-order variable | Kaggle GPU training | inspect notebook inputs and build variant |
| 4 | `rauffauzan_anchor_weight_065_035` | P2 | 24 | fusion code with new anchors and one merge weight | Kaggle notebook | combine verified 0.86 anchors, confirm new SHA |
| 5 | `mohamed_openmath_5k_mix` | P3 | 23 | small filtered external reasoning data slice | Kaggle GPU training | defer until training smoke succeeds |
| 6 | `tong_loss_mask_answer_only` | P3 | 22 | one loss-mask or LR-schedule change | Kaggle GPU/external GPU | defer; heavier than Mohamed/Taha |
| blocked | `hammad_dedquoc_kuang_public_output_repack` | BLOCKED | 17 | none | none | do not submit |

## Candidate Details

### 1. `keithtyser_anchor_ties_svd_rank32`

```yaml
submit_priority: P0
candidate_score:
  rank_gain_potential: 4
  method_distinctness: 5
  asset_availability: 4
  implementation_speed: 3
  kaggle_resource_fit: 4
  risk_control: 3
  replay_value: 4
  total: 27
```

Why first: this is the fastest route that may create a genuinely new 0.86+ plateau candidate. It is not a public output repack; it uses several same-format adapter anchors and a merge/compression mechanism. The next notebook should only inventory and merge files on Kaggle; no official submission until a confirm card exists.

### 2. `mohamed_replay_lr_3e4`

```yaml
submit_priority: P1
candidate_score:
  rank_gain_potential: 3
  method_distinctness: 3
  asset_availability: 4
  implementation_speed: 3
  kaggle_resource_fit: 4
  risk_control: 4
  replay_value: 5
  total: 26
```

Why second: our submitted Mohamed output scored 0.86, so this route has proven official evaluator compatibility. A single LR variant is easy to explain and review, but requires Kaggle GPU training to produce a real new adapter.

### 3. `taha_replay_mix_variant`

```yaml
submit_priority: P1
candidate_score:
  rank_gain_potential: 3
  method_distinctness: 4
  asset_availability: 3
  implementation_speed: 3
  kaggle_resource_fit: 4
  risk_control: 3
  replay_value: 5
  total: 25
```

Why third: also officially scored 0.86 for us, and data-mix variation is a distinct mechanism from LR-only tuning. It should not repeat the old public output.

### 4. `rauffauzan_anchor_weight_065_035`

```yaml
submit_priority: P2
candidate_score:
  rank_gain_potential: 3
  method_distinctness: 4
  asset_availability: 3
  implementation_speed: 4
  kaggle_resource_fit: 4
  risk_control: 3
  replay_value: 3
  total: 24
```

Why fourth: fusion code is available and prior family reached 0.86, but old output is not enough. It becomes useful only when paired with new verified anchors.

## Blocked / Do Not Submit

| Candidate | Reason |
|---|---|
| Hammad public output | scored 0.85 for our team |
| Dedquoc public output | scored 0.78 for our team |
| Kuang public output | scored 0.63 for our team |
| CocoaAI public output | SHA256 duplicate of Hammad |
| Kien/Akihiko low-score routes | no new mechanism, previously low score |
| DoRA direct adapter | official evaluator compatibility unknown |
| LoRAHub weight search | needs proxy metric; do not use leaderboard as optimizer |

## Recommended Execution Order

1. Build `keithtyser_anchor_inventory` Kaggle notebook.
2. If model files resolve cleanly, build `keithtyser_anchor_ties_svd_rank32` merge notebook.
3. If anchor route is blocked, switch to `mohamed_replay_lr_3e4` Kaggle GPU training notebook.
4. Generate `reports/STAGE7_SUBMIT_CONFIRM_<date>_<slot>_<candidate>.md` before any real competition submission.

## Current Submission Boundary

No `kaggle competitions submit` was executed while preparing this pool.
