# Stage 7 Master+ Discussion And Writeup Research Workflow

更新时间：2026-06-06

## 工作流变更

从现在开始，Stage 7 后续所有训练、fusion、数据处理、notebook 修改之前，都必须先完成一轮外部研究 gate。

这不是“多搜几个链接”的附加步骤，而是候选设计的前置条件：

```yaml
RESEARCH_GATE_REQUIRED_BEFORE:
  - candidate selection
  - notebook generation
  - kaggle kernel push
  - competition submit confirmation card
```

没有完成研究 gate 时，不得继续凭直觉改训练参数、fusion 权重或数据 mix。

## 为什么要改

我们已经验证过：

- notebook 标题里的 `0.87` 不可靠；
- public output repack 不能继续推动 rank；
- Keithtyser 多 adapter task arithmetic 没提升，结果是 `0.85`；
- Mohamed/Taha/Rauffauzan/Mirza 处在 `0.86` 平台，但靠重复提交或小改动不一定能前移；
- public/private 只有部分重合，继续用 public leaderboard 做超参搜索会过拟合。

因此下一步必须先读懂高排玩家已经公开的讨论、代码、数据生成方式和类似比赛复盘，再决定具体改什么。

## 已确认可用的信息通道

### Kaggle CLI

当前 Kaggle CLI 可以用：

```powershell
kaggle competitions leaderboard nvidia-nemotron-model-reasoning-challenge --show --page-size 20
kaggle competitions topics list nvidia-nemotron-model-reasoning-challenge -v -p 1
kaggle competitions topic-messages nvidia-nemotron-model-reasoning-challenge <topic_id> -n -1 -v
```

注意：`topics` CSV 中 `authorName` 当前经常为空；如果需要验证 Kaggle Master / Grandmaster tier，需要打开 Kaggle profile 页面或使用已登录浏览器人工确认。

### Web / GitHub / Hugging Face

需要补充浏览：

- Kaggle profile、Code、Discussions；
- GitHub repo；
- Hugging Face model/dataset/paper；
- 已结束类似竞赛的 solution / writeup；
- 官方 NVIDIA Nemotron / NeMo / evaluator 文档。

## 当前 leaderboard 前排观察

本轮通过 CLI 拉取前 20 名 public leaderboard，前排队伍包括：

| Public Rank | Team | Score |
|---:|---|---:|
| 1 | NullSira | 0.89 |
| 2 | Y \| M \| F | 0.87 |
| 3 | Researcher 7919 | 0.87 |
| 4 | Alehandreus & Yurnero | 0.87 |
| 5 | Team | 0.87 |
| 6 | Kh0a | 0.87 |
| 7 | Fate | 0.87 |
| 8 | LX | 0.87 |
| 9 | JK-Piece | 0.87 |
| 10 | Lora is all you need | 0.87 |
| 11 | Surya milenial | 0.87 |
| 12 | Yoshinari Kawashima | 0.87 |
| 13 | Michal Gromadzki | 0.87 |
| 14 | GeniusYY | 0.87 |
| 15 | Tsingtao Bro | 0.87 |
| 16 | kansai-kanto-kaggler | 0.87 |
| 17 | sda sad ads | 0.87 |
| 18 | coreforged | 0.87 |

后续如果要说“master+账号的经验”，必须逐个追踪 profile / discussion / code，而不是只看 team name。

## 必读 Nemotron 讨论

| Topic ID | Title | 已提取信号 | 对 workflow 的影响 |
|---:|---|---|---|
| 704491 | From Solving Overfitting to Fighting Non-Determinism | 同数据/同配置可能产生明显不同 score；seed 与训练非确定性强；有人提到 Muon 可能更稳定但配置错误会大跌。 | 后续训练候选必须记录 seed、重复运行风险、optimizer、run-to-run 方差；不要用单次 public score 判定方向。 |
| 703240 | From 8% to 71% on Cryptarithm Tasks, But Score Still Stuck at 0.86 | cryptarithm 提升会被 gravity/numeral/unit_conversion/bit regression 抵消；local validation 和 LB 存在噪声；LoRA rank 32 限制下类别权衡很强。 | 新数据 mix 必须先写 category tradeoff 假设；禁止只增强一个弱类而不保护强类。 |
| 687961 | Training Nemotron-3-Nano-30B-A3B-BF16 with rank 32 LoRA on length 8192 sequences | 8192 序列、rank32 LoRA、RTX Pro 6000 内存和吞吐限制；fused CE、microbatch、FA2/Unsloth 是关键。 | full training runtime 长是预期；不要为了快而隐式砍训练量，除非明确标记为 smoke test。 |
| 698293 | 97.2% Gold-Conditioned Symbolic Solver | symbolic/equation 结构可被 solver 解释，但使用 gold answer 的 solver 不能直接当提交方案。 | 可用于数据生成/CoT 质量分析，不得把 oracle 当推理方案。 |
| 681745 | Official Resources | 官方 Nemotron、NeMo Data Designer、Curator、RL、metric/evaluator 资源。 | 基础设施变更优先查官方资源，不靠猜测。 |
| 704473 | Extending Model Merging to LoRa Ensembling | LoRA ensembling/fusion 讨论。 | 新 fusion 方案必须先和该讨论里的机制对齐或说明差异。 |
| 702447 | How to break 0.86 ceiling | plateau-breaking 社区讨论。 | 只提取可复现实验机制，不采纳空 claim。 |
| 701761 | Score 0.87 started queuing at the top of leaderboard | 0.87 队伍开始堆叠，rank 是有效指标。 | 继续把 public rank delta 放在 score label 之前。 |

