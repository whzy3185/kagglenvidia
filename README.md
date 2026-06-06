# Nemotron Kaggle 冲分工程交接说明

本仓库用于 Kaggle 比赛 `nvidia-nemotron-model-reasoning-challenge` 的公开路线复现、adapter 打包、远端 notebook output 提交准备、提交计划和复盘记录。

当前原则很简单：不再大改 workflow，不再追标题里的 `0.86/0.87` 标签，只以 public rank 是否前移作为有效提升依据。

## 当前状态

更新时间：`2026-06-06`

- 队伍：`muelsyse111`
- 当前最佳显示分数：`0.86`
- 最新 public rank 基线：`393`
- 今日真实比赛提交次数：`0`
- 今日剩余额度：`5`
- 当前可执行候选：`hammad_agi_for_medal_087`
- 当前禁止事项：不自动提交、不复投 Huikang v27、不复投 Kien/Akihiko 低分路线、不提交同 hash 重复包

最新事实源：

```text
reports/SCORECARD.md
reports/DAILY_SUBMISSION_PLAN.md
reports/STAGE6_NOTEBOOK_SELECTION_AUDIT.md
reports/STAGE6_SUBMIT_GATE_hammad_agi_for_medal_087.md
reports/NEXT_STAGE_DECISION_TASK_CHAIN.md
```

## 接手第一步

在项目根目录执行：

```powershell
cd E:\Jitter\nemotron_086plus_repro
git status -sb
python scripts\04_query_submissions.py
python scripts\22_make_daily_submission_plan.py
```

然后先读：

```text
reports/DAILY_SUBMISSION_PLAN.md
reports/STAGE6_SUBMIT_GATE_hammad_agi_for_medal_087.md
reports/SCORECARD.md
```

只有 `DAILY_SUBMISSION_PLAN.md` 明确允许时，才考虑真实提交。

## 当前最重要候选

当前 slot1 是 `hammad_agi_for_medal_087`。

```yaml
candidate:
  source_kernel: hammadfarooq470/agi-for-medal-0-87
  local_repack_kernel: muelsyse111/nemotron-repack-hammad-087
  mechanism: "Huikang v20 adapter 上做 block_topk floor4 SVD 压缩，强制 fused rank 32"
  output_zip_confirmed: true
  rank_lte_32: true
  zip_root_files:
    - adapter_config.json
    - adapter_model.safetensors
  submission_zip_sha256: 945fe257b6222b471aff3d62f5c33edf1e64b0e8570691c9d9fd4ace6c5d75fa
```

Kaggle output 已确认：

```powershell
kaggle kernels files muelsyse111/nemotron-repack-hammad-087
```

应看到：

```text
submission.zip
```

推荐提交消息：

```text
slot1_hammad_agi_for_medal_087_945fe257b622
```

## 当前最佳两次历史提交

当前最高显示分数仍是 `0.86`，有多条并列。按后续调参价值排序，最重要的两条是：

| 优先级 | submission_id | 路线 | public score | 关键机制 |
| ---: | --- | --- | --- | --- |
| 1 | `53384098` | Mohamed replay-data finetune | `0.86` | Nemotron base + replay math，LoRA `r=32`，`steps=1000`，`lr=3.5e-4` |
| 2 | `53384096` | Taha custom repo finetune | `0.86` | Nemotron base + custom repo，LoRA `r=32`，`steps=1000`，`lr=2e-4` |

另外两条并列 `0.86` 可作为参考，但不应无改动复投：

| submission_id | 路线 | public score | 备注 |
| --- | --- | --- | --- |
| `53383735` | Rauffauzan fusion/rank compression | `0.86` | Huikang v20 相关 LoRA fusion + SVD rank compression |
| `53384030` | Mirza packaging route | `0.86` | 主要是公开 adapter packaging 路线 |

## 阶段情况

| 阶段 | 状态 | 说明 |
| --- | --- | --- |
| Stage 1 | 完成 | Kaggle CLI、资产审计、adapter validator、submission packer、dry-run 都已建立 |
| Stage 2 | 完成 | 公开 adapter 和 notebook output 路线已能审计、repack、远端提交准备 |
| Stage 3 | 部分完成 | proxy eval 框架存在，但 Nemotron 30B + Mamba/CUDA proxy 推理不稳定；不要把 proxy 当完成项 |
| Stage 4 | 部分完成 | daily plan 只生成计划，不自动提交；fusion 方向已有 Rauffauzan/Dedquoc/Hammad 审计 |
| Stage 5 | 完成 | Kaggle-side notebook workflow 可用，避免本地上传 3GB 级 `submission.zip` |
| Stage 6 | 进行中 | rank-first 候选选择已切到 Hammad，等待人工提交和官方结果 |

## 常用命令

刷新提交历史：

```powershell
python scripts\04_query_submissions.py
```

生成每日提交计划：

```powershell
python scripts\22_make_daily_submission_plan.py
```

检查 Hammad notebook output：

```powershell
kaggle kernels files muelsyse111/nemotron-repack-hammad-087
kaggle kernels logs muelsyse111/nemotron-repack-hammad-087
```

远端 output 提交命令模板：

```powershell
kaggle competitions submit nvidia-nemotron-model-reasoning-challenge -k muelsyse111/nemotron-repack-hammad-087 -f submission.zip -v <version> -m "slot1_hammad_agi_for_medal_087_945fe257b622"
```

注意：只有用户明确要求真实提交，并且 `DAILY_SUBMISSION_PLAN.md` 允许时，才执行提交命令。

## 安全边界

- 不提交 `kaggle.json`、token、secrets。
- 不提交 `.safetensors`、`.bin`、`.pt`、`.pth`、`submission.zip`。
- 不使用多账号，不绕过 Kaggle 每日额度。
- 不伪造 public score，不把 notebook 标题当真实分数。
- 不把 structural-valid 说成 official-valid。
- 不提交 rank `>32` 的 LoRA adapter。
- 不本地加载或训练 Nemotron 30B。
- 不为了用满 5 次额度而提交。
- slot2 到 slot5 在 slot1 没有 `COMPLETE + publicScore` 前保持 blocked。

## 下一步

```yaml
NEXT_ACTION:
  status: manual_submit_slot1_ready
  action: "submit Hammad slot1 from Kaggle Notebook Output after explicit user confirmation"
  reason: "Hammad output zip is confirmed, rank is 32, and the route is distinct from the prior 0.86 submissions."
```

提交后必须刷新：

```powershell
python scripts\04_query_submissions.py
python scripts\22_make_daily_submission_plan.py
```

结果判断只看 public rank 是否小于 `393`。显示分数仍是 `0.86` 但 rank 前移，也算有效提升。
