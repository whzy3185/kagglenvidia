# Nemotron 0.86+ Kaggle 冲分工程

本仓库用于 Kaggle 比赛
[`nvidia-nemotron-model-reasoning-challenge`](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge)
的公开方案复现、LoRA 训练、adapter 合并、结构验证、Kaggle Notebook
运行和提交复盘。

当前阶段为 **Stage 7：Aggressive Rank-Push Exploration**。目标不是重复获得
显示值 `0.86`，而是通过机制不同的新 adapter 推动 public rank 前移。

## 当前状态

更新时间：`2026-06-07`

```yaml
competition: nvidia-nemotron-model-reasoning-challenge
kaggle_user: muelsyse111
current_best_displayed_score: 0.86
target_public_rank: "<100"
today_submission_count: 0
today_remaining_quota: 5
output_ready_stage7_packages: 9
primary_submission_candidates: 5
competition_submission_executed_today: false
```

public rank 会随其他队伍提交变化，README 不固化可能过期的排名数字。实时排名应在
Kaggle leaderboard 页面确认；本地提交和分数以
[`reports/SCORECARD.md`](reports/SCORECARD.md) 为准。

## 当前最佳历史结果

目前最高显示分数为 `0.86`，其中最重要的两条训练路线是：

| submission id | 路线 | public score | 主要配置 |
|---|---|---:|---|
| `53384098` | Mohamed replay-data finetune | `0.86` | replay math、LoRA rank 32、1000 steps、LR `3.5e-4` |
| `53384096` | Taha custom-repo finetune | `0.86` | custom repo、LoRA rank 32、1000 steps、LR `2e-4` |

另外两条 `0.86` 参考路线：

| submission id | 路线 | public score | 说明 |
|---|---|---:|---|
| `53383735` | Rauffauzan fusion/SVD | `0.86` | 公开 adapter fusion 与 rank compression |
| `53384030` | Mirza adapter packaging | `0.86` | 公开 adapter 打包路线 |

已确认不应原样复投的低分路线：

| 路线 | 我方实测分数 |
|---|---:|
| Hammad `0.87` 标题路线 | `0.85` |
| Keith task-arithmetic 尝试 | `0.85` |
| Dedquoc SVD fusion | `0.78` |
| Kuang `0.87` 标题路线 | `0.63` |
| Akihiko LoRA | `0.50` |

结论：notebook 标题或作者 claim 不能当作真实成绩，只有我方 Kaggle submission
返回的 public score 才能写入成绩记录。

## Stage 7 已就绪候选

以下 9 个包均已在 Kaggle 云端生成，并通过：

- zip 根目录只包含 `adapter_config.json` 和 `adapter_model.safetensors`
- LoRA rank 不超过 32
- adapter 文件大小检查
- SHA256 记录
- 成功标记检查

这些结果只代表 **structural-valid**，不代表 **official-valid**，也不代表已经获得高分。

### 正式提交顺序

| slot | Kaggle kernel | 机制 | SHA256 前缀 | 风险 |
|---:|---|---|---|---|
| 1 | `muelsyse111/nemotron-s7-protected-rehearsal-v2` | protected category loss reweighting | `641c57f33c72` | 中高 |
| 2 | `muelsyse111/nemotron-s7-delta-space-svd-r32` | effective LoRA delta QR/SVD rank-32 recompression | `b31b987c290f` | 中高 |
| 3 | `muelsyse111/nemotron-s7-modulewise-delta-svd-r32` | module-family weighted delta SVD | `00d6bd3faafb` | 高 |
| 4 | `muelsyse111/nemotron-s7-muon-v5-audit` Version 2 | full-epoch Muon optimizer training | `2d42d0adb258` | 高 |
| 5 | `muelsyse111/nemotron-s7-norm-balanced-delta-svd-r32` | per-module norm-balanced delta SVD | `aec7776ecde0` | 高 |

详细风险、来源和完整哈希见：

```text
reports/STAGE7_REFERENCE_SUBMISSION_LIST.md
reports/DAILY_SUBMISSION_PLAN.md
reports/STAGE7_SUBMIT_CONFIRM_20260607_slot*.md
```

### Reserve 候选

