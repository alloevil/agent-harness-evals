# hal_online_mind2web: same model, different harness

Best score per (model, harness) pair. `spread` = max−min across harnesses for that model; `n` = harnesses measured. Spread with `n=2` is a single pairwise difference — read with care.

**no model has ≥3 harnesses yet.**

| model             |   Browser-Use |   SeeAct |   SeeAct  Pareto optimal |   Browser-Use  Pareto optimal |   spread |   n |
|:------------------|--------------:|---------:|-------------------------:|------------------------------:|---------:|----:|
| gpt-5             |         0.32  |  nan     |                    0.423 |                        nan    |    0.103 |   2 |
| claude-sonnet-4   |         0.4   |    0.367 |                  nan     |                        nan    |    0.033 |   2 |
| claude-3.7-sonnet |         0.393 |    0.303 |                  nan     |                        nan    |    0.09  |   2 |
| o3                |         0.29  |    0.39  |                  nan     |                        nan    |    0.1   |   2 |
| gpt-4.1           |         0.363 |    0.303 |                  nan     |                        nan    |    0.06  |   2 |
| o4-mini           |         0.2   |    0.32  |                  nan     |                        nan    |    0.12  |   2 |
| gemini-2.0-flash  |       nan     |  nan     |                    0.267 |                          0.29 |    0.023 |   2 |
