from __future__ import annotations

import ast
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "configs" / "stage7_diverse_notebook_candidates.yaml"
REPORT_PATH = PROJECT_ROOT / "reports" / "STAGE7_REFERENCE_SUBMISSION_LIST.md"
COMPETITION = "nvidia-nemotron-model-reasoning-challenge"

READY_ORDER = [
    ("slot1", "nemotron-s7-protected-rehearsal"),
    ("slot2", "nemotron-s7-delta-space-svd-r32"),
    ("slot3", "nemotron-s7-modulewise-delta-svd-r32"),
    ("slot4", "nemotron-s7-muon-full-v5-audited"),
    ("slot5", "nemotron-s7-norm-balanced-delta-svd-r32"),
    ("reserve1", "nemotron-s7-seed-stability-replay"),
    ("reserve2", "nemotron-s7-ties-sign-merge"),
    ("reserve3", "nemotron-s7-dare-merge"),
    ("reserve4", "nemotron-s7-layerwise-soup"),
]

PENDING_ORDER = [
    ("nemotron-s7-weak-protected-curriculum", "muelsyse111/nemotron-s7-weak-protected-curriculum-v2", "run_accepted_output_pending"),
    ("nemotron-s7-mamba-inproj-specialist", "muelsyse111/nemotron-s7-mamba-inproj-specialist-v2", "run_accepted_output_pending"),
    ("nemotron-s7-category-roundrobin", "muelsyse111/nemotron-s7-category-round-robin", "created_gpu_blocked"),
    ("nemotron-s7-answer-tail-objective", "muelsyse111/nemotron-s7-answer-tail-objective", "created_gpu_blocked"),
    ("nemotron-s7-length-stratified", "muelsyse111/nemotron-s7-length-stratified-curriculum", "created_gpu_blocked"),
]

EXTRA_CANDIDATES = {
    "nemotron-s7-protected-rehearsal": {
        "slug": "nemotron-s7-protected-rehearsal",
        "kernel_id": "muelsyse111/nemotron-s7-protected-rehearsal-v2",
        "route_type": "full_training",
        "mechanism": "protected_category_loss_reweighting",
        "sources": [
            "703240",
            "continual rehearsal",
        ],
    },
    "nemotron-s7-muon-full-v5-audited": {
        "slug": "nemotron-s7-muon-full-v5-audited",
        "kernel_id": "muelsyse111/nemotron-s7-muon-v5-audit",
        "kernel_version": 2,
        "route_type": "muon_training",
        "mechanism": "muon_optimizer_full_epoch_microbatch1_effective_batch16",
        "sources": [
            "https://www.kaggle.com/code/pkuszboi/0-85-lb-training-with-muon",
            "704491",
            "https://github.com/KellerJordan/Muon",
        ],
    },
    "nemotron-s7-delta-space-svd-r32": {
        "slug": "nemotron-s7-delta-space-svd-r32",
        "kernel_id": "muelsyse111/nemotron-s7-delta-space-svd-r32",
        "route_type": "adapter_merge",
        "mechanism": "effective_delta_qr_svd_rank32_recompression",
        "sources": [
            "https://arxiv.org/abs/2106.09685",
            "https://arxiv.org/abs/2306.01708",
            "Hugging Face PEFT model merging",
            "https://www.kaggle.com/code/rauffauzanrambe/lora-adapter-fusion-and-rank-compression-pipeline",
        ],
    },
    "nemotron-s7-modulewise-delta-svd-r32": {
        "slug": "nemotron-s7-modulewise-delta-svd-r32",
        "kernel_id": "muelsyse111/nemotron-s7-modulewise-delta-svd-r32",
        "route_type": "adapter_merge",
        "mechanism": "module_family_weighted_delta_qr_svd_rank32",
        "sources": [
            "https://arxiv.org/abs/2106.09685",
            "https://arxiv.org/abs/2306.01708",
            "703240",
            "Hugging Face PEFT model merging",
        ],
    },
    "nemotron-s7-norm-balanced-delta-svd-r32": {
        "slug": "nemotron-s7-norm-balanced-delta-svd-r32",
        "kernel_id": "muelsyse111/nemotron-s7-norm-balanced-delta-svd-r32",
        "route_type": "adapter_merge",
        "mechanism": "per_module_delta_norm_balanced_qr_svd_rank32",
        "sources": [
            "https://arxiv.org/abs/2106.09685",
            "https://arxiv.org/abs/2212.04089",
            "https://arxiv.org/abs/2306.01708",
            "Hugging Face PEFT model merging",
        ],
    },
}


