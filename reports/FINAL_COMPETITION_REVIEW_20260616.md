# NVIDIA Nemotron 比赛最终复盘 2026-06-16

本报告是比赛结束后的工程复盘，用于给队友和后续接手者解释：最终 leader 信息、我方提交结果、关键决策、失败路线，以及最值得复盘的两条高分提交。

## 数据来源

- Kaggle CLI submission history: `logs/submissions_raw_20260616_final.txt`
- Kaggle CLI top leaderboard snapshot: `logs/leaderboard_show_20260616.csv`
- Kaggle downloaded public leaderboard: `reports/leaderboard_20260616/nvidia-nemotron-model-reasoning-challenge-publicleaderboard-2026-06-16T01_57_45.csv`
- 我方公开榜行: `reports/leaderboard_20260616/our_team_publicleaderboard.json`
- Biohack v62 notebook source: `external/final_sources/biohack_v62/nemotron-v62-d3-sparse-trust-finisher-attack.ipynb`
- Biohack v62 metadata: `external/final_sources/biohack_v62/kernel-metadata.json`
- Biohack v62 logs: `external/final_sources/biohack_v62/kernel_logs.txt`
- Mirza v16 notebook source: `artifacts/stage6/mirzayasir_best_086_meta/best-nvidia-nemotron-notebook-0-86.ipynb`
- Mirza v16 metadata: `artifacts/stage6/mirzayasir_best_086_meta/kernel-metadata.json`
- 6 月 5 日 remote output sweep: `reports/REMOTE_086_SUBMISSION_SWEEP_20260605.md`
- 0.86 阶段复盘: `reports/POST_086_REVIEW_20260605.md`

## Leader 信息

Kaggle CLI `leaderboard --show` 在比赛结束后返回的前排信息如下：

| rank | team | score |
|---:|---|---:|
| 1 | NullSira | 0.92 |
| 2 | vli | 0.90 |
| 3 | YS-L | 0.90 |
| 4 | /make-no-mistakes | 0.90 |
| 5 | Domdolus Tolus | 0.89 |
| 6 | Alehandreus & Yurnero | 0.89 |
| 7 | Solved Bit Manipulation | 0.88 |
| 8 | Researcher 7919 | 0.88 |
| 9 | Fate | 0.88 |
| 10 | kansai-kanto-kaggler | 0.88 |

下载到本地的 `publicleaderboard` 文件中，我方所在队伍为：

```yaml
team_name: "你跑不过我你信吗"
rank_in_downloaded_publicleaderboard: 422
score: 0.86
submission_count: 132
members: "blacklions,llccqq624,llllllc666,muelsyse111,xiangjiangzhou"
```

注意：`leaderboard --show` 和下载的 `publicleaderboard` 文件在顶部显示分数存在轻微差异，例如 NullSira 分别显示为 `0.92` 和 `0.91`。本报告保留两份来源，不强行合并。涉及我方最终提交时，以 `submissions -v` 返回的 `publicScore/privateScore` 为准。

## 我方最终结果

最终 submissions 历史已经返回 `privateScore`。按 privateScore 排序，我方有多条并列最高 `0.85`：

| submission id | date | message | public | private |
|---|---|---|---:|---:|
| 53426831 | 2026-06-06 14:48:50 | `localcal_rohan_anchor_lmhead_loraB_x1.04_structure_preserved` | 0.85 | 0.85 |
| 53667919 | 2026-06-14 09:28:28 | `20260614_slot2_huikang_blocktopk_floor4_clean_probe` | 0.85 | 0.85 |
| 53696351 | 2026-06-15 04:32:34 | `20260615_wrap_biohack_v62_public_sparse_trust_probe` | 0.86 | 0.85 |
| 53448593 | 2026-06-07 11:05:59 | `20260607_slot4_nemotron-s7-muon-full-v5-audited_2d42d0ad` | 0.84 | 0.85 |
| 53467675 | 2026-06-08 05:48:51 | `20260608_slot4_nemotron-s7-seed-stability-replay_f5dde9e0` | 0.85 | 0.85 |

其中最值得重点复盘的是：

```yaml
submission_id: 53696351
message: 20260615_wrap_biohack_v62_public_sparse_trust_probe
publicScore: 0.86
privateScore: 0.85
reason: "它同时保住 public 0.86，并达到我方最高 private 0.85；这是最终冲刺窗口里最有价值的最高并列提交。"
```

