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
