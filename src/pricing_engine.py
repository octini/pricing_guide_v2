# src/pricing_engine.py
"""Rule-based pricing engine implementing the formula from the spec.

Constants calibrated against external price guides (DSA, MSRP, DMPG) via oracle review.
"""

from typing import Optional

RARITY_BASE_PRICES = {
    "mundane": 1,
    "common": 100,        # Calibrated: real median ~132 gp
    "uncommon": 750,      # Calibrated: real median ~852 gp
    "rare": 4000,         # Calibrated: real median ~3,890 gp
    "very_rare": 13500,   # Calibrated: real median ~13,450 gp
    "legendary": 47000,   # Calibrated: real median ~46,500 gp
    "artifact": 150000,   # Calibrated from rare artifact data
    "unknown_magic": 750,  # Fallback: between uncommon and rare
    "unknown": 1,
    "varies": 750,        # Fallback estimate
}

RARITY_FLOORS = {
    "mundane": 1,
    "common": 10,
    "uncommon": 50,
    "rare": 200,
    "very_rare": 1000,
    "legendary": 8000,
    "artifact": 50000,
    "unknown_magic": 10,
    "unknown": 1,
    "varies": 10,
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

WEAPON_BONUS_ADDITIVE = {1: 1500, 2: 4000, 3: 20000}   # Calibrated: was 10k/50k/200k
AC_BONUS_ADDITIVE = {1: 1500, 2: 4000, 3: 15000}        # Calibrated: was 15k/40k/150k
SPELL_ATTACK_ADDITIVE = {1: 1000, 2: 3000, 3: 10000}    # Calibrated: was 8k/25k/80k

CONDITION_IMMUNITY_VALUES = {
    "frightened": 400,
    "charmed": 400,
    "poisoned": 400,
    "exhaustion": 400,
    "petrified": 400,
    "paralyzed": 400,
    "blinded": 400,
    "deafened": 400,
    "stunned": 400,
    "incapacitated": 400,
    "prone": 400,
    "restrained": 400,
}


# Base mundane item costs to prevent magic variants from being cheaper than mundane base
# These are official PHB/XPHB prices in gp
MUNDANE_BASE_COSTS = {
    # Armor types
    "LA": 0,  # Light armor (average ~20 gp, low enough to ignore)
    "MA": 0,  # Medium armor (breastplate 400 gp is the expensive one — handled below)
    "HA": 0,  # Heavy armor — handled below per item
    "S": 10,  # Shield
    # Weapon types — most are cheap enough to ignore vs magic price
    "M": 0,  # Melee weapon (too varied; longsword=15, but greatsword=50)
    "R": 0,  # Ranged weapon
    "A": 0,  # Ammunition (per-piece pricing irrelevant)
}

# For armor specifically, we need to know the base armor type cost
# We detect this from item name for the most expensive armors
# IMPORTANT: Order matters! More specific names must come before substrings
# e.g., "half plate" must come before "plate armor" to avoid false matches
EXPENSIVE_ARMOR_BASES = {
    "half plate": 750,  # Must come before "plate armor"
    "plate armor": 1500,
    "splint armor": 200,
    "chain mail": 75,
    "breastplate": 400,
    "ring mail": 30,
    "scale mail": 50,
    "chain shirt": 50,
    "hide armor": 10,
    "leather armor": 10,
    "padded armor": 5,
    "studded leather": 45,
}

# Material flat-rate additions (DSA formula: MatCost = Armor Cost + Material Flat Rate)
# These are added ON TOP of the mundane base cost for armor made of rare materials
MATERIAL_FLAT_RATES = {
    "mithral": 1000, # DSA: Mithral adds 1,000 gp flat
    "adamantine": 3000, # DSA: Adamantine adds 3,000 gp flat
    "silvered": 100, # Silvered weapons: +100 gp (PHB: silvering costs 100 gp)
}

# DSA rarity multipliers for material armor
# These are applied to the material cost (base + flat rate) for armor made of rare materials
MATERIAL_RARITY_MULTIPLIERS = {
    "common": 1.0,
    "uncommon": 1.5,
    "rare": 2.0,
    "very_rare": 3.0,
    "legendary": 5.0,
}

# Standard Exchange Rates (per pound) from PHB/WDH/WDMM:
# - Iron/Steel: 0.1 gp/lb (PHB: 1 sp = 1 lb iron)
# - Gold: 50 gp/lb (PHB: 50 coins = 1 lb)
# - Mithral: 50 gp/lb (WDMM: 1 lb mithral = 50 gp)
# - Adamantine: 100 gp/lb (WDH: 10 lb adamantine bar = 1,000 gp)
MATERIAL_COST_PER_LB = {
    "iron": 0.1,
    "steel": 0.1,
    "gold": 50,
    "mithral": 50,
    "adamantine": 100,
}

# Ammunition weights (from 5eTools) - used for material cost calculation
AMMUNITION_WEIGHTS = {
    "arrow": 0.05,      # lb per arrow
    "bolt": 0.075,      # lb per bolt
    "bullet": 0.075,    # lb per sling bullet
    "firearm bullet": 0.05,  # lb per firearm bullet
    "needle": 0.02,     # lb per needle
}

# Markup factor for material ammunition
# Mundane arrows: 0.05 lb * 0.1 gp/lb (steel) = 0.005 gp material, sells for 0.05 gp = 10x markup
# DSA prices adamantine arrows at ~248 gp each (4,952 gp / 20)
# Material cost: 0.05 lb * 100 gp/lb = 5 gp
# DSA price / material cost = 248 / 5 = ~50x
# This suggests a 50x multiplier for special material ammunition (combining markup + rarity premium)
MATERIAL_AMMUNITION_MULTIPLIER = 50

# Flavor items: items with charges that have no tactical/combat value
# These should use a much lower charge valuation (10 gp/charge instead of 500 gp)
FLAVOR_ITEMS = {
    "staff of flowers",      # Creates flowers
    "staff of birdcalls",    # Makes bird sounds
    "wand of smiles",        # Forces smiling
    "wand of scowls",        # Forces scowling
    "wand of conducting",    # Conducts music
    "wand of pyrotechnics",  # Creates fireworks (minor utility)
    "heward's handy spice pouch",  # Produces seasoning
"instrument of scribing", # Sends messages (minor utility)
}


def calculate_price(criteria: dict) -> float:
    """Calculate item price based on criteria dict.

    Returns price in gold pieces.
    """
    rarity = criteria.get("rarity", "unknown")
    official_price = criteria.get("official_price_gp")
    req_attune = criteria.get("req_attune", "none")
    item_name_lower = str(criteria.get("name", "")).lower()

    # Official prices used directly for mundane items
    # NaN check: x == x is False for NaN, so NaN official prices fall through
    if official_price is not None and official_price == official_price and rarity in ("mundane", "none"):
        return float(official_price)

    # Byeshk items: use official price directly (includes +400 gp material premium)
    # Byeshk items have rarity=unknown but official_price_gp already set
    if item_name_lower.startswith("byeshk") and official_price is not None and official_price == official_price and official_price > 0:
        return float(official_price)

    # Spell scrolls: use level price directly (skip other formula)
    # BUT: Enspelled weapons are NOT scrolls - they're weapons with embedded spells
    # Enspelled items have charges and recharge, scrolls don't
    scroll_level = criteria.get("spell_scroll_level")
    is_enspelled = "enspelled" in item_name_lower
    if scroll_level is not None and scroll_level == scroll_level and not is_enspelled: # NaN check
        return float(SPELL_SCROLL_PRICES.get(int(scroll_level), 75))

    base = float(RARITY_BASE_PRICES.get(rarity, 750))

    # Base mundane item cost: magic items should cost at least as much as their mundane counterpart
    # Detect from item name for expensive armors
    base_item_cost = 0.0
    if rarity not in ("mundane", "none", "unknown", "varies"):
        for armor_name, armor_cost in EXPENSIVE_ARMOR_BASES.items():
            if armor_name in item_name_lower:
                base_item_cost = float(armor_cost)
                break

    # Material cost: add flat rate for rare materials (DSA formula)
    # This is added to base_item_cost, not as a multiplier
    material = criteria.get("material")
    material_cost = 0.0
    is_material_armor = False
    if material and material in MATERIAL_FLAT_RATES:
        material_cost = float(MATERIAL_FLAT_RATES[material])
        # For armor, add material cost to base_item_cost
        # For weapons, add as additive (handled below)
        if base_item_cost > 0:
            base_item_cost += material_cost
            is_material_armor = True

    # DSA formula for material armor: MatCost * rarity_multiplier * attunement_modifier
    # This overrides the normal pricing formula for armor made of rare materials
    if is_material_armor and material in ("mithral", "adamantine"):
        rarity_mult = MATERIAL_RARITY_MULTIPLIERS.get(rarity, 1.0)
        # Attunement modifier: DSA uses 1.1 for no attunement, 1.0 for attunement
        # But we want to be consistent with our attunement discount approach
        # So we use: base_item_cost * rarity_mult * (1.0 if attunement, 1.1 if no attunement)
        attune_bonus = 1.1 if req_attune == "none" else 1.0
        material_armor_price = base_item_cost * rarity_mult * attune_bonus
        # Return this price directly, bypassing the normal formula
        floor = RARITY_FLOORS.get(rarity, 1)
        return max(floor, material_armor_price)

    # Material ammunition: use weight-based formula
    # This handles adamantine/mithral/silvered arrows, bolts, bullets, etc.
    # Formula: weight * material_cost_per_lb * markup_multiplier
    is_ammunition = criteria.get("is_ammunition", False)
    if is_ammunition and material and material in MATERIAL_COST_PER_LB:
        # Determine ammunition type from item name
        item_name_lower = str(criteria.get("name", "")).lower()
        weight = 0.05  # Default weight (arrow)
        for ammo_type, ammo_weight in AMMUNITION_WEIGHTS.items():
            if ammo_type in item_name_lower:
                weight = ammo_weight
                break
        
        # Calculate material cost
        material_cost_per_lb = MATERIAL_COST_PER_LB.get(material, 100)
        material_price = weight * material_cost_per_lb * MATERIAL_AMMUNITION_MULTIPLIER
        
        # Apply minimum floor based on material
        min_price = 50 if material == "adamantine" else 25 if material == "mithral" else 10
        return max(min_price, material_price)
    
    # Silvered ammunition: PHB says silvering costs 100 gp regardless of weapon size
    # So silvered ammunition is +100 gp per piece (same as weapons)
    if is_ammunition and material == "silvered":
        return 100.0

    # --- Additive bonuses ---
    additive = 0.0

    # Weapon bonus (use the highest of weapon/attack/damage bonus)
    weapon_bonus = max(
        criteria.get("weapon_bonus") or 0,
        criteria.get("weapon_attack_bonus") or 0,
        criteria.get("weapon_damage_bonus") or 0,
    )
    if weapon_bonus > 0:
        additive += WEAPON_BONUS_ADDITIVE.get(min(weapon_bonus, 3), 20000)

    # AC bonus
    ac_bonus = criteria.get("ac_bonus") or 0
    if ac_bonus > 0:
        additive += AC_BONUS_ADDITIVE.get(min(ac_bonus, 3), 15000)

    # Spell attack / save DC bonus (take higher)
    spell_bonus = max(
        criteria.get("spell_attack_bonus") or 0,
        criteria.get("spell_save_dc_bonus") or 0,
    )
    if spell_bonus > 0:
        additive += SPELL_ATTACK_ADDITIVE.get(min(spell_bonus, 3), 10000)

    # Saving throw bonus
    save_bonus = criteria.get("saving_throw_bonus") or 0
    if save_bonus > 0:
        additive += 500 * save_bonus  # was 3000

    # Ability check bonus
    check_bonus = criteria.get("ability_check_bonus") or 0
    if check_bonus > 0:
        additive += 200 * check_bonus  # was 1000

    # Proficiency bonus
    prof_bonus = criteria.get("proficiency_bonus_mod") or 0
    if prof_bonus > 0:
        additive += 800 * prof_bonus  # was 5000

    # Resistances
    resistances = criteria.get("damage_resistances") or []
    if isinstance(resistances, str):
        resistances = [resistances] if resistances else []
    additive += 300 * len(resistances)  # was 2000

    # Immunities
    immunities = criteria.get("damage_immunities") or []
    if isinstance(immunities, str):
        immunities = [immunities] if immunities else []
    additive += 800 * len(immunities)  # was 5000

    # Condition immunities
    cond_immune = criteria.get("condition_immunities") or []
    if isinstance(cond_immune, str):
        cond_immune = [cond_immune] if cond_immune else []
    for cond in cond_immune:
        additive += CONDITION_IMMUNITY_VALUES.get(str(cond).lower(), 400)

    # Movement
    if criteria.get("flight_full"):
        additive += 3000   # was 15000
    elif criteria.get("flight_limited"):
        additive += 1000   # was 5000

    if criteria.get("swim_speed"):
        additive += 300    # was 2000
    if criteria.get("climb_speed"):
        additive += 300    # was 2000
    if criteria.get("burrow_speed"):
        additive += 500    # was 3000

    # Vision
    darkvision_ft = criteria.get("darkvision_feet") or 0
    if darkvision_ft > 0:
        additive += min(50 * (darkvision_ft // 30), 200)  # was 200/30ft, cap 800

    if criteria.get("truesight"):
        additive += 3000   # was 15000
    if criteria.get("blindsight"):
        additive += 1000   # was 5000
    if criteria.get("tremorsense"):
        additive += 500    # was 3000

    # Utility
    if criteria.get("stealth_advantage"):
        additive += 400    # was 2000
    if criteria.get("crit_immunity"):
        additive += 2000   # was 10000
    if criteria.get("teleportation"):
        additive += 5000   # was 20000
    if criteria.get("concentration_free"):
        additive += 500    # was 3000
    if criteria.get("invisibility_atwill"):
        additive += 8000   # was 25000

    # Healing
    healing_daily = criteria.get("healing_daily_hp") or 0
    if healing_daily > 0:
        additive += 30 * healing_daily  # was 150

    healing_consumable = criteria.get("healing_consumable_avg") or 0.0
    if healing_consumable > 0:
        additive += 10 * healing_consumable  # was 50

    # Tome / manual permanent boost
    if criteria.get("tome_manual_boost"):
        additive += 15000  # was 100000; manuals amalgamate ~41,500 at VR base ~13,500

    # Wish effect (ring of three wishes, similar items)
    if criteria.get("wish_effect"):
        additive += 30000 # was 500000

    # Charges: rechargeable charges add moderate value; non-rechargeable add less
    # Exception: flavor items (no tactical value) use much lower valuation
    charges = criteria.get("charges")
    if charges and charges == charges: # not None, not NaN
        # Handle dice strings like "{@dice 1d3}" by extracting the numeric part
        if isinstance(charges, str):
            import re
            m = re.search(r'(\d+)', charges)
            if m:
                charges = int(m.group(1))
            else:
                charges = None
        elif isinstance(charges, (int, float)):
            charges = int(charges)
        else:
            charges = None
        if charges and charges > 0:
            # Check if this is a flavor item (no tactical/combat value)
            item_name_lower = str(criteria.get("name", "")).lower()
            is_flavor_item = item_name_lower in FLAVOR_ITEMS
            
            recharge = str(criteria.get("recharge") or "")
            if is_flavor_item:
                # Flavor items: minimal charge value (just the novelty)
                additive += 10 * charges
            elif recharge in ("dawn", "restLong", "dusk"):
                additive += 500 * charges # Daily recharge: significant value (Staff of Power has 20)
            elif recharge in ("restShort",):
                additive += 750 * charges # Short rest recharge: higher value
            else:
                additive += 100 * charges # Non-rechargeable: lower value per charge

    # Ability score mods: items that set a stat to a fixed value (like Gauntlets of Ogre Power)
    # Format: dict with {"static": {"str": 19}} or list of dicts with {type: "ability", amount: N, stat: "str"}
    ability_mods = criteria.get("ability_score_mods")
    if isinstance(ability_mods, dict):
        # Dict format: {"static": {"str": 19}} means "sets STR to 19"
        static_mods = ability_mods.get("static") or {}
        for stat, value in static_mods.items():
            if isinstance(value, (int, float)) and value >= 17:
                # Value scales with how high the stat is set
                # Calibrated: Gauntlets of Ogre Power (STR 19) amalgamates at ~5,040 gp
                # Base uncommon 750 + ability_mod ~4,300 gp → 5,050 gp before attunement
                additive += 3000 + 1500 * (value - 17) # 17→3000, 18→4500, 19→6000, 20→7500
    elif isinstance(ability_mods, list):
        # List format: check for any static boosts
        for mod in ability_mods:
            if isinstance(mod, dict) and mod.get("type") == "ability":
                amount = mod.get("amount", 0)
                if isinstance(amount, (int, float)) and amount >= 3:
                    # Value scales with boost magnitude
                    additive += 1000 + 500 * (amount - 3) # +3→1000, +4→1500, +5→2000

    # Material cost for non-armor items (weapons, ammunition)
    # For armor, material cost was already added to base_item_cost above
    if material and material in MATERIAL_FLAT_RATES and base_item_cost == 0:
        # Silvered weapons: add as additive
        if material == "silvered":
            additive += MATERIAL_FLAT_RATES["silvered"]

    # --- Multiplicative modifiers ---
    attune_mod = 1.0
    req_attune = criteria.get("req_attune", "none")
    if req_attune == "open":
        attune_mod = 0.90   # was 0.85
    elif req_attune == "class":
        attune_mod = 0.80   # was 0.75

    consumable_mod = 1.0
    is_ammo = criteria.get("is_ammunition", False)
    if is_ammo:
        consumable_mod = 0.02  # Ammo is single-use, sold in bundles; was 0.10

    # Ammunition of Slaying and similar high-rarity ammunition:
    # These are priced per piece, not as full magic items
    # Apply additional discount for very_rare+ ammunition
    if is_ammo and rarity in ("very_rare", "legendary", "artifact"):
        # Ammunition is consumed on use, so high-rarity ammo should be much cheaper
        # than a permanent magic item of the same rarity
        # Arrow of Slaying: reference ~632 gp (DSA:267, MSRP:750, DMPG:1000)
        # vs very_rare base 13,500 gp → need ~20x reduction
        consumable_mod *= 0.05  # Additional 5% for high-rarity ammo

    # Potion/oil/elixir discount — rarity-tiered (single-use consumables)
    item_type = criteria.get("item_type_code", "") or ""
    if item_type in ("P", "G"):  # Potion, Oil/Ointment
        potion_discounts = {
            "common": 0.50,
            "uncommon": 0.30,
            "rare": 0.15,
            "very_rare": 0.10,
            "legendary": 0.08,
            "artifact": 0.08,
        }
        consumable_mod *= potion_discounts.get(rarity, 0.25)

    material_mod = 1.0  # mithral/adamantine handled in NLP

    curse_mod = 0.75 if criteria.get("is_cursed") else 1.0   # was 0.70
    sentient_mod = 1.15 if criteria.get("is_sentient") else 1.0  # was 1.25

    price = (base + additive) * attune_mod * consumable_mod * material_mod * curse_mod * sentient_mod
    price = max(price, base_item_cost)  # Never cheaper than mundane base

    floor = RARITY_FLOORS.get(rarity, 1)
    return max(floor, price)
