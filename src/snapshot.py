"""Persist a daily snapshot of the normalized records.

The parquet is overwritten on every fetch; snapshots make history diffable
and enable the per-model-per-harness trend view. One JSONL file per day,
line-oriented so `git diff` stays readable and the series can be replayed.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "data" / "clean" / "records.parquet"
SNAPSHOTS = ROOT / "data" / "snapshots"


def snapshot(dest: Path = SNAPSHOTS, records: pd.DataFrame | None = None) -> Path:
    if records is None:
        records = pd.read_parquet(CLEAN)
    dest.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    path = dest / f"{today}.jsonl"
    # Overwrite same-day file so a re-run within one day is idempotent.
    records.to_json(path, orient="records", lines=True, date_format="iso")
    print(f"snapshot: {path} ({path.stat().st_size/1024:.0f} KB)")
    return path


def load_history(src: Path = SNAPSHOTS) -> pd.DataFrame:
    """Concatenate all snapshots, adding a `date` column per file."""
    import json

    rows: list[dict] = []
    for f in sorted(src.glob("*.jsonl")):
        d = f.stem
        for line in f.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                rec["date"] = d
                rows.append(rec)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    snapshot()
