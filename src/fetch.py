"""Fetch live benchmark data from upstream sources.

Currently: Epoch AI Benchmarking Hub (CC-BY, updated ~daily).
Each source is a self-contained fetcher, following the Messier builder pattern.
"""
from __future__ import annotations

import io
import time
import zipfile
from pathlib import Path

import requests

EPOCH_URL = "https://epoch.ai/data/benchmark_data.zip"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def _get(url: str, timeout: int, tries: int = 3) -> requests.Response:
    """GET with linear-backoff retries; transient upstream hiccups are normal
    for a daily cron and should not cost a day of freshness."""
    for attempt in range(1, tries + 1):
        try:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            if attempt == tries:
                raise
            print(f"retry {attempt}/{tries - 1} for {url}: {e}")
            time.sleep(5 * attempt)
    raise AssertionError("unreachable")


def fetch_epoch(dest: Path = RAW_DIR / "epoch") -> Path:
    """Download and extract the Epoch benchmark data dump."""
    dest.mkdir(parents=True, exist_ok=True)
    resp = _get(EPOCH_URL, timeout=120)
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        zf.extractall(dest)
    n = len(list(dest.glob("*.csv")))
    print(f"epoch: extracted {n} CSVs -> {dest}")
    return dest


HAL_BENCHMARKS = [
    "swebench_verified_mini", "corebench_hard", "gaia", "online_mind2web",
    "scicode", "scienceagentbench", "taubench_airline", "usaco", "assistantbench",
]
HAL_URL = "https://hal.cs.princeton.edu/{}"


def fetch_hal(dest: Path = RAW_DIR / "hal") -> Path:
    """Download HAL leaderboard pages (harness x model x cost, historical).

    One failed page loses that benchmark for the day, not the whole run:
    the previous day's HTML stays on disk and normalize picks it up.
    """
    dest.mkdir(parents=True, exist_ok=True)
    for bench in HAL_BENCHMARKS:
        try:
            resp = _get(HAL_URL.format(bench), timeout=60)
        except requests.RequestException as e:
            print(f"WARN hal {bench} failed, keeping previous file: {e}")
            continue
        (dest / f"{bench}.html").write_text(resp.text)
        print(f"hal: {bench} ({len(resp.text)/1024:.0f} KB)")
    return dest


if __name__ == "__main__":
    fetch_epoch()
    fetch_hal()


