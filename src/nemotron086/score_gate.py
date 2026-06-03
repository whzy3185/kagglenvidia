from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .provenance import write_json
from .reporting import write_text


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def evaluate_candidate(project_root: Path, manifest_path: Path) -> dict[str, Any]:
    if not manifest_path.exists():
        return deny("candidate manifest missing", manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    reasons = []
    if not manifest.get("structural_valid", manifest.get("zip_structure_status") == "structural_valid"):
        reasons.append("zip_or_adapter_structure_invalid")
    if manifest.get("rank_lte_32") is False:
        reasons.append("rank_gt_32")
    if manifest.get("official_format_confirmed") is True:
        pass
    if not manifest.get("provenance") and manifest.get("official_format_confirmed") is not True:
        reasons.append("missing_or_unreviewed_provenance")
    provenance = manifest.get("provenance") or {}
    if manifest.get("license_status") == "unknown" or provenance.get("license_status") == "unknown":
        reasons.append("license_unknown")
    if manifest.get("known_score_below_target_without_new_delta"):
        reasons.append("known_score_below_target_without_new_delta")
    allowed = not reasons
    result = {
        "allowed": allowed,
        "reasons": reasons,
        "manifest_path": str(manifest_path),
        "message": "candidate passes static gate" if allowed else "candidate rejected by static gate",
    }
    write_json(project_root / "reports" / "SCORE_GATE_RESULT.json", result)
    write_text(project_root / "reports" / "SCORE_GATE_RESULT.md", render_gate_result(result))
    return result


def deny(reason: str, manifest_path: Path) -> dict[str, Any]:
    return {"allowed": False, "reasons": [reason], "manifest_path": str(manifest_path), "message": reason}


def render_gate_result(result: dict[str, Any]) -> str:
    reasons = "\n".join(f"- {item}" for item in result["reasons"]) if result["reasons"] else "- null"
    return f"""# Score Gate Result

- allowed: {result['allowed']}
- message: {result['message']}
- manifest_path: `{result['manifest_path']}`

## Reasons

{reasons}
"""
