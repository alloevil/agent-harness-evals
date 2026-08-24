# hal_scicode: same model, different harness

Best score per (model, harness) pair. `spread` = max−min across harnesses for that model; `n` = harnesses measured. Spread with `n=2` is a single pairwise difference — read with care.

**median spread 0.031 over 7 models with ≥3 harnesses.**

| model             |   HAL Generalist Agent |   Scicode Tool Calling Agent |   Scicode Zero Shot Agent |   Scicode Zero Shot Agent  Pareto optimal |   spread |   n |
|:------------------|-----------------------:|-----------------------------:|--------------------------:|------------------------------------------:|---------:|----:|
| o3                |                  0.031 |                        0.092 |                     0.046 |                                   nan     |    0.062 |   3 |
| o4-mini           |                  0.062 |                        0.046 |                     0.062 |                                     0.092 |    0.046 |   4 |
| gpt-4.1           |                  0.015 |                        0.015 |                     0.062 |                                   nan     |    0.046 |   3 |
| claude-3.7-sonnet |                  0.031 |                        0.046 |                     0.031 |                                   nan     |    0.015 |   3 |
| deepseek-v3       |                  0     |                        0     |                     0.031 |                                   nan     |    0.031 |   3 |
| gemini-2.0-flash  |                  0     |                        0.015 |                   nan     |                                     0.015 |    0.015 |   3 |
| deepseek-r1       |                  0     |                        0     |                     0     |                                   nan     |    0     |   3 |
