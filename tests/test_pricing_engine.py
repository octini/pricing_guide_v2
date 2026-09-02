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
    """Common +1 weapon (simple path): benchmark tier-priced with common 0.25 discount."""
    c = make_criteria(rarity="common", weapon_bonus=1)
    price = calculate_price(c)
    assert price == pytest.approx(725 * 0.25, rel=0.01)


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
    # explicit price_sources required (missing/empty → None, conservative anchor-wins)
    assert compute_guide_spread(1000, 3000, None, price_sources="DSA,MSRP") == pytest.approx(1.0, rel=0.01)
    # filtered by price_sources: only DSA+MSRP considered (DMPG ignored)
    assert compute_guide_spread(1000, 3000, 99999, price_sources="DSA,MSRP") == pytest.approx(1.0, rel=0.01)
    # only one guide → None (not divergent)
    assert compute_guide_spread(1000, None, None, price_sources="DSA") is None
    assert compute_guide_spread(1000, None, None, price_sources="DSA,MSRP") is None
    # equal prices → 0 spread (all three guides)
    assert compute_guide_spread(2000, 2000, 2000, price_sources="DSA,MSRP,DMPG") == pytest.approx(0.0, rel=0.01)
    # threshold boundary: spread exactly 0.60 with 2 guides: max 1300 min 700 mean 1000 => 0.60
    assert compute_guide_spread(700, 1300, None, price_sources="DSA,MSRP") == pytest.approx(0.60, rel=0.01)
    # missing/empty price_sources → None (unknown → anchor-wins), NOT "use all guides"
    assert compute_guide_spread(1000, 3000, None, price_sources=None) is None
    assert compute_guide_spread(1000, 3000, None, price_sources="") is None
    assert compute_guide_spread(1000, 3000, None, price_sources="   ") is None


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
    assert compute_guide_spread(1000, 3000, None, price_sources="DSA,MSRP") > 0.60
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


# ─── Save advantage tiered pricing ─────────────────────────────────────────
# Base: BROAD 400, CATEGORY 200 (0.5×), SITUATIONAL 100 (0.25×)
from src.pricing_engine import SAVE_ADVANTAGE_BASE_VALUE, SAVE_ADVANTAGE_CATEGORY_MULTIPLIER, SAVE_ADVANTAGE_SITUATIONAL_MULTIPLIER


def test_save_advantage_pricing_constants():
    assert SAVE_ADVANTAGE_BASE_VALUE == 400
    assert SAVE_ADVANTAGE_CATEGORY_MULTIPLIER == 0.5
    assert SAVE_ADVANTAGE_SITUATIONAL_MULTIPLIER == 0.25


def test_save_advantage_broad_pricing():
    base = calculate_price(make_criteria(rarity="rare"))
    c = make_criteria(rarity="rare", save_advantage=["saving throws"], save_advantage_broad=1, save_advantage_category=0, save_advantage_situational=0)
    assert calculate_price(c) == pytest.approx(base + 400, rel=0.01)
    c2 = make_criteria(rarity="rare", save_advantage=["intelligence", "wisdom", "charisma"], save_advantage_broad=3)
    assert calculate_price(c2) == pytest.approx(base + 400 * 3, rel=0.01)


def test_save_advantage_category_pricing_half():
    base = calculate_price(make_criteria(rarity="rare"))
    # CATEGORY is 0.5× base (200 gp) — e.g. vs frightened, vs spells, to avoid paralyzed
    c = make_criteria(rarity="rare", save_advantage=["saving throws"], save_advantage_broad=0, save_advantage_category=1, save_advantage_situational=0)
    assert calculate_price(c) == pytest.approx(base + 400 * 0.5, rel=0.01)


def test_save_advantage_situational_pricing_quarter():
    base = calculate_price(make_criteria(rarity="rare"))
    # SITUATIONAL is 0.25× base (100 gp) — e.g. while at 0 hp, while mounted
    c = make_criteria(rarity="rare", save_advantage=["saving throws"], save_advantage_broad=0, save_advantage_category=0, save_advantage_situational=1)
    assert calculate_price(c) == pytest.approx(base + 400 * 0.25, rel=0.01)


