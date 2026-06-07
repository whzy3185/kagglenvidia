# Stage 7 Submission Confirmation

- slot: `reserve2`
- candidate: `nemotron-s7-norm-balanced-delta-svd-r32`
- source: `https://arxiv.org/abs/2106.09685, https://arxiv.org/abs/2212.04089, https://arxiv.org/abs/2306.01708, Hugging Face PEFT model merging`
- base_route: `keithtyser/nemotron-086-adapters-20260605`
- main_change: `per_module_delta_norm_balanced_qr_svd_rank32`
- expected_rank_effect: unknown; official evaluation required
- risk: high
- current_best_displayed_score: 0.86
- today_remaining_quota_at_generation: 1
- kernel_id: `muelsyse111/nemotron-s7-norm-balanced-delta-svd-r32`
- kernel_version: `1`
- output_file: `submission.zip`
- zip_sha256: `aec7776ecde061995a675868329a51bf76938a84bc3def2489b30ef8bd708f04`
- zip_size_bytes: `3554385847`
- zip_root_valid: `true`
- rank_lte_32: `true`
- structural_valid_not_official_valid: `true`
- recommendation: review candidate risk before submitting

## Submit Command (Not Executed)

```powershell
kaggle competitions submit nvidia-nemotron-model-reasoning-challenge -k muelsyse111/nemotron-s7-norm-balanced-delta-svd-r32 -f submission.zip -v 1 -m "20260607_reserve2_nemotron-s7-norm-balanced-delta-svd-r32_aec7776e"
```

**Explicit user confirmation is required before submission.**
