# Contributing

This repo is an aggregation layer, not a benchmark. Contributions are data sources, name reconciliation rules, and views — all designed to be local changes that never touch the core consolidation logic.

## Add a data source

Each source is a self-contained fetch + normalize step. Follow the Epoch example:

1. **Fetch** (in `src/fetch.py`): add a `fetch_<name>()` that downloads the upstream dump into `data/raw/<name>/`. It must be idempotent and require no manual steps.

2. **Normalize** (in `src/normalize.py`): map the upstream rows into the unified record schema:

   ```
   benchmark, model, model_raw, scaffold, score, score_unit, stderr, org, release_date, source, source_link
   ```

   - `model`: canonical id — strip release-config suffixes (`_unknown`, `_max`, …), keep the base model as the unit.
   - `scaffold`: the agent harness. Empty string = provider-default. This is the field that makes cross-harness comparison possible; do not put step budgets or model names here (see `harness_aliases.yaml`).
   - `score_unit`: `rate` for 0–1 comparable scores, `raw` otherwise. Percent scales (max in (1.5, 100]) are rescaled to 0–1 by `rescale()`.

3. **Reconcile names** (in `src/harness_aliases.yaml`): add exact aliases or regex rules so the same harness spelled differently collapses to one column. Every un-reconciled duplicate inflates the harness count and fragments the matrix — this is the load-bearing step.

4. **Add a test** (in `tests/`): cover the new source's normalization and any alias rules. The data contract is: `rate` scores in [0,1], no empty model ids, `score_unit` in {rate, raw}.

Run the full pipeline locally before opening a PR:

```bash
pip install -r requirements.txt pytest
python src/fetch.py && python src/normalize.py && python src/views_harness.py && python src/snapshot.py && python src/build_site.py && python src/build_trend.py
python -m pytest tests/ -q
```

## Source quality bar

A source is only accepted if it is:

- **Harness-aware** — it records which agent (scaffold) produced the score, not just the model. A model-only leaderboard (e.g. SWE-bench's default board, which pins mini-swe-agent) does not add to the matrix.
- **Machine-readable** — a CSV/JSON dump or stable API, not a JS-rendered page to scrape.
- **Continuously updated or a labeled historical snapshot** — never a one-off with no date.

If the ecosystem has no second live harness source today, that is a fact to record in the README, not a gap to paper over with a low-value source.

## License

Code MIT; data CC-BY with source attribution.
