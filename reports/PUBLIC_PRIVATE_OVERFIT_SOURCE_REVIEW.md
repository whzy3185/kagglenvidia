# Public/Private Leaderboard 过拟合资料与策略

更新时间：2026-06-06

比赛：`nvidia-nemotron-model-reasoning-challenge`

当前目标：不要只追显示分数 `0.86/0.87`，而是让 public rank 从当前平台位置继续前移，并降低最终 private shake-up 风险。

## 当前问题

这个比赛只有一部分隐藏测试集参与 public leaderboard，另一部分会在最终 private leaderboard 使用。public score 是有用信号，但不是最终目标本身。连续根据 public 分数选择 notebook、复投公开 output、微调融合权重，都会把 public leaderboard 逐渐变成被反复使用的验证集。

当前本地证据已经说明，notebook 标题或作者 claim 不能直接当成真实路线：

| 路线 | 我方官方 public 结果 | 结论 |
|---|---:|---|
| Mohamed replay data | 0.86 | 当前 best 家族之一 |
| Taha custom repo | 0.86 | 当前 best 家族之一 |
| Rauffauzan fusion output | 0.86 | 可参考 fusion 机制，不应原样复投 |
| Mirza packaging route | 0.86 | 可参考 packaging，不应原样复投 |
| Hammad 0.87 claim | 0.85 | 标题 claim 失效 |
| Dedquoc SVD fusion claim | 0.78 | output 失效，代码可参考 |
| Kuang 0.87 training claim | 0.63 | output 失效 |
| Keithtyser multi-anchor task arithmetic | 0.85 | 当前融合实现未提升，不能继续盲调同类参数 |

结论：下一阶段必须减少“看标题、看 public claim、看单次 public score”的决策权重，改为记录机制差异、来源独立性、验证证据和 public/private 过拟合风险。

## 论文与方法来源

