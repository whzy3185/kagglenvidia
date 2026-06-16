# NVIDIA Nemotron 比赛最终复盘 2026-06-16

本报告基于 GitHub 远端 `origin/main` 已提交内容复盘，不把本地未提交的 Stage10 草稿当作正式结论。核心结论：最终需要重点复盘的是 Kaggle UI 截图中 public 和 private 两列都显示 `0.86` 的那次提交。

```yaml
target_submission:
  submission_id: 53384030
  title: "Best 0.86 | NVIDIA Nemotron Notebook - Version 16"
  owner: muelsyse111
  message: 20260605_slot4_mirzayasir_best_086_v16_remote_output
  status: Complete
  public_displayed_score: 0.86
  private_displayed_score: 0.86
  source_kernel: mirzayasirabdullah07/best-nvidia-nemotron-notebook-0-86
  source_version: 16
  source_adapter_dataset: assiabenazzouz/adappter-v32-epoch-5
```

说明：本地 6 月 5 日至 6 月 9 日的 Kaggle CLI 日志只记录到该提交的 `publicScore=0.86`，当时 `privateScore` 字段为空；赛后用户提供的 Kaggle UI 截图显示该行两个分数列均为 `0.86`。因此本报告以本地日志确认提交身份和 public 分数，以赛后 UI 截图确认 public/private 双 0.86 显示。

## 数据来源

- 赛后 Kaggle UI 截图：`Best 0.86 | NVIDIA Nemotron Notebook - Version 16`，message 为 `20260605_slot4_mirzayasir_best_086_v16_remote_output`，两个显示分数列均为 `0.86`
- `reports/STAGE1_DRY_RUN.md`
- `reports/ASSET_AUDIT.md`
- `reports/PUBLIC_BASELINE_REPRO_STATUS.md`
- `reports/STAGE2_BASELINE_DECISION.md`
- `reports/STAGE2_REPRO_REPORT.md`
- `reports/STAGE3_COMPLETION_REPORT.md`
- `reports/STAGE3_STAGE4_HANDOFF.md`
- `reports/STAGE4_READINESS.md`
- `reports/STAGE4_CANDIDATE_PLAN.md`
- `reports/KAGGLE_SIDE_NOTEBOOK_WORKFLOW.md`
- `reports/REMOTE_086_SUBMISSION_SWEEP_20260605.md`
- `reports/POST_086_REVIEW_20260605.md`
- `reports/STAGE7_OPEN_SOURCE_REPO_MINING.md`
- `reports/STAGE7_REFERENCE_SUBMISSION_LIST.md`
- `reports/STAGE8_SUBMISSION_RUN_20260608.md`
- `reports/SCORECARD.md`
- `reports/leaderboard_20260616/our_team_publicleaderboard.json`
- Mirza v16 notebook: `artifacts/stage6/mirzayasir_best_086_meta/best-nvidia-nemotron-notebook-0-86.ipynb`
- Mirza v16 metadata: `artifacts/stage6/mirzayasir_best_086_meta/kernel-metadata.json`

## Leader 信息

比赛结束后本地保存的 `leaderboard --show` 前排信息如下：

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

下载到本地的 public leaderboard 中，我方队伍为：

```yaml
team_name: "你跑不过我你信吗"
rank_in_downloaded_publicleaderboard: 422
score: 0.86
submission_count: 132
members: "blacklions,llccqq624,llllllc666,muelsyse111,xiangjiangzhou"
```

## 我们是不是只交了一个开源内容

不是“整个项目只交了一个开源内容”。GitHub 上记录显示，我们经历了多个阶段：

- 复现和提交了多个公开 Kaggle output。
- 生成了多个 Kaggle-side repack notebook。
- 设计并上传了多条自研或半自研训练/融合 notebook。
- 后续提交过 SVD、TIES、DARE、Muon、replay、module selection 等不同机制候选。

但如果只看本报告目标包 `53384030`，它本质上是一次公开内容复现提交：

```yaml
best_target_package_nature:
  original_adapter_source: "public Kaggle dataset"
  adapter_dataset: "assiabenazzouz/adappter-v32-epoch-5"
  packaging_notebook_source: "public Kaggle notebook"
  packaging_notebook: "mirzayasirabdullah07/best-nvidia-nemotron-notebook-0-86"
  version: 16
  our_work: "select source, verify route, submit exact remote notebook output, record provenance and score"
  our_training: false
  our_weight_modification: false
```

