from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
KAGGLE_USER = "muelsyse111"
COMPETITION = "nvidia-nemotron-model-reasoning-challenge"

MOHAMED_DIR = PROJECT_ROOT / "external" / "stage7_kernel_sources" / "mohamed_replay_data_086"
MOHAMED_NOTEBOOK = MOHAMED_DIR / "nemotron-replay-data-0-86.ipynb"
MOHAMED_METADATA = MOHAMED_DIR / "kernel-metadata.json"
MUON_DIR = PROJECT_ROOT / "external" / "stage7_kernel_sources" / "muon_085"
MUON_NOTEBOOK = MUON_DIR / "0-85-lb-training-with-muon.ipynb"
MUON_METADATA = MUON_DIR / "kernel-metadata.json"

OUT_ROOT = PROJECT_ROOT / "kaggle_kernels"
CONFIG_PATH = PROJECT_ROOT / "configs" / "stage7_diverse_notebook_candidates.yaml"
REPORT_PATH = PROJECT_ROOT / "reports" / "STAGE7_DIVERSE_NOTEBOOK_CANDIDATES.md"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "STAGE7_DIVERSE_NOTEBOOK_VALIDATION.md"

KEITHTYSER_MODEL = "keithtyser/nemotron-086-adapters-20260605"
ANCHORS = [
    "public_hk_to_kn_lm_head_lam1p0",
    "public_kn_to_hk_lm_head_lam1p0",
    "public_hk_to_kn_mamba_lam1p0",
]

COMMON_EVIDENCE = [
    {
        "source": "Kaggle discussion 704491",
        "url": "https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/704491",
        "lesson": "training and evaluation variance are material; fixed seed, logging, and optimizer stability matter",
    },
    {
        "source": "Kaggle discussion 703240",
        "url": "https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/703240",
        "lesson": "cryptarithm gains can be cancelled by forgetting in bit, gravity, numeral, and unit conversion",
    },
    {
        "source": "Kaggle discussion 687961",
        "url": "https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/687961",
        "lesson": "rank-32, length-8192 training is feasible on Kaggle RTX Pro 6000 with fused CE and careful microbatching",
    },
    {
        "source": "Kaggle discussion 698293",
        "url": "https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/698293",
        "lesson": "symbolic solvers are useful as distillation/data oracles, not inference-time shortcuts",
    },
]


