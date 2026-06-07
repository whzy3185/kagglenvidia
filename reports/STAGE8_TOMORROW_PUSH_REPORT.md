# Stage 8 Tomorrow Notebook Push Report

- updated_at: 2026-06-07T21:16:25
- expected_candidates: 5
- push_attempted: 5
- kernel_runs_started: 2
- notebooks_accepted_or_started: 5
- competition_submission_executed: false
- competition_quota_consumed: false

| kernel | mechanism | run started | GPU blocked | return code |
|---|---|---:|---:|---:|
| `muelsyse111/nemotron-s8-guarded-weak-replay-v1` | `guarded_weak_category_replay` | true | false | 0 |
| `muelsyse111/nemotron-s8-answer-tail-512-v1` | `answer_tail_512_loss_focus` | true | false | 0 |
| `muelsyse111/nemotron-s8-attn-mamba-no-lmhead-v1` | `attention_mamba_without_lm_head` | false | true | 0 |
| `muelsyse111/nemotron-s8-mlp-mamba-no-lmhead-v1` | `mlp_mamba_without_attention_lm_head` | false | true | 0 |
| `muelsyse111/nemotron-s8-rank-stable-alpha64-v1` | `rank32_high_alpha_capacity_test` | false | true | 0 |

## Command Output

### muelsyse111/nemotron-s8-guarded-weak-replay-v1

```text
Kernel version 1 successfully pushed.  Please check progress at https://www.kaggle.com/code/muelsyse111/nemotron-s8-guarded-weak-replay-v1
(no stderr)
```

### muelsyse111/nemotron-s8-answer-tail-512-v1

```text
Kernel version 1 successfully pushed.  Please check progress at https://www.kaggle.com/code/muelsyse111/nemotron-s8-answer-tail-512-v1
(no stderr)
```

### muelsyse111/nemotron-s8-attn-mamba-no-lmhead-v1

```text
Kernel push error: Maximum batch GPU session count of 2 reached.
(no stderr)
```

### muelsyse111/nemotron-s8-mlp-mamba-no-lmhead-v1

```text
Kernel push error: Maximum batch GPU session count of 2 reached.
(no stderr)
```

### muelsyse111/nemotron-s8-rank-stable-alpha64-v1

```text
Kernel push error: Maximum batch GPU session count of 2 reached.
(no stderr)
```

## Safety

This script only calls `kaggle kernels push`. It never calls `kaggle competitions submit` and does not consume competition submission quota.
