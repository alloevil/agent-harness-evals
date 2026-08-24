# hal_scienceagentbench: same model, different harness

Best score per (model, harness) pair. `spread` = max−min across harnesses for that model; `n` = harnesses measured. Spread with `n=2` is a single pairwise difference — read with care.

**median spread 0.059 over 1 models with ≥3 harnesses.**

| model             |   HAL Generalist Agent |   SAB Self-Debug |   SAB Self-Debug  Pareto optimal |   spread |   n |
|:------------------|-----------------------:|-----------------:|---------------------------------:|---------:|----:|
| o3                |                  0.098 |          nan     |                            0.333 |    0.235 |   2 |
| claude-3.7-sonnet |                  0.176 |            0.304 |                          nan     |    0.127 |   2 |
| claude-sonnet-4.5 |                nan     |            0.294 |                            0.304 |    0.01  |   2 |
| o4-mini           |                  0.216 |            0.274 |                            0.274 |    0.059 |   3 |
| gpt-4.1           |                  0.069 |            0.245 |                          nan     |    0.176 |   2 |
| deepseek-v3       |                  0.01  |            0.157 |                          nan     |    0.147 |   2 |