TRAINING_VARIANTS = [
    {
        "slug": "nemotron-s7-seed-stability-replay",
        "folder": "nemotron_s7_seed_stability_replay",
        "title": "Nemotron S7 Seed Stability Replay",
        "mechanism": "deterministic_seed_and_reproducible_shuffle",
        "hypothesis": "reduce run-to-run training variance while preserving the full Mohamed replay recipe",
        "code": r'''
        import random as _stage7_random
        import numpy as _stage7_np
        _stage7_random.seed(42)
        _stage7_np.random.seed(42)
        torch.manual_seed(42)
        torch.cuda.manual_seed_all(42)
        indices = list(range(len(examples)))
        _stage7_random.Random(42).shuffle(indices)
        examples = [examples[i] for i in indices]
        print("STAGE7_MECHANISM: deterministic seed 42 plus reproducible full-corpus shuffle")
''',
        "config_replacements": {"SHUFFLE_DATASET = False": "SHUFFLE_DATASET = False"},
        "sources": ["704491", "pkuszboi/0-85-lb-training-with-muon"],
    },
    {
        "slug": "nemotron-s7-category-roundrobin",
        "folder": "nemotron_s7_category_roundrobin",
        "title": "Nemotron S7 Category Round Robin",
        "mechanism": "category_balanced_round_robin_curriculum",
        "hypothesis": "avoid long same-category runs and reduce catastrophic forgetting across the nine task families",
        "code": r'''
        import csv as _stage7_csv
        from collections import defaultdict as _stage7_defaultdict

        _stage7_categories = {}
        with open(TRAIN_CSV_PATH, encoding="utf-8") as _stage7_handle:
            for _stage7_row in _stage7_csv.DictReader(_stage7_handle):
                _stage7_id = str(_stage7_row.get("id", ""))
                _stage7_cat = (
                    _stage7_row.get("category")
                    or _stage7_row.get("problem_type")
                    or _stage7_row.get("type")
                    or "unknown"
                )
                _stage7_categories[_stage7_id] = str(_stage7_cat)

        _stage7_buckets = _stage7_defaultdict(list)
        for _stage7_ex in examples:
            _stage7_pid = str(_stage7_ex.get("problem_id", ""))
            _stage7_cat = "replay_math" if _stage7_pid == "replay_math" else _stage7_categories.get(_stage7_pid, "unknown")
            _stage7_buckets[_stage7_cat].append(_stage7_ex)
        _stage7_ordered = []
        while any(_stage7_buckets.values()):
            for _stage7_cat in sorted(_stage7_buckets):
                if _stage7_buckets[_stage7_cat]:
                    _stage7_ordered.append(_stage7_buckets[_stage7_cat].pop(0))
        examples = _stage7_ordered
        print("STAGE7_MECHANISM: category-balanced round robin", {k: len(v) for k, v in _stage7_buckets.items()})
''',
        "config_replacements": {},
        "sources": ["703240", "tonghuikang/nemotron"],
    },
    {
        "slug": "nemotron-s7-protected-rehearsal",
        "folder": "nemotron_s7_protected_rehearsal",
        "title": "Nemotron S7 Protected Rehearsal",
        "mechanism": "protected_category_loss_reweighting",
        "hypothesis": "protect bit, gravity, numeral, and unit conversion while retaining weak-category replay",
        "code": r'''
        import csv as _stage7_csv
        _stage7_categories = {}
        with open(TRAIN_CSV_PATH, encoding="utf-8") as _stage7_handle:
            for _stage7_row in _stage7_csv.DictReader(_stage7_handle):
                _stage7_categories[str(_stage7_row.get("id", ""))] = str(
                    _stage7_row.get("category")
                    or _stage7_row.get("problem_type")
                    or _stage7_row.get("type")
                    or "unknown"
                )
        _stage7_protected = {"bit_manipulation", "gravity", "numeral", "unit_conversion"}
        _stage7_changed = 0
        for _stage7_ex in examples:
            _stage7_cat = _stage7_categories.get(str(_stage7_ex.get("problem_id", "")), "")
            if _stage7_cat in _stage7_protected:
                _stage7_ex["weights"] = [float(w) * 1.35 for w in _stage7_ex["weights"]]
                _stage7_changed += 1
        print("STAGE7_MECHANISM: protected-category loss reweighting", "changed_examples=", _stage7_changed)
''',
        "config_replacements": {},
        "sources": ["703240", "continual rehearsal"],
    },
    {
        "slug": "nemotron-s7-weak-protected-curriculum",
        "folder": "nemotron_s7_weak_protected_curriculum",
        "title": "Nemotron S7 Weak Protected Curriculum",
        "mechanism": "weak_category_plus_protected_interleaving",
        "hypothesis": "learn cryptarithm/equation weaknesses without placing weak-category gradients in an isolated block",
        "code": r'''
        import csv as _stage7_csv
        from collections import defaultdict as _stage7_defaultdict
        _stage7_categories = {}
        with open(TRAIN_CSV_PATH, encoding="utf-8") as _stage7_handle:
            for _stage7_row in _stage7_csv.DictReader(_stage7_handle):
                _stage7_categories[str(_stage7_row.get("id", ""))] = str(
                    _stage7_row.get("category")
                    or _stage7_row.get("problem_type")
                    or _stage7_row.get("type")
                    or "unknown"
                )
        _stage7_weak_names = {"cryptarithm_deduce", "cryptarithm_guess", "equation_numeric_guess"}
        _stage7_guard_names = {"bit_manipulation", "gravity", "numeral", "unit_conversion"}
        _stage7_weak, _stage7_guard, _stage7_other = [], [], []
        for _stage7_ex in examples:
            _stage7_cat = _stage7_categories.get(str(_stage7_ex.get("problem_id", "")), "replay_math")
            if _stage7_cat in _stage7_weak_names:
                _stage7_weak.append(_stage7_ex)
            elif _stage7_cat in _stage7_guard_names:
                _stage7_guard.append(_stage7_ex)
            else:
                _stage7_other.append(_stage7_ex)
        _stage7_ordered = []
        _stage7_n = max(len(_stage7_weak), len(_stage7_guard))
        for _stage7_i in range(_stage7_n):
            if _stage7_i < len(_stage7_weak):
                _stage7_ordered.append(_stage7_weak[_stage7_i])
            if _stage7_i < len(_stage7_guard):
                _stage7_ordered.append(_stage7_guard[_stage7_i])
        examples = _stage7_ordered + _stage7_other
        print("STAGE7_MECHANISM: weak/protected interleaving", len(_stage7_weak), len(_stage7_guard), len(_stage7_other))
''',
        "config_replacements": {},
        "sources": ["703240", "698293"],
    },
    {
        "slug": "nemotron-s7-answer-tail-objective",
        "folder": "nemotron_s7_answer_tail_objective",
        "title": "Nemotron S7 Answer Tail Objective",
        "mechanism": "tail_focused_loss_masking",
        "hypothesis": "reduce verbose trace imitation and concentrate rank-32 capacity on decisive reasoning and boxed answers",
        "code": r'''
        _stage7_tail_tokens = 384
        _stage7_changed = 0
        for _stage7_ex in examples:
            _stage7_positive = [i for i, w in enumerate(_stage7_ex["weights"]) if float(w) > 0.0]
            if len(_stage7_positive) > _stage7_tail_tokens:
                _stage7_keep = set(_stage7_positive[-_stage7_tail_tokens:])
                _stage7_ex["weights"] = [
                    float(w) if i in _stage7_keep else 0.0
                    for i, w in enumerate(_stage7_ex["weights"])
                ]
                _stage7_changed += 1
        print("STAGE7_MECHANISM: tail-focused loss masking", "tail_tokens=", _stage7_tail_tokens, "changed=", _stage7_changed)
''',
        "config_replacements": {},
        "sources": ["tonghuikang/nemotron loss_config.py", "reasoning trace compression"],
    },
    {
        "slug": "nemotron-s7-length-stratified",
        "folder": "nemotron_s7_length_stratified",
        "title": "Nemotron S7 Length Stratified Curriculum",
        "mechanism": "alternating_long_short_sequence_curriculum",
        "hypothesis": "avoid optimization being dominated by either short easy traces or long hard traces",
        "code": r'''
        _stage7_sorted = sorted(examples, key=lambda ex: len(ex["tokens"]))
        _stage7_ordered = []
        _stage7_left, _stage7_right = 0, len(_stage7_sorted) - 1
        while _stage7_left <= _stage7_right:
            _stage7_ordered.append(_stage7_sorted[_stage7_right])
            _stage7_right -= 1
            if _stage7_left <= _stage7_right:
                _stage7_ordered.append(_stage7_sorted[_stage7_left])
                _stage7_left += 1
        examples = _stage7_ordered
        print("STAGE7_MECHANISM: alternating long/short curriculum", "examples=", len(examples))
''',
        "config_replacements": {},
        "sources": ["687961", "curriculum learning"],
    },
    {
        "slug": "nemotron-s7-mamba-inproj-specialist",
        "folder": "nemotron_s7_mamba_inproj_specialist",
        "title": "Nemotron S7 Mamba InProj Specialist",
        "mechanism": "selective_mamba_in_proj_adaptation",
        "hypothesis": "constrain updates to Mamba input projections to reduce cross-task interference under rank 32",
        "code": r'''
        print("STAGE7_MECHANISM: selective Mamba in_proj LoRA adaptation")
''',
        "config_replacements": {"IN_PROJ_ONLY = False": "IN_PROJ_ONLY = True"},
        "sources": ["687961", "selective parameter-efficient adaptation"],
    },
]


