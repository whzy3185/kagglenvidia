# Stage 7 Submission Confirmation

- slot: `slot3`
- candidate: `nemotron-s7-modulewise-delta-svd-r32`
- source: `https://arxiv.org/abs/2106.09685, https://arxiv.org/abs/2306.01708, 703240, Hugging Face PEFT model merging`
- base_route: `keithtyser/nemotron-086-adapters-20260605`
- main_change: `module_family_weighted_delta_qr_svd_rank32`
- expected_rank_effect: unknown; official evaluation required
- risk: high
- current_best_displayed_score: 0.86
- today_remaining_quota_at_generation: 1
- kernel_id: `muelsyse111/nemotron-s7-modulewise-delta-svd-r32`
- kernel_version: `1`
- output_file: `submission.zip`
- zip_sha256: `00d6bd3faafb66e5430c6aa08ee130379a982d9f39f42b75dddfac4d2b1fc165`
- zip_size_bytes: `3554385847`
- zip_root_valid: `true`
- rank_lte_32: `true`
- structural_valid_not_official_valid: `true`
- recommendation: review candidate risk before submitting

## Submit Command (Not Executed)

```powershell
kaggle competitions submit nvidia-nemotron-model-reasoning-challenge -k muelsyse111/nemotron-s7-modulewise-delta-svd-r32 -f submission.zip -v 1 -m "20260607_slot3_nemotron-s7-modulewise-delta-svd-r32_00d6bd3f"
```

**Explicit user confirmation is required before submission.**
