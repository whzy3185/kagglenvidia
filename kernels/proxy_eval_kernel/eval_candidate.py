from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


OUT = Path("/kaggle/working")
KAGGLE_INPUT = Path("/kaggle/input")
CONFIG_PATH = Path(__file__).with_name("proxy_eval_kernel_config.json")
PROXY_SET_DIR = Path(os.environ.get("PROXY_SET_DIR", ""))
ADAPTER_DIR = Path(os.environ.get("ADAPTER_DIR", ""))
BASE_MODEL = os.environ.get("BASE_MODEL", "nvidia/NVIDIA-Nemotron-3-Nano-30B-v2")


def load_config() -> dict:
    candidates = [
        CONFIG_PATH,
        Path.cwd() / "proxy_eval_kernel_config.json",
        OUT / "proxy_eval_kernel_config.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return json.loads(candidate.read_text(encoding="utf-8"))
    return {}


def load_proxy_set(proxy_dir: Path) -> list[dict]:
    samples = []
    for path in sorted(proxy_dir.glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    samples.append(json.loads(line))
    return samples


def find_proxy_set_dir(config: dict) -> Path | None:
    configured = os.environ.get("PROXY_SET_DIR") or config.get("proxy_set_dir")
    if configured:
        path = Path(configured)
        if path.exists():
            return path
    if KAGGLE_INPUT.exists():
        for candidate in sorted(KAGGLE_INPUT.rglob("*.jsonl")):
            if candidate.name.startswith("generated_"):
                return candidate.parent
    return None


def find_adapter_dir(config: dict) -> Path | None:
    configured = os.environ.get("ADAPTER_DIR") or config.get("adapter_dir")
    if configured:
        path = Path(configured)
        if (path / "adapter_config.json").exists() and (path / "adapter_model.safetensors").exists():
            return path
    if KAGGLE_INPUT.exists():
        for candidate in sorted(KAGGLE_INPUT.rglob("adapter_config.json")):
            adapter_dir = candidate.parent
            if (adapter_dir / "adapter_model.safetensors").exists():
                return adapter_dir
    return None


def find_base_model(config: dict) -> str:
    configured = os.environ.get("BASE_MODEL") or config.get("base_model")
    if KAGGLE_INPUT.exists():
        for candidate in sorted(KAGGLE_INPUT.rglob("config.json")):
            model_dir = candidate.parent
            if (model_dir / "adapter_config.json").exists():
                continue
            has_weight = any(model_dir.glob("*.safetensors")) or any(model_dir.glob("*.bin"))
            if has_weight:
                return str(model_dir)
    return str(configured or BASE_MODEL)


def inference_enabled(config: dict, proxy_set_dir: Path | None, adapter_dir: Path | None) -> bool:
    if os.environ.get("ENABLE_PROXY_INFERENCE") == "1":
        return True
    if os.environ.get("ENABLE_PROXY_INFERENCE") == "0":
        return False
    if KAGGLE_INPUT.exists() and proxy_set_dir and adapter_dir:
        return True
    return bool(config.get("enable_proxy_inference"))


def main() -> None:
    config = load_config()
    proxy_set_dir = find_proxy_set_dir(config)
    adapter_dir = find_adapter_dir(config)
    samples = load_proxy_set(proxy_set_dir) if proxy_set_dir else []
    base_model = find_base_model(config)
    if not inference_enabled(config, proxy_set_dir, adapter_dir):
        result = {
            "stage": 3,
            "status": "staging_only",
            "base_model_loaded": False,
            "adapter_dir": str(adapter_dir) if adapter_dir else None,
            "proxy_set_dir": str(proxy_set_dir) if proxy_set_dir else None,
            "proxy_samples": len(samples),
            "message": "Set ENABLE_PROXY_INFERENCE=1 or proxy_eval_kernel_config.enable_proxy_inference=true after manual review.",
        }
        (OUT / "proxy_eval_kernel_report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        return
    if not proxy_set_dir or not samples:
        write_blocked("proxy_set_missing_or_empty", adapter_dir, proxy_set_dir, samples)
        return
    if not adapter_dir:
        write_blocked("adapter_dir_missing", adapter_dir, proxy_set_dir, samples)
        return

    try:
        try:
            predictions, backend = generate_with_vllm(base_model, adapter_dir, samples)
        except ModuleNotFoundError as exc:
            if exc.name != "vllm":
                raise
            predictions, backend = generate_with_transformers(base_model, adapter_dir, samples)
    except Exception as exc:
        write_blocked(f"inference_failed:{type(exc).__name__}:{str(exc)[:500]}", adapter_dir, proxy_set_dir, samples)
        return
    with (OUT / "proxy_predictions.jsonl").open("w", encoding="utf-8") as handle:
        for row in predictions:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    (OUT / "proxy_eval_kernel_report.json").write_text(
        json.dumps(
            {
                "stage": 3,
                "status": "predictions_generated",
                "base_model_loaded": True,
                "adapter_dir": str(adapter_dir),
                "proxy_set_dir": str(proxy_set_dir),
                "base_model": base_model,
                "backend": backend,
                "proxy_samples": len(samples),
                "predictions_path": "proxy_predictions.jsonl",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def generate_with_vllm(base_model: str, adapter_dir: Path, samples: list[dict]) -> tuple[list[dict], str]:
    from vllm import LLM, SamplingParams
    from vllm.lora.request import LoRARequest

    llm = LLM(
        model=base_model,
        enable_lora=True,
        max_model_len=int(os.environ.get("MAX_MODEL_LEN", "4096")),
        trust_remote_code=True,
    )
    sampling = SamplingParams(temperature=0.0, max_tokens=int(os.environ.get("MAX_TOKENS", "512")))
    prompts = [sample["prompt"] for sample in samples]
    outputs = llm.generate(prompts, sampling, lora_request=LoRARequest("candidate_adapter", 1, str(adapter_dir)))
    predictions = []
    for sample, output in zip(samples, outputs):
        text = output.outputs[0].text if output.outputs else ""
        predictions.append({"id": sample["id"], "output": text})
    return predictions, "vllm"


def generate_with_transformers(base_model: str, adapter_dir: Path, samples: list[dict]) -> tuple[list[dict], str]:
    ensure_mamba_runtime()
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        device_map="auto",
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(model, str(adapter_dir))
    model.eval()
    predictions = []
    max_new_tokens = int(os.environ.get("MAX_TOKENS", "512"))
    for sample in samples:
        inputs = tokenizer(sample["prompt"], return_tensors="pt").to(model.device)
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                do_sample=False,
                max_new_tokens=max_new_tokens,
                pad_token_id=tokenizer.eos_token_id,
            )
        new_tokens = output_ids[0][inputs["input_ids"].shape[-1] :]
        text = tokenizer.decode(new_tokens, skip_special_tokens=True)
        predictions.append({"id": sample["id"], "output": text})
    return predictions, "transformers_peft"


def ensure_mamba_runtime() -> None:
    force_source_build = os.environ.get("FORCE_SOURCE_BUILD_MAMBA", "1") == "1"
    if not force_source_build:
        try:
            import mamba_ssm  # noqa: F401

            return
        except Exception:
            pass
    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--quiet",
        "--force-reinstall",
        "--no-deps",
        "--no-build-isolation",
        "--no-binary",
        "mamba-ssm",
        "--no-binary",
        "causal-conv1d",
        "mamba-ssm",
        "causal-conv1d",
    ]
    completed = subprocess.run(command, text=True, capture_output=True, timeout=1800)
    if completed.returncode != 0:
        raise RuntimeError(
            "failed_to_install_mamba_runtime: "
            + (completed.stderr or completed.stdout or "unknown pip install failure")[-1000:]
        )


def write_blocked(status: str, adapter_dir: Path | None, proxy_set_dir: Path | None, samples: list[dict]) -> None:
    (OUT / "proxy_eval_kernel_report.json").write_text(
        json.dumps(
            {
                "stage": 3,
                "status": status,
                "base_model_loaded": False,
                "adapter_dir": str(adapter_dir) if adapter_dir else None,
                "proxy_set_dir": str(proxy_set_dir) if proxy_set_dir else None,
                "proxy_samples": len(samples),
                "predictions_path": None,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
