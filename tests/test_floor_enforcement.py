"""Tripwire floor enforcement: absolute rarity floors for all items except official and consumable modifiers."""

import importlib.util
import pathlib
import pandas as pd
import pytest

# Load the enforcement module via importlib (file name starts with digits, not importable normally)
_SPEC = importlib.util.spec_from_file_location(
    "enforce_floors", pathlib.Path(__file__).parent.parent / "scripts" / "09_enforce_floors.py"
)
_mod = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_mod)

ABSOLUTE_RARITY_FLOORS = _mod.ABSOLUTE_RARITY_FLOORS
apply_absolute_rarity_floor = _mod.apply_absolute_rarity_floor
_is_consumable_modifier_row = _mod._is_consumable_modifier_row
_is_official_price_row = _mod._is_official_price_row
find_mundane_prices = _mod.find_mundane_prices
find_base_item = _mod.find_base_item
is_flavor_item = _mod.is_flavor_item
RARITY_MINIMUMS = _mod.RARITY_MINIMUMS

from src.pricing_engine import RARITY_FLOORS as ENGINE_FLOORS


def _make_df(rows):
    """Helper: rows is list of dicts, return DataFrame with required columns."""
    # Ensure all expected columns exist with defaults for the enforcement helpers
    df = pd.DataFrame(rows)
    # Fill missing columns that helpers may access
    for col in ["item_type_code", "is_ammunition", "is_poison", "price_source", "rarity", "name", "final_price", "official_price_gp", "amalgamated_price", "price_confidence"]:
        if col not in df.columns:
            df[col] = pd.NA
    return df


def test_engine_floors_match_module():
    """ABSOLUTE_RARITY_FLOORS must mirror pricing_engine.RARITY_FLOORS."""
    assert ABSOLUTE_RARITY_FLOORS == ENGINE_FLOORS


def test_legendary_wondrous_at_5000_clamped_to_8000():
    df = _make_df([{
        "name": "Shard Solitaire",
        "rarity": "legendary",
        "item_type_code": "WD",  # wondrous
        "is_ammunition": False,
        "is_poison": False,
        "price_source": "rule",
        "final_price": 5000.0,
    }])
    adjs = apply_absolute_rarity_floor(df)
    assert len(adjs) == 1
    assert df.loc[0, "final_price"] == pytest.approx(8000, rel=0.01)
    assert adjs[0]["old_price"] == pytest.approx(5000, rel=0.01)
    assert adjs[0]["new_price"] == pytest.approx(8000, rel=0.01)


def test_legendary_grenade_5_clamped_to_8000():
    # Grenades are EXP|DMG / OTH etc, not consumable, must clamp
    df = _make_df([{
        "name": "Concussion Grenade (Legendary)",
        "rarity": "legendary",
        "item_type_code": "EXP|DMG",
        "is_ammunition": False,
        "is_poison": False,
        "price_source": "rule",
        "final_price": 5.0,
    }])
    adjs = apply_absolute_rarity_floor(df)
    assert df.loc[0, "final_price"] == pytest.approx(8000, rel=0.01)


def test_uncommon_wondrous_at_10_clamped_to_50():
    df = _make_df([{
        "name": "Mysterious Wondrous Bauble",
        "rarity": "uncommon",
        "item_type_code": "WD",
        "is_ammunition": False,
        "is_poison": False,
        "price_source": "rule",
        "final_price": 10.0,
    }])
    apply_absolute_rarity_floor(df)
    assert df.loc[0, "final_price"] == pytest.approx(50, rel=0.01)


def test_plus1_arrow_ammunition_unchanged():
    # Ammunition is consumable-modifier exempt even though 34.24 < uncommon floor 50
    df = _make_df([{
        "name": "+1 Arrow",
        "rarity": "uncommon",
        "item_type_code": "A|XPHB",
        "is_ammunition": True,
        "is_poison": False,
        "price_source": "rule",
        "final_price": 34.24,
    }])
    adjs = apply_absolute_rarity_floor(df)
    assert len(adjs) == 0
    assert df.loc[0, "final_price"] == pytest.approx(34.24, rel=0.01)
    # helper should flag as consumable
    assert _is_consumable_modifier_row(df.iloc[0]) is True


