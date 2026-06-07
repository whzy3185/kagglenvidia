from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
KAGGLE_USER = "muelsyse111"
COMPETITION = "nvidia-nemotron-model-reasoning-challenge"

SOURCE_DIR = PROJECT_ROOT / "external" / "stage7_kernel_sources" / "mohamed_replay_data_086"
SOURCE_NOTEBOOK = SOURCE_DIR / "nemotron-replay-data-0-86.ipynb"
SOURCE_METADATA = SOURCE_DIR / "kernel-metadata.json"

OUT_DIR = PROJECT_ROOT / "kaggle_kernels" / "nemotron_stage7_full_replay_hardmix_v2"
KERNEL_SLUG = "nemotron-stage7-full-replay-hardmix-v2"
CODE_FILE = "nemotron_stage7_full_replay_hardmix_v2.ipynb"


def main() -> int:
    if not SOURCE_NOTEBOOK.exists() or not SOURCE_METADATA.exists():
        raise SystemExit("Missing Mohamed 0.86 source notebook. Pull stage7 sources first.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source_nb = json.loads(SOURCE_NOTEBOOK.read_text(encoding="utf-8"))
    source_meta = json.loads(SOURCE_METADATA.read_text(encoding="utf-8"))

    write_json(OUT_DIR / "kernel-metadata.json", build_metadata(source_meta))
    write_json(OUT_DIR / CODE_FILE, build_notebook(source_nb))

    print("generated full-training notebook:")
    print(f"  {OUT_DIR}")
    print(f"  {OUT_DIR / 'kernel-metadata.json'}")
    print(f"  {OUT_DIR / CODE_FILE}")
    print("push:")
    print(f'  kaggle kernels push -p "{OUT_DIR}"')
    return 0


def build_metadata(source_meta: dict[str, Any]) -> dict[str, Any]:
    metadata = dict(source_meta)
    metadata.update(
        {
            "id": f"{KAGGLE_USER}/{KERNEL_SLUG}",
            "title": "nemotron stage7 full replay hardmix v2",
            "code_file": CODE_FILE,
            "language": "python",
            "kernel_type": "notebook",
            "is_private": "true",
            "enable_gpu": "true",
            "enable_tpu": False,
            "enable_internet": "false",
            "keywords": ["gpu", "stage7", "full-train"],
            "competition_sources": [COMPETITION],
            "machine_shape": "NvidiaRtxPro6000",
        }
    )
    metadata.pop("id_no", None)
    return metadata


def build_notebook(source_nb: dict[str, Any]) -> dict[str, Any]:
    cells: list[dict[str, Any]] = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Stage 7 Full Replay Hardmix V2\n",
                "\n",
                "Full training amount is preserved: `NUM_STEPS=1000`, `MAX_SEQ_LEN=8192`, "
                "and `TARGET_REPLAY_ANSWER_TOKENS=2_000_000`. This notebook only changes "
                "the data ordering/mixing report and packaging diagnostics. It does not submit the competition.\n",
            ],
        }
    ]

    seen_training_cell = False
    for raw_cell in source_nb.get("cells", []):
        src = "".join(raw_cell.get("source", []))
        if should_drop_cell(src):
            continue
        if "def run_training()" in src:
            if seen_training_cell:
                continue
            seen_training_cell = True
        cell = patch_cell(raw_cell)
        cells.append(cell)

    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def should_drop_cell(src: str) -> bool:
    blocked_markers = [
        "Modal glue",
        "import modal",
        "modal.App",
        "KAGGLE_API_TOKEN",
        "kaggle datasets version",
    ]
    return any(marker in src for marker in blocked_markers)


def patch_cell(cell: dict[str, Any]) -> dict[str, Any]:
    cell = dict(cell)
    if cell.get("cell_type") != "code":
        return {
            "cell_type": "markdown",
            "metadata": {},
            "source": cell.get("source", []),
        }

    src = "".join(cell.get("source", []))
    if "LORA_RANK" in src and "NUM_STEPS" in src and "TARGET_MODULES" in src:
        src = patch_config(src)
    if "REPLAY_TOKENIZED_PATH" in src and "mixed_examples.extend(replay_examples[replay_idx:])" in src:
        src = patch_data_mix(src)
    if "def run_training()" in src:
        src = patch_packaging(src)
    if "del model" in src and "run_training()" in src:
        src = src.replace("del model\ngc.collect()", "globals().pop('model', None)\ngc.collect()")

    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": lines(src),
    }


