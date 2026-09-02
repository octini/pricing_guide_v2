"""Hop B floor rules: family minimum + scroll-parity battery floor."""

import pytest
from src.pricing_engine import calculate_price, SPELL_SCROLL_PRICES, WEAPON_BONUS_VALUES

def make_criteria(**kw):
    defaults = dict(
        rarity="rare",
        req_attune="none",
        req_attune_class=None,
        item_type_code="M",
        is_ammunition=False,
        weapon_bonus=None,
        weapon_attack_bonus=None,
        weapon_damage_bonus=None,
        ac_bonus=None,
        spell_battery_max_level=None,
        charges=None,
        attached_spells=[],
        name="Test Item",
    )
    defaults.update(kw)
    return defaults

# ─── Family minimum ───────────────────────────────────────────────────────
def test_family_minimum_needler_plus1_rare():
    # Needler +1 rare is the canonical cheap-base case: mundane needle 97-146gp must not drag below 725
    c = make_criteria(rarity="rare", weapon_bonus=1, req_attune="none", item_type_code="R|XPHB", name="Repeater Needler +1")
    price = calculate_price(c)
    assert price >= 725 - 1e-6
    # class restriction scales after minimum: 725*0.80
    c_class = make_criteria(rarity="rare", weapon_bonus=1, req_attune="class", item_type_code="R|XPHB", name="Repeater Needler +1 class")
    price_class = calculate_price(c_class)
    assert price_class >= 725 * 0.80 - 1e-6
    # open 0.90
    c_open = make_criteria(rarity="rare", weapon_bonus=1, req_attune="open", item_type_code="R|XPHB", name="Repeater Needler +1 open")
    price_open = calculate_price(c_open)
    assert price_open >= 725 * 0.90 - 1e-6

def test_family_minimum_plus1_dagger():
    # Cheap mundane dagger base 2gp: +1 must still be >= family benchmark
    c = make_criteria(rarity="rare", weapon_bonus=1, req_attune="none", item_type_code="M", name="+1 Dagger")
    price = calculate_price(c)
    assert price >= 725 - 1e-6

def test_family_minimum_scales_with_rarity():
    # benchmark is already tier-priced; multiplier only discounts sub-norm rarity -> very_rare 1.0, legendary 1.0
    c_uncommon = make_criteria(rarity="uncommon", weapon_bonus=2, req_attune="none", item_type_code="M", name="+2 Dagger")
    assert calculate_price(c_uncommon) >= 3400 * 0.5 - 1e-6
    c_vr = make_criteria(rarity="very_rare", weapon_bonus=2, req_attune="none", item_type_code="M", name="+2 Dagger")
    assert calculate_price(c_vr) >= 3400 * 1.0 - 1e-6
    c_leg = make_criteria(rarity="legendary", weapon_bonus=3, req_attune="none", item_type_code="M", name="+3 Dagger")
    # legendary +3 raw 14950*1.0=14950, floor 8000, so expect at least 14950
    assert calculate_price(c_leg) >= 14950 * 1.0 - 1e-6

def test_ammunition_excluded_from_family_minimum():
    # +1 Needle (A) amalgam 32.88 vs weapon family 362.5 — ammo must NOT be lifted
    c_ammo = make_criteria(rarity="uncommon", weapon_bonus=1, req_attune="none", item_type_code="A|XPHB", is_ammunition=True, name="+1 Needle", amalgamated_price=32.88, price_confidence="multi")
    price_ammo = calculate_price(c_ammo)
    # Ammo stays at amalgam (per-piece) ~32.88, floored to 50? Actually uncommon floor 50 => max(50,32.88)=50
    # But must NOT be lifted to weapon family 362.5
    assert price_ammo < 362.5
    # Hop C5: Same bonus as weapon (M) with same amalgam should NOT be lifted (reference authority)
    c_weapon_amalg = make_criteria(rarity="uncommon", weapon_bonus=1, req_attune="none", item_type_code="M", is_ammunition=False, name="+1 Dagger", amalgamated_price=32.88, price_confidence="multi")
    price_weapon_amalg = calculate_price(c_weapon_amalg)
    # Amalgamated weapon stays at amalgam/floor, NOT family 362.5
    assert price_weapon_amalg < 362.5
    # Non-amalgamated weapon must be lifted to family 362.5
    c_weapon_algo = make_criteria(rarity="uncommon", weapon_bonus=1, req_attune="none", item_type_code="M", is_ammunition=False, name="+1 Dagger", amalgamated_price=None, price_confidence="none")
    price_weapon_algo = calculate_price(c_weapon_algo)
    assert price_weapon_algo >= 362.5 - 1e-6
    # Also direct simple without amalgam: uncommon +1 weapon is 362.5, ammo simple would be 362.5 but with exclusion should stay not uplifted beyond that
    # Verify helper returns None for ammo
    from src.pricing_engine import _family_min_for_criteria
    assert _family_min_for_criteria(c_ammo) is None
    assert _family_min_for_criteria(c_weapon_algo) is not None
    assert _family_min_for_criteria(c_weapon_amalg) is not None  # helper still returns value, but gating prevents use

