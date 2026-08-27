"""Unit tests for ML retrain fingerprint discipline."""

import json
import hashlib
from pathlib import Path

import pytest

from src.ml_fingerprint import compute_fingerprint, load_criteria_columns, get_training_feature_columns, current_fingerprint


def test_fingerprint_stable_across_runs():
    feats = ["weapon_bonus", "ac_bonus", "flight_full"]
    crits = ["name", "rarity", "weapon_bonus", "ac_bonus", "flight_full"]
    fp1 = compute_fingerprint(feats, crits)
    fp2 = compute_fingerprint(feats, crits)
    assert fp1 == fp2
    # full sha256 hex length
    assert len(fp1) == 64
    # hex chars
    assert all(c in "0123456789abcdef" for c in fp1)


def test_fingerprint_sorted_insensitive_to_input_order():
    feats_a = ["b", "a", "c"]
    feats_b = ["c", "a", "b"]
    crits_a = ["z", "a"]
    crits_b = ["a", "z"]
    assert compute_fingerprint(feats_a, crits_a) == compute_fingerprint(feats_b, crits_b)


def test_fingerprint_changes_when_feature_list_changes():
    crits = ["name", "rarity", "ac_bonus"]
    fp_base = compute_fingerprint(["ac_bonus", "weapon_bonus"], crits)
    fp_added = compute_fingerprint(["ac_bonus", "weapon_bonus", "flight_full"], crits)
    fp_removed = compute_fingerprint(["ac_bonus"], crits)
    assert fp_base != fp_added
    assert fp_base != fp_removed
    assert fp_added != fp_removed


def test_fingerprint_changes_when_criteria_columns_change():
    feats = ["ac_bonus", "weapon_bonus"]
    fp_base = compute_fingerprint(feats, ["a", "b", "c"])
    fp_added = compute_fingerprint(feats, ["a", "b", "c", "new_col"])
    fp_removed = compute_fingerprint(feats, ["a", "b"])
    assert fp_base != fp_added
    assert fp_base != fp_removed


def test_fingerprint_trims_and_string_coerces():
    # " a " and "a" should be identical after strip
    assert compute_fingerprint([" a ", "b"], [" c"]) == compute_fingerprint(["a", "b"], ["c"])


def test_load_criteria_columns_reads_header(tmp_path: Path):
    p = tmp_path / "criteria.csv"
    p.write_text("col_a,col_b,col_c\n1,2,3\n", encoding="utf-8")
    cols = load_criteria_columns(p)
    assert cols == ["col_a", "col_b", "col_c"]


def test_load_criteria_columns_fallback_missing_returns_empty(tmp_path: Path):
    p = tmp_path / "nonexistent.csv"
    cols = load_criteria_columns(p)
    assert cols == []


def test_get_training_feature_columns_matches_06():
    cols = get_training_feature_columns()
    # must include FEATURE_COLS subset and derived dummies
    assert "weapon_bonus" in cols
    assert "ac_bonus" in cols
    assert "rarity_legendary" in cols
    assert "attune_open" in cols
    assert "type_M" in cols
    assert "has_ability_mods" in cols
    # no duplicates
    assert len(cols) == len(set(cols))


def test_current_fingerprint_stable(tmp_path: Path):
    # current_fingerprint uses real repo files; should be deterministic
    fp1 = current_fingerprint()
    fp2 = current_fingerprint()
    assert fp1 == fp2
    assert len(fp1) == 64


def test_check_r2_mismatch_detection_logic(tmp_path: Path):
    """Test the helper logic that check_r2 uses: stored vs current."""
    # Simulate stored coefficients with old fingerprint
    feats_old = ["weapon_bonus", "ac_bonus"]
    crits_old = ["weapon_bonus", "ac_bonus", "name"]
    stored_fp = compute_fingerprint(feats_old, crits_old)

    # Current has new feature -> mismatch
    feats_new = ["weapon_bonus", "ac_bonus", "flight_full"]
    current_fp = compute_fingerprint(feats_new, crits_old)
    assert stored_fp != current_fp

    # Simulate check_r2 comparison branch
    mismatch = current_fp != stored_fp
    assert mismatch is True

    # Matching case
    assert compute_fingerprint(feats_old, crits_old) == stored_fp


def test_compute_fingerprint_known_vector():
    # Known payload: sorted feats ["a","b"] + sorted crits ["x","y"]
    # payload = "a\nb\n---\nx\ny" -> sha256 known
    payload = "a\nb\n---\nx\ny"
    expected = hashlib.sha256(payload.encode()).hexdigest()
    assert compute_fingerprint(["b", "a"], ["y", "x"]) == expected
