from __future__ import annotations

import json
from pathlib import Path


OUT = Path("/kaggle/working")


def main() -> None:
    manifest = {
        "stage": 2,
        "status": "staging_only",
        "adapter_generated": False,
        "message": "No training assets wired yet; no adapter is fabricated.",
    }
    (OUT / "repro_report.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (OUT / "candidate_card.md").write_text("# Candidate Card\n\nNo adapter generated.\n", encoding="utf-8")
    (OUT / "provenance.json").write_text(json.dumps({"sources": []}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
