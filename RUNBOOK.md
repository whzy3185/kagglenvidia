# Runbook

1. Run Stage 1 dry-run:

```powershell
python scripts/05_stage1_dry_run.py
```

2. If a candidate adapter exists, validate and package it:

```powershell
python scripts/02_validate_adapter.py --adapter-dir path/to/adapter
python scripts/03_pack_submission.py --adapter-dir path/to/adapter
```

3. Build Stage 2 kernel only after Stage 1 passes and a reproducible baseline is selected:

```powershell
python scripts/06_build_baseline_kernel.py
```

4. Do not submit until score gate approves:

```powershell
python scripts/10_score_gate.py --candidate-manifest path/to/manifest.json
```

5. Prepare Stage 3 proxy-eval inputs:

```powershell
python scripts/15_prepare_stage3_inputs.py
python scripts/18_stage3_kaggle_deploy.py
```

6. After any active local competition submit retry has finished, create the private proxy-set dataset and push the proxy-eval kernel:

```powershell
python scripts/18_stage3_kaggle_deploy.py --create-dataset --yes
python scripts/18_stage3_kaggle_deploy.py --push-kernel --yes
```

The kernel is staged at `kernels/proxy_eval_kernel/`. It auto-detects proxy JSONL files, adapter files, and a mounted base-model directory under `/kaggle/input` when available. If the base model is not automatically mounted, manually attach Kaggle model candidate `metric/nemotron-3-nano-30b-a3b-bf16` before rerunning the kernel.

7. Fetch and ingest proxy predictions after the Kaggle kernel finishes:

```powershell
python scripts/19_stage3_fetch_proxy_predictions.py --yes
python scripts/14_stage4_readiness.py
python scripts/17_stage4_candidate_plan.py
```

8. Stage 4 execution remains blocked until `reports/STAGE4_READINESS.md` says `can_start_stage4: True`.
