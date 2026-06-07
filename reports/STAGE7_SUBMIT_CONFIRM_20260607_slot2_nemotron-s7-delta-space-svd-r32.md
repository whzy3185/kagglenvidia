# Stage 7 Submission Confirmation

- slot: `slot2`
- candidate: `nemotron-s7-delta-space-svd-r32`
- source: `https://arxiv.org/abs/2106.09685, https://arxiv.org/abs/2306.01708, Hugging Face PEFT model merging, https://www.kaggle.com/code/rauffauzanrambe/lora-adapter-fusion-and-rank-compression-pipeline`
- base_route: `keithtyser/nemotron-086-adapters-20260605`
- main_change: `effective_delta_qr_svd_rank32_recompression`
- expected_rank_effect: unknown; official evaluation required
- risk: high
- current_best_displayed_score: 0.86
- today_remaining_quota_at_generation: 1
- kernel_id: `muelsyse111/nemotron-s7-delta-space-svd-r32`
- kernel_version: `1`
- output_file: `submission.zip`
- zip_sha256: `b31b987c290ff52fa688c00738b75d73b486bc41c477790eb908292e20fb50f7`
- zip_size_bytes: `3554385847`
- zip_root_valid: `true`
- rank_lte_32: `true`
- structural_valid_not_official_valid: `true`
- recommendation: review candidate risk before submitting

## Submit Command (Not Executed)

```powershell
kaggle competitions submit nvidia-nemotron-model-reasoning-challenge -k muelsyse111/nemotron-s7-delta-space-svd-r32 -f submission.zip -v 1 -m "20260607_slot2_nemotron-s7-delta-space-svd-r32_b31b987c"
```

**Explicit user confirmation is required before submission.**