def test_potion_of_healing_unchanged():
    # Potion is consumable-modifier exempt (P type + name potion)
    df = _make_df([{
        "name": "Potion of Healing",
        "rarity": "rare",
        "item_type_code": "P|XPHB",
        "is_ammunition": False,
        "is_poison": False,
        "price_source": "rule",
        "final_price": 330.99,
    }])
    adjs = apply_absolute_rarity_floor(df)
    assert len(adjs) == 0
    assert df.loc[0, "final_price"] == pytest.approx(330.99, rel=0.01)
    assert _is_consumable_modifier_row(df.iloc[0]) is True

    # Also verify exemption holds even when potion is below floor: rare potion at 50 (<200) must stay 50
    df2 = _make_df([{
        "name": "Potion of Flying",
        "rarity": "rare",
        "item_type_code": "P|XPHB",
        "is_ammunition": False,
        "is_poison": False,
        "price_source": "rule",
        "final_price": 50.0,
    }])
    adjs2 = apply_absolute_rarity_floor(df2)
    assert len(adjs2) == 0
    assert df2.loc[0, "final_price"] == pytest.approx(50.0, rel=0.01)


def test_scroll_unchanged_when_below_floor():
    df = _make_df([{
        "name": "Scroll of Fireball",
        "rarity": "rare",
        "item_type_code": "SC|XPHB",
        "is_ammunition": False,
        "is_poison": False,
        "price_source": "rule",
        "final_price": 50.0,  # below rare 200
    }])
    adjs = apply_absolute_rarity_floor(df)
    assert len(adjs) == 0
    assert df.loc[0, "final_price"] == pytest.approx(50.0, rel=0.01)
    assert _is_consumable_modifier_row(df.iloc[0]) is True


def test_poison_unchanged_when_below_floor():
    df = _make_df([{
        "name": "Assassin's Blood",
        "rarity": "rare",
        "item_type_code": "G|XPHB",
        "is_ammunition": False,
        "is_poison": True,
        "price_source": "rule",
        "final_price": 10.0,  # below rare 200
    }])
    adjs = apply_absolute_rarity_floor(df)
    assert len(adjs) == 0
    assert df.loc[0, "final_price"] == pytest.approx(10.0, rel=0.01)
    assert _is_consumable_modifier_row(df.iloc[0]) is True


def test_official_commodity_unchanged():
    # official/commodity-exact prices bypass floors entirely
    df = _make_df([{
        "name": "Ball Bearing",
        "rarity": "mundane",
        "item_type_code": "G",
        "is_ammunition": False,
        "is_poison": False,
        "price_source": "official",
        "final_price": 0.01,  # below mundane floor 1, but official -> exempt
        "official_price_gp": 0.01,
    }])
    adjs = apply_absolute_rarity_floor(df)
    assert len(adjs) == 0
    assert df.loc[0, "final_price"] == pytest.approx(0.01, rel=0.01)
    assert _is_official_price_row(df.iloc[0]) is True

    # also verify ball bearing 0.00 stays 0.00 (spec literal)
    df2 = _make_df([{
        "name": "Ball Bearing",
        "rarity": "mundane",
        "item_type_code": "G",
        "is_ammunition": False,
        "is_poison": False,
        "price_source": "official",
        "final_price": 0.0,
    }])
    adjs2 = apply_absolute_rarity_floor(df2)
    assert df2.loc[0, "final_price"] == pytest.approx(0.0, abs=0.001)
    # zero prices are also left alone by the <=0 guard


def test_common_at_10_stays_10():
    df = _make_df([{
        "name": "Common Wondrous Trinket",
        "rarity": "common",
        "item_type_code": "WD",
        "is_ammunition": False,
        "is_poison": False,
        "price_source": "rule",
        "final_price": 10.0,
    }])
    adjs = apply_absolute_rarity_floor(df)
    assert len(adjs) == 0
    assert df.loc[0, "final_price"] == pytest.approx(10, rel=0.01)

    # common below floor should clamp to 10
    df2 = _make_df([{
        "name": "Common Wondrous Trinket 2",
        "rarity": "common",
        "item_type_code": "WD",
        "is_ammunition": False,
        "is_poison": False,
        "price_source": "rule",
        "final_price": 5.0,
    }])
    apply_absolute_rarity_floor(df2)
    assert df2.loc[0, "final_price"] == pytest.approx(10, rel=0.01)


