# Stage 3 to Stage 4 Handoff

Stage 3 has been supplemented with Kaggle deployment scaffolding, but it is not complete until real proxy predictions are produced by the Kaggle GPU kernel and ingested locally.

## Stage 3 Added Components

- `scripts/18_stage3_kaggle_deploy.py`
- `scripts/19_stage3_fetch_proxy_predictions.py`
- `kernels/proxy_eval_kernel/proxy_eval_kernel_config.json`
- `artifacts/stage3/kaggle_proxy_set_dataset/`
- `artifacts/stage3/kaggle_deployment_manifest.json`
- `reports/STAGE3_KAGGLE_DEPLOYMENT.md`
- `reports/STAGE3_PROXY_OUTPUT_FETCH.md`

## Kaggle Deployment Targets

- proxy_dataset_ref: `muelsyse111/nemotron-086plus-proxy-set`
- proxy_kernel_ref: `muelsyse111/nemotron-086plus-proxy-eval`
- adapter_model_source: `huikang/nemotron-adapter/Transformers/default/27`
- base_model_candidate: `metric/nemotron-3-nano-30b-a3b-bf16`

## Current Blocking Point

- missing_file: `artifacts/stage3/proxy_predictions.jsonl`
- stage3_complete: false
- stage4_can_start: false
- blocker: `proxy_eval_not_complete`

## Execution Order After Active Submit Retry Finishes

```powershell
python scripts/18_stage3_kaggle_deploy.py --create-dataset --yes
python scripts/18_stage3_kaggle_deploy.py --push-kernel --yes
python scripts/19_stage3_fetch_proxy_predictions.py --yes
python scripts/14_stage4_readiness.py
python scripts/17_stage4_candidate_plan.py
```

Do not execute fusion, specialist training, or daily runner until `reports/STAGE4_READINESS.md` reports `can_start_stage4: True`.

NEXT_ACTION:
  status: stay_stage3
  action: "wait for the active Kaggle submit retry to finish, then deploy the Stage 3 proxy kernel"
  reason: "Stage 4 remains blocked until proxy_predictions.jsonl is generated and ingested."
