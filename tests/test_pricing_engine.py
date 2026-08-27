# tests/test_pricing_engine.py
"""Tests for rule-based pricing engine.

Constants updated to match calibrated values from oracle review (2026-04-07).
Base prices and additives were reduced ~3-10× to match real-world guide data.
"""
import pytest
from src.pricing_engine import (
    calculate_price,
    calculate_price_with_outlier_check,
    compute_criteria_coverage,
    compute_guide_spread,
    CRITERIA_RICH_THRESHOLD,
    GUIDE_DIVERGENCE_THRESHOLD,
    RARITY_BASE_PRICES,
    RARITY_FLOORS,
)


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


@pytest.mark.parametrize("item_type", ["$A", "$G|XDMG", "$C", "TG", "TB"])
def test_pure_wealth_commodity_types_use_exact_official_price(item_type):
    """Treasure/commodity rows use listed value even when rarity is not mundane."""
    c = make_criteria(
        rarity="varies",
        name="Commodity Item",
        item_type_code=item_type,
        official_price_gp=500.0,
    )

    price = calculate_price(c)

    assert price == 500.0


def test_magic_material_weapon_with_official_value_does_not_use_commodity_exact_override():
    """Material/+N magic variants keep formula behavior when raw values conflict."""
    c = make_criteria(
        rarity="uncommon",
        name="+1 Adamantine Longsword",
        item_type_code="M",
        weapon_bonus=1,
        material="adamantine",
        official_price_gp=100.0,
    )

    price = calculate_price(c)

    assert price != pytest.approx(100.0)
    assert price >= 725.0


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


def test_extra_damage_uses_condition_multiplier_without_mutating_raw_average():
    base = calculate_price(make_criteria(rarity="rare"))
    c = make_criteria(
        rarity="rare",
        extra_damage_avg=7.0,
        extra_damage_condition="vs_creature_type",
        extra_damage_multiplier=0.25,
    )

    price = calculate_price(c)

    assert c["extra_damage_avg"] == 7.0
    assert price == pytest.approx(base + 1500 * 7.0 * 0.25, rel=0.01)


def test_extra_damage_crit_only_multiplier_preserves_existing_expected_value():
    base = calculate_price(make_criteria(rarity="uncommon"))
    c = make_criteria(
        rarity="uncommon",
        extra_damage_avg=3.5,
        extra_damage_condition="on_crit",
        extra_damage_multiplier=0.05,
    )

    price = calculate_price(c)

    assert price == pytest.approx(base + 1500 * 3.5 * 0.05, rel=0.01)


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


# ─── Tiered authority: coverage >=3 + spread >0.60 → formula wins ───────────


def _rich_criteria():
    """Helper: coverage exactly 3 (resistances + extra_damage + sentient)."""
    return make_criteria(
        rarity="rare",
        damage_resistances=["fire"],
        extra_damage_avg=5.0,
        is_sentient=True,
    )


def test_compute_criteria_coverage_counts_distinct_buckets():
    c = _rich_criteria()
    assert compute_criteria_coverage(c) == 3
    c2 = make_criteria(rarity="rare", damage_resistances=["fire"], extra_damage_avg=5.0)
    assert compute_criteria_coverage(c2) == 2
    c3 = make_criteria(rarity="rare", flight_full=True, material="mithral", is_cursed=True)
    assert compute_criteria_coverage(c3) == 3
    # material "none" should not count
    c4 = make_criteria(rarity="rare", material="none", flight_full=True)
    assert compute_criteria_coverage(c4) == 1


def test_compute_guide_spread_basic_and_threshold():
    # 2 guides: (3000-1000)/2000 = 1.0 >0.60 high divergence
    assert compute_guide_spread(1000, 3000, None) == pytest.approx(1.0, rel=0.01)
    # filtered by price_sources: only DSA+MSRP considered
    assert compute_guide_spread(1000, 3000, 99999, price_sources="DSA,MSRP") == pytest.approx(1.0, rel=0.01)
    # only one guide → None (not divergent)
    assert compute_guide_spread(1000, None, None) is None
    # equal prices → 0 spread
    assert compute_guide_spread(2000, 2000, 2000) == pytest.approx(0.0, rel=0.01)
    # threshold boundary: spread exactly 0.60 with 2 guides: max 1300 min 700 mean 1000 => 0.60
    assert compute_guide_spread(700, 1300, None) == pytest.approx(0.60, rel=0.01)


def test_tiered_authority_anchor_wins_when_not_rich_or_not_divergent():
    """Anchor wins if NOT (rich and divergent) — current behavior."""
    base_rich = _rich_criteria()
    # Expected formula price without anchor (for comparison)
    formula_price = calculate_price({**base_rich, "amalgamated_price": None, "price_confidence": "none"})
    amalgamated = 99999.0
    # Case 1: not rich (coverage 2) + high divergence => anchor wins
    c_not_rich = make_criteria(
        rarity="rare",
        damage_resistances=["fire"],
        extra_damage_avg=5.0,  # coverage 2
        amalgamated_price=amalgamated,
        price_confidence="multi",
        dsa_price=1000,
        msrp_price=3000,
    )
    # coverage 2, spread 1.0 => not rich => anchor
    assert compute_criteria_coverage(c_not_rich) == 2
    assert compute_guide_spread(1000, 3000, None) > 0.60
    assert calculate_price(c_not_rich, criteria_coverage=2, guide_spread=1.0) == pytest.approx(amalgamated, rel=0.01)
    # Case 2: rich but low divergence => anchor wins
    c_low_div = {**base_rich, "amalgamated_price": amalgamated, "price_confidence": "multi"}
    assert calculate_price(c_low_div, criteria_coverage=3, guide_spread=0.2) == pytest.approx(amalgamated, rel=0.01)
    # Case 3: rich + high divergence but confidence none => anchor not applicable, falls to formula anyway but not flagged as formula-wins; price should be formula
    c_no_conf = {**base_rich, "amalgamated_price": amalgamated, "price_confidence": "none"}
    assert calculate_price(c_no_conf, criteria_coverage=3, guide_spread=1.0) == pytest.approx(formula_price, rel=0.01)


