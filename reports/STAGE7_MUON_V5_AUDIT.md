# Stage 7 Muon v5 Audit

- source kernel: `muelsyse111/nemotron-s7-muon-full-training-v5`
- audit kernel: `muelsyse111/nemotron-s7-muon-v5-audit`
- source training: 7830 records, one epoch, effective batch 16
- GPU required for audit: false
- base model loaded: false
- competition submission executed: false
- latest verified kernel version: 2
- source and output SHA256: `2d42d0adb258956398e4a501f4629aa4a812da2612e506cf1f0449b6143170f5`
- source and output size: 3833093217 bytes
- LoRA rank: 32
- safetensors tensor count: 12011
- exact zip root: `adapter_config.json`, `adapter_model.safetensors`

The source training output only printed its package size and success marker.
This audit mounts that output, verifies the exact two-file root, rank, target
modules, safetensors header, size and SHA256, then copies the validated source
package unchanged to avoid increasing its compressed size.