| 来源 | 类型 | 核心观点 | 对当前项目的用法 |
|---|---|---|---|
| [A Meta-Analysis of Overfitting in Machine Learning](https://papers.nips.cc/paper_files/paper/2019/hash/ee39e503b6bedf0c98c388b7e8589aca-Abstract.html) | Kaggle public/private 实证研究 | 分析 100+ Kaggle 比赛，比较 public ranking 与 final ranking，研究测试集复用带来的适应性过拟合。 | 不能把 public rank 的小幅波动当成可靠泛化提升；需要记录提交次数、机制差异和最终选择偏差。 |
| [The Ladder: A Reliable Leaderboard for Machine Learning Competitions](https://proceedings.mlr.press/v37/blum15.html) | 可靠 leaderboard 机制 | 反复提交会让参赛者适应 public holdout；Ladder 通过只公布显著改进来降低过拟合。 | 我方没有控制 Kaggle leaderboard 机制，但可以内部模拟：只有明显 rank 前移或机制证据充分时才继续沿该方向。 |
| [Reducing overfitting in challenge-based competitions](https://arxiv.org/abs/1607.00091) | 小样本 leaderboard 风险 | public leaderboard 样本小的时候，轻微分数波动更容易被利用并导致过拟合；提出 bootstrap 风格的分数发布思路。 | 如果本比赛 public 占比只有一半，且 0.86 平台拥挤，小数位或 rank 微动应按高噪声处理。 |
| [Climbing a shaky ladder: Better adaptive risk estimation](https://arxiv.org/abs/1706.02733) | adaptive risk estimation | 继续研究 Ladder 问题，并指出 adaptive leaderboard 本身存在可攻击和噪声问题。 | 禁止把 Kaggle public leaderboard 当成无限超参搜索器。 |
| [The Reusable Holdout](https://sachsmc.github.io/reusable-holdout/) | 可复用 holdout 方法与实验代码 | 面向反复使用验证集时如何保持有效性的研究；附有 Python/R 实验代码。 | 建议建立内部 candidate holdout 思路：提交前冻结假设，提交后只按预设规则解释，不用一次 public 结果反向无限调参。 |
| [On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation](https://jmlr.csail.mit.edu/papers/v11/cawley10a.html) | 模型选择过拟合 | 选择准则本身有方差时，反复优化该准则会过拟合，效果可与算法差异同量级。 | public score/rank 就是高方差选择准则；提交策略必须避免对同一微变量反复扫。 |

## 开源仓库与数据源

| 来源 | 类型 | 可用信息 | 本项目用途 |
|---|---|---|---|
| [sachsmc/reusable-holdout](https://github.com/sachsmc/reusable-holdout/tree/master/Code) | reusable holdout 实验代码 | 包含 Dwork et al. reusable holdout 相关 Python/R 实验文件。 | 参考其“验证集反复使用”的风险建模，不直接接入比赛评测。 |
| [Kaggle Meta Kaggle](https://www.kaggle.com/datasets/kaggle/meta-kaggle) | Kaggle 历史公开数据 | Kaggle 官方公开的 competitions、submissions、scores、code 等元数据。 | 用于后续离线分析“public rank 与 private rank 的历史 shake-up”，不是当前比赛 hidden 标签来源。 |
| [Kaggle Meta Kaggle Code](https://www.kaggle.com/datasets/kaggle/meta-kaggle-code) | Kaggle notebook 代码数据 | 大量公开且 Apache 2.0 许可的 Kaggle notebook 源码。 | 可检索竞赛中常见防过拟合、提交选择、CV/holdout 实践。 |
| [Cloud-CV/EvalAI](https://github.com/Cloud-CV/EvalAI) | 开源评测平台 | 支持 public/private leaderboard、remote evaluation、evaluation worker 等挑战赛机制。 | 参考其 public/private split 和 challenge phase 设计，帮助设计内部 proxy/holdout gate。 |
| [codalab/codalab-competitions](https://github.com/codalab/codalab-competitions) | 开源竞赛平台 | CodaLab Competitions 平台源码，JMLR 论文配套。 | 参考 competition phase、submission、leaderboard 的组织方式。 |
| [codalab/codabench](https://github.com/codalab/codabench) | 开源 benchmark 平台 | Codabench 是可复现 benchmark 平台，Apache 2.0。 | 参考可复现实验记录、基准和提交阶段设计。 |
| [paris-saclay-cds/ramp-workflow](https://github.com/paris-saclay-cds/ramp-workflow) | 数据挑战 workflow | 定义和运行 predictive workflow 的工具。 | 可借鉴“统一候选接口 + 统一报告”的思想，不直接迁移到 LLM adapter 推理。 |
| [Hugging Face PEFT model merging](https://huggingface.co/docs/peft/developer_guides/model_merging) | LoRA merge 文档 | PEFT 支持 linear、SVD、TIES、DARE 等 adapter merge 方法。 | 支撑后续 fusion 方向，但必须避免本地加载 30B base model。 |
| [arcee-ai/mergekit](https://github.com/arcee-ai/mergekit) | 模型合并工具 | 支持多种 LLM merge 算法，偏 full model merge。 | 只参考算法配置和 merge 思路，不在本地合并 30B base。 |
| [sail-sg/lorahub](https://github.com/sail-sg/lorahub) | LoRA 动态组合 | 用多个 LoRA 模块做跨任务组合。 | 可参考 LoRA 权重搜索思想，但不能用 public leaderboard 当权重优化目标。 |
| [tonghuikang/nemotron](https://github.com/tonghuikang/nemotron) | Nemotron 比赛公开训练路线 | 包含 reasoning、augmentation、corpus、train_sft、loss/lr 相关代码。 | 当前最相关训练代码来源；下一步若训练新 adapter，应在 Kaggle 资源上做单一主变量实验。 |

## 当前比赛的过拟合判断框架

每个候选提交前，生成一张风险卡。不要只问“能不能 0.86”，而要问下面 8 个问题：

| 维度 | 低风险 | 高风险 |
|---|---|---|
| source_independence | 来源、训练数据、融合机制与当前 best 明显不同 | 只是当前 best 的同源 output 或同 hash 复投 |
| mechanism_distinctness | 改了一个可解释主变量 | 同时改多个变量，无法复盘 |
| public_probe_count | 该方向提交次数少 | 同一方向连续按 public 反馈调参 |
| score_margin | rank 明显前移 | 只是在 0.86 平台内无明显移动 |
| validation_evidence | 有结构验证、日志、proxy/holdout 或强代码证据 | 只有 notebook 标题 claim |
| private_robustness | 不牺牲已知强项，或有明确 tradeoff 证据 | public 低分却强行解释为 private 可能好 |
| duplicate_hash | 新 SHA256、新 adapter 行为 | same hash 或几乎同源重打包 |
| format_safety | rank<=32、zip 根目录正确、官方评测 COMPLETE | ERROR 或结构不明 |

建议输出：

```yaml
PUBLIC_PRIVATE_OVERFIT_RISK_CARD:
  candidate:
  source:
  main_change:
  source_independence: low | medium | high
  mechanism_distinctness: low | medium | high
  public_probe_count_for_family:
  validation_evidence:
  duplicate_hash: true | false | unknown
  public_score_if_submitted:
  public_rank_delta_if_known:
  risk_level: low | medium | high
  decision: submit | hold | reject
  reason:
```

## 只有一半 public 时怎么判断

如果 public leaderboard 只覆盖隐藏测试集的一半，那么 public score 对 private score 是一个抽样估计，而不是最终真值。直接后果：

1. `0.86` 平台内部的微小 rank 差异可能只是 public 子集噪声。
2. 同一机制的反复微调越多，越可能选择到“刚好适配 public 子集”的候选。
3. public 从 `0.86` 掉到 `0.85` 的候选，通常不能寄希望于 private 反转，除非它有明确机制说明为什么 public 子集被牺牲而 private 更可能获益。
4. public 仍是 `0.86` 但 rank 不前移，不应视为有效提升。
5. public 仍是 `0.86` 且 rank 明显前移，可以作为继续围绕该机制做小变体的证据，但仍不能声称 private 一定提升。

## 对下一阶段的直接策略

当前不建议继续提交普通公开 output repack，也不建议继续对已掉分的 Keithtyser task arithmetic 融合做盲目权重微调。更合理的方向是：

1. 先把候选分成“训练路线”“融合路线”“数据处理路线”“公开 output 复投”四类。
2. 复投类除非有新 SHA、新机制、新日志，否则直接拒绝。
3. fusion 类必须从“同一变量改变”开始，例如只换 merge 算法、只换 density、只换 anchor 组合，不能同时改三件事。
4. training 类优先基于 `tonghuikang/nemotron`、Mohamed、Taha 等已证明 0.86 家族，做一个主变量：loss mask、LR、数据 mix、curriculum。
5. 每天可以激进用 quota，但每次提交前必须有风险卡；提交后必须把 public score、rank、source、SHA、主变量写入复盘。

## 推荐新增任务链

下一轮如果继续推进，先做这三个轻量文件，不需要大改 workflow：

```text
configs/public_private_overfit_policy.yaml
reports/PUBLIC_PRIVATE_OVERFIT_RISK_CARD_<candidate>.md
reports/STAGE7_SUBMISSION_REVIEW_<date>_<slot>_<candidate>.md
```

推荐提交前 gate：

```yaml
SUBMIT_GATE:
  current_best_public_score: 0.86
  target_metric: public_rank_delta
  no_same_hash: true
  no_title_claim_only: true
  main_change_is_single_variable: true
  source_independence_recorded: true
  public_private_overfit_risk_level: low | medium | high
  user_confirmed_submit: true
```

## 本轮边界

本轮只查找和整理论文、开源仓库与策略，不提交比赛，不训练，不加载 Nemotron 30B，不下载或写入大模型权重，不提交 `.safetensors` 或 `submission.zip`。
