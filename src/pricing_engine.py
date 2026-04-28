# src/pricing_engine.py
"""Rule-based pricing engine implementing the formula from the spec.

Constants calibrated against external price guides (DSA, MSRP, DMPG) via oracle review.
"""

import ast
import math
import re
import pandas as pd
from typing import Any, Optional

from .spell_data import get_spell_level
from .constants import RARITY_MEDIANS, CONDITION_IMMUNITY_VALUES


def _parse_list_field(value):
    """Parse a list field from CSV (serialized as string) back to Python list.
    
    CSV stores Python lists as their repr string (e.g., '[]', "['fire']").
    This safely deserializes them using ast.literal_eval.
    Returns an empty list for None/NaN/empty input.
    """
    if value is None or (isinstance(value, float) and value != value):
        return []
    if isinstance(value, str):
        if not value or value == "nan":
            return []
        try:
            result = ast.literal_eval(value)
            return result if isinstance(result, list) else [result]
        except (ValueError, SyntaxError):
            return [value] if value else []
    return value if isinstance(value, list) else [value]

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

# Enspelled item base prices (DSA formula)
# These are the base prices for generic "Enspelled Weapon/Armor" at each spell level
# Formula: Base_Enspelled[level] + Item_Base_Cost × 5.0
ENSPELLED_BASE_PRICES = {
    0: 405,      # Cantrip
    1: 1215,     # 1st level
    2: 3240,     # 2nd level
    3: 5400,     # 3rd level
    4: 12150,    # 4th level
    5: 17010,    # 5th level
    6: 37800,    # 6th level
    7: 48600,    # 7th level
    8: 60750,    # 8th level
}

WEAPON_BONUS_ADDITIVE = {1: 1500, 2: 4000, 3: 20000}   # Calibrated: was 10k/50k/200k
AC_BONUS_ADDITIVE = {1: 1500, 2: 4000, 3: 15000}        # Calibrated: was 15k/40k/150k
SPELL_ATTACK_ADDITIVE = {1: 1000, 2: 3000, 3: 10000}    # Calibrated: was 8k/25k/80k

USAGE_MULTIPLIERS = {
    "will": 3.0,
    "daily": 1.5,
    "charges": 1.0,
    "rest": 0.75,
    "limited": 0.5,
    "other": 0.5,
}

# Property item premium multipliers (multipliers applied to base item)
# These are based on analysis of actual pricing data from the guides
PROPERTY_PREMIUMS = {
    # High-value properties
    "death": 5.0,          # Wounding/Death items are powerful
    "life": 3.5,            # Healing/positive effects
    "wounding": 3.0,
    
    # Moderate properties  
    "warning": 2.0,         # Common property - significant premium
    "giantslayer": 2.5,     # Slaying items
    "dragonslayer": 2.5,
    "elemental": 2.0,
    "vorpal": 3.0,          # Very powerful
    
    # Low-moderate properties
    "finesse": 1.3,
    "brilliant": 1.5,
    "ice": 1.5,
    "flaming": 1.5,
    "frost": 1.5,
    "shocking": 1.5,
    "acid": 1.5,
    "thundering": 1.3,
    
    # Low premium
    "gleaming": 1.2,
    "silvered": 1.1,
    "returning": 1.1,
}

