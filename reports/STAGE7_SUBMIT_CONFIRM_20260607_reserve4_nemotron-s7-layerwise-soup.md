# Stage 7 Submission Confirmation

- slot: `reserve4`
- candidate: `nemotron-s7-layerwise-soup`
- source: `model soups, 704473, Hugging Face PEFT model merging`
- base_route: `keithtyser/nemotron-086-adapters-20260605`
- main_change: `module_aware_layerwise_weighted_soup`
- expected_rank_effect: unknown; official evaluation required
- risk: high
- current_best_displayed_score: 0.86
- today_remaining_quota_at_generation: 5
- kernel_id: `muelsyse111/nemotron-s7-layerwise-adapter-soup`
- kernel_version: `1`
- output_file: `submission.zip`
- zip_sha256: `4480e232def317221bf967b490aa196309aa506735edc7ce5651019929ba4084`
- zip_size_bytes: `3554385847`
- zip_root_valid: `true`
- rank_lte_32: `true`
- structural_valid_not_official_valid: `true`
- recommendation: review candidate risk before submitting

## Submit Command (Not Executed)

```powershell
kaggle competitions submit nvidia-nemotron-model-reasoning-challenge -k muelsyse111/nemotron-s7-layerwise-adapter-soup -f submission.zip -v 1 -m "20260607_reserve4_nemotron-s7-layerwise-soup_4480e232"
```

**Explicit user confirmation is required before submission.**
