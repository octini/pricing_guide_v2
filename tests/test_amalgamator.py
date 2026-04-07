# tests/test_amalgamator.py
import pytest
import pandas as pd
from src.amalgamator import trim_outliers, calculate_weights, fuzzy_match_items


def test_trim_outliers_removes_top_and_bottom_2pct():
    prices = list(range(1, 101))  # 100 items, 1..100
    df = pd.DataFrame({"price_gp": prices})
    trimmed = trim_outliers(df, "price_gp", pct=0.02)
    # 2% of 100 = 2 items from each end (prices 1,2 and 99,100 removed)
    assert trimmed["price_gp"].min() >= 3
    assert trimmed["price_gp"].max() <= 98
    assert len(trimmed) == 96


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
