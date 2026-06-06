from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.kaggle_cli import query_submission_history  # noqa: E402
from nemotron086.provenance import read_json  # noqa: E402
from nemotron086.reporting import markdown_table, write_text  # noqa: E402
from nemotron086.score_db import fetch_scores, upsert_submissions  # noqa: E402


POLICY_PATH = PROJECT_ROOT / "configs" / "submission_policy.yaml"
PUSH_REPORT_PATH = PROJECT_ROOT / "reports" / "KAGGLE_NOTEBOOK_PUSH_REPORT.md"
CHECKLIST_PATH = PROJECT_ROOT / "reports" / "MANUAL_SUBMISSION_CHECKLIST.md"
MANUAL_FIX_REASON_PATH = PROJECT_ROOT / "reports" / "SLOT1_MANUAL_FIX_REASON.md"
STAGE2_MANIFEST_PATH = PROJECT_ROOT / "artifacts" / "stage2" / "tong_full_repro" / "stage2_manifest.json"
PACK_MANIFEST_PATH = PROJECT_ROOT / "artifacts" / "stage2" / "tong_full_repro" / "submission" / "manifest.json"
SCORE_DB_PATH = PROJECT_ROOT / "logs" / "score.db"
REPORT_PATH = PROJECT_ROOT / "reports" / "DAILY_SUBMISSION_PLAN.md"
STAGE6_CANDIDATE_PATH = PROJECT_ROOT / "configs" / "stage6_candidate_routes.yaml"

KERNEL_ID = "muelsyse111/nemotron-repack-huikang-v27"
KERNEL_DIR = "kaggle_kernels\\nemotron_repack_huikang_v27"
MODEL_SOURCE = "huikang/nemotron-adapter/Transformers/default/27"
KIEN_KERNEL_ID = "muelsyse111/nemotron-repack-kien-output"
KIEN_KERNEL_DIR = "kaggle_kernels\\nemotron_repack_kien_output"
KIEN_SOURCE_KERNEL = "kienngx/nvidia-nemotron-training-copy-run-instantly"
RAUFFAUZAN_KERNEL_ID = "muelsyse111/nemotron-repack-rauffauzan-fusion"
RAUFFAUZAN_KERNEL_DIR = "kaggle_kernels\\nemotron_repack_rauffauzan_fusion"
RAUFFAUZAN_SOURCE_KERNEL = "rauffauzanrambe/lora-adapter-fusion-and-rank-compression-pipeline"
DEDQUOC_KERNEL_ID = "muelsyse111/nemotron-repack-dedquoc-svd-fusion"
DEDQUOC_KERNEL_DIR = "kaggle_kernels\\nemotron_repack_dedquoc_svd_fusion"
DEDQUOC_SOURCE_KERNEL = "dedquoc/nvidia-nmrc-low-rank-svd-lora-adapter-fusion"
MANUAL_SUBMIT_PATH = "Kaggle Notebook -> Output -> submission.zip -> Submit to Competition"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a daily manual submission plan without submitting.")
    parser.add_argument("--no-refresh-history", action="store_true", help="Use existing score.db only; do not query Kaggle CLI.")
    args = parser.parse_args()

    policy = load_policy(POLICY_PATH)
    history_payload = refresh_history(not args.no_refresh_history)
    scores = fetch_scores(SCORE_DB_PATH)
    stage2_manifest = read_json_if_exists(STAGE2_MANIFEST_PATH)
    pack_manifest = read_json_if_exists(PACK_MANIFEST_PATH)
    stage6_candidates = load_yaml_dict(STAGE6_CANDIDATE_PATH)
    push_report = parse_push_report(PUSH_REPORT_PATH)
    if push_report.get("pushed"):
        push_report = merge_kernel_live_status(push_report)
    checklist_exists = CHECKLIST_PATH.exists()
    manual_fix_reason = read_manual_fix_reason(MANUAL_FIX_REASON_PATH)

    candidate = build_current_candidate(stage2_manifest, pack_manifest, push_report, stage6_candidates)
    best_score = current_best_public_score(scores)
    slot1_result = find_slot1_result(history_payload.get("rows", []) + scores, candidate)
    slots = build_slots(policy, history_payload, candidate, slot1_result, manual_fix_reason)
    recommended = build_recommended_action(history_payload, candidate, slots)

    report_payload = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "policy": policy,
        "history": history_payload,
        "best_public_score": best_score,
        "candidate": candidate,
        "slot1_result": slot1_result,
        "manual_fix_reason": manual_fix_reason,
        "slots": slots,
        "manual_checklist_exists": checklist_exists,
        "manual_submit_path": MANUAL_SUBMIT_PATH,
        "recommended": recommended,
        "no_automatic_competition_submission": True,
        "submission_quota_consumed": False,
    }
    write_text(REPORT_PATH, render_report(report_payload))

    print(f"report: {REPORT_PATH.relative_to(PROJECT_ROOT).as_posix()}")
    print(f"today_submission_count: {history_payload.get('today_submission_count')}")
    print(f"today_remaining_quota: {history_payload.get('today_remaining_quota')}")
    print(f"recommended_action: {recommended['action']}")
    return 0 if history_payload.get("query_ok") else 2


