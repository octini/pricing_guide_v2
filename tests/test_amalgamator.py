# tests/test_amalgamator.py
import pytest
import pandas as pd
from src.amalgamator import trim_outliers, calculate_weights, fuzzy_match_items


def test_trim_outliers_removes_top_and_bottom_2pct():
    """Current intended behavior (b449ba0 2026-04-13): only zero-price joke items
    removed; the original top/bottom 2% trimming was dropped because it
    incorrectly removed legitimate expensive items like Rod of Resurrection
    (MSRP 140k, DMPG 125k). The pct param is retained for signature compat
    but no longer trims high/low tails. This test verifies zero-price
    filtering and that all legitimate prices are preserved."""
    prices = list(range(1, 101))  # 100 items, 1..100 — no zeros
    df = pd.DataFrame({"price_gp": prices})
    trimmed = trim_outliers(df, "price_gp", pct=0.02)
    # No legitimate prices trimmed
    assert trimmed["price_gp"].min() == 1
    assert trimmed["price_gp"].max() == 100
    assert len(trimmed) == 100
    # Zero-price (joke/cursed) items are the only outliers removed
    df2 = pd.DataFrame({"price_gp": [0, 0] + list(range(1, 101))})
    trimmed2 = trim_outliers(df2, "price_gp", pct=0.02)
    assert 0 not in trimmed2["price_gp"].values
    assert len(trimmed2) == 100


def test_trim_outliers_small_df():
    """Should not error on tiny dataframes."""
    df = pd.DataFrame({"price_gp": [100, 200, 300]})
    trimmed = trim_outliers(df, "price_gp", pct=0.02)
    assert len(trimmed) > 0


def test_calculate_weights_all_close():
    """All three guides within 25% → equal weights."""
    prices = {"DSA": 1000.0, "MSRP": 1050.0, "DMPG": 1020.0}
    weights = calculate_weights(prices)
    assert abs(weights["DSA"] - 1/3) < 0.01
    assert abs(weights["MSRP"] - 1/3) < 0.01
    assert abs(weights["DMPG"] - 1/3) < 0.01


def test_calculate_weights_two_aligned():
    """DSA and MSRP within 25%, DMPG is outlier → DMPG weight = 0.20."""
    prices = {"DSA": 1000.0, "MSRP": 1050.0, "DMPG": 5000.0}
    weights = calculate_weights(prices)
    assert weights["DMPG"] == pytest.approx(0.20, abs=0.01)
    assert weights["DSA"] == pytest.approx(0.40, abs=0.01)
    assert weights["MSRP"] == pytest.approx(0.40, abs=0.01)


def test_calculate_weights_all_diverge():
    """All diverge → 40% DSA, 30% MSRP, 30% DMPG."""
    prices = {"DSA": 1000.0, "MSRP": 5000.0, "DMPG": 20000.0}
    weights = calculate_weights(prices)
    assert weights["DSA"] == pytest.approx(0.40, abs=0.01)
    assert weights["MSRP"] == pytest.approx(0.30, abs=0.01)
    assert weights["DMPG"] == pytest.approx(0.30, abs=0.01)


def test_fuzzy_match_exact():
    items = ["Bag of Holding", "Cloak of Elvenkind"]
    candidates = ["bag of holding", "cloak of elvenkind", "boots of speed"]
    matches = fuzzy_match_items("Bag of Holding", candidates, threshold=85)
    assert "bag of holding" in matches


def test_fuzzy_match_no_match():
    matches = fuzzy_match_items("Vorpal Sword", ["boots of speed", "ring of protection"], threshold=85)
    assert len(matches) == 0
