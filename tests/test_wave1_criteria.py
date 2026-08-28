# tests/test_wave1_criteria.py
"""Wave-1 criteria extraction tests: temp HP, HP-max, initiative."""
import math
import pytest
import pandas as pd
from src.criteria_extractor import extract_prose_criteria
from src.pricing_engine import calculate_price


def test_temp_hp_on_kill():
    desc = "When you reduce the target to 0 hit points, you gain 2d6 temporary hit points."
    c = extract_prose_criteria(desc)
    assert c["temp_hp_avg"] == pytest.approx(7.0)
    assert c["temp_hp_frequency"] == "on_kill"


def test_temp_hp_on_kill_inflections():
    for verb in ["reduce", "reduces", "reduced"]:
        desc = f"When you {verb} the target to 0 hit points, you gain 5 temporary hit points."
        c = extract_prose_criteria(desc)
        assert c["temp_hp_frequency"] == "on_kill", f"failed for verb {verb}"


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


def test_temp_hp_daily_next_dawn_and_once_a_day():
    for phrase in ["next dawn", "once a day"]:
        desc = f"{phrase}, you gain 5 temporary hit points."
        c = extract_prose_criteria(desc)
        assert c["temp_hp_frequency"] == "daily", f"daily marker {phrase} failed"
    # Capitalized variant
    c = extract_prose_criteria("Next dawn, you gain 5 temporary hit points.")
    assert c["temp_hp_frequency"] == "daily"


def test_temp_hp_daily_capped_kill_effect_is_daily():
    # Single sentence containing both kill and daily — daily precedence
    desc = "When you reduce the target to 0 hit points, you gain 5 temporary hit points once per dawn."
    c = extract_prose_criteria(desc)
    assert c["temp_hp_frequency"] == "daily"


def test_temp_hp_adjacent_unrelated_action_does_not_flip_daily():
    desc = "Once per dawn, you gain 5 temporary hit points. You can use an action to attack."
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
    # Correct encoding: flat N, per_level 1 (not per_level 10)
    assert c["hp_max_flat"] == 10
    assert c["hp_max_per_level"] == 1


def test_hp_max_per_level_equal_plus_level_without_amount_prefix():
    desc = "Your hit point maximum increases by 10 + your level."
    c = extract_prose_criteria(desc)
    assert c["hp_max_flat"] == 10
    assert c["hp_max_per_level"] == 1


def test_hp_max_per_level_for_each_level():
    desc = "Your hit point maximum increases by 1 for each level you have attained."
    c = extract_prose_criteria(desc)
    assert c["hp_max_per_level"] == 1
    assert c["hp_max_flat"] == 0


def test_hp_max_flat_dice_1d4():
    desc = "Your hit point maximum increases by 1d4."
    c = extract_prose_criteria(desc)
    assert c["hp_max_flat"] == pytest.approx(2.5)
    assert c["hp_max_per_level"] == 0


def test_hp_max_flat_dice_2d10_plus_4():
    desc = "Your hit point maximum increases by 2d10 + 4."
    c = extract_prose_criteria(desc)
    assert c["hp_max_flat"] == pytest.approx(15.0)
    assert c["hp_max_per_level"] == 0


def test_hp_max_flat_amount_equal_standalone():
    desc = "Your hit point maximum increases by an amount equal to 5."
    c = extract_prose_criteria(desc)
    assert c["hp_max_flat"] == 5
    assert c["hp_max_per_level"] == 0


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


def test_initiative_disadvantage_not_misread_as_advantage():
    desc = "You have disadvantage on initiative rolls."
    c = extract_prose_criteria(desc)
    assert c["initiative_advantage"] is False
    assert c["initiative_bonus"] == 0


def test_initiative_disadvantage_corpus_case_L26912():
    # Real corpus case mentioned in review: trimmed_5etools_list.md L26912 pattern
    desc = "The creature has disadvantage on initiative rolls and attack rolls."
    c = extract_prose_criteria(desc)
    assert c["initiative_advantage"] is False


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


