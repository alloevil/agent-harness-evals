"""Unit tests for the normalization layer — the load-bearing wall of the pipeline.

The scale heuristic and name reconciliation decide whether two scores are
comparable. If upstream renames a column or a benchmark ships a new scale,
these tests must fail loudly rather than let the matrix silently go wrong.
"""
import pandas as pd
import pytest

from normalize import canon_model, canon_scaffold, rescale


# --- model id canonicalization ------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("gpt-5.3-codex", "gpt-5.3-codex"),
    ("claude-opus-4-6_unknown", "claude-opus-4-6"),
    ("gemini-3.1-pro_max", "gemini-3.1-pro"),
    ("deepseek-v4_128K", "deepseek-v4"),
    ("gpt-5-mini_medium", "gpt-5-mini"),
])
def test_canon_model_strips_release_suffix(raw, expected):
    assert canon_model(raw) == expected


# --- scaffold (harness) reconciliation ---------------------------------------

def test_canon_scaffold_exact_alias():
    assert canon_scaffold("Forge Code") == "ForgeCode"
    assert canon_scaffold("grok-cli") == "Grok CLI"
    assert canon_scaffold("Codex") == "Codex CLI"


def test_canon_scaffold_regex_collapses_step_budget_family():
    # OSWorld records "<model> (N steps)": not a harness, a budget.
    assert canon_scaffold("claude-sonnet-4-6 (100 steps)") == "computer-use"
    assert canon_scaffold("o3 (15 steps)") == "computer-use"
    assert canon_scaffold("qwen2.5-vl-72b-instruct (50 steps)") == "computer-use"


def test_canon_scaffold_passthrough_and_empty():
    assert canon_scaffold("Droid") == "Droid"
    assert canon_scaffold("  Terminus 2  ") == "Terminus 2"  # stripped
    assert canon_scaffold(None) == ""


# --- scale classification ----------------------------------------------------

def test_rescale_percent_to_rate():
    scores, stderr, unit = rescale(pd.Series([0.0, 50.0, 80.0]), pd.Series([1.0, 2.0, 4.0]))
    assert unit == "rate"
    assert scores.tolist() == pytest.approx([0.0, 0.5, 0.8])
    assert stderr.tolist() == pytest.approx([0.01, 0.02, 0.04])


def test_rescale_already_rate_untouched():
    scores, _, unit = rescale(pd.Series([0.0, 0.5, 0.8]))
    assert unit == "rate"
    assert scores.tolist() == pytest.approx([0.0, 0.5, 0.8])


def test_rescale_raw_units_flagged():
    scores, _, unit = rescale(pd.Series([0.0, 200.0, 5000.0]))
    assert unit == "raw"
    assert scores.tolist() == pytest.approx([0.0, 200.0, 5000.0])


def test_rescale_boundary_150_is_rate_not_percent():
    # 1.5 is not > 1.5, so a max of exactly 1.5 stays rate (not /100).
    scores, _, unit = rescale(pd.Series([0.0, 1.5]))
    assert unit == "rate"
    assert scores.tolist() == pytest.approx([0.0, 1.5])


# --- data contract -----------------------------------------------------------

def test_normalize_epoch_contract(tmp_path):
    """A synthetic two-benchmark dump must come out rate-bounded and clean."""
    import normalize as n
    (tmp_path / "percent_bench.csv").write_text(
        "Model version,mean_score,Organization\n"
        "model-a_unknown,78.0,Org\n"
        "model-b,62.5,Org\n"
    )
    (tmp_path / "raw_bench.csv").write_text(
        "Model version,Accuracy mean,Agent\n"
        "model-a,1200.0,Droid\n"
        "model-b,3400.0,Droid\n"
    )
    records = n.normalize_epoch(tmp_path)
    # normalize_epoch writes to the real CLEAN_DIR; restore the real parquet
    # afterwards is not needed here since we only assert on the returned frame.
    rate = records[records["score_unit"] == "rate"]
    raw = records[records["score_unit"] == "raw"]
    assert not rate.empty and not raw.empty
    assert rate["score"].between(0, 1).all()
    assert raw["score"].min() > 100.0
    assert (records["model"] != "").all()
    assert set(records["score_unit"]).issubset({"rate", "raw"})