FUSION_VARIANTS = [
    {
        "slug": "nemotron-s7-ties-sign-merge",
        "folder": "nemotron_s7_ties_sign_merge",
        "title": "Nemotron S7 TIES Sign Merge",
        "mechanism": "ties_trim_elect_sign_merge",
        "hypothesis": "reduce destructive interference between several 0.86-class adapter anchors",
        "method": "ties",
        "sources": ["https://arxiv.org/abs/2306.01708", "https://github.com/prateeky2806/ties-merging"],
    },
    {
        "slug": "nemotron-s7-dare-merge",
        "folder": "nemotron_s7_dare_merge",
        "title": "Nemotron S7 DARE Merge",
        "mechanism": "dare_drop_and_rescale_merge",
        "hypothesis": "sparsify conflicting adapter deltas before combining them",
        "method": "dare",
        "sources": ["https://arxiv.org/abs/2311.03099", "Hugging Face PEFT model merging"],
    },
    {
        "slug": "nemotron-s7-layerwise-soup",
        "folder": "nemotron_s7_layerwise_soup",
        "title": "Nemotron S7 Layerwise Adapter Soup",
        "mechanism": "module_aware_layerwise_weighted_soup",
        "hypothesis": "use different anchor emphasis for attention, Mamba, expert, and output modules",
        "method": "layerwise",
        "sources": ["model soups", "704473", "Hugging Face PEFT model merging"],
    },
]


def main() -> int:
    require_sources()
    candidates: list[dict[str, Any]] = []
    for spec in TRAINING_VARIANTS:
        candidates.append(build_training_variant(spec))
    candidates.append(build_muon_variant())
    for spec in FUSION_VARIANTS:
        candidates.append(build_fusion_variant(spec))

    validation = [validate_candidate(item) for item in candidates]
    write_json(CONFIG_PATH, {"stage": 7, "candidates": candidates, "evidence": COMMON_EVIDENCE})
    write_report(candidates)
    write_validation(validation)

    failures = [item for item in validation if not item["valid"]]
    print(f"generated_candidates={len(candidates)}")
    print(f"validation_failures={len(failures)}")
    for item in candidates:
        print(f"{item['slug']}: {item['kernel_dir']}")
    return 2 if failures else 0


def require_sources() -> None:
    for path in [MOHAMED_NOTEBOOK, MOHAMED_METADATA, MUON_NOTEBOOK, MUON_METADATA]:
        if not path.exists():
            raise SystemExit(f"Missing required source: {path}")


