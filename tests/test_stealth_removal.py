# tests/test_stealth_removal.py
"""Stealth-disadvantage removal pricing (option D, 400 gp parity with stealth_advantage)."""
import math
import pandas as pd
from src.pricing_engine import calculate_price, STEALTH_REMOVAL_RATE


def _base_armor_criteria(stealth_penalty=True, resistances=None, name="Chain Mail", item_type="HA|XPHB"):
    return {
        "rarity": "rare",
        "req_attune": "none",
        "name": name,
        "item_type_code": item_type,
        "weapon_bonus": None,
        "weapon_attack_bonus": None,
        "weapon_damage_bonus": None,
        "ac_bonus": None,
        "saving_throw_bonus": None,
        "ability_check_bonus": None,
        "proficiency_bonus_mod": None,
        "spell_attack_bonus": None,
        "spell_save_dc_bonus": None,
        "spell_damage_bonus": None,
        "damage_resistances": resistances if resistances is not None else [],
        "damage_immunities": [],
        "condition_immunities": [],
        "speed_mods": {},
        "is_sentient": False,
        "is_cursed": False,
        "is_focus": False,
        "charges": None,
        "recharge": None,
        "official_price_gp": None,
        "amalgamated_price": None,
        "price_confidence": "none",
        "extra_damage_avg": 0,
        "dsa_price": None,
        "msrp_price": None,
        "dmpg_price": None,
        "price_sources": None,
        "material": None,
        "is_ammunition": False,
        "is_shield": False,
        "stealth_penalty": stealth_penalty,
        "stealth_advantage": False,
        "ability_score_mods": [],
        "spell_scroll_level": None,
        "attached_spells": [],
        "tome_manual_boost": False,
        "wish_effect": False,
        "flight_full": False,
        "flight_limited": False,
        "teleportation": False,
        "invisibility_atwill": False,
        "healing_daily_hp": 0,
        "healing_consumable_avg": 0.0,
        "temp_hp_avg": 0.0,
        "temp_hp_frequency": None,
        "hp_max_flat": 0,
        "hp_max_per_level": 0,
        "initiative_bonus": 0,
        "initiative_advantage": False,
    }


def test_stealth_removal_adds_400_over_identical_armor():
    base_without = _base_armor_criteria(stealth_penalty=True, name="Chain Mail", item_type="HA|XPHB")
    base_with = _base_armor_criteria(stealth_penalty=False, name="Chain Mail", item_type="HA|XPHB")
    price_without = calculate_price(base_without)
    price_with = calculate_price(base_with)
    assert STEALTH_REMOVAL_RATE == 400
    assert price_with == price_without + 400, f"expected +400, got {price_with} vs {price_without} diff={price_with-price_without}"


def test_stealth_removal_additive_on_top_of_resistance():
    # Resistance pricing is 300 per type; removal should be additive on top
    without = _base_armor_criteria(stealth_penalty=True, resistances=["poison"], name="Chain Mail")
    with_ = _base_armor_criteria(stealth_penalty=False, resistances=["poison"], name="Chain Mail")
    # Also check vs no-resistance baseline
    bare_without = _base_armor_criteria(stealth_penalty=True, resistances=[], name="Chain Mail")
    bare_with = _base_armor_criteria(stealth_penalty=False, resistances=[], name="Chain Mail")
    # Resistance alone should be +300
    assert calculate_price(without) == calculate_price(bare_without) + 300
    # Removal alone should be +400
    assert calculate_price(bare_with) == calculate_price(bare_without) + 400
    # Both together should be +700 vs bare without
    assert calculate_price(with_) == calculate_price(bare_without) + 700
    # And +400 vs resistance-only without removal
    assert calculate_price(with_) == calculate_price(without) + 400


