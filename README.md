# Nemotron 0.86+ Kaggle 冲分工程交接说明

本仓库用于 Kaggle 比赛 `nvidia-nemotron-model-reasoning-challenge` 的分阶段复现、打包、提交规划和复盘。  
目标不是搭一个大而全的自动化平台，而是用可审计流程稳定复现公开高分路线，并继续寻找 `0.87+` 的可执行增量。

本 README 面向两类接手者：

- 新的 Codex / Agent：先读这里，再读报告，不要凭上下文猜。
- 人类操作者：按命令刷新状态，按报告决定下一步，不要盲目提交。

编码说明：本文件使用 UTF-8；如果 PowerShell 直接 `Get-Content` 出现乱码，请用编辑器或 `Get-Content README.md -Encoding UTF8` 查看。

## 当前状态

截至 `2026-06-05`：

- Kaggle CLI：可用，认证正常。
- 规则接受：已在 Kaggle 网页端完成。
- 当前队伍：`muelsyse111`
- 当前最好 public score：`0.86`
- 当前 public rank：`399`
- `0.86` 区间：rank `19` 到 `1376`，共有 `1358` 队。
- 今天有效提交次数：`5`
- 今天剩余额度：`0`
- 当前动作：今天停止提交，下一步审计 `0.87+` 或 `0.89` 路线。

最新事实源：

- `reports/SCORECARD.md`
- `reports/POST_086_REVIEW_20260605.md`
- `reports/LEADERBOARD_STATUS_20260605.md`
- `reports/DAILY_SUBMISSION_PLAN.md`

如果这些报告过期，先运行刷新命令，不要沿用旧结论。

## 当前最好的两次提交

当前最高 public score 是 `0.86`，有多条提交并列。按“分数最高 + 最适合作为后续 0.87+ 改进起点”的标准，当前最重要的两次是：

| 优先级 | submission_id | 路线 | public score | 为什么重要 |
| ---: | --- | --- | --- | --- |
| 1 | `53384098` | Mohamed replay-data finetune：`mohamedamr992/nemotron-replay-data-0-86` v4 | `0.86` | 公开 GPU 训练路线，使用 Nemotron base，加 `mohamedamr992/replay-math` 数据；可观察超参为 LoRA `r=32`、`alpha=32`、`dropout=0.0`、`max_seq_len=8192`、`steps=1000`、`batch=32`、`micro_batch=4`、`lr=3.5e-4`、MoE expert tie enabled。 |
| 2 | `53384096` | Taha custom repo finetune：`tahaalam2009/end-to-end-finetuning-for-lb-0-86-custom-repo` v6 | `0.86` | 公开 GPU 训练路线，使用 Nemotron base 和 custom repo；可观察超参为 LoRA `r=32`、`alpha=32`、`dropout=0.0`、`max_seq_len=8192`、`steps=1000`、`batch=32`、`micro_batch=4`、`lr=2e-4`、MoE expert tie enabled。 |

另外两条也是并列最高 `0.86`，但更偏“可提交包复现/打包路线”，后续改进信息量略少：

| submission_id | 路线 | public score | 备注 |
| --- | --- | --- | --- |
| `53383735` | Rauffauzan fusion/rank compression：`rauffauzanrambe/lora-adapter-fusion-and-rank-compression-pipeline` | `0.86` | Huikang v20 相关 LoRA fusion + SVD rank compression 到 `32`。 |
| `53384030` | Mirza packaging route：`mirzayasirabdullah07/best-nvidia-nemotron-notebook-0-86` v16 | `0.86` | 使用 `assiabenazzouz/adappter-v32-epoch-5`，主要是 adapter packaging/提交包生成路线。 |

接手者不要把这两条“最佳”理解为比其他 `0.86` 分数更高；它们是同分并列，只是后续可继续调参和复现的信息量更高。

## 最高优先级规则

任何接手者必须遵守：

- 不泄漏 Kaggle token，不提交 `kaggle.json`。
- 不使用多账号，不绕过每日提交额度。
- 不自动接受比赛规则，不模拟网页登录。
- 不伪造 public score，不把 notebook 标题当作真实分数。
- 不把 structural-valid 当作 official-valid。
- 不提交 rank `>32` 的 LoRA adapter。
- 不下载或提交大模型权重到仓库。
- 本地 RTX 4060 只做脚本、结构验证、打包和轻量检查，不跑 Nemotron 30B 主训练。
- 没有明确新机制时，不重复提交同一个 hash 或同一失败路线。
- 今天额度为 `0` 时，任何提交动作都必须停止。

## 接手后先做什么

在项目根目录执行：

