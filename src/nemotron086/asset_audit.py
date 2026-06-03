from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from .provenance import ensure_dir, write_json
from .reporting import markdown_table, write_text


UNKNOWN = "unknown"


def audit_assets(project_root: Path) -> dict[str, Any]:
    config_path = project_root / "configs" / "public_baselines.yaml"
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    baselines = config.get("baselines") or {}
    external_dir = ensure_dir(project_root / "external")

    records = []
    for name, item in baselines.items():
        records.append(_audit_one(name, item or {}, external_dir))

    summary = Counter(record["classification"] for record in records)
    result = {
        "audit_mode": "stage1_static_or_local_only",
        "records": records,
        "summary": dict(summary),
        "candidate_adapter_found": any(record["classification"] == "candidate_adapter" for record in records),
    }

    write_json(external_dir / "public_baselines_index.json", result)
    write_json(ensure_dir(external_dir / "public_baselines") / "index.json", result)
    reports_dir = ensure_dir(project_root / "reports")
    write_text(reports_dir / "ASSET_AUDIT.md", render_asset_audit(result))
    write_text(reports_dir / "PUBLIC_BASELINE_REPRO_STATUS.md", render_repro_status(result))
    return result


def _audit_one(name: str, item: dict[str, Any], external_dir: Path) -> dict[str, Any]:
    local_dir = external_dir / name
    local_files = []
    if local_dir.exists():
        local_files = [path for path in local_dir.rglob("*") if path.is_file() and path.name != ".gitkeep"]

    local_asset_found = bool(local_files)
    has_adapter_config = (local_dir / "adapter_config.json").exists()
    has_adapter_model = (local_dir / "adapter_model.safetensors").exists()
    local_adapter_found = has_adapter_config and has_adapter_model

    url = item.get("url")
    adapter_url = item.get("adapter_url")
    dataset_url = item.get("dataset_url")
    license_url = item.get("license_url")
    type_hint = item.get("type_hint") or item.get("type") or UNKNOWN

    source_code_available = True if url else UNKNOWN
    dataset_available = True if dataset_url else UNKNOWN
    adapter_available: bool | str = True if (adapter_url or local_adapter_found) else UNKNOWN
    license_status = "known" if license_url else UNKNOWN

    classification = _classify(type_hint, local_adapter_found, bool(url), bool(dataset_url), bool(adapter_url))
    allowed_use = "reference_only" if license_status == UNKNOWN else _allowed_use_for(classification)
    blocking_issue = _blocking_issue(classification, license_status, adapter_available, source_code_available, dataset_available)

    return {
        "name": name,
        "type_hint": type_hint,
        "claimed_score_range": item.get("claimed_score_range") or item.get("expected_score_range") or UNKNOWN,
        "url": url,
        "adapter_url": adapter_url,
        "dataset_url": dataset_url,
        "license_url": license_url,
        "local_asset_found": local_asset_found,
        "local_asset_path": str(local_dir) if local_dir.exists() else None,
        "adapter_available": adapter_available,
        "source_code_available": source_code_available,
        "dataset_available": dataset_available,
        "license_status": license_status,
        "classification": classification,
        "allowed_use": allowed_use,
        "blocking_issue": blocking_issue,
        "next_required_manual_action": _next_action(classification, blocking_issue),
    }


def _classify(type_hint: str, local_adapter: bool, has_url: bool, has_dataset: bool, has_adapter_url: bool) -> str:
    if local_adapter or has_adapter_url:
        return "candidate_adapter"
    if type_hint == "conversion_baseline":
        return "conversion_only"
    if type_hint == "trainable_baseline":
        if has_url and has_dataset:
            return "trainable_baseline"
        return "needs_manual_asset"
    if type_hint in {"score_claim_reference", "dependent_improvement", "training_stack_variant", "optimizer_variant", "specialist_baseline"}:
        return "idea_only"
    return "needs_manual_asset"


def _allowed_use_for(classification: str) -> str:
    mapping = {
        "candidate_adapter": "structural_validation_packaging",
        "trainable_baseline": "stage2_candidate_after_manual_review",
        "conversion_only": "conversion_reference_only",
        "idea_only": "reference_only",
        "needs_manual_asset": "reference_only",
        "blocked": "do_not_use",
    }
    return mapping.get(classification, "reference_only")


def _blocking_issue(classification: str, license_status: str, adapter_available: Any, source_code_available: Any, dataset_available: Any) -> str | None:
    if license_status == UNKNOWN:
        return "license_unknown"
    if classification == "conversion_only" and adapter_available is not True:
        return "original_adapter_missing"
    if classification == "needs_manual_asset":
        return "source_url_or_local_asset_missing"
    if classification == "trainable_baseline" and (source_code_available is not True or dataset_available is not True):
        return "trainable_assets_incomplete"
    return None


def _next_action(classification: str, blocking_issue: str | None) -> str:
    if classification == "candidate_adapter" and blocking_issue is None:
        return "run scripts/02_validate_adapter.py with the local adapter path"
    if classification == "conversion_only":
        return "manually provide the original adapter before conversion can matter"
    if blocking_issue == "license_unknown":
        return "manually fill license_url and source URL fields"
    return "manually fill url, adapter_url, dataset_url, and license_url if available"


def render_asset_audit(result: dict[str, Any]) -> str:
    rows = [
        [
            record["name"],
            record["type_hint"],
            record["claimed_score_range"],
            record["local_asset_found"],
            record["adapter_available"],
            record["license_status"],
            record["classification"],
            record["allowed_use"],
            record["blocking_issue"],
        ]
        for record in result["records"]
    ]
    return f"""# Asset Audit

- audit_mode: {result['audit_mode']}
- candidate_adapter_found: {result['candidate_adapter_found']}

{markdown_table(['name', 'type_hint', 'claimed_score_range', 'local_asset_found', 'adapter_available', 'license_status', 'classification', 'allowed_use', 'blocking_issue'], rows)}
"""


def render_repro_status(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Public Baseline Repro Status",
        "",
        f"- trainable_baselines: {summary.get('trainable_baseline', 0)}",
        f"- conversion_only_baselines: {summary.get('conversion_only', 0)}",
        f"- candidate_adapters: {summary.get('candidate_adapter', 0)}",
        f"- idea_only_routes: {summary.get('idea_only', 0)}",
        f"- needs_manual_asset: {summary.get('needs_manual_asset', 0)}",
        f"- blocked_routes: {summary.get('blocked', 0)}",
        "",
        "NEXT_ACTION:",
        "  status: stay_stage1",
        '  action: "manually fill url fields in configs/public_baselines.yaml"',
        '  reason: "all 0.86 routes are currently asset-unknown unless local assets are added"',
        "",
    ]
    return "\n".join(lines)
