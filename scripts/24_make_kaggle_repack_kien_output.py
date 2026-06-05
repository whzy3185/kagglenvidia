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


DEFAULT_KERNEL_SLUG = "nemotron-repack-kien-output"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "kaggle_kernels" / "nemotron_repack_kien_output"
COMPETITION = "nvidia-nemotron-model-reasoning-challenge"
SOURCE_KERNEL = "kienngx/nvidia-nemotron-training-copy-run-instantly"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Kaggle-side repack notebook for Kien public kernel output.")
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
        "kernel_sources": [SOURCE_KERNEL],
        "model_sources": [],
    }
    metadata_path = output_dir / "kernel-metadata.json"
    notebook_path = output_dir / code_file
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    notebook_path.write_text(json.dumps(build_notebook(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    validate_no_forbidden_text(notebook_path.read_text(encoding="utf-8"))
    write_route_report(kaggle_user, kernel_slug, output_dir)

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

INPUT_ROOT = Path("/kaggle/input")
WORKING_ROOT = Path("/kaggle/working")
SUBMISSION_ZIP = WORKING_ROOT / "submission.zip"
REQUIRED = {"adapter_config.json", "adapter_model.safetensors"}


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_config_from_zip(path):
    with zipfile.ZipFile(path, "r") as zf:
        names = zf.namelist()
        config_name = next((name for name in names if name.endswith("adapter_config.json")), None)
        if not config_name:
            return None, names
        return json.loads(zf.read(config_name).decode("utf-8")), names


def find_member_by_basename(names, basename):
    matches = [name for name in names if Path(name).name == basename and not name.endswith("/")]
    if not matches:
        raise SystemExit(f"ERROR: {basename} not found in source zip")
    return sorted(matches, key=lambda name: (len(Path(name).parts), name))[0]


def copy_zip_member(src_zip, dst_zip, src_name, dst_name):
    with src_zip.open(src_name, "r") as src_handle:
        with dst_zip.open(dst_name, "w", force_zip64=True) as dst_handle:
            while True:
                chunk = src_handle.read(1024 * 1024)
                if not chunk:
                    break
                dst_handle.write(chunk)


def repack_exact_adapter_from_submission_zip(source_zip, output_zip):
    config, names = read_config_from_zip(source_zip)
    if config is None:
        raise SystemExit(f"ERROR: adapter_config.json missing from {source_zip}")
    config_name = find_member_by_basename(names, "adapter_config.json")
    model_name = find_member_by_basename(names, "adapter_model.safetensors")
    with zipfile.ZipFile(source_zip, "r") as src_zf:
        with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_STORED) as dst_zf:
            copy_zip_member(src_zf, dst_zf, config_name, "adapter_config.json")
            copy_zip_member(src_zf, dst_zf, model_name, "adapter_model.safetensors")
    return config, names


def is_valid_submission_zip(path):
    try:
        config, names = read_config_from_zip(path)
    except Exception as exc:
        print("zip_rejected:", path, "reason=", repr(exc))
        return False, None, []
    base_names = {Path(name).name for name in names if not name.endswith("/")}
    if not REQUIRED.issubset(base_names):
        print("zip_rejected:", path, "base_names=", sorted(base_names))
        return False, config, names
    rank = None if config is None else config.get("r")
    if rank is None:
        print("zip_rejected:", path, "missing rank")
        return False, config, names
    if int(rank) > 32:
        print("zip_rejected:", path, "rank>", rank)
        return False, config, names
    return True, config, names


def candidate_score(path):
    text = str(path).lower()
    score = 0
    if "submission.zip" in text:
        score += 10
    if "nvidia-nemotron-training-copy-run-instantly" in text:
        score += 5
    if "adapter" in text:
        score += 2
    return score


def find_adapter_candidates():
    candidates = []
    for config_path in sorted(INPUT_ROOT.rglob("adapter_config.json")):
        model_path = config_path.parent / "adapter_model.safetensors"
        if model_path.exists():
            candidates.append({"dir": config_path.parent, "config": config_path, "model": model_path})
    return candidates


print("Kaggle-side Kien public output repack")
print("input_root:", INPUT_ROOT)
print("working_root:", WORKING_ROOT)
print("python:", sys.version)

if not INPUT_ROOT.exists():
    raise SystemExit("ERROR: /kaggle/input does not exist.")

WORKING_ROOT.mkdir(parents=True, exist_ok=True)
if SUBMISSION_ZIP.exists():
    SUBMISSION_ZIP.unlink()

zip_candidates = sorted(INPUT_ROOT.rglob("submission.zip"))
print("submission_zip_candidates:", [str(path) for path in zip_candidates])
for source_zip in sorted(zip_candidates, key=lambda path: (-candidate_score(path), str(path))):
    ok, config, names = is_valid_submission_zip(source_zip)
    if not ok:
        continue
    config, names = repack_exact_adapter_from_submission_zip(source_zip, SUBMISSION_ZIP)
    print("selected_existing_submission_zip:", source_zip)
    print("source_zip_namelist:", names)
    print("repack_mode:", "exact_adapter_files_only")
    print("source_peft_type:", config.get("peft_type"))
    print("source_r:", config.get("r"))
    print("source_target_modules:", config.get("target_modules"))
    break

if not SUBMISSION_ZIP.exists():
    adapter_candidates = find_adapter_candidates()
    print("adapter_candidates:")
    for index, candidate in enumerate(adapter_candidates, 1):
        print(index, "dir=", candidate["dir"], "model=", candidate["model"])
    if not adapter_candidates:
        raise SystemExit("ERROR: no adapter_config.json with sibling adapter_model.safetensors found.")
    selected = sorted(adapter_candidates, key=lambda item: (-candidate_score(item["dir"]), str(item["dir"])))[0]
    config = json.loads(selected["config"].read_text(encoding="utf-8"))
    rank = config.get("r")
    if rank is None or int(rank) > 32:
        raise SystemExit(f"ERROR: invalid adapter rank: {rank!r}")
    print("selected_adapter_dir:", selected["dir"])
    print("peft_type:", config.get("peft_type"))
    print("r:", config.get("r"))
    print("target_modules:", config.get("target_modules"))
    print("base_model_name_or_path:", config.get("base_model_name_or_path"))
    with zipfile.ZipFile(SUBMISSION_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
        zf.write(selected["config"], arcname="adapter_config.json")
        zf.write(selected["model"], arcname="adapter_model.safetensors")

with zipfile.ZipFile(SUBMISSION_ZIP, "r") as zf:
    names = sorted(zf.namelist())
base_names = {Path(name).name for name in names if not name.endswith("/")}
print("zip_namelist:", names)
if names != ["adapter_config.json", "adapter_model.safetensors"]:
    raise SystemExit(f"ERROR: zip root must contain exactly adapter_config.json and adapter_model.safetensors: {names!r}")
if not REQUIRED.issubset(base_names):
    raise SystemExit(f"ERROR: required adapter files missing from zip: {sorted(base_names)!r}")
with zipfile.ZipFile(SUBMISSION_ZIP, "r") as zf:
    config_name = next(name for name in zf.namelist() if name.endswith("adapter_config.json"))
    final_config = json.loads(zf.read(config_name).decode("utf-8"))
rank = final_config.get("r")
if rank is None or int(rank) > 32:
    raise SystemExit(f"ERROR: invalid final adapter rank: {rank!r}")

print("final_peft_type:", final_config.get("peft_type"))
print("final_r:", final_config.get("r"))
print("final_target_modules:", final_config.get("target_modules"))
print("final_base_model_name_or_path:", final_config.get("base_model_name_or_path"))
print("submission_zip:", SUBMISSION_ZIP)
print("submission_zip_size_bytes:", SUBMISSION_ZIP.stat().st_size)
print("submission_zip_sha256:", sha256_file(SUBMISSION_ZIP))
print("OK: /kaggle/working/submission.zip is ready.")
print("OK: Kien public notebook output route was used.")
'''
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "id": "kien-route-title",
                "metadata": {},
                "source": [
                    "# Nemotron Kien Public Output Repack\n",
                    "\n",
                    "This notebook mounts Kien's public training notebook output and creates `/kaggle/working/submission.zip`. It does not train, load the base model, or submit to the competition.\n",
                ],
            },
            {
                "cell_type": "code",
                "id": "kien-route-repack",
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


def validate_no_forbidden_text(text: str) -> None:
    forbidden = [
        "kaggle competitions submit",
        "kaggle.json",
        "AutoModel",
        "PeftModel",
        "from_pretrained",
        "TrainingArguments",
        "torch.cuda",
        "trainer.train",
    ]
    lower = text.lower()
    for item in forbidden:
        if item.lower() in lower:
            raise SystemExit(f"generated notebook contains forbidden text: {item}")


def write_route_report(kaggle_user: str, kernel_slug: str, output_dir: Path) -> None:
    kernel_id = f"{kaggle_user}/{kernel_slug}"
    rel_output = output_dir.relative_to(PROJECT_ROOT).as_posix()
    content = f"""# Kien Route Switch Decision

- status: prepared
- previous_route: `huikang_v27`
- previous_route_status: `official_evaluator_failed`
- selected_route: `kien_public_training_output`
- selected_kernel_source: `{SOURCE_KERNEL}`
- new_kernel_id: `{kernel_id}`
- kernel_dir: `{rel_output}`
- no_training: true
- no_base_model_loading: true
- no_competition_submit: true

## Reason

Huikang v27 raw and normalized packages failed official evaluation. Kien's public notebook/model family is a separate public 0.86-style route and exposes adapter outputs from a public training notebook.

## Evidence

- `kaggle kernels files {SOURCE_KERNEL}` lists `adapter_config.json` and `adapter_model.safetensors`.
- The public notebook metadata is `is_private: false`.
- The public notebook uses competition source `nvidia-nemotron-model-reasoning-challenge`.
- This repack notebook mounts the public notebook as `kernel_sources`, not as a private dataset.

## Generate

```powershell
python scripts\\24_make_kaggle_repack_kien_output.py --kaggle-user {kaggle_user}
```

## Push Notebook

```powershell
python scripts\\21_push_kaggle_notebook.py --kernel-dir "{rel_output}"
```

## Check

```powershell
kaggle kernels status {kernel_id}
kaggle kernels files {kernel_id}
kaggle kernels logs {kernel_id}
```

## Submit Boundary

Do not submit until notebook logs show:

```text
OK: /kaggle/working/submission.zip is ready.
OK: Kien public notebook output route was used.
```
"""
    write_text(PROJECT_ROOT / "reports" / "KIEN_ROUTE_SWITCH_DECISION.md", content)


if __name__ == "__main__":
    raise SystemExit(main())
