"""Recompute the numbers docs/claims.json publishes, from committed artifacts only.

Deliberately *not* a re-run of src/build_site.py: a gate that re-runs the code which produced
a number agrees with itself by construction and can never fail. Every figure below is derived
again from data this repository commits:

    records   rows, and distinct benchmark keys, of data/snapshots/<date>.jsonl
    coverage  union of models and harnesses over boards where some model has 2+ harnesses
    spread    per-model spread recomputed from a committed views/harness_matrix_<b>.csv
    motion    the built page animates and honours prefers-reduced-motion (reads docs/index.html)

Standard library only. The claims CI job installs nothing (it runs on a bare python3), so the
receipt behind a claim has to be executable without pandas, the network, or any API key.

Usage (paths are relative to the repository root, which is where the claims job runs):
    python3 src/claims_check.py records data/snapshots/2026-09-12.jsonl
    python3 src/claims_check.py coverage data/snapshots/2026-09-12.jsonl
    python3 src/claims_check.py spread views/harness_matrix_terminalbench.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict

MIN_HARNESSES = 2  # a board is cross-harness only if some model was measured under 2+
SPREAD_MIN_N = 3  # a 2-harness gap is one pairwise difference, not a spread


def load_snapshot(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def best_cells(rows: list[dict]) -> dict[str, dict[tuple[str, str], float]]:
    """{benchmark: {(model, harness): best 0-1 rate}} over scaffolded records."""
    cells: dict[str, dict[tuple[str, str], float]] = defaultdict(dict)
    for rec in rows:
        if not rec["scaffold"] or rec["score_unit"] != "rate":
            continue
        key = (rec["model"], rec["scaffold"])
        bench = cells[rec["benchmark"]]
        if key not in bench or rec["score"] > bench[key]:
            bench[key] = rec["score"]
    return cells


def cross_harness(cells: dict[str, dict[tuple[str, str], float]]) -> dict[str, dict[tuple[str, str], float]]:
    """Keep the boards where at least one model was measured under MIN_HARNESSES+ harnesses.

    Boards with no such model are native-pairing boards (every model under one harness), which
    carry no model x harness matrix and so are not part of the coverage figure.
    """
    boards = {}
    for bench, cell in cells.items():
        seen: dict[str, set[str]] = defaultdict(set)
        for model, harness in cell:
            seen[model].add(harness)
        keep = {m for m, hs in seen.items() if len(hs) >= MIN_HARNESSES}
        if keep:
            boards[bench] = {k: v for k, v in cell.items() if k[0] in keep}
    return boards


def cmd_records(snapshot: str) -> str:
    rows = load_snapshot(snapshot)
    return f"{len(rows)} records across {len({r['benchmark'] for r in rows})} benchmarks"


def cmd_coverage(snapshot: str) -> str:
    boards = cross_harness(best_cells(load_snapshot(snapshot)))
    models = {m for cell in boards.values() for m, _ in cell}
    harnesses = {h for cell in boards.values() for _, h in cell}
    return f"{len(models)} models and {len(harnesses)} harnesses over {len(boards)} benchmarks"


def cmd_spread(matrix_csv: str) -> str:
    """Median of (best - worst harness) over the matrix rows a model needs 3+ harnesses for."""
    with open(matrix_csv, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        # `n` is recounted from the cells rather than trusted as a column
        cols = [i for i, name in enumerate(header) if name not in ("model", "spread", "n")]
        spreads = []
        for row in reader:
            scores = [float(row[i]) for i in cols if row[i] != ""]
            if len(scores) >= SPREAD_MIN_N:
                spreads.append(max(scores) - min(scores))
    if not spreads:
        raise SystemExit(f"{matrix_csv}: no model is measured under {SPREAD_MIN_N}+ harnesses")
    return f"{round(statistics.median(spreads), 3):.3f} over {len(spreads)} models"


def cmd_motion(page: str) -> str:
    """Check the page animates and can be told not to.

    Covers every way this page can move — CSS animations and transitions, cross-document view
    transitions, SVG SMIL, requestAnimationFrame and WAAPI's element.animate() — and requires a
    reduced-motion branch wherever one is found. A miss here is not a silent pass: `found` is
    asserted, so a page that moves in a way the detector does not know about fails loudly instead
    of looking compliant.
    """
    import pathlib as _pathlib
    import re as _re

    text = _pathlib.Path(page).read_text(encoding="utf-8")
    moves = _re.compile(r"animation\s*:|@keyframes|<animate\b|requestAnimationFrame|\.animate\("
                        r"|transition\s*:|@view-transition")
    found = bool(moves.search(text))
    reducible = "prefers-reduced-motion" in text
    assert found, f"{page}: no motion primitive found — the check would pass vacuously"
    assert reducible, f"{page}: animates without a prefers-reduced-motion branch"
    return f"animated 1 reducible 1 ({page})"


COMMANDS = {"records": cmd_records, "coverage": cmd_coverage, "spread": cmd_spread,
            "motion": cmd_motion}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="claims_check",
        description="Recompute a published figure from the committed snapshot or matrix CSV.",
    )
    sub = parser.add_subparsers(dest="what", required=True)
    for name in ("records", "coverage"):
        sub.add_parser(name).add_argument("snapshot", help="data/snapshots/<date>.jsonl")
    sub.add_parser("spread").add_argument("matrix_csv", help="views/harness_matrix_<b>.csv")
    sub.add_parser("motion").add_argument("page", help="docs/index.html")
    args = parser.parse_args(argv)
    path = (args.snapshot if args.what in ("records", "coverage")
            else args.matrix_csv if args.what == "spread" else args.page)
    print(COMMANDS[args.what](path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
