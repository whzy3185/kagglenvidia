# Nemotron Kaggle 冲分工程交接说明

本仓库用于 Kaggle 比赛 `nvidia-nemotron-model-reasoning-challenge` 的公开路线复现、adapter 打包、远端 notebook output 提交准备、提交计划和复盘记录。

当前原则很简单：不再大改 workflow，不再追标题里的 `0.86/0.87` 标签，只以 public rank 是否前移作为有效提升依据。

## 当前状态

更新时间：`2026-06-06`

- 队伍：`muelsyse111`
- 当前最佳显示分数：`0.86`
- 最新 public rank 基线：`393`
- 今日真实比赛提交次数：`3`
- 今日剩余额度：`2`
- 当前推荐候选：`keithtyser_anchor_ties_svd_rank32`
- 当前禁止事项：不自动提交、不复投 Huikang v27、不复投 Kien/Akihiko 低分路线、不提交同 hash 重复包、不再复投标题 claim 型 `0.87` output

最新事实源：

```text
reports/SCORECARD.md
reports/DAILY_SUBMISSION_PLAN.md
reports/STAGE7_OPEN_SOURCE_REPO_MINING.md
reports/STAGE7_CANDIDATE_POOL.md
configs/stage7_candidate_pool.yaml
configs/stage7_repo_sources.yaml
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
reports/STAGE7_OPEN_SOURCE_REPO_MINING.md
reports/STAGE7_CANDIDATE_POOL.md
reports/SCORECARD.md
```

只有 `DAILY_SUBMISSION_PLAN.md` 明确允许时，才考虑真实提交。

## 当前最重要候选

当前 Stage 7 推荐先做 `keithtyser_anchor_ties_svd_rank32`。

```yaml
candidate:
  source_model: keithtyser/nemotron-086-adapters-20260605
  source_url: https://www.kaggle.com/models/keithtyser/nemotron-086-adapters-20260605
  mechanism: "多个 0.86-class rank32 adapter anchors 上做 TIES/DARE/weighted SVD merge，再强制 rank<=32"
  reason: "上一轮公开 output repack 全部低于当前 best；下一轮必须生成新 hash 和真实行为变化"
  required_first_step: "先生成 Kaggle-side anchor inventory notebook，确认真实文件、rank、SHA256"
  submission_allowed_now: false
```

不要直接提交该候选。必须先生成 inventory/merge notebook，确认 `adapter_config.json`、`adapter_model.safetensors`、`rank<=32`、zip 根目录结构和新 SHA256，再生成 `STAGE7_SUBMIT_CONFIRM_*` 确认卡，由用户明确确认后才可提交。

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

## Stage 7 已读来源和链接

本阶段不再相信 notebook 标题里的 `0.87` claim，而是把来源分成“可生成新 adapter 行为”的资产、代码、数据和论文方法。完整细节见：

```text
reports/STAGE7_OPEN_SOURCE_REPO_MINING.md
reports/STAGE7_CANDIDATE_POOL.md
configs/stage7_repo_sources.yaml
configs/stage7_ideas.yaml
configs/stage7_candidate_pool.yaml
```

### Kaggle 比赛相关来源

