from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any


FORBIDDEN_DIRS = {"fusion", "daily_runner"}
FORBIDDEN_SCRIPT_NAMES = {
    "12_daily_runner.py",
}
FORBIDDEN_IMPORTS = {"selenium", "playwright", "pyppeteer"}
SCAN_DIRS = ("scripts", "src")
CODE_SCAN_EXCLUDES = {Path("src") / "nemotron086" / "safety.py"}

DANGEROUS_CODE_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "multi_account_logic": [
        re.compile(r"(?i)\bmulti[_-]?account\b"),
        re.compile(r"(?i)\b(account|user)\s*(rotation|rotator|switching)\b"),
    ],
    "quota_bypass_logic": [
        re.compile(r"(?i)\bquota[_-]?bypass\b"),
        re.compile(r"(?i)\bbypass\w*\s+quota\b"),
        re.compile(r"(?i)\bquota\s+bypass\w*\b"),
    ],
    "token_printing": [
        re.compile(r"(?i)\bprint\s*\([^)]*(token|kaggle_key|kaggle_api_token|password|secret)[^)]*\)"),
    ],
    "large_model_download": [
        re.compile(r"(?i)\bsnapshot_download\s*\("),
        re.compile(r"(?i)\bhf_hub_download\s*\("),
        re.compile(r"(?i)\bgit\s+lfs\b"),
        re.compile(r"(?i)\b(wget|curl)\b.*\b(model|nemotron|safetensors|checkpoint|weights)\b"),
    ],
    "base_model_loading": [
        re.compile(r"(?i)\bAutoModel(ForCausalLM)?\s*\.\s*from_pretrained\s*\("),
        re.compile(r"(?i)\bfrom_pretrained\s*\([^)]*nemotron"),
        re.compile(r"(?i)\btransformers\b.*\bfrom_pretrained\s*\("),
    ],
    "unsafe_submit": [
        re.compile(r"(?i)\bkaggle\s+competitions\s+submit\b(?!.*score_gate)"),
        re.compile(r"(?i)\bcompetition_submit\s*\("),
    ],
}


def redact_sensitive(text: str) -> str:
    redacted = text
    patterns = [
        r"(?i)(KAGGLE_KEY\s*=\s*)[^\s]+",
        r"(?i)(token\s*[:=]\s*)[^\s,;]+",
        r"(?i)(password\s*[:=]\s*)[^\s,;]+",
        r"(?i)(key\s*[:=]\s*)[A-Za-z0-9_\-]{16,}",
    ]
    for pattern in patterns:
        redacted = re.sub(pattern, r"\1<redacted>", redacted)
    return redacted


def ensure_stage1_safety(project_root: Path) -> dict[str, Any]:
    forbidden_paths = []
    for name in FORBIDDEN_DIRS:
        path = project_root / name
        if path.exists():
            forbidden_paths.append(str(path.relative_to(project_root)))
    for name in FORBIDDEN_SCRIPT_NAMES:
        path = project_root / "scripts" / name
        if path.exists():
            forbidden_paths.append(str(path.relative_to(project_root)))

    kaggle_json = [
        str(path.relative_to(project_root))
        for path in project_root.rglob("kaggle.json")
        if path.is_file()
    ]
    forbidden_imports = _find_forbidden_imports(project_root)
    dangerous_code = _find_dangerous_code(project_root)

    violations = forbidden_paths + kaggle_json + forbidden_imports + dangerous_code
    return {
        "stage1_safety_valid": not violations,
        "forbidden_paths_found": forbidden_paths,
        "kaggle_json_found": kaggle_json,
        "forbidden_imports_found": forbidden_imports,
        "dangerous_code_patterns_found": dangerous_code,
    }


def _find_forbidden_imports(project_root: Path) -> list[str]:
    findings: list[str] = []
    for path in _iter_stage1_python_files(project_root):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            module_names: list[str] = []
            if isinstance(node, ast.Import):
                module_names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                module_names = [node.module]
            for module_name in module_names:
                root = module_name.split(".", 1)[0]
                if root in FORBIDDEN_IMPORTS:
                    findings.append(f"{path.relative_to(project_root)} imports {root}")
    return findings


def _find_dangerous_code(project_root: Path) -> list[str]:
    findings: list[str] = []
    for path in _iter_stage1_python_files(project_root):
        rel_path = path.relative_to(project_root)
        if rel_path in CODE_SCAN_EXCLUDES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for category, patterns in DANGEROUS_CODE_PATTERNS.items():
            for pattern in patterns:
                if pattern.search(text):
                    findings.append(f"{rel_path} matches {category}")
                    break
    return findings


def _iter_stage1_python_files(project_root: Path) -> list[Path]:
    files: list[Path] = []
    for directory in SCAN_DIRS:
        root = project_root / directory
        if root.exists():
            files.extend(sorted(root.rglob("*.py")))
    return files