def build_training_variant(spec: dict[str, Any]) -> dict[str, Any]:
    source_nb = json.loads(MOHAMED_NOTEBOOK.read_text(encoding="utf-8"))
    source_meta = json.loads(MOHAMED_METADATA.read_text(encoding="utf-8"))
    out_dir = OUT_ROOT / spec["folder"]
    out_dir.mkdir(parents=True, exist_ok=True)
    code_file = f"{spec['folder']}.ipynb"

    metadata = copy.deepcopy(source_meta)
    metadata.update(
        {
            "id": f"{KAGGLE_USER}/{remote_slug(spec)}",
            "title": spec["title"],
            "code_file": code_file,
            "is_private": "true",
            "enable_gpu": "true",
            "enable_tpu": False,
            "enable_internet": "false",
            "competition_sources": [COMPETITION],
            "machine_shape": "NvidiaRtxPro6000",
        }
    )
    metadata.pop("id_no", None)
    notebook = transform_mohamed_notebook(source_nb, spec)
    write_json(out_dir / "kernel-metadata.json", metadata)
    write_json(out_dir / code_file, notebook)
    return candidate_record(spec, out_dir, code_file, "full_training")


def transform_mohamed_notebook(source_nb: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    cells: list[dict[str, Any]] = [
        markdown_cell(
            spec["title"],
            [
                f"Mechanism: `{spec['mechanism']}`.",
                f"Hypothesis: {spec['hypothesis']}.",
                "Full training amount is preserved: rank 32, max sequence length 8192, 1000 steps, and 2,000,000 replay answer tokens.",
                "This notebook trains on Kaggle and packages `/kaggle/working/submission.zip`; it never submits the competition.",
            ],
        )
    ]
    seen_training_cell = False
    for raw_cell in source_nb.get("cells", []):
        src = "".join(raw_cell.get("source", []))
        if should_drop_source_cell(src):
            continue
        if "def run_training()" in src:
            if seen_training_cell:
                continue
            seen_training_cell = True
        cell = clean_cell(raw_cell)
        if cell["cell_type"] == "code":
            src = "".join(cell["source"])
            if "LORA_RANK" in src and "NUM_STEPS" in src and "TARGET_MODULES" in src:
                src = patch_training_config(src, spec)
            if "def run_training()" in src:
                src = sanitize_training_function(src)
                src = inject_training_mechanism(src, spec["code"])
                src = patch_packaging(src)
            if "del model" in src and "run_training()" in src:
                src = src.replace("del model\ngc.collect()", "globals().pop('model', None)\ngc.collect()")
            cell["source"] = lines(src)
        cells.append(cell)
    if not seen_training_cell:
        raise RuntimeError(f"No run_training definition retained for {spec['slug']}")
    return notebook_document(cells)


def patch_training_config(src: str, spec: dict[str, Any]) -> str:
    for old, new in spec.get("config_replacements", {}).items():
        src = src.replace(old, new)
    marker = f'''

# Stage 7 evidence-backed candidate.
STAGE7_CANDIDATE = "{spec["slug"]}"
STAGE7_MECHANISM = "{spec["mechanism"]}"
STAGE7_KEEP_FULL_TRAINING = True
STAGE7_EXPECTED_MAX_SEQ_LEN = 8192
STAGE7_EXPECTED_NUM_STEPS = 1000
STAGE7_EXPECTED_REPLAY_ANSWER_TOKENS = 2_000_000
'''
    if "STAGE7_CANDIDATE" not in src:
        src += marker
    return src


def inject_training_mechanism(src: str, mechanism_code: str) -> str:
    marker = """        print(
            f"Mixed corpus: {mixed_tokens:,} tokens "
            f"(unmasked={mixed_unmasked:,.0f})"
        )
"""
    if marker not in src:
        raise RuntimeError("Mohamed training-cell mixed-corpus marker not found")
    return src.replace(marker, marker + "\n" + mechanism_code.rstrip() + "\n", 1)


def sanitize_training_function(src: str) -> str:
    start_marker = "\n    else:  # IS_MODAL_WORKER\n        import shutil"
    end_marker = '        print("Kaggle upload complete.")'
    start = src.rfind(start_marker)
    if start >= 0:
        end = src.find(end_marker, start)
        if end >= 0:
            end += len(end_marker)
            src = src[:start] + '\n    else:\n        raise RuntimeError("Non-Kaggle upload path disabled")' + src[end:]
    return src


def patch_packaging(src: str) -> str:
    replacement = '''import hashlib
        def _sha256_file(_path):
            _digest = hashlib.sha256()
            with open(_path, "rb") as _handle:
                for _chunk in iter(lambda: _handle.read(1024 * 1024), b""):
                    _digest.update(_chunk)
            return _digest.hexdigest()
        with zipfile.ZipFile(SUBMISSION_ZIP, "r") as _zf:
            _names = sorted(_zf.namelist())
        if _names != ["adapter_config.json", "adapter_model.safetensors"]:
            raise RuntimeError(f"bad submission zip contents: {_names}")
        print("zip_namelist:", _names)
        print("submission_zip_size_bytes:", os.path.getsize(SUBMISSION_ZIP))
        print("submission_zip_sha256:", _sha256_file(SUBMISSION_ZIP))
        print("OK: /kaggle/working/submission.zip is ready.")'''
    if 'print(f"Wrote {SUBMISSION_ZIP}")' in src:
        src = src.replace('print(f"Wrote {SUBMISSION_ZIP}")', replacement, 1)
    return src


def build_muon_variant() -> dict[str, Any]:
    spec = {
        "slug": "nemotron-s7-muon-full",
        "folder": "nemotron_s7_muon_full",
        "title": "Nemotron S7 Muon Full Training",
        "mechanism": "muon_optimizer_training",
        "hypothesis": "use the public Muon implementation reported by a rank-45 competitor as a more stable optimizer path",
        "sources": [
            "https://www.kaggle.com/code/pkuszboi/0-85-lb-training-with-muon",
            "704491",
            "https://github.com/KellerJordan/Muon",
        ],
    }
    nb = json.loads(MUON_NOTEBOOK.read_text(encoding="utf-8"))
    meta = json.loads(MUON_METADATA.read_text(encoding="utf-8"))
    known_gpu_meta = json.loads(MOHAMED_METADATA.read_text(encoding="utf-8"))
    out_dir = OUT_ROOT / spec["folder"]
    out_dir.mkdir(parents=True, exist_ok=True)
    code_file = f"{spec['folder']}.ipynb"
    meta.update(
        {
            "id": f"{KAGGLE_USER}/{remote_slug(spec)}",
            "title": spec["title"],
            "code_file": code_file,
            "is_private": "true",
            "enable_gpu": "true",
            "enable_internet": "false",
            "competition_sources": [COMPETITION],
            "machine_shape": "NvidiaRtxPro6000",
            "docker_image": known_gpu_meta["docker_image"],
        }
    )
    meta.pop("id_no", None)
    nb["cells"].insert(
        0,
        markdown_cell(
            spec["title"],
            [
                f"Mechanism: `{spec['mechanism']}`.",
                "Source is the public Kaggle Muon training notebook referenced in discussion 704491.",
                "This notebook produces a submission package but never calls the competition submit API.",
            ],
        ),
    )
    nb["cells"].insert(
        1,
        code_cell(
            """
import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"

import torch

print("torch_version:", torch.__version__)
print("cuda_available:", torch.cuda.is_available())
if not torch.cuda.is_available():
    raise RuntimeError("Kaggle GPU allocation is required before importing Unsloth.")
print("cuda_device:", torch.cuda.get_device_name(0))
""".strip()
        ),
    )
    for cell in nb.get("cells", []):
        cell.pop("outputs", None) if cell.get("cell_type") != "code" else None
        if cell.get("cell_type") == "code":
            cell["execution_count"] = None
            cell["outputs"] = []
            src = "".join(cell.get("source", []))
            src = src.replace(
                "per_device_train_batch_size=2,",
                "per_device_train_batch_size=1,",
            )
            src = src.replace(
                "gradient_accumulation_steps=8,",
                "gradient_accumulation_steps=16,",
            )
            src = src.replace(
                "    from transformers import AutoModelForCausalLM\n"
                "    # 将原始模型加载到 CPU，避免占用宝贵的 GPU 显存\n"
                "    original_model = AutoModelForCausalLM.from_pretrained(\n"
                "        MODEL_PATH, \n"
                "        torch_dtype=torch.bfloat16, \n"
                '        device_map="cpu",\n'
                "        trust_remote_code=True,\n"
                "    )\n"
                "    original_state_dict = original_model.state_dict()\n",
                "",
            )
            if "submission.zip" in src and "zipfile" in src and "OK: /kaggle/working/submission.zip" not in src:
                src += '\nprint("OK: /kaggle/working/submission.zip is ready.")\n'
            cell["source"] = lines(src)
    nb["metadata"] = notebook_document([])["metadata"]
    assign_cell_ids(nb)
    write_json(out_dir / "kernel-metadata.json", meta)
    write_json(out_dir / code_file, nb)
    return candidate_record(spec, out_dir, code_file, "muon_training")


def build_fusion_variant(spec: dict[str, Any]) -> dict[str, Any]:
    out_dir = OUT_ROOT / spec["folder"]
    out_dir.mkdir(parents=True, exist_ok=True)
    code_file = f"{spec['folder']}.ipynb"
    metadata = {
        "id": f"{KAGGLE_USER}/{remote_slug(spec)}",
        "title": spec["title"],
        "code_file": code_file,
        "language": "python",
        "kernel_type": "notebook",
        "is_private": "true",
        "enable_gpu": "false",
        "enable_internet": "false",
        "dataset_sources": [],
        "competition_sources": [COMPETITION],
        "kernel_sources": [],
        "model_sources": [
            f"{KEITHTYSER_MODEL}/Transformers/{anchor}/1" for anchor in ANCHORS
        ],
    }
    source = fusion_source(spec)
    notebook = notebook_document(
        [
            markdown_cell(
                spec["title"],
                [
                    f"Mechanism: `{spec['mechanism']}`.",
                    f"Hypothesis: {spec['hypothesis']}.",
                    "This adapter-level operation does not load the 30B base model.",
                    "It writes a structurally checked `/kaggle/working/submission.zip` and never submits it.",
                ],
            ),
            code_cell(source),
        ]
    )
    write_json(out_dir / "kernel-metadata.json", metadata)
    write_json(out_dir / code_file, notebook)
    return candidate_record(spec, out_dir, code_file, "adapter_merge")


def fusion_source(spec: dict[str, Any]) -> str:
    template = r'''from pathlib import Path
import gc
import hashlib
import json
import re
import shutil
import zipfile

import torch
from safetensors.torch import load_file, save_file

CANDIDATE = "__CANDIDATE__"
METHOD = "__METHOD__"
INPUT_ROOT = Path("/kaggle/input")
WORKING_ROOT = Path("/kaggle/working")
OUT_DIR = WORKING_ROOT / CANDIDATE
ADAPTER_DIR = OUT_DIR / "adapter"
SUBMISSION_ZIP = WORKING_ROOT / "submission.zip"
PREFERRED = __PREFERRED__


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_adapters():
    found = []
    for cfg_path in sorted(INPUT_ROOT.rglob("adapter_config.json")):
        model_path = cfg_path.parent / "adapter_model.safetensors"
        if not model_path.exists():
            continue
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        lower = str(cfg_path.parent).lower()
        slug = next((name for name in PREFERRED if name.lower() in lower), cfg_path.parent.name)
        found.append({"slug": slug, "cfg": cfg_path, "model": model_path, "rank": cfg.get("r"), "targets": cfg.get("target_modules")})
    by_slug = {item["slug"]: item for item in found}
    selected = [by_slug[name] for name in PREFERRED if name in by_slug]
    if len(selected) < 3:
        selected = found[:3]
    if len(selected) < 3:
        raise RuntimeError(f"need three compatible adapters, found {len(selected)}")
    ranks = {int(item["rank"]) for item in selected}
    targets = {json.dumps(item["targets"], sort_keys=True) for item in selected}
    if max(ranks) > 32 or len(targets) != 1:
        raise RuntimeError(f"incompatible adapter configs: ranks={ranks}, target_sets={len(targets)}")
    return selected


def layer_number(key):
    match = re.search(r"\.layers\.(\d+)\.", key)
    return int(match.group(1)) if match else -1


def merge_tensor(key, tensors):
    base = tensors[0].float()
    deltas = [tensor.float() - base for tensor in tensors[1:]]
    if METHOD == "ties":
        stacked = torch.stack(deltas)
        threshold = torch.quantile(stacked.abs().reshape(-1), 0.20)
        trimmed = torch.where(stacked.abs() >= threshold, stacked, torch.zeros_like(stacked))
        elected = torch.sign(trimmed.sum(dim=0))
        agrees = torch.sign(trimmed) == elected.unsqueeze(0)
        counts = agrees.sum(dim=0).clamp_min(1)
        merged_delta = torch.where(agrees, trimmed, torch.zeros_like(trimmed)).sum(dim=0) / counts
        return base + 0.55 * merged_delta
    if METHOD == "dare":
        generator = torch.Generator(device="cpu").manual_seed(20260606 + max(0, layer_number(key)))
        kept = []
        density = 0.55
        for delta in deltas:
            mask = torch.rand(delta.shape, generator=generator) < density
            kept.append(torch.where(mask, delta / density, torch.zeros_like(delta)))
        return base + 0.45 * torch.stack(kept).mean(dim=0)
    if METHOD == "layerwise":
        lower = key.lower()
        if "mamba" in lower or "in_proj" in lower or "out_proj" in lower:
            weights = [0.45, 0.35, 0.20]
        elif "expert" in lower or "gate_up_proj" in lower or "down_proj" in lower:
            weights = [0.55, 0.20, 0.25]
        elif "lm_head" in lower:
            weights = [0.35, 0.45, 0.20]
        else:
            weights = [0.50, 0.25, 0.25]
        return sum(weight * tensor.float() for weight, tensor in zip(weights, tensors))
    raise RuntimeError(f"unknown method {METHOD}")


selected = find_adapters()
print("selected_adapters:", [(item["slug"], item["rank"], str(item["model"])) for item in selected])
all_tensors = [load_file(str(item["model"]), device="cpu") for item in selected]
keys = sorted(all_tensors[0])
for item in all_tensors[1:]:
    if sorted(item) != keys:
        raise RuntimeError("adapter tensor keys differ")

merged = {}
for index, key in enumerate(keys):
    values = [item[key] for item in all_tensors]
    shapes = {tuple(value.shape) for value in values}
    if len(shapes) != 1:
        raise RuntimeError(f"shape mismatch for {key}: {shapes}")
    merged[key] = merge_tensor(key, values).to(values[0].dtype)
    if index % 250 == 0:
        print("merged_tensors:", index, "/", len(keys))

OUT_DIR.mkdir(parents=True, exist_ok=True)
ADAPTER_DIR.mkdir(parents=True, exist_ok=True)
cfg_out = ADAPTER_DIR / "adapter_config.json"
model_out = ADAPTER_DIR / "adapter_model.safetensors"
shutil.copyfile(selected[0]["cfg"], cfg_out)
save_file(merged, str(model_out))
if model_out.stat().st_size < 100 * 1024 * 1024:
    raise RuntimeError(
        f"adapter_model.safetensors is unexpectedly small: {model_out.stat().st_size} bytes"
    )
del all_tensors, merged
gc.collect()

if SUBMISSION_ZIP.exists():
    SUBMISSION_ZIP.unlink()
with zipfile.ZipFile(SUBMISSION_ZIP, "w", zipfile.ZIP_STORED) as zf:
    zf.write(cfg_out, "adapter_config.json")
    zf.write(model_out, "adapter_model.safetensors")
with zipfile.ZipFile(SUBMISSION_ZIP, "r") as zf:
    names = sorted(zf.namelist())
if names != ["adapter_config.json", "adapter_model.safetensors"]:
    raise RuntimeError(f"bad zip contents: {names}")
if SUBMISSION_ZIP.stat().st_size < 100 * 1024 * 1024:
    raise RuntimeError(
        f"submission.zip is unexpectedly small: {SUBMISSION_ZIP.stat().st_size} bytes"
    )
report = {
    "candidate": CANDIDATE,
    "method": METHOD,
    "source_adapters": [item["slug"] for item in selected],
    "adapter_model_sha256": sha256_file(model_out),
    "submission_zip_sha256": sha256_file(SUBMISSION_ZIP),
    "submission_zip_size_bytes": SUBMISSION_ZIP.stat().st_size,
    "zip_namelist": names,
    "rank_lte_32": True,
}
(WORKING_ROOT / f"{CANDIDATE}_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
print("OK: /kaggle/working/submission.zip is ready.")
'''
    return (
        template.replace("__CANDIDATE__", spec["slug"])
        .replace("__METHOD__", spec["method"])
        .replace("__PREFERRED__", json.dumps(ANCHORS))
    )


def should_drop_source_cell(src: str) -> bool:
    return any(marker in src for marker in ["Modal glue", "import modal", "modal.App"])


def clean_cell(raw_cell: dict[str, Any]) -> dict[str, Any]:
    if raw_cell.get("cell_type") == "code":
        return code_cell("".join(raw_cell.get("source", [])))
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": raw_cell.get("source", []),
    }