def test_temp_hp_verb_boundaries_regains_temporary():
    desc = "You regains 2d6 temporary hit points when you reduce the target to 0 hit points."
    # Note: "regains" is grammatical but tests verb boundary; also check "regain"
    c = extract_prose_criteria("You regain 2d6 temporary hit points.")
    assert c["temp_hp_avg"] == pytest.approx(7.0)
    c2 = extract_prose_criteria("You regains 2d6 temporary hit points.")
    # Even with extra s, our \b pattern includes regains
    assert c2["temp_hp_avg"] == pytest.approx(7.0)


def test_temp_hp_verb_boundaries_grant():
    for phrase in ["grant 5 temporary hit points", "grants 5 temporary hit points"]:
        desc = f"You can {phrase} to an ally."
        c = extract_prose_criteria(desc)
        assert c["temp_hp_avg"] == pytest.approx(5.0), f"verb grant failed for {phrase}"


def test_temp_hp_verb_boundary_regains_hit_points_not_temporary():
    desc = "You regains 2d6 hit points at dawn."
    c = extract_prose_criteria(desc)
    assert c["temp_hp_avg"] == pytest.approx(0.0)
    assert c["temp_hp_frequency"] is None


def test_temp_hp_regains_without_temporary_not_set():
    desc = "You regain 2d6 hit points."
    c = extract_prose_criteria(desc)
    assert c["temp_hp_avg"] == pytest.approx(0.0)


def test_init_defaults_when_absent():
    c = extract_prose_criteria("A plain cloak with no magical properties.")
    assert c["temp_hp_avg"] == pytest.approx(0.0)
    assert c["temp_hp_frequency"] is None
    assert c["hp_max_flat"] == 0
    assert c["hp_max_per_level"] == 0
    assert c["initiative_bonus"] == 0
    assert c["initiative_advantage"] is False


# --- Pricing integration: simple-item bypass ---

def _base_weapon_criteria():
    return {
        "rarity": "rare",
        "req_attune": "none",
        "name": "Acheron Blade",
        "item_type_code": "M",
        "weapon_bonus": 1,
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
        "stealth_penalty": False,
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
    }


def test_simple_item_bypass_temp_hp_priced():
    base = _base_weapon_criteria()
    price_without = calculate_price(base)
    # Same weapon plus temp HP prose
    with_temp = dict(base)
    with_temp["temp_hp_avg"] = 7.0
    with_temp["temp_hp_frequency"] = "on_kill"
    price_with = calculate_price(with_temp)
    assert price_with > price_without, f"temp HP should increase price: {price_with} <= {price_without}"

    # Also via HP-max and initiative
    with_hp = dict(base)
    with_hp["hp_max_flat"] = 10
    assert calculate_price(with_hp) > price_without

    with_init = dict(base)
    with_init["initiative_bonus"] = 2
    assert calculate_price(with_init) > price_without

    with_adv = dict(base)
    with_adv["initiative_advantage"] = True
    assert calculate_price(with_adv) > price_without


def test_pricing_wave1_pd_na_no_raise():
    # pd.NA / NaN should not raise, should be treated as 0/False
    base = _base_weapon_criteria()
    for na_val in [pd.NA, float("nan"), None]:
        c = dict(base)
        c["temp_hp_avg"] = na_val
        c["temp_hp_frequency"] = na_val
        c["hp_max_flat"] = na_val
        c["hp_max_per_level"] = na_val
        c["initiative_bonus"] = na_val
        c["initiative_advantage"] = na_val
        # Should not raise
        price = calculate_price(c)
        assert isinstance(price, (int, float))
        assert not math.isnan(price)
        assert price >= 0

    # Mixed NA with valid temp HP
    c = dict(base)
    c["temp_hp_avg"] = pd.NA
    c["hp_max_flat"] = float("nan")
    c["initiative_advantage"] = pd.NA
    price = calculate_price(c)
    assert price == calculate_price(base)