def test_save_advantage_mixed_tier_pricing():
    base = calculate_price(make_criteria(rarity="rare"))
    # 1 BROAD (400) + 1 CATEGORY (200) + 1 SITUATIONAL (100) = 700
    c = make_criteria(rarity="rare", save_advantage=["strength", "saving throws", "dexterity"], save_advantage_broad=1, save_advantage_category=1, save_advantage_situational=1)
    assert calculate_price(c) == pytest.approx(base + 400 + 200 + 100, rel=0.01)


def test_save_advantage_pricing_via_tiers_list():
    base = calculate_price(make_criteria(rarity="rare"))
    c = make_criteria(rarity="rare", save_advantage=["strength", "saving throws"], save_advantage_tiers=["BROAD", "CATEGORY"])
    assert calculate_price(c) == pytest.approx(base + 400 + 200, rel=0.01)
    c2 = make_criteria(rarity="rare", save_advantage=["saving throws"], save_advantage_tiers=["SITUATIONAL"])
    assert calculate_price(c2) == pytest.approx(base + 100, rel=0.01)


def test_save_advantage_backward_compat_missing_tier_is_broad():
    base = calculate_price(make_criteria(rarity="rare"))
    # No tier fields at all → treat all as BROAD (original 400 gp behavior)
    c = make_criteria(rarity="rare", save_advantage=["saving throws"])
    assert calculate_price(c) == pytest.approx(base + 400, rel=0.01)
    c2 = make_criteria(rarity="rare", save_advantage=["strength", "dexterity"])
    assert calculate_price(c2) == pytest.approx(base + 800, rel=0.01)
    # Empty tier list also falls back to BROAD
    c3 = make_criteria(rarity="rare", save_advantage=["saving throws"], save_advantage_tiers=[])
    assert calculate_price(c3) == pytest.approx(base + 400, rel=0.01)


def test_save_advantage_tier_counts_mismatch_pads_broad():
    base = calculate_price(make_criteria(rarity="rare"))
    # Tier counts sum < len(save_advantage) → remainder counted as BROAD
    c = make_criteria(rarity="rare", save_advantage=["a", "b", "c"], save_advantage_broad=1, save_advantage_category=1, save_advantage_situational=0)
    # 1 broad (400) +1 cat (200) + remainder 1 broad (400) = 1000
    assert calculate_price(c) == pytest.approx(base + 1000, rel=0.01)
def test_extra_damage_priced_avg_mixed_consumes_priced():
    base = calculate_price(make_criteria(rarity="rare"))
    # Mixed priced avg already weighted: 3.5*1.0 + 4.5*0.25 = 4.625
    c = make_criteria(rarity="rare", extra_damage_avg=8.0, extra_damage_priced_avg=4.625, extra_damage_condition="mixed", extra_damage_multiplier=0.578)
    assert calculate_price(c) == pytest.approx(base + 1500 * 4.625, rel=0.01)
    # Fallback when priced avg missing still uses multiplier (old behavior preserved)
    c2 = make_criteria(rarity="rare", extra_damage_avg=7.0, extra_damage_condition="vs_creature_type", extra_damage_multiplier=0.25)
    assert calculate_price(c2) == pytest.approx(base + 1500 * 7.0 * 0.25, rel=0.01)
    # NaN priced avg falls back
    c3 = make_criteria(rarity="rare", extra_damage_avg=7.0, extra_damage_priced_avg=float("nan"), extra_damage_condition="vs_creature_type", extra_damage_multiplier=0.25)
    assert calculate_price(c3) == pytest.approx(base + 1500 * 7.0 * 0.25, rel=0.01)


