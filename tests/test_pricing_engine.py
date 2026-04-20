# tests/test_pricing_engine.py
"""Tests for rule-based pricing engine.

Constants updated to match calibrated values from oracle review (2026-04-07).
Base prices and additives were reduced ~3-10× to match real-world guide data.
"""
import pytest
from src.pricing_engine import calculate_price, RARITY_BASE_PRICES, RARITY_FLOORS


def make_criteria(rarity="rare", **kwargs):
    """Build minimal criteria dict for testing."""
    defaults = {
        "rarity": rarity,
        "req_attune": "none",
        "req_attune_class": None,
        "item_type_code": "",
        "is_ammunition": False,
        "spell_scroll_level": None,
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
        "damage_resistances": [],
        "damage_immunities": [],
        "condition_immunities": [],
        "speed_mods": {},
        "is_sentient": False,
        "is_cursed": False,
        "is_tattoo": False,
        "is_wondrous": False,
        "is_shield": False,
        "is_poison": False,
        "is_firearm": False,
        "attached_spells": [],
        "charges": None,
        "recharge": None,
        "stealth_penalty": False,
        "ability_score_mods": [],
        "official_price_gp": None,
        # NLP fields
        "flight_full": False,
        "flight_limited": False,
        "darkvision_feet": 0,
        "truesight": False,
        "blindsight": False,
        "tremorsense": False,
        "teleportation": False,
        "invisibility_atwill": False,
        "healing_daily_hp": 0,
        "healing_consumable_avg": 0.0,
        "healing_permanent_hp": 0,
        "tome_manual_boost": False,
        "concentration_free": False,
        "crit_immunity": False,
        "wish_effect": False,
        "stealth_advantage": False,
        "swim_speed": False,
        "climb_speed": False,
        "burrow_speed": False,
    }
    defaults.update(kwargs)
    return defaults


def test_base_rare_price():
    """Plain rare item with no bonuses."""
    c = make_criteria(rarity="rare")
    price = calculate_price(c)
    assert price == RARITY_BASE_PRICES["rare"]  # 4000


def test_rare_with_attunement():
    """Rare item with open attunement: 4000 * 0.90 = 3600."""
    c = make_criteria(rarity="rare", req_attune="open")
    price = calculate_price(c)
    assert price == pytest.approx(4000 * 0.90, rel=0.01)


def test_rare_with_class_attunement():
    """Rare item with class-restricted attunement: 4000 * 0.80 = 3200."""
    c = make_criteria(rarity="rare", req_attune="class")
    price = calculate_price(c)
    assert price == pytest.approx(4000 * 0.80, rel=0.01)


def test_weapon_bonus_plus1():
    """Rare weapon +1 (simple bonus path): 725 * (4000/4000) = 725."""
    c = make_criteria(rarity="rare", weapon_bonus=1)
    price = calculate_price(c)
    assert price == pytest.approx(725, rel=0.01)


def test_weapon_bonus_plus3():
    """Rare weapon +3 (simple bonus path): 14950 * (4000/4000) = 14950."""
    c = make_criteria(rarity="rare", weapon_bonus=3)
    price = calculate_price(c)
    assert price == pytest.approx(14950, rel=0.01)


def test_ac_bonus_plus2():
    """Rare armor +2 AC: 4000 + 4000 = 8000."""
    c = make_criteria(rarity="rare", ac_bonus=2)
    price = calculate_price(c)
    assert price == pytest.approx(8000, rel=0.01)


def test_cursed_item():
    """Cursed rare item: 4000 * 0.75 = 3000."""
    c = make_criteria(rarity="rare", is_cursed=True)
    price = calculate_price(c)
    assert price == pytest.approx(4000 * 0.75, rel=0.01)


def test_sentient_item():
    """Sentient rare item: 4000 * 1.15 = 4600."""
    c = make_criteria(rarity="rare", is_sentient=True)
    price = calculate_price(c)
    assert price == pytest.approx(4000 * 1.15, rel=0.01)


def test_spell_scroll_level_3():
    """Level 3 scroll = 300 gp."""
    c = make_criteria(rarity="uncommon", spell_scroll_level=3)
    price = calculate_price(c)
    assert price == pytest.approx(300, rel=0.01)


def test_floor_applied():
    """Cursed common item should not go below floor."""
    c = make_criteria(rarity="common", is_cursed=True)
    price = calculate_price(c)
    assert price >= RARITY_FLOORS["common"]


def test_official_price_used_directly():
    """Items with official prices bypass formula."""
    c = make_criteria(rarity="mundane", official_price_gp=15.0)
    price = calculate_price(c)
    assert price == 15.0


def test_flight_full_bonus():
    """Flight (full) adds 10000 gp to rare base of 4000 = 14000."""
    c = make_criteria(rarity="rare", flight_full=True)
    price = calculate_price(c)
    assert price == pytest.approx(4000 + 10000, rel=0.01)


def test_teleportation_bonus():
    """Teleportation adds 5000 gp to very_rare base of 13500 = 18500."""
    c = make_criteria(rarity="very_rare", teleportation=True)
    price = calculate_price(c)
    assert price == pytest.approx(13500 + 5000, rel=0.01)


def test_damage_resistance():
    """Each resistance adds 300 gp; two resistances on rare = 4000 + 600 = 4600."""
    c = make_criteria(rarity="rare", damage_resistances=["fire", "cold"])
    price = calculate_price(c)
    assert price == pytest.approx(4000 + 600, rel=0.01)


def test_potion_consumable_discount():
    """Potions (type 'P') get flat 0.50 discount. Rare potion: 4000 * 0.50 = 2000."""
    c = make_criteria(rarity="rare", item_type_code="P")
    price = calculate_price(c)
    assert price == pytest.approx(4000 * 0.50, rel=0.01)


def test_scroll_consumable_discount():
    """Scrolls (type 'SC') get 0.70 discount. Very rare scroll: 13500 * 0.70 = 9450."""
    c = make_criteria(rarity="very_rare", item_type_code="SC")
    price = calculate_price(c)
    assert price == pytest.approx(13500 * 0.70, rel=0.01)


def test_poison_consumable_discount():
    """Poisons get 0.60 discount. Rare poison: 4000 * 0.60 = 2400."""
    c = make_criteria(rarity="rare", is_poison=True)
    price = calculate_price(c)
    assert price == pytest.approx(4000 * 0.60, rel=0.01)


# --- Rarity-scaled additive bonus tests ---


def test_common_weapon_bonus_scales_by_rarity():
    """Common +1 weapon (simple path): uses amalgamated price 725."""
    c = make_criteria(rarity="common", weapon_bonus=1)
    price = calculate_price(c)
    assert price == pytest.approx(725, rel=0.01)


def test_legendary_weapon_bonus_scales_by_rarity():
    """Legendary +1 weapon (simple path): 725 floored to legendary floor 8000."""
    c = make_criteria(rarity="legendary", weapon_bonus=1)
    price = calculate_price(c)
    assert price == pytest.approx(8000, rel=0.01)


def test_rare_ac_bonus_keeps_existing_anchor():
    """Rare +2 AC: 4000 + 4000*(4000/4000) = 8000 (unchanged)."""
    c = make_criteria(rarity="rare", ac_bonus=2)
    price = calculate_price(c)
    assert price == pytest.approx(8000, rel=0.01)
