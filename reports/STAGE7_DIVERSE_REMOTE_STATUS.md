# Stage 7 Diverse Remote Status

- updated_at: 2026-06-07T03:34:07
- expected_candidates: 11
- checked_candidates: 11
- state_counts: `{"output_ready": 4, "uploaded_status_unknown": 7}`
- competition_submission_executed: false

| kernel | route | mechanism | remote state | output | success marker | SHA256 |
|---|---|---|---|---:|---:|---|
| `muelsyse111/nemotron-s7-seed-stability-replay` | full_training | `deterministic_seed_and_reproducible_shuffle` | output_ready | true | true | `f5dde9e053d7` |
| `muelsyse111/nemotron-s7-category-round-robin` | full_training | `category_balanced_round_robin_curriculum` | uploaded_status_unknown | false | false | `n/a` |
| `muelsyse111/nemotron-s7-protected-rehearsal` | full_training | `protected_category_loss_reweighting` | uploaded_status_unknown | false | false | `n/a` |
| `muelsyse111/nemotron-s7-weak-protected-curriculum` | full_training | `weak_category_plus_protected_interleaving` | uploaded_status_unknown | false | false | `n/a` |
| `muelsyse111/nemotron-s7-answer-tail-objective` | full_training | `tail_focused_loss_masking` | uploaded_status_unknown | false | false | `n/a` |
| `muelsyse111/nemotron-s7-length-stratified-curriculum` | full_training | `alternating_long_short_sequence_curriculum` | uploaded_status_unknown | false | false | `n/a` |
| `muelsyse111/nemotron-s7-mamba-inproj-specialist` | full_training | `selective_mamba_in_proj_adaptation` | uploaded_status_unknown | false | false | `n/a` |
| `muelsyse111/nemotron-s7-muon-full-training` | muon_training | `muon_optimizer_training` | uploaded_status_unknown | false | false | `n/a` |
| `muelsyse111/nemotron-s7-ties-sign-merge` | adapter_merge | `ties_trim_elect_sign_merge` | output_ready | true | true | `b03e975ea48d` |
| `muelsyse111/nemotron-s7-dare-merge` | adapter_merge | `dare_drop_and_rescale_merge` | output_ready | true | true | `4f37c3377e93` |
| `muelsyse111/nemotron-s7-layerwise-adapter-soup` | adapter_merge | `module_aware_layerwise_weighted_soup` | output_ready | true | true | `4480e232def3` |

## Diagnostics

### muelsyse111/nemotron-s7-seed-stability-replay

- remote_state: `output_ready`
- status_returncode: `1`
- files_returncode: `0`
- logs_returncode: `0`

