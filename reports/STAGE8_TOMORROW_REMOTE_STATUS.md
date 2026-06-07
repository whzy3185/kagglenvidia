# Stage 8 Tomorrow Remote Status

- updated_at: 2026-06-07T21:22:29
- status_source: Kaggle kernel files and logs
- competition_submission_executed: false

| kernel | mechanism | state | step | output | SHA256 | size bytes |
|---|---|---|---|---:|---|---:|
| `muelsyse111/nemotron-s8-guarded-weak-replay-v1` | `guarded_weak_category_replay` | `queued_no_logs` | `n/a` | false | `n/a` | n/a |
| `muelsyse111/nemotron-s8-answer-tail-512-v1` | `answer_tail_512_loss_focus` | `queued_no_logs` | `n/a` | false | `n/a` | n/a |
| `muelsyse111/nemotron-s8-attn-mamba-no-lmhead-v1` | `attention_mamba_without_lm_head` | `created_not_started_or_no_output` | `n/a` | false | `n/a` | n/a |
| `muelsyse111/nemotron-s8-mlp-mamba-no-lmhead-v1` | `mlp_mamba_without_attention_lm_head` | `created_not_started_or_no_output` | `n/a` | false | `n/a` | n/a |
| `muelsyse111/nemotron-s8-rank-stable-alpha64-v1` | `rank32_high_alpha_capacity_test` | `created_not_started_or_no_output` | `n/a` | false | `n/a` | n/a |

## Next Actions

- `output_ready`: can be converted into a tomorrow confirmation card after quota resets.
- `running_or_finalizing`: keep polling; do not submit.
- `created_not_started_or_no_output`: push again later if GPU session slots free.
- `failed`: inspect failure before rerun; do not blindly submit.