也就是说：这次双 0.86 包的权重不是我们训练出来的；我们做的是识别、验证、选择并提交一个公开 Kaggle notebook 生成的 adapter submission output。它的开源/公开来源是：

```text
Kaggle Notebook:
  mirzayasirabdullah07/best-nvidia-nemotron-notebook-0-86
  Version 16

Kaggle Dataset:
  assiabenazzouz/adappter-v32-epoch-5
  adapter/
    adapter_config.json
    adapter_model.safetensors
```

## 目标包实际做了什么

本地保存的 v16 notebook 是一个极简 Kaggle 端打包 notebook，而不是训练 notebook。

第一段代码：

```python
import kagglehub

path = kagglehub.dataset_download("assiabenazzouz/adappter-v32-epoch-5")
print("Path to dataset files:", path)
```

第二段代码：

```python
import os, zipfile, json

ADAPTER_DIR = '/kaggle/input/datasets/assiabenazzouz/adappter-v32-epoch-5/adapter'
zip_path = '/kaggle/working/submission.zip'

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for fname in ["adapter_config.json", "adapter_model.safetensors"]:
        fpath = os.path.join(ADAPTER_DIR, fname)
        if os.path.exists(fpath):
            zf.write(fpath, fname)
            print(f"Added: {fname}")
        else:
            print(f"Missing: {fname}")
```

实际动作：

1. 从公开 Kaggle dataset 获取 adapter。
2. 读取 `adapter_config.json` 和 `adapter_model.safetensors`。
3. 生成 `/kaggle/working/submission.zip`。
4. zip 根目录直接包含两个 adapter 文件。
5. 不训练、不加载 base model、不推理、不改权重。

## 为什么这次提交有效

关键不是模型调参，而是工程策略正确：

1. 及时停止继续修复官方评测失败的早期 adapter 包。
2. 选择已经有公开 0.86 证据的 Kaggle notebook output。
3. 使用 remote kernel output submit，避免本地下载和上传 1GB+ 大包。
4. 不二次修改 adapter 权重，避免把公开强包改坏。
5. 保持 zip 结构最小化，只包含比赛 evaluator 需要的两个文件。

对应提交命令形态：

```powershell
kaggle competitions submit nvidia-nemotron-model-reasoning-challenge `
  -k mirzayasirabdullah07/best-nvidia-nemotron-notebook-0-86 `
  -f submission.zip `
  -v 16 `
  -m "20260605_slot4_mirzayasir_best_086_v16_remote_output"
```

## 全 Stage 复盘

### Stage 1：资产审计与最小闭环

状态：完成。

证据：

```yaml
kaggle_cli_status: success
submission_history_query_status: success
raw_submission_result: "No submissions found"
today_submission_count: 0
today_remaining_quota: 5
candidate_adapters: 0
submission_zip_generated: false
can_enter_stage2: true
```

关键决策：

- 先修 Kaggle CLI 和 submission history 查询。
- 正确把 `No submissions found` 当成认证成功但无历史提交，而不是失败。
- 建立 adapter validator、submission packer、dry-run report。
- 不训练、不提交、不下载 base model。

评价：这是正确的。它避免一开始就把工程变成不可控的大训练平台。

### Stage 2：公开 adapter 获取与结构验证

状态：结构闭环完成，官方格式未在此阶段确认。

GitHub 记录中选择过：

```yaml
selected_route: tong_full_repro
classification: candidate_adapter
source_url: https://www.kaggle.com/models/huikang/nemotron-adapter
model_version_ref: huikang/nemotron-adapter/Transformers/default/27
```

Stage 2 结果：

```yaml
fetch_status: success
adapter_config_exists: true
adapter_model_exists: true
structural_valid: true
rank_lte_32: true
safetensors_opened: true
submission_zip_generated: true
official_format_confirmed: false
```

关键教训：结构有效不等于官方评测有效。后面早期包多次失败，说明 evaluator 兼容性必须通过真实官方评测确认。

### Stage 3：proxy eval

状态：框架存在，但未完成。