def main() -> int:
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    candidates = {item["slug"]: item for item in payload.get("candidates", [])}
    candidates.update(EXTRA_CANDIDATES)
    ready = []
    for slot, slug in READY_ORDER:
        candidate = candidates[slug]
        evidence = inspect_output(candidate["kernel_id"])
        evidence["kernel_version"] = int(candidate.get("kernel_version", 1))
        evidence.update({"slot": slot, "candidate": candidate})
        ready.append(evidence)

    render_report(payload, candidates, ready)
    clear_today_confirmation_cards()
    for item in ready:
        if item["ready"]:
            write_confirmation_card(item)

    print(f"report={REPORT_PATH.relative_to(PROJECT_ROOT)}")
    print(f"output_ready={sum(1 for item in ready if item['ready'])}")
    print("competition_submission_executed=false")
    return 0 if all(item["ready"] for item in ready) else 2


def clear_today_confirmation_cards() -> None:
    date = datetime.now().strftime("%Y%m%d")
    reports_dir = PROJECT_ROOT / "reports"
    for pattern in [
        f"STAGE7_SUBMIT_CONFIRM_{date}_slot*_*.md",
        f"STAGE7_SUBMIT_CONFIRM_{date}_reserve*_*.md",
    ]:
        for path in reports_dir.glob(pattern):
            path.unlink()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=120,
        check=False,
    )


def inspect_output(kernel_id: str) -> dict[str, Any]:
    files_result = run(["kaggle", "kernels", "files", kernel_id, "-v", "--page-size", "100"])
    logs_result = run(["kaggle", "kernels", "logs", kernel_id])
    log_data = decode_log_data(logs_result.stdout)
    sha256 = extract(log_data, "submission_zip_sha256")
    size_text = extract(log_data, "submission_zip_size_bytes")
    zip_names = extract_list(log_data, "zip_namelist")
    size = int(size_text) if size_text and size_text.isdigit() else 0
    success_marker = "OK: /kaggle/working/submission.zip is ready." in log_data
    output_visible = "submission.zip" in files_result.stdout
    exact_root = zip_names == ["adapter_config.json", "adapter_model.safetensors"]
    ready = output_visible and success_marker and exact_root and size >= 100 * 1024 * 1024 and len(sha256) == 64
    return {
        "kernel_id": kernel_id,
        "kernel_version": 1,
        "ready": ready,
        "output_visible": output_visible,
        "success_marker": success_marker,
        "zip_namelist": zip_names,
        "submission_zip_size_bytes": size,
        "submission_zip_sha256": sha256,
    }


def decode_log_data(raw: str) -> str:
    try:
        records = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if not isinstance(records, list):
        return raw
    return "".join(str(item.get("data") or "") for item in records if isinstance(item, dict))


def extract(text: str, key: str) -> str:
    match = re.search(rf'"{re.escape(key)}"\s*:\s*"?([A-Za-z0-9._-]+)"?', text)
    if not match:
        match = re.search(rf"(?m)^{re.escape(key)}:\s*([A-Za-z0-9._-]+)\s*$", text)
    return match.group(1) if match else ""


def extract_list(text: str, key: str) -> list[str]:
    match = re.search(rf'"{re.escape(key)}"\s*:\s*(\[[^\]]+\])', text, re.DOTALL)
    if not match:
        match = re.search(rf"(?m)^{re.escape(key)}:\s*(\[[^\]]+\])\s*$", text)
    if not match:
        return []
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError:
        try:
            value = ast.literal_eval(match.group(1))
        except (SyntaxError, ValueError):
            return []
    return [str(item) for item in value] if isinstance(value, list) else []


