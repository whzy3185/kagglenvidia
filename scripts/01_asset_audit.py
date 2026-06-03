from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.asset_audit import audit_assets  # noqa: E402


def main() -> int:
    try:
        result = audit_assets(PROJECT_ROOT)
    except Exception as exc:  # noqa: BLE001
        print(f"asset_audit_failed: {exc}")
        return 3
    print("reports: reports/ASSET_AUDIT.md, reports/PUBLIC_BASELINE_REPRO_STATUS.md")
    print(f"candidate_adapter_found: {result['candidate_adapter_found']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