# ─── Group 2: hardened authority metrics ─────────────────────────────────────
def test_compute_criteria_coverage_null_safe_nan_na_strings():
    """NaN/pd.NA/None/strings/inf never count; only finite >0 numeric counts."""
    import math
    import pandas as pd
    # weapon_bonus variants
    assert compute_criteria_coverage(make_criteria(rarity="rare", weapon_bonus=float("nan"))) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", weapon_bonus=pd.NA)) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", weapon_bonus=None)) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", weapon_bonus="2")) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", weapon_bonus=float("inf"))) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", weapon_bonus=float("-inf"))) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", weapon_bonus=0)) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", weapon_bonus=-1)) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", weapon_bonus=1)) == 1
    # ac_bonus strings should not count
    assert compute_criteria_coverage(make_criteria(rarity="rare", ac_bonus="2")) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", ac_bonus=float("nan"))) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", ac_bonus=pd.NA)) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", ac_bonus=1)) == 1
    # spell bonuses NaN/pd.NA/strings not counted
    assert compute_criteria_coverage(make_criteria(rarity="rare", spell_attack_bonus=float("nan"))) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", spell_attack_bonus=pd.NA)) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", spell_attack_bonus="1")) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", spell_attack_bonus=1)) == 1
    # extra_damage NaN/inf/None/string/pd.NA not counted
    assert compute_criteria_coverage(make_criteria(rarity="rare", extra_damage_avg=float("nan"))) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", extra_damage_avg=float("inf"))) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", extra_damage_avg="5.0")) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", extra_damage_avg=pd.NA)) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", extra_damage_avg=None)) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", extra_damage_avg=0)) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", extra_damage_avg=5.0)) == 1
    # flight strings/NaN should not count
    assert compute_criteria_coverage(make_criteria(rarity="rare", flight_full="true")) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", flight_full=float("nan"))) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", flight_full=pd.NA)) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", flight_full=True)) == 1
    # sentience string/NaN not counted
    assert compute_criteria_coverage(make_criteria(rarity="rare", is_sentient="true")) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", is_sentient=float("nan"))) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", is_sentient=pd.NA)) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", is_sentient=True)) == 1
    # curse string not counted, but list still counts via effects
    assert compute_criteria_coverage(make_criteria(rarity="rare", is_cursed="true")) == 0
    assert compute_criteria_coverage(make_criteria(rarity="rare", is_cursed=True)) == 1


def test_compute_guide_spread_rejects_non_finite():
    """inf/-inf/NaN guide prices rejected before computing; fewer than 2 valid → None."""
    import math
    # inf with only one other valid → single valid after rejection → None
    assert compute_guide_spread(float("inf"), 1000, None, price_sources="DSA,MSRP") is None
    assert compute_guide_spread(float("-inf"), 1000, None, price_sources="DSA,MSRP") is None
    assert compute_guide_spread(float("nan"), 1000, None, price_sources="DSA,MSRP") is None
    # all non-finite except one → None
    assert compute_guide_spread(float("nan"), float("inf"), 1000, price_sources="DSA,MSRP,DMPG") is None
    assert compute_guide_spread(float("inf"), float("-inf"), None, price_sources="DSA,MSRP") is None
    # non-finite mixed with two finite: inf rejected, remaining two compute correctly
    assert compute_guide_spread(float("inf"), 1000, 2000, price_sources="DSA,MSRP,DMPG") == pytest.approx((2000 - 1000) / 1500, rel=0.01)
    assert compute_guide_spread(float("nan"), 1000, 2000, price_sources="DSA,MSRP,DMPG") == pytest.approx((2000 - 1000) / 1500, rel=0.01)
    # mean ≤0 guard → None (all prices ≤0 after filtering)
    assert compute_guide_spread(-100, -200, None, price_sources="DSA,MSRP") is None
    assert compute_guide_spread(0, 0, 0, price_sources="DSA,MSRP,DMPG") is None