def candidate_record(spec: dict[str, Any], out_dir: Path, code_file: str, route_type: str) -> dict[str, Any]:
    return {
        "slug": spec["slug"],
        "title": spec["title"],
        "route_type": route_type,
        "mechanism": spec["mechanism"],
        "hypothesis": spec["hypothesis"],
        "sources": spec["sources"],
        "kernel_id": f"{KAGGLE_USER}/{remote_slug(spec)}",
        "kernel_dir": str(out_dir.relative_to(PROJECT_ROOT)),
        "metadata_path": str((out_dir / "kernel-metadata.json").relative_to(PROJECT_ROOT)),
        "notebook_path": str((out_dir / code_file).relative_to(PROJECT_ROOT)),
        "push_command": f'kaggle kernels push -p "{out_dir.relative_to(PROJECT_ROOT)}"',
        "competition_submit_called": False,
    }


def remote_slug(spec: dict[str, Any]) -> str:
    return re.sub(r"[^a-z0-9]+", "-", spec["title"].lower()).strip("-")


def validate_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    metadata_path = PROJECT_ROOT / candidate["metadata_path"]
    notebook_path = PROJECT_ROOT / candidate["notebook_path"]
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    nb = json.loads(notebook_path.read_text(encoding="utf-8"))
    text = "\n".join("".join(cell.get("source", [])) for cell in nb.get("cells", []))
    checks = {
        "metadata_id_matches": meta.get("id") == candidate["kernel_id"],
        "notebook_exists": notebook_path.exists(),
        "submission_zip_output_declared": "submission.zip" in text,
        "success_marker_declared": "OK: /kaggle/working/submission.zip is ready." in text,
        "no_competition_submit": "kaggle competitions submit" not in text,
        "no_literal_secret": "Bearer " not in text and '"username"' not in text and '"key"' not in text,
        "mechanism_recorded": candidate["mechanism"] in text,
    }
    if candidate["route_type"] == "full_training":
        definition = text.find("def run_training()")
        call = text.rfind("run_training()")
        checks.update(
            {
                "gpu_enabled": str(meta.get("enable_gpu")).lower() == "true",
                "training_definition_present": definition >= 0,
                "training_call_after_definition": definition >= 0 and call > definition,
                "rank_32_preserved": "LORA_RANK = 32" in text,
                "max_seq_8192_preserved": "MAX_SEQ_LEN = 8192" in text,
                "steps_1000_preserved": "NUM_STEPS = 1000" in text,
                "replay_tokens_2m_preserved": "TARGET_REPLAY_ANSWER_TOKENS = 2_000_000" in text,
            }
        )
    elif candidate["route_type"] == "muon_training":
        checks.update(
            {
                "gpu_enabled": str(meta.get("enable_gpu")).lower() == "true",
                "gpu_machine_shape": meta.get("machine_shape") == "NvidiaRtxPro6000",
                "cuda_preflight_present": "Kaggle GPU allocation is required before importing Unsloth." in text,
                "rank_32_preserved": "LORA_RANK = 32" in text,
                "max_seq_8192_preserved": "MAX_SEQ_LEN = 8192" in text,
                "full_epoch_preserved": "num_train_epochs=1" in text,
                "microbatch_one": "per_device_train_batch_size=1" in text,
                "effective_batch_preserved": "gradient_accumulation_steps=16" in text,
                "expandable_segments": "expandable_segments:True" in text,
            }
        )
    valid = all(checks.values())
    return {"slug": candidate["slug"], "valid": valid, "checks": checks}


