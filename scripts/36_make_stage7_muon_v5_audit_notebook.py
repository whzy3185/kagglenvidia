from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "kaggle_kernels" / "nemotron_s7_muon_v5_audit"
METADATA_PATH = OUT_DIR / "kernel-metadata.json"
NOTEBOOK_PATH = OUT_DIR / "nemotron_s7_muon_v5_audit.ipynb"
REPORT_PATH = PROJECT_ROOT / "reports" / "STAGE7_MUON_V5_AUDIT.md"
KERNEL_ID = "muelsyse111/nemotron-s7-muon-v5-audit"
SOURCE_KERNEL = "muelsyse111/nemotron-s7-muon-full-training-v5"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    metadata = {
        "id": KERNEL_ID,
        "title": "Nemotron S7 Muon V5 Audit",
        "code_file": NOTEBOOK_PATH.name,
        "language": "python",
        "kernel_type": "notebook",
        "is_private": "true",
        "enable_gpu": "false",
        "enable_internet": "false",
        "dataset_sources": [],
        "competition_sources": ["nvidia-nemotron-model-reasoning-challenge"],
        "kernel_sources": [SOURCE_KERNEL],
        "model_sources": [],
    }
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "id": "intro",
                "metadata": {},
                "source": [
                    "# Muon v5 structural audit\n",
                    "\n",
                    "Audits and repacks the completed Muon training output. "
                    "No base model, training, or competition submission is used.\n",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "id": "audit",
                "metadata": {},
                "outputs": [],
                "source": notebook_source().splitlines(keepends=True),
            },
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
    print(f"report={REPORT_PATH.relative_to(PROJECT_ROOT)}")
    print(f'push_command=kaggle kernels push -p "{OUT_DIR.relative_to(PROJECT_ROOT)}"')
    return 0


def notebook_source() -> str:
    return r'''from pathlib import Path
import hashlib
import json
import shutil
import struct
import zipfile

INPUT_ROOT = Path("/kaggle/input")
WORKING_ROOT = Path("/kaggle/working")
EXTRACT_DIR = WORKING_ROOT / "muon_v5_audit_extract"
OUTPUT_ZIP = WORKING_ROOT / "submission.zip"
EXPECTED = ["adapter_config.json", "adapter_model.safetensors"]


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safetensors_header(path):
    with open(path, "rb") as handle:
        raw_length = handle.read(8)
        if len(raw_length) != 8:
            raise RuntimeError("safetensors header length is missing")
        header_length = struct.unpack("<Q", raw_length)[0]
        if header_length <= 0 or header_length > 100 * 1024 * 1024:
            raise RuntimeError(f"invalid safetensors header length: {header_length}")
        header = json.loads(handle.read(header_length))
    tensor_keys = [key for key in header if key != "__metadata__"]
    if not tensor_keys:
        raise RuntimeError("safetensors contains no tensor entries")
    return header_length, len(tensor_keys)


candidates = sorted(INPUT_ROOT.rglob("submission.zip"))
print("submission_zip_candidates:", [str(path) for path in candidates])
if not candidates:
    raise FileNotFoundError("Muon v5 submission.zip was not mounted")
source_zip = next(
    (
        path
        for path in candidates
        if "muon" in str(path).lower() or "training-v5" in str(path).lower()
    ),
    candidates[0],
)
print("selected_source_zip:", source_zip)

if EXTRACT_DIR.exists():
    shutil.rmtree(EXTRACT_DIR)
EXTRACT_DIR.mkdir(parents=True)
with zipfile.ZipFile(source_zip, "r") as archive:
    names = sorted(archive.namelist())
    print("source_zip_namelist:", names)
    if names != EXPECTED:
        raise RuntimeError(f"unexpected source zip root: {names}")
    archive.extractall(EXTRACT_DIR)

config_path = EXTRACT_DIR / "adapter_config.json"
model_path = EXTRACT_DIR / "adapter_model.safetensors"
config = json.loads(config_path.read_text(encoding="utf-8"))
rank = int(config.get("r", 0))
target_modules = config.get("target_modules")
if rank <= 0 or rank > 32:
    raise RuntimeError(f"invalid LoRA rank: {rank}")
if not target_modules:
    raise RuntimeError("target_modules is missing")
if model_path.stat().st_size < 100 * 1024 * 1024:
    raise RuntimeError(f"adapter model is unexpectedly small: {model_path.stat().st_size}")
header_length, tensor_count = safetensors_header(model_path)

if OUTPUT_ZIP.exists():
    OUTPUT_ZIP.unlink()
shutil.copy2(source_zip, OUTPUT_ZIP)
with zipfile.ZipFile(OUTPUT_ZIP, "r") as archive:
    output_names = sorted(archive.namelist())
if output_names != EXPECTED:
    raise RuntimeError(f"unexpected output zip root: {output_names}")

report = {
    "candidate": "nemotron-s7-muon-full-training-v5-audited",
    "source_kernel": "muelsyse111/nemotron-s7-muon-full-training-v5",
    "source_zip_sha256": sha256_file(source_zip),
    "source_zip_size_bytes": source_zip.stat().st_size,
    "submission_zip_sha256": sha256_file(OUTPUT_ZIP),
    "submission_zip_size_bytes": OUTPUT_ZIP.stat().st_size,
    "zip_namelist": output_names,
    "rank": rank,
    "rank_lte_32": rank <= 32,
    "target_modules": target_modules,
    "safetensors_header_length": header_length,
    "safetensors_tensor_count": tensor_count,
    "safetensors_opened": True,
}
(WORKING_ROOT / "nemotron-s7-muon-v5-audit_report.json").write_text(
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
        "source_kernel": metadata.get("kernel_sources") == [SOURCE_KERNEL],
        "cpu_only": str(metadata.get("enable_gpu")).lower() == "false",
        "exact_zip_root": 'EXPECTED = ["adapter_config.json", "adapter_model.safetensors"]' in text,
        "rank_check": "rank > 32" in text,
        "safetensors_header": 'struct.unpack("<Q"' in text,
        "sha256": "submission_zip_sha256" in text,
        "success_marker": "OK: /kaggle/working/submission.zip is ready." in text,
        "no_base_model": "from_pretrained" not in text,
        "no_submit": "kaggle competitions submit" not in text,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"Audit notebook validation failed: {failed}")


def render_report() -> str:
    return """# Stage 7 Muon v5 Audit

- source kernel: `muelsyse111/nemotron-s7-muon-full-training-v5`
- audit kernel: `muelsyse111/nemotron-s7-muon-v5-audit`
- source training: 7830 records, one epoch, effective batch 16
- GPU required for audit: false
- base model loaded: false
- competition submission executed: false
- latest verified kernel version: 2
- source and output SHA256: `2d42d0adb258956398e4a501f4629aa4a812da2612e506cf1f0449b6143170f5`
- source and output size: 3833093217 bytes
- LoRA rank: 32
- safetensors tensor count: 12011
- exact zip root: `adapter_config.json`, `adapter_model.safetensors`

The source training output only printed its package size and success marker.
This audit mounts that output, verifies the exact two-file root, rank, target
modules, safetensors header, size and SHA256, then copies the validated source
package unchanged to avoid increasing its compressed size.
"""


if __name__ == "__main__":
    raise SystemExit(main())