def test_compute_guide_spread_empty_string_or_missing_returns_none():
    """Empty-string or missing price_sources → None (conservative anchor-wins), NOT use-all-guides."""
    import pandas as pd
    assert compute_guide_spread(1000, 3000, 5000, price_sources="") is None
    assert compute_guide_spread(1000, 3000, 5000, price_sources="   ") is None
    assert compute_guide_spread(1000, 3000, 5000, price_sources=None) is None
    assert compute_guide_spread(1000, 3000, 5000, price_sources=pd.NA) is None
    assert compute_guide_spread(1000, 3000, 5000, price_sources=float("nan")) is None
    # even with explicit list empty → None
    assert compute_guide_spread(1000, 3000, 5000, price_sources=[]) is None
    assert compute_guide_spread(1000, 3000, 5000, price_sources=[pd.NA, ""]) is None
    # valid sources still compute when provided
    assert compute_guide_spread(1000, 3000, None, price_sources="DSA,MSRP") == pytest.approx(1.0, rel=0.01)


def test_compute_guide_spread_single_guide_returns_none():
    """Fewer than 2 valid guides → None."""
    assert compute_guide_spread(1000, None, None, price_sources="DSA") is None
    assert compute_guide_spread(1000, None, None, price_sources="DSA,MSRP") is None
    assert compute_guide_spread(1000, 2000, None, price_sources="DSA") is None  # only DSA allowed even though MSRP available
    assert compute_guide_spread(None, 2000, None, price_sources="MSRP,DMPG") is None  # only one price present among allowed
    assert compute_guide_spread(1000, None, 2000, price_sources="DSA,DMPG") == pytest.approx((2000 - 1000) / 1500, rel=0.01)  # two valid → not None


def test_price_authority_flag_vs_branch_consistency():
    """Anchor flag implies amalgamated>0 was used; formula flag implies formula branch produced price."""
    from src.pricing_engine import derive_price_authority
    base = _rich_criteria()
    formula_price = calculate_price({**base, "amalgamated_price": None, "price_confidence": "none"})
    amalgamated = 99999.0
    # Anchor case: not rich or not divergent → anchor wins, flag anchor, price == amalgamated
    c_anchor = {**base, "amalgamated_price": amalgamated, "price_confidence": "multi"}
    price_anchor = calculate_price(c_anchor, criteria_coverage=2, guide_spread=0.8)
    assert price_anchor == pytest.approx(amalgamated, rel=0.01)
    auth_anchor = derive_price_authority(c_anchor, criteria_coverage=2, guide_spread=0.8, price_source="rule")
    assert auth_anchor == "anchor"
    # Formula case: rich+divergent → formula wins, flag formula, price == formula
    c_formula = {**base, "amalgamated_price": amalgamated, "price_confidence": "multi"}
    price_formula = calculate_price(c_formula, criteria_coverage=3, guide_spread=0.8)
    assert price_formula == pytest.approx(formula_price, rel=0.01)
    auth_formula = derive_price_authority(c_formula, criteria_coverage=3, guide_spread=0.8, price_source="rule")
    assert auth_formula == "formula"
    # Backward compat: None args → anchor wins if applicable
    c_backward = {**base, "amalgamated_price": amalgamated, "price_confidence": "multi"}
    price_backward = calculate_price(c_backward)  # no coverage/spread args
    assert price_backward == pytest.approx(amalgamated, rel=0.01)
    auth_backward = derive_price_authority(c_backward, criteria_coverage=None, guide_spread=None, price_source="rule")
    assert auth_backward == "anchor"
    # No valid amalgamated (0, NaN, None) → never anchor/formula, falls to rule
    c_zero = {**base, "amalgamated_price": 0, "price_confidence": "multi"}
    assert derive_price_authority(c_zero, criteria_coverage=2, guide_spread=0.8, price_source="rule") == "rule"
    c_nan = {**base, "amalgamated_price": float("nan"), "price_confidence": "multi"}
    assert derive_price_authority(c_nan, criteria_coverage=2, guide_spread=0.8, price_source="rule") == "rule"
    c_none = {**base, "amalgamated_price": None, "price_confidence": "multi"}
    assert derive_price_authority(c_none, criteria_coverage=3, guide_spread=0.8, price_source="rule") == "rule"
    # solo-outlier → rule-outlier regardless of coverage/spread
    c_outlier = {**base, "amalgamated_price": 5000, "price_confidence": "solo-outlier"}
    assert derive_price_authority(c_outlier, criteria_coverage=3, guide_spread=0.8, price_source="rule-outlier-detected") == "rule-outlier"
    # official → official
    c_off = {**base, "amalgamated_price": 5000, "price_confidence": "multi"}
    assert derive_price_authority(c_off, criteria_coverage=3, guide_spread=0.8, price_source="official") == "official"


