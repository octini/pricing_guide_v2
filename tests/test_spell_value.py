"""Tests for spell value calculation in pricing_engine."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pricing_engine import calculate_spell_value


def test_list_format_unlimited():
    value = calculate_spell_value(["fireball", "invisibility"])
    expected = (3 ** 2 * 500 * 2.0) + (2 ** 2 * 500 * 2.0)
    assert value == expected, f"Expected {expected}, got {value}"


def test_daily_format():
    value = calculate_spell_value({"daily": {"1": ["fireball"]}})
    expected = 3 ** 2 * 500 * 1.5 * 1
    assert value == expected, f"Expected {expected}, got {value}"


def test_charges_format_with_frequency():
    value = calculate_spell_value({"charges": {"3": ["fireball"]}})
    expected = 3 ** 2 * 500 * 1.0 * 3
    assert value == expected, f"Expected {expected}, got {value}"


def test_will_format_at_will():
    value = calculate_spell_value({"will": ["thunderwave"]})
    expected = 1 ** 2 * 500 * 3.0
    assert value == expected, f"Expected {expected}, got {value}"


def test_multiple_usage_types():
    value = calculate_spell_value({
        "will": ["scrying"],
        "daily": {"1e": ["suggestion"]}
    })
    expected = (5 ** 2 * 500 * 3.0) + (2 ** 2 * 500 * 1.5 * 1)
    assert value == expected, f"Expected {expected}, got {value}"


def test_empty_attached_spells():
    assert calculate_spell_value(None) == 0.0
    assert calculate_spell_value([]) == 0.0
    assert calculate_spell_value({}) == 0.0


def test_skips_non_usage_keys():
    value = calculate_spell_value({
        "ability": {"choose": ["int", "wis", "cha"]}
    })
    assert value == 0.0


def test_adze_of_annam_example():
    value = calculate_spell_value({"daily": {"1": ["fabricate", "move earth"]}})
    expected = (4 ** 2 * 500 * 1.5 * 1) + (6 ** 2 * 500 * 1.5 * 1)
    assert value == expected, f"Expected {expected}, got {value}"


if __name__ == "__main__":
    test_list_format_unlimited()
    test_daily_format()
    test_charges_format_with_frequency()
    test_will_format_at_will()
    test_multiple_usage_types()
    test_empty_attached_spells()
    test_skips_non_usage_keys()
    test_adze_of_annam_example()
    print("All tests passed!")