def test_stealth_removal_na_absent_safety():
    base = _base_armor_criteria(stealth_penalty=True, name="Chain Mail")
    base_price = calculate_price(base)
    for na_val in [pd.NA, float("nan"), None]:
        c = dict(base)
        c["stealth_penalty"] = na_val
        price = calculate_price(c)
        # NA/None should be treated as no removal (same as penalty present) and not raise
        assert isinstance(price, (int, float))
        assert not math.isnan(price)
        assert price == base_price, f"NA value {na_val!r} changed price {price} vs {base_price}"
    # Absent key
    c = dict(base)
    c.pop("stealth_penalty", None)
    price = calculate_price(c)
    assert isinstance(price, (int, float))
    assert not math.isnan(price)
    assert price == base_price
    # String encodings
    for s, should_be_removal in [("False", True), ("false", True), ("True", False), ("true", False)]:
        c = dict(base)
        c["stealth_penalty"] = s
        # Need HA type to trigger removal; string logic mirrors bool
        price_s = calculate_price(c)
        expected = base_price + (400 if should_be_removal else 0)
        # For HA, "False" string means no penalty => removal => +400
        assert price_s == expected, f"string {s!r} price {price_s} vs expected {expected}"


def test_stealth_removal_only_for_heavy_or_disadvantaged_medium():
    base_ha_true = _base_armor_criteria(stealth_penalty=True, name="Chain Mail", item_type="HA|XPHB")
    base_ha_false = _base_armor_criteria(stealth_penalty=False, name="Chain Mail", item_type="HA|XPHB")
    assert calculate_price(base_ha_false) == calculate_price(base_ha_true) + 400

    # Light armor (LA) natural False should NOT get removal
    la_true = _base_armor_criteria(stealth_penalty=True, name="Leather Armor", item_type="LA|XPHB")
    la_false = _base_armor_criteria(stealth_penalty=False, name="Leather Armor", item_type="LA|XPHB")
    # LA false is natural no-penalty, not removal; both should price same (0 extra)
    # Our logic returns False for LA, so no diff
    assert calculate_price(la_false) == calculate_price(la_true)

    # MA natural False (Breastplate) should NOT get removal
    ma_breast_false = _base_armor_criteria(stealth_penalty=False, name="Breastplate", item_type="MA|XPHB")
    ma_breast_true = _base_armor_criteria(stealth_penalty=True, name="Breastplate", item_type="MA|XPHB")
    # Breastplate is MA but not disadvantaged base, so removal not triggered even with False
    assert calculate_price(ma_breast_false) == calculate_price(ma_breast_true)

    # MA disadvantaged (Half Plate) False SHOULD get removal
    ma_half_false = _base_armor_criteria(stealth_penalty=False, name="Half Plate Armor", item_type="MA|XPHB")
    ma_half_true = _base_armor_criteria(stealth_penalty=True, name="Half Plate Armor", item_type="MA|XPHB")
    assert calculate_price(ma_half_false) == calculate_price(ma_half_true) + 400


def test_stealth_removal_simple_item_forcing():
    # Stealth removal on a +1 armor-like item should force the full formula (non-simple),
    # otherwise the 400 gp term would be skipped via the simple +N path.
    c_removal = _base_armor_criteria(stealth_penalty=False, name="Chain Mail", item_type="HA|XPHB")
    c_removal["weapon_bonus"] = 1
    c_penalty = dict(c_removal)
    c_penalty["stealth_penalty"] = True
    # Without removal, the item is simple (+1) -> 725 gp path (rare base not used)
    assert calculate_price(c_penalty) == 725
    # With removal, must bypass simple path and price via formula (base + item cost + removal)
    price_removal = calculate_price(c_removal)
    assert price_removal != 725
    assert price_removal > calculate_price(c_penalty)
    # The removal term must be present in the formula price; check additive gap vs
    # an equivalent non-weapon armor (which is already non-simple) to isolate 400
    armor_removal = _base_armor_criteria(stealth_penalty=False, name="Chain Mail", item_type="HA|XPHB")
    armor_penalty = _base_armor_criteria(stealth_penalty=True, name="Chain Mail", item_type="HA|XPHB")
    assert calculate_price(armor_removal) == calculate_price(armor_penalty) + 400
