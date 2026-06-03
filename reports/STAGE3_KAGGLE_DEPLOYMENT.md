# Stage 3 Kaggle Deployment

This prepares the Kaggle-side proxy eval deployment. It does not train locally, submit a competition file, or load a base model locally.

- dataset_ref: `muelsyse111/nemotron-086plus-proxy-set`
- kernel_ref: `muelsyse111/nemotron-0-86-proxy-eval`
- adapter_model_source: `huikang/nemotron-adapter/Transformers/default/27`
- base_model_candidate: `metric/nemotron-3-nano-30b-a3b-bf16`
- base_model_source: `metric/nemotron-3-nano-30b-a3b-bf16/transformers/default/1`
- base_model_source_status: attached_in_kernel_metadata
- no_local_base_model_loading: true
- no_training: true
- no_submission: true
- enable_internet: true

## Proxy Dataset Files

| path | size | sha256 |
| --- | --- | --- |
| artifacts/stage3/kaggle_proxy_set_dataset/generated_bit.jsonl | 1158 | 6ca3ae6e4da49f90ea570a4e2080b2ff202a9ab34c379447771d2e97a6de004a |
| artifacts/stage3/kaggle_proxy_set_dataset/generated_cipher.jsonl | 1105 | 8d87ae3a6aff43aa52de0d4162ee852d74fc63424a86f1a37e178ba035305147 |
| artifacts/stage3/kaggle_proxy_set_dataset/generated_numeric.jsonl | 1113 | 3f6977582584621a5262ecaf4fc502ff2344cb7480499d3d4a83385025f2cd2f |
| artifacts/stage3/kaggle_proxy_set_dataset/generated_symbolic.jsonl | 1193 | 8540c166a2e518065c0eef085f03ec610b8e5079963feab2b9826344c091258a |
| artifacts/stage3/kaggle_proxy_set_dataset/generated_unit_conversion.jsonl | 1150 | b0dd35694c7ee9a82025a38d0589fdbc2edf9dd8e9642f834aef23b19106db37 |

## Kernel Inputs

- dataset_sources: `['muelsyse111/nemotron-086plus-proxy-set']`
- model_sources: `['huikang/nemotron-adapter/Transformers/default/27', 'metric/nemotron-3-nano-30b-a3b-bf16/transformers/default/1']`
- kernel_metadata: `kernels/proxy_eval_kernel/kernel-metadata.json`
- kernel_config: `kernels/proxy_eval_kernel/proxy_eval_kernel_config.json`

## Kaggle Actions

| name | status | returncode | log_path | stderr_head |
| --- | --- | --- | --- | --- |
| push_kernel | success | 0 | logs/stage3_push_kernel.log |  |

## Caveat

The adapter model source and base model source are attached in kernel metadata. The kernel still auto-detects mounted paths under `/kaggle/input` because Kaggle input mount names can vary.

NEXT_ACTION:
  status: stay_stage3
  action: "wait for Kaggle kernel completion, then download proxy_predictions.jsonl"
  reason: "Proxy eval cannot complete until the Kaggle kernel output is available locally."