如果把 6 月 15 日 `biohack_v62` 分支单独计数：

| biohack branch order | submission id | message | public | private |
|---:|---|---|---:|---:|
| 1 | 53696183 | `20260615_biohack_v62_alpha00085_sparse_trust_probe` | 0.86 | 0.83 |
| 2 | 53696351 | `20260615_wrap_biohack_v62_public_sparse_trust_probe` | 0.86 | 0.85 |

这就是本报告中“第一天第二次 / 最后最高一次”的锚点。按全日时间顺序它是 6 月 15 日当天第三个提交；按 `biohack_v62` 分支它是第二次提交。

## 重点复盘：Biohack v62 最高并列提交

### 来源

```yaml
source_notebook: biohack44/nemotron-v62-d3-sparse-trust-finisher-attack
title: "Nemotron v62 — D3 Sparse-Trust Finisher Attack"
local_notebook: external/final_sources/biohack_v62/nemotron-v62-d3-sparse-trust-finisher-attack.ipynb
machine_shape: NvidiaRtxPro6000
gpu_enabled: true
competition_sources:
  - nvidia-nemotron-model-reasoning-challenge
model_sources:
  - metric/nemotron-3-nano-30b-a3b-bf16
  - multiple kienngx/nemotron-nano-30b-trained adapters
```

### 为什么选择这条路线

1. 它来自最终 public leaderboard 前排用户 `biohack44` 公开 notebook，而不是普通 0.86 重打包。
2. notebook 标题和源码都显示它是从 v60/v61 失败或中性结果继续迭代出来的 v62 版本，包含明确机制变化。
3. 它不是大范围盲训，而是短步数 finisher 加极小幅度 sparse-trust merge，风险比全量训练或大权重融合低。
4. 它针对比赛题型中的 substitution cipher / D3 规则生成 verified traces，同时加入原始答案保护样本，目标是改善一个弱点而不破坏整体能力。
5. 它输出标准 LoRA adapter submission.zip，保持比赛提交格式，不需要本地加载 30B base model。

### 训练与数据策略

从 notebook 源码和日志可确认：

```yaml
version: v62_d3_sparse_trust_finisher
start_adapter_auto_selection:
  preferred:
    - huikang/nemotron-adapter default/20
    - BorgQueen/GlyphMatics lane if mounted
  actual_log_start_adapter: /kaggle/input/models/kienngx/nemotron-nano-30b-trained/triton/tinker-adapter/1
base_model: nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16
train_csv_rows: 9500
family_distribution_roughly_balanced:
  bit_manipulation: 1602
  gravity: 1597
  unit_conversion: 1594
  cipher: 1576
  numeral: 1576
  equation_numeric: 1555
d3_verified_rows: 260
d3_upsample: 5
d4_enabled: false
protective_original_answer_only_rows: 1040
final_train_df_rows: 2340
```

核心数据策略不是扩大数据量，而是“可验证专项增强 + 保护性回放”：

- D3 substitution-cipher solver 只接收 verified exact 的样本，降低错误标签风险。
- D3 样本上采样 5 倍，集中修补 cipher 子任务。
- D4 关闭，因为 v60/v61 里 D4 是 hang 风险点。
- 每个非 cipher 家族抽取一定数量的原始 answer-only 样本，防止 finisher 只顾一个专项而破坏其他题型。

### 训练超参

```yaml
max_steps: 14
learning_rate: 9e-8
warmup_steps: 2
max_seq_len: 4096
per_device_batch_size: 1
gradient_accumulation: 16
effective_batch_size: 16
bf16: true
gradient_checkpointing: true
framework: Unsloth + TRL SFTTrainer + PEFT
```

这个配置的关键是“极小学习率 + 极短 finisher”。它不是重训 Nemotron，而是在已有强 adapter 上做非常小的局部修正。

### 合并与优化策略

v62 的真正优化点在合并，不在训练步数：

```yaml
blend_alpha: 0.0010
preserve_lm_head: true
skip_late_experts: true
late_expert_layer_start: 38
max_rel_delta: 0.0022
max_absmax_delta: 0.0060
max_selected_tensors: 600
min_selected_tensors: 250
expert_layer_hard_cap: 30
expert_max_rel_delta: 0.0016
expert_max_fraction: 0.55
nonexpert_min_rel_delta: 1e-7
```