```text
500 Server Error: Internal Server Error for url: https://api.kaggle.com/v1/kernels.KernelsApiService/GetKernelSessionStatus
name,size,creationDate

README.md,858,"3:38 pm, Saturday 6 June 2026 UTC"

replay_math_tokenized.jsonl,917,"3:38 pm, Saturday 6 June 2026 UTC"

submission.zip,873,"3:38 pm, Saturday 6 June 2026 UTC"
1,"data":"    micro-batch 2: 4 seqs, max_len=7411, total_len=18424, wall=7.0s, peak=96.8GB, mem=77.7GB\n"}
,{"stream_name":"stdout","time":13280.160960922,"data":"    micro-batch 3: 4 seqs, max_len=8191, total_len=24622, wall=7.5s, peak=96.8GB, mem=77.7GB\n"}
,{"stream_name":"stdout","time":13286.252734854,"data":"    micro-batch 4: 4 seqs, max_len=6168, total_len=12808, wall=6.1s, peak=96.8GB, mem=77.6GB\n"}
,{"stream_name":"stdout","time":13290.651797819,"data":"    micro-batch 5: 4 seqs, max_len=3990, total_len=10155, wall=4.4s, peak=96.8GB, mem=77.5GB\n"}
,{"stream_name":"stdout","time":13295.064531714,"data":"    micro-batch 6: 4 seqs, max_len=4013, total_len=11486, wall=4.4s, peak=96.8GB, mem=77.5GB\n"}
,{"stream_name":"stdout","time":13301.555901983,"data":"    micro-batch 7: 4 seqs, max_len=6680, total_len=13779, wall=6.4s, peak=96.8GB, mem=77.6GB\n"}
,{"stream_name":"stdout","time":13301.618840873,"data":"  step 253/254: loss:mean=0.044592, grad_norm=0.0478, lr=2.76e-06\n"}
,{"stream_name":"stdout","time":13305.881602579,"data":"    micro-batch 0: 4 seqs, max_len=3540, total_len=8857, wall=4.1s, peak=96.8GB, mem=77.5GB\n"}
,{"stream_name":"stdout","time":13312.736202505,"data":"    micro-batch 1: 4 seqs, max_len=7226, total_len=17644, wall=6.9s, peak=96.8GB, mem=77.7GB\n"}
,{"stream_name":"stdout","time":13318.622897619,"data":"    micro-batch 2: 4 seqs, max_len=5922, total_len=13160, wall=5.9s, peak=96.8GB, mem=77.6GB\n"}
,{"stream_name":"stdout","time":13325.323929096,"data":"    micro-batch 3: 4 seqs, max_len=7043, total_len=17625, wall=6.7s, peak=96.8GB, mem=77.6GB\n"}
,{"stream_name":"stdout","time":13331.11430356,"data":"    micro-batch 4: 4 seqs, max_len=5792, total_len=11457, wall=5.8s, peak=96.8GB, mem=77.6GB\n"}
,{"stream_name":"stdout","time":13337.222000542,"data":"    micro-batch 5: 4 seqs, max_len=6152, total_len=13330, wall=6.1s, peak=96.8GB, mem=77.6GB\n"}
,{"stream_name":"stdout","time":13343.81496728,"data":"    micro-batch 6: 4 seqs, max_len=6934, total_len=16804, wall=6.6s, peak=96.8GB, mem=77.6GB\n"}
,{"stream_name":"stdout","time":13349.430554326,"data":"    micro-batch 7: 4 seqs, max_len=5554, total_len=11913, wall=5.6s, peak=96.8GB, mem=77.6GB\n"}
,{"stream_name":"stdout","time":13349.538754025,"data":"  step 254/254: loss:mean=0.001356, grad_norm=0.0211, lr=1.38e-06\n"}
,{"stream_name":"stdout","time":13349.740299683,"data":"\n"}
,{"stream_name":"stdout","time":13349.740306433,"data":"Training complete. Peak VRAM: 96.8 GB\n"}
,{"stream_name":"stderr","time":13349.946257242,"data":"/usr/local/lib/python3.12/dist-packages/peft/utils/save_and_load.py:279: UserWarning: Setting `save_embedding_layers` to `True` as embedding layers found in `target_modules`.\n"}
,{"stream_name":"stderr","time":13349.946267572,"data":"  warnings.warn(\"Setting `save_embedding_layers` to `True` as embedding layers found in `target_modules`.\")\n"}
,{"stream_name":"stderr","time":13349.946275732,"data":"\n"}
,{"stream_name":"stderr","time":13349.946276982,"data":"/usr/local/lib/python3.12/dist-packages/peft/utils/save_and_load.py:279: UserWarning: Setting `save_embedding_layers` to `True` as embedding layers found in `target_modules`.\n"}
,{"stream_name":"stderr","time":13349.946278072,"data":"  warnings.warn(\"Setting `save_embedding_layers` to `True` as embedding layers found in `target_modules`.\")\n"}
,{"stream_name":"stdout","time":13435.843145173,"data":"zip_namelist: ['adapter_config.json', 'adapter_model.safetensors']\n"}
,{"stream_name":"stdout","time":13435.843163793,"data":"submission_zip_size_bytes: 1374496735\n"}
,{"stream_name":"stdout","time":13436.611982917,"data":"submission_zip_sha256: f5dde9e053d7b28b5b4d88eb0881c3d0f118b0361d05e51836fe5c3ce371c1b6\n"}
,{"stream_name":"stdout","time":13436.611996177,"data":"OK: /kaggle/working/submission.zip is ready.\n"}
,{"stream_name":"stdout","time":13436.611998227,"data":"Training complete.\n"}
,{"stream_name":"stderr","time":13441.659860338,"data":"/usr/local/lib/python3.12/dist-packages/mistune.py:435: SyntaxWarning: invalid escape sequence '\\|'\n"}
,{"stream_name":"stderr","time":13441.659877618,"data":"  cells[i][c] = re.sub('\\\\\\\\\\|', '|', cell)\n"}
,{"stream_name":"stderr","time":13441.791371927,"data":"/usr/local/lib/python3.12/dist-packages/nbconvert/filters/filter_links.py:36: SyntaxWarning: invalid escape sequence '\\_'\n"}
,{"stream_name":"stderr","time":13441.791384957,"data":"  text = re.sub(r'_', '\\_', text) # Escape underscores in display text\n"}
,{"stream_name":"stderr","time":13442.179878254,"data":"[NbConvertApp] Converting notebook __notebook__.ipynb to notebook\n"}
,{"stream_name":"stderr","time":13442.453253991,"data":"[NbConvertApp] Writing 351925 bytes to __notebook__.ipynb\n"}
,{"stream_name":"stderr","time":13443.609925952,"data":"[NbConvertApp] Converting notebook __notebook__.ipynb to html\n"}
,{"stream_name":"stderr","time":13444.086282159,"data":"[NbConvertApp] Writing 698926 bytes to __results__.html\n"}
]
```

