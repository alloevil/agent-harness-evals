"""Generate the model x harness matrix — the view no public leaderboard offers.

For every benchmark that records a scaffold (agent harness), pivot to
models-as-rows, harnesses-as-columns. Only models evaluated under 2+
harnesses are kept: the point is isolating the harness contribution
while holding the model fixed.

Outputs per benchmark:
    views/harness_matrix_<benchmark>.csv
    views/harness_matrix_<benchmark>.md   (README-embeddable)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

CLEAN = Path(__file__).resolve().parent.parent / "data" / "clean" / "records.parquet"
VIEWS = Path(__file__).resolve().parent.parent / "views"


def harness_matrices(min_harnesses: int = 2) -> dict[str, pd.DataFrame]:
    records = pd.read_parquet(CLEAN)
    scaffolded = records[(records["scaffold"] != "") & (records["score_unit"] == "rate")]
    out: dict[str, pd.DataFrame] = {}
    VIEWS.mkdir(exist_ok=True)

    for bench, grp in scaffolded.groupby("benchmark"):
        # best score per (model, scaffold); dedupe repeated submissions
        cell = (grp.groupby(["model", "scaffold"])["score"].max().reset_index())
        counts = cell.groupby("model")["scaffold"].nunique()
        keep = counts[counts >= min_harnesses].index
        cell = cell[cell["model"].isin(keep)]
        if cell.empty:
            continue

        matrix = cell.pivot(index="model", columns="scaffold", values="score")
        # order: models by their best score, harnesses by coverage
        matrix = matrix.loc[matrix.max(axis=1).sort_values(ascending=False).index]
        matrix = matrix[matrix.notna().sum().sort_values(ascending=False).index]
        matrix["spread"] = matrix.max(axis=1) - matrix.min(axis=1)

        matrix.to_csv(VIEWS / f"harness_matrix_{bench}.csv")
        (VIEWS / f"harness_matrix_{bench}.md").write_text(
            f"# {bench}: same model, different harness\n\n"
            f"Best score per (model, harness) pair; `spread` = max−min across "
            f"harnesses for that model.\n\n"
            + matrix.round(3).to_markdown()
            + "\n"
        )
        out[bench] = matrix
        print(f"{bench}: {matrix.shape[0]} models x {matrix.shape[1]-1} harnesses, "
              f"median spread {matrix['spread'].median():.3f}")
    return out


if __name__ == "__main__":
    harness_matrices()
