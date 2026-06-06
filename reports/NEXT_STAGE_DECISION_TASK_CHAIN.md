# 下一阶段决策与任务链

## 当前基线

- 当前最佳显示分数：`0.86`
- 最新 public rank：`393`
- leaderboard 快照：`logs/leaderboard_20260606/nvidia-nemotron-model-reasoning-challenge.zip`
- `0.86` 档位当前覆盖 rank `19` 到 `1398`，总计 `1380` 队
- 今日可用提交额度：`5`
- 自动提交：`禁止`

## 核心判断

这阶段不再追逐 `0.86/0.87` 标签本身，只看一件事：新候选是否有机会把 rank 从 `393` 往前推。  
workflow 已经够用，后续只做候选筛选、单变量调优判断和远端 repack 准备，不再继续折腾提交流程。

## 候选排序

1. `hammadfarooq470/agi-for-medal-0-87`
   当前首选。理由是有真实 output、机制独立、代码里明确是 Huikang v20 上做 `block_topk floor4 + forced rank 32` 压缩，不是我们昨天 0.86 路线的重复源。
2. `kuangyicheng/nemotron-087-training`
   第二顺位。它不是简单 repack，而是 `huikang v27 warmstart + synthetic data + 240 steps finetune`。上限可能更高，但训练链更重，优先级略低于 Hammad 的直接 output 路线。
3. `dedquoc/nvidia-nmrc-low-rank-svd-lora-adapter-fusion`
   作为 fallback 保留。机制是 QR-trick SVD fusion，值得留作不同机制候选，但缺少比 `0.86` 更强的公开结果证据。
4. `cocoaai/nvidia-nemotron-huikang-0-87-svd-submit`
   降权。它更像 Hammad 家族的衍生 repack，不适合作为第一独立候选。

## 单变量调优方向

### Hammad 路线

- 主变量只改 `candidate spec`
- 可选单变量：
  - `block_topk_floor4_model`
  - `block_topk_floor4_x_bias_model`
  - `block_topk_floor4_model_no_lm_head`
  - `dense_svd_model`
- 规则：
  - 一次只换一个 candidate spec
  - 每次都记录新 hash 和 source kernel version
  - 没有官方结果前，不开第二条同家族变体

### Kuang 路线

- 只作为第二阶段调优方向
- 可选单变量：
  - `learning_rate`: `2e-4 -> 2.5e-4` 或 `3e-4`
  - `max_steps`: `240 -> 320`
  - synthetic/train mix ratio
- 规则：
  - 不本地训练 30B
  - 只有在 Hammad 无提升或报结构兼容问题时，才切到这条线

## 本轮执行链

1. 固化 rank-first 候选审计
2. 使用现有脚本生成 `hammad` 的 Kaggle-side repack notebook
3. 不 push 旧候选，不重提旧 `0.86`
4. push 新 notebook 前先看 `STAGE6_SUBMIT_GATE_hammad_agi_for_medal_087.md`
5. 只有 output 确认存在 `submission.zip` 后，才考虑人工提交
6. 提交后只用 `rank < 393` 判定是否有效

## 当前最推荐动作

```yaml
NEXT_ACTION:
  status: check_hammad_output
  action: "kaggle kernels status muelsyse111/nemotron-repack-hammad-087 ; kaggle kernels files muelsyse111/nemotron-repack-hammad-087"
  reason: "Hammad 的 repack notebook 已经 push，下一步只剩确认 Kaggle Output 是否生成 submission.zip。"
```
