# Remote 0.86 Submission Sweep 2026-06-05

- competition: `nvidia-nemotron-model-reasoning-challenge`
- strategy: `remote_kernel_output_submit`
- local_large_zip_upload: false
- base_model_downloaded_locally: false
- submitted_count_today: `5`
- resolved_best_public_score: `0.86`
- result_summary: `four remote kernel-output candidates reached 0.86; one reached 0.85`

## Submitted Candidates

| submission_id | route | kernel | version | message | status | public_score |
| --- | --- | --- | --- | --- | --- | --- |
| 53383735 | Rauffauzan fusion/rank compression | `muelsyse111/nemotron-repack-rauffauzan-fusion` | 1 | `20260605_slot3_rauffauzan_fusion_output_af996be0` | COMPLETE | 0.86 |
| 53384030 | Mirza best 0.86 notebook | `mirzayasirabdullah07/best-nvidia-nemotron-notebook-0-86` | 16 | `20260605_slot4_mirzayasir_best_086_v16_remote_output` | COMPLETE | 0.86 |
| 53384059 | Debatreya 0.86 under 5min | `debatreyabiswas/nemotroncomp-best-0-86-solution-nvidia-under-5min` | 1 | `20260605_slot5_debatreyabiswas_086_v1_remote_output` | COMPLETE | 0.85 |
| 53384096 | Taha custom repo 0.86 | `tahaalam2009/end-to-end-finetuning-for-lb-0-86-custom-repo` | 6 | `20260605_slot7_taha_custom_repo_086_v6_remote_output` | COMPLETE | 0.86 |
| 53384098 | Mohamed replay data 0.86 | `mohamedamr992/nemotron-replay-data-0-86` | 4 | `20260605_slot6_mohamed_replay_data_086_v4_remote_output` | COMPLETE | 0.86 |

## Notes

- Remote kernel-output submission was used via `kaggle competitions submit -k <kernel> -f submission.zip -v <version>`.
- This avoids downloading and re-uploading 3GB+ output files locally.
- Failed local/format attempts were not useful for score discovery; remote kernel-output submission was the effective route.
- Do not submit additional candidates today because the five useful daily slots are already used.

```yaml
NEXT_ACTION:
  status: stop_today
  action: "audit 0.87 and 0.89 public routes before the next submission window"
  reason: "The current route reached the 0.86 plateau, while leaderboard separation starts at 0.87."
```
