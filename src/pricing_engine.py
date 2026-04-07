# src/pricing_engine.py
"""Rule-based pricing engine implementing the formula from the spec."""

from typing import Optional

RARITY_BASE_PRICES = {
    "mundane": 1,
    "common": 500,
    "uncommon": 2500,
    "rare": 20000,
    "very_rare": 100000,
    "legendary": 500000,
    "artifact": 1500000,
    "unknown_magic": 5000,  # fallback estimate
    "unknown": 1,
    "varies": 5000,  # fallback estimate
}

RARITY_FLOORS = {
    "mundane": 1,
    "common": 50,
    "uncommon": 100,
    "rare": 500,
    "very_rare": 5000,
    "legendary": 50000,
    "artifact": 500000,
    "unknown_magic": 50,
    "unknown": 1,
    "varies": 50,
}

SPELL_SCROLL_PRICES = {
    0: 25,
    1: 75,
    2: 150,
    3: 300,
    4: 1500,
    5: 3000,
    6: 8500,
    7: 20000,
    8: 45000,
    9: 100000,
}

WEAPON_BONUS_ADDITIVE = {1: 10000, 2: 50000, 3: 200000}
AC_BONUS_ADDITIVE = {1: 15000, 2: 40000, 3: 150000}
SPELL_ATTACK_ADDITIVE = {1: 8000, 2: 25000, 3: 80000}

CONDITION_IMMUNITY_VALUES = {
    "frightened": 2000,
    "charmed": 3000,
    "poisoned": 2500,
    "exhaustion": 5000,
    "petrified": 3000,
    "paralyzed": 4000,
    "blinded": 4000,
    "deafened": 1000,
    "stunned": 4000,
    "incapacitated": 6000,
    "prone": 1500,
    "restrained": 3000,
}


def calculate_price(criteria: dict) -> float:
    """Calculate item price based on criteria dict.

    Returns price in gold pieces.
    """
    rarity = criteria.get("rarity", "unknown")
    official_price = criteria.get("official_price_gp")

    # Official prices used directly for mundane items
    if official_price and rarity in ("mundane", "none"):
        return float(official_price)

    # Spell scrolls: use level price directly (skip other formula)
    scroll_level = criteria.get("spell_scroll_level")
    if scroll_level is not None:
        return float(SPELL_SCROLL_PRICES.get(int(scroll_level), 75))

    base = float(RARITY_BASE_PRICES.get(rarity, 5000))

    # --- Additive bonuses ---
    additive = 0.0

    # Weapon bonus (use the highest of weapon/attack/damage bonus)
    weapon_bonus = max(
        criteria.get("weapon_bonus") or 0,
        criteria.get("weapon_attack_bonus") or 0,
        criteria.get("weapon_damage_bonus") or 0,
    )
    if weapon_bonus > 0:
        additive += WEAPON_BONUS_ADDITIVE.get(min(weapon_bonus, 3), 200000)

    # AC bonus
    ac_bonus = criteria.get("ac_bonus") or 0
    if ac_bonus > 0:
        additive += AC_BONUS_ADDITIVE.get(min(ac_bonus, 3), 150000)

    # Spell attack / save DC bonus (take higher)
    spell_bonus = max(
        criteria.get("spell_attack_bonus") or 0,
        criteria.get("spell_save_dc_bonus") or 0,
    )
    if spell_bonus > 0:
        additive += SPELL_ATTACK_ADDITIVE.get(min(spell_bonus, 3), 80000)

    # Saving throw bonus
    save_bonus = criteria.get("saving_throw_bonus") or 0
    if save_bonus > 0:
        additive += 3000 * save_bonus

    # Ability check bonus
    check_bonus = criteria.get("ability_check_bonus") or 0
    if check_bonus > 0:
        additive += 1000 * check_bonus

    # Proficiency bonus
    prof_bonus = criteria.get("proficiency_bonus_mod") or 0
    if prof_bonus > 0:
        additive += 5000 * prof_bonus

    # Resistances
    resistances = criteria.get("damage_resistances") or []
    if isinstance(resistances, str):
        resistances = [resistances] if resistances else []
    additive += 2000 * len(resistances)

    # Immunities
    immunities = criteria.get("damage_immunities") or []
    if isinstance(immunities, str):
        immunities = [immunities] if immunities else []
    additive += 5000 * len(immunities)

    # Condition immunities
    cond_immune = criteria.get("condition_immunities") or []
    if isinstance(cond_immune, str):
        cond_immune = [cond_immune] if cond_immune else []
    for cond in cond_immune:
        additive += CONDITION_IMMUNITY_VALUES.get(str(cond).lower(), 2000)

    # Movement
    if criteria.get("flight_full"):
        additive += 15000
    elif criteria.get("flight_limited"):
        additive += 5000

    if criteria.get("swim_speed"):
        additive += 2000
    if criteria.get("climb_speed"):
        additive += 2000
    if criteria.get("burrow_speed"):
        additive += 3000

    # Vision
    darkvision_ft = criteria.get("darkvision_feet") or 0
    if darkvision_ft > 0:
        additive += min(200 * (darkvision_ft // 30), 800)

    if criteria.get("truesight"):
        additive += 15000
    if criteria.get("blindsight"):
        additive += 5000
    if criteria.get("tremorsense"):
        additive += 3000

    # Utility
    if criteria.get("stealth_advantage"):
        additive += 2000
    if criteria.get("crit_immunity"):
        additive += 10000
    if criteria.get("teleportation"):
        additive += 20000
    if criteria.get("concentration_free"):
        additive += 3000
    if criteria.get("invisibility_atwill"):
        additive += 25000

    # Healing
    healing_daily = criteria.get("healing_daily_hp") or 0
    if healing_daily > 0:
        additive += 150 * healing_daily

    healing_consumable = criteria.get("healing_consumable_avg") or 0.0
    if healing_consumable > 0:
        additive += 50 * healing_consumable

    # Tome / manual permanent boost
    if criteria.get("tome_manual_boost"):
        additive += 100000  # midpoint of 50k-200k range

    # Wish effect
    if criteria.get("wish_effect"):
        additive += 500000

    # --- Multiplicative modifiers ---
    attune_mod = 1.0
    req_attune = criteria.get("req_attune", "none")
    if req_attune == "open":
        attune_mod = 0.85
    elif req_attune == "class":
        attune_mod = 0.75

    consumable_mod = 1.0
    is_ammo = criteria.get("is_ammunition", False)
    if is_ammo:
        consumable_mod = 0.05

    material_mod = 1.0  # mithral/adamantine handled in NLP

    curse_mod = 0.70 if criteria.get("is_cursed") else 1.0
    sentient_mod = 1.25 if criteria.get("is_sentient") else 1.0

    price = (base + additive) * attune_mod * consumable_mod * material_mod * curse_mod * sentient_mod

    floor = RARITY_FLOORS.get(rarity, 1)
    return max(floor, price)