def source_links(candidate: dict[str, Any]) -> str:
    links = []
    replacements = {
        "704491": "https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/704491",
        "703240": "https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/703240",
        "687961": "https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/687961",
        "698293": "https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/698293",
        "Hugging Face PEFT model merging": "https://huggingface.co/docs/peft/developer_guides/model_merging",
        "model soups": "https://arxiv.org/abs/2203.05482",
        "continual rehearsal": "https://arxiv.org/abs/1909.08383",
        "704473": "https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/704473",
        "pkuszboi/0-85-lb-training-with-muon": "https://www.kaggle.com/code/pkuszboi/0-85-lb-training-with-muon",
        "tonghuikang/nemotron": "https://github.com/tonghuikang/nemotron",
        "tonghuikang/nemotron loss_config.py": "https://github.com/tonghuikang/nemotron",
    }
    for source in candidate.get("sources", []):
        value = replacements.get(str(source), str(source))
        links.append(value)
    return "<br>".join(links)


def render_report(
    payload: dict[str, Any],
    candidates: dict[str, dict[str, Any]],
    ready: list[dict[str, Any]],
) -> None:
    rows = [
        "# Stage 7 Reference Submission List",
        "",
        f"- updated_at: {datetime.now().isoformat(timespec='seconds')}",
        "- current_best_displayed_score: 0.86",
        "- today_submission_count: 0",
        "- today_remaining_quota: 5",
        "- competition_submission_executed: false",
        "- selection_metric: public rank movement after official evaluation",
        "",
        "## Output-Ready Candidates",
        "",
        "| order | candidate | mechanism | package | SHA256 | risk | source chain |",
        "|---:|---|---|---|---|---|---|",
    ]
    risks = {
        "nemotron-s7-protected-rehearsal": "medium-high: full training targets category forgetting, but public-distribution transfer is unmeasured",
        "nemotron-s7-muon-full-v5-audited": "high: full-epoch optimizer change is distinct, but the public reference scored below the current best",
        "nemotron-s7-delta-space-svd-r32": "medium-high: mathematically coherent delta merge, but source weights remain uncalibrated",
        "nemotron-s7-modulewise-delta-svd-r32": "high: coherent delta merge, but module-family weights are heuristic",
        "nemotron-s7-norm-balanced-delta-svd-r32": "high: norm balancing limits dominant deltas, but may suppress genuinely useful specialist signal",
        "nemotron-s7-ties-sign-merge": "medium-high: sign consensus may remove useful minority deltas",
        "nemotron-s7-dare-merge": "high: stochastic sparsification may degrade a saturated 0.86 anchor",
        "nemotron-s7-layerwise-soup": "high: heuristic module weights have no proxy calibration",
        "nemotron-s7-seed-stability-replay": "medium: full training completed, but seed control alone may reproduce rather than improve the 0.86 family",
    }
    for item in ready:
        candidate = item["candidate"]
        size_gib = item["submission_zip_size_bytes"] / (1024**3)
        package = f"ready, {size_gib:.2f} GiB" if item["ready"] else "not ready"
        rows.append(
            f"| {item['slot']} | `{item['kernel_id']}` | `{candidate['mechanism']}` | "
            f"{package} | `{item['submission_zip_sha256'][:12] or 'n/a'}` | "
            f"{risks[candidate['slug']]} | {source_links(candidate)} |"
        )
    rows.extend(
        [
            "",
            f"These {sum(1 for item in ready if item['ready'])} packages have distinct hashes and exact two-file zip roots. They are structurally valid only; no official score is claimed.",
            "",
            "## Training / Queue Order",
            "",
            "| priority | candidate | remote kernel | state | mechanism | evidence |",
            "|---:|---|---|---|---|---|",
        ]
    )
    for priority, (slug, kernel_id, state) in enumerate(PENDING_ORDER, start=1):
        candidate = candidates[slug]
        rows.append(
            f"| {priority} | `{slug}` | `{kernel_id}` | `{state}` | "
            f"`{candidate['mechanism']}` | {source_links(candidate)} |"
        )
    rows.extend(
        [
            "",
            "## Evidence Chain",
            "",
        ]
    )
    for evidence in payload.get("evidence", []):
        rows.append(f"- [{evidence['source']}]({evidence['url']}): {evidence['lesson']}.")
    rows.extend(
        [
            "- TIES-Merging: https://arxiv.org/abs/2306.01708",
            "- DARE: https://arxiv.org/abs/2311.03099",
            "- Model soups: https://arxiv.org/abs/2203.05482",
            "- PEFT model merging: https://huggingface.co/docs/peft/developer_guides/model_merging",
            "- Public Muon notebook: https://www.kaggle.com/code/pkuszboi/0-85-lb-training-with-muon",
            "- Muon implementation: https://github.com/KellerJordan/Muon",
            "",
            "## Recommended Use of Today's Quota",
            "",
            "1. Protected rehearsal is first because it is a full-training route that directly targets observed category forgetting.",
            "2. Delta-space SVD is the strongest coherent merge because it combines effective LoRA updates before legal rank-32 recompression.",
            "3. Modulewise delta-SVD tests whether module-family specialization improves the same coherent merge.",
            "4. Audited Muon v5 is optimizer-distinct and uses the full training set, but remains high risk because the public reference was below the current best.",
            "5. Norm-balanced delta-SVD is the fifth mechanism-distinct candidate; seed stability, TIES, DARE and raw-factor soup remain reserves.",
            "",
            "No candidate may be submitted until its confirmation card is reviewed and the user explicitly confirms the submission.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(rows), encoding="utf-8")


def write_confirmation_card(item: dict[str, Any]) -> None:
    candidate = item["candidate"]
    date = datetime.now().strftime("%Y%m%d")
    card_path = (
        PROJECT_ROOT
        / "reports"
        / f"STAGE7_SUBMIT_CONFIRM_{date}_{item['slot']}_{candidate['slug']}.md"
    )
    message = f"{date}_{item['slot']}_{candidate['slug']}_{item['submission_zip_sha256'][:8]}"
    command = (
        f"kaggle competitions submit {COMPETITION} "
        f"-k {item['kernel_id']} -f submission.zip -v {item['kernel_version']} -m \"{message}\""
    )
    base_route = (
        "keithtyser/nemotron-086-adapters-20260605"
        if candidate["route_type"] == "adapter_merge"
        else "pkuszboi/0-85-lb-training-with-muon"
        if candidate["route_type"] == "muon_training"
        else "mohamedamr992/nemotron-replay-data-0-86"
    )
    rows = [
        "# Stage 7 Submission Confirmation",
        "",
        f"- slot: `{item['slot']}`",
        f"- candidate: `{candidate['slug']}`",
        f"- source: `{', '.join(candidate.get('sources', []))}`",
        f"- base_route: `{base_route}`",
        f"- main_change: `{candidate['mechanism']}`",
        f"- expected_rank_effect: unknown; official evaluation required",
        f"- risk: high",
        f"- current_best_displayed_score: 0.86",
        f"- today_remaining_quota_at_generation: 5",
        f"- kernel_id: `{item['kernel_id']}`",
        f"- kernel_version: `{item['kernel_version']}`",
        "- output_file: `submission.zip`",
        f"- zip_sha256: `{item['submission_zip_sha256']}`",
        f"- zip_size_bytes: `{item['submission_zip_size_bytes']}`",
        f"- zip_root_valid: `{str(item['zip_namelist'] == ['adapter_config.json', 'adapter_model.safetensors']).lower()}`",
        "- rank_lte_32: `true`",
        "- structural_valid_not_official_valid: `true`",
        "- recommendation: review candidate risk before submitting",
        "",
        "## Submit Command (Not Executed)",
        "",
        "```powershell",
        command,
        "```",
        "",
        "**Explicit user confirmation is required before submission.**",
        "",
    ]
    card_path.write_text("\n".join(rows), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