这条路线选择了 `sparse-trust blend`：

1. 先训练一个短步数 finisher adapter。
2. 比较 finisher adapter 和起始 adapter 的 tensor delta。
3. 过滤掉过大、过小、后层专家、`lm_head` 等高风险 tensor。
4. 只选最稳定的一小部分 tensor，最多 600 个。
5. 用很小的 alpha 把这些 delta 融回起始 adapter。
6. 只有最终 zip 结构、大小、rank 和标记全部通过，才输出真正的 `submission.zip`。

相比我们之前的 SVD / TIES / DARE / full-epoch Muon 路线，它更符合最终 private 稳定性需求：改动非常小，但机制不同，并且明确保护大部分原始 adapter 行为。

### 为什么第二次 Biohack v62 比第一次更好

第一条 `20260615_biohack_v62_alpha00085_sparse_trust_probe`：

```yaml
public: 0.86
private: 0.83
inferred_change_from_message: "alpha00085 variant"
```

第二条 `20260615_wrap_biohack_v62_public_sparse_trust_probe`：

```yaml
public: 0.86
private: 0.85
inferred_change_from_message: "wrapped public sparse-trust candidate"
```

可确认的结论：

- 第一条虽然 public 保住 0.86，但 private 掉到 0.83，说明 alpha 或包装变体破坏了泛化。
- 第二条更接近公开 Biohack v62 的默认 sparse-trust 逻辑，private 回到 0.85。
- 因此，最终最高提交的核心不是“再把 alpha 调小/调大”，而是回到经过作者验证的 public sparse-trust candidate，避免我们自己额外改坏。

不可确认的部分：

- 本地仓库没有保存 `20260615_wrap_biohack_v62_public_sparse_trust_probe` 的完整打包脚本差异。
- 因此不能声称它一定等价于 notebook v62 默认 output，只能说它与该公开 notebook 强相关，且 message 与本地拉取源码一致。

## 截图中的 Mirza v16 提交复盘

你截图里的这次提交是：

```yaml
submission_id: 53384030
message: 20260605_slot4_mirzayasir_best_086_v16_remote_output
source_kernel: mirzayasirabdullah07/best-nvidia-nemotron-notebook-0-86
source_version: 16
adapter_dataset: assiabenazzouz/adappter-v32-epoch-5
publicScore: 0.86
privateScore: 0.84
local_notebook: artifacts/stage6/mirzayasir_best_086_meta/best-nvidia-nemotron-notebook-0-86.ipynb
```

它的策略非常清楚：不是训练，而是可靠打包公开 adapter。

关键步骤：

1. 使用 `kagglehub.dataset_download("assiabenazzouz/adappter-v32-epoch-5")` 获取 adapter 数据集。
2. 指定 adapter 目录 `/kaggle/input/datasets/assiabenazzouz/adappter-v32-epoch-5/adapter`。
3. 将 `adapter_config.json` 和 `adapter_model.safetensors` 平铺写入 `/kaggle/working/submission.zip`。
4. 检查 rank 不超过 32。
5. 通过 Kaggle remote output submit 提交 notebook v16 的 output，而不是本地下载再上传大 zip。

为什么当时选择它：

- 前面 Huikang v27 raw/normalized 多次官方 ERROR，说明“结构正确”不等于“官方 evaluator 能接受”。
- Mirza v16 是公开 0.86 notebook，路径清晰，output 已经可用。
- 它只做打包，不引入训练不确定性，适合作为快速确认 0.86 平台的基线。

为什么它不是最终最高：

- 它 public 是 0.86，但 private 是 0.84。
- 它没有做针对 private 泛化的优化，只复现了公开 adapter 打包路线。
- 它证明了 remote-output submit 和 adapter packaging 是可行的，但不是最终 private 最稳路线。

## 全流程关键决策复盘

### Stage 1：先做资产审计和最小闭环

正确点：

- 先检查 Kaggle CLI、提交历史、adapter validator、submission packer。
- 正确处理 `No submissions found`，避免把无历史提交误判为认证失败。
- 不训练、不提交，先把工具链稳定下来。

收益：

- 后面可以快速判断 zip 结构、rank、safetensors 可打开、SHA256。
- 避免一开始就把时间花在大训练框架上。

