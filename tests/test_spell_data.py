"""Tests for spell_data module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.spell_data import get_spell_level, normalize_spell_name


def test_normalize_spell_name():
    assert normalize_spell_name("fireball") == "fireball"
    assert normalize_spell_name("fireball|xphb") == "fireball"
    assert normalize_spell_name("thunderwave#4") == "thunderwave"
    assert normalize_spell_name("FireBall") == "fireball"


def test_get_spell_level_known_spells():
    assert get_spell_level("fireball") == 3
    assert get_spell_level("wish") == 9
    assert get_spell_level("fabricate") == 4
    assert get_spell_level("move earth") == 6
    assert get_spell_level("invisibility") == 2


def test_get_spell_level_with_suffixes():
    assert get_spell_level("fireball|xphb") == 3
    assert get_spell_level("wish|xphb") == 9


def test_get_spell_level_unknown_defaults_to_1():
    assert get_spell_level("unknown spell name") == 1


if __name__ == "__main__":
    test_normalize_spell_name()
    test_get_spell_level_known_spells()
    test_get_spell_level_with_suffixes()
    test_get_spell_level_unknown_defaults_to_1()
    print("All tests passed!")
