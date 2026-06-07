# Stage 7 Active Runs

- updated_at: 2026-06-07T21:02:32
- status_source: Kaggle kernel files and logs
- competition submission executed: false

| kernel | resource | mechanism | state | step | CUDA | output | SHA256 |
|---|---|---|---|---|---|---:|---|
| `muelsyse111/nemotron-s7-protected-rehearsal-v2` | RTX Pro 6000 | `protected_category_loss_reweighting` | `output_ready` | `254/254` | `n/a` | true | `641c57f33c72` |
| `muelsyse111/nemotron-s7-muon-full-training-v5` | RTX Pro 6000 | `muon_optimizer_microbatch1_effective_batch16` | `output_ready` | `n/a` | `True` | true | `n/a` |
| `muelsyse111/nemotron-s7-muon-v5-audit` | CPU | `muon_v5_structural_audit_and_repack` | `output_ready` | `n/a` | `n/a` | true | `2d42d0adb258` |
| `muelsyse111/nemotron-s7-delta-space-svd-r32` | CPU | `effective_delta_qr_svd_rank32_recompression` | `output_ready` | `n/a` | `n/a` | true | `b31b987c290f` |
| `muelsyse111/nemotron-s7-modulewise-delta-svd-r32` | CPU | `module_family_weighted_delta_qr_svd_rank32` | `output_ready` | `n/a` | `n/a` | true | `00d6bd3faafb` |
| `muelsyse111/nemotron-s7-norm-balanced-delta-svd-r32` | CPU | `per_module_delta_norm_balanced_qr_svd_rank32` | `output_ready` | `n/a` | `n/a` | true | `aec7776ecde0` |
| `muelsyse111/nemotron-s7-weak-protected-curriculum-v2` | RTX Pro 6000 | `weak_category_plus_protected_interleaving` | `output_ready` | `254/254` | `n/a` | true | `631a2bfb4dc5` |
| `muelsyse111/nemotron-s7-mamba-inproj-specialist-v2` | RTX Pro 6000 | `selective_mamba_in_proj_adaptation` | `output_ready` | `254/254` | `n/a` | true | `852e80252228` |

## Interpretation

- `queued_no_logs`: Kaggle accepted the version but has not started notebook execution.
- `running_or_finalizing`: logs exist and no terminal success/error marker is present.
- `output_ready`: `submission.zip` is visible and the notebook printed the success marker.
- `failed`: logs contain a terminal Python or Papermill exception.
