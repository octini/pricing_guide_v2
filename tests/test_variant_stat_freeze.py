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