def patch_config(src: str) -> str:
    if "STAGE7_FULL_TRAINING_MODE" in src:
        return src
    src = src.replace(
        "SHUFFLE_DATASET = False",
        """SHUFFLE_DATASET = False

# Stage 7 full training controls. Do not reduce training amount here.
STAGE7_FULL_TRAINING_MODE = "full_replay_hardmix_v2"
STAGE7_KEEP_FULL_STEPS = True
STAGE7_EXPECTED_NUM_STEPS = 1000
STAGE7_EXPECTED_TARGET_REPLAY_ANSWER_TOKENS = 2_000_000""",
    )
    return src


def patch_data_mix(src: str) -> str:
    marker = """        print(
            f"Mixed corpus: {mixed_tokens:,} tokens "
            f"(unmasked={mixed_unmasked:,.0f})"
        )
"""
    insertion = r'''

        # Stage 7 full training hardmix v2: keep the full amount of data and
        # steps, but move high-unmasked target/replay examples to the front so
        # early gradients see harder answer-bearing traces.
        def _stage7_stats(ex):
            token_len = max(1, len(ex["tokens"]))
            unmasked = float(sum(ex["weights"]))
            density = unmasked / token_len
            return token_len, unmasked, density

        original_count = len(examples)
        target_pool = [e for e in examples if e.get("problem_id") != "replay_math"]
        replay_pool = [e for e in examples if e.get("problem_id") == "replay_math"]
        target_hard = sorted(
            target_pool,
            key=lambda e: (_stage7_stats(e)[1], _stage7_stats(e)[2], _stage7_stats(e)[0]),
            reverse=True,
        )
        replay_hard = sorted(
            replay_pool,
            key=lambda e: (_stage7_stats(e)[1], _stage7_stats(e)[2], _stage7_stats(e)[0]),
            reverse=True,
        )
        hard_prefix = target_hard[: max(1, len(target_hard) // 3)] + replay_hard[: max(1, len(replay_hard) // 3)]
        seen = set()
        reordered = []
        for ex in hard_prefix + examples:
            key = id(ex)
            if key in seen:
                continue
            seen.add(key)
            reordered.append(ex)
        examples = reordered

        stage7_report = {
            "mode": STAGE7_FULL_TRAINING_MODE,
            "full_training_amount_preserved": True,
            "num_steps": NUM_STEPS,
            "max_seq_len": MAX_SEQ_LEN,
            "target_replay_answer_tokens": TARGET_REPLAY_ANSWER_TOKENS,
            "original_count": original_count,
            "after_reorder_count": len(examples),
            "target_pool": len(target_pool),
            "replay_pool": len(replay_pool),
            "hard_prefix_count": len(hard_prefix),
        }
        with open("/kaggle/working/stage7_full_training_plan.json", "w") as f:
            json.dump(stage7_report, f, indent=2)
        print("STAGE7_FULL_TRAINING_PLAN:", json.dumps(stage7_report, indent=2))
'''
    if "STAGE7_FULL_TRAINING_PLAN" not in src:
        src = src.replace(marker, marker + insertion)
    return src


def patch_packaging(src: str) -> str:
    src = src.replace(
        'print(f"Wrote {SUBMISSION_ZIP}")',
        '''import hashlib
        def _sha256_file(_path):
            _digest = hashlib.sha256()
            with open(_path, "rb") as _handle:
                for _chunk in iter(lambda: _handle.read(1024 * 1024), b""):
                    _digest.update(_chunk)
            return _digest.hexdigest()
        with zipfile.ZipFile(SUBMISSION_ZIP, "r") as _zf:
            _names = sorted(_zf.namelist())
        print("zip_namelist:", _names)
        if _names != ["adapter_config.json", "adapter_model.safetensors"]:
            raise RuntimeError(f"bad submission zip contents: {_names}")
        print(f"Wrote {SUBMISSION_ZIP}")
        print("submission_zip_sha256:", _sha256_file(SUBMISSION_ZIP))
        print("OK: /kaggle/working/submission.zip is ready.")''',
    )
    return src


def lines(text: str) -> list[str]:
    return [line + "\n" for line in text.splitlines()]


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