## 必读类似竞赛复盘

后续每一轮较大调整前，至少覆盖下面四类：

| 类别 | 为什么相关 | 需要提取 |
|---|---|---|
| AIMO / AI Mathematical Olympiad | LLM reasoning、数学/符号数据、verifier、synthetic data、public/private 分裂。 | 数据生成、solver/verifier、训练/推理分工、shake-up 经验。 |
| ARC Prize | 规则/符号/程序搜索式推理，类似“弱类别靠程序生成或结构化 CoT”。 | puzzle solver、数据合成、ensemble/selection、过拟合防护。 |
| LLM Science Exam | LLM 竞赛中的检索、数据清洗、ensemble、public/private 选择。 | validation 设计、submission selection、ensemble 纪律。 |
| Don't Overfit / Don't Overfit II | public leaderboard 过拟合教科书。 | 提交节奏、public/private 选择偏差、防 shake-up 方法。 |

Seed links for follow-up reading:

- AIMO2 leaderboard: https://www.kaggle.com/c/ai-mathematical-olympiad-progress-prize-2/leaderboard
- AIMO2 1st place paper: https://arxiv.org/abs/2504.16891
- AIMO2 2nd place code/writeup: https://github.com/imagination-research/aimo2/
- ARC Prize 2024 competition page: https://arcprize.org/competitions/2024/
- ARC Prize 2024 technical report: https://arcprize.org/media/arc-prize-2024-technical-report.pdf
- ARC Prize 2024 arXiv: https://arxiv.org/abs/2412.04604
- ARC Prize 2024 winning solution page: https://da-fr.github.io/arc-prize-2024/
- ARC Prize 2024 solution repository example: https://github.com/zoenguyenramirez/arc-prize-2024
- LLM Science Exam Kaggle recap pointer: https://www.linkedin.com/posts/kaggle_its-a-wrap-our-llm-science-exam-competition-activity-7123411997051772929-Jn5t

## 新候选设计模板

以后每个候选必须附带以下内容：

```yaml
RESEARCH_BACKED_CANDIDATE_CARD:
  candidate:
  source_accounts_reviewed:
  kaggle_topics_reviewed:
  similar_writeups_reviewed:
  copied_claims: []
  concrete_mechanism:
  category_tradeoff_hypothesis:
  expected_rank_effect:
  public_private_overfit_risk:
  why_not_title_claim_only:
  why_not_duplicate_public_output:
  implementation_plan:
  submit_allowed: false
```

## 实施规则

1. 每次新 notebook 前先更新 `reports/STAGE7_MASTER_DISCUSSION_RESEARCH.md` 或单独的 source notes。
2. 每次训练/fusion 实现前必须跑：

```powershell
python scripts\26_stage7_research_gate.py
```

3. gate 不通过时，只允许继续浏览、整理、写报告，不允许生成新提交候选。
4. Kaggle topic 内容可用 CLI 拉取；账号 tier 和历史 discussion 需要 Kaggle 页面或 Chrome 登录态辅助确认。
5. 不允许把 Master/Grandmaster 身份当成方案正确性的证明；只把他们的可复现实验、代码、数据、失败复盘纳入证据。

## 下一步

```yaml
NEXT_ACTION:
  status: research_before_more_training_changes
  action: "run scripts/26_stage7_research_gate.py and fill missing source notes before designing the next candidate"
  reason: "Future changes must be backed by high-rank discussion evidence and similar-competition writeups, not by leaderboard title claims."
```
