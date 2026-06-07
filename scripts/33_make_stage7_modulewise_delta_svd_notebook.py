from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_GENERATOR = PROJECT_ROOT / "scripts" / "32_make_stage7_delta_svd_notebook.py"
BASE_DIR = PROJECT_ROOT / "kaggle_kernels" / "nemotron_s7_delta_space_svd_r32"
OUT_DIR = PROJECT_ROOT / "kaggle_kernels" / "nemotron_s7_modulewise_delta_svd_r32"
METADATA_PATH = OUT_DIR / "kernel-metadata.json"
NOTEBOOK_PATH = OUT_DIR / "nemotron_s7_modulewise_delta_svd_r32.ipynb"
REPORT_PATH = PROJECT_ROOT / "reports" / "STAGE7_MODULEWISE_DELTA_SVD_R32.md"
KERNEL_ID = "muelsyse111/nemotron-s7-modulewise-delta-svd-r32"


def main() -> int:
    subprocess.run(
        [sys.executable, str(BASE_GENERATOR)],
        cwd=PROJECT_ROOT,
        check=True,
        timeout=60,
    )
    base_metadata = json.loads(
        (BASE_DIR / "kernel-metadata.json").read_text(encoding="utf-8")
    )
    base_notebook = json.loads(
        (BASE_DIR / "nemotron_s7_delta_space_svd_r32.ipynb").read_text(
            encoding="utf-8"
        )
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base_metadata.update(
        {
            "id": KERNEL_ID,
            "title": "Nemotron S7 Modulewise Delta SVD R32",
            "code_file": NOTEBOOK_PATH.name,
        }
    )
    intro = "".join(base_notebook["cells"][0]["source"])
    intro = intro.replace(
        "Nemotron S7 Delta-Space SVD Rank-32",
        "Nemotron S7 Modulewise Delta-Space SVD Rank-32",
    )
    intro += (
        "\n\nWeights vary by module family so attention, Mamba, experts, and the "
        "output head can preserve different source-adapter behavior."
    )
    base_notebook["cells"][0]["source"] = intro.splitlines(keepends=True)
    source = "".join(base_notebook["cells"][1]["source"])
    source = source.replace(
        'CANDIDATE = "nemotron-s7-delta-space-svd-r32"',
        'CANDIDATE = "nemotron-s7-modulewise-delta-svd-r32"',
    )
    source = source.replace(
        'MECHANISM = "effective_delta_qr_svd_rank32_recompression"',
        'MECHANISM = "module_family_weighted_delta_qr_svd_rank32"',
    )
    source = source.replace(
        "def weights_for_key(key):\n    return WEIGHTS",
        '''def weights_for_key(key):
    lower = key.lower()
    if "lm_head" in lower:
        return [0.25, 0.60, 0.15]
    if "mamba" in lower or "in_proj" in lower or "out_proj" in lower:
        return [0.45, 0.15, 0.40]
    if any(name in lower for name in ["q_proj", "k_proj", "v_proj", "o_proj"]):
        return [0.55, 0.30, 0.15]
    if "expert" in lower or "up_proj" in lower or "down_proj" in lower:
        return [0.50, 0.20, 0.30]
    return WEIGHTS''',
    )
    source = source.replace(
        'print("weights:", WEIGHTS)',
        'print("default_weights:", WEIGHTS)\nprint("weight_policy: module_family_specific")',
    )
    base_notebook["cells"][1]["source"] = source.splitlines(keepends=True)
    METADATA_PATH.write_text(
        json.dumps(base_metadata, indent=2) + "\n", encoding="utf-8"
    )
    NOTEBOOK_PATH.write_text(
        json.dumps(base_notebook, indent=1) + "\n", encoding="utf-8"
    )
    validate(base_metadata, source)
    REPORT_PATH.write_text(render_report(), encoding="utf-8")
    print(f"kernel_id={KERNEL_ID}")
    print(f"kernel_dir={OUT_DIR.relative_to(PROJECT_ROOT)}")
    print(f"report={REPORT_PATH.relative_to(PROJECT_ROOT)}")
    print(f'push_command=kaggle kernels push -p "{OUT_DIR.relative_to(PROJECT_ROOT)}"')
    return 0


def validate(metadata: dict, source: str) -> None:
    checks = {
        "kernel_id": metadata.get("id") == KERNEL_ID,
        "cpu_only": str(metadata.get("enable_gpu")).lower() == "false",
        "module_policy": "weight_policy: module_family_specific" in source,
        "lm_head_policy": '"lm_head" in lower' in source,
        "mamba_policy": '"mamba" in lower' in source,
        "expert_policy": '"expert" in lower' in source,
        "delta_space": "c_matrix = torch.cat(c_blocks, dim=1)" in source,
        "rank32": "TARGET_RANK = 32" in source,
        "no_base_model": "from_pretrained" not in source,
        "no_submit": "kaggle competitions submit" not in source,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"Validation failed: {failed}")


def render_report() -> str:
    return """# Stage 7 Modulewise Delta-Space SVD Rank-32

- kernel: `muelsyse111/nemotron-s7-modulewise-delta-svd-r32`
- mechanism: module-family source weighting in effective LoRA delta space
- base model loaded: false
- GPU required: false
- competition submission executed: false

## Main Change

The global delta-SVD candidate uses one source-weight vector for every module.
This candidate uses distinct vectors for attention, Mamba, experts, and
`lm_head`, then recompresses each effective update to rank 32.

## Evidence

- Competition discussion on category trade-offs:
  https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/703240
- TIES-Merging: https://arxiv.org/abs/2306.01708
- LoRA: https://arxiv.org/abs/2106.09685
- PEFT merging: https://huggingface.co/docs/peft/developer_guides/model_merging

The weights are heuristic and therefore high risk. Remote output must pass the
same structural, size, SHA256, and rank gates before it becomes a submission
candidate.
"""


if __name__ == "__main__":
    raise SystemExit(main())
