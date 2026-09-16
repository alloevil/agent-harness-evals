"""The gate behind docs/claims.json: each figure is recomputed from a committed artifact.

A checker that quietly agrees with whatever is published is worse than no checker, so these
pin the parts of src/claims_check.py that decide a number: which records count, when a board is
cross-harness, and that a model's spread comes from the matrix cells and not from the CSV's own
`spread`/`n` columns.

The motion check gets the same treatment for the same reason: its detector decides what counts as
moving, and a detector that has quietly lost a primitive turns "animates and is reducible" into a
pass for pages that do neither. The primitives are enumerated below, so a page that moves in a way
the detector does not know about is a test failure rather than a silent pass.
"""
import csv
import json

import pytest

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


REDUCED = "@media (prefers-reduced-motion: reduce) { * { transition-duration: .001ms !important; } }\n"

# Every way a page in this project can move. Losing one of these from the detector used to be
# invisible: the check asserts `found`, so the failure mode is an error on a page that does animate,
# not a pass — but it means the receipt cannot be satisfied for that page at all.
MOTION_PRIMITIVES = [
    ".a { animation: spin 1s linear infinite; }\n",
    "@keyframes spin { to { transform: rotate(1turn); } }\n",
    '<svg><animate attributeName="x" dur="1s"></animate></svg>\n',
    "requestAnimationFrame(() => step());\n",
    "row.animate([{ transform: 'translateY(0)' }], { duration: 200 });\n",
    ".a { transition: color .12s; }\n",
    "@view-transition { navigation: auto; }\n",
]


@pytest.mark.parametrize("primitive", MOTION_PRIMITIVES)
def test_motion_recognises_every_primitive_it_claims_to_cover(tmp_path, capsys, primitive):
    page = tmp_path / "index.html"
    page.write_text(f"<html><head><style>{primitive}{REDUCED}</style></head></html>")
    assert claims_check.main(["motion", str(page)]) == 0
    assert capsys.readouterr().out == f"animated 1 reducible 1 ({page})\n"


def test_motion_rejects_animation_without_a_reduced_motion_branch(tmp_path):
    page = tmp_path / "index.html"
    page.write_text("<html><head><style>.a { transition: color .12s; }</style></head></html>")
    with pytest.raises(AssertionError, match="animates without a prefers-reduced-motion branch"):
        claims_check.main(["motion", str(page)])


def test_motion_fails_loudly_when_the_detector_finds_no_primitive(tmp_path):
    # The anti-vacuous guard: a page that does not move cannot pass "animates and is reducible".
    page = tmp_path / "index.html"
    page.write_text(f"<html><head><style>{REDUCED}</style></head></html>")
    with pytest.raises(AssertionError, match="would pass vacuously"):
        claims_check.main(["motion", str(page)])