# +N weapon bonuses (calibrated from DSA/MSRP/DMPG)
# Target prices: +1=725, +2=3400, +3=14950
WEAPON_BONUS_VALUES = {
    1: 725,      
    2: 3400,     
    3: 14950,    
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
    "half plate": 750, # Must come before "plate armor"
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

# Weapon base costs for enspelled items (PHB prices)
# Used for DSA formula: Base_Enspelled + Item_Cost × 5.0
WEAPON_BASE_COSTS = {
    "dagger": 2,
    "shortsword": 10,
    "longsword": 15,
    "greatsword": 50,
    "glaive": 20,
    "staff": 5,
    "spear": 1,
    "warhammer": 15,
    "battleaxe": 10,
    "handaxe": 5,
    "light crossbow": 25,
    "heavy crossbow": 50,
    "shortbow": 25,
    "longbow": 50,
    "rapier": 25,
    "scimitar": 25,
    "double-bladed scimitar": 100,
    # Default fallback for weapons not listed
    "default": 15,
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
# - Silver: 5 gp/lb (PHB: 50 silver coins = 1 lb, 1 sp = 0.1 gp)
# - Gold: 50 gp/lb (PHB: 50 coins = 1 lb)
# - Mithral: 50 gp/lb (WDMM: 1 lb mithral = 50 gp)
# - Adamantine: 100 gp/lb (WDH: 10 lb adamantine bar = 1,000 gp)
MATERIAL_COST_PER_LB = {
    "iron": 0.1,
    "steel": 0.1,
    "silver": 5,
    "silvered": 5,  # Same as silver (coating uses silver material)
    "gold": 50,
    "mithral": 50,
    "adamantine": 100,
}

# Ammunition weights (from 5eTools) - used for material cost calculation
# Order matters: more specific patterns must come before generic ones
AMMUNITION_WEIGHTS = {
 "firearm bullet": 0.2, # lb per firearm bullet (check before "bullet")
 "sling bullet": 0.075, # lb per sling bullet (check before "bullet")
 "arrow": 0.05, # lb per arrow
 "bolt": 0.075, # lb per bolt
 "bullet": 0.075, # lb per generic bullet (fallback)
 "needle": 0.02, # lb per needle
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
    "staff of flowers", # Creates flowers
    "wyllows staff of flowers", # Creates flowers (same mechanics, normalized name)
    "staff of birdcalls", # Makes bird sounds
    "wand of smiles", # Forces smiling
    "wand of scowls", # Forces scowling
    "wand of conducting", # Conducts music
    "wand of pyrotechnics", # Creates fireworks (minor utility)
    "hewards handy spice pouch", # Produces seasoning
    "instrument of scribing", # Sends messages (minor utility)
}

# ─── Artifact Tier-Based Pricing System ───────────────────────────────────────
# Artifacts are assigned to tiers (S/A/B/C/D) based on practical usability:
#   S-tier (700k-1M): Game-changing, campaign-defining power
#   A-tier (500k-700k): Extremely powerful, broadly useful
#   B-tier (350k-500k): Strong artifacts with good utility
#   C-tier (250k-350k): Moderate artifacts, niche or limited use
#   D-tier (250k floor): Weakest artifacts, significant drawbacks or very niche
#
# Within each tier, items are ranked by a sub-score (0.0-1.0) that determines
# where they fall in the tier's price range. Sub-scores reflect relative power
# within the tier based on: drawbacks/curses, attunement restrictions,
# limited vs unlimited uses, conditional vs always-on powers, corruption.
#
# Dormant/Awakened/Exalted variants of Vestiges of Divergence are placed in
# progressively higher tiers to reflect their growth.

ARTIFACT_TIER_PRICES = {
    "S": (700000, 1000000),
    "A": (500000, 700000),
    "B": (350000, 500000),
    "C": (250000, 350000),
    "D": (250000, 275000),  # Narrow range near floor
}

# Format: "artifact name fragment" -> (tier, sub_score)
# sub_score 0.0 = bottom of tier, 1.0 = top of tier
# Names are lowercased, apostrophes removed for matching
ARTIFACT_TIERS = {
    # ── S-TIER: Game-changing artifacts ──────────────────────────────────────
    # Wand of Orcus: summon undead army, +3, 12d6 necrotic, legendary resistance
    "wand of orcus": ("S", 0.95),
    # Sword of Kas: +3 vorpal, +2d10 damage, advantage on all saves, legendary
    "sword of kas": ("S", 0.90),
    # Rod of Seven Parts: wish-level power when assembled, massive spell list
    "rod of seven parts": ("S", 0.85),
    # Eye of Vecna: truesight, X-ray vision, dominate monster, disintegrate
    "eye of vecna": ("S", 0.75),
    # Hand of Vecna: cold damage, teleport, finger of death, multiple immunities
    "hand of vecna": ("S", 0.70),
    # Book of Vile Darkness: permanent stat boost, dominate, summon nightwalker
    "book of vile darkness": ("S", 0.60),
    # Blade of Avernus: +3, vorpal vs fiends, fly 60ft, 6d6 radiant
    "blade of avernus": ("S", 0.55),
    # Daoud's Wondrous Lanthorn: plane shift, prismatic spray, wall of force at will
    "daouds wondrous lanthorn": ("S", 0.50),
    # Book of Exalted Deeds: permanent WIS boost, halo, spell enhancements
    "book of exalted deeds": ("S", 0.40),
    # Axe of the Dwarvish Lords: +3, conjure earth elemental, plane shift, many bonuses
    "axe of the dwarvish lords": ("S", 0.30),

    # ── A-TIER: Extremely powerful, broadly useful ──────────────────────────
    # Ring of Winter: immunity to cold, wall of ice, control weather, sleet storm
    "ring of winter": ("A", 0.95),
    # Teeth of Dahlver-Nar: implant teeth for powerful boons (22 options)
    "teeth of dahlver-nar": ("A", 0.90),
    # Adze of Annam: +3, giant-themed powers, enlarge, earthquake, plane shift
    "adze of annam": ("A", 0.85),
    # Demonomicon of Iggwilv: summon/bind demons, massive spell list
    "demonomicon of iggwilv": ("A", 0.80),
    # Orrery of the Wanderer: multiple powerful components, plane shift
    "orrery of the wanderer": ("A", 0.75),
    # Crook of Rao: banish fiends en masse, protection from evil
    "crook of rao": ("A", 0.70),
    # Dekella, Bident of Thassa: +3, control water, wall of water, water breathing
    "dekella": ("A", 0.65),
    # Blackrazor: +3, devour souls, haste, legendary sentient sword
    "blackrazor": ("A", 0.55),
    # Helm of Perfect Potential: powerful mental stat boosts, psychic abilities
    "helm of perfect potential": ("A", 0.45),
    # Orlassk's Reach: petrification, earth control, powerful utility
    "orlassks reach": ("A", 0.35),
    # Grovelthrash (Exalted): fully powered vestige, earthquake, powerful
    "grovelthrash (exalted)": ("A", 0.25),
    # Blade of Broken Mirrors (Exalted): fully powered, shapechange, +3
    "blade of broken mirrors (exalted)": ("A", 0.20),
    # Book of Vile Darkness (Variant): slightly weaker variant
    "book of vile darkness (variant)": ("A", 0.15),

    # ── B-TIER: Strong artifacts with good utility ──────────────────────────
    # Baba Yaga's Mortar and Pestle: fly, plane shift, force cage
    "baba yagas mortar and pestle": ("B", 0.95),
    # Akmon, Hammer of Purphoros: +3, create magic items, fire damage
    "akmon": ("B", 0.90),
    # Khrusor, Spear of Heliod: +3, radiant damage, searing light, sunburst
    "khrusor": ("B", 0.85),
    # Ephixis, Bow of Nylea: +3, seeking arrows, conjure volley
    "ephixis": ("B", 0.80),
    # Sword of Zariel: +3, radiant damage, fly, truesight
    "sword of zariel": ("B", 0.75),
    # Silken Spite (Exalted): fully powered vestige, +3, poison, web
    "silken spite (exalted)": ("B", 0.72),
    # The Bloody End (Exalted): fully powered vestige, +3, brutal
    "the bloody end (exalted)": ("B", 0.68),
    # Mace of the Black Crown (Exalted): fully powered, +3, fire, animate dead
    "mace of the black crown (exalted)": ("B", 0.65),
    # Wave: +3 trident, cube of force, water breathing, dominate
    "wave": ("B", 0.60),
    # Whelm: +3 warhammer, detect gems/evil, shatter, stun giants
    "whelm": ("B", 0.55),
    # Bigby's Beneficent Bracelet: Bigby's Hand at will, powerful utility
    "bigbys beneficent bracelet": ("B", 0.50),
    # Mastix, Whip of Erebos: +3, drain life, animate dead
    "mastix": ("B", 0.45),
    # Ruin's Wake (Exalted): fully powered vestige, +3, brutal attacks
    "ruins wake (exalted)": ("B", 0.42),
    # Will of the Talon (Exalted): fully powered vestige
    "will of the talon (exalted)": ("B", 0.38),
    # Lash of Shadows (Exalted): fully powered vestige
    "lash of shadows (exalted)": ("B", 0.35),
    # Calimemnon Crystal: fire/ice control, powerful AoE
    "calimemnon crystal": ("B", 0.30),
    # Orb of Dragonkind: dominate dragons, detect dragons
    "orb of dragonkind": ("B", 0.25),
    # Crown of Horns: powerful necromancy, undead control
    "crown of horns": ("B", 0.20),
    # Baba Yaga's Pestle: +3 weapon component of mortar set
    "baba yagas pestle": ("B", 0.15),
    # Kharash's Promise: powerful oath-bound weapon
    "kharashs promise": ("B", 0.10),
    # Blade of Broken Mirrors (Awakened): mid-power vestige
    "blade of broken mirrors (awakened)": ("B", 0.05),

    # ── C-TIER: Moderate artifacts, niche or limited ────────────────────────
    # Silken Spite (Awakened): mid-power vestige
    "silken spite (awakened)": ("C", 0.95),
    # The Bloody End (Awakened): mid-power vestige
    "the bloody end (awakened)": ("C", 0.90),
    # Mace of the Black Crown (Awakened): mid-power vestige
    "mace of the black crown (awakened)": ("C", 0.85),
    # Grovelthrash (Awakened): mid-power vestige
    "grovelthrash (awakened)": ("C", 0.80),
    # Ruin's Wake (Awakened): mid-power vestige
    "ruins wake (awakened)": ("C", 0.75),
    # Will of the Talon (Awakened): mid-power vestige
    "will of the talon (awakened)": ("C", 0.70),
    # Lash of Shadows (Awakened): mid-power vestige
    "lash of shadows (awakened)": ("C", 0.65),
    # Crown of Lies: deception, disguise, niche utility
    "crown of lies": ("C", 0.60),
    # Orb of Damara: regional effects, niche
    "orb of damara": ("C", 0.55),
    # Wyrmskull Throne: dwarven throne, situational
    "wyrmskull throne": ("C", 0.50),
    # Stone of Golorr: information gathering, niche
    "stone of golorr": ("C", 0.45),
    # Luba's Tarokka of Souls: divination, niche
    "lubas tarokka of souls": ("C", 0.40),
    # Staff of the Forgotten One: powerful but heavy drawbacks
    "staff of the forgotten one": ("C", 0.35),
    # Iggwilv's Cauldron: summoning, niche utility
    "iggwilvs cauldron": ("C", 0.30),
    # Ghaal'duur, the Mighty Dirge: bardic artifact, niche
    "ghaalduur": ("C", 0.25),
    # Grovelthrash (Dormant): low-power vestige
    "grovelthrash (dormant)": ("C", 0.15),
    # Mace of the Black Crown (Dormant): low-power vestige
    "mace of the black crown (dormant)": ("C", 0.10),
    # Ruin's Wake (Dormant): low-power vestige
    "ruins wake (dormant)": ("C", 0.05),

    # ── D-TIER: Weakest artifacts, significant drawbacks or very niche ──────
    # The Bloody End (Dormant): low-power vestige
    "the bloody end (dormant)": ("D", 0.95),
    # Silken Spite (Dormant): low-power vestige
    "silken spite (dormant)": ("D", 0.85),
    # Blade of Broken Mirrors (Dormant): low-power vestige, shapechange limited
    "blade of broken mirrors (dormant)": ("D", 0.75),
    # Will of the Talon (Dormant): low-power vestige
    "will of the talon (dormant)": ("D", 0.65),
    # Lash of Shadows (Dormant): low-power vestige
    "lash of shadows (dormant)": ("D", 0.55),
    # Mask of the Dragon Queen: powerful but extreme drawbacks, corruption
    "mask of the dragon queen": ("D", 0.45),
    # Mighty Servant of Leuk-o: vehicle, very niche, hard to use
    "mighty servant of leuk-o": ("D", 0.35),
    # Draakhorn: single-use alarm, very niche
    "draakhorn": ("D", 0.25),
    # Ruinstone: self-destructive, extreme drawbacks
    "ruinstone": ("D", 0.15),

    # ── Base Vestiges of Divergence (no Dormant/Awakened/Exalted suffix) ────
    # These are generic entries; price at Dormant-equivalent (D-tier, low)
    # NOTE: These patterns must NOT match the suffixed versions, so we use
    # exact-match logic in calculate_artifact_tier_price() for these.
}


def calculate_artifact_tier_price(name: str) -> Optional[float]:
    """Calculate artifact price based on tier assignment.
    
    Returns None if the artifact is not in the tier system.
    Uses the tier's price range and the artifact's sub-score to interpolate.
    """
    # Normalize name for matching
    name_lower = name.lower().replace("'", "").replace("\u2019", "")
    
    # Try longest (most specific) patterns first to avoid partial matches
    # e.g., "grovelthrash (exalted)" must match before "grovelthrash"
    sorted_patterns = sorted(ARTIFACT_TIERS.keys(), key=len, reverse=True)
    
    for pattern in sorted_patterns:
        if pattern in name_lower:
            tier, sub_score = ARTIFACT_TIERS[pattern]
            low, high = ARTIFACT_TIER_PRICES[tier]
            price = low + (high - low) * sub_score
            return round(price, 2)
    
    # Base Vestiges of Divergence (exact name, no suffix) → D-tier floor
    base_vestiges = {
        "blade of broken mirrors", "grovelthrash", "lash of shadows",
        "mace of the black crown", "ruins wake", "silken spite",
        "the bloody end", "will of the talon",
    }
    if name_lower in base_vestiges:
        return 250000.0
    
    return None


def calculate_spell_value(attached_spells: Any) -> float:
    """Calculate the additive value of attached spells.

    Args:
        attached_spells: The attached_spells field from criteria

    Returns:
        Total spell value in gold pieces
    """
    if not attached_spells:
        return 0.0

    total_value = 0.0

    # Handle list format (unlimited use)
    if isinstance(attached_spells, list):
        for spell_name in attached_spells:
            spell_level = get_spell_level(spell_name)
            if spell_level == 0:
                continue
            spell_value = spell_level ** 2 * 500
            total_value += spell_value * 2.0  # Unlimited multiplier
        return total_value

    # Handle dict format
    if isinstance(attached_spells, dict):
        for usage_type, usage_data in attached_spells.items():
            # Skip non-usage keys like 'ability', 'choose', etc.
            if usage_type not in USAGE_MULTIPLIERS:
                continue

            multiplier = USAGE_MULTIPLIERS.get(usage_type, 0.5)

            if isinstance(usage_data, dict):
                # {'1': ['spell1'], '3': ['spell2']}
                # For charge-based spells, freq = charges consumed per cast
                # Higher charge cost means fewer casts per day → LESS valuable
                # For daily/rest-based, freq = times per day → MORE valuable
                is_charge_based = usage_type == "charges"
                for frequency, spells in usage_data.items():
                    # Skip non-frequency keys
                    try:
                        freq = int(str(frequency).replace("e", ""))
                    except ValueError:
                        continue
                    for spell_name in spells:
                        spell_level = get_spell_level(spell_name)
                        if spell_level == 0:
                            continue
                        spell_value = spell_level ** 2 * 500
                        if is_charge_based:
                            # Charge cost: higher cost = fewer uses = less value
                            # Use sqrt to dampen the penalty (spending 4 charges
                            # doesn't make it 4x less valuable, more like 2x)
                            total_value += spell_value * multiplier / (freq ** 0.5)
                        else:
                            total_value += spell_value * multiplier * freq
            elif isinstance(usage_data, list):
                # {'will': ['spell1', 'spell2']}
                for spell_name in usage_data:
                    spell_level = get_spell_level(spell_name)
                    if spell_level == 0:
                        continue
                    spell_value = spell_level ** 2 * 500
                    total_value += spell_value * multiplier

    return total_value


def get_consumable_modifier(criteria: dict) -> float:
    """Return the explicit consumable multiplier for the current item."""
    rarity = criteria.get("rarity", "unknown")
    item_type = str(criteria.get("item_type_code", "") or "").split("|")[0]
    item_name_lower = str(criteria.get("name", "")).lower()

    if criteria.get("is_ammunition", False):
        modifier = 0.25
        if rarity in ("very_rare", "legendary", "artifact"):
            modifier *= 0.05
        return modifier

    if item_type == "P" or any(token in item_name_lower for token in ("potion", "elixir")):
        return 0.50
    if item_type == "SC":
        return 0.70
    if criteria.get("is_poison", False):
        return 0.60
    if item_type == "G" and any(token in item_name_lower for token in ("oil", "ointment")):
        return 0.50
    return 1.0


RARITY_SCALING_BASE = float(RARITY_BASE_PRICES["rare"])


def get_scaled_bonus_additive(additive_table: dict, bonus: int, rarity: str, use_scaling: bool = True) -> float:
    """Scale calibrated rare-tier adders to the current item's rarity base.
    
    For legendary and artifact items, use flat adders to prevent massive inflation
    from rarity scaling. Scaling is only appropriate for common-uncommon-rare items.
    """
    if bonus <= 0:
        return 0.0

    capped_bonus = min(int(bonus), 3)
    fallback_bonus = additive_table[max(additive_table)]
    anchored_additive = float(additive_table.get(capped_bonus, fallback_bonus))
    
    # Only apply rarity scaling for common through very_rare items
    # Legendary and artifact items use flat adders to prevent inflation
    if use_scaling and rarity in ("common", "uncommon", "rare", "very_rare"):
        rarity_base = float(RARITY_BASE_PRICES.get(rarity, RARITY_BASE_PRICES["uncommon"]))
        return anchored_additive * (rarity_base / RARITY_SCALING_BASE)
    else:
        # Flat additive for legendary/artifact (and mundane/unknown as fallback)
        return anchored_additive


def calculate_price(criteria: dict) -> float:
    """Calculate item price based on criteria dict.

    Returns price in gold pieces.
    """
    rarity = criteria.get("rarity", "unknown")
    official_price = criteria.get("official_price_gp")
    req_attune = criteria.get("req_attune", "none")
    item_name_lower = str(criteria.get("name", "")).lower().replace("'", "")

    # Artifact tier-based pricing: overrides all other pricing for artifacts
    # This ensures all artifacts fall within the 250k-1M GP range with
    # tier-appropriate pricing based on practical usability assessment.
    if rarity == "artifact":
        tier_price = calculate_artifact_tier_price(criteria.get("name", ""))
        if tier_price is not None:
            return tier_price
        # Artifacts not in tier system: use algorithmic price but clamp to range
        # (fall through to normal formula, then clamp at the end)

    # Named item pricing overrides: iconic items whose full power isn't captured
    # by the generic formula due to unique abilities (auras, plane shift, etc.)
    # These prices are calibrated to match user-specified target ranges.
    # Format: (name_pattern, override_price, require_weapon)
    NAMED_ITEM_OVERRIDES = [
        # Holy Avenger: +3, 2d10 radiant vs fiends/undead, +2 save bonus aura,
        # advantage on saves vs spells for allies within 10ft. Target: 200k-225k
        ("holy avenger", 225000, False),
        # Greater Silver Sword: +3, advantage on INT/WIS/CHA saves, severs astral
        # cords (instant kill in astral plane), psychic damage. Target: 250k-300k
        ("greater silver sword", 275000, False),
        # "Of the Planes" weapons: +3, can cast Plane Shift (7th level spell),
        # bonus damage to creatures not on their home plane. Target: 125k-150k
        # NOTE: Only matches weapon variants, not "Amulet of the Planes" (wondrous item)
        ("of the planes", 137500, True),
        # Defender: +3, can transfer attack bonus to AC (unique defensive ability).
        # Amalgamated price is 31.5k from DSA/MSRP/DMPG - let amalgamation determine price.
        # Removed override: amalgamated price flows through naturally.
    ]
    
    item_type_code = str(criteria.get("item_type_code", "") or "").split("|")[0]
    is_weapon_type = item_type_code in ("M", "R")
    
    for override_key, override_price, require_weapon in NAMED_ITEM_OVERRIDES:
        if override_key in item_name_lower:
            if require_weapon and not is_weapon_type:
                continue  # Skip non-weapon items for weapon-only overrides
            # Apply attunement modifier (these are all attunement items)
            # But use a lighter discount since the override already accounts for power
            attune_mod = 1.0
            if req_attune == "class":
                attune_mod = 0.95  # Light discount for class restriction
            
            floor = RARITY_FLOORS.get(rarity, 1)
            return max(floor, override_price * attune_mod)

    # Official prices used directly for mundane items
    # NaN check: x == x is False for NaN, so NaN official prices fall through
    if official_price is not None and official_price == official_price and rarity in ("mundane", "none"):
        return float(official_price)

    # Moon-Touched weapons: additive pricing (base weapon + 85 gp)
    # These are common items that shed light like a torch
    # MSRP: 95 gp, DMPG: 75 gp → average 85 gp additive
    if "moon-touched" in item_name_lower and rarity == "common":
        # Get base weapon cost
        base_weapon_cost = 0.0
        for weapon_name, weapon_cost in WEAPON_BASE_COSTS.items():
            if weapon_name != "default" and weapon_name in item_name_lower:
                base_weapon_cost = float(weapon_cost)
                break
        else:
            # Use default if no match
            base_weapon_cost = float(WEAPON_BASE_COSTS["default"])
        
        # Additive: base weapon + 85 gp (average of MSRP 95 and DMPG 75)
        moon_touched_price = base_weapon_cost + 85.0
        
        # Apply floor
        floor = RARITY_FLOORS.get(rarity, 1)
        return max(floor, moon_touched_price)

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

    # Enspelled items: use DSA formula (Base_Enspelled[level] + Item_Cost × 5.0)
    # Extract spell level from item name (e.g., "Enspelled (Level 8) Dagger" -> 8)
    if is_enspelled:
        level_match = re.search(r'Level (\d+)', criteria.get("name", ""))
        cantrip_match = re.search(r'Cantrip', criteria.get("name", ""), re.IGNORECASE)
        
        if level_match:
            spell_level = int(level_match.group(1))
        elif cantrip_match:
            spell_level = 0
        else:
            # Fallback: can't determine level, use rarity-based pricing
            spell_level = None
        
        if spell_level is not None and spell_level in ENSPELLED_BASE_PRICES:
            # Get base enspelled price
            base_enspelled_price = ENSPELLED_BASE_PRICES[spell_level]
            
            # Get item base cost (mundane item cost)
            # Check armor first, then weapons
            item_base_cost = 0.0
            for armor_name, armor_cost in EXPENSIVE_ARMOR_BASES.items():
                if armor_name in item_name_lower:
                    item_base_cost = float(armor_cost)
                    break
            
            # If not armor, check weapons
            if item_base_cost == 0:
                for weapon_name, weapon_cost in WEAPON_BASE_COSTS.items():
                    if weapon_name != "default" and weapon_name in item_name_lower:
                        item_base_cost = float(weapon_cost)
                        break
                else:
                    # Use default weapon cost if no match found
                    if any(w in item_name_lower for w in ["sword", "axe", "hammer", "bow", "dagger", "spear", "staff"]):
                        item_base_cost = float(WEAPON_BASE_COSTS["default"])
            
            # Apply formula: Base_Enspelled + Item_Cost × 1.0
            # DSA does NOT apply attunement modifiers to enspelled items
            enspelled_price = base_enspelled_price + item_base_cost * 1.0
            
            # Apply floor
            floor = RARITY_FLOORS.get(rarity, 1)
            return max(floor, enspelled_price)

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

        # Add AC bonus for magic variants (e.g., Mithral +1 Plate Armor)
        # AC bonus is added AFTER the multiplier (same as normal formula)
        ac_bonus = criteria.get("ac_bonus") or 0
        if ac_bonus > 0:
            material_armor_price += get_scaled_bonus_additive(AC_BONUS_ADDITIVE, ac_bonus, rarity)

        # Return this price directly, bypassing the normal formula
        floor = RARITY_FLOORS.get(rarity, 1)
        return max(floor, material_armor_price)

    # Material ammunition: use ratio-based formula relative to arrow baseline
    # This handles adamantine/mithral/silvered arrows, bolts, bullets, etc.
    # For expensive materials (adamantine, mithral), use custom ratios instead of
    # weight-based scaling to avoid overpricing heavier ammo types.
    is_ammunition = criteria.get("is_ammunition", False)
    if is_ammunition and material and material in MATERIAL_COST_PER_LB:
        # Determine ammunition type from item name
        item_name_lower = str(criteria.get("name", "")).lower().replace("'", "")

        # Check if this is an expensive material that needs ratio-based pricing
        expensive_materials = {"adamantine", "mithral"}
        if material in expensive_materials:
            # Custom ratios relative to arrow baseline (arrow = 1.0x)
            MATERIAL_AMMO_RATIOS = {
                "firearm bullet": 2.0,
                "sling bullet": 1.25,
                "arrow": 1.0,
                "bolt": 1.25,
                "bullet": 1.25,  # fallback (same as sling bullet)
                "needle": 0.5,
            }
            ratio = 1.0  # default (arrow)
            for ammo_type, ammo_ratio in MATERIAL_AMMO_RATIOS.items():
                if ammo_type in item_name_lower:
                    ratio = ammo_ratio
                    break

            # Arrow baseline: weight(0.05) * cost_per_lb * multiplier
            arrow_weight = 0.05
            material_cost_per_lb = MATERIAL_COST_PER_LB.get(material, 100)
            arrow_base = arrow_weight * material_cost_per_lb * MATERIAL_AMMUNITION_MULTIPLIER
            material_price = arrow_base * ratio
        else:
            # For cheaper materials (silver, etc.), weight-based is fine
            weight = 0.05  # Default weight (arrow)
            for ammo_type, ammo_weight in AMMUNITION_WEIGHTS.items():
                if ammo_type in item_name_lower:
                    weight = ammo_weight
                    break
            material_cost_per_lb = MATERIAL_COST_PER_LB.get(material, 100)
            material_price = weight * material_cost_per_lb * MATERIAL_AMMUNITION_MULTIPLIER

        # Apply minimum floor based on material
        min_price = 50 if material == "adamantine" else 25 if material == "mithral" else 10 if material in ("silver", "silvered") else 1
        return max(min_price, material_price)

    # --- Additive bonuses ---
    additive = 0.0

    # Weapon bonus (use the highest of weapon/attack/damage bonus)
    weapon_bonus = max(
        criteria.get("weapon_bonus") or 0,
        criteria.get("weapon_attack_bonus") or 0,
        criteria.get("weapon_damage_bonus") or 0,
    )

    # Simple +N weapons: use amalgamated prices as primary reference
    # These items have a bonus (+1/+2/+3) but no other special properties
    # Amalgamated reference prices (from DSA, MSRP, DMPG):
    # +1 Weapon: 725 gp (DSA:825, MSRP:625)
    # +2 Weapon: 3,400 gp (DSA:3,300, MSRP:3,500)
    # +3 Weapon: 14,950 gp (DSA:9,900, MSRP:20,000)
    # Use calibrated values from WEAPON_BONUS_VALUES
    SIMPLE_BONUS_PRICES = WEAPON_BONUS_VALUES.copy()

    # Check if this is a simple +N weapon (no other special properties)
    is_simple_bonus_item = False
    if weapon_bonus > 0 and weapon_bonus <= 3:
            # Check if this is a simple +N item (no other significant properties)
            has_charges = criteria.get("charges") is not None
            has_spell_scroll = criteria.get("spell_scroll_level") is not None
            has_resistances = _parse_list_field(criteria.get("damage_resistances"))
            has_immunities = _parse_list_field(criteria.get("damage_immunities"))
            has_condition_immunities = _parse_list_field(criteria.get("condition_immunities"))
            has_flight = criteria.get("flight_full") or criteria.get("flight_limited")
            has_teleport = criteria.get("teleportation")
            has_invisibility = criteria.get("invisibility_atwill")
            has_healing = criteria.get("healing_daily_hp") or criteria.get("healing_consumable_avg")
            has_ability_mods = criteria.get("ability_score_mods") and len(criteria.get("ability_score_mods", [])) > 0
            has_wish = criteria.get("wish_effect")
            is_sentient = criteria.get("is_sentient")
            has_extra_damage = (criteria.get("extra_damage_avg") or 0) > 0
            has_ac_bonus = (criteria.get("ac_bonus") or 0) > 0
            has_save_advantage = bool(criteria.get("save_advantage"))
            has_save_bonus = (criteria.get("saving_throw_bonus") or 0) > 0
            has_legendary_resistance = criteria.get("legendary_resistance")
            has_artifact_properties = (
                (criteria.get("minor_beneficial") or 0) > 0 or
                (criteria.get("major_beneficial") or 0) > 0 or
                (criteria.get("minor_detrimental") or 0) > 0 or
                (criteria.get("major_detrimental") or 0) > 0
            )
            has_spell_damage_bonus = (criteria.get("spell_damage_bonus") or 0) > 0
            has_vulnerabilities = len(_parse_list_field(criteria.get("damage_vulnerabilities"))) > 0
            has_environmental_breathing = criteria.get("environmental_breathing")
            has_water_breathing = criteria.get("water_breathing")
            has_grants_language = criteria.get("grants_language")
            has_grants_proficiency = criteria.get("grants_proficiency")
            has_conc_save_bonus = (criteria.get("bonus_saving_throw_concentration") or 0) > 0
            has_death_save_adv = criteria.get("death_save_advantage")
            has_cond_save_adv = len(_parse_list_field(criteria.get("conditional_save_advantage"))) > 0
            has_walk_speed_mod = False
            _speed_mods = criteria.get("speed_mods") or {}
            if isinstance(_speed_mods, dict):
                has_walk_speed_mod = (_speed_mods.get("multiply") or {}).get("walk", 1) > 1 or (_speed_mods.get("bonus") or {}).get("walk", 0) or 0 >= 10

            # Item is "simple" if it only has the bonus and no other major properties
            is_simple_bonus_item = not (
                has_charges or has_spell_scroll or
                (has_resistances and len(has_resistances) > 0) or
                (has_immunities and len(has_immunities) > 0) or
                (has_condition_immunities and len(has_condition_immunities) > 0) or
                has_flight or has_teleport or has_invisibility or
                has_healing or has_ability_mods or has_wish or
                is_sentient or
                is_enspelled or
                material in ("mithral", "adamantine") or
                has_extra_damage or
                has_ac_bonus or
                has_save_advantage or
                has_save_bonus or
                has_legendary_resistance or
                has_artifact_properties or
                has_spell_damage_bonus or
                has_vulnerabilities or
                has_environmental_breathing or
                has_water_breathing or
                has_grants_language or
                has_grants_proficiency or
                has_conc_save_bonus or
                has_death_save_adv or
                has_cond_save_adv or
                has_walk_speed_mod
            )

    if is_simple_bonus_item:
        # Use amalgamated price if available, otherwise use simple bonus base
        amalgamated_price = criteria.get("amalgamated_price")
        if pd.notna(amalgamated_price) and amalgamated_price > 0:
            simple_price = amalgamated_price
            # Do NOT apply attunement modifier to amalgamated prices -
            # guide prices already factor in attunement requirements
        else:
            simple_price = SIMPLE_BONUS_PRICES.get(weapon_bonus, 0)
            # Apply modest rarity scaling for items without amalgamated prices
            # Scaling is conservative to prevent massive inflation
            if simple_price > 0 and rarity != 'artifact':
                rarity_multipliers = {
                    "uncommon": 0.5,
                    "rare": 1.0,
                    "very_rare": 2.0,
                    "legendary": 3.0,  # Reduced from 10.0 to prevent overpricing
                }
                simple_price *= rarity_multipliers.get(rarity, 1.0)
            # Apply attunement modifier only for non-amalgamated prices
            attune_mod = 1.0
            req_attune = criteria.get("req_attune", "none")
            if req_attune == "open":
                attune_mod = 0.90
            elif req_attune == "class":
                attune_mod = 0.80
            simple_price *= attune_mod
        
        if simple_price > 0:
            # Apply property premium for named variants (e.g., Returning weapons)
            for prop_keyword, prop_mult in PROPERTY_PREMIUMS.items():
                if prop_keyword in item_name_lower:
                    simple_price *= prop_mult
                    break
            
            # Apply floor
            floor = RARITY_FLOORS.get(rarity, 1)
            return max(floor, simple_price)

    # Amalgamated price priority: items with multi-source amalgamated prices
    # should use that as the primary reference, with minimal rule-based adjustment.
    # This ensures items like Vorpal Sword, Defender, etc. stay close to guide prices.
    # NOTE: Do NOT apply attunement modifier here - guide prices already factor in attunement.
    amalgamated_price = criteria.get("amalgamated_price")
    price_confidence = criteria.get("price_confidence", "none")
    if pd.notna(amalgamated_price) and amalgamated_price > 0 and price_confidence in ("multi", "solo"):
        amalg_price = float(amalgamated_price)
        
        # Apply floor
        floor = RARITY_FLOORS.get(rarity, 1)
        return max(floor, amalg_price)

    if weapon_bonus > 0:
        additive += get_scaled_bonus_additive(WEAPON_BONUS_ADDITIVE, weapon_bonus, rarity)

    # AC bonus
    ac_bonus = criteria.get("ac_bonus") or 0
    if ac_bonus > 0:
        additive += get_scaled_bonus_additive(AC_BONUS_ADDITIVE, ac_bonus, rarity)

    # Spell attack / save DC bonus (take higher)
    spell_bonus = max(
        criteria.get("spell_attack_bonus") or 0,
        criteria.get("spell_save_dc_bonus") or 0,
    )
    if spell_bonus > 0:
        additive += SPELL_ATTACK_ADDITIVE.get(min(spell_bonus, 3), 10000)

    # Spell damage bonus (e.g., "You gain a +1 bonus to spell damage rolls")
    spell_damage_bonus = criteria.get("spell_damage_bonus") or 0
    if spell_damage_bonus > 0:
        additive += 200 * spell_damage_bonus

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
    resistances = _parse_list_field(criteria.get("damage_resistances"))
    additive += 300 * len(resistances)  # was 2000

    # Immunities
    immunities = _parse_list_field(criteria.get("damage_immunities"))
    additive += 800 * len(immunities)  # was 5000

    # Damage vulnerabilities: items that make you weaker cost less
    vulnerabilities = _parse_list_field(criteria.get("damage_vulnerabilities"))
    additive -= 300 * len(vulnerabilities)

    # Condition immunities
    cond_immune = _parse_list_field(criteria.get("condition_immunities"))
    for cond in cond_immune:
        additive += CONDITION_IMMUNITY_VALUES.get(str(cond).lower(), 400)
    
    # Condition immunity from prose (e.g., Mind Carapace: "immune to the frightened condition")
    cond_immune_prose = _parse_list_field(criteria.get("condition_immunity_prose"))
    for cond in cond_immune_prose:
        additive += CONDITION_IMMUNITY_VALUES.get(str(cond).lower(), 400)
    
    # Saving throw advantage (e.g., Mind Carapace: "advantage on Intelligence, Wisdom, and Charisma saving throws")
    save_advantage = _parse_list_field(criteria.get("save_advantage"))
    if save_advantage:
        # Each ability save advantage is worth ~400gp (similar to condition immunity)
        additive += 400 * len(save_advantage)
    
    # Language known (e.g., Demon Armor: "you know Abyssal")
    language_known = _parse_list_field(criteria.get("language_known"))
    if language_known:
        additive += 100 * len(language_known)  # Minor utility
    
    # Grants language (structured field)
    if criteria.get("grants_language"):
        additive += 100  # Same as language_known
    
    # Grants proficiency (structured field)
    if criteria.get("grants_proficiency"):
        additive += 300  # Minor utility value
    
    # Concentration saving throw bonus (e.g., Orb of Skoraeus: +2)
    conc_save_bonus = criteria.get("bonus_saving_throw_concentration") or 0
    if conc_save_bonus > 0:
        additive += 400 * conc_save_bonus

    # Conditional save advantage (non-ability-targeted, e.g., vs poison, vs gases)
    cond_save_adv = _parse_list_field(criteria.get("conditional_save_advantage"))
    if cond_save_adv:
        additive += 200 * len(cond_save_adv)
    
    # Death saving throw advantage
    if criteria.get("death_save_advantage"):
        additive += 200
    
    # Immune to disease
    if criteria.get("immune_to_disease"):
        additive += 400

    # Unarmed strike bonus (e.g., Demon Armor: "+1 bonus to unarmed strikes")
    unarmed_bonus = criteria.get("unarmed_strike_bonus")
    if unarmed_bonus and unarmed_bonus > 0:
        additive += 500 * unarmed_bonus  # Similar to weapon bonus but less valuable
    
    # Unarmed strike damage (e.g., Demon Armor: "1d8 slashing damage")
    unarmed_dmg = criteria.get("unarmed_strike_damage")
    if unarmed_dmg:
        # Handle list format (from CSV) or string format
        if isinstance(unarmed_dmg, list):
            unarmed_dmg = unarmed_dmg[0] if unarmed_dmg else None
        if unarmed_dmg and isinstance(unarmed_dmg, str):
            from .criteria_extractor import _avg_dice
            additive += _avg_dice(unarmed_dmg) * 50  # Scale damage to gp
    
    # Spell casting abilities (e.g., Armor of the Fallen: "cast Speak with Dead or Animate Dead")
    spell_abilities = _parse_list_field(criteria.get("spell_casting_abilities"))
    if spell_abilities:
        for spell_name in spell_abilities:
            spell_level = get_spell_level(spell_name)
            if spell_level > 0:
                # Once-per-day spell casting is worth spell_level^2 * 200
                additive += spell_level ** 2 * 200
            else:
                # Unknown spell, give minor value
                additive += 200

    # Movement
    if criteria.get("flight_full"):
        additive += 10000   # bumped for flight value
    elif criteria.get("flight_limited"):
        additive += 1000   # was 5000

    if criteria.get("swim_speed"):
        additive += 800    # Permanent swim speed is a significant utility
    if criteria.get("climb_speed"):
        additive += 300    # was 2000
    if criteria.get("burrow_speed"):
        additive += 500    # was 3000

    # Environmental breathing
    if criteria.get("environmental_breathing"):
        additive += 500
    
    # Water breathing
    if criteria.get("water_breathing"):
        additive += 300

    # Walk speed modifications (from structured modifySpeed field)
    # Handles multiply (Boots of Speed: walk x2) and bonus modifiers
    speed_mods = criteria.get("speed_mods") or {}
    if isinstance(speed_mods, dict):
        if "multiply" in speed_mods and isinstance(speed_mods["multiply"], dict):
            walk_mult = speed_mods["multiply"].get("walk", 1)
            if walk_mult > 1:
                additive += 2000 * (walk_mult - 1)
        if "bonus" in speed_mods and isinstance(speed_mods["bonus"], dict):
            walk_bonus = speed_mods["bonus"].get("walk", 0) or 0
            if walk_bonus >= 10:
                additive += 200 * (walk_bonus // 10)

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

    # Legendary resistance
    if criteria.get("legendary_resistance"):
        additive += 3000  # Powerful defensive ability
    
    # Spell absorption
    if criteria.get("spell_absorption"):
        additive += 5000  # Very powerful

    # Healing
    healing_daily = criteria.get("healing_daily_hp") or 0
    if healing_daily > 0:
        additive += 200 * healing_daily  # Daily emergency healing is valuable

    healing_consumable = criteria.get("healing_consumable_avg") or 0.0
    if healing_consumable > 0:
        additive += 10 * healing_consumable  # was 50

    # Tome / manual permanent boost
    if criteria.get("tome_manual_boost"):
        additive += 15000  # was 100000; manuals amalgamate ~41,500 at VR base ~13,500

    # Wish effect (ring of three wishes, similar items)
    if criteria.get("wish_effect"):
        additive += 50000 # bumped for wish effect

    # Artifact random properties (beneficial/detrimental)
    # These are randomly determined properties from the DMG tables
    # Minor beneficial: +20,000 gp each (e.g., "While attuned, you can't be surprised")
    # Major beneficial: +40,000 gp each (e.g., "You are immune to disease")
    # Minor detrimental: -10,000 gp each (e.g., "You glow dimly in darkness")
    # Major detrimental: -20,000 gp each (e.g., "You have vulnerability to fire")
    # Note: Detrimental properties reduce price but are offset by beneficial ones
    minor_beneficial = criteria.get("minor_beneficial") or 0
    major_beneficial = criteria.get("major_beneficial") or 0
    minor_detrimental = criteria.get("minor_detrimental") or 0
    major_detrimental = criteria.get("major_detrimental") or 0

    if minor_beneficial > 0:
        additive += 20000 * minor_beneficial
    if major_beneficial > 0:
        additive += 40000 * major_beneficial
    if minor_detrimental > 0:
        additive -= 10000 * minor_detrimental
    if major_detrimental > 0:
        additive -= 20000 * major_detrimental

    # Staff of the Forgotten One: fixed beneficial/detrimental properties (hardcoded from extractor)
    staff_beneficial = criteria.get("staff_forgotten_one_beneficial") or 0
    staff_detrimental = criteria.get("staff_forgotten_one_detrimental") or 0
    if staff_beneficial > 0:
        additive += staff_beneficial
    if staff_detrimental > 0:
        additive -= staff_detrimental

    # Moonblade properties (d100 table runes — each rune adds extra weapon bonus, damage, or utility)
    # The user requested bringing Moonblade closer to the artifact average.
    # We increase the modifier per property to 35,000 gp
    moonblade_properties = criteria.get("moonblade_properties") or 0
    if moonblade_properties > 0:
        additive += 35000 * moonblade_properties

    # Charges: rechargeable charges add moderate value; non-rechargeable add less
    # Exception: flavor items (no tactical value) use much lower valuation
    charges = criteria.get("charges")
    if charges and charges == charges: # not None, not NaN
        # Handle dice strings like "{@dice 1d3}" by extracting the numeric part
        if isinstance(charges, str):
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
            item_name_lower = str(criteria.get("name", "")).lower().replace("'", "")
            is_flavor_item = item_name_lower in FLAVOR_ITEMS
            
            # Check if this item has attached spells (charges used to cast spells)
            # Items WITH spells: charges enable spell-casting (Staff of Power, Staff of the Magi)
            #   → flat rate per charge is appropriate (spell value calculated separately)
            # Items WITHOUT spells: charges power non-spell effects (healing, creating objects)
            #   → diminishing returns (sqrt) since high charge counts typically mean weak per-charge effects
            #   e.g., Hag-Stitched Troll Leather (50 charges, 1 HP each) vs Staff of Power (20 charges, spells)
            attached_spells = criteria.get("attached_spells")
            has_spell_charges = False
            if attached_spells:
                # Handle string representation from CSV
                if isinstance(attached_spells, str):
                    try:
                        import ast
                        attached_spells = ast.literal_eval(attached_spells)
                    except (ValueError, SyntaxError):
                        pass
                if isinstance(attached_spells, dict) and "charges" in attached_spells:
                    has_spell_charges = True
                elif isinstance(attached_spells, list) and len(attached_spells) > 0:
                    has_spell_charges = True
            
            recharge = str(criteria.get("recharge") or "")
            if is_flavor_item:
                # Flavor items: minimal charge value (just the novelty)
                additive += 10 * charges
            elif recharge in ("dawn", "restLong", "dusk"):
                if has_spell_charges:
                    additive += 500 * charges # Spell-casting charges: flat rate (Staff of Power has 20)
                else:
                    # Non-spell charges: diminishing returns via sqrt
                    # sqrt(50) * 500 ≈ 3,535 vs 50 * 500 = 25,000
                    # sqrt(20) * 500 ≈ 2,236 vs 20 * 500 = 10,000
                    additive += int(500 * math.sqrt(charges))
            elif recharge in ("restShort",):
                if has_spell_charges:
                    additive += 750 * charges # Short rest recharge: higher value
                else:
                    additive += int(750 * math.sqrt(charges))
            else:
                additive += 100 * charges # Non-rechargeable: lower value per charge

    # Extra damage (e.g., Holy Avenger 2d10 radiant, Dragonlance 3d6, etc.)
    # This is damage dealt on every hit (or conditionally), extracted from prose
    # NOTE: Skip for Moonblade items - their extra damage is already captured
    # in moonblade_properties (the random rune abilities include damage bonuses)
    extra_damage_avg = criteria.get("extra_damage_avg") or 0
    has_moonblade_props = (criteria.get("moonblade_properties") or 0) > 0
    if extra_damage_avg > 0 and not has_moonblade_props:
        # Scale: 3000 gp per point of average damage for legendary/artifact,
        # 1500 gp per point for lower rarities
        if rarity in ("legendary", "artifact"):
            additive += 3000 * extra_damage_avg
        else:
            additive += 1500 * extra_damage_avg

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

    # Attached spells: calculate value based on spell levels and usage
    attached_spells = criteria.get("attached_spells")
    if attached_spells:
        spell_value = calculate_spell_value(attached_spells)
        additive += spell_value

    # --- Multiplicative modifiers ---
    attune_mod = 1.0
    req_attune = criteria.get("req_attune", "none")
    if req_attune == "open":
        attune_mod = 0.90   # was 0.85
    elif req_attune == "class":
        attune_mod = 0.80   # was 0.75

    consumable_mod = get_consumable_modifier(criteria)

    material_mod = 1.0  # mithral/adamantine handled in NLP

    # Property items (e.g., "Sword of Fire", "Shield of Warning"): apply premium multiplier
    # Only applies if item has recognized property AND doesn't already have other pricing
    if " of " in item_name_lower and rarity not in ("mundane", "none", "unknown", "varies"):
        property_multiplier = 1.0
        item_name_lower_stripped = item_name_lower.replace("+1 ", "").replace("+2 ", "").replace("+3 ", "")
        
        # Check for known property keywords
        for prop_keyword, prop_mult in PROPERTY_PREMIUMS.items():
            if prop_keyword in item_name_lower_stripped:
                property_multiplier = max(property_multiplier, prop_mult)
                break  # Use the highest match
        
        # Apply property multiplier
        if property_multiplier > 1.0:
            additive *= property_multiplier

    curse_mod = 0.75 if criteria.get("is_cursed") else 1.0 # was 0.70
    
    # Specific curse effects from prose (e.g., Demon Armor: "disadvantage vs demons")
    # These provide additional curse penalties beyond the generic curse flag
    curse_effects = _parse_list_field(criteria.get("curse_effects"))
    if curse_effects:
        # Each curse effect adds an additional 5% price reduction
        curse_mod *= max(0.5, 1.0 - 0.05 * len(curse_effects))
    sentient_mod = 1.15 if criteria.get("is_sentient") else 1.0 # was 1.25

    # Flavor items: apply discount (no tactical/combat value)
    # Staff of Flowers, Wand of Smiles, etc. are priced ~50-60 gp in guides
    # vs our base of 100 gp, so we need a ~0.5x multiplier
    flavor_mod = 0.5 if item_name_lower in FLAVOR_ITEMS else 1.0

    # Legendary/artifact power scaling: items with significant properties at these
    # tiers should be priced substantially higher than the base + additive formula
    # produces. This reflects that legendary items are meant to be rare, powerful,
    # and expensive. The multiplier scales with the number of significant properties.
    # NOTE: Properties already valued in the additive (moonblade_properties, artifact
    # properties) are NOT counted here to avoid double-counting.
    legendary_power_mult = 1.0
    if rarity == "legendary" and additive > 5000:
        # Count significant properties to determine scaling
        sig_props = 0
        if (criteria.get("extra_damage_avg") or 0) > 0 and not has_moonblade_props:
            sig_props += 1
        if (criteria.get("saving_throw_bonus") or 0) > 0:
            sig_props += 1
        if criteria.get("save_advantage"):
            save_adv = criteria.get("save_advantage")
            if isinstance(save_adv, list):
                sig_props += len(save_adv)
            else:
                sig_props += 1
        if criteria.get("teleportation"):
            sig_props += 2  # Teleportation/plane shift is very powerful at legendary tier
        if criteria.get("flight_full"):
            sig_props += 1
        if criteria.get("spell_absorption"):
            sig_props += 1
        if criteria.get("legendary_resistance"):
            sig_props += 1
        if criteria.get("spell_damage_bonus") and (criteria.get("spell_damage_bonus") or 0) > 0:
            sig_props += 1
        if criteria.get("environmental_breathing"):
            sig_props += 1
        if criteria.get("water_breathing"):
            sig_props += 1
        if criteria.get("invisibility_atwill"):
            sig_props += 1
        # Do NOT count moonblade_properties here - already valued at 35k each in additive
        # Scale: 1.0 base + 0.5 per significant property, capped at 4.0
        legendary_power_mult = min(4.0, 1.0 + 0.5 * sig_props)
    elif rarity == "artifact" and additive > 10000:
        legendary_power_mult = 1.9  # Artifact boost calibrated to target ~800k max

    price = (base + base_item_cost + additive) * attune_mod * consumable_mod * material_mod * curse_mod * sentient_mod * flavor_mod * legendary_power_mult

    # Gleaming: add premium on top of base armor cost
    # Reference guides: DSA=330, MSRP=95, avg=212.5 gp for generic "Armor of Gleaming"
    # Premium = gleaming_avg - mundane_base (using 200 as the premium)
    if "gleaming" in item_name_lower and base_item_cost > 0:
        price += 200


    floor = RARITY_FLOORS.get(rarity, 1)
    price = max(floor, price)

    # Cap algorithm-only ammunition (slaying, bloodseeker, etc.) at 1.2× the +3 ammo price
    # +3 ammo amalgamated price is ~644 gp, so cap = 773 gp
    # This only applies to algorithm-priced ammo (no amalgamated price), not amalgamated items
    is_ammunition = criteria.get("is_ammunition", False)
    if is_ammunition and price > 773:
        amalgamated_price = criteria.get("amalgamated_price")
        price_confidence = criteria.get("price_confidence", "none")
        has_amalgamated = pd.notna(amalgamated_price) and amalgamated_price > 0 and price_confidence in ("multi", "solo")
        if not has_amalgamated:
            price = min(price, 773)

    # Clamp any artifact not handled by tier system to 250k-1M range
    if rarity == "artifact":
        price = max(250000, min(1000000, price))

    return price


def calculate_price_with_outlier_check(criteria: dict) -> tuple[float, str]:
    """
    Calculate price with single-source outlier detection.

    Returns:
        (price, price_source): The calculated price and its source type
    """
    # Get amalgamated price info
    amalgamated_price = criteria.get("amalgamated_price")
    price_confidence = criteria.get("price_confidence", "none")

    # Check for single-source outlier flag from amalgamator
    if price_confidence == "solo-outlier":
        # Use rule-based price instead of amalgamated price
        rule_price = calculate_price(criteria)
        return (rule_price, "rule-outlier-detected")

    # Normal pricing
    price = calculate_price(criteria)

    # Determine source
    # Note: amalgamated price is used for R² comparison only, not blended into final price
    source = "rule"

    return (price, source)


def calculate_composite_features(criteria: dict) -> dict:
    """
    Calculate composite features for ML model.
    
    These features capture interactions and aggregated power levels.
    
    Returns:
        dict with keys: power_score, defensive_score, spell_complexity,
        interaction_weapon_damage, interaction_flight_invisibility
    """
    features = {}
    
    # Power score: combines offensive bonuses and damage
    weapon_bonus = criteria.get("weapon_bonus") or 0
    spell_attack_bonus = criteria.get("spell_attack_bonus") or 0
    extra_damage_avg = criteria.get("extra_damage_avg") or 0
    features["power_score"] = (
        weapon_bonus + 
        spell_attack_bonus + 
        (extra_damage_avg / 1000)  # Scale down to be comparable to bonus levels
    )
    
    # Defensive score: combines AC bonus, resistances, immunities
    ac_bonus = criteria.get("ac_bonus") or 0
    resistances = _parse_list_field(criteria.get("damage_resistances"))
    immunities = _parse_list_field(criteria.get("damage_immunities"))
    condition_immunities = _parse_list_field(criteria.get("condition_immunities"))
    
    features["defensive_score"] = (
        ac_bonus + 
        2 * len(resistances) + 
        3 * len(immunities) + 
        2 * len(condition_immunities)
    )
    
    # Spell complexity: combines spell count and spellcasting bonuses
    attached_spells = criteria.get("attached_spells") or []
    spell_save_dc_bonus = criteria.get("spell_save_dc_bonus") or 0
    spell_damage_bonus = criteria.get("spell_damage_bonus") or 0
    
    # Count spells
    spell_count = 0
    if isinstance(attached_spells, list):
        spell_count = len(attached_spells)
    elif isinstance(attached_spells, dict):
        # Count all spells in the dict structure
        for usage_type, usage_data in attached_spells.items():
            if usage_type not in ["ability", "choose", "options"]:
                if isinstance(usage_data, list):
                    spell_count += len(usage_data)
                elif isinstance(usage_data, dict):
                    for freq, spells in usage_data.items():
                        if isinstance(spells, list):
                            spell_count += len(spells)
    
    features["spell_complexity"] = (
        spell_count + 
        spell_attack_bonus + 
        spell_save_dc_bonus +
        spell_damage_bonus
    )
    
    # Interaction: weapon bonus + extra damage synergy
    # High weapon bonus combined with extra damage is particularly valuable
    features["interaction_weapon_damage"] = weapon_bonus * extra_damage_avg if extra_damage_avg > 0 else 0
    
    # Interaction: flight + invisibility synergy
    # Both together are more powerful than separately
    flight_full = criteria.get("flight_full") or False
    flight_limited = criteria.get("flight_limited") or False
    invisibility_atwill = criteria.get("invisibility_atwill") or False
    has_flight = flight_full or flight_limited
    features["interaction_flight_invisibility"] = 1.0 if has_flight and invisibility_atwill else 0.0
    
    return features