def load_policy(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text) or {}
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    hard_limit_match = re.search(r"(?m)^hard_limit_per_day:\s*(\d+)\s*$", text)
    target_match = re.search(r"(?m)^default_target_submissions:\s*(\d+)\s*$", text)
    return {
        "hard_limit_per_day": int(hard_limit_match.group(1)) if hard_limit_match else 5,
        "default_target_submissions": int(target_match.group(1)) if target_match else 1,
        "principle": [],
        "use_all_5_only_if": [],
        "never_submit_for": [],
    }


def load_yaml_dict(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text) or {}
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def refresh_history(refresh: bool) -> dict[str, Any]:
    if refresh:
        result = query_submission_history(PROJECT_ROOT, force=True)
        parsed = result["parsed"]
        upsert_submissions(SCORE_DB_PATH, parsed.get("rows", []))
        return {
            "source": "kaggle_cli",
            "query_ok": result["query_ok"],
            "submission_history_query_status": parsed.get("submission_history_query_status"),
            "today_submission_count": parsed.get("today_submission_count"),
            "today_remaining_quota": parsed.get("today_remaining_quota"),
            "quota_effective_today_submission_count": quota_effective_today_count(parsed.get("rows", [])),
            "quota_effective_today_remaining": max(0, 5 - quota_effective_today_count(parsed.get("rows", []))),
            "today_submission_count_parse_status": parsed.get("today_submission_count_parse_status"),
            "rows": parsed.get("rows", []),
        }

    rows = fetch_scores(SCORE_DB_PATH)
    return {
        "source": "score_db_only",
        "query_ok": True,
        "submission_history_query_status": "not_refreshed",
        "today_submission_count": None,
        "today_remaining_quota": None,
        "quota_effective_today_submission_count": quota_effective_today_count(rows),
        "quota_effective_today_remaining": max(0, 5 - quota_effective_today_count(rows)),
        "today_submission_count_parse_status": "not_refreshed",
        "rows": rows,
    }


def quota_effective_today_count(rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in rows if is_today_row(row) and not is_error_status(row.get("status")))


def is_today_row(row: dict[str, Any]) -> bool:
    today = datetime.now().date().isoformat()
    date_text = str(row.get("date") or row.get("submitted_at") or "")
    return date_text.startswith(today)


def read_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = read_json(path)
    return data if isinstance(data, dict) else {}


def parse_push_report(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "exists": False,
            "kernel_id": KERNEL_ID,
            "pushed": False,
            "output_submission_zip_confirmed": False,
            "status": "missing_report",
        }
    text = path.read_text(encoding="utf-8", errors="replace")
    kernel_id = extract_markdown_value(text, "kernel_id") or extract_markdown_value(text, "kernel id") or KERNEL_ID
    explicit_not_run = re.search(r"(?im)^-\s*status:\s*not_run\s*$", text) is not None
    success_true = re.search(r"(?im)^-\s*success:\s*true\s*$", text) is not None
    success_false = re.search(r"(?im)^-\s*success:\s*false\s*$", text) is not None
    output_zip = "submission.zip" in extract_section(text, "Files Result")
    return {
        "exists": True,
        "kernel_id": kernel_id,
        "pushed": success_true and not explicit_not_run,
        "output_submission_zip_confirmed": output_zip,
        "status": "not_run" if explicit_not_run else "success" if success_true else "failed" if success_false else "unknown",
        "raw_summary": first_lines(text, 20),
    }


