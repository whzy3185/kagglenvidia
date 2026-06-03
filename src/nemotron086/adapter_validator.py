from __future__ import annotations

import json
import struct
from pathlib import Path
from typing import Any

from .provenance import ensure_dir, sha256_file, write_json
from .reporting import write_text


MAX_RANK = 32


def validate_adapter(
    adapter_dir: Path,
    project_root: Path,
    output_dir: Path | None = None,
    write_reports: bool = True,
) -> dict[str, Any]:
    adapter_dir = adapter_dir.resolve()
    output_dir = output_dir or project_root / "artifacts" / "validation"
    report: dict[str, Any] = {
        "adapter_dir": str(adapter_dir),
        "structural_valid": False,
        "official_model_load_tested": False,
        "official_format_confirmed": False,
        "base_model_loaded": False,
        "rank_lte_32": False,
        "safetensors_opened": False,
        "checks": {},
        "errors": [],
        "files": {},
    }

    config_path = adapter_dir / "adapter_config.json"
    model_path = adapter_dir / "adapter_model.safetensors"
    report["checks"]["adapter_dir_exists"] = adapter_dir.exists() and adapter_dir.is_dir()
    report["checks"]["adapter_config_exists"] = config_path.exists()
    report["checks"]["adapter_model_safetensors_exists"] = model_path.exists()

    config: dict[str, Any] = {}
    if report["checks"]["adapter_config_exists"]:
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            report["checks"]["adapter_config_parseable"] = True
            report["files"]["adapter_config.json"] = {"sha256": sha256_file(config_path), "size": config_path.stat().st_size}
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            report["checks"]["adapter_config_parseable"] = False
            report["errors"].append(f"adapter_config_json_parse_failed: {exc}")
    else:
        report["checks"]["adapter_config_parseable"] = False

    rank = _extract_rank(config)
    target_modules = config.get("target_modules")
    report["config_rank"] = rank
    report["target_modules"] = target_modules
    report["rank_lte_32"] = isinstance(rank, int) and rank <= MAX_RANK
    report["checks"]["target_modules_non_empty"] = bool(target_modules)

    safetensors_header: dict[str, Any] | None = None
    inferred = {"status": "not_checked", "ranks": [], "max_rank": None, "matches_config": None}
    if report["checks"]["adapter_model_safetensors_exists"]:
        try:
            safetensors_header = read_safetensors_header(model_path)
            report["safetensors_opened"] = True
            report["files"]["adapter_model.safetensors"] = {"sha256": sha256_file(model_path), "size": model_path.stat().st_size}
            inferred = infer_rank_from_safetensors_header(safetensors_header, rank)
        except Exception as exc:  # noqa: BLE001 - report exact structural open failure
            report["safetensors_opened"] = False
            report["errors"].append(f"safetensors_open_failed: {exc}")

    report["rank_inference"] = inferred
    rank_inference_ok = inferred["status"] in {"matched", "not_found", "no_config_rank"}
    if inferred["status"] == "mismatch":
        report["errors"].append("safetensors_inferred_rank_mismatch")
    if inferred["max_rank"] is not None and inferred["max_rank"] > MAX_RANK:
        report["errors"].append("safetensors_inferred_rank_gt_32")
        rank_inference_ok = False

    required_checks = [
        report["checks"]["adapter_dir_exists"],
        report["checks"]["adapter_config_exists"],
        report["checks"]["adapter_model_safetensors_exists"],
        report["checks"]["adapter_config_parseable"],
        report["rank_lte_32"],
        report["checks"]["target_modules_non_empty"],
        report["safetensors_opened"],
        rank_inference_ok,
    ]
    report["structural_valid"] = all(required_checks)

    if write_reports:
        output_dir = ensure_dir(output_dir)
        json_path = output_dir / "validate_report.json"
        md_path = output_dir / "validate_report.md"
        write_json(json_path, report)
        write_text(md_path, render_validation_report(report))
        report["json_report_path"] = str(json_path.relative_to(project_root))
        report["markdown_report_path"] = str(md_path.relative_to(project_root))
    else:
        report["json_report_path"] = None
        report["markdown_report_path"] = None
    return report


def _extract_rank(config: dict[str, Any]) -> int | None:
    for key in ("r", "rank", "lora_rank"):
        value = config.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return None


def read_safetensors_header(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        raw_length = handle.read(8)
        if len(raw_length) != 8:
            raise ValueError("file_too_small_for_safetensors_header")
        header_len = struct.unpack("<Q", raw_length)[0]
        if header_len <= 0:
            raise ValueError("invalid_safetensors_header_length")
        if header_len > path.stat().st_size:
            raise ValueError("safetensors_header_length_exceeds_file_size")
        raw_header = handle.read(header_len)
    return json.loads(raw_header.decode("utf-8"))


def infer_rank_from_safetensors_header(header: dict[str, Any], config_rank: int | None) -> dict[str, Any]:
    ranks: list[int] = []
    for name, meta in header.items():
        if name == "__metadata__" or not isinstance(meta, dict):
            continue
        shape = meta.get("shape")
        if not isinstance(shape, list) or len(shape) < 2:
            continue
        lower = name.lower()
        if "lora_a" in lower:
            ranks.append(int(shape[-2] if len(shape) >= 3 else shape[0]))
        elif "lora_b" in lower:
            ranks.append(int(shape[-1] if len(shape) >= 3 else shape[1]))
        elif "lora" in lower:
            ranks.append(int(min(shape)))

    unique_ranks = sorted(set(ranks))
    max_rank = max(unique_ranks) if unique_ranks else None
    if not unique_ranks:
        status = "not_found"
        matches = None
    elif config_rank is None:
        status = "no_config_rank"
        matches = None
    elif all(rank == config_rank for rank in unique_ranks):
        status = "matched"
        matches = True
    else:
        status = "mismatch"
        matches = False
    return {"status": status, "ranks": unique_ranks, "max_rank": max_rank, "matches_config": matches}


def render_validation_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- {key}: {value}" for key, value in report["checks"].items())
    errors = "\n".join(f"- {error}" for error in report["errors"]) if report["errors"] else "- null"
    return f"""# Adapter Validation Report

- adapter_dir: `{report['adapter_dir']}`
- structural_valid: {report['structural_valid']}
- official_model_load_tested: false
- official_format_confirmed: false
- base_model_loaded: false
- rank_lte_32: {report['rank_lte_32']}
- safetensors_opened: {report['safetensors_opened']}
- config_rank: {report.get('config_rank')}
- rank_inference_status: {report['rank_inference']['status']}
- rank_inference_ranks: {report['rank_inference']['ranks']}

## Checks

{checks}

## Errors

{errors}
"""