| 优先级 | 来源 | 类型 | 用途 |
| --- | --- | --- | --- |
| P0 | [keithtyser/nemotron-086-adapters-20260605](https://www.kaggle.com/models/keithtyser/nemotron-086-adapters-20260605) | model adapter anchors | 六个 0.86-class rank32 adapter anchors，下一步做 inventory + fusion |
| P1 | [mohamedamr992/nemotron-replay-data-0-86](https://www.kaggle.com/code/mohamedamr992/nemotron-replay-data-0-86) | training route | 我方已提交原 output 得到 `0.86`，适合做 LR 单变量变体 |
| P1 | [tahaalam2009/end-to-end-finetuning-for-lb-0-86-custom-repo](https://www.kaggle.com/code/tahaalam2009/end-to-end-finetuning-for-lb-0-86-custom-repo) | training route | 我方已提交原 output 得到 `0.86`，适合做 replay/data mix 单变量变体 |
| P1 | [rauffauzanrambe/lora-adapter-fusion-and-rank-compression-pipeline](https://www.kaggle.com/code/rauffauzanrambe/lora-adapter-fusion-and-rank-compression-pipeline) | fusion/SVD code | 旧 output 已是 0.86 参考，不复投；可换 anchors 和 merge weight |
| BLOCKED | [hammadfarooq470/agi-for-medal-0-87](https://www.kaggle.com/code/hammadfarooq470/agi-for-medal-0-87) | public output | 我方提交后官方分 `0.85`，不再复投 |
| BLOCKED | [dedquoc/nvidia-nmrc-low-rank-svd-lora-adapter-fusion](https://www.kaggle.com/code/dedquoc/nvidia-nmrc-low-rank-svd-lora-adapter-fusion) | public output / fusion code | output 官方分 `0.78`，只保留代码参考 |
| BLOCKED | [kuangyicheng/nemotron-087-training](https://www.kaggle.com/code/kuangyicheng/nemotron-087-training) | public output | output 官方分 `0.63`，不再复投 |
| BLOCKED | [cocoaai/nvidia-nemotron-huikang-0-87-svd-submit](https://www.kaggle.com/code/cocoaai/nvidia-nemotron-huikang-0-87-svd-submit) | public output | 与 Hammad output 同 SHA256，重复 hash |

### 开源代码仓库和工具

| 优先级 | 链接 | 方法 | 用途 |
| --- | --- | --- | --- |
| P1 | [Hugging Face PEFT model merging](https://huggingface.co/docs/peft/developer_guides/model_merging) | `add_weighted_adapter`、linear、SVD、TIES、DARE | LoRA adapter merge 方法参考；实现时优先做 adapter tensor merge，避免本地加载 base model |
| P2 | [tonghuikang/nemotron](https://github.com/tonghuikang/nemotron) | `train_sft.py`、corpus、augmentation、loss、LR schedule | 官方公开训练路线参考；适合 Kaggle GPU 上做 loss mask/LR 单变量变体 |
| P3 | [arcee-ai/mergekit](https://github.com/arcee-ai/mergekit) | task arithmetic、TIES、DARE、merge configs | 只做算法参考，不本地合并 30B full model |
| P3 | [sail-sg/lorahub](https://github.com/sail-sg/lorahub) | dynamic LoRA composition / weight search | 需要 proxy objective；禁止用 leaderboard 当权重搜索器 |

### Hugging Face 数据来源

| 优先级 | 链接 | 用途 | 注意 |
| --- | --- | --- | --- |
| P2 | [nvidia/OpenMathReasoning](https://huggingface.co/datasets/nvidia/OpenMathReasoning) | 小规模 hard numeric/symbolic reasoning 数据切片 | 数据很大，只能过滤小样本；注意格式和去污染 |
| P2 | [open-r1/OpenR1-Math-220k](https://huggingface.co/datasets/open-r1/OpenR1-Math-220k) | verified reasoning traces / answer format 稳定训练 | 控制长度和类别 |
| P2 | [AI-MO/NuminaMath-CoT](https://huggingface.co/datasets/AI-MO/NuminaMath-CoT) | math CoT curriculum / data mix | 通用数学数据，不保证贴合 hidden distribution |

### 论文和方法

| 优先级 | 链接 | 方法 | 可转化实验 |
| --- | --- | --- | --- |
| P3 | [TIES-Merging](https://arxiv.org/abs/2306.01708) | trim + elect sign + merge，降低多模型合并干扰 | 对多个 adapter delta 做 sign-consensus merge |
| P3 | [DARE / Language Models are Super Mario](https://arxiv.org/abs/2311.03099) | drop and rescale delta merge | 对 adapter delta 做稀疏化再 merge |
| P3 | [Editing Models with Task Arithmetic](https://arxiv.org/abs/2212.04089) | task vector / delta addition | 同源 LoRA adapter 的加权 delta 实验 |
| P2 | [QLoRA](https://arxiv.org/abs/2305.14314) | NF4 / paged optimizer / efficient finetuning | Kaggle GPU 训练 rank32 adapter 的工程参考 |
| BLOCKED | [DoRA](https://arxiv.org/abs/2402.09353) | weight-decomposed LoRA | 官方 evaluator 是否接受 DoRA adapter 未确认，不直接提交 |

## 阶段情况

| 阶段 | 状态 | 说明 |
| --- | --- | --- |
| Stage 1 | 完成 | Kaggle CLI、资产审计、adapter validator、submission packer、dry-run 都已建立 |
| Stage 2 | 完成 | 公开 adapter 和 notebook output 路线已能审计、repack、远端提交准备 |
| Stage 3 | 部分完成 | proxy eval 框架存在，但 Nemotron 30B + Mamba/CUDA proxy 推理不稳定；不要把 proxy 当完成项 |
| Stage 4 | 部分完成 | daily plan 只生成计划，不自动提交；fusion 方向已有 Rauffauzan/Dedquoc/Hammad 审计 |
| Stage 5 | 完成 | Kaggle-side notebook workflow 可用，避免本地上传 3GB 级 `submission.zip` |
| Stage 6 | 完成复盘 | Hammad/Dedquoc/Kuang public output repack 已提交验证，分别为 `0.85/0.78/0.63`，不能继续按标题 claim 复投 |
| Stage 7 | 进行中 | 已完成开源来源挖掘和候选池；下一步优先做 keithtyser adapter anchors inventory + merge notebook |

## 常用命令

刷新提交历史：

```powershell
python scripts\04_query_submissions.py
```

生成每日提交计划：

```powershell
python scripts\22_make_daily_submission_plan.py
```

检查已知 public-output notebook output：

```powershell
kaggle kernels files muelsyse111/nemotron-repack-hammad-087
kaggle kernels logs muelsyse111/nemotron-repack-hammad-087
kaggle kernels files muelsyse111/nemotron-repack-dedquoc-svd-fusion
kaggle kernels files muelsyse111/nemotron-repack-kuang-087-training
```

远端 output 提交命令模板只作为格式参考，不要直接复制执行：

```powershell
kaggle competitions submit nvidia-nemotron-model-reasoning-challenge -k <kernel_id> -f submission.zip -v <version> -m "<message>"
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
- 不为了用满 5 次额度而提交；激进模式也必须先生成确认卡。
- 不再复投 Hammad/Dedquoc/Kuang/CocoaAI 公开 output。
- 每次真实提交前必须生成 `reports/STAGE7_SUBMIT_CONFIRM_<date>_<slot>_<candidate>.md` 并得到用户确认。

## 下一步

```yaml
NEXT_ACTION:
  status: prepare_stage7_notebook
  action: "build Kaggle-side inventory notebook for keithtyser/nemotron-086-adapters-20260605"
  reason: "Public output repacks failed; the next useful attempt must create a new rank<=32 adapter hash through real fusion or training changes."
```

提交后必须刷新：

```powershell
python scripts\04_query_submissions.py
python scripts\22_make_daily_submission_plan.py
```

结果判断只看 public rank 是否小于 `393`。显示分数仍是 `0.86` 但 rank 前移，也算有效提升。
