# Huikang V27 Route Decision

- timestamp: 2026-06-04
- route: `huikang_v27_kaggle_side_repack`
- source: `huikang/nemotron-adapter/Transformers/default/27`
- model_is_private: false
- model_license: Apache 2.0
- dataset_source_used: false
- official_score_obtained: false
- decision: `stop_blind_submits`

## Evidence

| attempt | submission_id | package | status | public_score |
| --- | --- | --- | --- | --- |
| local upload/raw or earlier repack | 53329563 | raw adapter package | SubmissionStatus.ERROR | null |
| notebook v1 | 53350464 | raw Kaggle-side repack | SubmissionStatus.ERROR | null |
| notebook v1 repeat | 53351317 | raw Kaggle-side repack | SubmissionStatus.ERROR | null |
| notebook v2 | 53352307 | normalized config + zero-tensor-stripped model | SubmissionStatus.ERROR | null |

## Interpretation

The notebook workflow is working: it can mount the Kaggle model source and create a structurally valid `submission.zip`. The official evaluator still fails. Repeating this route is now a quota risk, not a high-score path.

## Decision

Do not submit Huikang v27 again today. Only resume this exact route if one of these happens:

- Kaggle submission details expose a concrete loader error that can be fixed.
- A different officially accepted packaging format is found from a trusted public source.
- A new adapter asset with different provenance is selected.

## Next Action

```yaml
NEXT_ACTION:
  status: switch_route
  action: "inspect Kaggle error details once, then audit a different public adapter or trainable baseline"
  reason: "The current Huikang v27 adapter has failed official evaluation across raw and normalized packages."
```
