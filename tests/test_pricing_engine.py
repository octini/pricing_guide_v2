# tests/test_pricing_engine.py
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
    assert price == 20000

def test_rare_with_attunement():
    """Rare item with open attunement: 20000 * 0.85 = 17000."""
    c = make_criteria(rarity="rare", req_attune="open")
    price = calculate_price(c)
    assert price == pytest.approx(17000, rel=0.01)

def test_rare_with_class_attunement():
    """Rare item with class-restricted attunement: 20000 * 0.75 = 15000."""
    c = make_criteria(rarity="rare", req_attune="class")
    price = calculate_price(c)
    assert price == pytest.approx(15000, rel=0.01)

def test_weapon_bonus_plus1():
    """Rare weapon +1 bonus: 20000 + 10000 = 30000."""
    c = make_criteria(rarity="rare", weapon_bonus=1)
    price = calculate_price(c)
    assert price == pytest.approx(30000, rel=0.01)

def test_weapon_bonus_plus3():
    """Rare weapon +3 bonus: 20000 + 200000 = 220000."""
    c = make_criteria(rarity="rare", weapon_bonus=3)
    price = calculate_price(c)
    assert price == pytest.approx(220000, rel=0.01)

def test_ac_bonus_plus2():
    """Rare armor +2 AC: 20000 + 40000 = 60000."""
    c = make_criteria(rarity="rare", ac_bonus=2)
    price = calculate_price(c)
    assert price == pytest.approx(60000, rel=0.01)

def test_cursed_item():
    """Cursed rare item: 20000 * 0.70 = 14000."""
    c = make_criteria(rarity="rare", is_cursed=True)
    price = calculate_price(c)
    assert price == pytest.approx(14000, rel=0.01)

def test_sentient_item():
    """Sentient rare item: 20000 * 1.25 = 25000."""
    c = make_criteria(rarity="rare", is_sentient=True)
    price = calculate_price(c)
    assert price == pytest.approx(25000, rel=0.01)

def test_spell_scroll_level_3():
    """Level 3 scroll = 300 gp."""
    c = make_criteria(rarity="uncommon", spell_scroll_level=3)
    price = calculate_price(c)
    assert price == pytest.approx(300, rel=0.01)

def test_floor_applied():
    """Cursed common item should not go below floor (50 gp)."""
    c = make_criteria(rarity="common", is_cursed=True)
    price = calculate_price(c)
    assert price >= RARITY_FLOORS["common"]

def test_official_price_used_directly():
    """Items with official prices bypass formula."""
    c = make_criteria(rarity="mundane", official_price_gp=15.0)
    price = calculate_price(c)
    assert price == 15.0

def test_flight_full_bonus():
    """Flight adds 15000 gp."""
    c = make_criteria(rarity="rare", flight_full=True)
    price = calculate_price(c)
    assert price == pytest.approx(35000, rel=0.01)  # 20000 + 15000

def test_teleportation_bonus():
    """Teleportation adds 20000 gp."""
    c = make_criteria(rarity="very_rare", teleportation=True)
    price = calculate_price(c)
    assert price == pytest.approx(120000, rel=0.01)  # 100000 + 20000

def test_damage_resistance():
    """Each resistance adds 2000 gp."""
    c = make_criteria(rarity="rare", damage_resistances=["fire", "cold"])
    price = calculate_price(c)
    assert price == pytest.approx(24000, rel=0.01)  # 20000 + 4000