def test_wondrous_and_grenade_do_clamp():
    # Grenades/wondrous are NOT exempt — they must clamp
    for rarity, price, floor in [("legendary", 5000, 8000), ("uncommon", 10, 50), ("rare", 100, 200)]:
        df_w = _make_df([{
            "name": f"Wondrous {rarity} Item",
            "rarity": rarity,
            "item_type_code": "WD",
            "is_ammunition": False,
            "is_poison": False,
            "price_source": "rule",
            "final_price": float(price),
        }])
        apply_absolute_rarity_floor(df_w)
        assert df_w.loc[0, "final_price"] == pytest.approx(floor, rel=0.01)

        df_g = _make_df([{
            "name": f"Grenade {rarity}",
            "rarity": rarity,
            "item_type_code": "EXP|DMG",
            "is_ammunition": False,
            "is_poison": False,
            "price_source": "rule",
            "final_price": float(price),
        }])
        apply_absolute_rarity_floor(df_g)
        assert df_g.loc[0, "final_price"] == pytest.approx(floor, rel=0.01)


def test_weapon_mundane_relative_behavior_unchanged():
    """Weapons/armor still enforce mundane-relative multiplier; absolute floor is additive thereafter."""
    # Build a minimal df with mundane base and a magic variant below mundane-relative floor
    df = pd.DataFrame([
        {"name": "Plate Armor", "rarity": "mundane", "official_price_gp": 1500.0, "final_price": 1500.0, "item_type_code": "HA|XPHB", "is_ammunition": False, "is_poison": False, "price_source": "official"},
        {"name": "+1 Plate Armor", "rarity": "uncommon", "official_price_gp": pd.NA, "final_price": 100.0, "item_type_code": "HA|XPHB", "is_ammunition": False, "is_poison": False, "price_source": "rule", "amalgamated_price": pd.NA, "price_confidence": "none"},
    ])
    # Run mundane-relative logic as the script does
    mundane_prices = find_mundane_prices(df)
    assert mundane_prices.get("Plate Armor") == pytest.approx(1500, rel=0.01)
    base_name, base_price = find_base_item("+1 Plate Armor", mundane_prices)
    assert base_name == "Plate Armor"
    rarity_key = "uncommon"
    min_price = base_price * RARITY_MINIMUMS[rarity_key]  # 1500 * 2.0 = 3000
    assert min_price == pytest.approx(3000, rel=0.01)
    # The mundane-relative clamp would raise 100 -> 3000
    # Now verify absolute floor for uncommon is 50, which is lower, so mundane-relative dominates.
    # Simulate full sequence: mundane clamp then absolute
    df_magic = df.copy()
    # mundane-relative clamp
    for idx, row in df_magic.iterrows():
        if row["rarity"] == "mundane":
            continue
        bn, bp = find_base_item(row["name"], mundane_prices)
        if bn and bp:
            rk = row["rarity"].lower().replace(" ", "_")
            mp = bp * RARITY_MINIMUMS.get(rk, 1.5)
            cur = float(row["final_price"])
            if cur < mp - 0.01:
                df_magic.loc[idx, "final_price"] = round(mp, 2)
    assert df_magic.loc[1, "final_price"] == pytest.approx(3000, rel=0.01)
    # absolute floor should not lower it or raise it further (3000 > 50)
    apply_absolute_rarity_floor(df_magic)
    assert df_magic.loc[1, "final_price"] == pytest.approx(3000, rel=0.01)

    # Also verify a cheap-base weapon where absolute floor exceeds mundane-relative still clamps higher
    # Example: Dagger mundane 2 gp, legendary mundane-relative 2*10=20, but absolute 8000 wins
    df2 = pd.DataFrame([
        {"name": "Dagger", "rarity": "mundane", "official_price_gp": 2.0, "final_price": 2.0, "item_type_code": "M|XPHB", "is_ammunition": False, "is_poison": False, "price_source": "official"},
        {"name": "+3 Dagger", "rarity": "legendary", "official_price_gp": pd.NA, "final_price": 10.0, "item_type_code": "M|XPHB", "is_ammunition": False, "is_poison": False, "price_source": "rule", "amalgamated_price": pd.NA, "price_confidence": "none"},
    ])
    mundane_prices2 = find_mundane_prices(df2)
    bn2, bp2 = find_base_item("+3 Dagger", mundane_prices2)
    assert bn2 == "Dagger"
    # mundane-relative: 2*10=20
    # absolute: 8000
    df2_magic = df2.copy()
    for idx, row in df2_magic.iterrows():
        if row["rarity"] == "mundane":
            continue
        bn, bp = find_base_item(row["name"], mundane_prices2)
        if bn and bp:
            rk = row["rarity"].lower().replace(" ", "_")
            mp = bp * RARITY_MINIMUMS.get(rk, 1.5)
            cur = float(row["final_price"])
            if cur < mp - 0.01:
                df2_magic.loc[idx, "final_price"] = round(mp, 2)
    # after mundane, price is 20 (10 <20 so raised)
    assert df2_magic.loc[1, "final_price"] == pytest.approx(20, rel=0.01)
    # absolute lifts to 8000
    apply_absolute_rarity_floor(df2_magic)
    assert df2_magic.loc[1, "final_price"] == pytest.approx(8000, rel=0.01)