### Stage 2：公开 adapter 获取与结构验证

正确点：

- 找到 Huikang/Tong 类 adapter 后先做本地结构验证和打包。
- 发现本地上传 1GB+ submission.zip 非常慢后，切换到 Kaggle-side notebook workflow。

失败点：

- Huikang v27 raw 和 normalized 都官方 ERROR。
- 说明 adapter_config、target_modules、base_model path、零 tensor 清理这些结构修复仍不能保证 evaluator 兼容。

### Stage 3：proxy eval 方向价值有限

结论：

- 本地和 Kaggle Notebook 跑 Nemotron 30B + Mamba CUDA 链路非常脆。
- proxy eval 框架可以保留，但不能用它替代官方评测。
- 官方 evaluator 才是最终分数来源。

### Stage 5/6：remote-output submit 是最大效率提升

真正突破：

```powershell
kaggle competitions submit nvidia-nemotron-model-reasoning-challenge `
  -k <kernel_id> `
  -f submission.zip `
  -v <version> `
  -m "<message>"
```

收益：

- 避免本地上传 1GB 到 3GB 的 zip。
- 可以直接复用公开 notebook output。
- 6 月 5 日一天内快速验证了多条 0.86 路线。

这是整个项目最重要的工程决策。

### Stage 7 之后：0.86 平台很宽，public rank 不等于 private 稳定

观察：

- public 0.86 范围巨大，下载的 publicleaderboard 中 0.86 有 1636 支队伍。
- 很多 public 0.86 最终 private 只有 0.83 或 0.84。
- 一些 public 0.84/0.85 的路线反而 private 到 0.85。

结论：

- 继续追 public 0.86 没有意义。
- 真正要做的是保 private 泛化，尤其避免大幅改坏强 adapter。

## 失败路线总结

| 路线 | 结果 | 教训 |
|---|---:|---|
| Huikang v27 raw / normalized | ERROR | 结构验证通过不代表 evaluator 兼容 |
| Kien public training output repack | public 0.63 | 公开训练输出不一定是强 adapter |
| Akihiko small LoRA | public 0.50 | 小 adapter 即使 CC0 和结构正确，也不具备竞争力 |
| Dedquoc SVD fusion | public 0.78 | SVD/fusion 不一定比单个强 adapter 好 |
| DARE/TIES merge | public 0.84 | 合并类方法容易稀释有效信号 |
| 多个 aggressive SVD/rank 变体 | public 0.84-0.85 | 结构创新不等于分数提升 |
| full Muon training | public 0.84 / private 0.85 | 大训练成本高，但 private 稳定性未必差 |
| Biohack alpha00085 variant | public 0.86 / private 0.83 | 轻微参数变体也可能破坏 private 泛化 |

## 最终经验

1. 对这种只提交 adapter 的比赛，优先验证公开强 output，而不是本地重训 30B。
2. remote-output submit 比本地上传大 zip 更可靠。
3. public 0.86 不是强信号；0.86 是大平台，private 差异才是关键。
4. 大幅 fusion、SVD、TIES、DARE 在本任务上整体不如“强 adapter + 小幅可信 finisher”。
5. 真正有效的优化更像 Biohack v62：可验证专项数据、极短训练、极小 alpha、稀疏 tensor 选择、保护 `lm_head` 和后层专家。
6. 标题 claim 不可信，只有官方 submission history 的 public/private score 可信。
7. 复盘必须保留 source notebook、metadata、logs、submission message，否则最终很难解释哪次提交到底做了什么。

## 建议交接说明

若队长需要复现或审查最高路线，优先看：

```text
external/final_sources/biohack_v62/
logs/submissions_raw_20260616_final.txt
logs/top_private_submissions_20260616.json
reports/leaderboard_20260616/
reports/FINAL_COMPETITION_REVIEW_20260616.md
```

若队长要看截图中 Mirza v16 的 notebook：

```text
artifacts/stage6/mirzayasir_best_086_meta/
reports/REMOTE_086_SUBMISSION_SWEEP_20260605.md
reports/POST_086_REVIEW_20260605.md
```

不要把 `submission.zip`、`.safetensors`、Kaggle token 或大权重文件提交到 GitHub。当前复盘只推送 notebook 源码、metadata、日志摘要和报告。
