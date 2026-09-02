"""L1 hardening: variant-stat freeze pin is corpus-insensitive and warns when inert."""

import logging

import pandas as pd
import pytest

from src.variant_system import compute_generic_group_stats


def _make_mapping_with_weapon_and_armor():
    rows = []
    # 50 +1 Weapon variants — would give live max_weight 20, max_dmg_tier 5, count 50
    for i in range(50):
        rows.append(
            {
                "specific_name": f"+1 Weapon Variant {i}",
                "generic_name": "+1 Weapon",
                "weight": float((i % 20) + 1),  # 1..20 => max 20
                "ac": None,
                "dmg_tier": float((i % 5) + 1),  # 1..5 => max 5
            }
        )
    # Control group: +1 Armor (not frozen) — 5 variants, ac-driven
    for i, ac in enumerate([11, 12, 14, 15, 16]):
        rows.append(
            {
                "specific_name": f"+1 Armor Variant {i}",
                "generic_name": "+1 Armor",
                "weight": None,
                "ac": float(ac),
                "dmg_tier": None,
            }
        )
    return pd.DataFrame(rows)


def test_frozen_weapon_stats_pinned():
    df = _make_mapping_with_weapon_and_armor()
    stats = compute_generic_group_stats(df)

    # +1 Weapon must be frozen to baseline (43/18.0/4.0), not live (50/20/5)
    w1 = stats[stats["generic_name"] == "+1 Weapon"].iloc[0]
    assert w1["variant_count"] == 43
    assert w1["max_weight"] == pytest.approx(18.0)
    assert w1["max_dmg_tier"] == pytest.approx(4.0)

    # Control group must remain LIVE (not frozen) — armor +1 not in frozen set
    armor = stats[stats["generic_name"] == "+1 Armor"].iloc[0]
    assert armor["variant_count"] == 5
    # ac stats are live: max_ac 16, median etc.
    assert armor["max_ac"] == pytest.approx(16.0)
    assert armor["min_ac"] == pytest.approx(11.0)
    # weight stats for armor group are None/NaN (no weight), but not frozen
    # Ensure we didn't accidentally freeze armor max_weight
    assert pd.isna(armor["max_weight"]) or armor["max_weight"] is None


def test_frozen_group_absent_emits_warning(caplog):
    # Mapping with NO +2 Weapon or +3 Weapon — freeze should warn for those keys
    rows = []
    for i in range(10):
        rows.append(
            {
                "specific_name": f"+1 Weapon Variant {i}",
                "generic_name": "+1 Weapon",
                "weight": 1.0,
                "ac": None,
                "dmg_tier": 2.0,
            }
        )
    df = pd.DataFrame(rows)
    caplog.set_level(logging.WARNING)
    stats = compute_generic_group_stats(df)
    # +1 Weapon still frozen
    assert stats[stats["generic_name"] == "+1 Weapon"].iloc[0]["variant_count"] == 43
    # Warnings for absent +2 and +3
    msgs = [r.getMessage() for r in caplog.records]
    assert any("Frozen variant group +2 Weapon absent from corpus" in m for m in msgs)
    assert any("Frozen variant group +3 Weapon absent from corpus" in m for m in msgs)


