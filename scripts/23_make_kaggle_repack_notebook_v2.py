from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.provenance import ensure_dir  # noqa: E402
from nemotron086.reporting import write_text  # noqa: E402


DEFAULT_KERNEL_SLUG = "nemotron-repack-huikang-v27-normalized"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "kaggle_kernels" / "nemotron_repack_huikang_v27_normalized"
MODEL_SOURCE = "huikang/nemotron-adapter/Transformers/default/27"
COMPETITION = "nvidia-nemotron-model-reasoning-challenge"
BASE_MODEL_NAME = "nvidia/Nemotron-3-Nano-30B-A3B-BF16"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Kaggle-side normalized adapter repack notebook.")
    parser.add_argument("--kaggle-user", required=True)
    parser.add_argument("--kernel-slug", default=DEFAULT_KERNEL_SLUG)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()

    kaggle_user = args.kaggle_user.strip()
    if not kaggle_user:
        raise SystemExit("--kaggle-user must not be empty")
    kernel_slug = args.kernel_slug.strip()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir
    ensure_dir(output_dir)

    code_file = f"{kernel_slug.replace('-', '_')}.ipynb"
    metadata = {
        "id": f"{kaggle_user}/{kernel_slug}",
        "title": kernel_slug.replace("-", " "),
        "code_file": code_file,
        "language": "python",
        "kernel_type": "notebook",
        "is_private": "true",
        "enable_gpu": "false",
        "enable_internet": "false",
        "dataset_sources": [],
        "competition_sources": [COMPETITION],
        "kernel_sources": [],
        "model_sources": [MODEL_SOURCE],
    }

    metadata_path = output_dir / "kernel-metadata.json"
    notebook_path = output_dir / code_file
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    notebook_path.write_text(json.dumps(build_notebook(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    validate_no_forbidden_notebook_text(notebook_path.read_text(encoding="utf-8"))
    write_adjustment_report(kaggle_user, kernel_slug, output_dir)

    rel_output = output_dir.relative_to(PROJECT_ROOT).as_posix()
    print(f"kernel directory: {rel_output}")
    print(f"metadata path: {metadata_path.relative_to(PROJECT_ROOT).as_posix()}")
    print(f"notebook path: {notebook_path.relative_to(PROJECT_ROOT).as_posix()}")
    print(f"next push command: python scripts\\21_push_kaggle_notebook.py --kernel-dir \"{rel_output}\"")
    return 0


def build_notebook() -> dict[str, Any]:
    source = r'''from pathlib import Path
import json
import zipfile
import hashlib
import os
import sys
import struct
import shutil

INPUT_ROOT = Path("/kaggle/input")
WORKING_ROOT = Path("/kaggle/working")
SUBMISSION_ZIP = WORKING_ROOT / "submission.zip"
NORMALIZED_CONFIG = WORKING_ROOT / "adapter_config.json"
NORMALIZED_MODEL = WORKING_ROOT / "adapter_model.safetensors"
EXPECTED_ZIP_NAMES = ["adapter_config.json", "adapter_model.safetensors"]
BASE_MODEL_NAME = "nvidia/Nemotron-3-Nano-30B-A3B-BF16"


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def candidate_score(candidate):
    path_text = str(candidate["dir"]).lower()
    score = 0
    if "nemotron" in path_text:
        score += 2
    if "adapter" in path_text:
        score += 1
    return score


def read_safetensors_header(path):
    with path.open("rb") as handle:
        header_len = struct.unpack("<Q", handle.read(8))[0]
        header = json.loads(handle.read(header_len).decode("utf-8"))
    return header_len, header


def tensor_names(header):
    return [name for name in header if name != "__metadata__"]


def has_zero_shape(info):
    return any(int(dim) == 0 for dim in info.get("shape", []))


def derive_target_modules(header):
    modules = set()
    for name in tensor_names(header):
        if has_zero_shape(header[name]):
            continue
        if ".lora_A." not in name:
            continue
        prefix = name.split(".lora_A.")[0]
        modules.add(prefix.split(".")[-1])
    # Keep a deterministic order that follows common transformer/MoE naming.
    preferred = [
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "out_proj",
        "x_proj",
        "w1",
        "w2",
        "up_proj",
        "down_proj",
        "lm_head",
    ]
    ordered = [name for name in preferred if name in modules]
    ordered.extend(sorted(modules - set(ordered)))
    return ordered


def strip_zero_tensors(source_path, target_path):
    with source_path.open("rb") as source:
        header_len = struct.unpack("<Q", source.read(8))[0]
        header = json.loads(source.read(header_len).decode("utf-8"))
        data_start = 8 + header_len
        kept = []
        removed = []
        cursor = 0
        new_header = {}
        if "__metadata__" in header:
            new_header["__metadata__"] = header["__metadata__"]
        for name in tensor_names(header):
            info = dict(header[name])
            if has_zero_shape(info):
                removed.append(name)
                continue
            start, end = info["data_offsets"]
            length = int(end) - int(start)
            info["data_offsets"] = [cursor, cursor + length]
            new_header[name] = info
            kept.append((name, int(start), int(end), length))
            cursor += length

        header_bytes = json.dumps(new_header, separators=(",", ":")).encode("utf-8")
        with target_path.open("wb") as target:
            target.write(struct.pack("<Q", len(header_bytes)))
            target.write(header_bytes)
            for _name, start, _end, length in kept:
                source.seek(data_start + start)
                remaining = length
                while remaining:
                    chunk = source.read(min(1024 * 1024, remaining))
                    if not chunk:
                        raise RuntimeError("Unexpected EOF while copying safetensors payload")
                    target.write(chunk)
                    remaining -= len(chunk)
    return kept, removed


print("Kaggle-side Nemotron adapter normalized repack v2")
print("input_root:", INPUT_ROOT)
print("working_root:", WORKING_ROOT)
print("python:", sys.version)

if not INPUT_ROOT.exists():
    raise SystemExit("ERROR: /kaggle/input does not exist. Check notebook inputs.")

configs = sorted(INPUT_ROOT.rglob("adapter_config.json"))
candidates = []
for config_path in configs:
    model_path = config_path.parent / "adapter_model.safetensors"
    candidates.append(
        {
            "dir": config_path.parent,
            "config": config_path,
            "model": model_path,
            "model_exists": model_path.exists(),
        }
    )

print("adapter candidates:")
for idx, candidate in enumerate(candidates, 1):
    print(idx, "dir=", candidate["dir"], "model_exists=", candidate["model_exists"])

valid_candidates = [candidate for candidate in candidates if candidate["model_exists"]]
if not valid_candidates:
    raise SystemExit("ERROR: no adapter_config.json with sibling adapter_model.safetensors was found.")

selected = sorted(valid_candidates, key=lambda item: (-candidate_score(item), str(item["dir"])))[0]
config_path = selected["config"]
model_path = selected["model"]
print("selected_adapter_dir:", selected["dir"])

original_config = json.loads(config_path.read_text(encoding="utf-8"))
header_len, original_header = read_safetensors_header(model_path)
target_modules = derive_target_modules(original_header)
zero_tensors = [name for name in tensor_names(original_header) if has_zero_shape(original_header[name])]

print("original_peft_type:", original_config.get("peft_type"))
print("original_r:", original_config.get("r"))
print("original_base_model_name_or_path:", original_config.get("base_model_name_or_path"))
print("original_target_modules:", original_config.get("target_modules"))
print("safetensors_header_len:", header_len)
print("safetensors_tensor_count:", len(tensor_names(original_header)))
print("zero_tensor_count:", len(zero_tensors))
print("derived_target_modules:", target_modules)

rank = original_config.get("r")
if rank is not None:
    try:
        rank_int = int(rank)
    except Exception as exc:
        raise SystemExit(f"ERROR: adapter rank r is not an integer: {rank!r}") from exc
    if rank_int > 32:
        raise SystemExit(f"ERROR: adapter rank r={rank_int} exceeds competition limit 32.")
else:
    raise SystemExit("ERROR: adapter rank r is missing.")

WORKING_ROOT.mkdir(parents=True, exist_ok=True)
for path in [SUBMISSION_ZIP, NORMALIZED_CONFIG, NORMALIZED_MODEL]:
    if path.exists():
        path.unlink()

normalized_config = dict(original_config)
normalized_config["target_modules"] = target_modules
if normalized_config.get("base_model_name_or_path") in (None, ""):
    normalized_config["base_model_name_or_path"] = BASE_MODEL_NAME
normalized_config["inference_mode"] = True
NORMALIZED_CONFIG.write_text(json.dumps(normalized_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

kept, removed = strip_zero_tensors(model_path, NORMALIZED_MODEL)
_, normalized_header = read_safetensors_header(NORMALIZED_MODEL)
normalized_zero = [name for name in tensor_names(normalized_header) if has_zero_shape(normalized_header[name])]
if normalized_zero:
    raise SystemExit(f"ERROR: normalized safetensors still has zero tensors: {normalized_zero[:5]}")

print("normalized_base_model_name_or_path:", normalized_config.get("base_model_name_or_path"))
print("normalized_target_modules:", normalized_config.get("target_modules"))
print("normalized_inference_mode:", normalized_config.get("inference_mode"))
print("kept_tensor_count:", len(kept))
print("removed_zero_tensor_count:", len(removed))
print("removed_zero_tensor_sample:", removed[:12])
print("normalized_model_size_bytes:", NORMALIZED_MODEL.stat().st_size)
print("normalized_model_sha256:", sha256_file(NORMALIZED_MODEL))

with zipfile.ZipFile(SUBMISSION_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
    zf.write(NORMALIZED_CONFIG, arcname="adapter_config.json")
    zf.write(NORMALIZED_MODEL, arcname="adapter_model.safetensors")

with zipfile.ZipFile(SUBMISSION_ZIP, "r") as zf:
    names = sorted(zf.namelist())
print("zip_namelist:", names)
if names != EXPECTED_ZIP_NAMES:
    raise SystemExit(f"ERROR: invalid zip root contents: {names!r}")

size_bytes = SUBMISSION_ZIP.stat().st_size
sha256 = sha256_file(SUBMISSION_ZIP)
print("submission_zip:", SUBMISSION_ZIP)
print("submission_zip_size_bytes:", size_bytes)
print("submission_zip_sha256:", sha256)
NORMALIZED_CONFIG.unlink()
NORMALIZED_MODEL.unlink()
remaining_outputs = sorted(path.name for path in WORKING_ROOT.iterdir() if path.is_file() and not path.name.startswith("__"))
all_working_files = sorted(path.name for path in WORKING_ROOT.iterdir() if path.is_file())
print("all_working_files_after_cleanup:", all_working_files)
print("working_output_files_after_cleanup:", remaining_outputs)
if remaining_outputs != ["submission.zip"]:
    raise SystemExit(f"ERROR: unexpected files left in /kaggle/working: {remaining_outputs!r}")
print("OK: /kaggle/working/submission.zip is ready.")
print("OK: normalized adapter config and zero-tensor-stripped safetensors were used.")
'''
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "id": "stage5-v2-title",
                "metadata": {},
                "source": [
                    "# Nemotron Huikang v27 Normalized Repack\n",
                    "\n",
                    "This notebook creates a metadata-normalized adapter package after the raw repack failed the official evaluator. It does not train, load a base model, or submit to the competition.\n",
                ],
            },
            {
                "cell_type": "code",
                "id": "stage5-v2-repack",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [line + "\n" for line in source.splitlines()],
            },
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def validate_no_forbidden_notebook_text(text: str) -> None:
    forbidden = [
        "kaggle competitions submit",
        "kaggle.json",
        "AutoModel",
        "PeftModel",
        "from_pretrained",
        "TrainingArguments",
        "torch.cuda",
    ]
    lower = text.lower()
    for item in forbidden:
        if item.lower() in lower:
            raise SystemExit(f"generated notebook contains forbidden text: {item}")


def write_adjustment_report(kaggle_user: str, kernel_slug: str, output_dir: Path) -> None:
    kernel_id = f"{kaggle_user}/{kernel_slug}"
    rel_output = output_dir.relative_to(PROJECT_ROOT).as_posix()
    content = f"""# Kaggle-side Notebook V2 Adjustment

- status: prepared
- kernel_id: `{kernel_id}`
- kernel_dir: `{rel_output}`
- model_source: `{MODEL_SOURCE}`
- competition: `{COMPETITION}`
- no_competition_submit: true
- no_base_model_loading: true
- no_training: true

## Why V2 Exists

Two official submissions built from the raw Kaggle-side repack failed with `Evaluation metric raised an unexpected error`. The raw notebook successfully mounted the adapter and produced a large `submission.zip`, so the failure is more likely an official evaluator loading or metadata compatibility issue than a notebook resource issue.

## V2 Changes

1. Reads the safetensors header with Python standard library only.
2. Derives explicit LoRA `target_modules` from nonzero LoRA tensor names instead of leaving `target_modules` as `all-linear`.
3. Sets missing `base_model_name_or_path` to `{BASE_MODEL_NAME}`.
4. Sets `inference_mode` to `true`.
5. Removes zero-size safetensors entries before packaging. The local header audit found zero-size `w3` LoRA tensors in the raw adapter.
6. Uses `ZIP_DEFLATED` instead of `ZIP_STORED` to reduce output size.
7. Deletes temporary normalized files after zipping so Kaggle Output only exposes `submission.zip`.

## Generate

```powershell
python scripts\\23_make_kaggle_repack_notebook_v2.py --kaggle-user {kaggle_user}
```

## Push Notebook Only

```powershell
python scripts\\21_push_kaggle_notebook.py --kernel-dir "{rel_output}"
```

## Check Output

```powershell
kaggle kernels status {kernel_id}
kaggle kernels files {kernel_id}
kaggle kernels logs {kernel_id}
```

## Manual Submit Boundary

Only submit manually from Kaggle Notebook Output after confirming the v2 log contains:

```text
OK: normalized adapter config and zero-tensor-stripped safetensors were used.
```

Do not submit the v1 raw repack again.
"""
    write_text(PROJECT_ROOT / "reports" / "KAGGLE_SIDE_NOTEBOOK_V2_ADJUSTMENT.md", content)


if __name__ == "__main__":
    raise SystemExit(main())