GitHub 报告结论：

```yaml
stage: 3
status: blocked
complete: false
reason: "proxy predictions are missing or incomplete"
proxy_samples: 25
can_enter_stage4: false
```

关键教训：

- 本地和 Kaggle Notebook 上跑完整 Nemotron 30B 推理链不稳定。
- proxy eval 只能作为辅助门控，不能替代官方 evaluator。
- 对这个比赛，官方提交分数才是最终判断。

### Stage 4：fusion / specialist / daily plan

状态：只完成 readiness 和候选计划，未正式展开执行。

GitHub 报告结论：

```yaml
can_start_stage4: false
validated_adapters: 1
proxy_eval_complete: false
score_gate_allowed: true
blocked_reason: proxy_eval_not_complete
```

候选方向包括 compressed trace、numeric/unit conversion、cipher、bit operation、rank32 fusion。但由于 proxy eval 未完成，正式 Stage 4 应被视为 blocked。

评价：这个阶段的边界控制是正确的。没有在缺少 proxy eval 的情况下直接把 fusion/daily runner 做成自动盲提系统。

### Stage 5：Kaggle-side notebook workflow

状态：完成，并成为关键工程突破。

目的：

- 本地不再上传大型 `submission.zip`。
- 本地只上传小 notebook。
- Kaggle 云端挂载公开 adapter 或 notebook output。
- 最终通过 Kaggle output 生成或直接提交 `submission.zip`。

核心价值：

```yaml
local_large_zip_upload: false
base_model_downloaded_locally: false
remote_kernel_output_submit: true
```

评价：这是整个项目最重要的工程转折。没有这个切换，很难高频验证多个公开 output。

### Stage 6：公开 output 扫描与 0.86 平台确认

状态：完成。

2026-06-05 remote sweep：

| submission_id | route | kernel | version | public |
|---|---|---|---:|---:|
| 53383735 | Rauffauzan fusion/rank compression | `muelsyse111/nemotron-repack-rauffauzan-fusion` | 1 | 0.86 |
| 53384030 | Mirza adapter packaging | `mirzayasirabdullah07/best-nvidia-nemotron-notebook-0-86` | 16 | 0.86 |
| 53384059 | Debatreya direct adapter route | `debatreyabiswas/nemotroncomp-best-0-86-solution-nvidia-under-5min` | 1 | 0.85 |
| 53384096 | Taha custom repo finetune | `tahaalam2009/end-to-end-finetuning-for-lb-0-86-custom-repo` | 6 | 0.86 |
| 53384098 | Mohamed replay data finetune | `mohamedamr992/nemotron-replay-data-0-86` | 4 | 0.86 |

关键结论：

- 我们不是只发现一个 0.86，而是验证了多个公开 0.86 路线。
- 但截图中 public/private 双 0.86 的目标包是 `53384030`。
- 当时最有价值的不是盲目训练，而是确认 remote-output submit 是有效路线。

### Stage 7：激进 rank-push 探索

状态：执行过大量探索，但没有超过 0.86。

GitHub 记录的主要来源：

- `tonghuikang/nemotron`
- Mohamed replay-data notebook
- Taha custom repo notebook
- Rauffauzan LoRA fusion/rank compression notebook
- Hugging Face PEFT model merging
- MergeKit
- LoRAHub
- NVIDIA OpenMathReasoning
- OpenR1-Math-220k
- NuminaMath-CoT
- Muon optimizer
- TIES / DARE / Task Arithmetic / Model Soups / LoRA / QLoRA 相关论文

Stage 7 输出了多条结构有效候选，包括：

- protected rehearsal
- delta-space SVD rank32
- modulewise delta SVD
- full-epoch Muon
- Mamba in-projection specialist
- weak-protected curriculum
- norm-balanced delta SVD
- seed-stability replay
- TIES sign merge
- DARE merge
- layerwise adapter soup

评价：

- 方法覆盖面足够广。
- 很多候选是我们基于公开论文/代码思路改造的，不是简单复投。
- 但官方结果显示，大多数自研/融合/训练候选没有超过已知公开 0.86 包。
- 对这个比赛，改动越大越容易破坏已有 adapter 的稳定性。

### Stage 8：后续提交验证

状态：执行过，未改善。