### muelsyse111/nemotron-s7-category-round-robin

- remote_state: `uploaded_status_unknown`
- status_returncode: `1`
- files_returncode: `0`
- logs_returncode: `1`

```text
500 Server Error: Internal Server Error for url: https://api.kaggle.com/v1/kernels.KernelsApiService/GetKernelSessionStatus
name,size,creationDate
404 Client Error: Not Found for url: https://api.kaggle.com/v1/kernels.KernelsApiService/ListKernelSessionOutput
```

### muelsyse111/nemotron-s7-protected-rehearsal

- remote_state: `uploaded_status_unknown`
- status_returncode: `1`
- files_returncode: `0`
- logs_returncode: `1`

```text
500 Server Error: Internal Server Error for url: https://api.kaggle.com/v1/kernels.KernelsApiService/GetKernelSessionStatus
name,size,creationDate
404 Client Error: Not Found for url: https://api.kaggle.com/v1/kernels.KernelsApiService/ListKernelSessionOutput
```

### muelsyse111/nemotron-s7-weak-protected-curriculum

- remote_state: `uploaded_status_unknown`
- status_returncode: `1`
- files_returncode: `0`
- logs_returncode: `1`

```text
500 Server Error: Internal Server Error for url: https://api.kaggle.com/v1/kernels.KernelsApiService/GetKernelSessionStatus
name,size,creationDate
404 Client Error: Not Found for url: https://api.kaggle.com/v1/kernels.KernelsApiService/ListKernelSessionOutput
```

### muelsyse111/nemotron-s7-answer-tail-objective

- remote_state: `uploaded_status_unknown`
- status_returncode: `1`
- files_returncode: `0`
- logs_returncode: `1`

```text
500 Server Error: Internal Server Error for url: https://api.kaggle.com/v1/kernels.KernelsApiService/GetKernelSessionStatus
name,size,creationDate
404 Client Error: Not Found for url: https://api.kaggle.com/v1/kernels.KernelsApiService/ListKernelSessionOutput
```

### muelsyse111/nemotron-s7-length-stratified-curriculum

- remote_state: `uploaded_status_unknown`
- status_returncode: `1`
- files_returncode: `0`
- logs_returncode: `1`

```text
500 Server Error: Internal Server Error for url: https://api.kaggle.com/v1/kernels.KernelsApiService/GetKernelSessionStatus
name,size,creationDate
404 Client Error: Not Found for url: https://api.kaggle.com/v1/kernels.KernelsApiService/ListKernelSessionOutput
```

### muelsyse111/nemotron-s7-mamba-inproj-specialist

- remote_state: `uploaded_status_unknown`
- status_returncode: `1`
- files_returncode: `0`
- logs_returncode: `1`

```text
500 Server Error: Internal Server Error for url: https://api.kaggle.com/v1/kernels.KernelsApiService/GetKernelSessionStatus
name,size,creationDate
404 Client Error: Not Found for url: https://api.kaggle.com/v1/kernels.KernelsApiService/ListKernelSessionOutput
```

### muelsyse111/nemotron-s7-muon-full-training

- remote_state: `uploaded_status_unknown`
- status_returncode: `1`
- files_returncode: `0`
- logs_returncode: `1`

```text
500 Server Error: Internal Server Error for url: https://api.kaggle.com/v1/kernels.KernelsApiService/GetKernelSessionStatus
name,size,creationDate
404 Client Error: Not Found for url: https://api.kaggle.com/v1/kernels.KernelsApiService/ListKernelSessionOutput
```

