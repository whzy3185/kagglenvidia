# Daily Submission Plan

- timestamp: 2026-06-08T14:12:27
- today_submission_count: 5
- today_remaining_quota: 0
- quota_effective_today_submission_count: 5
- quota_effective_today_remaining: 0
- current_best_public_score: `{"public_score": 0.86, "submission_id": "53384098", "status": "SubmissionStatus.COMPLETE", "description": "20260605_slot6_mohamed_replay_data_086_v4_remote_output", "submitted_at": "2026-06-05 07:00:55.467000"}`
- stage7_output_ready_candidates: 5
- no_automatic_competition_submission: true
- submission_quota_consumed_by_this_script: false

## Stage 7 Candidate Plan

| slot | candidate | kernel | hash | state | required action |
|---|---|---|---|---|---|
| slot1 | `nemotron-s7-protected-rehearsal` | `muelsyse111/nemotron-s7-protected-rehearsal-v2` | `641c57f33c72` | `official_evaluation_complete` | review public score `0.85` |
| slot2 | `nemotron-s7-delta-space-svd-r32` | `muelsyse111/nemotron-s7-delta-space-svd-r32` | `b31b987c290f` | `official_evaluation_complete` | review public score `0.85` |
| slot3 | `nemotron-s7-modulewise-delta-svd-r32` | `muelsyse111/nemotron-s7-modulewise-delta-svd-r32` | `00d6bd3faafb` | `official_evaluation_complete` | review public score `0.85` |
| slot4 | `nemotron-s7-muon-full-v5-audited` | `muelsyse111/nemotron-s7-muon-v5-audit` | `2d42d0adb258` | `official_evaluation_complete` | review public score `0.84` |
| slot5 | `nemotron-s7-mamba-inproj-specialist-v2` | `muelsyse111/nemotron-s7-mamba-inproj-specialist-v2` | `852e80252228` | `official_evaluation_complete` | review public score `0.81` |

## Candidate State

- 5 primary Stage 7 slot cards are structurally ready.
- Reserve candidates and blocked training routes are tracked in `reports/STAGE7_REFERENCE_SUBMISSION_LIST.md`.
- A ready package is not an official score claim; ranking requires competition evaluation.

## Today's Recommended Operation

```yaml
NEXT_ACTION:
  status: all_planned_slots_evaluated
  action: "review all Stage 7 official results"
  reason: "all planned Stage 7 candidates already have official submission records."
```

## Safety

- This script does not call `kaggle competitions submit`.
- It does not upload a package or consume quota.
- Structural validity is not an official score claim.
