# NVIDIA Nemotron 比赛最终复盘 2026-06-16

本报告修正上一版复盘的主对象：上一版把 `Biohack v62` 当作重点最高包复盘，这是错的。用户明确指出需要复盘的是 Kaggle UI 截图中 public 和 private 两列都显示 `0.86` 的那次提交：

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
- 6 月 5 日 remote output sweep: `reports/REMOTE_086_SUBMISSION_SWEEP_20260605.md`
- 0.86 阶段复盘: `reports/POST_086_REVIEW_20260605.md`
- Mirza v16 notebook source: `artifacts/stage6/mirzayasir_best_086_meta/best-nvidia-nemotron-notebook-0-86.ipynb`
- Mirza v16 metadata: `artifacts/stage6/mirzayasir_best_086_meta/kernel-metadata.json`
- Kaggle CLI historical logs: `logs/submissions_raw_20260605.txt` 至 `logs/submissions_raw_20260609.txt`
- Kaggle CLI top leaderboard snapshot: `logs/leaderboard_show_20260616.csv`
- Downloaded public leaderboard: `reports/leaderboard_20260616/nvidia-nemotron-model-reasoning-challenge-publicleaderboard-2026-06-16T01_57_45.csv`
- 我方公开榜行: `reports/leaderboard_20260616/our_team_publicleaderboard.json`

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

这里的 `0.86` 是平台显示分数，不代表所有 0.86 内部排序完全一致。用户后续复盘应继续以 Kaggle UI 的最终 public/private 显示和最终排名为准。

## 正确复盘对象：Mirza v16 双 0.86 包

### 提交身份

```yaml
submission_id: 53384030
date: 2026-06-05 06:58:51
message: 20260605_slot4_mirzayasir_best_086_v16_remote_output
status: COMPLETE
source_kernel: mirzayasirabdullah07/best-nvidia-nemotron-notebook-0-86
source_version: 16
source_title: "Best NVIDIA Nemotron Notebook | 0.86"
adapter_dataset: assiabenazzouz/adappter-v32-epoch-5
local_notebook: artifacts/stage6/mirzayasir_best_086_meta/best-nvidia-nemotron-notebook-0-86.ipynb
local_metadata: artifacts/stage6/mirzayasir_best_086_meta/kernel-metadata.json
score_evidence:
  local_cli_public: 0.86
  final_ui_public_displayed: 0.86
  final_ui_private_displayed: 0.86
```

### Notebook 实际做了什么

本地保存的 v16 notebook 很短，主要是一个 Kaggle 端打包 notebook，而不是训练 notebook。

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

它的有效工作是：

1. 从公开 dataset `assiabenazzouz/adappter-v32-epoch-5` 取 adapter。
2. 固定读取 `/kaggle/input/datasets/assiabenazzouz/adappter-v32-epoch-5/adapter`。
3. 只把 `adapter_config.json` 和 `adapter_model.safetensors` 两个文件写入 `/kaggle/working/submission.zip`。
4. zip 根目录是平铺结构，没有把父目录套进去。
5. 不训练、不加载 base model、不推理、不改 adapter 权重。

Notebook markdown 里写了 rank 校验、自动发现 adapter、zip 内复核等更完整的流程说明；但本地保存的实际执行代码是上面这种最小打包实现。因此不能把它描述成复杂训练或复杂验证路线。

## 这次提交的策略和优化策略

这次最高包的关键不是模型调参，而是工程选择和资产选择。

### 1. 选对已有公开 adapter

`adappter-v32-epoch-5` 是这次提交真正承载分数的资产。Mirza v16 notebook 本身没有训练，它只是把这个 adapter 重新包装成比赛要求的 `submission.zip`。

这说明当时最有效的决策是：

```text
不要继续盲修 Huikang v27 ERROR 包
不要本地上传 1GB+ zip
不要本地训练或加载 30B
直接复用已经能产出 0.86 的公开 adapter notebook output
```