def merge_kernel_live_status(push_report: dict[str, Any]) -> dict[str, Any]:
    kernel_id = str(push_report.get("kernel_id") or KERNEL_ID)
    status_result = run_command(["kaggle", "kernels", "status", kernel_id])
    files_result = run_command(["kaggle", "kernels", "files", kernel_id])
    logs_result = run_command(["kaggle", "kernels", "logs", kernel_id])
    files_text = files_result.get("stdout", "") + "\n" + files_result.get("stderr", "")
    logs_text = logs_result.get("stdout", "") + "\n" + logs_result.get("stderr", "")
    output_zip = "submission.zip" in files_text or "OK: /kaggle/working/submission.zip is ready." in logs_text
    return {
        **push_report,
        "live_status_result": status_result,
        "live_files_result": files_result,
        "live_logs_result": {
            **logs_result,
            "stdout": first_lines(logs_result.get("stdout", ""), 80),
            "stderr": first_lines(logs_result.get("stderr", ""), 20),
        },
        "output_submission_zip_confirmed": bool(push_report.get("output_submission_zip_confirmed")) or output_zip,
        "kernel_complete": "COMPLETE" in files_text.upper() or "COMPLETE" in (status_result.get("stdout", "") + status_result.get("stderr", "")).upper(),
    }


def run_command(command: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=120,
        )
        return {
            "command": " ".join(command),
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "ok": completed.returncode == 0,
        }
    except Exception as exc:
        return {
            "command": " ".join(command),
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "ok": False,
        }


def read_manual_fix_reason(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "exists": False,
            "path": path.relative_to(PROJECT_ROOT).as_posix(),
            "accepted": False,
            "text": "",
        }
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    return {
        "exists": True,
        "path": path.relative_to(PROJECT_ROOT).as_posix(),
        "accepted": bool(text),
        "text": text,
    }


def extract_markdown_value(text: str, label: str) -> str | None:
    pattern = rf"(?im)^-\s*{re.escape(label)}:\s*`?([^`\n]+)`?\s*$"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else None


def extract_section(text: str, section: str) -> str:
    match = re.search(rf"(?ims)^##\s+{re.escape(section)}\s*(.*?)(?:^##\s+|\Z)", text)
    return match.group(1) if match else ""


def first_lines(text: str, limit: int) -> str:
    return "\n".join(text.splitlines()[:limit])


def build_current_candidate(stage2: dict[str, Any], pack: dict[str, Any], push: dict[str, Any], stage6_candidates: dict[str, Any]) -> dict[str, Any]:
    selected_stage6 = stage6_candidates.get("selected_candidate")
    if isinstance(selected_stage6, dict) and selected_stage6:
        return build_stage6_candidate(selected_stage6, pick_push_report_for_candidate(push, selected_stage6))
    kernel_id = str(push.get("kernel_id") or "")
    if "nemotron-repack-kien-output" in kernel_id:
        return build_kien_candidate(push)
    if "nemotron-repack-rauffauzan-fusion" in kernel_id:
        return build_public_kernel_candidate(
            push,
            name="rauffauzan_fusion_repack",
            route="rauffauzan_lora_fusion_rank_compression",
            source_kernel=RAUFFAUZAN_SOURCE_KERNEL,
            source_url="https://www.kaggle.com/code/rauffauzanrambe/lora-adapter-fusion-and-rank-compression-pipeline",
            kernel_dir=RAUFFAUZAN_KERNEL_DIR,
            default_kernel_id=RAUFFAUZAN_KERNEL_ID,
        )
    if "nemotron-repack-dedquoc-svd-fusion" in kernel_id:
        return build_public_kernel_candidate(
            push,
            name="dedquoc_svd_fusion_repack",
            route="dedquoc_svd_lora_fusion",
            source_kernel=DEDQUOC_SOURCE_KERNEL,
            source_url="https://www.kaggle.com/code/dedquoc/nvidia-nmrc-low-rank-svd-lora-adapter-fusion",
            kernel_dir=DEDQUOC_KERNEL_DIR,
            default_kernel_id=DEDQUOC_KERNEL_ID,
        )
    return build_huikang_candidate(stage2, pack, push)


