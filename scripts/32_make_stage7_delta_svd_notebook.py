from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "kaggle_kernels" / "nemotron_s7_delta_space_svd_r32"
METADATA_PATH = OUT_DIR / "kernel-metadata.json"
NOTEBOOK_PATH = OUT_DIR / "nemotron_s7_delta_space_svd_r32.ipynb"
REPORT_PATH = PROJECT_ROOT / "reports" / "STAGE7_DELTA_SPACE_SVD_R32.md"

KERNEL_ID = "muelsyse111/nemotron-s7-delta-space-svd-r32"
MODEL = "keithtyser/nemotron-086-adapters-20260605"
ANCHORS = [
    "public_hk_to_kn_lm_head_lam1p0",
    "public_kn_to_hk_lm_head_lam1p0",
    "public_hk_to_kn_mamba_lam1p0",
]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    metadata = {
        "id": KERNEL_ID,
        "title": "Nemotron S7 Delta Space SVD R32",
        "code_file": NOTEBOOK_PATH.name,
        "language": "python",
        "kernel_type": "notebook",
        "is_private": "true",
        "enable_gpu": "false",
        "enable_internet": "false",
        "dataset_sources": [],
        "competition_sources": ["nvidia-nemotron-model-reasoning-challenge"],
        "kernel_sources": [],
        "model_sources": [f"{MODEL}/Transformers/{name}/1" for name in ANCHORS],
    }
    notebook = {
        "cells": [
            markdown_cell(
                "# Nemotron S7 Delta-Space SVD Rank-32\n\n"
                "This notebook merges three compatible rank-32 LoRA adapters in their "
                "effective update space, `sum_i w_i B_i A_i`, then recompresses each "
                "module to rank 32 with QR plus a small-core SVD. It never loads the "
                "30B base model and never submits the competition."
            ),
            code_cell(notebook_source()),
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.12"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    NOTEBOOK_PATH.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    validate(metadata, notebook)
    REPORT_PATH.write_text(render_report(), encoding="utf-8")
    print(f"kernel_id={KERNEL_ID}")
    print(f"kernel_dir={OUT_DIR.relative_to(PROJECT_ROOT)}")
    print(f"metadata={METADATA_PATH.relative_to(PROJECT_ROOT)}")
    print(f"notebook={NOTEBOOK_PATH.relative_to(PROJECT_ROOT)}")
    print(f"report={REPORT_PATH.relative_to(PROJECT_ROOT)}")
    print(f'push_command=kaggle kernels push -p "{OUT_DIR.relative_to(PROJECT_ROOT)}"')
    return 0


def markdown_cell(text: str) -> dict:
    return {
        "cell_type": "markdown",
        "id": "delta-svd-intro",
        "metadata": {},
        "source": text.splitlines(keepends=True),
    }


def code_cell(text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": "delta-svd-run",
        "metadata": {},
        "outputs": [],
        "source": text.splitlines(keepends=True),
    }


def notebook_source() -> str:
    return r'''from pathlib import Path
import gc
import hashlib
import json
import math
import re
import shutil
import zipfile

import torch
from safetensors.torch import load_file, save_file

CANDIDATE = "nemotron-s7-delta-space-svd-r32"
MECHANISM = "effective_delta_qr_svd_rank32_recompression"
INPUT_ROOT = Path("/kaggle/input")
WORKING_ROOT = Path("/kaggle/working")
ADAPTER_DIR = WORKING_ROOT / CANDIDATE / "adapter"
SUBMISSION_ZIP = WORKING_ROOT / "submission.zip"
PREFERRED = [
    "public_hk_to_kn_lm_head_lam1p0",
    "public_kn_to_hk_lm_head_lam1p0",
    "public_hk_to_kn_mamba_lam1p0",
]
WEIGHTS = [0.50, 0.30, 0.20]
TARGET_RANK = 32


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_adapters():
    found = []
    for cfg_path in sorted(INPUT_ROOT.rglob("adapter_config.json")):
        model_path = cfg_path.parent / "adapter_model.safetensors"
        if not model_path.exists():
            continue
        config = json.loads(cfg_path.read_text(encoding="utf-8"))
        lower = str(cfg_path.parent).lower()
        slug = next((name for name in PREFERRED if name.lower() in lower), cfg_path.parent.name)
        found.append(
            {
                "slug": slug,
                "config_path": cfg_path,
                "model_path": model_path,
                "config": config,
            }
        )
    by_slug = {item["slug"]: item for item in found}
    selected = [by_slug[name] for name in PREFERRED if name in by_slug]
    if len(selected) != 3:
        raise RuntimeError(f"Expected all three named anchors, found {[item['slug'] for item in selected]}")
    ranks = {int(item["config"].get("r", 0)) for item in selected}
    targets = {json.dumps(item["config"].get("target_modules"), sort_keys=True) for item in selected}
    if ranks != {32} or len(targets) != 1:
        raise RuntimeError(f"Incompatible adapters: ranks={ranks}, target_sets={len(targets)}")
    return selected


def paired_b_key(a_key):
    if ".lora_A." not in a_key:
        return None
    return a_key.replace(".lora_A.", ".lora_B.", 1)


def effective_scale(config, key):
    rank = int(config.get("r", TARGET_RANK))
    alpha = float(config.get("lora_alpha", rank))
    alpha_pattern = config.get("alpha_pattern") or {}
    rank_pattern = config.get("rank_pattern") or {}
    for name, value in alpha_pattern.items():
        if name in key:
            alpha = float(value)
            break
    for name, value in rank_pattern.items():
        if name in key:
            rank = int(value)
            break
    return alpha / rank


def weights_for_key(key):
    return WEIGHTS


def recompress_pair(a_values, b_values, configs, a_key):
    output_scale = effective_scale(configs[0], a_key)
    c_blocks = []
    d_blocks = []
    module_weights = weights_for_key(a_key)
    for weight, a_value, b_value, config in zip(module_weights, a_values, b_values, configs):
        if a_value.ndim != 2 or b_value.ndim != 2:
            raise RuntimeError(f"LoRA pair must be matrices: {a_key}")
        if b_value.shape[1] != a_value.shape[0]:
            raise RuntimeError(f"LoRA pair shape mismatch: {a_key}, {b_value.shape}, {a_value.shape}")
        coefficient = weight * effective_scale(config, a_key) / output_scale
        root = math.sqrt(abs(coefficient))
        sign = -1.0 if coefficient < 0 else 1.0
        c_blocks.append(b_value.float() * (root * sign))
        d_blocks.append(a_value.float() * root)

    c_matrix = torch.cat(c_blocks, dim=1)
    d_matrix = torch.cat(d_blocks, dim=0)
    q_c, r_c = torch.linalg.qr(c_matrix, mode="reduced")
    q_d, r_d = torch.linalg.qr(d_matrix.T, mode="reduced")
    core = r_c @ r_d.T
    u, singular, vh = torch.linalg.svd(core, full_matrices=False)
    rank = min(TARGET_RANK, singular.numel())
    sqrt_s = singular[:rank].clamp_min(0).sqrt()
    b_new = (q_c @ u[:, :rank]) * sqrt_s.unsqueeze(0)
    a_new = sqrt_s.unsqueeze(1) * (vh[:rank, :] @ q_d.T)
    retained = float(singular[:rank].sum() / singular.sum().clamp_min(1e-12))
    return a_new, b_new, retained


selected = find_adapters()
print("source_adapters:", [item["slug"] for item in selected])
print("weights:", WEIGHTS)
tensors = [load_file(str(item["model_path"]), device="cpu") for item in selected]
configs = [item["config"] for item in selected]
keys = sorted(tensors[0])
for tensor_map in tensors[1:]:
    if sorted(tensor_map) != keys:
        raise RuntimeError("Adapter tensor key sets differ")

merged = {}
processed_b = set()
retained_ratios = []
pair_count = 0
for index, key in enumerate(keys):
    if key in processed_b:
        continue
    b_key = paired_b_key(key)
    if b_key and b_key in tensors[0]:
        a_values = [tensor_map[key] for tensor_map in tensors]
        b_values = [tensor_map[b_key] for tensor_map in tensors]
        a_new, b_new, retained = recompress_pair(a_values, b_values, configs, key)
        merged[key] = a_new.to(a_values[0].dtype).contiguous()
        merged[b_key] = b_new.to(b_values[0].dtype).contiguous()
        processed_b.add(b_key)
        retained_ratios.append(retained)
        pair_count += 1
    else:
        # Non-LoRA tensors are kept from the strongest anchor. Averaging full
        # saved modules would mix absolute weights rather than adapter deltas.
        merged[key] = tensors[0][key]
    if index % 250 == 0:
        print("processed_keys:", index, "/", len(keys), "pairs:", pair_count)

if pair_count == 0:
    raise RuntimeError("No LoRA A/B pairs were found")

ADAPTER_DIR.mkdir(parents=True, exist_ok=True)
config_out = ADAPTER_DIR / "adapter_config.json"
model_out = ADAPTER_DIR / "adapter_model.safetensors"
shutil.copyfile(selected[0]["config_path"], config_out)
save_file(merged, str(model_out))
if model_out.stat().st_size < 100 * 1024 * 1024:
    raise RuntimeError(f"Unexpectedly small adapter: {model_out.stat().st_size}")

if SUBMISSION_ZIP.exists():
    SUBMISSION_ZIP.unlink()
with zipfile.ZipFile(SUBMISSION_ZIP, "w", zipfile.ZIP_STORED) as archive:
    archive.write(config_out, "adapter_config.json")
    archive.write(model_out, "adapter_model.safetensors")
with zipfile.ZipFile(SUBMISSION_ZIP, "r") as archive:
    names = sorted(archive.namelist())
if names != ["adapter_config.json", "adapter_model.safetensors"]:
    raise RuntimeError(f"Invalid zip root: {names}")

report = {
    "candidate": CANDIDATE,
    "mechanism": MECHANISM,
    "source_adapters": [item["slug"] for item in selected],
    "weights": WEIGHTS,
    "lora_pair_count": pair_count,
    "mean_retained_singular_mass": sum(retained_ratios) / len(retained_ratios),
    "rank_lte_32": True,
    "adapter_model_sha256": sha256_file(model_out),
    "submission_zip_sha256": sha256_file(SUBMISSION_ZIP),
    "submission_zip_size_bytes": SUBMISSION_ZIP.stat().st_size,
    "zip_namelist": names,
}
(WORKING_ROOT / f"{CANDIDATE}_report.json").write_text(
    json.dumps(report, indent=2), encoding="utf-8"
)
print(json.dumps(report, indent=2))
print("OK: /kaggle/working/submission.zip is ready.")
'''


def validate(metadata: dict, notebook: dict) -> None:
    text = "\n".join(
        "".join(cell.get("source", [])) for cell in notebook.get("cells", [])
    )
    checks = {
        "kernel_id": metadata.get("id") == KERNEL_ID,
        "cpu_only": str(metadata.get("enable_gpu")).lower() == "false",
        "three_model_sources": len(metadata.get("model_sources", [])) == 3,
        "delta_space": "c_matrix = torch.cat(c_blocks, dim=1)" in text,
        "small_core_svd": "torch.linalg.svd(core" in text,
        "rank32": "TARGET_RANK = 32" in text,
        "exact_zip_root": '["adapter_config.json", "adapter_model.safetensors"]' in text,
        "success_marker": "OK: /kaggle/working/submission.zip is ready." in text,
        "no_competition_submit": "kaggle competitions submit" not in text,
        "no_base_model_load": "from_pretrained" not in text,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"Notebook validation failed: {failed}")


def render_report() -> str:
    return """# Stage 7 Delta-Space SVD Rank-32

- kernel: `muelsyse111/nemotron-s7-delta-space-svd-r32`
- mechanism: effective LoRA delta merge plus rank-32 recompression
- GPU required: false
- base model loaded: false
- competition submission executed: false

## Why This Differs

Directly averaging LoRA A and B factors generally does not equal averaging their
effective model updates. This experiment merges `B @ A` updates and uses a
low-rank QR/SVD identity to avoid materializing large dense matrices.

## Sources

- LoRA: https://arxiv.org/abs/2106.09685
- TIES-Merging: https://arxiv.org/abs/2306.01708
- PEFT model merging: https://huggingface.co/docs/peft/developer_guides/model_merging
- Rauffauzan rank-compression route:
  https://www.kaggle.com/code/rauffauzanrambe/lora-adapter-fusion-and-rank-compression-pipeline

## Gate

The output is only structurally valid after the remote notebook prints the
success marker, exact zip root, size, SHA256, LoRA pair count, and retained
singular-mass diagnostic.
"""


if __name__ == "__main__":
    raise SystemExit(main())