| reserve | Kaggle kernel | 机制 | SHA256 前缀 |
|---:|---|---|---|
| 1 | `muelsyse111/nemotron-s7-seed-stability-replay` | deterministic seed/reproducible shuffle | `f5dde9e053d7` |
| 2 | `muelsyse111/nemotron-s7-ties-sign-merge` | TIES trim/elect-sign/merge | `b03e975ea48d` |
| 3 | `muelsyse111/nemotron-s7-dare-merge` | DARE drop-and-rescale merge | `4f37c3377e93` |
| 4 | `muelsyse111/nemotron-s7-layerwise-adapter-soup` | module-aware weighted soup | `4480e232def3` |

## Muon v5 结果

Muon v5 使用 Kaggle RTX Pro 6000 完成了完整训练：

```yaml
records: 7830
epochs: 1
sequence_length: 8192
lora_rank: 32
micro_batch_size: 1
gradient_accumulation_steps: 16
effective_batch_size: 16
training_time_minutes: 434.5
```

独立 CPU audit notebook 验证结果：

```yaml
audit_kernel: muelsyse111/nemotron-s7-muon-v5-audit
audit_version: 2
zip_size_bytes: 3833093217
zip_sha256: 2d42d0adb258956398e4a501f4629aa4a812da2612e506cf1f0449b6143170f5
lora_rank: 32
safetensors_tensor_count: 12011
zip_root_valid: true
```

Version 2 直接复制已验证源 zip，避免 Version 1 使用 `ZIP_STORED` 后额外增加约
426 MB。

## 正在运行或排队

两个完整训练量的差异化 notebook 已成功 push，当前等待 Kaggle GPU 调度：

| kernel | 机制 | 当前状态 |
|---|---|---|
| `muelsyse111/nemotron-s7-weak-protected-curriculum-v2` | weak-category 与 protected-category 交错课程 | `queued_no_logs` |
| `muelsyse111/nemotron-s7-mamba-inproj-specialist-v2` | 只适配 Mamba `in_proj` 等选择性模块 | `queued_no_logs` |

两者均保持 rank 32、最大长度 8192 和完整训练量，没有通过缩减数据或训练步数来加速。

状态以 [`reports/STAGE7_ACTIVE_RUNS.md`](reports/STAGE7_ACTIVE_RUNS.md) 为准。
Kaggle 的 `kernels status` 接口经常返回 HTTP 500，因此本项目主要结合
`kaggle kernels files` 与 `kaggle kernels logs` 判断状态。

## 阶段完成情况

| 阶段 | 状态 | 说明 |
|---|---|---|
| Stage 1 | 完成 | Kaggle CLI、资产审计、adapter validator、submission packer、dry-run |
| Stage 2 | 完成 | 公开 adapter 获取、结构验证、云端 repack 和提交格式闭环 |
| Stage 3 | 部分完成 | proxy eval 框架存在，但 Nemotron 30B Mamba/CUDA 推理链不稳定，不能声称完整 proxy eval 已完成 |
| Stage 4 | 部分完成 | daily plan、score gate、fusion 研究已建立；比赛提交仍需人工确认 |
| Stage 5 | 完成 | Kaggle-side notebook workflow 可用，避免本地上传大型 zip |
| Stage 6 | 完成复盘 | 多条公开 output 已经官方验证，标题 claim 与真实分数偏差已记录 |
| Stage 7 | 进行中 | 9 个结构有效候选已就绪，2 个完整训练任务排队 |

## 接手顺序

任何新 Agent 或人工接手时，先运行：

```powershell
cd E:\Jitter\nemotron_086plus_repro
git status -sb
python scripts\04_query_submissions.py
python scripts\22_make_daily_submission_plan.py
python scripts\34_check_stage7_active_runs.py
```

然后按顺序阅读：

```text
reports/DAILY_SUBMISSION_PLAN.md
reports/STAGE7_REFERENCE_SUBMISSION_LIST.md
reports/STAGE7_ACTIVE_RUNS.md
reports/SCORECARD.md
reports/NEXT_STAGE_DECISION_TASK_CHAIN.md
```

当前工作区包含大量尚未提交到 Git 的 Stage 7 文件。不要使用
`git reset --hard`、`git clean -fd` 或其他会删除现有实验的命令。

## 提交规则

仓库脚本默认只准备 notebook、候选和确认卡，不自动执行比赛提交。

真实提交前必须同时满足：

