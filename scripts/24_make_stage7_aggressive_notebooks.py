from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
KAGGLE_USER = "muelsyse111"
COMPETITION = "nvidia-nemotron-model-reasoning-challenge"

KEITHTYSER_MODEL = "keithtyser/nemotron-086-adapters-20260605"
KEITHTYSER_INSTANCES = [
    "huikang_default20_ready",
    "public_hk_to_kn_lm_head_lam1p0",
    "public_hk_to_kn_mamba_lam1p0",
    "public_hk_to_kn_no_experts_lam1p0",
    "public_kn_to_hk_lm_head_lam1p0",
    "public_kn_to_hk_lm_head_lam1p0_alpha32",
]


def main() -> int:
    build_multi_anchor_fusion_notebook()
    build_reasoning_data_training_notebook()
    print("generated:")
    print("  kaggle_kernels/nemotron_stage7_multi_anchor_fusion_factory")
    print("  kaggle_kernels/nemotron_stage7_reasoning_data_factory")
    return 0


def build_multi_anchor_fusion_notebook() -> None:
    slug = "nemotron-stage7-multi-anchor-fusion-factory"
    out_dir = PROJECT_ROOT / "kaggle_kernels" / "nemotron_stage7_multi_anchor_fusion_factory"
    out_dir.mkdir(parents=True, exist_ok=True)
    code_file = "nemotron_stage7_multi_anchor_fusion_factory.ipynb"

    metadata = {
        "id": f"{KAGGLE_USER}/{slug}",
        "title": "nemotron stage7 multi anchor fusion factory",
        "code_file": code_file,
        "language": "python",
        "kernel_type": "notebook",
        "is_private": "true",
        "enable_gpu": "false",
        "enable_internet": "false",
        "dataset_sources": [],
        "competition_sources": [COMPETITION],
        "kernel_sources": [],
        "model_sources": [
            f"{KEITHTYSER_MODEL}/Transformers/{name}/1" for name in KEITHTYSER_INSTANCES
        ],
    }
    write_json(out_dir / "kernel-metadata.json", metadata)

    source = r'''from pathlib import Path
import gc
import hashlib
import json
import os
import shutil
import sys
import zipfile

import torch
from safetensors.torch import load_file, save_file

INPUT_ROOT = Path("/kaggle/input")
WORKING_ROOT = Path("/kaggle/working")
OUT_DIR = WORKING_ROOT / "stage7_multi_anchor_fusion"
MERGED_DIR = OUT_DIR / "merged_adapter"
SUBMISSION_ZIP = WORKING_ROOT / "submission.zip"
REPORT_PATH = WORKING_ROOT / "stage7_multi_anchor_fusion_report.json"

PREFERRED_SLUGS = [
    "public_hk_to_kn_lm_head_lam1p0",
    "public_kn_to_hk_lm_head_lam1p0",
    "public_hk_to_kn_mamba_lam1p0",
]
DELTA_WEIGHTS = {
    "public_kn_to_hk_lm_head_lam1p0": 0.35,
    "public_hk_to_kn_mamba_lam1p0": 0.20,
}
METHOD = "task_arithmetic_delta_rank32"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def find_adapters() -> list[dict]:
    adapters = []
    for config_path in sorted(INPUT_ROOT.rglob("adapter_config.json")):
        model_path = config_path.parent / "adapter_model.safetensors"
        if not model_path.exists():
            continue
        cfg = load_config(config_path)
        slug = ""
        lower = str(config_path.parent).lower()
        for item in PREFERRED_SLUGS + [
            "huikang_default20_ready",
            "public_hk_to_kn_no_experts_lam1p0",
            "public_kn_to_hk_lm_head_lam1p0_alpha32",
        ]:
            if item.lower() in lower:
                slug = item
                break
        if not slug:
            slug = config_path.parent.name
        adapters.append(
            {
                "slug": slug,
                "dir": str(config_path.parent),
                "config": str(config_path),
                "model": str(model_path),
                "size_bytes": model_path.stat().st_size,
                "rank": cfg.get("r"),
                "lora_alpha": cfg.get("lora_alpha"),
                "target_modules": cfg.get("target_modules"),
                "base_model_name_or_path": cfg.get("base_model_name_or_path"),
                "peft_type": cfg.get("peft_type"),
                "sha256": sha256_file(model_path),
            }
        )
    return adapters


def choose_adapters(adapters: list[dict]) -> list[dict]:
    by_slug = {a["slug"]: a for a in adapters}
    selected = [by_slug[s] for s in PREFERRED_SLUGS if s in by_slug]
    if len(selected) < 3:
        ranked = sorted(adapters, key=lambda a: (a["slug"] not in PREFERRED_SLUGS, a["slug"]))
        selected = ranked[:3]
    if len(selected) < 2:
        raise SystemExit("ERROR: need at least two compatible adapter anchors")
    return selected


def assert_config_compatible(selected: list[dict]) -> None:
    ranks = {int(a["rank"]) for a in selected if a["rank"] is not None}
    if not ranks or max(ranks) > 32:
        raise SystemExit(f"ERROR: invalid ranks for selected adapters: {ranks}")
    targets = [json.dumps(a["target_modules"], sort_keys=True) for a in selected]
    if len(set(targets)) != 1:
        raise SystemExit("ERROR: selected adapters have different target_modules")


def tensor_key_report(paths: list[Path]) -> dict:
    reports = []
    base_keys = None
    base_shapes = None
    for path in paths:
        tensors = load_file(str(path), device="cpu")
        keys = sorted(tensors.keys())
        shapes = {k: tuple(tensors[k].shape) for k in keys}
        reports.append({"path": str(path), "num_keys": len(keys), "sha256": sha256_file(path)})
        if base_keys is None:
            base_keys = keys
            base_shapes = shapes
        else:
            if keys != base_keys:
                raise SystemExit(f"ERROR: tensor keys differ for {path}")
            if shapes != base_shapes:
                raise SystemExit(f"ERROR: tensor shapes differ for {path}")
        del tensors
        gc.collect()
    return {"reports": reports, "num_keys": len(base_keys or [])}


def merge_task_arithmetic(selected: list[dict]) -> dict:
    base = selected[0]
    others = selected[1:]
    base_path = Path(base["model"])
    print("base_anchor:", base["slug"], base_path)
    base_tensors = load_file(str(base_path), device="cpu")
    merged = {k: v.to(torch.float32).clone() for k, v in base_tensors.items()}
    original_dtypes = {k: v.dtype for k, v in base_tensors.items()}

    used_weights = {}
    for adapter in others:
        slug = adapter["slug"]
        weight = float(DELTA_WEIGHTS.get(slug, 0.15))
        used_weights[slug] = weight
        print("delta_anchor:", slug, "weight:", weight)
        tensors = load_file(str(adapter["model"]), device="cpu")
        for key in merged:
            delta = tensors[key].to(torch.float32) - base_tensors[key].to(torch.float32)
            merged[key].add_(delta, alpha=weight)
        del tensors
        gc.collect()

    out_tensors = {}
    for key, tensor in merged.items():
        out_tensors[key] = tensor.to(original_dtypes[key])
    return {"tensors": out_tensors, "weights": used_weights}


print("Stage 7 multi-anchor fusion factory")
print("python:", sys.version)
print("input_root:", INPUT_ROOT)
if not INPUT_ROOT.exists():
    raise SystemExit("ERROR: /kaggle/input not found")

adapters = find_adapters()
print("adapters_found:", len(adapters))
for item in adapters:
    print(json.dumps({k: item[k] for k in ["slug", "rank", "size_bytes", "sha256", "dir"]}, ensure_ascii=False))
if len(adapters) < 2:
    raise SystemExit("ERROR: fewer than two adapter anchors found")

selected = choose_adapters(adapters)
assert_config_compatible(selected)
print("selected_slugs:", [a["slug"] for a in selected])
key_info = tensor_key_report([Path(a["model"]) for a in selected])
print("tensor_key_report:", key_info)

OUT_DIR.mkdir(parents=True, exist_ok=True)
MERGED_DIR.mkdir(parents=True, exist_ok=True)
for path in MERGED_DIR.glob("adapter*"):
    path.unlink()

merge_result = merge_task_arithmetic(selected)
base_config_path = Path(selected[0]["config"])
merged_config_path = MERGED_DIR / "adapter_config.json"
merged_model_path = MERGED_DIR / "adapter_model.safetensors"
shutil.copyfile(base_config_path, merged_config_path)
save_file(merge_result["tensors"], str(merged_model_path))

if SUBMISSION_ZIP.exists():
    SUBMISSION_ZIP.unlink()
with zipfile.ZipFile(SUBMISSION_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    zf.write(merged_config_path, "adapter_config.json")
    zf.write(merged_model_path, "adapter_model.safetensors")
with zipfile.ZipFile(SUBMISSION_ZIP, "r") as zf:
    names = sorted(zf.namelist())
if names != ["adapter_config.json", "adapter_model.safetensors"]:
    raise SystemExit(f"ERROR: bad zip contents: {names}")

report = {
    "stage": "7",
    "candidate": "keithtyser_task_arithmetic_delta_rank32",
    "method": METHOD,
    "selected": selected,
    "delta_weights": merge_result["weights"],
    "tensor_key_report": key_info,
    "merged_adapter_sha256": sha256_file(merged_model_path),
    "submission_zip_path": str(SUBMISSION_ZIP),
    "submission_zip_sha256": sha256_file(SUBMISSION_ZIP),
    "submission_zip_size_bytes": SUBMISSION_ZIP.stat().st_size,
    "zip_namelist": names,
    "rank_lte_32": True,
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
print("OK: /kaggle/working/submission.zip is ready.")
'''

    notebook = build_notebook(
        "Stage 7 Multi-Anchor Fusion Factory",
        "Creates one task-arithmetic rank-32 adapter from mounted Keithtyser 0.86-class anchors. It does not load the base model and does not submit.",
        source,
    )
    write_json(out_dir / code_file, notebook)