def write_report(candidates: list[dict[str, Any]]) -> None:
    rows = [
        "# Stage 7 Diverse Notebook Candidates",
        "",
        "These candidates were designed after reviewing current competition discussions, public training notebooks, adapter-merge papers, and prior failed submissions. They are mechanism-diverse rather than small hyperparameter variants.",
        "",
        "## Evidence Chain",
        "",
    ]
    for item in COMMON_EVIDENCE:
        rows.append(f"- [{item['source']}]({item['url']}): {item['lesson']}.")
    rows.extend(
        [
            "",
            "Additional implementation sources:",
            "",
            "- `mohamedamr992/nemotron-replay-data-0-86`: our verified 0.86 training family.",
            "- `pkuszboi/0-85-lb-training-with-muon`: public Muon training implementation.",
            "- `tonghuikang/nemotron`: training, loss, corpus, and schedule reference.",
            "- `lkevincc0/kaggle-nemotron-equation-symbolic`: symbolic data-oracle reference.",
            "- TIES-Merging, DARE, AdaLoRA, and model-soup literature for merge/rank/interference control.",
            "",
            "## Candidate List",
            "",
            "| # | Kernel | Route | Mechanism | Hypothesis |",
            "|---:|---|---|---|---|",
        ]
    )
    for index, item in enumerate(candidates, start=1):
        rows.append(
            f"| {index} | `{item['kernel_id']}` | {item['route_type']} | "
            f"`{item['mechanism']}` | {item['hypothesis']} |"
        )
    rows.extend(
        [
            "",
            "## Reference Submission Order",
            "",
            "This is a preparation order, not permission to submit. Official submission still requires a completed kernel, a valid output package, a unique SHA256, quota availability, and explicit user confirmation.",
            "",
            "1. `nemotron-s7-protected-rehearsal` - directly addresses observed category forgetting.",
            "2. `nemotron-s7-muon-full` - optimizer/stability mechanism backed by a public competition notebook.",
            "3. `nemotron-s7-ties-sign-merge` - interference-aware merge over 0.86-class anchors.",
            "4. `nemotron-s7-weak-protected-curriculum` - balances weak and saturated categories.",
            "5. `nemotron-s7-mamba-inproj-specialist` - structurally constrained adaptation.",
            "6. `nemotron-s7-category-roundrobin` - category order balancing.",
            "7. `nemotron-s7-answer-tail-objective` - objective/loss-mask change.",
            "8. `nemotron-s7-dare-merge` - sparse delta merge.",
            "9. `nemotron-s7-layerwise-soup` - module-aware weighted merge.",
            "10. `nemotron-s7-length-stratified` - sequence-difficulty curriculum.",
            "11. `nemotron-s7-seed-stability-replay` - reproducibility control candidate.",
            "",
            "No `kaggle competitions submit` command is executed by the generator or notebooks.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(rows), encoding="utf-8")


def write_validation(results: list[dict[str, Any]]) -> None:
    rows = [
        "# Stage 7 Diverse Notebook Validation",
        "",
        "| candidate | valid | failed checks |",
        "|---|---:|---|",
    ]
    for item in results:
        failed = [name for name, ok in item["checks"].items() if not ok]
        rows.append(f"| `{item['slug']}` | {str(item['valid']).lower()} | {', '.join(failed) or 'none'} |")
    VALIDATION_PATH.write_text("\n".join(rows) + "\n", encoding="utf-8")


def markdown_cell(title: str, paragraphs: list[str]) -> dict[str, Any]:
    source = [f"# {title}\n", "\n"]
    for paragraph in paragraphs:
        source.extend([paragraph + "\n", "\n"])
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def code_cell(source: str) -> dict[str, Any]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": lines(source),
    }


def notebook_document(cells: list[dict[str, Any]]) -> dict[str, Any]:
    document = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    assign_cell_ids(document)
    return document


def assign_cell_ids(notebook: dict[str, Any]) -> None:
    for index, cell in enumerate(notebook.get("cells", [])):
        source = "".join(cell.get("source", []))
        digest = hashlib.sha1(f"{index}:{source}".encode("utf-8")).hexdigest()[:12]
        cell["id"] = digest


def lines(text: str) -> list[str]:
    return [line + "\n" for line in text.splitlines()]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
