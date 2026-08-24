# hal_taubench_airline: same model, different harness

Best score per (model, harness) pair. `spread` = max−min across harnesses for that model; `n` = harnesses measured. Spread with `n=2` is a single pairwise difference — read with care.

**no model has ≥3 harnesses yet.**

| model             |   HAL Generalist Agent |   TAU-bench Tool Calling |   spread |   n |
|:------------------|-----------------------:|-------------------------:|---------:|----:|
| claude-3.7-sonnet |                   0.56 |                     0.52 |     0.04 |   2 |
| o4-mini           |                   0.22 |                     0.56 |     0.34 |   2 |
| claude-opus-4.1   |                   0.54 |                     0.52 |     0.02 |   2 |
| o3                |                   0.2  |                     0.54 |     0.34 |   2 |
| gpt-5             |                   0.3  |                     0.48 |     0.18 |   2 |
| deepseek-v3       |                   0.18 |                     0.44 |     0.26 |   2 |
| deepseek-r1       |                   0.1  |                     0.36 |     0.26 |   2 |
| gpt-4.1           |                   0.16 |                     0.36 |     0.2  |   2 |
| gemini-2.0-flash  |                   0.22 |                     0.28 |     0.06 |   2 |