2026-06-08 五次提交：

| slot | candidate | mechanism | public | decision |
|---:|---|---|---:|---|
| 1 | guarded weak replay | guarded weak-category replay | 0.84 | reject |
| 2 | answer-tail 512 | answer-tail loss focus | 0.27 | hard reject |
| 3 | weak-protected curriculum | weak/protected interleaving | 0.85 | reject |
| 4 | seed-stability replay | deterministic replay | 0.85 | reject |
| 5 | TIES sign merge | TIES sign merge | 0.84 | reject |

关键结论：

- answer-tail objective 是明显破坏性方向。
- replay 排序和 weak/protected reweighting 没有突破 0.86。
- TIES 类合并没有带来提升。
- GPU quota 成为后续运行瓶颈。

## 最重要的决策复盘

### 正确决策

1. 先完成 CLI、审计、验证、打包闭环。
2. 不在本地加载或训练 30B。
3. 从本地大包上传切换到 Kaggle remote-output submit。
4. 迅速验证多个公开 output，而不是只盯一个失败包。
5. 对每次提交保留 message、kernel、version、source chain。
6. 对低分路线及时 reject，不重复提交。

### 错误或低效决策

1. 早期对结构有效包的官方兼容性过于乐观。
2. proxy eval 投入较多，但没有形成可靠分数预测。
3. 后期 fusion/SVD/merge 方向投入较多，但官方分数没有突破。
4. 训练目标改动过激时容易崩盘，例如 answer-tail loss focus。
5. 一些标题声称高分的公开 notebook 实测不高，说明 title claim 不能作为决策依据。

## 最终技术结论

1. 目标双 0.86 包不是我们训练出来的模型，而是公开 Kaggle adapter 包装路线。
2. 权重来源是 `assiabenazzouz/adappter-v32-epoch-5`。
3. 打包 notebook 来源是 `mirzayasirabdullah07/best-nvidia-nemotron-notebook-0-86` Version 16。
4. 我们的关键贡献是工程化选择、提交路径设计、失败路线筛除、分数记录和复盘。
5. 项目后续自研探索有价值，但没有超过这个公开强包。
6. 对这类只提交 LoRA adapter 的比赛，最稳策略是先锁定强公开 adapter/output，再谨慎做极小变量改动；大规模 merge 或 objective 改动风险很高。

## 给队长的交接信息

优先审查：

```text
artifacts/stage6/mirzayasir_best_086_meta/
reports/REMOTE_086_SUBMISSION_SWEEP_20260605.md
reports/POST_086_REVIEW_20260605.md
reports/SCORECARD.md
reports/FINAL_COMPETITION_REVIEW_20260616.md
```

本地打开目标 notebook：

```powershell
code artifacts/stage6/mirzayasir_best_086_meta/best-nvidia-nemotron-notebook-0-86.ipynb
```

目标提交来源链：

```yaml
competition: nvidia-nemotron-model-reasoning-challenge
submission_id: 53384030
message: 20260605_slot4_mirzayasir_best_086_v16_remote_output
source_kernel: mirzayasirabdullah07/best-nvidia-nemotron-notebook-0-86
source_version: 16
adapter_dataset: assiabenazzouz/adappter-v32-epoch-5
local_notebook_copy: artifacts/stage6/mirzayasir_best_086_meta/best-nvidia-nemotron-notebook-0-86.ipynb
```

不要提交到 GitHub：

```text
submission.zip
adapter_model.safetensors
kaggle.json
任何 token 或大模型权重
```

可以提交到 GitHub：

```text
notebook 源码
kernel-metadata.json
复盘报告
CLI 日志摘要
leaderboard 摘要
```

## 最终结论

```yaml
final_review_target:
  submission_id: 53384030
  message: 20260605_slot4_mirzayasir_best_086_v16_remote_output
  public_displayed_score: 0.86
  private_displayed_score: 0.86
  route_type: public_adapter_repack
  adapter_source: assiabenazzouz/adappter-v32-epoch-5
  notebook_source: mirzayasirabdullah07/best-nvidia-nemotron-notebook-0-86
  source_version: 16
  our_training: false
  our_weight_modification: false
  our_real_contribution: "source selection, remote-output submission workflow, validation records, and failure-route elimination"
```
