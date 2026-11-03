# hal_scienceagentbench: same model, different harness

Best score per (model, harness) pair. `spread` = max−min across harnesses for that model; `n` = harnesses measured. Spread with `n=2` is a single pairwise difference — read with care.

**no model has ≥3 harnesses yet.**

| model             |   HAL Generalist Agent |   SAB Self-Debug |   spread |   n |
|:------------------|-----------------------:|-----------------:|---------:|----:|
| o3                |                  0.098 |            0.333 |    0.235 |   2 |
| claude-3.7-sonnet |                  0.176 |            0.304 |    0.127 |   2 |
| o4-mini           |                  0.216 |            0.274 |    0.059 |   2 |
| gpt-4.1           |                  0.069 |            0.245 |    0.176 |   2 |
| deepseek-v3       |                  0.01  |            0.157 |    0.147 |   2 |