def test_consumable_detection_matches_engine():
    """Verify our row-level consumable detection matches get_consumable_modifier semantics for the four types."""
    from src.pricing_engine import get_consumable_modifier
    # potion via P type
    assert _is_consumable_modifier_row(pd.Series({"name": "Potion of Healing", "item_type_code": "P|XPHB", "is_ammunition": False, "is_poison": False})) is True
    assert get_consumable_modifier({"name": "Potion of Healing", "item_type_code": "P|XPHB", "is_ammunition": False, "is_poison": False, "rarity": "uncommon"}) != 1.0
    # potion via name even if type is G (edge)
    assert _is_consumable_modifier_row(pd.Series({"name": "Potion of Something", "item_type_code": "G", "is_ammunition": False, "is_poison": False})) is True
    # elixir
    assert _is_consumable_modifier_row(pd.Series({"name": "Elixir of Health", "item_type_code": "P|XPHB", "is_ammunition": False, "is_poison": False})) is True
    # scroll
    assert _is_consumable_modifier_row(pd.Series({"name": "Scroll of Fireball", "item_type_code": "SC|XPHB", "is_ammunition": False, "is_poison": False})) is True
    assert get_consumable_modifier({"name": "Scroll of Fireball", "item_type_code": "SC|XPHB", "is_ammunition": False, "is_poison": False}) != 1.0
    # ammunition
    assert _is_consumable_modifier_row(pd.Series({"name": "+1 Arrow", "item_type_code": "A|XPHB", "is_ammunition": True, "is_poison": False})) is True
    assert get_consumable_modifier({"name": "+1 Arrow", "item_type_code": "A|XPHB", "is_ammunition": True, "is_poison": False}) != 1.0
    # poison
    assert _is_consumable_modifier_row(pd.Series({"name": "Basic Poison", "item_type_code": "G|XPHB", "is_ammunition": False, "is_poison": True})) is True
    assert get_consumable_modifier({"name": "Basic Poison", "item_type_code": "G|XPHB", "is_ammunition": False, "is_poison": True}) != 1.0
    # grenade not consumable
    assert _is_consumable_modifier_row(pd.Series({"name": "Concussion Grenade", "item_type_code": "EXP|DMG", "is_ammunition": False, "is_poison": False})) is False
    # wondrous not consumable
    assert _is_consumable_modifier_row(pd.Series({"name": "Shard Solitaire", "item_type_code": "WD", "is_ammunition": False, "is_poison": False})) is False
    # SCF focus not scroll
    assert _is_consumable_modifier_row(pd.Series({"name": "Arcane Focus", "item_type_code": "SCF|XPHB", "is_ammunition": False, "is_poison": False})) is False


def test_official_bypasses_even_when_below_floor():
    """Official items are never clamped, even far below floor."""
    df = _make_df([{
        "name": "Cheap Official Trinket",
        "rarity": "legendary",
        "item_type_code": "WD",
        "is_ammunition": False,
        "is_poison": False,
        "price_source": "official",
        "final_price": 5.0,
    }])
    adjs = apply_absolute_rarity_floor(df)
    assert len(adjs) == 0
    assert df.loc[0, "final_price"] == pytest.approx(5.0, rel=0.01)
    # same for mundane official commodity far below 1
    df2 = _make_df([{
        "name": "Candle",
        "rarity": "mundane",
        "item_type_code": "G",
        "is_ammunition": False,
        "is_poison": False,
        "price_source": "official",
        "final_price": 0.01,
    }])
    adjs2 = apply_absolute_rarity_floor(df2)
    assert len(adjs2) == 0
    assert df2.loc[0, "final_price"] == pytest.approx(0.01, rel=0.01)
