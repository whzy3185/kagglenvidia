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


DEFAULT_KERNEL_SLUG = "nemotron-repack-huikang-v27"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "kaggle_kernels" / "nemotron_repack_huikang_v27"
MODEL_SOURCE = "huikang/nemotron-adapter/Transformers/default/27"
COMPETITION = "nvidia-nemotron-model-reasoning-challenge"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Kaggle-side adapter repack notebook.")
    parser.add_argument("--kaggle-user", required=True, help="Kaggle username used in kernel-metadata.json id.")
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

    code_file = notebook_filename(kernel_slug)
    metadata_path = output_dir / "kernel-metadata.json"
    notebook_path = output_dir / code_file

    metadata = build_metadata(kaggle_user, kernel_slug, code_file)
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    notebook_path.write_text(json.dumps(build_notebook(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    validate_notebook_text(notebook_path.read_text(encoding="utf-8"))
    write_workflow_report(kaggle_user, kernel_slug, output_dir)
    write_manual_checklist(kaggle_user, kernel_slug)
    write_initial_push_report(kaggle_user, kernel_slug, output_dir)

    relative_output = output_dir.relative_to(PROJECT_ROOT).as_posix()
    print(f"kernel directory: {relative_output}")
    print(f"metadata path: {(metadata_path.relative_to(PROJECT_ROOT)).as_posix()}")
    print(f"notebook path: {(notebook_path.relative_to(PROJECT_ROOT)).as_posix()}")
    print(f"next push command: python scripts\\21_push_kaggle_notebook.py --kernel-dir \"{relative_output}\"")
    return 0


def notebook_filename(kernel_slug: str) -> str:
    return f"{kernel_slug.replace('-', '_')}.ipynb"


def build_metadata(kaggle_user: str, kernel_slug: str, code_file: str) -> dict[str, Any]:
    return {
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


def build_notebook() -> dict[str, Any]:
    source = """from pathlib import Path
import json
import zipfile
import hashlib
import os
import sys

INPUT_ROOT = Path("/kaggle/input")
WORKING_ROOT = Path("/kaggle/working")
SUBMISSION_ZIP = WORKING_ROOT / "submission.zip"
EXPECTED_ZIP_NAMES = ["adapter_config.json", "adapter_model.safetensors"]


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


print("Kaggle-side Nemotron adapter repack")
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
    print(
        idx,
        "dir=",
        candidate["dir"],
        "model_exists=",
        candidate["model_exists"],
    )

valid_candidates = [candidate for candidate in candidates if candidate["model_exists"]]
if not valid_candidates:
    raise SystemExit("ERROR: no adapter_config.json with sibling adapter_model.safetensors was found.")

selected = sorted(valid_candidates, key=lambda item: (-candidate_score(item), str(item["dir"])))[0]
config_path = selected["config"]
model_path = selected["model"]
print("selected_adapter_dir:", selected["dir"])

config = json.loads(config_path.read_text(encoding="utf-8"))
peft_type = config.get("peft_type")
rank = config.get("r")
base_model = config.get("base_model_name_or_path")
print("peft_type:", peft_type)
print("r:", rank)
print("base_model_name_or_path:", base_model)

if rank is not None:
    try:
        rank_int = int(rank)
    except Exception as exc:
        raise SystemExit(f"ERROR: adapter rank r is not an integer: {rank!r}") from exc
    if rank_int > 32:
        raise SystemExit(f"ERROR: adapter rank r={rank_int} exceeds competition limit 32.")
else:
    print("WARNING: adapter rank r is missing; zip will be built after structural file checks only.")

WORKING_ROOT.mkdir(parents=True, exist_ok=True)
if SUBMISSION_ZIP.exists():
    SUBMISSION_ZIP.unlink()

with zipfile.ZipFile(SUBMISSION_ZIP, "w", compression=zipfile.ZIP_STORED) as zf:
    zf.write(config_path, arcname="adapter_config.json")
    zf.write(model_path, arcname="adapter_model.safetensors")

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
print("OK: /kaggle/working/submission.zip is ready.")
"""
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Nemotron Huikang v27 Kaggle-side Repack\n",
                    "\n",
                    "This notebook repacks the mounted public adapter into `/kaggle/working/submission.zip`. It does not train, load a base model, or submit to the competition.\n",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [line + "\n" for line in source.splitlines()],
            },
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def validate_notebook_text(text: str) -> None:
    forbidden = [
        "kaggle competitions submit",
        "kaggle.json",
        "AutoModel",
        "PeftModel",
        "from_pretrained",
        "trainer",
        "TrainingArguments",
        "torch.cuda",
    ]
    lower_text = text.lower()
    for item in forbidden:
        if item.lower() in lower_text:
            raise SystemExit(f"generated notebook contains forbidden text: {item}")


def write_workflow_report(kaggle_user: str, kernel_slug: str, output_dir: Path) -> None:
    kernel_id = f"{kaggle_user}/{kernel_slug}"
    rel_output = output_dir.relative_to(PROJECT_ROOT).as_posix()
    content = f"""# Kaggle-side Notebook Workflow

## Purpose

The local `submission.zip` is about 1.3 GB, so uploading it from the local machine is slow and fragile. This workflow uploads only a small Kaggle Notebook project. Kaggle mounts the public adapter model and creates `submission.zip` in `/kaggle/working`.

## Stages

1. notebook-only: generate `kernel-metadata.json` and the repack notebook locally.
2. push-notebook: push the small notebook project to Kaggle with Kaggle CLI.
3. manual-submit: open the Kaggle Notebook output and manually submit `submission.zip`.

## Generate Notebook

```powershell
python scripts\\20_make_kaggle_repack_notebook.py --kaggle-user {kaggle_user}
```

Generated directory:

```text
{rel_output}
```

## Push Notebook

```powershell
python scripts\\21_push_kaggle_notebook.py --kernel-dir "{rel_output}"
```

Equivalent Kaggle CLI command:

```powershell
kaggle kernels push -p "{rel_output}"
```

## Check Status

```powershell
kaggle kernels status {kernel_id}
```

## Check Output Files

```powershell
kaggle kernels files {kernel_id}
```

Expected output includes:

```text
submission.zip
```

## Manual Submit

Open the Kaggle Notebook page, then use:

```text
Notebook -> Output -> submission.zip -> Submit to Competition
```

This manual action is the only step that should consume competition submission quota.

## Safety Boundaries

- Does not call competition submit.
- Does not consume submission quota during notebook generation or push.
- Does not store tokens.
- Does not upload `kaggle.json`.
- Does not train.
- Does not load the base model.
- Does not use GPU.
- Does not upload the local 1.3 GB `submission.zip`.

## Failure Checks

- Add Input did not mount `huikang/nemotron-adapter/Transformers/default/27`.
- `model_sources` did not take effect.
- `adapter_config.json` or `adapter_model.safetensors` was not found under `/kaggle/input`.
- Zip root contains nested directories or unexpected files.
- Adapter rank `r` is greater than 32.
- Kaggle CLI is not logged in.
- `kaggle kernels push` failed.
"""
    write_text(PROJECT_ROOT / "reports" / "KAGGLE_SIDE_NOTEBOOK_WORKFLOW.md", content)


def write_manual_checklist(kaggle_user: str, kernel_slug: str) -> None:
    kernel_id = f"{kaggle_user}/{kernel_slug}"
    content = f"""# Manual Submission Checklist

Kernel id:

```text
{kernel_id}
```

## Before Manual Submit

- Notebook run is complete.
- Output contains `submission.zip`.
- Notebook log contains `OK: /kaggle/working/submission.zip is ready.`
- Zip contents are exactly:
  - `adapter_config.json`
  - `adapter_model.safetensors`
- Adapter rank `r <= 32`.
- No script executed competition submit automatically.
- Kaggle competition submission quota is sufficient.
- The notebook mounted `huikang/nemotron-adapter/Transformers/default/27`.

## Manual Submit Path

```text
Kaggle Notebook -> Output -> submission.zip -> Submit to Competition
```

## After Submit Record

- submission id:
- message:
- status:
- public score:
- error message:
- enter Stage 6: yes/no

## If Submission Errors

- Do not repeat-submit immediately.
- Check zip root structure.
- Check adapter rank.
- Check adapter file completeness.
- Check notebook output logs.
- Confirm the mounted model source is the intended Huikang v27 adapter.
"""
    write_text(PROJECT_ROOT / "reports" / "MANUAL_SUBMISSION_CHECKLIST.md", content)


def write_initial_push_report(kaggle_user: str, kernel_slug: str, output_dir: Path) -> None:
    kernel_id = f"{kaggle_user}/{kernel_slug}"
    rel_output = output_dir.relative_to(PROJECT_ROOT).as_posix()
    content = f"""# Kaggle Notebook Push Report

- status: not_run
- kernel_id: `{kernel_id}`
- kernel_dir: `{rel_output}`
- push_command: `kaggle kernels push -p "{rel_output}"`
- status_check_command: `kaggle kernels status {kernel_id}`
- files_check_command: `kaggle kernels files {kernel_id}`
- note: `Run scripts/21_push_kaggle_notebook.py only when you are ready to push the notebook. This does not submit to the competition.`
"""
    write_text(PROJECT_ROOT / "reports" / "KAGGLE_NOTEBOOK_PUSH_REPORT.md", content)


if __name__ == "__main__":
    raise SystemExit(main())
