# Stage 3 Proxy Kernel Plan

The proxy eval kernel is staged at `kernels/proxy_eval_kernel/`.

It does not run inference by default. In Kaggle GPU, after manual review, set:

```text
ENABLE_PROXY_INFERENCE=1
PROXY_SET_DIR=/kaggle/input/nemotron-proxy-set
ADAPTER_DIR=/kaggle/input/tong-full-repro-adapter
```

Expected output:

```text
proxy_predictions.jsonl
proxy_eval_kernel_report.json
```

Then copy `proxy_predictions.jsonl` back locally and run:

```powershell
python scripts/09_proxy_eval.py --predictions path/to/proxy_predictions.jsonl
```

No local base model loading was performed while preparing this plan.
