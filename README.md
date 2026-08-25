<p align="center">
  <a href="https://alloevil.github.io/agent-harness-evals/">
    <img src="./assets/readme/hero.svg" width="100%" alt="agent-harness-evals: same model, different harness, different score. Live matrix showing claude-opus-4.6 scoring 0.580 under Claude Code and 0.699 under Droid on terminal-bench — a 0.218 spread controlled by the harness alone.">
  </a>
</p>

<p align="center">
  <a href="https://alloevil.github.io/agent-harness-evals/"><b>Explore the live matrix →</b></a>
</p>

The same model does not get the same score. On terminal-bench, `claude-opus-4.6` passes **58.0%** of tasks under Claude Code and **69.9%** under Droid; `gpt-5.3-codex` moves from **64.7%** (Terminus 2) to **77.3%** (Droid). Median cross-harness spread across 30 models: **11 points** — the same order of magnitude as a model-generation upgrade. Model leaderboards hide this variable. This project gives it an axis.

## What it is

Not another benchmark. An **aggregation and reconciliation layer** over benchmarks that already exist:

1. **Fetch** live leaderboard data (Epoch AI Benchmarking Hub, 75 benchmarks, refreshed ~daily, CC-BY) plus the HAL harness leaderboards.
2. **Normalize** model / scaffold / score semantics into one record schema — `(benchmark, model, scaffold, score)` — with **one model id across sources**: `claude-sonnet-4-5-20250929` (Epoch) and "Claude Sonnet 4.5 High (September 2025)" (HAL) both land on `claude-sonnet-4.5`, so cross-source rows join instead of fragmenting.
3. **Render** views no single leaderboard offers: the **model × harness matrix**, a **harness ranking** (share of each model's best score a harness retains), a **model ranking** (each model's best score and the harness that got it there), and **native-pairing boards** (FrontierSWE, frontiercode) where each model runs in its vendor's own CLI.

Existing cross-layer corpora ([Messier](https://arxiv.org/abs/2607.25891), [HAL](https://github.com/princeton-pli/hal-harness)) are one-off snapshots; live leaderboards are single-layer. This repo is the missing combination: **cross-layer and alive** — a scheduled `fetch → normalize → build` run keeps the page exactly as fresh as the upstream data, with zero evaluation cost.

## Use it

```bash
pip install -r requirements.txt
python src/fetch.py && python src/normalize.py && python src/views_harness.py && python src/snapshot.py && python src/build_site.py && python src/build_trend.py
```

Outputs:

| artifact | content |
|---|---|
| `data/clean/records.parquet` | ~5,500 unified records across 83 benchmarks (grows with upstream) |
| `data/snapshots/*.jsonl` | daily snapshots — history is diffable, powers the trend view |
| `views/harness_matrix_*.{csv,md}` | per-benchmark model × harness matrices |
| `docs/index.html` | the [live site](https://alloevil.github.io/agent-harness-evals/) — matrix, harness ranking, model ranking; self-contained |
| `docs/trend.html` | [score over time](https://alloevil.github.io/agent-harness-evals/trend.html), one line per harness |

## Record schema

Follows the reconciliation model of [Messier](https://arxiv.org/abs/2607.25891) (model, scaffold, environment, task, verifier), collapsed to benchmark granularity for sources that publish only aggregates.

| field | meaning |
|---|---|
| `benchmark` | canonical benchmark id |
| `model` / `model_raw` | canonical id, shared across sources (effort/date suffixes and provider prefixes stripped, `claude-*-4-5` → `claude-*-4.5`) / original |
| `scaffold` | agent harness; `""` = provider-default |
| `score`, `score_unit` | primary metric; `rate` = 0–1 comparable, `raw` = source units |
| `source`, `source_link` | provenance, down to per-run logs where upstream provides them |

## Sources

| source | layer | cadence | status |
|---|---|---|---|
| [Epoch Benchmarking Hub](https://epoch.ai/benchmarks) | models + harnesses (Terminal-Bench, FrontierSWE, frontiercode, posttrainbench, btf3 agent×model boards) | ~daily | live |
| [HAL](https://hal.cs.princeton.edu/) | harness×model×cost across 9 benchmarks (26k rollouts) | snapshot, paused | imported |
| [Messier corpus](https://arxiv.org/abs/2607.25891) | task/verifier-level harness corpus (960k trials, 205 scaffolds, 31 benchmarks) | snapshot | pending release |

## Status & limitations

- **Two harness sources.** Terminal-Bench (via Epoch) is the only *live*, machine-readable harness leaderboard. HAL adds a second, *historical* harness dimension — its leaderboard score tables are public HTML (only the traces are encrypted), covering 9 benchmarks with a different harness set (SWE-Agent, Browser-Use, CORE-Agent, …). SWE-bench pins a single harness (mini-swe-agent), so its official board is a model ranking, not a harness matrix.
- **Scores are aggregates, not trials.** Upstream publishes benchmark-level scores; `spread` is computed from those, with a per-model `n` and `stderr` where reported. n<3 spreads are dimmed.
- **Tool-layer comparisons** (tool A vs tool B under a fixed agent) have no public data source yet and are out of scope until one exists.
- **Messier is not yet downloadable.** The Messier paper (arXiv, still in anonymous review) and its code are public, but the dataset is only referenced as a "companion dataset" — no public download URL exists in the paper or its repo. Importing it is blocked on the paper's de-anonymized release, not on this repo.

## License

Code MIT. Data CC-BY, credit [Epoch AI](https://epoch.ai/benchmarks).