### muelsyse111/nemotron-s7-ties-sign-merge

- remote_state: `output_ready`
- status_returncode: `1`
- files_returncode: `0`
- logs_returncode: `0`

```text
500 Server Error: Internal Server Error for url: https://api.kaggle.com/v1/kernels.KernelsApiService/GetKernelSessionStatus
name,size,creationDate

adapter_config.json,940,"3:39 pm, Saturday 6 June 2026 UTC"

adapter_model.safetensors,968,"3:39 pm, Saturday 6 June 2026 UTC"

nemotron-s7-ties-sign-merge_report.json,928,"3:39 pm, Saturday 6 June 2026 UTC"

submission.zip,851,"3:39 pm, Saturday 6 June 2026 UTC"
5500 / 12010\n"}
,{"stream_name":"stdout","time":193.670339307,"data":"merged_tensors: 5750 / 12010\n"}
,{"stream_name":"stdout","time":195.593902979,"data":"merged_tensors: 6000 / 12010\n"}
,{"stream_name":"stdout","time":197.541495308,"data":"merged_tensors: 6250 / 12010\n"}
,{"stream_name":"stdout","time":199.6764503,"data":"merged_tensors: 6500 / 12010\n"}
,{"stream_name":"stdout","time":201.642337573,"data":"merged_tensors: 6750 / 12010\n"}
,{"stream_name":"stdout","time":203.783007984,"data":"merged_tensors: 7000 / 12010\n"}
,{"stream_name":"stdout","time":205.774675326,"data":"merged_tensors: 7250 / 12010\n"}
,{"stream_name":"stdout","time":207.944011513,"data":"merged_tensors: 7500 / 12010\n"}
,{"stream_name":"stdout","time":209.879240013,"data":"merged_tensors: 7750 / 12010\n"}
,{"stream_name":"stdout","time":212.130553085,"data":"merged_tensors: 8000 / 12010\n"}
,{"stream_name":"stdout","time":214.075722892,"data":"merged_tensors: 8250 / 12010\n"}
,{"stream_name":"stdout","time":216.265040804,"data":"merged_tensors: 8500 / 12010\n"}
,{"stream_name":"stdout","time":218.308127089,"data":"merged_tensors: 8750 / 12010\n"}
,{"stream_name":"stdout","time":220.51212594,"data":"merged_tensors: 9000 / 12010\n"}
,{"stream_name":"stdout","time":222.55191539,"data":"merged_tensors: 9250 / 12010\n"}
,{"stream_name":"stdout","time":224.652965742,"data":"merged_tensors: 9500 / 12010\n"}
,{"stream_name":"stdout","time":226.667069324,"data":"merged_tensors: 9750 / 12010\n"}
,{"stream_name":"stdout","time":228.74851732,"data":"merged_tensors: 10000 / 12010\n"}
,{"stream_name":"stdout","time":230.700126471,"data":"merged_tensors: 10250 / 12010\n"}
,{"stream_name":"stdout","time":232.955791325,"data":"merged_tensors: 10500 / 12010\n"}
,{"stream_name":"stdout","time":234.883425191,"data":"merged_tensors: 10750 / 12010\n"}
,{"stream_name":"stdout","time":236.912980387,"data":"merged_tensors: 11000 / 12010\n"}
,{"stream_name":"stdout","time":238.883856394,"data":"merged_tensors: 11250 / 12010\n"}
,{"stream_name":"stdout","time":241.010155514,"data":"merged_tensors: 11500 / 12010\n"}
,{"stream_name":"stdout","time":242.98441696,"data":"merged_tensors: 11750 / 12010\n"}
,{"stream_name":"stdout","time":244.925921958,"data":"merged_tensors: 12000 / 12010\n"}
,{"stream_name":"stdout","time":314.892033038,"data":"{\n"}
,{"stream_name":"stdout","time":314.892086933,"data":"  \"candidate\": \"nemotron-s7-ties-sign-merge\",\n"}
,{"stream_name":"stdout","time":314.892095005,"data":"  \"method\": \"ties\",\n"}
,{"stream_name":"stdout","time":314.892110314,"data":"  \"source_adapters\": [\n"}
,{"stream_name":"stdout","time":314.892116547,"data":"    \"public_hk_to_kn_lm_head_lam1p0\",\n"}
,{"stream_name":"stdout","time":314.892123778,"data":"    \"public_kn_to_hk_lm_head_lam1p0\",\n"}
,{"stream_name":"stdout","time":314.892130145,"data":"    \"public_hk_to_kn_mamba_lam1p0\"\n"}
,{"stream_name":"stdout","time":314.892135184,"data":"  ],\n"}
,{"stream_name":"stdout","time":314.8921405,"data":"  \"adapter_model_sha256\": \"06f856c03cf49750ebab9bc7ca8e53157ca9dbadae7c14454bf09c19793b5d11\",\n"}
,{"stream_name":"stdout","time":314.892147163,"data":"  \"submission_zip_sha256\": \"b03e975ea48dd04a262f9c05b039a4a52fe00222401cb3d3484fd21c27b6b1b6\",\n"}
,{"stream_name":"stdout","time":314.892153272,"data":"  \"submission_zip_size_bytes\": 3554385847,\n"}
,{"stream_name":"stdout","time":314.892158772,"data":"  \"zip_namelist\": [\n"}
,{"stream_name":"stdout","time":314.892164047,"data":"    \"adapter_config.json\",\n"}
,{"stream_name":"stdout","time":314.892169544,"data":"    \"adapter_model.safetensors\"\n"}
,{"stream_name":"stdout","time":314.892175452,"data":"  ],\n"}
,{"stream_name":"stdout","time":314.892194045,"data":"  \"rank_lte_32\": true\n"}
,{"stream_name":"stdout","time":314.892199506,"data":"}\n"}
,{"stream_name":"stdout","time":314.892203598,"data":"OK: /kaggle/working/submission.zip is ready.\n"}
,{"stream_name":"stderr","time":319.536318016,"data":"/usr/local/lib/python3.12/dist-packages/mistune.py:435: SyntaxWarning: invalid escape sequence '\\|'\n"}
,{"stream_name":"stderr","time":319.536371877,"data":"  cells[i][c] = re.sub('\\\\\\\\\\|', '|', cell)\n"}
,{"stream_name":"stderr","time":319.74607727,"data":"/usr/local/lib/python3.12/dist-packages/nbconvert/filters/filter_links.py:36: SyntaxWarning: invalid escape sequence '\\_'\n"}
,{"stream_name":"stderr","time":319.746121617,"data":"  text = re.sub(r'_', '\\_', text) # Escape underscores in display text\n"}
,{"stream_name":"stderr","time":320.610398965,"data":"[NbConvertApp] Converting notebook __notebook__.ipynb to notebook\n"}
,{"stream_name":"stderr","time":321.058052463,"data":"[NbConvertApp] Writing 12696 bytes to __notebook__.ipynb\n"}
,{"stream_name":"stderr","time":324.235457206,"data":"[NbConvertApp] Converting notebook __notebook__.ipynb to html\n"}
,{"stream_name":"stderr","time":325.307914907,"data":"[NbConvertApp] Writing 309911 bytes to __results__.html\n"}
]
```

