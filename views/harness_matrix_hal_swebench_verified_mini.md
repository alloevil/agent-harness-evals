# hal_swebench_verified_mini: same model, different harness

Best score per (model, harness) pair. `spread` = max−min across harnesses for that model; `n` = harnesses measured. Spread with `n=2` is a single pairwise difference — read with care.

**no model has ≥3 harnesses yet.**

| model             |   HAL Generalist Agent |   SWE-Agent |   spread |   n |
|:------------------|-----------------------:|------------:|---------:|----:|
| claude-sonnet-4.5 |                   0.4  |        0.72 |     0.32 |   2 |
| claude-opus-4.1   |                   0.46 |        0.61 |     0.15 |   2 |
| claude-3.7-sonnet |                   0.26 |        0.54 |     0.28 |   2 |
| o4-mini           |                   0.06 |        0.54 |     0.48 |   2 |
| claude-opus-4     |                   0.34 |        0.5  |     0.16 |   2 |
| gpt-5             |                   0.12 |        0.46 |     0.34 |   2 |
| o3                |                   0    |        0.46 |     0.46 |   2 |
| gpt-4.1           |                   0.02 |        0.44 |     0.42 |   2 |
| deepseek-v3       |                   0.1  |        0.24 |     0.14 |   2 |
| gemini-2.0-flash  |                   0.02 |        0.24 |     0.22 |   2 |
| deepseek-r1       |                   0.06 |        0    |     0.06 |   2 |
