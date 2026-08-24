# agent-harness-evals

Unified, continuously-updated evaluation data across **models**, **agent harnesses**, and **tools** — one schema, live sources.

Not another benchmark. This is an aggregation and reconciliation layer over benchmarks that already exist: it fetches live leaderboard data, normalizes model / scaffold / score semantics into one record schema, and produces views no single leaderboard offers — starting with the **model × harness matrix** (same model, different harness).

## Why

- Model leaderboards (SWE-bench, BFCL, ...) hide the harness. Harness leaderboards (Terminal-Bench) exist for one domain. Cross-layer corpora (Messier, HAL) are one-off snapshots.
- The same model scores 20+ points apart under different harnesses on Terminal-Bench. That variable deserves its own axis, permanently, from live data.

## Data flow

```
fetch.py      pull upstream dumps        (Epoch Benchmarking Hub, ~daily, CC-BY)
normalize.py  -> data/clean/records.parquet   one row = (benchmark, model, scaffold, score)
views_*.py    -> views/                  model x harness matrices, per benchmark
```

Run:

```bash
pip install requests pandas pyarrow tabulate
python src/fetch.py && python src/normalize.py && python src/views_harness.py
```

## Record schema

Follows the reconciliation model of [Messier](https://arxiv.org/abs/2607.25891) (model, scaffold, environment, task, verifier), collapsed to benchmark-level granularity for live sources that publish only aggregates.

| field | meaning |
|---|---|
| `benchmark` | canonical benchmark id |
| `model` / `model_raw` | canonical id (release-config suffix stripped) / original |
| `scaffold` | agent harness; `""` = provider-default |
| `score`, `score_unit` | primary metric; `rate` = 0-1 comparable, `raw` = source units |
| `source`, `source_link` | provenance |

## Sources

| source | layer | cadence | status |
|---|---|---|---|
| [Epoch Benchmarking Hub](https://epoch.ai/benchmarks) | models + harnesses (75 benchmarks, incl. Terminal-Bench agent×model) | ~daily | live |
| [Messier corpus](https://arxiv.org/abs/2607.25891) | historical task/verifier-level backfill (960k trials) | snapshot | planned |
| SWE-bench / BFCL official | per-benchmark cross-check | on release | planned |

Epoch data is CC-BY (credit: Epoch AI). Tool-layer comparisons (tool A vs tool B under a fixed agent) have no public data source and are out of scope until one exists.