# ─── Hop C5: family-min gated to non-amalgamated (reference authority) ───────
def test_hop_c5_family_min_gated_to_non_amalgamated():
    """(a) amalgamated +3 Dagger 8987 NOT lifted; (b) Algorithm 146 →725; (c) amalgamated Needler NOT lifted."""
    # (a) amalgamated +3 Dagger: has amalgamated multi → family-min must NOT lift, stays at amalgamated
    c_dagger_amalg = make_criteria(
        rarity="very_rare", weapon_bonus=3, item_type_code="M|XPHB", is_ammunition=False,
        amalgamated_price=8987.72, price_confidence="multi", name="+3 Dagger"
    )
    price_dagger = calculate_price(c_dagger_amalg)
    # With amalgamated, price should be amalgamated (8987), not family-min 14950 (floor 1000 <8987)
    assert price_dagger == pytest.approx(8987.72, rel=0.01)
    # Same dagger without amalgamated (Algorithm) → family-min 14950
    c_dagger_algo = make_criteria(
        rarity="very_rare", weapon_bonus=3, item_type_code="M|XPHB", is_ammunition=False,
        amalgamated_price=None, price_confidence="none", name="+3 Dagger"
    )
    price_dagger_algo = calculate_price(c_dagger_algo)
    assert price_dagger_algo == pytest.approx(14950, rel=0.01)

    # (b) Algorithm +1 cheap-base weapon at 146 → lifted to 725 (family-min)
    c_cheap = make_criteria(
        rarity="rare", weapon_bonus=1, item_type_code="M|XPHB", is_ammunition=False,
        amalgamated_price=None, price_confidence="none", name="+1 Longsword"
    )
    price_cheap = calculate_price(c_cheap)
    assert price_cheap == pytest.approx(725, rel=0.01)
    # solo-outlier should still clamp (Algorithm path)
    c_solo_outlier = make_criteria(
        rarity="rare", weapon_bonus=1, item_type_code="M|XPHB", is_ammunition=False,
        amalgamated_price=146.0, price_confidence="solo-outlier", name="+1 Longsword"
    )
    price_solo = calculate_price(c_solo_outlier)
    assert price_solo == pytest.approx(725, rel=0.01)

    # (c) amalgamated Drow +3 Needler → NOT family-min lifted, but floored to 8000 (legendary floor)
    c_needler_amalg = make_criteria(
        rarity="legendary", weapon_bonus=3, item_type_code="R|XPHB", is_ammunition=False,
        amalgamated_price=635.88, price_confidence="multi", name="Drow +3 Repeater Needler"
    )
    price_needler = calculate_price(c_needler_amalg)
    # Family-min gated (no 14950), but absolute floor 8000 wins over 635
    assert price_needler == pytest.approx(8000, rel=0.01)
    assert price_needler != pytest.approx(14950, rel=0.01)
    # Non-amalgamated Needler (hypothetical) would be lifted to 14950
    c_needler_algo = make_criteria(
        rarity="legendary", weapon_bonus=3, item_type_code="R|XPHB", is_ammunition=False,
        amalgamated_price=None, price_confidence="none", name="Drow +3 Repeater Needler"
    )
    price_needler_algo = calculate_price(c_needler_algo)
    assert price_needler_algo == pytest.approx(14950, rel=0.01)
