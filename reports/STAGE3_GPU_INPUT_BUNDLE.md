# Stage 3 GPU Input Bundle

This bundle stages proxy evaluation only. It does not train, submit, or run local base-model inference.

## Local Inputs

- proxy_set_dir: `eval/proxy_set`
- proxy_set_zip: `artifacts/stage3/proxy_set.zip`
- proxy_set_zip_sha256: `4babcb908631d274a95f9db3f7bc60edee3494d6284019924ef44c0469d18892`
- sample_count: 25
- adapter_dir: `artifacts/stage2/tong_full_repro/adapter`
- submission_zip_path: `artifacts/stage2/tong_full_repro/submission/submission.zip`
- submission_zip_sha256: `db56ce42bcf8aac2ac197521c6596a534a2b49c0dd84bb17914df89841c761a8`
- structural_valid: True
- rank_lte_32: True
- safetensors_opened: True
- official_format_confirmed: False

## Category Coverage

| category | samples |
| --- | --- |
| bit_manipulation | 5 |
| cipher | 5 |
| equation_numeric | 5 |
| symbolic | 5 |
| unit_conversion | 5 |

## Dataset Issues

- null

## Kaggle GPU Run

Use `kernels/proxy_eval_kernel/eval_candidate.py` only in an approved Kaggle GPU environment after manually attaching the proxy set input and an adapter input directory containing `adapter_config.json` and `adapter_model.safetensors`.

Required environment variables:

```text
ENABLE_PROXY_INFERENCE=1
PROXY_SET_DIR=/kaggle/input/<proxy-set-input-dir>
ADAPTER_DIR=/kaggle/input/<adapter-input-dir-containing-adapter-files>
BASE_MODEL=nvidia/NVIDIA-Nemotron-3-Nano-30B-v2
```

Expected Kaggle output:

```text
proxy_predictions.jsonl
proxy_eval_kernel_report.json
```

After downloading `proxy_predictions.jsonl` to `artifacts/stage3/proxy_predictions.jsonl`, run:

```powershell
python scripts/16_stage3_ingest_predictions.py --predictions artifacts/stage3/proxy_predictions.jsonl
```

NEXT_ACTION:
  status: stay_stage3
  action: "run the staged proxy eval kernel on Kaggle GPU, bring back proxy_predictions.jsonl, then run the ingest script"
  reason: "Stage 4 remains blocked until proxy predictions are evaluated locally."
