from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nemotron086.reporting import write_text  # noqa: E402
from nemotron086.safety import redact_sensitive  # noqa: E402


DEFAULT_KERNEL_DIR = PROJECT_ROOT / "kaggle_kernels" / "nemotron_repack_huikang_v27"


def main() -> int:
    parser = argparse.ArgumentParser(description="Push a Kaggle-side repack notebook.")
    parser.add_argument("--kernel-dir", default=str(DEFAULT_KERNEL_DIR))
    args = parser.parse_args()

    kernel_dir = Path(args.kernel_dir)
    if not kernel_dir.is_absolute():
        kernel_dir = PROJECT_ROOT / kernel_dir

    metadata_path = kernel_dir / "kernel-metadata.json"
    metadata: dict[str, Any] = {}
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    code_file = metadata.get("code_file") if isinstance(metadata.get("code_file"), str) else "nemotron_repack_huikang_v27.ipynb"
    notebook_path = kernel_dir / code_file
    missing = [str(path.relative_to(PROJECT_ROOT)) for path in [metadata_path, notebook_path] if not path.exists()]
    payload: dict[str, Any] = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "kernel_dir": str(kernel_dir),
        "metadata_path": str(metadata_path),
        "notebook_path": str(notebook_path),
        "missing_files": missing,
        "success": False,
    }

    if missing:
        payload["failure_reason"] = "missing_required_files"
        write_report(payload)
        print(f"missing required files: {missing}")
        return 4

    kernel_id = metadata.get("id")
    if not isinstance(kernel_id, str) or "/" not in kernel_id:
        payload["failure_reason"] = "invalid_kernel_id"
        payload["kernel_id"] = kernel_id
        write_report(payload)
        print(f"invalid kernel id in metadata: {kernel_id!r}")
        return 4

    push_command = ["kaggle", "kernels", "push", "-p", str(kernel_dir)]
    status_command = ["kaggle", "kernels", "status", kernel_id]
    files_command = ["kaggle", "kernels", "files", kernel_id]
    payload.update(
        {
            "kernel_id": kernel_id,
            "push_command": " ".join(push_command),
            "status_check_command": " ".join(status_command),
            "files_check_command": " ".join(files_command),
        }
    )

    push_result = run_command(push_command)
    payload["push_result"] = push_result
    if push_result["returncode"] != 0:
        payload["failure_reason"] = "kernel_push_failed"
        write_report(payload)
        print("kernel push failed")
        print(push_result["stderr"] or push_result["stdout"])
        return push_result["returncode"] or 5

    payload["status_result"] = run_command(status_command)
    payload["files_result"] = run_command(files_command)
    payload["success"] = True
    write_report(payload)

    print(f"kernel id: {kernel_id}")
    print(f"push ok: true")
    print(f"status check: {' '.join(status_command)}")
    print(f"files check: {' '.join(files_command)}")
    print("manual submit path: Kaggle Notebook -> Output -> submission.zip -> Submit to Competition")
    return 0


def run_command(command: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            text=True,
            capture_output=True,
            timeout=7200,
        )
        return {
            "command": " ".join(command),
            "returncode": completed.returncode,
            "stdout": redact_sensitive(completed.stdout),
            "stderr": redact_sensitive(completed.stderr),
        }
    except FileNotFoundError as exc:
        return {
            "command": " ".join(command),
            "returncode": 127,
            "stdout": "",
            "stderr": redact_sensitive(str(exc)),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": " ".join(command),
            "returncode": 124,
            "stdout": redact_sensitive(exc.stdout or ""),
            "stderr": redact_sensitive(exc.stderr or "command timed out"),
        }


def write_report(payload: dict[str, Any]) -> None:
    content = render_report(payload)
    write_text(PROJECT_ROOT / "reports" / "KAGGLE_NOTEBOOK_PUSH_REPORT.md", content)


def render_report(payload: dict[str, Any]) -> str:
    push = payload.get("push_result", {})
    status = payload.get("status_result", {})
    files = payload.get("files_result", {})
    return f"""# Kaggle Notebook Push Report

- timestamp: {payload.get('timestamp')}
- success: {payload.get('success')}
- kernel id: `{payload.get('kernel_id')}`
- kernel dir: `{payload.get('kernel_dir')}`
- push command: `{payload.get('push_command')}`
- status check command: `{payload.get('status_check_command')}`
- files check command: `{payload.get('files_check_command')}`
- missing files: `{payload.get('missing_files')}`
- failure reason: `{payload.get('failure_reason')}`

## Push Result

- returncode: {push.get('returncode')}

```text
{push.get('stdout', '')}
{push.get('stderr', '')}
```

## Status Result

- returncode: {status.get('returncode')}

```text
{status.get('stdout', '')}
{status.get('stderr', '')}
```

## Files Result

- returncode: {files.get('returncode')}

```text
{files.get('stdout', '')}
{files.get('stderr', '')}
```

## Manual Submit

After the notebook run succeeds and `submission.zip` appears in Output:

```text
Kaggle Notebook -> Output -> submission.zip -> Submit to Competition
```
"""


if __name__ == "__main__":
    raise SystemExit(main())