def pick_push_report_for_candidate(push: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    desired_kernel_id = str(candidate.get("kernel_id") or "").strip().lower()
    current_kernel_id = str(push.get("kernel_id") or "").strip().lower()
    if desired_kernel_id and desired_kernel_id == current_kernel_id:
        return push
    return {
        "exists": False,
        "kernel_id": candidate.get("kernel_id"),
        "pushed": False,
        "output_submission_zip_confirmed": False,
        "status": "not_pushed_for_selected_candidate",
        "raw_summary": "",
    }


def build_stage6_candidate(selected: dict[str, Any], push: dict[str, Any]) -> dict[str, Any]:
    candidate = build_public_kernel_candidate(
        push,
        name=str(selected.get("name") or "stage6_selected_candidate"),
        route=str(selected.get("route") or "stage6_selected_route"),
        source_kernel=str(selected.get("source_kernel") or selected.get("model_source") or ""),
        source_url=str(selected.get("source_url") or ""),
        kernel_dir=str(selected.get("kernel_dir") or ""),
        default_kernel_id=str(selected.get("kernel_id") or ""),
    )
    selected_hash = str(selected.get("candidate_hash_prefix") or "").strip() or None
    if selected_hash:
        candidate["candidate_hash_prefix"] = selected_hash
        candidate["recommended_manual_message"] = f"slot1_{candidate['name']}_{selected_hash}"
    candidate["slot"] = str(selected.get("slot") or "slot1")
    candidate["candidate_type"] = str(selected.get("candidate_type") or candidate["candidate_type"])
    candidate["mechanism"] = str(selected.get("mechanism") or candidate["mechanism"])
    candidate["structural_valid"] = bool(selected.get("zip_structure_known"))
    candidate["rank_lte_32"] = bool(selected.get("adapter_rank_lte_32"))
    candidate["output_submission_zip_confirmed"] = (
        bool(selected.get("output_available"))
        and push.get("output_submission_zip_confirmed") is True
    )
    candidate["claimed_score"] = selected.get("claimed_score")
    candidate["claimed_rank"] = selected.get("claimed_rank")
    candidate["rank_evidence"] = selected.get("rank_evidence")
    candidate["submit_priority"] = selected.get("submit_priority")
    candidate["route_switch_candidate"] = True
    return candidate


def build_kien_candidate(push: dict[str, Any]) -> dict[str, Any]:
    return build_public_kernel_candidate(
        push,
        name="kien_public_output_repack",
        route="kien_public_training_output",
        source_kernel=KIEN_SOURCE_KERNEL,
        source_url="https://www.kaggle.com/code/kienngx/nvidia-nemotron-training-copy-run-instantly",
        kernel_dir=KIEN_KERNEL_DIR,
        default_kernel_id=KIEN_KERNEL_ID,
    )


def build_public_kernel_candidate(
    push: dict[str, Any],
    name: str,
    route: str,
    source_kernel: str,
    source_url: str,
    kernel_dir: str,
    default_kernel_id: str,
) -> dict[str, Any]:
    logs = ""
    live_logs = push.get("live_logs_result")
    if isinstance(live_logs, dict):
        logs = f"{live_logs.get('stdout', '')}\n{live_logs.get('stderr', '')}"
    sha256 = extract_log_value(logs, "submission_zip_sha256")
    zip_namelist = extract_log_value(logs, "zip_namelist")
    rank = extract_log_value(logs, "final_r") or extract_log_value(logs, "source_r")
    target_modules = extract_log_value(logs, "final_target_modules") or extract_log_value(logs, "source_target_modules")
    ok_ready = "OK: /kaggle/working/submission.zip is ready." in logs
    zip_text = zip_namelist or ""
    exact_two_file_zip = (
        "adapter_config.json" in zip_text
        and "adapter_model.safetensors" in zip_text
        and "README.md" not in zip_text
        and "tokenizer" not in zip_text
    )
    hash_prefix = sha256[:12] if sha256 else None
    return {
        "slot": "slot1",
        "name": name,
        "route": route,
        "model_source": source_kernel,
        "source_url": source_url,
        "candidate_type": "kaggle_side_public_kernel_output_candidate",
        "mechanism": "Kaggle Notebook mounts a public kernel output and repacks only adapter_config.json plus adapter_model.safetensors.",
        "structural_valid": ok_ready and exact_two_file_zip,
        "rank_lte_32": rank is not None and safe_int(rank) is not None and safe_int(rank) <= 32,
        "license_status": "public_kernel_output_reference",
        "local_pack_sha256": sha256 or None,
        "candidate_hash_prefix": hash_prefix,
        "kernel_id": push.get("kernel_id") or default_kernel_id,
        "kernel_dir": kernel_dir,
        "notebook_pushed": push.get("pushed") is True,
        "output_submission_zip_confirmed": push.get("output_submission_zip_confirmed") is True and ok_ready and exact_two_file_zip,
        "push_report_status": push.get("status"),
        "recommended_manual_message": f"slot1_{name}_{hash_prefix or 'hash_unknown'}",
        "manual_web_match_after_utc": local_iso_to_utc_naive_string(extract_markdown_value(push.get("raw_summary", ""), "timestamp") or ""),
        "route_switch_candidate": True,
        "zip_namelist": zip_namelist or None,
        "rank": rank,
        "target_modules": target_modules,
    }


def extract_log_value(text: str, label: str) -> str | None:
    line_match = re.search(rf"(?im)^{re.escape(label)}:\s*(.+?)\s*$", text)
    if line_match:
        return line_match.group(1).strip()
    json_log_match = re.search(rf"(?<![A-Za-z0-9_]){re.escape(label)}:\s*(.+?)(?:\\n|\n|\")", text)
    return json_log_match.group(1).strip() if json_log_match else None


def safe_int(value: Any) -> int | None:
    try:
        return int(str(value).strip())
    except Exception:
        return None


def local_iso_to_utc_naive_string(value: str) -> str | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.astimezone()
        utc_dt = parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return utc_dt.isoformat(sep=" ", timespec="seconds")
    except Exception:
        return None


def build_huikang_candidate(stage2: dict[str, Any], pack: dict[str, Any], push: dict[str, Any]) -> dict[str, Any]:
    sha256 = str(pack.get("sha256") or "")
    hash_prefix = sha256[:12] if sha256 else None
    structural_valid = stage2.get("structural_valid") is True
    rank_lte_32 = stage2.get("rank_lte_32") is True
    return {
        "slot": "slot1",
        "name": "huikang_v27_kaggle_side_repack",
        "route": stage2.get("route") or "tong_full_repro",
        "model_source": stage2.get("model_version_ref") or MODEL_SOURCE,
        "source_url": stage2.get("source_url") or "https://www.kaggle.com/models/huikang/nemotron-adapter",
        "candidate_type": "kaggle_side_manual_submit_candidate",
        "mechanism": "Kaggle Notebook mounts Huikang v27 adapter and builds submission.zip in /kaggle/working.",
        "structural_valid": structural_valid,
        "rank_lte_32": rank_lte_32,
        "license_status": stage2.get("license_status") or "unknown",
        "local_pack_sha256": sha256 or None,
        "candidate_hash_prefix": hash_prefix,
        "kernel_id": push.get("kernel_id") or KERNEL_ID,
        "kernel_dir": KERNEL_DIR,
        "notebook_pushed": push.get("pushed") is True,
        "output_submission_zip_confirmed": push.get("output_submission_zip_confirmed") is True,
        "push_report_status": push.get("status"),
        "recommended_manual_message": f"slot1_huikang_v27_kaggle_side_repack_{hash_prefix or 'hash_unknown'}",
    }


def current_best_public_score(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    best_value: float | None = None
    for row in rows:
        score = parse_score(row.get("public_score"))
        if score is None:
            continue
        if best_value is None or score > best_value:
            best = row
            best_value = score
    if best is None:
        return None
    return {
        "public_score": best_value,
        "submission_id": best.get("submission_id"),
        "status": best.get("status"),
        "description": best.get("description"),
        "submitted_at": best.get("submitted_at") or best.get("date"),
    }


def find_slot1_result(rows: list[dict[str, Any]], candidate: dict[str, Any]) -> dict[str, Any]:
    hash_prefix = str(candidate.get("candidate_hash_prefix") or "").lower()
    route = str(candidate.get("route") or "").lower()
    web_match_after = candidate.get("manual_web_match_after_utc")
    matched = []
    for row in rows:
        description = str(row.get("description") or "").lower()
        status = str(row.get("status") or "")
        file_name = str(row.get("file_name") or "").lower()
        score = parse_score(row.get("public_score"))
        hash_matches = bool(hash_prefix and hash_prefix in description)
        route_matches = route and route.split("_", 1)[0] in description
        huikang_matches = "huikang" in description and ("v27" in description or "adapter" in description)
        likely_manual_web_submit = file_name == "submission.zip" and not description.strip() and blank_web_submission_can_match(row, candidate, web_match_after)
        if hash_matches or route_matches or huikang_matches or likely_manual_web_submit:
            matched.append(
                {
                    "submission_id": row.get("submission_id"),
                    "file_name": row.get("file_name"),
                    "description": row.get("description"),
                    "status": status,
                    "public_score": score,
                    "complete_with_public_score": is_complete_status(status) and score is not None,
                    "same_hash": hash_matches,
                    "likely_manual_web_submit": likely_manual_web_submit,
                    "pending": is_pending_status(status),
                    "error": is_error_status(status),
                }
            )
    completed = [row for row in matched if row["complete_with_public_score"]]
    same_hash_completed = [row for row in completed if row["same_hash"]]
    pending = [row for row in matched if row["pending"]]
    errors = [row for row in matched if row["error"]]
    return {
        "matched_rows": matched,
        "complete_with_public_score": bool(completed),
        "same_hash_complete_with_public_score": bool(same_hash_completed),
        "pending": bool(pending),
        "error_without_complete_score": bool(errors),
        "latest_complete": completed[0] if completed else None,
        "latest_pending": pending[0] if pending else None,
        "latest_error": errors[0] if errors else None,
    }


def blank_web_submission_can_match(row: dict[str, Any], candidate: dict[str, Any], after_utc: Any) -> bool:
    if candidate.get("route_switch_candidate") is not True:
        return True
    if not after_utc:
        return False
    row_date = parse_datetime(row.get("date") or row.get("submitted_at"))
    after_date = parse_datetime(after_utc)
    return row_date is not None and after_date is not None and row_date >= after_date


def parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip().replace("T", " ")
    try:
        return datetime.fromisoformat(text)
    except Exception:
        return None


def parse_score(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).strip())
    except ValueError:
        return None


def is_complete_status(value: Any) -> bool:
    return "COMPLETE" in str(value or "").upper()


def is_pending_status(value: Any) -> bool:
    return "PENDING" in str(value or "").upper() or "RUNNING" in str(value or "").upper()


def is_error_status(value: Any) -> bool:
    upper = str(value or "").upper()
    return "ERROR" in upper or "FAILED" in upper


def build_slots(
    policy: dict[str, Any],
    history: dict[str, Any],
    candidate: dict[str, Any],
    slot1_result: dict[str, Any],
    manual_fix_reason: dict[str, Any],
) -> list[dict[str, Any]]:
    hard_limit = int(policy.get("hard_limit_per_day") or 5)
    today_count = history.get("quota_effective_today_submission_count")
    remaining = history.get("quota_effective_today_remaining")
    slots: list[dict[str, Any]] = []

    global_block = None
    if not history.get("query_ok"):
        global_block = "submission_history_query_failed"
    elif today_count is None or remaining is None:
        global_block = "today_submission_count_unavailable"
    elif int(today_count) >= hard_limit or int(remaining) <= 0:
        global_block = "daily_submission_quota_exhausted"
    elif any(is_pending_status(row.get("status")) for row in history.get("rows", [])):
        global_block = "submission_history_has_pending_result"

    slot1_allowed, slot1_reason, slot1_action = evaluate_slot1(global_block, candidate, slot1_result, manual_fix_reason)
    slots.append(
        {
            "slot": "slot1",
            "candidate": candidate["name"],
            "allowed": slot1_allowed,
            "reason": slot1_reason,
            "manual_action": slot1_action,
        }
    )

    slot1_known = slot1_result.get("complete_with_public_score") is True
    for index in range(2, 6):
        if global_block:
            reason = global_block
        elif not slot1_known:
            reason = "blocked_until_slot1_complete_with_public_score"
        else:
            reason = "no_distinct_non_duplicate_candidate_available"
        slots.append(
            {
                "slot": f"slot{index}",
                "candidate": None,
                "allowed": False,
                "reason": reason,
                "manual_action": "none",
            }
        )
    return slots


def evaluate_slot1(
    global_block: str | None,
    candidate: dict[str, Any],
    slot1_result: dict[str, Any],
    manual_fix_reason: dict[str, Any],
) -> tuple[bool, str, str]:
    if global_block:
        return False, global_block, "none"
    if slot1_result.get("pending"):
        return False, "slot1_submission_still_pending", "wait for pending submission result"
    if slot1_result.get("same_hash_complete_with_public_score"):
        return False, "same_hash_candidate_already_completed_with_public_score", "none"
    if slot1_result.get("error_without_complete_score") and not manual_fix_reason.get("accepted"):
        return (
            False,
            "previous_slot1_error_without_manual_fix_reason",
            f"write a concrete fix reason to {MANUAL_FIX_REASON_PATH.relative_to(PROJECT_ROOT).as_posix()} before considering another slot1 attempt",
        )
    if not candidate.get("structural_valid"):
        return False, "candidate_structural_validation_missing_or_failed", "none"
    if not candidate.get("rank_lte_32"):
        return False, "candidate_rank_gt_32_or_unknown", "none"
    if not candidate.get("notebook_pushed"):
        return (
            False,
            "kaggle_side_notebook_not_pushed",
            f'python scripts\\21_push_kaggle_notebook.py --kernel-dir "{candidate.get("kernel_dir") or KERNEL_DIR}"',
        )
    if not candidate.get("output_submission_zip_confirmed"):
        return (
            False,
            "kaggle_notebook_output_submission_zip_not_confirmed",
            f"kaggle kernels status {candidate['kernel_id']} && kaggle kernels files {candidate['kernel_id']}",
        )
    return True, "manual_submit_allowed_for_slot1_only", MANUAL_SUBMIT_PATH


def build_recommended_action(history: dict[str, Any], candidate: dict[str, Any], slots: list[dict[str, Any]]) -> dict[str, str]:
    slot1 = slots[0]
    if slot1["allowed"]:
        return {
            "status": "manual_submit_slot1",
            "action": f"manual submit {candidate['name']} from Kaggle Notebook Output",
            "reason": "Slot1 is the only current candidate and notebook output is confirmed.",
        }
    if slot1["reason"] == "kaggle_side_notebook_not_pushed":
        return {
            "status": "prepare_slot1",
            "action": f'python scripts\\21_push_kaggle_notebook.py --kernel-dir "{candidate.get("kernel_dir") or KERNEL_DIR}"',
            "reason": "The Kaggle-side notebook has not been pushed yet, so there is no cloud output to submit.",
        }
    if slot1["reason"] == "kaggle_notebook_output_submission_zip_not_confirmed":
        return {
            "status": "check_slot1_output",
            "action": f"kaggle kernels status {candidate['kernel_id']} ; kaggle kernels files {candidate['kernel_id']}",
            "reason": "The notebook push is recorded, but submission.zip is not confirmed in Kaggle output.",
        }
    return {
        "status": "blocked",
        "action": "do not submit today",
        "reason": str(slot1["reason"]),
    }


def render_report(payload: dict[str, Any]) -> str:
    history = payload["history"]
    candidate = payload["candidate"]
    best = payload["best_public_score"]
    slots = payload["slots"]
    recommended = payload["recommended"]
    policy = payload["policy"]
    slot1_result = payload["slot1_result"]
    manual_fix_reason = payload["manual_fix_reason"]
    recommended_action = yaml_single_quote(recommended["action"])
    recommended_reason = yaml_single_quote(recommended["reason"])
    if history.get("quota_effective_today_remaining") == 0:
        current_implication = (
            "Current practical implication: no submission should be made today. "
            f"`{candidate['name']}` is listed only as the currently tracked candidate for the next planning window."
        )
    else:
        current_implication = (
            f"Current practical implication: `{candidate['name']}` is the only candidate in the plan. "
            "Do not use slots 2-5 until slot1 has `COMPLETE` plus a public score, or until a distinct documented candidate exists."
        )

    candidate_rows = [
        [
            candidate["slot"],
            candidate["name"],
            candidate["candidate_type"],
            candidate["model_source"],
            candidate["structural_valid"],
            candidate["rank_lte_32"],
            candidate["notebook_pushed"],
            candidate["output_submission_zip_confirmed"],
            candidate["candidate_hash_prefix"],
        ]
    ]
    slot_rows = [[slot["slot"], slot["candidate"], slot["allowed"], slot["reason"], slot["manual_action"]] for slot in slots]
    best_text = "None" if best is None else json.dumps(best, ensure_ascii=False)
    matched_text = json.dumps(slot1_result["matched_rows"], ensure_ascii=False, indent=2)
    principles = "\n".join(f"- {item}" for item in policy.get("principle", [])) or "- null"

    return f"""# Daily Submission Plan

- timestamp: {payload['timestamp']}
- today_submission_count: {history.get('today_submission_count')}
- today_remaining_quota: {history.get('today_remaining_quota')}
- quota_effective_today_submission_count: {history.get('quota_effective_today_submission_count')}
- quota_effective_today_remaining: {history.get('quota_effective_today_remaining')}
- submission_history_query_status: {history.get('submission_history_query_status')}
- today_submission_count_parse_status: {history.get('today_submission_count_parse_status')}
- current_best_public_score: `{best_text}`
- manual_checklist_exists: {payload['manual_checklist_exists']}
- manual_fix_reason_exists: {manual_fix_reason['exists']}
- manual_fix_reason_accepted: {manual_fix_reason['accepted']}
- no_automatic_competition_submission: {payload['no_automatic_competition_submission']}
- submission_quota_consumed_by_this_script: {payload['submission_quota_consumed']}

## Task Chain Assessment

The chain is reasonable for quota control and reproducibility: query history first, plan only one distinct candidate, require official feedback before slot2-slot5, and avoid repeated same-hash submissions. It does not create a higher-score model by itself. A real high score still requires a valid candidate to be manually submitted and scored by Kaggle's official evaluator.

{current_implication}

## Submission Policy Principles

{principles}

## Candidate List

{markdown_table(["slot", "name", "type", "model_source", "structural_valid", "rank_lte_32", "notebook_pushed", "output_zip_confirmed", "hash_prefix"], candidate_rows)}

## Slot Plan

{markdown_table(["slot", "candidate", "allowed", "reason", "manual_action"], slot_rows)}

## Slot1 Result Match

```json
{matched_text}
```

## Manual Fix Marker

- path: `{manual_fix_reason['path']}`
- accepted: {manual_fix_reason['accepted']}

Only create this marker after documenting a concrete change that explains why a repeated slot1 attempt is not the same failed candidate.

## Required Manual Path

```text
{MANUAL_SUBMIT_PATH}
```

Recommended manual submission message:

```text
{candidate['recommended_manual_message']}
```

## If Notebook Is Not Pushed

```powershell
python scripts\\21_push_kaggle_notebook.py --kernel-dir "{candidate.get('kernel_dir') or KERNEL_DIR}"
```

## If Output Is Not Confirmed

```powershell
kaggle kernels status {candidate['kernel_id']}
kaggle kernels files {candidate['kernel_id']}
```

## Today's Recommended Operation

```yaml
NEXT_ACTION:
  status: {recommended['status']}
  action: {recommended_action}
  reason: {recommended_reason}
```

## Safety

- This script does not call competition submit.
- This script does not upload `submission.zip`.
- This script does not consume Kaggle submission quota.
- Slot2-slot5 are blocked until slot1 result is known.
- Repeating a COMPLETE same-hash candidate is blocked.
"""


def yaml_single_quote(value: Any) -> str:
    return "'" + str(value).replace("'", "''") + "'"


if __name__ == "__main__":
    raise SystemExit(main())
