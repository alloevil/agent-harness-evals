"""The gate behind docs/claims.json: each figure is recomputed from a committed artifact.

A checker that quietly agrees with whatever is published is worse than no checker, so these
pin the parts of src/claims_check.py that decide a number: which records count, when a board is
cross-harness, and that a model's spread comes from the matrix cells and not from the CSV's own
`spread`/`n` columns.
"""
import csv
import json

import claims_check

SNAPSHOT = [
    # repeated submissions of one (model, harness) pair are one cell, the best one
    {"benchmark": "a", "model": "m1", "scaffold": "h1", "score": 0.1, "score_unit": "rate"},
    {"benchmark": "a", "model": "m1", "scaffold": "h1", "score": 0.2, "score_unit": "rate"},
    {"benchmark": "a", "model": "m1", "scaffold": "h2", "score": 0.3, "score_unit": "rate"},
    # a single-harness model is not a cross-harness datapoint
    {"benchmark": "a", "model": "m2", "scaffold": "h1", "score": 0.5, "score_unit": "rate"},
    # an unscaffolded record is a model-only score, and a non-rate score is not comparable
    {"benchmark": "b", "model": "m3", "scaffold": "", "score": 0.9, "score_unit": "rate"},
    {"benchmark": "b", "model": "m3", "scaffold": "h9", "score": 0.7, "score_unit": "rate"},
    {"benchmark": "c", "model": "m4", "scaffold": "h1", "score": 0.4, "score_unit": "percent"},
]


def write_snapshot(tmp_path):
    path = tmp_path / "snap.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in SNAPSHOT))
    return str(path)


def test_records_counts_rows_and_benchmark_keys(tmp_path, capsys):
    assert claims_check.main(["records", write_snapshot(tmp_path)]) == 0
    assert capsys.readouterr().out == "7 records across 3 benchmarks\n"


def test_coverage_keeps_only_models_that_were_measured_under_two_harnesses(tmp_path, capsys):
    claims_check.main(["coverage", write_snapshot(tmp_path)])
    # m2 (one harness), board b (one harness per model) and board c (not a 0-1 rate) drop out
    assert capsys.readouterr().out == "1 models and 2 harnesses over 1 benchmarks\n"


def test_spread_comes_from_the_matrix_cells_not_the_csv_columns(tmp_path, capsys):
    matrix = tmp_path / "matrix.csv"
    with matrix.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "A", "B", "C", "spread", "n"])
        # both rows claim n=9 and a spread of 0.9; only m2 really has 3+ harnesses
        w.writerow(["m1", "0.1", "0.5", "", "0.9", "9"])
        w.writerow(["m2", "0.2", "0.4", "0.6", "0.9", "9"])
    claims_check.main(["spread", str(matrix)])
    assert capsys.readouterr().out == "0.400 over 1 models\n"
