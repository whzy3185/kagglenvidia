# Stage 3 Prediction Ingest

This report validates returned proxy predictions before marking Stage 3 complete. It does not claim an official Kaggle score.

- status: blocked
- predictions_file_exists: False
- predictions_path: `artifacts/stage3/proxy_predictions.jsonl`
- sample_count: 25
- prediction_count: 0
- can_evaluate: False
- missing_count: 25
- extra_count: 0
- empty_output_count: 0

## Dataset Issues

- null

## Parse Issues

- prediction file missing: E:\Jitter\nemotron_086plus_repro\artifacts\stage3\proxy_predictions.jsonl

## Blocking Issues

- missing predictions for 25 samples

## Missing By Category

| category | missing |
| --- | --- |
| bit_manipulation | 5 |
| cipher | 5 |
| equation_numeric | 5 |
| symbolic | 5 |
| unit_conversion | 5 |

## Proxy Eval Summary

- not_run

NEXT_ACTION:
  status: stay_stage3
  action: "run the staged proxy eval kernel on Kaggle GPU and save proxy_predictions.jsonl under artifacts/stage3"
  reason: "Stage 3 cannot complete until Kaggle GPU predictions are returned locally."
