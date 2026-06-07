from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_GENERATOR = PROJECT_ROOT / "scripts" / "32_make_stage7_delta_svd_notebook.py"
BASE_DIR = PROJECT_ROOT / "kaggle_kernels" / "nemotron_s7_delta_space_svd_r32"
OUT_DIR = PROJECT_ROOT / "kaggle_kernels" / "nemotron_s7_norm_balanced_delta_svd_r32"
METADATA_PATH = OUT_DIR / "kernel-metadata.json"
NOTEBOOK_PATH = OUT_DIR / "nemotron_s7_norm_balanced_delta_svd_r32.ipynb"
REPORT_PATH = PROJECT_ROOT / "reports" / "STAGE7_NORM_BALANCED_DELTA_SVD_R32.md"
KERNEL_ID = "muelsyse111/nemotron-s7-norm-balanced-delta-svd-r32"


def main() -> int:
    subprocess.run(
        [sys.executable, str(BASE_GENERATOR)],
        cwd=PROJECT_ROOT,
        check=True,
        timeout=60,
    )
    metadata = json.loads(
        (BASE_DIR / "kernel-metadata.json").read_text(encoding="utf-8")
    )
    notebook = json.loads(
        (BASE_DIR / "nemotron_s7_delta_space_svd_r32.ipynb").read_text(
            encoding="utf-8"
        )
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    metadata.update(
        {
            "id": KERNEL_ID,
            "title": "Nemotron S7 Norm Balanced Delta SVD R32",
            "code_file": NOTEBOOK_PATH.name,
        }
    )
    intro = "".join(notebook["cells"][0]["source"])
    intro = intro.replace(
        "Nemotron S7 Delta-Space SVD Rank-32",
        "Nemotron S7 Norm-Balanced Delta-Space SVD Rank-32",
    )
    intro += (
        "\n\nEach source update is normalized by its exact low-rank Frobenius norm "
        "before weighted task arithmetic, limiting scale domination."
    )
    notebook["cells"][0]["source"] = intro.splitlines(keepends=True)
    source = "".join(notebook["cells"][1]["source"])
    source = source.replace(
        'CANDIDATE = "nemotron-s7-delta-space-svd-r32"',
        'CANDIDATE = "nemotron-s7-norm-balanced-delta-svd-r32"',
    )
    source = source.replace(
        'MECHANISM = "effective_delta_qr_svd_rank32_recompression"',
        'MECHANISM = "per_module_delta_norm_balanced_qr_svd_rank32"',
    )
    source = source.replace(
        "def recompress_pair(a_values, b_values, configs, a_key):",
        '''def low_rank_frobenius_norm(a_value, b_value):
    # ||B A||_F^2 = trace((A A^T) (B^T B)); only rank x rank matrices are formed.
    gram_a = a_value.float() @ a_value.float().T
    gram_b = b_value.float().T @ b_value.float()
    value = torch.sum(gram_a * gram_b.T).clamp_min(1e-20)
    return value.sqrt()


def recompress_pair(a_values, b_values, configs, a_key):''',
    )
    source = source.replace(
        "    module_weights = weights_for_key(a_key)\n"
        "    for weight, a_value, b_value, config in zip(module_weights, a_values, b_values, configs):",
        '''    module_weights = weights_for_key(a_key)
    norms = [low_rank_frobenius_norm(a, b) for a, b in zip(a_values, b_values)]
    norm_reference = torch.stack(norms).median().clamp_min(1e-12)
    for weight, norm, a_value, b_value, config in zip(
        module_weights, norms, a_values, b_values, configs
    ):
        # Normalize each source toward the module-wise median update norm.
        weight = weight * float(norm_reference / norm.clamp_min(1e-12))''',
    )
    source = source.replace(
        'print("weights:", WEIGHTS)',
        'print("base_weights:", WEIGHTS)\nprint("normalization: exact_low_rank_frobenius_to_module_median")',
    )
    notebook["cells"][1]["source"] = source.splitlines(keepends=True)
    METADATA_PATH.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    NOTEBOOK_PATH.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    validate(metadata, source)
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
        "norm_identity": "trace((A A^T) (B^T B))" in source,
        "median_reference": "torch.stack(norms).median()" in source,
        "delta_space": "c_matrix = torch.cat(c_blocks, dim=1)" in source,
        "rank32": "TARGET_RANK = 32" in source,
        "success_marker": "OK: /kaggle/working/submission.zip is ready." in source,
        "no_base_model": "from_pretrained" not in source,
        "no_submit": "kaggle competitions submit" not in source,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"Validation failed: {failed}")


def render_report() -> str:
    return """# Stage 7 Norm-Balanced Delta-Space SVD Rank-32

- kernel: `muelsyse111/nemotron-s7-norm-balanced-delta-svd-r32`
- mechanism: per-module effective-delta norm balancing plus rank-32 SVD
- base model loaded: false
- GPU required: false
- competition submission executed: false

## Main Change

For each LoRA module, this route computes the exact Frobenius norm of `B @ A`
using only rank-sized Gram matrices. Source updates are normalized toward the
module median norm before weighted task arithmetic and rank-32 recompression.

This tests a different hypothesis from fixed global weights: adapter scale, not
only direction, may be causing destructive dominance during fusion.

## Sources

- LoRA: https://arxiv.org/abs/2106.09685
- Task arithmetic: https://arxiv.org/abs/2212.04089
- TIES-Merging: https://arxiv.org/abs/2306.01708
- PEFT merging: https://huggingface.co/docs/peft/developer_guides/model_merging

Remote output must pass the exact zip-root, rank, size, SHA256, pair-count, and
retained-singular-mass checks before it is considered structurally valid.
"""


if __name__ == "__main__":
    raise SystemExit(main())
