# Stage 7 Aggressive Notebook Run 2026-06-06

## Summary

```yaml
generated_notebooks:
  - muelsyse111/nemotron-stage7-multi-anchor-fusion-factory
  - muelsyse111/nemotron-stage7-reasoning-data-factory
pushed_to_kaggle: true
competition_submission_executed: true
submission_id: 53424138
today_submission_count_after_submit: 4
today_remaining_quota_after_submit: 1
```

## Notebook 1: Multi-Anchor Fusion Factory

```yaml
kernel_id: muelsyse111/nemotron-stage7-multi-anchor-fusion-factory
kernel_version: 1
status: output_ready
candidate: keithtyser_task_arithmetic_delta_rank32
source_model: keithtyser/nemotron-086-adapters-20260605
method: task_arithmetic_delta_rank32
base_anchor: public_hk_to_kn_lm_head_lam1p0
delta_anchors:
  public_kn_to_hk_lm_head_lam1p0: 0.35
  public_hk_to_kn_mamba_lam1p0: 0.2
rank_lte_32: true
tensor_keys: 12010
zip_namelist:
  - adapter_config.json
  - adapter_model.safetensors
merged_adapter_sha256: f3dbdddda01b2258777e136a52b3af45be93e337c2fb39ef10d57482c18d6282
submission_zip_sha256: 3b1d2fc378c6b9014c9b4ec742775db3031dddf562cfa86ba12ab1b448d50949
submission_zip_size_bytes: 3270593850
```

Submission:

```yaml
submission_id: 53424138
message: 20260606_slot4_stage7_keithtyser_taskarith_3b1d2fc3
status_at_last_check: PENDING
public_score_at_last_check: null
```

## Notebook 2: Reasoning Data Training Factory

```yaml
kernel_id: muelsyse111/nemotron-stage7-reasoning-data-factory
kernel_version: 1
status: no_output_yet
output_submission_zip_exists: false
submitted: false
reason_not_submitted: "Kaggle output file list is empty; no submission.zip exists."
```

This notebook was generated from the Mohamed replay-data training chain and injects a Stage 7 `hard_unmasked_curriculum_mix` data-processing step. It was pushed successfully, but at the time of this report Kaggle had not exposed logs or output files.

## Current Submission History

```yaml
latest_submission:
  id: 53424138
  status: PENDING
  public_score: null
today_submission_count: 4
today_remaining_quota: 1
```

## Safety

- No local 30B base model load was performed.
- No local training was performed.
- No `.safetensors` or `submission.zip` was committed.
- The second notebook was not submitted because no validated output existed.
- One remaining quota slot is intentionally unused until a real `submission.zip` exists.

## Next Check

```powershell
kaggle competitions submissions nvidia-nemotron-model-reasoning-challenge -v
kaggle kernels files muelsyse111/nemotron-stage7-reasoning-data-factory -v --page-size 100
```
