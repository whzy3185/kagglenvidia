from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from .adapter_validator import validate_adapter
from .provenance import ensure_dir, sha256_file, timestamp_stamp, top_level_regular_files, write_json
from .reporting import write_text


REQUIRED_ROOT_FILES = {"adapter_config.json", "adapter_model.safetensors"}


def pack_submission(
    adapter_dir: Path,
    project_root: Path,
    output_dir: Path | None = None,
    write_validation_reports: bool = True,
) -> dict[str, Any]:
    validation = validate_adapter(adapter_dir, project_root, write_reports=write_validation_reports)
    if not validation["structural_valid"]:
        return {
            "packed": False,
            "status": "validation_failed",
            "validation": validation,
            "zip_path": None,
            "manifest_path": None,
            "pack_report_path": None,
        }

    output_dir = ensure_dir(output_dir or project_root / "artifacts" / "submissions" / timestamp_stamp())
    zip_path = output_dir / "submission.zip"
    files = top_level_regular_files(adapter_dir)
    file_names = {path.name for path in files}
    missing = sorted(REQUIRED_ROOT_FILES - file_names)
    if missing:
        return {
            "packed": False,
            "status": "required_files_missing_after_validation",
            "missing": missing,
            "validation": validation,
            "zip_path": None,
        }

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in files:
            archive.write(file_path, arcname=file_path.name)

    inspection = inspect_zip_structure(zip_path)
    manifest = {
        "zip_structure_status": "structural_valid" if inspection["structural_valid"] else "invalid",
        "official_format_confirmed": False,
        "confirmation_source": None,
        "sha256": sha256_file(zip_path),
        "files": inspection["files"],
    }
    manifest_path = write_json(output_dir / "manifest.json", manifest)
    spec_path = write_text(output_dir / "SUBMISSION_FORMAT_SPEC.md", render_submission_format_spec())
    pack_report_path = write_text(output_dir / "pack_report.md", render_pack_report(zip_path, manifest, validation))

    return {
        "packed": inspection["structural_valid"],
        "status": manifest["zip_structure_status"],
        "validation": validation,
        "zip_path": str(zip_path),
        "manifest_path": str(manifest_path),
        "pack_report_path": str(pack_report_path),
        "submission_format_spec_path": str(spec_path),
        "manifest": manifest,
    }


def inspect_zip_structure(zip_path: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="stage1_zip_inspect_") as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(zip_path, "r") as archive:
            names = archive.namelist()
            archive.extractall(temp_path)
        root_files = {path.name for path in temp_path.iterdir() if path.is_file()}
        nested = [name for name in names if "/" in name.rstrip("/")]
        required_present = REQUIRED_ROOT_FILES.issubset(root_files)
        structural_valid = required_present and not nested
        shutil.rmtree(temp_path, ignore_errors=True)
    return {"structural_valid": structural_valid, "files": names, "nested_entries": nested}


def render_submission_format_spec() -> str:
    return """# Submission Format Spec

Stage 1 structural assumption:

```text
submission.zip
  adapter_config.json
  adapter_model.safetensors
```

official_format_confirmed: false
confirmation_source: null

This is structural-valid only, not official-valid.
"""


def render_pack_report(zip_path: Path, manifest: dict[str, Any], validation: dict[str, Any]) -> str:
    files = "\n".join(f"- {name}" for name in manifest["files"])
    return f"""# Pack Report

- submission_zip: `{zip_path}`
- zip_structure_status: {manifest['zip_structure_status']}
- official_format_confirmed: false
- confirmation_source: null
- sha256: `{manifest['sha256']}`
- validator_structural_valid: {validation['structural_valid']}

## Files

{files}
"""
