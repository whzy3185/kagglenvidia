# Submission Fallback Plan

The first real submit attempt used the validated Stage 2 adapter zip:

```text
artifacts/stage2/tong_full_repro/submission/submission.zip
```

Result:

- submit_attempted: true
- submitted: false
- failure_reason: kaggle_submit_timeout_no_submission_recorded
- today_submission_count_after_attempt: 0
- today_remaining_quota_after_attempt: 5
- score_gate_allowed: true
- adapter_structural_valid: true
- license_ok: true
- official_format_confirmed: false
- official_score_verified_locally: false

The local upload did not complete within 30 minutes. Residual Kaggle submit processes were stopped, and a follow-up Kaggle submission-history query still returned `No submissions found`.

Recommended next action is a single longer controlled retry with the updated submit script, which now has an internal timeout and process-tree cleanup:

```powershell
python scripts/11_submit_candidate.py --zip artifacts/stage2/tong_full_repro/submission/submission.zip --candidate-manifest artifacts/stage2/tong_full_repro/stage2_manifest.json --message "20260603 slot_1 tong_adapter_repack db56ce42 stage2 structural_public_adapter_retry" --timeout-seconds 7200 --yes
```

Do not repeatedly retry the same large upload if this second controlled attempt also times out. In that case, switch to a Kaggle-hosted packaging/submission path instead of spending more local upload time.

NEXT_ACTION:
  status: stay_submission_attempt
  action: "run one longer controlled submit retry with scripts/11_submit_candidate.py --timeout-seconds 7200"
  reason: "The candidate passed static gates, but the first local 1.41GB upload timed out before Kaggle recorded a submission."
