# Stage 7 Open Source Repo Mining

## Current Goal

- Current rank: 393 from latest local leaderboard snapshot; user task baseline was 399, but local refresh shows the best rank has moved to 393.
- Current best displayed score: 0.86.
- Target rank: <100.
- Main metric: public rank delta, not displayed 0.86/0.87 labels.
- Today submission status: 3 counted submissions, 2 remaining by CLI parse, but no submission is made in this task.

## Search Scope

- Kaggle: competition kernels, model list, dataset list, public output history.
- GitHub: Nemotron repo, PEFT/adapter merging repositories, mergekit, LoRAHub.
- Hugging Face: PEFT docs, OpenMathReasoning, OpenR1-Math-220k, NuminaMath-CoT.
- Papers: TIES, DARE, Task Arithmetic, QLoRA, DoRA, LoRAHub, model soup family.

## Current Submission Evidence

| Submission | Source | Public score | Result |
|---|---|---:|---|
| `53416566` | Hammad public output repack | 0.85 | worse than best |
| `53416809` | Dedquoc SVD fusion output repack | 0.78 | worse than best |
| `53417126` | Kuang training output repack | 0.63 | worse than best |
| `53384098` | Mohamed replay-data output | 0.86 | current best family |
| `53384096` | Taha custom repo output | 0.86 | current best family |
| `53384030` | Mirza 0.86 output | 0.86 | current best family |
| `53383735` | Rauffauzan fusion output | 0.86 | current best family |

Conclusion: public output repacks are no longer enough. The next candidate must create a new adapter hash through one real variable: fusion algorithm/weights, training LR, or data mix.

## High-Value Sources Found

| Priority | Source | Type | Method | Why relevant | Next experiment |
|---|---|---|---|---|---|
| P0 | `keithtyser/nemotron-086-adapters-20260605` | Kaggle model adapter anchors | six rank-32 0.86-class adapter anchors | Best immediate base for real fusion; CLI shows six READY instances around 3.55GB each | Kaggle-side inventory notebook, then one TIES/DARE/SVD rank32 merge |
| P1 | `mohamedamr992/nemotron-replay-data-0-86` | Kaggle training route | replay data / SFT | Our submitted output scored 0.86; a single LR delta may move inside 0.86 plateau | Kaggle GPU training variant with lr=3e-4 |
| P1 | `tahaalam2009/end-to-end-finetuning-for-lb-0-86-custom-repo` | Kaggle training route | custom repo / replay mix | Our submitted output scored 0.86; data-mix change is distinct from LR sweep | One replay/hard-case ratio or sample-order variant |
| P1 | `rauffauzanrambe/lora-adapter-fusion-and-rank-compression-pipeline` | Kaggle fusion code | adapter fusion + SVD rank compression | Prior family reached 0.86; useful as code path if source adapters/weights change | Weighted fusion using verified 0.86 anchors |
| P1 | Hugging Face PEFT model merging | library docs | `add_weighted_adapter`, linear/SVD/TIES/DARE | Directly maps to LoRA adapter merge variants | Implement tensor-safe adapter merge without local base load |
| P2 | `tonghuikang/nemotron` | GitHub training repo | public SFT/corpus/loss/schedule code | Canonical code reference for training variants | Port one loss-mask or LR variant to Kaggle GPU |
| P2 | NVIDIA OpenMathReasoning | HF dataset | 5.68M reasoning rows, CoT/TIR/GenSelect | Useful for small filtered data-mix variants | Add a small hard numeric/symbolic slice to known 0.86 route |
| P2 | OpenR1-Math-220k | HF dataset | verified reasoning traces | Useful for answer-format-stable training subset | Filter short verified traces and normalize final answers |
| P2 | NuminaMath-CoT | HF dataset | math CoT dataset | Useful for curriculum/data mix, not direct submit | Small curriculum subset mixed into Mohamed/Taha |
| P3 | TIES / DARE / Task Arithmetic papers | paper methods | interference-reduced delta merge | Method references for adapter tensor merge | Apply to adapter A/B tensors with rank<=32 gate |

## Rejected / Low-Value Sources

| Source | Reason |
|---|---|
| Hammad `agi-for-medal-0-87` public output | Already submitted by us, scored 0.85. Do not repeat. |
| Dedquoc SVD fusion public output | Already submitted by us, scored 0.78. Code may be useful, output is not. |
| Kuang `nemotron-087-training` public output | Already submitted by us, scored 0.63. Do not repeat public output. |
| CocoaAI `huikang 0.87 svd submit` | Same SHA256 as Hammad output. Duplicate hash. |
| Kien/Akihiko families | Previously low scores around 0.63/0.50 without a new mechanism. |
| Title-only 0.87 notebooks | Notebook title/claim was proven unreliable by Stage 7 submissions. |
| DoRA direct submission | Potentially useful training idea, but official adapter format compatibility is not proven. |
| LoRAHub direct leaderboard search | Requires proxy objective; using public leaderboard as mixture optimizer would be unsafe. |

## Top 5 Actionable Leads

1. `keithtyser_anchor_ties_svd_rank32`
   - Use Kaggle model anchors, inspect exact files, merge adapters with TIES/DARE or weighted SVD, enforce rank<=32.
   - Candidate score: 27.

2. `mohamed_replay_lr_3e4`
   - Rerun known 0.86 replay-data route with exactly one LR change.
   - Candidate score: 26.

3. `taha_replay_mix_variant`
   - Rerun known 0.86 custom-repo route with one data-mix/order change.
   - Candidate score: 25.

4. `rauffauzan_anchor_weight_065_035`
   - Reuse fusion/rank-compression code but change source anchors and one fusion weight.
   - Candidate score: 24.

5. `mohamed_openmath_5k_mix`
   - Inject a small filtered OpenMath/OpenR1/Numina reasoning slice into a known 0.86 training route.
   - Candidate score: 23, high-risk exploration.

## Recommended Next Candidate

- candidate: `keithtyser_anchor_ties_svd_rank32`
- source: `https://www.kaggle.com/models/keithtyser/nemotron-086-adapters-20260605`
- main change: create a new adapter by merging multiple rank-32 0.86-class anchors using TIES/DARE or weighted SVD, then package a new rank<=32 adapter.
- why it may improve rank: it can create a real behavior delta from multiple 0.86-class anchors without retraining the 30B base and without repeating known failed public outputs.
- risk: current CLI listing shows six READY instances but does not expose exact variation names/files cleanly; a Kaggle-side inventory notebook is required first.
- next action: generate a Kaggle-side inventory-and-merge notebook, push it, verify output files/SHA/rank, then produce a submit confirmation card. Do not submit until user confirms.

## Search Notes

- `kaggle kernels list --competition nvidia-nemotron-model-reasoning-challenge --search "0.86"` surfaced Mohamed, Taha, Mirza, Debatreya, Rauffauzan-adjacent, symbolic, and Unsloth routes.
- `kaggle kernels list --competition nvidia-nemotron-model-reasoning-challenge --search "0.87"` surfaced Hammad, CocoaAI, Kuang, procedural CoT, and task-family-tour routes. The first three are now negative or duplicate evidence from our own submissions.
- `kaggle models list --search "0.86 adapter"` surfaced `keithtyser/nemotron-086-adapters-20260605`.
- `kaggle datasets list --search "nemotron"` and `"reasoning traces"` surfaced Nemotron training data, CoT trajectories, bit-manipulation CoT, Nemotron math filtered data, OpenR1-Math, and AIMO-style reasoning datasets.

## Boundary

This report did not call `kaggle competitions submit`, did not train, did not load the 30B base model, and did not create or commit any safetensors/submission zip/token.