### muelsyse111/nemotron-s7-dare-merge

- remote_state: `output_ready`
- status_returncode: `1`
- files_returncode: `0`
- logs_returncode: `0`

```text
500 Server Error: Internal Server Error for url: https://api.kaggle.com/v1/kernels.KernelsApiService/GetKernelSessionStatus
name,size,creationDate

adapter_config.json,930,"3:39 pm, Saturday 6 June 2026 UTC"

adapter_model.safetensors,958,"3:39 pm, Saturday 6 June 2026 UTC"

nemotron-s7-dare-merge_report.json,913,"3:39 pm, Saturday 6 June 2026 UTC"

submission.zip,851,"3:39 pm, Saturday 6 June 2026 UTC"
5500 / 12010\n"}
,{"stream_name":"stdout","time":148.66160599,"data":"merged_tensors: 5750 / 12010\n"}
,{"stream_name":"stdout","time":149.361753056,"data":"merged_tensors: 6000 / 12010\n"}
,{"stream_name":"stdout","time":150.069595531,"data":"merged_tensors: 6250 / 12010\n"}
,{"stream_name":"stdout","time":150.874658905,"data":"merged_tensors: 6500 / 12010\n"}
,{"stream_name":"stdout","time":151.595802508,"data":"merged_tensors: 6750 / 12010\n"}
,{"stream_name":"stdout","time":152.334074173,"data":"merged_tensors: 7000 / 12010\n"}
,{"stream_name":"stdout","time":153.040737019,"data":"merged_tensors: 7250 / 12010\n"}
,{"stream_name":"stdout","time":153.769715551,"data":"merged_tensors: 7500 / 12010\n"}
,{"stream_name":"stdout","time":154.453189619,"data":"merged_tensors: 7750 / 12010\n"}
,{"stream_name":"stdout","time":155.248159803,"data":"merged_tensors: 8000 / 12010\n"}
,{"stream_name":"stdout","time":155.960006471,"data":"merged_tensors: 8250 / 12010\n"}
,{"stream_name":"stdout","time":156.817969001,"data":"merged_tensors: 8500 / 12010\n"}
,{"stream_name":"stdout","time":157.49838259,"data":"merged_tensors: 8750 / 12010\n"}
,{"stream_name":"stdout","time":158.240661237,"data":"merged_tensors: 9000 / 12010\n"}
,{"stream_name":"stdout","time":158.927795281,"data":"merged_tensors: 9250 / 12010\n"}
,{"stream_name":"stdout","time":159.742732112,"data":"merged_tensors: 9500 / 12010\n"}
,{"stream_name":"stdout","time":160.448003991,"data":"merged_tensors: 9750 / 12010\n"}
,{"stream_name":"stdout","time":161.294683463,"data":"merged_tensors: 10000 / 12010\n"}
,{"stream_name":"stdout","time":162.049130162,"data":"merged_tensors: 10250 / 12010\n"}
,{"stream_name":"stdout","time":162.872397675,"data":"merged_tensors: 10500 / 12010\n"}
,{"stream_name":"stdout","time":163.606453333,"data":"merged_tensors: 10750 / 12010\n"}
,{"stream_name":"stdout","time":164.407530369,"data":"merged_tensors: 11000 / 12010\n"}
,{"stream_name":"stdout","time":165.168126484,"data":"merged_tensors: 11250 / 12010\n"}
,{"stream_name":"stdout","time":166.074601314,"data":"merged_tensors: 11500 / 12010\n"}
,{"stream_name":"stdout","time":166.787399382,"data":"merged_tensors: 11750 / 12010\n"}
,{"stream_name":"stdout","time":167.511424429,"data":"merged_tensors: 12000 / 12010\n"}
,{"stream_name":"stdout","time":207.244361301,"data":"{\n"}
,{"stream_name":"stdout","time":207.244401171,"data":"  \"candidate\": \"nemotron-s7-dare-merge\",\n"}
,{"stream_name":"stdout","time":207.244408464,"data":"  \"method\": \"dare\",\n"}
,{"stream_name":"stdout","time":207.244414013,"data":"  \"source_adapters\": [\n"}
,{"stream_name":"stdout","time":207.244419272,"data":"    \"public_hk_to_kn_lm_head_lam1p0\",\n"}
,{"stream_name":"stdout","time":207.244424462,"data":"    \"public_kn_to_hk_lm_head_lam1p0\",\n"}
,{"stream_name":"stdout","time":207.244429574,"data":"    \"public_hk_to_kn_mamba_lam1p0\"\n"}
,{"stream_name":"stdout","time":207.244435053,"data":"  ],\n"}
,{"stream_name":"stdout","time":207.244438336,"data":"  \"adapter_model_sha256\": \"a5d9ffc9263058fb393a8625a7dcce4c3b142d9cb253011573a2c88ee16f0e0d\",\n"}
,{"stream_name":"stdout","time":207.244441889,"data":"  \"submission_zip_sha256\": \"4f37c3377e93633f851ae2a57446c8a22edbb787b12722a4460095e6a47e3a42\",\n"}
,{"stream_name":"stdout","time":207.244445607,"data":"  \"submission_zip_size_bytes\": 3554385847,\n"}
,{"stream_name":"stdout","time":207.24444903,"data":"  \"zip_namelist\": [\n"}
,{"stream_name":"stdout","time":207.244452363,"data":"    \"adapter_config.json\",\n"}
,{"stream_name":"stdout","time":207.244455665,"data":"    \"adapter_model.safetensors\"\n"}
,{"stream_name":"stdout","time":207.244458809,"data":"  ],\n"}
,{"stream_name":"stdout","time":207.244470093,"data":"  \"rank_lte_32\": true\n"}
,{"stream_name":"stdout","time":207.244472912,"data":"}\n"}
,{"stream_name":"stdout","time":207.244475321,"data":"OK: /kaggle/working/submission.zip is ready.\n"}
,{"stream_name":"stderr","time":211.723292236,"data":"/usr/local/lib/python3.12/dist-packages/mistune.py:435: SyntaxWarning: invalid escape sequence '\\|'\n"}
,{"stream_name":"stderr","time":211.723333372,"data":"  cells[i][c] = re.sub('\\\\\\\\\\|', '|', cell)\n"}
,{"stream_name":"stderr","time":211.955604959,"data":"/usr/local/lib/python3.12/dist-packages/nbconvert/filters/filter_links.py:36: SyntaxWarning: invalid escape sequence '\\_'\n"}
,{"stream_name":"stderr","time":211.95563453,"data":"  text = re.sub(r'_', '\\_', text) # Escape underscores in display text\n"}
,{"stream_name":"stderr","time":212.781386755,"data":"[NbConvertApp] Converting notebook __notebook__.ipynb to notebook\n"}
,{"stream_name":"stderr","time":213.169691236,"data":"[NbConvertApp] Writing 12664 bytes to __notebook__.ipynb\n"}
,{"stream_name":"stderr","time":216.270288782,"data":"[NbConvertApp] Converting notebook __notebook__.ipynb to html\n"}
,{"stream_name":"stderr","time":217.337260587,"data":"[NbConvertApp] Writing 309870 bytes to __results__.html\n"}
]
```