### 2. 使用 remote kernel output submit，避免本地大包上传

当时真正突破工程瓶颈的是这个提交方式：

```powershell
kaggle competitions submit nvidia-nemotron-model-reasoning-challenge `
  -k mirzayasirabdullah07/best-nvidia-nemotron-notebook-0-86 `
  -f submission.zip `
  -v 16 `
  -m "20260605_slot4_mirzayasir_best_086_v16_remote_output"
```

它的价值：

- 不需要把 1GB 以上的 `submission.zip` 下载到本地再上传。
- 避免本地网络/VPN 导致的上传超时。
- 直接提交 Kaggle notebook version 16 的云端 output，减少本地重打包引入的格式漂移。
- 保留公开 notebook 产出的原始包结构，降低官方 evaluator ERROR 风险。

### 3. 保持提交包极简

该包只包含：

```text
submission.zip
  adapter_config.json
  adapter_model.safetensors
```

没有额外目录、训练日志、manifest、缓存文件或 notebook 输出杂物。这种极简结构符合比赛 adapter 提交习惯，也避免了 evaluator 读取路径时失败。

### 4. 不改权重，避免把公开强包改坏

后续我们做过很多 SVD、TIES、DARE、delta scaling、module filtering、训练变体，但大多数只到 0.84-0.85，甚至更低。Mirza v16 这包的优势在于它没有试图二次修改 adapter，而是完整保留公开强 adapter 的行为。

复盘结论：

```yaml
main_strategy: "public strong adapter preservation"
main_engineering_optimization: "Kaggle remote-output submit"
main_packaging_optimization: "flat two-file adapter zip"
main_model_optimization: "none in our workflow; score comes from selected public adapter"
why_it_worked: "选中的公开 adapter 已经有效，远端 output 提交避免了本地重打包和上传风险。"
```

## 为什么上一版复盘错到了 Biohack v62

上一版报告把 `Biohack v62` 当作最高重点，是因为它依赖赛后 CLI 中已经显示 `privateScore` 的较新提交记录：

```yaml
biohack_v62:
  submission_id: 53696351
  message: 20260615_wrap_biohack_v62_public_sparse_trust_probe
  publicScore: 0.86
  privateScore_from_cli: 0.85
```

这个判断对“Biohack v62 是后期一个 public 0.86 / private 0.85 的有效路线”是成立的，但它不是用户截图中要求复盘的双 0.86 包。用户截图的目标行是：

```yaml
target:
  submission_id: 53384030
  message: 20260605_slot4_mirzayasir_best_086_v16_remote_output
  public_displayed_score: 0.86
  private_displayed_score: 0.86
```

因此修正后的主复盘对象必须是 Mirza v16，而不是 Biohack v62。

## 与其他路线的对比

| 路线 | 提交/结果 | 复盘结论 |
|---|---:|---|
| Huikang v27 raw / normalized | ERROR | 结构验证通过不代表官方 evaluator 能接受 |
| Kien public training output repack | public 0.63 | 公开训练输出不等于强 adapter |
| Akihiko small adapter | public 0.50 | 小型公开 LoRA 虽合法但不具竞争力 |
| Rauffauzan fusion/rank compression | public 0.86 | fusion/SVD 能到 0.86，但未证明优于 Mirza 双 0.86 包 |
| Mirza v16 adapter packaging | public 0.86 / private 0.86 displayed | 本报告重点；公开强 adapter + 远端 output 提交 |
| Debatreya direct Kien adapter route | public 0.85 | 快速但低于 Mirza |
| Taha custom repo finetune | public 0.86 | 训练路线可到 0.86，但训练成本和不确定性更高 |
| Mohamed replay-data finetune | public 0.86 | replay data 路线可到 0.86，但不是本次双 0.86 目标包 |
| Biohack v62 public sparse-trust probe | public 0.86 / private 0.85 | 后期有效路线，但不是用户截图指定的双 0.86 包 |

