"""Normalize raw benchmark CSVs into the unified record schema.

Schema (subset of Messier's reconciliation model):
    benchmark   str   canonical benchmark id
    model       str   canonical model id (release-config suffixes stripped)
    model_raw   str   original identifier, for traceability
    scaffold    str   agent harness ("" = provider-default / unscaffolded)
    score       float primary metric; percent scales rescaled to 0-1
    score_unit  str   "rate" (0-1 comparable) | "raw" (source units, e.g. $)
    stderr      float standard error when reported
    org         str   model organization
    release_date str  model release date (ISO)
    source      str   data source id
    source_link str   provenance URL
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import yaml

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
CLEAN_DIR = Path(__file__).resolve().parent.parent / "data" / "clean"
_ALIAS_FILE = Path(__file__).resolve().parent / "harness_aliases.yaml"


def _load_aliases() -> tuple[dict[str, str], list[tuple[str, "re.Pattern"]]]:
    spec = yaml.safe_load(_ALIAS_FILE.read_text())
    exact = {alias.strip(): canon
             for canon, al in (spec.get("aliases") or {}).items()
             for alias in al}
    patterns = [(canon, re.compile(rx, re.IGNORECASE))
                for canon, rx in (spec.get("regex") or {}).items()]
    return exact, patterns


_ALIAS_EXACT, _ALIAS_RE = _load_aliases()

# Release-config suffixes Epoch appends to model ids (_unknown, _medium, _max,
# _xhigh, _128K, ...). Keep reasoning-effort levels distinct? No: for cross-
# harness comparison the base model is the unit; effort level goes to model_raw.
_SUFFIX = re.compile(r"_(unknown|medium|low|high|xhigh|max|mini|\d+K)$")


def canon_model(raw: str) -> str:
    return _SUFFIX.sub("", str(raw).strip())


def canon_scaffold(raw) -> str:
    if pd.isna(raw):
        return ""
    s = str(raw).strip()
    if s in _ALIAS_EXACT:
        return _ALIAS_EXACT[s]
    for canon, pat in _ALIAS_RE:
        if pat.search(s):
            return canon
    return s

def rescale(scores: pd.Series, stderr: "pd.Series | None" = None) -> tuple[pd.Series, "pd.Series | None", str]:
    """Classify a benchmark's score scale; normalize percent (0-100) to 0-1.

    Heuristic on the benchmark's max score: (1.5, 100] -> percent -> rate;
    >100 -> raw units (e.g. dollars); otherwise already a 0-1 rate. The
    stderr column, when present, is rescaled in lockstep with the score.
    """
    mx = scores.max()
    if pd.isna(mx):
        return scores, stderr, "rate"
    if 1.5 < mx <= 100.0:
        return (scores / 100.0,
                (stderr / 100.0 if stderr is not None else stderr),
                "rate")
    if mx > 100.0:
        return scores, stderr, "raw"
    return scores, stderr, "rate"


_HARNESS_COLS = ("Agent", "Harness", "Scaffold")
_SCORE_COLS = (
    "Accuracy mean", "mean_score", "Best score (across scorers)", "Score",
    "Main score", "Pass@1", "Pooled score", "Average score", "Average (%)",
    "Mean capability", "Score OPT@1",
)


def _harness_col(df: pd.DataFrame) -> "str | None":
    """Find the harness/scaffold column. Skip boolean pseudo-harness columns
    (deepresearchbench's `Agent` column is a True/False flag, not names)."""
    for c in _HARNESS_COLS:
        if c in df.columns:
            vals = df[c].dropna()
            if vals.map(type).eq(bool).all() and vals.nunique() <= 2:
                continue
            return c
    return None


def normalize_epoch(src: Path = RAW_DIR / "epoch") -> pd.DataFrame:
    """Flatten every Epoch per-benchmark CSV into unified records.

    Epoch files come in two shapes:
      - model-level:  Model version, mean_score / Best score, ...
      - agent-level:  Model version, Agent, Accuracy mean, ...  (e.g. terminal-bench)
    """
    frames: list[pd.DataFrame] = []
    for csv in sorted(src.glob("*.csv")):
        bench = csv.stem.removesuffix("_external")
        if bench in ("epoch_capabilities_index",):  # index, not a benchmark
            continue
        try:
            df = pd.read_csv(csv)
        except Exception as e:  # malformed upstream file: skip, don't die
            print(f"skip {csv.name}: {e}")
            continue
        hcol = _harness_col(df)
        score_col = next((c for c in _SCORE_COLS if c in df.columns), None)
        if score_col is None:
            continue

        out = pd.DataFrame({
            "benchmark": bench,
            "model": df["Model version"].map(canon_model),
            "model_raw": df["Model version"],
            "scaffold": df[hcol].map(canon_scaffold) if hcol else "",
            "score": pd.to_numeric(df[score_col], errors="coerce"),
            "stderr": pd.to_numeric(
                df.get("Accuracy SE", df.get("stderr", pd.Series(dtype=float))),
                errors="coerce",
            ),
            "org": df.get("Organization", ""),
            "release_date": df.get("Release date", ""),
            "source": "epoch",
            "source_link": df.get("Source Link", df.get("Log viewer", "")),
        })
        out = out.dropna(subset=["score"])
        out = out[out["model_raw"].notna() & (out["model"] != "") & (out["model"] != "nan")]
        # Scale heuristic: 0-100 percent scales -> 0-1. Non-rate metrics
        # (e.g. vending_bench dollars) stay raw, flagged via score_unit.
        out["score"], out["stderr"], out["score_unit"] = rescale(
            out["score"], out["stderr"]
        )
        frames.append(out)

    records = pd.concat(frames, ignore_index=True)
    return records


# --- HAL (Holistic Agent Leaderboard): historical harness x model x cost -------

_HAL_EFFORT = re.compile(r"\s+(High|Medium|Low)\s*$")
_HAL_DATE = re.compile(r"\s*\(.*\)\s*$")
_PCT = re.compile(r"([\d.]+)%")


def canon_hal_model(raw: str) -> str:
    """'Claude Sonnet 4.5 High (September 2025)' -> 'claude-sonnet-4.5'."""
    s = _HAL_DATE.sub("", str(raw).strip())
    s = _HAL_EFFORT.sub("", s)
    return s.lower().replace(" ", "-")


def parse_pct(x) -> "float | None":
    m = _PCT.search(str(x))
    return float(m.group(1)) / 100.0 if m else None


def normalize_hal(src: Path = RAW_DIR / "hal") -> pd.DataFrame:
    """Parse HAL leaderboard HTML into unified records (source='hal')."""
    frames: list[pd.DataFrame] = []
    for f in sorted(src.glob("*.html")):
        bench = "hal_" + f.stem
        try:
            tables = pd.read_html(f)
        except Exception as e:
            print(f"skip {f.name}: {e}")
            continue
        if not tables:
            continue
        t = tables[0]
        if t.shape[1] < 6:  # not a leaderboard table
            continue
        out = pd.DataFrame({
            "benchmark": bench,
            "model": t.iloc[:, 2].map(canon_hal_model),
            "model_raw": t.iloc[:, 2],
            "scaffold": t.iloc[:, 1].map(lambda x: str(x).strip()),
            "score": t.iloc[:, 4].map(parse_pct),
            "score_unit": "rate",
            "stderr": None,
            "org": "",
            "release_date": "",
            "source": "hal",
            "source_link": f"https://hal.cs.princeton.edu/{f.stem}",
        })
        out = out.dropna(subset=["score"])
        frames.append(out)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def normalize_all() -> pd.DataFrame:
    """Run every source builder and write the unified parquet."""
    parts = [normalize_epoch(), normalize_hal()]
    records = pd.concat([p for p in parts if not p.empty], ignore_index=True)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    dest = CLEAN_DIR / "records.parquet"
    records.to_parquet(dest, index=False)
    print(f"normalized {len(records)} records across "
          f"{records['benchmark'].nunique()} benchmarks -> {dest}")
    return records


if __name__ == "__main__":
    normalize_all()
