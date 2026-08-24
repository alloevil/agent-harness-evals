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
        if "Model version" not in df.columns:
            continue

        score_col = next(
            (c for c in ("Accuracy mean", "mean_score", "Best score (across scorers)", "Score")
             if c in df.columns),
            None,
        )
        if score_col is None:
            continue

        out = pd.DataFrame({
            "benchmark": bench,
            "model": df["Model version"].map(canon_model),
            "model_raw": df["Model version"],
            "scaffold": df["Agent"].map(canon_scaffold) if "Agent" in df.columns else "",
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
        mx = out["score"].max()
        if 1.5 < mx <= 100.0:
            out["score"] /= 100.0
            out["stderr"] /= 100.0
            out["score_unit"] = "rate"
        elif mx > 100.0:
            out["score_unit"] = "raw"
        else:
            out["score_unit"] = "rate"
        frames.append(out)

    records = pd.concat(frames, ignore_index=True)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    dest = CLEAN_DIR / "records.parquet"
    records.to_parquet(dest, index=False)
    print(f"normalized {len(records)} records across "
          f"{records['benchmark'].nunique()} benchmarks -> {dest}")
    return records


if __name__ == "__main__":
    normalize_epoch()
