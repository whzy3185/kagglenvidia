# Submission Error Triage

- timestamp: 2026-06-04
- competition: `nvidia-nemotron-model-reasoning-challenge`
- candidate: `huikang_v27_kaggle_side_repack`
- kernel: `muelsyse111/nemotron-repack-huikang-v27`
- kernel_status_checked: `COMPLETE`
- notebook_output_zip_seen: true
- notebook_log_success_marker: `OK: /kaggle/working/submission.zip is ready.`
- notebook_zip_size_bytes: `1544349350`
- notebook_zip_sha256: `1b2ea89dd9959909b541397394b406a3be67cc85743ea5cdadf9e22e24bdedf8`
- local_adapter_structural_valid: true
- local_rank_lte_32: true
- local_safetensors_opened: true
- official_format_confirmed: false
- huikang_model_is_private: false
- huikang_model_license: Apache 2.0
- dataset_sources_used_for_adapter: false

## Current Kaggle Submission State

| submission_id | date | status | public_score | note |
| --- | --- | --- | --- | --- |
| 53352307 | 2026-06-04 06:39:53.923000 | SubmissionStatus.ERROR | null | v2 normalized repack also failed official evaluation |
| 53351317 | 2026-06-04 06:04:15.417000 | SubmissionStatus.ERROR | null | v1 raw repack failed official evaluation |
| 53350464 | 2026-06-04 05:29:54.377000 | SubmissionStatus.ERROR | null | user observed failure after waiting |
| 53329563 | 2026-06-03 13:37:44.970000 | SubmissionStatus.ERROR | null | earlier local upload attempt |

## Interpretation

The Kaggle-side Notebook did mount the model source and did generate a large `submission.zip` with exactly:

```text
adapter_config.json
adapter_model.safetensors
```

Therefore the failed submission should not be treated as a notebook-resource failure or local-upload failure. The more likely failure boundary is the official competition evaluator loading or accepting this adapter package.

## Adapter Config Risk Points

Observed config values:

```json
{
  "peft_type": "LORA",
  "r": 32,
  "target_modules": "all-linear",
  "base_model_name_or_path": null,
  "task_type": "CAUSAL_LM"
}
```

These pass structural checks, but structural-valid is not the same as official-valid. Possible official evaluator incompatibilities include:

- `target_modules: "all-linear"` may not match the evaluator loader's expected module list.
- `base_model_name_or_path: null` may not be accepted by the competition loader.
- The public Kaggle model may be a reference artifact but not directly compatible with the current official evaluator.
- The competition may require a stricter adapter metadata format than local structural validation checks.

## V2 Attempt Result

The normalized V2 notebook changed:

```text
target_modules: all-linear -> explicit module list
base_model_name_or_path: null -> nvidia/Nemotron-3-Nano-30B-A3B-BF16
inference_mode: false -> true
removed_zero_tensor_count: 46
```

The notebook output was structurally valid, but official evaluation still returned `SubmissionStatus.ERROR`. This strongly suggests the Huikang v27 adapter package is not directly compatible with the current official evaluator, or the official evaluator has an undisclosed loader/metric failure path for this artifact.

## Asset Privacy Check

This route uses Kaggle `model_sources`, not `dataset_sources`:

```json
{
  "model_sources": ["huikang/nemotron-adapter/Transformers/default/27"],
  "dataset_sources": []
}
```

Kaggle model metadata check:

```json
{
  "ownerSlug": "huikang",
  "slug": "nemotron-adapter",
  "isPrivate": false
}
```

Kaggle model instance metadata check:

```json
{
  "framework": "transformers",
  "licenseName": "Apache 2.0",
  "versionNumber": 27,
  "trainingData": []
}
```

So the failure is not explained by a private dataset permission issue.

## Do Not Do

- Do not repeat-submit Huikang v27 raw or normalized packages today.
- Do not consume slot2-slot5 with the same hash.
- Do not call this candidate proven high-score until a `COMPLETE` public score exists.
- Do not treat Notebook `COMPLETE` as competition `COMPLETE`.

## Next Checks

1. Inspect the Kaggle website submission detail pages for `53352307`, `53351317`, and `53350464`.
2. Query if needed:

```powershell
kaggle competitions submissions nvidia-nemotron-model-reasoning-challenge -v
```

3. If the website still exposes only `Evaluation metric raised an unexpected error`, stop this route and switch to another public adapter or a trainable baseline.
4. Do not build a third blind Huikang v27 variant without a concrete official error detail.

## Recommended Next Action

```yaml
NEXT_ACTION:
  status: blocked
  action: "inspect Kaggle submission detail error for 53352307, then switch route if no concrete loader error is exposed"
  reason: "Huikang v27 raw and normalized packages both fail official evaluation despite structurally valid notebook output."
```
