# Stage 2 Baseline Decision

selected_route:
  name: tong_full_repro
  classification: candidate_adapter
  source_url: https://www.kaggle.com/models/huikang/nemotron-adapter
  model_version_ref: huikang/nemotron-adapter/Transformers/default/27
  reason: "Research reports and Kaggle CLI file listing confirm adapter_config.json and adapter_model.safetensors are available."
  evidence:
    - e:/deep-research-report.md
    - e:/NVIDIA Nemotron 推理挑战公开高分方案研究报告 (1).docx
    - kaggle models instances versions files huikang/nemotron-adapter/Transformers/default/27
  risks:
    - license_status_unknown
    - official_format_not_confirmed_by_submission
    - public_score_claim_not_locally_verified
  can_validate_and_pack: true
