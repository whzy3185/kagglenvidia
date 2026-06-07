# Stage 7 Submission Confirmation

- slot: `reserve3`
- candidate: `nemotron-s7-dare-merge`
- source: `https://arxiv.org/abs/2311.03099, Hugging Face PEFT model merging`
- base_route: `keithtyser/nemotron-086-adapters-20260605`
- main_change: `dare_drop_and_rescale_merge`
- expected_rank_effect: unknown; official evaluation required
- risk: high
- current_best_displayed_score: 0.86
- today_remaining_quota_at_generation: 5
- kernel_id: `muelsyse111/nemotron-s7-dare-merge`
- kernel_version: `1`
- output_file: `submission.zip`
- zip_sha256: `4f37c3377e93633f851ae2a57446c8a22edbb787b12722a4460095e6a47e3a42`
- zip_size_bytes: `3554385847`
- zip_root_valid: `true`
- rank_lte_32: `true`
- structural_valid_not_official_valid: `true`
- recommendation: review candidate risk before submitting

## Submit Command (Not Executed)

```powershell
kaggle competitions submit nvidia-nemotron-model-reasoning-challenge -k muelsyse111/nemotron-s7-dare-merge -f submission.zip -v 1 -m "20260607_reserve3_nemotron-s7-dare-merge_4f37c337"
```

**Explicit user confirmation is required before submission.**
