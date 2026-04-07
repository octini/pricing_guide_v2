# tests/test_criteria_extractor.py
import json
import pytest
from src.criteria_extractor import extract_structured_criteria

def make_item(**kwargs):
    """Helper: build a minimal item dict."""
    base = {"name": "Test Item", "source": "PHB", "rarity": "rare"}
    base.update(kwargs)
    return base

def test_weapon_bonus_string():
    item = make_item(bonusWeapon="+2")
    c = extract_structured_criteria(item)
    assert c["weapon_bonus"] == 2

def test_weapon_bonus_int():
    item = make_item(bonusWeapon=1)
    c = extract_structured_criteria(item)
    assert c["weapon_bonus"] == 1

def test_ac_bonus():
    item = make_item(bonusAc="+1")
    c = extract_structured_criteria(item)
    assert c["ac_bonus"] == 1

def test_req_attune_open():
    item = make_item(reqAttune=True)
    c = extract_structured_criteria(item)
    assert c["req_attune"] == "open"
    assert c["req_attune_class"] is None

def test_req_attune_class_restricted():
    item = make_item(reqAttune="by a wizard")
    c = extract_structured_criteria(item)
    assert c["req_attune"] == "class"
    assert "wizard" in c["req_attune_class"]

def test_no_attune():
    item = make_item()
    c = extract_structured_criteria(item)
    assert c["req_attune"] == "none"

def test_is_sentient():
    item = make_item(sentient=True)
    c = extract_structured_criteria(item)
    assert c["is_sentient"] is True

def test_is_cursed():
    item = make_item(curse=True)
    c = extract_structured_criteria(item)
    assert c["is_cursed"] is True

def test_spell_scroll_level():
    item = make_item(spellScrollLevel=3)
    c = extract_structured_criteria(item)
    assert c["spell_scroll_level"] == 3

def test_damage_resistances():
    item = make_item(resist=["fire", "cold"])
    c = extract_structured_criteria(item)
    assert c["damage_resistances"] == ["fire", "cold"]

def test_charges():
    item = make_item(charges=7)
    c = extract_structured_criteria(item)
    assert c["charges"] == 7

def test_is_ammunition():
    item = make_item(type="A")
    c = extract_structured_criteria(item)
    assert c["is_ammunition"] is True

def test_is_wondrous():
    item = make_item(wondrous=True)
    c = extract_structured_criteria(item)
    assert c["is_wondrous"] is True

def test_tattoo():
    item = make_item(tattoo=True)
    c = extract_structured_criteria(item)
    assert c["is_tattoo"] is True

# NLP prose criteria tests
from src.criteria_extractor import extract_prose_criteria

def test_flight_full():
    desc = "While wearing this cloak, you have a flying speed of 30 feet."
    c = extract_prose_criteria(desc)
    assert c["flight_full"] is True
    assert c["flight_limited"] is False

def test_flight_limited():
    desc = "You can use an action to fly for up to 1 minute."
    c = extract_prose_criteria(desc)
    assert c["flight_full"] is False
    assert c["flight_limited"] is True

def test_darkvision():
    desc = "You gain darkvision out to a range of 60 feet."
    c = extract_prose_criteria(desc)
    assert c["darkvision_feet"] == 60

def test_truesight():
    desc = "You gain truesight out to a range of 30 feet."
    c = extract_prose_criteria(desc)
    assert c["truesight"] is True

def test_teleportation():
    desc = "As an action, you can teleport to any unoccupied space."
    c = extract_prose_criteria(desc)
    assert c["teleportation"] is True

def test_invisibility_at_will():
    desc = "As an action, you become invisible until you attack."
    c = extract_prose_criteria(desc)
    assert c["invisibility_atwill"] is True

def test_healing_consumable():
    desc = "You regain 2d4+2 hit points when you drink this potion."
    c = extract_prose_criteria(desc)
    assert c["healing_consumable_avg"] > 0

def test_healing_daily():
    desc = "At dawn, you regain 10 hit points."
    c = extract_prose_criteria(desc)
    assert c["healing_daily_hp"] == 10

def test_tome_manual():
    desc = "This tome contains wisdom and insight. After 48 hours of study, your Wisdom score increases by 2."
    c = extract_prose_criteria(desc)
    assert c["tome_manual_boost"] is True

def test_concentration_free():
    desc = "This effect doesn't require concentration."
    c = extract_prose_criteria(desc)
    assert c["concentration_free"] is True

def test_crit_immunity():
    desc = "While you wear this armor, critical hits against you are treated as normal hits."
    c = extract_prose_criteria(desc)
    assert c["crit_immunity"] is True
