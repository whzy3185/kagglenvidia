from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGETS = PROJECT_ROOT / "configs" / "stage7_master_research_targets.yaml"
WORKFLOW_REPORT = PROJECT_ROOT / "reports" / "STAGE7_MASTER_DISCUSSION_RESEARCH.md"
OVERFIT_REPORT = PROJECT_ROOT / "reports" / "PUBLIC_PRIVATE_OVERFIT_SOURCE_REVIEW.md"
STATUS_REPORT = PROJECT_ROOT / "reports" / "STAGE7_RESEARCH_GATE_STATUS.md"

REQUIRED_TOPIC_IDS = [
    "704491",
    "703240",
    "687961",
    "698293",
    "681745",
    "704473",
    "704595",
    "702447",
    "701761",
]

REQUIRED_SIMILAR_COMPETITIONS = [
    "AIMO",
    "ARC Prize",
    "LLM Science Exam",
    "Don't Overfit",
]


def main() -> int:
    checks: list[dict[str, object]] = []
    checks.append(check_exists("targets_config_exists", TARGETS))
    checks.append(check_exists("workflow_report_exists", WORKFLOW_REPORT))
    checks.append(check_exists("public_private_overfit_report_exists", OVERFIT_REPORT))

    targets_text = read_text(TARGETS)
    workflow_text = read_text(WORKFLOW_REPORT)
    combined = targets_text + "\n" + workflow_text

    for topic_id in REQUIRED_TOPIC_IDS:
        checks.append(
            {
                "name": f"topic_{topic_id}_recorded",
                "ok": topic_id in combined,
                "detail": f"required Kaggle discussion topic {topic_id}",
            }
        )

    for item in REQUIRED_SIMILAR_COMPETITIONS:
        checks.append(
            {
                "name": f"similar_competition_{slug(item)}_recorded",
                "ok": item.lower() in combined.lower(),
                "detail": item,
            }
        )

    checks.append(
        {
            "name": "top_leaderboard_accounts_recorded",
            "ok": count_pattern(combined, r"public_score:\s*0\.87|public_score:\s*0\.89|0\.87|0\.89") >= 10,
            "detail": "top leaderboard teams and score bands should be present",
        }
    )
    checks.append(
        {
            "name": "candidate_card_template_recorded",
            "ok": "RESEARCH_BACKED_CANDIDATE_CARD" in workflow_text,
            "detail": "future candidates need source-backed cards",
        }
    )

    passed = all(bool(item["ok"]) for item in checks)
    write_status(checks, passed)
    print(f"research_gate_passed={str(passed).lower()}")
    print(f"status_report={STATUS_REPORT}")
    return 0 if passed else 2


def check_exists(name: str, path: Path) -> dict[str, object]:
    return {"name": name, "ok": path.exists(), "detail": str(path.relative_to(PROJECT_ROOT))}


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def count_pattern(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, flags=re.IGNORECASE))


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def write_status(checks: list[dict[str, object]], passed: bool) -> None:
    lines = [
        "# Stage 7 Research Gate Status",
        "",
        f"- timestamp: {datetime.now().isoformat(timespec='seconds')}",
        f"- research_gate_passed: {str(passed).lower()}",
        "",
        "| check | status | detail |",
        "|---|---|---|",
    ]
    for item in checks:
        status = "pass" if item["ok"] else "fail"
        lines.append(f"| {item['name']} | {status} | {item['detail']} |")
    lines.extend(
        [
            "",
            "## Rule",
            "",
            "If this gate fails, do not design or push a new competition candidate. Continue source research first.",
            "",
            "This script does not call `kaggle competitions submit` and does not consume submission quota.",
            "",
        ]
    )
    STATUS_REPORT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
