from __future__ import annotations

import importlib.util
import json
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STAGE7_SCRIPT = PROJECT_ROOT / "scripts" / "27_make_stage7_diverse_notebooks.py"
CONFIG_PATH = PROJECT_ROOT / "configs" / "stage8_tomorrow_submission_packages.yaml"
REPORT_PATH = PROJECT_ROOT / "reports" / "STAGE8_TOMORROW_PACKAGE_PLAN.md"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "STAGE8_TOMORROW_NOTEBOOK_VALIDATION.md"


def load_stage7_module() -> Any:
    spec = importlib.util.spec_from_file_location("stage7_diverse", STAGE7_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {STAGE7_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def target_modules_block(modules: list[str]) -> str:
    inner = "\n".join(f'    "{name}",' for name in modules)
    return f"TARGET_MODULES = [\n{inner}\n]"


BASE_TARGET_MODULES = target_modules_block(
    ["q_proj", "k_proj", "v_proj", "o_proj", "up_proj", "down_proj", "in_proj", "out_proj", "lm_head"]
)


TOMORROW_VARIANTS: list[dict[str, Any]] = [
    {
        "slug": "nemotron-s8-guarded-weak-replay-v1",
        "folder": "nemotron_s8_guarded_weak_replay_v1",
        "title": "Nemotron S8 Guarded Weak Replay V1",
        "mechanism": "guarded_weak_category_replay",
        "hypothesis": "repair weak symbolic/equation categories while explicitly protecting bit, gravity, numeral, and unit-conversion families that can regress",
        "code": r'''
        import csv as _stage8_csv
        _stage8_categories = {}
        with open(TRAIN_CSV_PATH, encoding="utf-8") as _stage8_handle:
            for _stage8_row in _stage8_csv.DictReader(_stage8_handle):
                _stage8_categories[str(_stage8_row.get("id", ""))] = str(
                    _stage8_row.get("category")
                    or _stage8_row.get("problem_type")
                    or _stage8_row.get("type")
                    or "unknown"
                )
        _stage8_weak = {"cryptarithm_deduce", "cryptarithm_guess", "equation_numeric_guess", "symbolic"}
        _stage8_guard = {"bit_manipulation", "gravity", "numeral", "unit_conversion"}
        _stage8_weak_examples, _stage8_guard_examples, _stage8_other_examples = [], [], []
        for _stage8_ex in examples:
            _stage8_cat = _stage8_categories.get(str(_stage8_ex.get("problem_id", "")), "replay_math")
            if _stage8_cat in _stage8_weak:
                _stage8_ex["weights"] = [float(w) * 1.18 for w in _stage8_ex["weights"]]
                _stage8_weak_examples.append(_stage8_ex)
            elif _stage8_cat in _stage8_guard:
                _stage8_ex["weights"] = [float(w) * 1.12 for w in _stage8_ex["weights"]]
                _stage8_guard_examples.append(_stage8_ex)
            else:
                _stage8_other_examples.append(_stage8_ex)
        _stage8_ordered = []
        _stage8_n = max(len(_stage8_weak_examples), len(_stage8_guard_examples))
        for _stage8_i in range(_stage8_n):
            if _stage8_i < len(_stage8_weak_examples):
                _stage8_ordered.append(_stage8_weak_examples[_stage8_i])
            if _stage8_i < len(_stage8_guard_examples):
                _stage8_ordered.append(_stage8_guard_examples[_stage8_i])
        examples = _stage8_ordered + _stage8_other_examples
        print("STAGE8_MECHANISM: guarded weak replay", len(_stage8_weak_examples), len(_stage8_guard_examples), len(_stage8_other_examples))
''',
        "config_replacements": {},
        "sources": [
            "Kaggle discussion 703240",
            "bankoglu/hard-families-cot",
            "continual rehearsal",
        ],
        "expected_fix": "today's protected route scored 0.85, so this variant weakly boosts both weak and guard families instead of protecting only guard families.",
    },
    {
        "slug": "nemotron-s8-answer-tail-512-v1",
        "folder": "nemotron_s8_answer_tail_512_v1",
        "title": "Nemotron S8 Answer Tail 512 V1",
        "mechanism": "answer_tail_512_loss_focus",
        "hypothesis": "preserve reasoning context while concentrating gradient on final answer and decisive tail tokens",
        "code": r'''
        _stage8_tail_tokens = 512
        _stage8_changed = 0
        _stage8_kept_tokens = 0
        for _stage8_ex in examples:
            _stage8_positive = [i for i, w in enumerate(_stage8_ex["weights"]) if float(w) > 0.0]
            if len(_stage8_positive) > _stage8_tail_tokens:
                _stage8_keep = set(_stage8_positive[-_stage8_tail_tokens:])
                _stage8_ex["weights"] = [
                    float(w) if i in _stage8_keep else 0.0
                    for i, w in enumerate(_stage8_ex["weights"])
                ]
                _stage8_changed += 1
                _stage8_kept_tokens += len(_stage8_keep)
        print("STAGE8_MECHANISM: answer tail 512 loss focus", "changed=", _stage8_changed, "kept=", _stage8_kept_tokens)
''',
        "config_replacements": {},
        "sources": [
            "reasoning trace compression",
            "Tong loss_config reference",
            "LoRA paper",
        ],
        "expected_fix": "targets the long-trace over-imitation risk without shortening training or changing the submission format.",
    },
    {
        "slug": "nemotron-s8-attn-mamba-no-lmhead-v1",
        "folder": "nemotron_s8_attn_mamba_no_lmhead_v1",
        "title": "Nemotron S8 Attn Mamba No LMHead V1",
        "mechanism": "attention_mamba_without_lm_head",
        "hypothesis": "avoid large lm_head/MLP memorization and put rank-32 capacity into attention plus Mamba routing-sensitive projections",
        "code": r'''
        print("STAGE8_MECHANISM: attention+mamba target modules without lm_head/mlp adapters")
''',
        "config_replacements": {
            BASE_TARGET_MODULES: target_modules_block(["q_proj", "k_proj", "v_proj", "o_proj", "in_proj", "out_proj"]),
            "LORA_ALPHA = 32": "LORA_ALPHA = 48",
        },
        "sources": [
            "LoRA paper",
            "AdaLoRA rank allocation",
            "Kaggle discussion 687961",
        ],
        "expected_fix": "today's full-target variants underperformed; this tests a narrower adaptation surface instead of another data-only tweak.",
    },
    {
        "slug": "nemotron-s8-mlp-mamba-no-lmhead-v1",
        "folder": "nemotron_s8_mlp_mamba_no_lmhead_v1",
        "title": "Nemotron S8 MLP Mamba No LMHead V1",
        "mechanism": "mlp_mamba_without_attention_lm_head",
        "hypothesis": "shift rank-32 capacity toward transformation modules while avoiding output-head drift",
        "code": r'''
        print("STAGE8_MECHANISM: mlp+mamba target modules without attention/lm_head adapters")
''',
        "config_replacements": {
            BASE_TARGET_MODULES: target_modules_block(["up_proj", "down_proj", "in_proj", "out_proj"]),
            "LORA_ALPHA = 32": "LORA_ALPHA = 48",
        },
        "sources": [
            "AdaLoRA rank allocation",
            "DoRA weight decomposition",
            "Kaggle discussion 687961",
        ],
        "expected_fix": "pairs with the attention+mamba candidate as a module-allocation ablation rather than a small scalar sweep.",
    },
    {
        "slug": "nemotron-s8-rank-stable-alpha64-v1",
        "folder": "nemotron_s8_rank_stable_alpha64_v1",
        "title": "Nemotron S8 Rank Stable Alpha64 V1",
        "mechanism": "rank32_high_alpha_capacity_test",
        "hypothesis": "increase LoRA update amplitude at fixed legal rank 32 after several conservative variants landed below the 0.86 family",
        "code": r'''
        print("STAGE8_MECHANISM: rank-32 high-alpha capacity test with deterministic corpus order")
''',
        "config_replacements": {
            "LORA_ALPHA = 32": "LORA_ALPHA = 64",
            "SHUFFLE_DATASET = False": "SHUFFLE_DATASET = False",
        },
        "sources": [
            "rank-stabilized LoRA",
            "LoRA-GA initialization",
            "Kaggle discussion 704491",
        ],
        "expected_fix": "tests whether the 0.85 plateau is under-adaptation rather than data selection; rank remains <=32.",
    },
]


EVIDENCE = [
    {
        "source": "Kaggle CLI current results",
        "url": "local reports/SCORECARD.md",
        "lesson": "2026-06-07 SVD-family slots returned 0.85 and Muon audit returned 0.84, so tomorrow should not spend all slots on SVD/Muon variants.",
    },
    {
        "source": "bankoglu/hard-families-cot",
        "url": "https://www.kaggle.com/datasets/bankoglu/hard-families-cot",
        "lesson": "small MIT-licensed hard-family CoT dataset exposes weak-family prompts and generated traces for later corpus preprocessing.",
    },
    {
        "source": "Hugging Face PEFT model merging",
        "url": "https://huggingface.co/docs/peft/developer_guides/model_merging",
        "lesson": "adapter merging can be useful, but today's SVD results suggest merge-only candidates should be backups.",
    },
    {
        "source": "TIES-Merging",
        "url": "https://arxiv.org/abs/2306.01708",
        "lesson": "interference-aware merging remains a reserve, not the primary tomorrow path after two SVD-family failures.",
    },
    {
        "source": "DoRA / AdaLoRA / LoRA-GA family",
        "url": "https://arxiv.org/abs/2402.09353",
        "lesson": "rank and module capacity allocation are stronger next levers than another plain 0.86 repack.",
    },
]


def main() -> int:
    stage7 = load_stage7_module()
    candidates = []
    for spec in TOMORROW_VARIANTS:
        candidates.append(stage7.build_training_variant(spec))
    validation = [stage7.validate_candidate(item) for item in candidates]
    payload = {
        "stage": "8_tomorrow",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "competition_submission_executed": False,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "evidence": EVIDENCE,
    }
    write_json(CONFIG_PATH, payload)
    write_report(payload, validation)
    write_validation(validation)
    failures = [item for item in validation if not item["valid"]]
    print(f"tomorrow_candidates={len(candidates)}")
    print(f"validation_failures={len(failures)}")
    print(f"config={CONFIG_PATH.relative_to(PROJECT_ROOT)}")
    print(f"report={REPORT_PATH.relative_to(PROJECT_ROOT)}")
    return 2 if failures else 0


def write_report(payload: dict[str, Any], validation: list[dict[str, Any]]) -> None:
    validation_by_slug = {item["slug"]: item for item in validation}
    rows = [
        "# Stage 8 Tomorrow Submission Package Plan",
        "",
        f"- generated_at: {payload['generated_at']}",
        "- target: improve displayed 0.86 family toward 0.87 / rank movement",
        "- tomorrow_package_count: 5",
        "- competition_submission_executed: false",
        "- local_base_model_loaded: false",
        "- local_training_executed: false",
        "",
        "## Today's Result-Derived Fix",
        "",
        "- 2026-06-07 slot1 protected rehearsal: 0.85.",
        "- 2026-06-07 slot2 delta-space SVD: 0.85.",
        "- 2026-06-07 slot3 modulewise delta SVD: 0.85.",
        "- 2026-06-07 slot4 Muon audit/repack: 0.84.",
        "- 2026-06-07 slot5 mamba in-proj specialist: pending at generation time.",
        "",
        "Conclusion: tomorrow's primary queue should move away from pure SVD/Muon reuse and test training-objective and target-module changes.",
        "",
        "## Evidence Chain",
        "",
    ]
    for item in payload["evidence"]:
        rows.append(f"- [{item['source']}]({item['url']}): {item['lesson']}")
    rows.extend(
        [
            "",
            "## Five Packages for Tomorrow",
            "",
            "| slot | candidate | kernel | mechanism | technical path | validation |",
            "|---:|---|---|---|---|---:|",
        ]
    )
    for index, item in enumerate(payload["candidates"], start=1):
        spec = next(spec for spec in TOMORROW_VARIANTS if spec["slug"] == item["slug"])
        valid = validation_by_slug[item["slug"]]["valid"]
        rows.append(
            f"| {index} | `{item['slug']}` | `{item['kernel_id']}` | "
            f"`{item['mechanism']}` | {spec['expected_fix']} | {str(valid).lower()} |"
        )
    rows.extend(
        [
            "",
            "## Submission Policy",
            "",
            "- These notebooks may be pushed to Kaggle to generate remote `submission.zip` outputs.",
            "- They must not be submitted to the competition until tomorrow's quota is available and the current pending slot5 result has been reviewed.",
            "- Any candidate returning `0.86` should trigger a leaderboard rank check before spending the next slot.",
            "- Do not commit generated `submission.zip`, `.safetensors`, or external cache files.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(rows), encoding="utf-8")


def write_validation(results: list[dict[str, Any]]) -> None:
    rows = [
        "# Stage 8 Tomorrow Notebook Validation",
        "",
        "| candidate | valid | failed checks |",
        "|---|---:|---|",
    ]
    for item in results:
        failed = [name for name, ok in item["checks"].items() if not ok]
        rows.append(f"| `{item['slug']}` | {str(item['valid']).lower()} | {', '.join(failed) or 'none'} |")
    VALIDATION_PATH.write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