1. `reports/DAILY_SUBMISSION_PLAN.md` 显示额度可用。
2. 对应 `STAGE7_SUBMIT_CONFIRM_<date>_<slot>_<candidate>.md` 存在。
3. kernel output 中存在 `submission.zip`。
4. zip 根目录结构、rank 和 SHA256 已确认。
5. 候选不是重复 hash，也不是已知低分原包复投。
6. 用户明确给出类似 `提交 slot1` 的指令。

提交命令只应从确认卡复制，不应手写猜测 kernel version：

```powershell
kaggle competitions submit nvidia-nemotron-model-reasoning-challenge `
  -k <kernel_id> `
  -f submission.zip `
  -v <version> `
  -m "<message>"
```

提交后刷新：

```powershell
python scripts\04_query_submissions.py
python scripts\22_make_daily_submission_plan.py
```

## 常用命令

刷新官方提交历史：

```powershell
python scripts\04_query_submissions.py
```

生成每日候选计划：

```powershell
python scripts\22_make_daily_submission_plan.py
```

检查 Stage 7 云端任务：

```powershell
python scripts\34_check_stage7_active_runs.py
```

查看单个 notebook 日志和输出：

```powershell
kaggle kernels logs <owner/kernel-slug>
kaggle kernels files <owner/kernel-slug> -v --page-size 100
```

重新生成候选排序与确认卡：

```powershell
python scripts\31_build_stage7_reference_submission_list.py
```

## 研究依据

### 比赛与代码

- [Tong Huikang Nemotron repository](https://github.com/tonghuikang/nemotron)
- [Muon optimizer implementation](https://github.com/KellerJordan/Muon)
- [Public Muon competition notebook](https://www.kaggle.com/code/pkuszboi/0-85-lb-training-with-muon)
- [Rauffauzan LoRA fusion/rank compression](https://www.kaggle.com/code/rauffauzanrambe/lora-adapter-fusion-and-rank-compression-pipeline)
- [Hugging Face PEFT model merging](https://huggingface.co/docs/peft/developer_guides/model_merging)
- [MergeKit](https://github.com/arcee-ai/mergekit)
- [LoRAHub](https://github.com/sail-sg/lorahub)

### 论文

- [LoRA](https://arxiv.org/abs/2106.09685)
- [QLoRA](https://arxiv.org/abs/2305.14314)
- [TIES-Merging](https://arxiv.org/abs/2306.01708)
- [DARE](https://arxiv.org/abs/2311.03099)
- [Task Arithmetic](https://arxiv.org/abs/2212.04089)
- [Model Soups](https://arxiv.org/abs/2203.05482)
- [Continual Learning with Experience Replay](https://arxiv.org/abs/1909.08383)

### 数据

- [NVIDIA OpenMathReasoning](https://huggingface.co/datasets/nvidia/OpenMathReasoning)
- [OpenR1-Math-220k](https://huggingface.co/datasets/open-r1/OpenR1-Math-220k)
- [NuminaMath-CoT](https://huggingface.co/datasets/AI-MO/NuminaMath-CoT)

完整来源记录见：

```text
reports/STAGE7_MASTER_DISCUSSION_RESEARCH.md
reports/STAGE7_OPEN_SOURCE_REPO_MINING.md
reports/PUBLIC_PRIVATE_OVERFIT_SOURCE_REVIEW.md
configs/stage7_master_research_targets.yaml
configs/stage7_repo_sources.yaml
```

## 安全边界

- 不提交 `kaggle.json`、token、密码或 secrets。
- 不提交 `.safetensors`、`.bin`、`.pt`、`.pth` 或 `submission.zip` 到 Git。
- 不使用多账号，不绕过每日提交额度。
- 不伪造 public score、rank、adapter 或实验结果。
- 不把 structural-valid 描述成 official-valid。
- 不提交 rank 大于 32 的 LoRA adapter。
- 不在本地加载或训练 Nemotron 30B。
- 不使用 leaderboard 进行隐藏标签推断或无限超参搜索。
- 不自动执行 `kaggle competitions submit`。
- 公开方案、代码、数据和论文必须保留来源记录。

## 下一步

```yaml
NEXT_ACTION:
  status: monitor_and_evaluate
  action: "monitor the two queued Stage 7 GPU notebooks and review the slot1 confirmation card before any official submission"
  reason: "five structurally valid primary candidates are ready, while two mechanism-distinct full-training experiments are waiting for Kaggle GPU execution."
```
