# hal_gaia: same model, different harness

Best score per (model, harness) pair. `spread` = max−min across harnesses for that model; `n` = harnesses measured. Spread with `n=2` is a single pairwise difference — read with care.

**median spread 0.436 over 1 models with ≥3 harnesses.**

| model             |   HF Open Deep Research |   HAL Generalist Agent |   HAL Generalist Agent  Pareto optimal |   spread |   n |
|:------------------|------------------------:|-----------------------:|---------------------------------------:|---------:|----:|
| claude-sonnet-4.5 |                   0.309 |                  0.709 |                                  0.745 |    0.436 |   3 |
| claude-opus-4.1   |                   0.285 |                  0.685 |                                nan     |    0.4   |   2 |
| claude-opus-4     |                   0.576 |                  0.648 |                                nan     |    0.073 |   2 |
| claude-3.7-sonnet |                   0.37  |                  0.642 |                                nan     |    0.273 |   2 |
| gpt-5             |                   0.628 |                  0.594 |                                nan     |    0.034 |   2 |
| o4-mini           |                   0.558 |                nan     |                                  0.582 |    0.024 |   2 |
| gpt-4.1           |                   0.503 |                  0.497 |                                nan     |    0.006 |   2 |
| gemini-2.0-flash  |                   0.194 |                nan     |                                  0.327 |    0.133 |   2 |
| o3                |                   0.327 |                  0.285 |                                nan     |    0.042 |   2 |
| deepseek-r1       |                   0.249 |                  0.303 |                                nan     |    0.054 |   2 |
| deepseek-v3       |                   0.285 |                  0.294 |                                nan     |    0.009 |   2 |
