# tests/test_wave1_criteria.py
"""Wave-1 criteria extraction tests: temp HP, HP-max, initiative."""
import pytest
from src.criteria_extractor import extract_prose_criteria


def test_temp_hp_on_kill():
    desc = "When you reduce the target to 0 hit points, you gain 2d6 temporary hit points."
    c = extract_prose_criteria(desc)
    assert c["temp_hp_avg"] == pytest.approx(7.0)
    assert c["temp_hp_frequency"] == "on_kill"


def test_temp_hp_per_action():
    desc = "You can use an action to give yourself 1d4 + 4 temporary hit points."
    c = extract_prose_criteria(desc)
    # 1d4 avg 2.5 + 4 = 6.5; spec lists 6.0 but true dice avg is 6.5
    assert c["temp_hp_avg"] == pytest.approx(6.5)
    assert c["temp_hp_frequency"] == "per_action"


def test_temp_hp_daily():
    desc = "Once per dawn, you gain 5 temporary hit points."
    c = extract_prose_criteria(desc)
    assert c["temp_hp_avg"] == pytest.approx(5.0)
    assert c["temp_hp_frequency"] == "daily"


def test_temp_hp_daily_each_dawn_variant():
    desc = "Each dawn you gain 5 temporary hit points."
    c = extract_prose_criteria(desc)
    assert c["temp_hp_frequency"] == "daily"


def test_hp_max_flat():
    desc = "Your hit point maximum increases by 20."
    c = extract_prose_criteria(desc)
    assert c["hp_max_flat"] == 20
    assert c["hp_max_per_level"] == 0


def test_hp_max_per_level_equal_plus_level():
    desc = "Your hit point maximum increases by an amount equal to 10 + your level."
    c = extract_prose_criteria(desc)
    assert c["hp_max_per_level"] == 10
    assert c["hp_max_flat"] == 0


def test_hp_max_per_level_for_each_level():
    desc = "Your hit point maximum increases by 1 for each level you have attained."
    c = extract_prose_criteria(desc)
    assert c["hp_max_per_level"] == 1


def test_initiative_bonus():
    desc = "You gain a +2 bonus to initiative."
    c = extract_prose_criteria(desc)
    assert c["initiative_bonus"] == 2
    assert c["initiative_advantage"] is False


def test_initiative_bonus_negative():
    desc = "You have a -1 bonus to initiative when cursed."
    c = extract_prose_criteria(desc)
    assert c["initiative_bonus"] == -1


def test_initiative_advantage():
    desc = "You have advantage on initiative rolls."
    c = extract_prose_criteria(desc)
    assert c["initiative_advantage"] is True


def test_initiative_advantage_all_variant():
    desc = "You have advantage on all initiative rolls."
    c = extract_prose_criteria(desc)
    assert c["initiative_advantage"] is True


def test_healing_not_misread_as_temp_hp():
    desc = "You regain 2d6 hit points at dawn."
    c = extract_prose_criteria(desc)
    assert c["temp_hp_avg"] == pytest.approx(0.0)
    assert c["temp_hp_frequency"] is None
    # Should be classified as daily healing, not temp HP
    assert c["healing_daily_hp"] == 7


def test_temp_hp_does_not_trigger_healing():
    desc = "You gain 5 temporary hit points when you reduce a creature to 0 hit points."
    c = extract_prose_criteria(desc)
    assert c["temp_hp_avg"] == pytest.approx(5.0)
    assert c["healing_daily_hp"] == 0
    assert c["healing_consumable_avg"] == pytest.approx(0.0)


def test_temp_hp_unclassified_frequency():
    desc = "You gain 5 temporary hit points."
    c = extract_prose_criteria(desc)
    assert c["temp_hp_avg"] == pytest.approx(5.0)
    assert c["temp_hp_frequency"] == "unclassified"


def test_temp_hp_keeps_max_avg():
    desc = "You gain 5 temporary hit points. Later you gain 2d6 temporary hit points when you reduce the target to 0 hit points."
    c = extract_prose_criteria(desc)
    # Max is 7.0 vs 5.0, should keep 7.0 and classify using the 2d6 occurrence's window (on_kill)
    assert c["temp_hp_avg"] == pytest.approx(7.0)
    assert c["temp_hp_frequency"] == "on_kill"


def test_init_defaults_when_absent():
    c = extract_prose_criteria("A plain cloak with no magical properties.")
    assert c["temp_hp_avg"] == pytest.approx(0.0)
    assert c["temp_hp_frequency"] is None
    assert c["hp_max_flat"] == 0
    assert c["hp_max_per_level"] == 0
    assert c["initiative_bonus"] == 0
    assert c["initiative_advantage"] is False