```powershell
cd E:\Jitter\nemotron_086plus_repro
git status -sb
python scripts\04_query_submissions.py
python scripts\22_make_daily_submission_plan.py
```

然后阅读：

```text
reports/DAILY_SUBMISSION_PLAN.md
reports/SCORECARD.md
reports/POST_086_REVIEW_20260605.md
reports/LEADERBOARD_STATUS_20260605.md
```

如果 `DAILY_SUBMISSION_PLAN.md` 写着 `do not submit today`，就不要提交。

## 项目阶段

### Stage 1：资产审计 + 最小闭环

状态：已完成。

已实现：

- Kaggle CLI 检查。
- 公开 baseline 资产审计。
- adapter 结构验证器。
- `submission.zip` 打包器。
- 提交历史解析。
- dry-run 报告。

关键脚本：

```powershell
python scripts\00_check_kaggle_cli.py
python scripts\01_asset_audit.py
python scripts\02_validate_adapter.py --adapter-dir <adapter目录>
python scripts\03_pack_submission.py --adapter-dir <adapter目录>
python scripts\04_query_submissions.py
python scripts\05_stage1_dry_run.py
```

### Stage 2：公开 adapter / baseline 路线复现

状态：已完成多条路线审计与打包验证。

重点结论：

- Huikang v27 adapter 结构有效，但官方评测失败，不再盲交。
- Kaggle-side repack notebook 能在 Kaggle 云端生成 `submission.zip`。
- 远端 kernel output 提交流程有效，避免本地上传 1GB 到 3.5GB 的 zip。

关键报告：

```text
reports/HUIKANG_V27_ROUTE_DECISION.md
reports/SUBMISSION_ERROR_TRIAGE.md
reports/KIEN_ROUTE_SWITCH_DECISION.md
reports/RAUFFAUZAN_FUSION_OUTPUT_CHECK.md
```

### Stage 3：proxy eval

状态：部分建设完成，但不是当前主路径。

原因：

- Kaggle Notebook 中跑 Nemotron 30B proxy 推理时遇到 Mamba/CUDA kernel 兼容问题。
- 这不代表官方评测不能跑。
- 当前真实分数来自官方 Kaggle evaluator，不来自本地 proxy。

处理原则：

- 不伪造 `proxy_predictions.jsonl`。
- 不把 proxy eval 写成 complete。
- 后续如果继续 Stage 3，应先解决 GPU/CUDA/Mamba 兼容或换更轻量代理验证。

### Stage 4：fusion / specialist / daily runner

状态：只做了可控提交计划和公开 fusion 路线复现，没有做自动提交 runner。

已实现：

- daily submission plan：只生成计划，不自动提交。
- Rauffauzan fusion/rank compression 路线已提交并得到 `0.86`。
- Dedquoc SVD fusion notebook 已准备为下一窗口候选，但今天不能提交。

关键脚本：

```powershell
python scripts\22_make_daily_submission_plan.py
python scripts\25_make_kaggle_repack_public_kernel_output.py --help
```

### Stage 5：Kaggle-side notebook workflow

状态：已可用。

用途：

- 本地只生成小 notebook 项目。
- Kaggle 云端挂载公开 adapter 或公开 notebook output。
- Kaggle 云端生成 `submission.zip`。
- 用户或 CLI 使用 Kaggle output 提交，避免本地大文件上传。

关键脚本：

```powershell
python scripts\21_push_kaggle_notebook.py --kernel-dir "<kaggle_kernels下的目录>"
python scripts\23_make_kaggle_repack_notebook_v2.py --help
python scripts\24_make_kaggle_repack_kien_output.py --help
python scripts\25_make_kaggle_repack_public_kernel_output.py --help
```

## 已提交路线复盘

真实提交结果以 `reports/POST_086_REVIEW_20260605.md` 为准。概要如下：

