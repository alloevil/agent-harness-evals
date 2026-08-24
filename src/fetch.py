"""Fetch live benchmark data from upstream sources.

Currently: Epoch AI Benchmarking Hub (CC-BY, updated ~daily).
Each source is a self-contained fetcher, following the Messier builder pattern.
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import requests

EPOCH_URL = "https://epoch.ai/data/benchmark_data.zip"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def fetch_epoch(dest: Path = RAW_DIR / "epoch") -> Path:
    """Download and extract the Epoch benchmark data dump."""
    dest.mkdir(parents=True, exist_ok=True)
    resp = requests.get(EPOCH_URL, timeout=120)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        zf.extractall(dest)
    n = len(list(dest.glob("*.csv")))
    print(f"epoch: extracted {n} CSVs -> {dest}")
    return dest


if __name__ == "__main__":
    fetch_epoch()
