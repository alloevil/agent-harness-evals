# hal_swebench_verified_mini: same model, different harness

Best score per (model, harness) pair. `spread` = max−min across harnesses for that model; `n` = harnesses measured. Spread with `n=2` is a single pairwise difference — read with care.

**median spread 0.320 over 1 models with ≥3 harnesses.**

| model             |   HAL Generalist Agent |   SWE-Agent |   SWE-Agent  Pareto optimal |   HAL Generalist Agent  Pareto optimal |   spread |   n |
|:------------------|-----------------------:|------------:|----------------------------:|---------------------------------------:|---------:|----:|
| claude-sonnet-4.5 |                   0.4  |        0.68 |                        0.72 |                                 nan    |     0.32 |   3 |
| claude-opus-4.1   |                   0.46 |        0.61 |                      nan    |                                 nan    |     0.15 |   2 |
| claude-3.7-sonnet |                   0.26 |        0.54 |                      nan    |                                 nan    |     0.28 |   2 |
| o4-mini           |                   0.06 |        0.54 |                      nan    |                                 nan    |     0.48 |   2 |
| claude-opus-4     |                   0.34 |        0.5  |                      nan    |                                 nan    |     0.16 |   2 |
| gpt-5             |                   0.12 |        0.46 |                      nan    |                                 nan    |     0.34 |   2 |
| o3                |                   0    |        0.46 |                      nan    |                                 nan    |     0.46 |   2 |
| claude-haiku-4.5  |                   0.24 |      nan    |                      nan    |                                   0.44 |     0.2  |   2 |
| gpt-4.1           |                   0.02 |        0.44 |                      nan    |                                 nan    |     0.42 |   2 |
| deepseek-v3       |                   0.1  |        0.24 |                      nan    |                                 nan    |     0.14 |   2 |
| gemini-2.0-flash  |                   0.02 |      nan    |                        0.24 |                                 nan    |     0.22 |   2 |
| deepseek-r1       |                   0.06 |        0    |                      nan    |                                 nan    |     0.06 |   2 |
