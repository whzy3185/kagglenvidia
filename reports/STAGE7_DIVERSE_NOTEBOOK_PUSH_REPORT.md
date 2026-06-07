# Stage 7 Diverse Notebook Push Report

- original_attempt_at: 2026-06-06T23:39:43
- reconciled_at: 2026-06-07T03:30:00
- expected_candidates: 11
- push_attempted: 11
- kernel_runs_started: 4
- notebooks_created_but_run_blocked: 7
- competition_submission_executed: false

The original CLI process returned exit code 0 even when stdout contained
`Kernel push error: Maximum batch GPU session count of 2 reached`. The table
below is reconciled from stdout, not from the process return code.

| kernel | run started | created but GPU-blocked | CLI return code |
|---|---:|---:|---:|
| `muelsyse111/nemotron-s7-seed-stability-replay` | true | false | 0 |
| `muelsyse111/nemotron-s7-category-round-robin` | false | true | 0 |
| `muelsyse111/nemotron-s7-protected-rehearsal` | false | true | 0 |
| `muelsyse111/nemotron-s7-weak-protected-curriculum` | false | true | 0 |
| `muelsyse111/nemotron-s7-answer-tail-objective` | false | true | 0 |
| `muelsyse111/nemotron-s7-length-stratified-curriculum` | false | true | 0 |
| `muelsyse111/nemotron-s7-mamba-inproj-specialist` | false | true | 0 |
| `muelsyse111/nemotron-s7-muon-full-training` | false | true | 0 |
| `muelsyse111/nemotron-s7-ties-sign-merge` | true | false | 0 |
| `muelsyse111/nemotron-s7-dare-merge` | true | false | 0 |
| `muelsyse111/nemotron-s7-layerwise-adapter-soup` | true | false | 0 |

## Command Output

### muelsyse111/nemotron-s7-seed-stability-replay

```text
Kernel version 1 successfully pushed.  Please check progress at https://www.kaggle.com/code/muelsyse111/nemotron-s7-seed-stability-replay
(no stderr)
```

### muelsyse111/nemotron-s7-category-roundrobin

```text
Your kernel title does not resolve to the specified id. This may result in surprising behavior. We suggest making your title something that resolves to the specified id. See https://en.wikipedia.org/wiki/Clean_URL#Slug for more information on how slugs are determined.
Kernel push error: Maximum batch GPU session count of 2 reached.
(no stderr)
```

### muelsyse111/nemotron-s7-protected-rehearsal

```text
Kernel push error: Maximum batch GPU session count of 2 reached.
(no stderr)
```

### muelsyse111/nemotron-s7-weak-protected-curriculum

```text
Kernel push error: Maximum batch GPU session count of 2 reached.
(no stderr)
```

### muelsyse111/nemotron-s7-answer-tail-objective

```text
Kernel push error: Maximum batch GPU session count of 2 reached.
(no stderr)
```

### muelsyse111/nemotron-s7-length-stratified

```text
Your kernel title does not resolve to the specified id. This may result in surprising behavior. We suggest making your title something that resolves to the specified id. See https://en.wikipedia.org/wiki/Clean_URL#Slug for more information on how slugs are determined.
Kernel push error: Maximum batch GPU session count of 2 reached.
(no stderr)
```

### muelsyse111/nemotron-s7-mamba-inproj-specialist

```text
Kernel push error: Maximum batch GPU session count of 2 reached.
(no stderr)
```

### muelsyse111/nemotron-s7-muon-full

```text
Your kernel title does not resolve to the specified id. This may result in surprising behavior. We suggest making your title something that resolves to the specified id. See https://en.wikipedia.org/wiki/Clean_URL#Slug for more information on how slugs are determined.
Kernel push error: Maximum batch GPU session count of 2 reached.
(no stderr)
```

### muelsyse111/nemotron-s7-ties-sign-merge

```text
Kernel version 1 successfully pushed.  Please check progress at https://www.kaggle.com/code/muelsyse111/nemotron-s7-ties-sign-merge
(no stderr)
```

### muelsyse111/nemotron-s7-dare-merge

```text
Kernel version 1 successfully pushed.  Please check progress at https://www.kaggle.com/code/muelsyse111/nemotron-s7-dare-merge
(no stderr)
```

### muelsyse111/nemotron-s7-layerwise-soup

```text
Your kernel title does not resolve to the specified id. This may result in surprising behavior. We suggest making your title something that resolves to the specified id. See https://en.wikipedia.org/wiki/Clean_URL#Slug for more information on how slugs are determined.
Kernel version 1 successfully pushed.  Please check progress at https://www.kaggle.com/code/muelsyse111/nemotron-s7-layerwise-adapter-soup
(no stderr)
```

## Safety

This script only calls `kaggle kernels push`. It never calls `kaggle competitions submit` and does not consume competition submission quota.