def test_tiered_authority_formula_wins_when_rich_and_divergent():
    """Rich (>=3) + high divergence (>0.60) + multi/solo => formula wins."""
    base = _rich_criteria()
    formula_price = calculate_price({**base, "amalgamated_price": None, "price_confidence": "none"})
    amalgamated = 99999.0
    c = {**base, "amalgamated_price": amalgamated, "price_confidence": "multi"}
    # Without tiered params, anchor wins (backward compat baseline)
    assert calculate_price(c) == pytest.approx(amalgamated, rel=0.01)
    # With rich+divergent, formula wins
    price_tiered = calculate_price(c, criteria_coverage=3, guide_spread=0.8)
    assert price_tiered == pytest.approx(formula_price, rel=0.01)
    assert price_tiered != pytest.approx(amalgamated, rel=0.01)
    # Via outlier_check wrapper propagates too
    price2, src = calculate_price_with_outlier_check(c, criteria_coverage=3, guide_spread=0.8)
    assert price2 == pytest.approx(formula_price, rel=0.01)
    # Solo also formula-wins
    c_solo = {**base, "amalgamated_price": amalgamated, "price_confidence": "solo"}
    assert calculate_price(c_solo, criteria_coverage=4, guide_spread=1.0) == pytest.approx(formula_price, rel=0.01)


def test_tiered_authority_boundary_coverage3_spread060_anchor_wins():
    """Thresholds are strict >: coverage >=3 is rich, but spread must be >0.60."""
    base = _rich_criteria()
    formula_price = calculate_price({**base, "amalgamated_price": None, "price_confidence": "none"})
    amalgamated = 50000.0
    c = {**base, "amalgamated_price": amalgamated, "price_confidence": "multi"}
    # Exactly 3 and exactly 0.60 => NOT divergent => anchor wins
    assert calculate_price(c, criteria_coverage=3, guide_spread=0.60) == pytest.approx(amalgamated, rel=0.01)
    # 3 and 0.61 => divergent => formula wins
    assert calculate_price(c, criteria_coverage=3, guide_spread=0.61) == pytest.approx(formula_price, rel=0.01)
    # 2 and 0.61 => not rich => anchor wins even though divergent
    assert calculate_price(c, criteria_coverage=2, guide_spread=0.61) == pytest.approx(amalgamated, rel=0.01)
    # 4 and 0.60 => anchor wins (just below threshold)
    assert calculate_price(c, criteria_coverage=4, guide_spread=0.60) == pytest.approx(amalgamated, rel=0.01)
    # 4 and 0.6001 => formula wins
    assert calculate_price(c, criteria_coverage=4, guide_spread=0.6001) == pytest.approx(formula_price, rel=0.01)


def test_tiered_authority_backward_compat_no_new_args_identical():
    """No new args (or None) must give identical output to today — anchor wins."""
    base = _rich_criteria()
    amalgamated = 12345.0
    c = {**base, "amalgamated_price": amalgamated, "price_confidence": "multi"}
    price_default = calculate_price(c)
    assert price_default == pytest.approx(amalgamated, rel=0.01)
    # Explicit None should be identical to omitting args
    price_none = calculate_price(c, criteria_coverage=None, guide_spread=None)
    assert price_none == pytest.approx(price_default, rel=0.01)
    # Via wrapper with None also identical
    price_w, _ = calculate_price_with_outlier_check(c)
    price_w_none, _ = calculate_price_with_outlier_check(c, criteria_coverage=None, guide_spread=None)
    assert price_w == pytest.approx(price_w_none, rel=0.01)
    assert price_w == pytest.approx(amalgamated, rel=0.01)
    # Even when criteria are rich+divergent, omitting args must still anchor (backward compat)
    rich_div_c = {**base, "amalgamated_price": amalgamated, "price_confidence": "solo"}
    assert calculate_price(rich_div_c) == pytest.approx(amalgamated, rel=0.01)
    assert calculate_price(rich_div_c, criteria_coverage=None, guide_spread=None) == pytest.approx(amalgamated, rel=0.01)


def test_tiered_authority_formula_respects_rarity_floor():
    """Formula win still floors at rarity minimum."""
    # common floor is 10, uncommon 50, etc. Use common with cursed to drive formula below floor?
    # Common base 100, cursed 0.75 => 75, but with amalgamated anchor high. Rich+divergent forces formula which floors.
    c = make_criteria(
        rarity="common",
        damage_resistances=["fire"],
        extra_damage_avg=1.0,
        is_sentient=True,  # coverage 3
        is_cursed=True,  # cursed reduces but still above floor; to test floor we use a tiny formula item
        amalgamated_price=99999,
        price_confidence="multi",
    )
    # coverage 3 + spread high => formula wins
    price = calculate_price(c, criteria_coverage=3, guide_spread=1.0)
    assert price >= RARITY_FLOORS["common"]
    assert price != pytest.approx(99999, rel=0.01)