def build_reasoning_data_training_notebook() -> None:
    slug = "nemotron-stage7-reasoning-data-factory"
    out_dir = PROJECT_ROOT / "kaggle_kernels" / "nemotron_stage7_reasoning_data_factory"
    out_dir.mkdir(parents=True, exist_ok=True)
    code_file = "nemotron_stage7_reasoning_data_factory.ipynb"
    source_nb_path = (
        PROJECT_ROOT
        / "external"
        / "stage7_kernel_sources"
        / "mohamed_replay_data_086"
        / "nemotron-replay-data-0-86.ipynb"
    )
    source_meta_path = source_nb_path.with_name("kernel-metadata.json")
    if not source_nb_path.exists() or not source_meta_path.exists():
        raise SystemExit("Missing Mohamed source notebook. Pull it before generating Stage 7 notebook.")

    nb = json.loads(source_nb_path.read_text(encoding="utf-8"))
    metadata = json.loads(source_meta_path.read_text(encoding="utf-8"))
    metadata.update(
        {
            "id": f"{KAGGLE_USER}/{slug}",
            "title": "nemotron stage7 reasoning data factory",
            "code_file": code_file,
            "is_private": "true",
            "enable_gpu": "true",
            "enable_internet": "false",
            "competition_sources": [COMPETITION],
        }
    )
    metadata.pop("id_no", None)
    write_json(out_dir / "kernel-metadata.json", metadata)

    nb["cells"].insert(
        0,
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Stage 7 Reasoning Data Training Factory\n",
                "\n",
                "Based on the Mohamed 0.86 replay-data training chain, but changes the data pipeline with hard-unmasked curriculum mixing. It uses Kaggle GPU and writes `/kaggle/working/submission.zip` if training completes.\n",
            ],
        },
    )
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = "".join(cell.get("source", []))
        if "KAGGLE_API_TOKEN" in src:
            src = re.sub(
                r"\n    else:  # IS_MODAL_WORKER\n        import shutil.*?        print\(\"Kaggle upload complete\.\"\)",
                "",
                src,
                flags=re.DOTALL,
            )
        if "LEARNING_RATE" in src and "LORA_RANK" in src:
            src = src.replace(
                "SHUFFLE_DATASET = False",
                """SHUFFLE_DATASET = False

# Stage 7 aggressive data factory: this is not an LR sweep.
STAGE7_DATA_FACTORY_MODE = "hard_unmasked_curriculum_mix"
STAGE7_TARGET_HARD_FRACTION = 0.60
STAGE7_REPLAY_HARD_FRACTION = 0.40
STAGE7_MAX_EXAMPLES = None""",
            )
            cell["source"] = lines(src)
        if "REPLAY_TOKENIZED_PATH" in src and "mixed_examples.extend(replay_examples[replay_idx:])" in src:
            marker = """        print(
            f"Mixed corpus: {mixed_tokens:,} tokens "
            f"(unmasked={mixed_unmasked:,.0f})"
        )
"""
            insertion = r'''

        # Stage 7 aggressive data processing: hard-unmasked curriculum mix.
        def _example_stats(ex):
            token_len = max(1, len(ex["tokens"]))
            unmasked = float(sum(ex["weights"]))
            density = unmasked / token_len
            return token_len, unmasked, density

        before_count = len(examples)
        target_pool = [e for e in examples if e.get("problem_id") != "replay_math"]
        replay_pool = [e for e in examples if e.get("problem_id") == "replay_math"]
        target_hard = sorted(target_pool, key=lambda e: (_example_stats(e)[1], _example_stats(e)[2], _example_stats(e)[0]), reverse=True)
        replay_hard = sorted(replay_pool, key=lambda e: (_example_stats(e)[1], _example_stats(e)[2], _example_stats(e)[0]), reverse=True)
        target_take = max(1, int(len(target_pool) * STAGE7_TARGET_HARD_FRACTION))
        replay_take = max(1, int(len(replay_pool) * STAGE7_REPLAY_HARD_FRACTION)) if replay_pool else 0
        selected = []
        seen_ids = set()

        def _add(ex):
            key = (ex.get("problem_id"), len(selected))
            selected.append(ex)
            seen_ids.add(key)

        # Curriculum shape: hard target examples first, then hard replay examples,
        # then original-order examples to preserve distributional coverage.
        for ex in target_hard[:target_take]:
            _add(ex)
        for ex in replay_hard[:replay_take]:
            _add(ex)
        for ex in examples:
            if STAGE7_MAX_EXAMPLES is not None and len(selected) >= STAGE7_MAX_EXAMPLES:
                break
            _add(ex)
        examples = selected

        stage7_report = {
            "mode": STAGE7_DATA_FACTORY_MODE,
            "before_count": before_count,
            "after_count": len(examples),
            "target_pool": len(target_pool),
            "replay_pool": len(replay_pool),
            "target_take": target_take,
            "replay_take": replay_take,
            "max_examples": STAGE7_MAX_EXAMPLES,
            "total_tokens": sum(len(e["tokens"]) for e in examples),
            "total_unmasked": sum(sum(e["weights"]) for e in examples),
        }
        with open("/kaggle/working/stage7_data_processing_report.json", "w") as f:
            json.dump(stage7_report, f, indent=2)
        print("STAGE7_DATA_PROCESSING_REPORT:", json.dumps(stage7_report, indent=2))
'''
            if "STAGE7_DATA_PROCESSING_REPORT" not in src:
                src = src.replace(marker, marker + insertion)
            src = src.replace(
                'print(f"Wrote {SUBMISSION_ZIP}")',
                '''import hashlib
        def _sha256_file(_path):
            _digest = hashlib.sha256()
            with open(_path, "rb") as _handle:
                for _chunk in iter(lambda: _handle.read(1024 * 1024), b""):
                    _digest.update(_chunk)
            return _digest.hexdigest()
        with zipfile.ZipFile(SUBMISSION_ZIP, "r") as _zf:
            _names = sorted(_zf.namelist())
        print("zip_namelist:", _names)
        if _names != ["adapter_config.json", "adapter_model.safetensors"]:
            raise RuntimeError(f"bad submission zip contents: {_names}")
        print(f"Wrote {SUBMISSION_ZIP}")
        print("submission_zip_sha256:", _sha256_file(SUBMISSION_ZIP))
        print("OK: /kaggle/working/submission.zip is ready.")''',
            )
            cell["source"] = lines(src)
    nb["cells"] = [
        cell
        for cell in nb.get("cells", [])
        if not (
            cell.get("cell_type") == "code"
            and (
                "Modal glue" in "".join(cell.get("source", []))
                or "import modal" in "".join(cell.get("source", []))
                or "modal.App" in "".join(cell.get("source", []))
            )
        )
    ]
    nb["metadata"]["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    write_json(out_dir / code_file, nb)


def build_notebook(title: str, description: str, source: str) -> dict[str, Any]:
    return {
        "cells": [
            {"cell_type": "markdown", "metadata": {}, "source": [f"# {title}\n", "\n", description + "\n"]},
            {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": lines(source)},
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def lines(text: str) -> list[str]:
    return [line + "\n" for line in text.splitlines()]


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
