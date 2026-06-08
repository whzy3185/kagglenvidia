# Stage 8 Retry Blocked Notebooks

- generated_at: 2026-06-08T13:47:05
- reason: original remote slugs returned Kaggle `Notebook not found` after GPU-blocked push attempts
- competition_submission_executed: false

| retry candidate | source candidate | kernel | command |
|---|---|---|---|
| `nemotron-s8-attn-mamba-no-lmhead-run2` | `nemotron-s8-attn-mamba-no-lmhead-v1` | `muelsyse111/nemotron-s8-attn-mamba-no-lmhead-run2` | `kaggle kernels push -p "kaggle_kernels\nemotron_s8_attn_mamba_no_lmhead_run2"` |
| `nemotron-s8-mlp-mamba-no-lmhead-run2` | `nemotron-s8-mlp-mamba-no-lmhead-v1` | `muelsyse111/nemotron-s8-mlp-mamba-no-lmhead-run2` | `kaggle kernels push -p "kaggle_kernels\nemotron_s8_mlp_mamba_no_lmhead_run2"` |
| `nemotron-s8-rank-stable-alpha64-run2` | `nemotron-s8-rank-stable-alpha64-v1` | `muelsyse111/nemotron-s8-rank-stable-alpha64-run2` | `kaggle kernels push -p "kaggle_kernels\nemotron_s8_rank_stable_alpha64_run2"` |

These retry notebooks preserve the same code path and only change the remote Kaggle slug/code filename.