# ─── Battery floor (q7b) — parity not premium ────────────────────────────────
def test_battery_floor_diamond_gem():
    # Diamond gem level 9 -> scroll 100000
    c = make_criteria(rarity="legendary", spell_battery_max_level=9, name="Spell Gem (Diamond)")
    price = calculate_price(c)
    assert price >= 100000 - 1e-6

def test_battery_floor_silver_shard():
    # Silver shard style level 7 -> 20000
    c = make_criteria(rarity="rare", spell_battery_max_level=7, name="Silver Shard")
    price = calculate_price(c)
    assert price >= 20000 - 1e-6

def test_battery_floor_obsidian_exact_parity():
    # Obsidian level 0 -> 25 exactly when prior price 10. Use mundane rarity to get low base so battery binds.
    c = make_criteria(rarity="mundane", spell_battery_max_level=0, name="Spell Gem (Obsidian)")
    price = calculate_price(c)
    # mundane base 1, floor 1, battery 25 => 25 exactly (parity)
    assert price == pytest.approx(25, rel=0.01)

def test_battery_floor_charges_with_attached_spells():
    # Condition (b): charges >0 AND attached_spells non-empty -> max level from spells
    # hold monster 5th -> scroll 3000
    c = make_criteria(rarity="uncommon", charges=6, attached_spells={'daily': {'1': ['hold monster']}}, name="Test Battery via charges")
    price = calculate_price(c)
    assert price >= 3000 - 1e-6

def test_battery_parity_not_premium():
    # Gem whose formula price exceeds parity is untouched
    # Topaz very_rare base 13500 > 8500 (level 6) stays 13500
    c = make_criteria(rarity="very_rare", spell_battery_max_level=6, name="Spell Gem (Topaz)")
    price = calculate_price(c)
    assert price == pytest.approx(13500, rel=0.01)
    # Also Star ruby level7 20000 vs legendary base 47000+? Actually legendary base 47000 >20000 stays
    c2 = make_criteria(rarity="legendary", spell_battery_max_level=7, name="Spell Gem (Star ruby)")
    price2 = calculate_price(c2)
    # legendary base 47000 + additive? For Star ruby with no additive, price via rarity base 47000 *? But with our engine, legendary Star ruby would be floored to battery? Actually base 47000 >20000 so stays
    assert price2 >= 20000

def test_battery_enspelled_not_firing():
    # Enspelled weapons use "store one spell" without level bound — should NOT parse battery level, and charges+spells empty => no floor
    # Use typical enspelled structure: charges 6, no attached_spells, spell_battery_max_level None
    c = make_criteria(rarity="uncommon", charges=6, attached_spells=[], spell_battery_max_level=None, item_type_code="M", name="Enspelled (Cantrip) Longsword")
    price = calculate_price(c)
    # Should be based on enspelled formula, not battery 25
    # Cantrip enspelled base 405 + default 15 =420
    assert price == pytest.approx(420, rel=0.1) or price >= 400

def test_battery_precedence_over_family():
    # If both family and battery apply, max wins
    c = make_criteria(rarity="rare", weapon_bonus=1, item_type_code="M", is_ammunition=False, spell_battery_max_level=9, name="Battery Weapon +1")
    price = calculate_price(c)
    # Family 725, battery 100000 => battery wins
    assert price >= 100000 - 1e-6
