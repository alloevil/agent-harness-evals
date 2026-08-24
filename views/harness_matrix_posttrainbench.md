# posttrainbench: same model, different harness

Best score per (model, harness) pair. `spread` = max−min across harnesses for that model; `n` = harnesses measured. Spread with `n=2` is a single pairwise difference — read with care.

**no model has ≥3 harnesses yet.**

| model                |   OpenCode |   Claude Code |   Codex CLI |   Gemini CLI |   spread |   n |
|:---------------------|-----------:|--------------:|------------:|-------------:|---------:|----:|
| gpt-5.1-codex-max    |      0.076 |       nan     |       0.197 |      nan     |    0.12  |   2 |
| gemini-3-pro-preview |      0.149 |       nan     |     nan     |        0.181 |    0.033 |   2 |
| claude-opus-4.5      |      0.173 |         0.171 |     nan     |      nan     |    0.002 |   2 |