# ─── Hop C5: needle-weight contamination — weapon stats must exclude ammo ───────
def test_hop_c5_weapon_stats_exclude_ammunition():
    """Weapon variant-group stats must EXCLUDE is_ammunition True members (Needle 0.02lb).

    Diagnose: Adamantine Weapon contaminated by Adamantine Needle (0.02lb, A|XPHB) → min_weight 0.02
    vs filtered 1.0; Needler weapon (3lb) no longer ammo-depressed (adj 0 vs negative).
    Bounded diagnosis: which pool/stat produces Needler's large negative adj → weight pool min_weight
    via log_range = log(max/min); ammo 0.02 expands range, depresses weight_factor for light weapons
    but Needler at median stays 0; filtered restores honest min.
    """
    from src.variant_system import compute_adjustment_factor, categorize_generic_variant

    # Build weapon group with 3 honest weapons (1lb-6lb) + 1 ammo member (0.02lb)
    rows = [
        {"specific_name": "Adamantine Longsword", "generic_name": "Adamantine Weapon", "weight": 3.0, "ac": None, "dmg_tier": 3.0, "is_ammunition": False},
        {"specific_name": "Adamantine Greatsword", "generic_name": "Adamantine Weapon", "weight": 6.0, "ac": None, "dmg_tier": 4.0, "is_ammunition": False},
        {"specific_name": "Adamantine Dagger", "generic_name": "Adamantine Weapon", "weight": 1.0, "ac": None, "dmg_tier": 2.0, "is_ammunition": False},
        {"specific_name": "Adamantine Needle", "generic_name": "Adamantine Weapon", "weight": 0.02, "ac": None, "dmg_tier": None, "is_ammunition": True},  # contaminant
        {"specific_name": "Adamantine Arrow", "generic_name": "Adamantine Weapon", "weight": 0.05, "ac": None, "dmg_tier": None, "is_ammunition": True},
    ]
    df = pd.DataFrame(rows)
    stats = compute_generic_group_stats(df)
    w_stats = stats[stats["generic_name"] == "Adamantine Weapon"].iloc[0]
    # After exclusion, min_weight should be 1.0 (lightest honest weapon), not 0.02
    assert w_stats["min_weight"] == pytest.approx(1.0, rel=0.01)
    # variant_count should reflect filtered count (3 weapons, not 5)
    assert w_stats["variant_count"] == 3
    # median_weight should be 3.0 (honest median), not pulled down by ammo
    assert w_stats["median_weight"] == pytest.approx(3.0, rel=0.01)

    # Verify Needler weapon (3lb, dmg_tier None) adjustment is not ammo-depressed
    # Needler-like row: weight 3lb (median), so weight_factor 0 → overall 0
    needler_row = pd.Series({"weight": 3.0, "dmg_tier": None})
    cat = categorize_generic_variant("Adamantine Weapon", "M|XPHB")
    adj = compute_adjustment_factor(needler_row, w_stats, cat)
    assert adj == pytest.approx(0.0, abs=0.001)
    # Light weapon (1lb Dagger) would have been more negative if ammo included (log_range larger → dampened negative)
    # Filtered gives more honest negative: log(1/3)/log(6/1) ≈ -0.61 vs with ammo log(1/3)/log(6/0.02) ≈ -0.19
    dagger_row = pd.Series({"weight": 1.0, "dmg_tier": 2.0})
    adj_dagger = compute_adjustment_factor(dagger_row, w_stats, cat)
    # With filtered min 1.0, max 6.0, median 3.0 → weight_factor = log(1/3)/log(6/1) = -1.0986/1.7918 = -0.613, dmg_factor = (2-3)/(4-2)= -0.5 → blend = -0.556
    assert adj_dagger == pytest.approx(-0.556, abs=0.02)

    # Ammo groups must RETAIN their members (not filtered)
    rows_ammo = [
        {"specific_name": "Needle of Slaying", "generic_name": "Ammunition of Slaying", "weight": 0.02, "ac": None, "dmg_tier": None, "is_ammunition": True},
        {"specific_name": "Arrow of Slaying", "generic_name": "Ammunition of Slaying", "weight": 0.05, "ac": None, "dmg_tier": None, "is_ammunition": True},
    ]
    df_ammo = pd.DataFrame(rows_ammo)
    stats_ammo = compute_generic_group_stats(df_ammo)
    a_stats = stats_ammo[stats_ammo["generic_name"] == "Ammunition of Slaying"].iloc[0]
    assert a_stats["variant_count"] == 2
    assert a_stats["min_weight"] == pytest.approx(0.02, rel=0.01)