### muelsyse111/nemotron-s7-layerwise-adapter-soup

- remote_state: `output_ready`
- status_returncode: `1`
- files_returncode: `0`
- logs_returncode: `0`

```text
500 Server Error: Internal Server Error for url: https://api.kaggle.com/v1/kernels.KernelsApiService/GetKernelSessionStatus
name,size,creationDate

adapter_config.json,960,"3:39 pm, Saturday 6 June 2026 UTC"

adapter_model.safetensors,988,"3:39 pm, Saturday 6 June 2026 UTC"

nemotron-s7-layerwise-soup_report.json,947,"3:39 pm, Saturday 6 June 2026 UTC"

submission.zip,873,"3:39 pm, Saturday 6 June 2026 UTC"
2010\n"}
,{"stream_name":"stdout","time":144.110252954,"data":"merged_tensors: 5750 / 12010\n"}
,{"stream_name":"stdout","time":144.537529494,"data":"merged_tensors: 6000 / 12010\n"}
,{"stream_name":"stdout","time":144.942079933,"data":"merged_tensors: 6250 / 12010\n"}
,{"stream_name":"stdout","time":145.414698697,"data":"merged_tensors: 6500 / 12010\n"}
,{"stream_name":"stdout","time":145.816613586,"data":"merged_tensors: 6750 / 12010\n"}
,{"stream_name":"stdout","time":146.254715208,"data":"merged_tensors: 7000 / 12010\n"}
,{"stream_name":"stdout","time":146.664088846,"data":"merged_tensors: 7250 / 12010\n"}
,{"stream_name":"stdout","time":147.131259326,"data":"merged_tensors: 7500 / 12010\n"}
,{"stream_name":"stdout","time":147.566522206,"data":"merged_tensors: 7750 / 12010\n"}
,{"stream_name":"stdout","time":148.044709139,"data":"merged_tensors: 8000 / 12010\n"}
,{"stream_name":"stdout","time":148.480554146,"data":"merged_tensors: 8250 / 12010\n"}
,{"stream_name":"stdout","time":148.94460059,"data":"merged_tensors: 8500 / 12010\n"}
,{"stream_name":"stdout","time":149.37519144,"data":"merged_tensors: 8750 / 12010\n"}
,{"stream_name":"stdout","time":149.817928394,"data":"merged_tensors: 9000 / 12010\n"}
,{"stream_name":"stdout","time":150.207976133,"data":"merged_tensors: 9250 / 12010\n"}
,{"stream_name":"stdout","time":150.681599958,"data":"merged_tensors: 9500 / 12010\n"}
,{"stream_name":"stdout","time":151.142623284,"data":"merged_tensors: 9750 / 12010\n"}
,{"stream_name":"stdout","time":151.606981896,"data":"merged_tensors: 10000 / 12010\n"}
,{"stream_name":"stdout","time":152.029644335,"data":"merged_tensors: 10250 / 12010\n"}
,{"stream_name":"stdout","time":152.506874401,"data":"merged_tensors: 10500 / 12010\n"}
,{"stream_name":"stdout","time":153.02753461,"data":"merged_tensors: 10750 / 12010\n"}
,{"stream_name":"stdout","time":153.594461775,"data":"merged_tensors: 11000 / 12010\n"}
,{"stream_name":"stdout","time":154.169743657,"data":"merged_tensors: 11250 / 12010\n"}
,{"stream_name":"stdout","time":154.772693802,"data":"merged_tensors: 11500 / 12010\n"}
,{"stream_name":"stdout","time":155.360051639,"data":"merged_tensors: 11750 / 12010\n"}
,{"stream_name":"stdout","time":155.941445409,"data":"merged_tensors: 12000 / 12010\n"}
,{"stream_name":"stdout","time":227.770090634,"data":"{\n"}
,{"stream_name":"stdout","time":227.770167345,"data":"  \"candidate\": \"nemotron-s7-layerwise-soup\",\n"}
,{"stream_name":"stdout","time":227.770173573,"data":"  \"method\": \"layerwise\",\n"}
,{"stream_name":"stdout","time":227.770177118,"data":"  \"source_adapters\": [\n"}
,{"stream_name":"stdout","time":227.770180438,"data":"    \"public_hk_to_kn_lm_head_lam1p0\",\n"}
,{"stream_name":"stdout","time":227.770183834,"data":"    \"public_kn_to_hk_lm_head_lam1p0\",\n"}
,{"stream_name":"stdout","time":227.77018717,"data":"    \"public_hk_to_kn_mamba_lam1p0\"\n"}
,{"stream_name":"stdout","time":227.770196736,"data":"  ],\n"}
,{"stream_name":"stdout","time":227.770199934,"data":"  \"adapter_model_sha256\": \"01eb5f689a6601c5a9d4cb2b86467148bce8291782c6370207f64cbcd02f63e8\",\n"}
,{"stream_name":"stdout","time":227.770203615,"data":"  \"submission_zip_sha256\": \"4480e232def317221bf967b490aa196309aa506735edc7ce5651019929ba4084\",\n"}
,{"stream_name":"stdout","time":227.770207241,"data":"  \"submission_zip_size_bytes\": 3554385847,\n"}
,{"stream_name":"stdout","time":227.770210678,"data":"  \"zip_namelist\": [\n"}
,{"stream_name":"stdout","time":227.770214051,"data":"    \"adapter_config.json\",\n"}
,{"stream_name":"stdout","time":227.77021721,"data":"    \"adapter_model.safetensors\"\n"}
,{"stream_name":"stdout","time":227.770220477,"data":"  ],\n"}
,{"stream_name":"stdout","time":227.770235083,"data":"  \"rank_lte_32\": true\n"}
,{"stream_name":"stdout","time":227.770237763,"data":"}\n"}
,{"stream_name":"stdout","time":227.770240397,"data":"OK: /kaggle/working/submission.zip is ready.\n"}
,{"stream_name":"stderr","time":232.215120392,"data":"/usr/local/lib/python3.12/dist-packages/mistune.py:435: SyntaxWarning: invalid escape sequence '\\|'\n"}
,{"stream_name":"stderr","time":232.215162128,"data":"  cells[i][c] = re.sub('\\\\\\\\\\|', '|', cell)\n"}
,{"stream_name":"stderr","time":232.441952658,"data":"/usr/local/lib/python3.12/dist-packages/nbconvert/filters/filter_links.py:36: SyntaxWarning: invalid escape sequence '\\_'\n"}
,{"stream_name":"stderr","time":232.441981347,"data":"  text = re.sub(r'_', '\\_', text) # Escape underscores in display text\n"}
,{"stream_name":"stderr","time":233.298346787,"data":"[NbConvertApp] Converting notebook __notebook__.ipynb to notebook\n"}
,{"stream_name":"stderr","time":233.698945606,"data":"[NbConvertApp] Writing 12725 bytes to __notebook__.ipynb\n"}
,{"stream_name":"stderr","time":236.915013133,"data":"[NbConvertApp] Converting notebook __notebook__.ipynb to html\n"}
,{"stream_name":"stderr","time":238.050464447,"data":"[NbConvertApp] Writing 309954 bytes to __results__.html\n"}
]
```
