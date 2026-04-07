# tests/test_utils.py
import pytest
from src.utils import normalize_item_name, parse_value_cp, get_5etools_url

def test_normalize_item_name_lowercase():
    assert normalize_item_name("Sword of FIRE") == "sword of fire"

def test_normalize_item_name_strips_plus():
    assert normalize_item_name("+1 Longsword") == "longsword +1"

def test_normalize_item_name_strips_punctuation():
    assert normalize_item_name("Bag of Holding (Type I)") == "bag of holding type i"

def test_parse_value_cp_converts_to_gp():
    # value field is in copper pieces; 100 cp = 1 gp
    assert parse_value_cp(5000) == 50.0

def test_parse_value_cp_none_returns_none():
    assert parse_value_cp(None) is None

def test_parse_value_cp_zero_returns_none():
    assert parse_value_cp(0) is None

def test_get_5etools_url_basic():
    url = get_5etools_url("Longsword", "PHB")
    assert url == "https://5e.tools/items.html#longsword_phb"

def test_get_5etools_url_spaces():
    url = get_5etools_url("Bag of Holding", "DMG")
    assert url == "https://5e.tools/items.html#bag%20of%20holding_dmg"
