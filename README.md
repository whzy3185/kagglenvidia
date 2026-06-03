# Nemotron 0.86+ Repro System

This repository is a staged Kaggle workflow for `nvidia-nemotron-model-reasoning-challenge`.

Current default stage: Stage 1 asset audit and minimal submission loop.

Safety rules:

- Do not train locally on RTX 4060 except lightweight validation.
- Do not submit without score gate approval and daily quota check.
- Do not load the Nemotron base model in local validation scripts.
- Do not store Kaggle tokens in the repository.
- Do not treat structural-valid packages as official-valid.

Common commands:

```powershell
python scripts/00_check_kaggle_cli.py
python scripts/01_asset_audit.py
python scripts/04_query_submissions.py
python scripts/05_stage1_dry_run.py
python scripts/02_validate_adapter.py --adapter-dir path/to/adapter
python scripts/03_pack_submission.py --adapter-dir path/to/adapter
```

Later-stage scripts are gated. They should report missing prerequisites instead of fabricating training, proxy eval, scores, or submissions.