## 第一阶段到最终提交的关键决策

### Stage 1：先建立最小闭环

正确点：

- 先修 Kaggle CLI 认证和提交历史查询。
- 正确处理 `No submissions found`。
- 先做 adapter validator 和 submission packer。
- 不训练、不提交、不下载 base model。

这使后续每个 adapter 至少能检查基本结构，而不是盲目提交。

### Stage 2：从“本地大包上传”切到“Kaggle 云端 output”

本地上传 1GB+ `submission.zip` 太慢且易失败。Kaggle-side notebook 和 remote output submit 让我们可以直接提交 notebook output。

这是整个项目最重要的工程转折点。

### Stage 3：proxy eval 被降级

Kaggle Notebook 上跑 Nemotron 30B + Mamba/CUDA proxy inference 容易失败。后续判断分数主要依赖官方 evaluator，而不是继续卡在本地或 notebook proxy。

### Stage 5/6：一天内验证多个公开 output

6 月 5 日的 remote sweep 一次验证了多条公开路线：

| submission_id | route | public |
|---|---|---:|
| 53383735 | Rauffauzan fusion/rank compression | 0.86 |
| 53384030 | Mirza v16 adapter packaging | 0.86 |
| 53384059 | Debatreya direct Kien adapter | 0.85 |
| 53384096 | Taha custom repo finetune | 0.86 |
| 53384098 | Mohamed replay data finetune | 0.86 |

其中用户截图指定的最终双 0.86 复盘对象是 `53384030`。

## 这次双 0.86 包给出的经验

1. 对只提交 adapter 的比赛，资产选择比本地复杂 workflow 更重要。
2. 公开强 adapter 不应轻易二次修改；很多“看起来高级”的 merge/compression 会把分数打低。
3. remote-output submit 是比本地上传大 zip 更稳定的提交方式。
4. `submission.zip` 应保持最小结构：根目录直接放 `adapter_config.json` 和 `adapter_model.safetensors`。
5. 复盘时必须把“notebook 做了什么”和“adapter 本身来自哪里”分开。Mirza notebook 做的是打包，分数来自 `adappter-v32-epoch-5`。
6. 最终报告不能只看后期 CLI privateScore 列，还要对齐用户在 Kaggle UI 中指定的具体提交行。

## 给队长的交接信息

优先审查这个目录：

```text
artifacts/stage6/mirzayasir_best_086_meta/
```

本地打开 notebook：

```powershell
code artifacts/stage6/mirzayasir_best_086_meta/best-nvidia-nemotron-notebook-0-86.ipynb
```

关键远端信息：

```yaml
kernel: mirzayasirabdullah07/best-nvidia-nemotron-notebook-0-86
version: 16
dataset: assiabenazzouz/adappter-v32-epoch-5
submission_message: 20260605_slot4_mirzayasir_best_086_v16_remote_output
```

可复查提交命令形态：

```powershell
kaggle competitions submit nvidia-nemotron-model-reasoning-challenge `
  -k mirzayasirabdullah07/best-nvidia-nemotron-notebook-0-86 `
  -f submission.zip `
  -v 16 `
  -m "20260605_slot4_mirzayasir_best_086_v16_remote_output"
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

本次应该复盘的 public/private 双 0.86 包是 `Mirza v16`：

```yaml
final_review_target:
  submission_id: 53384030
  message: 20260605_slot4_mirzayasir_best_086_v16_remote_output
  public_displayed_score: 0.86
  private_displayed_score: 0.86
  strategy: "use a proven public adapter dataset and submit the exact Kaggle notebook remote output"
  optimization: "preserve adapter weights, keep zip flat and minimal, avoid local upload/repack drift"
  not_training: true
  not_fusion: true
  not_local_30b: true
```

上一版 Biohack v62 复盘应降级为“后期对照路线”，不能再作为本报告主对象。