| 序号 | submission_id | 路线 | 模型或 adapter | 可观察调参 / 机制 | public score |
| ---: | --- | --- | --- | --- | --- |
| 1 | 53329563 | Tong/Huikang repack | Huikang v27 风格 adapter | raw repack，结构检查通过但官方失败 | ERROR |
| 2 | 53350464 | Huikang v27 notebook v1 | `huikang/nemotron-adapter` v27 | Kaggle-side raw flat zip | ERROR |
| 3 | 53351317 | Huikang v27 repeat | 同上 | 重复 raw package | ERROR |
| 4 | 53352307 | Huikang v27 normalized | 同上 | 显式 target modules、补 base model path、去零 tensor | ERROR |
| 5 | 53355919 | Kien public output | `kienngx/nvidia-nemotron-training-copy-run-instantly` | public training output repack，LoRA r32，lr1e-4 | 0.63 |
| 6 | 53364584 | Akihiko small adapter | `akihikokatsumata/nemotron-lora-exp1-lr1e4-r32` | CC0 小 adapter，r32，lr1e-4 | 0.50 |
| 7 | 53383735 | Rauffauzan fusion | Huikang v20 -> fusion/SVD | LoRA fusion + SVD rank compression 到 32 | 0.86 |
| 8 | 53384030 | Mirza packaging | `assiabenazzouz/adappter-v32-epoch-5` | packaging route，rank <= 32 | 0.86 |
| 9 | 53384059 | Debatreya/Kien tinker | Kien `triton/tinker-adapter/1` | 直接 zip 已有 adapter 路线 | 0.85 |
| 10 | 53384096 | Taha custom repo | Nemotron base + custom repo | RTX Pro 6000，LoRA r32，seq8192，steps1000，lr2e-4 | 0.86 |
| 11 | 53384098 | Mohamed replay-data | Nemotron base + replay math | RTX Pro 6000，LoRA r32，seq8192，steps1000，lr3.5e-4 | 0.86 |

注意：

- 本仓库没有本地训练这些 0.86 模型。
- 对 #7 到 #11，提交的是公开 Kaggle Notebook output 或公开 adapter 的打包结果。
- 训练超参只记录公开源码或元数据中能确认的内容，未知项不要编造。

## 当前可用命令

刷新提交历史：

```powershell
python scripts\04_query_submissions.py
```

生成今日提交计划：

```powershell
python scripts\22_make_daily_submission_plan.py
```

查看 Kaggle 提交历史：

```powershell
kaggle competitions submissions nvidia-nemotron-model-reasoning-challenge -v
```

下载 leaderboard 快照：

```powershell
kaggle competitions leaderboard nvidia-nemotron-model-reasoning-challenge -d -p logs\leaderboard_YYYYMMDD
```

推送 Kaggle notebook：

```powershell
python scripts\21_push_kaggle_notebook.py --kernel-dir "kaggle_kernels\<目录名>"
```

检查 notebook 状态和输出：

```powershell
kaggle kernels status <user>/<kernel-slug>
kaggle kernels files <user>/<kernel-slug>
kaggle kernels logs <user>/<kernel-slug>
```

远端 notebook output 提交命令形态：

```powershell
kaggle competitions submit nvidia-nemotron-model-reasoning-challenge -k <kernel_id> -f submission.zip -v <version> -m "<message>"
```

只有在 `DAILY_SUBMISSION_PLAN.md` 允许时才考虑真实提交。

## 目录说明

```text
configs/          比赛、提交策略、baseline、proxy eval 配置
scripts/          阶段脚本；真实提交脚本必须受 gate 控制
src/nemotron086/  共享 Python 模块
kaggle_kernels/   Kaggle-side repack notebook 项目，不含 output zip
reports/          主要事实源和复盘文档
logs/             Kaggle CLI 输出、score.db、leaderboard 快照
artifacts/        本地生成物；不应提交大文件
external/         外部缓存；不应提交权重或大包
secrets/          本地密钥目录；不提交
```

`.gitignore` 应继续保护：

```text
.env
kaggle.json
secrets/
artifacts/
external/*/weights/
*.safetensors
*.bin
*.pt
*.pth
logs/*.db
logs/*.jsonl
__pycache__/
```

## 下一步建议

当前已经复现 `0.86`，但没有突破 `0.87`。下一步只推荐一个方向：

```yaml
NEXT_ACTION:
  status: audit_next_tier
  action: "审计并验证一个公开 0.87+ 或 0.89 路线，再进入下一次提交窗口"
  reason: "当前 0.86 已进入大平台区，继续重复 0.86 包没有实际收益。"
```

执行前先确认：

```powershell
python scripts\04_query_submissions.py
python scripts\22_make_daily_submission_plan.py
```

如果当天剩余额度为 `0`，只允许做审计、脚本、notebook 准备和报告，不允许提交。

## 给新 Agent 的最短指令

如果你是新 agent，只做下面这些：

1. 运行 `git status -sb`，确认工作区状态。
2. 运行 `python scripts\04_query_submissions.py`。
3. 运行 `python scripts\22_make_daily_submission_plan.py`。
4. 读 `reports/POST_086_REVIEW_20260605.md` 和 `reports/DAILY_SUBMISSION_PLAN.md`。
5. 不要提交，除非日计划明确允许且用户明确要求。
6. 下一步优先找 `0.87+` 真实路线，不要重复 Huikang v27 或低分 adapter。
