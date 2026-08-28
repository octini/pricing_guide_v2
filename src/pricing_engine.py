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
from .constants import CONDITION_IMMUNITY_VALUES, EXPENSIVE_ARMOR_BASES, RARITY_MEDIANS
from .list_curation import is_commodity_exact_price_candidate, official_price_gp


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

# ─── Tiered pricing authority thresholds ─────────────────────────────────────
CRITERIA_RICH_THRESHOLD = 3
GUIDE_DIVERGENCE_THRESHOLD = 0.60


def compute_criteria_coverage(criteria: dict) -> int:
    """Count distinct price-bearing criteria the extractor found.

    Spec-defined buckets (11): weapon/ac/spell bonuses, resistances,
    immunities, extra_damage_avg, save_advantage, flight, material,
    sentience, curse — the inputs pricing_engine's additive/multiplicative
    stacks actually consume. Each bucket counts once regardless of magnitude.
    >=3 = criteria-rich.

    Null-safe: NaN/pd.NA/None/strings never count as present; count only
    finite values >0 where numeric.
    """
    count = 0

    def _finite_positive(v) -> bool:
        if v is None:
            return False
        try:
            if pd.isna(v):
                return False
        except Exception:
            return False
        if isinstance(v, str):
            return False
        try:
            f = float(v)
        except (TypeError, ValueError):
            return False
        if not math.isfinite(f):
            return False
        return f > 0

    def _is_true_bool(v) -> bool:
        if v is None:
            return False
        try:
            if pd.isna(v):
                return False
        except Exception:
            return False
        if isinstance(v, str):
            return False
        # strict bool check — only True counts (handles python bool & numpy bool)
        if isinstance(v, bool):
            return v is True
        try:
            import numpy as np  # local
            if isinstance(v, np.bool_):
                return bool(v) is True
        except Exception:
            pass
        return v is True

    # weapon bonus (any of weapon_bonus / attack / damage)
    if any(_finite_positive(criteria.get(k)) for k in ("weapon_bonus", "weapon_attack_bonus", "weapon_damage_bonus")):
        count += 1
    # ac bonus
    if _finite_positive(criteria.get("ac_bonus")):
        count += 1
    # spell bonuses (attack / save dc / damage)
    if any(_finite_positive(criteria.get(k)) for k in ("spell_attack_bonus", "spell_save_dc_bonus", "spell_damage_bonus")):
        count += 1
    # resistances
    if len(_parse_list_field(criteria.get("damage_resistances"))) > 0:
        count += 1
    # immunities (damage or condition)
    if (
        len(_parse_list_field(criteria.get("damage_immunities"))) > 0
        or len(_parse_list_field(criteria.get("condition_immunities"))) > 0
        or len(_parse_list_field(criteria.get("condition_immunity_prose"))) > 0
    ):
        count += 1
    # extra_damage_avg — only finite >0 numeric
    if _finite_positive(criteria.get("extra_damage_avg")):
        count += 1
    # save_advantage (includes save_advantage and conditional)
    if (
        len(_parse_list_field(criteria.get("save_advantage"))) > 0
        or len(_parse_list_field(criteria.get("conditional_save_advantage"))) > 0
        or _is_true_bool(criteria.get("death_save_advantage"))
    ):
        count += 1
    # flight
    if _is_true_bool(criteria.get("flight_full")) or _is_true_bool(criteria.get("flight_limited")):
        count += 1
    # material
    material = criteria.get("material")
    if material is not None:
        try:
            if pd.isna(material):
                pass
            else:
                m_str = str(material).strip().lower()
                if m_str and m_str not in ("", "none", "nan", "unknown", "null", "<na>"):
                    count += 1
        except Exception:
            pass
    # sentience
    if _is_true_bool(criteria.get("is_sentient")):
        count += 1
    # curse (is_cursed or curse_effects)
    if _is_true_bool(criteria.get("is_cursed")) or len(_parse_list_field(criteria.get("curse_effects"))) > 0:
        count += 1
    return count


def compute_guide_spread(
    dsa_price: Any = None,
    msrp_price: Any = None,
    dmpg_price: Any = None,
    price_sources: Any = None,
) -> Optional[float]:
    """Guide spread = (max-min)/mean across guides post-trim.

    Args:
        dsa_price, msrp_price, dmpg_price: raw guide prices (may be None/NaN/inf).
        price_sources: optional comma-separated string like "DSA,MSRP"
            indicating which guides survived trim/outlier filtering. When
            missing/empty-string/pd.NA → return None (unknown → conservative
            anchor-wins path), NOT "use all guides".

    Returns None when fewer than 2 guides contribute or mean ≤0 or non-finite;
    otherwise float. >0.60 = high divergence. Rejects non-finite (inf/-inf/NaN)
    guide prices before computing.
    """
    import pandas as pd  # local to avoid circular

    # Missing/empty price_sources → unknown → conservative anchor-wins (None)
    if price_sources is None:
        return None
    if isinstance(price_sources, (list, tuple, set)):
        # Filter out NA/empty entries first (check list/tuple/set BEFORE pd.isna scalar — pd.isna(list) raises)
        cleaned: list[str] = []
        for a in price_sources:
            try:
                if pd.isna(a):
                    continue
            except Exception:
                pass
            if isinstance(a, str):
                s = a.strip()
                if not s:
                    continue
                cleaned.append(s)
            elif a is None:
                continue
            else:
                # coerce non-string (e.g. numbers) to string?
                try:
                    s = str(a).strip()
                    if s and s.lower() not in ("nan", "none", "null"):
                        cleaned.append(s)
                except Exception:
                    continue
        if not cleaned:
            return None
        allowed_upper = {str(a).upper() for a in cleaned}
        candidates = {k: v for k, v in {"DSA": dsa_price, "MSRP": msrp_price, "DMPG": dmpg_price}.items() if k in allowed_upper}
    else:
        try:
            if pd.isna(price_sources):
                return None
        except Exception:
            return None
        if isinstance(price_sources, str):
            stripped = price_sources.strip()
            if not stripped:
                return None
            allowed = {s.strip() for s in stripped.split(",") if s.strip()}
            if not allowed:
                return None
            allowed_upper = {a.upper() for a in allowed}
            candidates: dict[str, Any] = {k: v for k, v in {"DSA": dsa_price, "MSRP": msrp_price, "DMPG": dmpg_price}.items() if k in allowed_upper}
        else:
            # Unexpected type (e.g. float, int) → treat as missing
            return None

    prices: list[float] = []
    for p in candidates.values():
        if p is None:
            continue
        try:
            if pd.isna(p):
                continue
        except Exception:
            pass
        if isinstance(p, str):
            s = p.strip()
            if not s:
                continue
        try:
            f = float(p)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(f):
            continue
        if f <= 0:
            continue
        prices.append(f)
    if len(prices) < 2:
        return None
    mean = sum(prices) / len(prices)
    if not math.isfinite(mean) or mean <= 0:
        return None
    spread = (max(prices) - min(prices)) / mean
    if not math.isfinite(spread):
        return None
    return float(spread)


def compute_guide_spread_from_criteria(criteria: dict) -> Optional[float]:
    """Convenience wrapper: compute spread directly from criteria dict."""
    return compute_guide_spread(
        criteria.get("dsa_price"),
        criteria.get("msrp_price"),
        criteria.get("dmpg_price"),
        criteria.get("price_sources"),
    )


# ─── Price authority: branch-derived ─────────────────────────────────────────
def _has_valid_amalgamated(criteria: dict) -> bool:
    amalg = criteria.get("amalgamated_price")
    if amalg is None:
        return False
    try:
        if pd.isna(amalg):
            return False
    except Exception:
        return False
    try:
        f = float(amalg)
    except (TypeError, ValueError):
        return False
    if not math.isfinite(f):
        return False
    return f > 0


def _is_criteria_rich(criteria_coverage: Optional[int]) -> bool:
    if criteria_coverage is None:
        return False
    try:
        if pd.isna(criteria_coverage):
            return False
    except Exception:
        return False
    try:
        # strings never count; direct float/int check via _finite logic
        if isinstance(criteria_coverage, str):
            return False
        f = float(criteria_coverage)
    except (TypeError, ValueError):
        return False
    if not math.isfinite(f):
        return False
    return int(f) >= CRITERIA_RICH_THRESHOLD


def _is_guide_divergent(guide_spread: Optional[float]) -> bool:
    if guide_spread is None:
        return False
    try:
        if pd.isna(guide_spread):
            return False
    except Exception:
        return False
    try:
        f = float(guide_spread)
    except (TypeError, ValueError):
        return False
    if not math.isfinite(f):
        return False
    return f > GUIDE_DIVERGENCE_THRESHOLD


def derive_price_authority(
    criteria: dict,
    criteria_coverage: Optional[int],
    guide_spread: Optional[float],
    price_source: Optional[str] = None,
) -> str:
    """Derive price_authority from the pricing branch actually taken.

    Anchor ⟺ amalgamated_price >0 AND confidence multi/solo AND NOT rich+divergent.
    Formula only when the formula branch produced the price (rich+divergent overriding anchor).
    None-args backward compat: when coverage/spread is None, should_force is False → anchor wins if applicable.
    Solo-outlier and official are explicit branches.
    Re-evaluates branch conditions by design — kept identical to pricing branch logic; covered by consistency test.
    """
    if price_source == "official":
        return "official"
    _pc_raw = criteria.get("price_confidence")
    try:
        if pd.isna(_pc_raw):
            _pc_raw = None
    except Exception:
        pass
    price_conf = str(_pc_raw or "none")
    if price_conf == "solo-outlier":
        return "rule-outlier"
    has_amalg = _has_valid_amalgamated(criteria)
    is_rich = _is_criteria_rich(criteria_coverage)
    is_div = _is_guide_divergent(guide_spread)
    should_force = is_rich and is_div and price_conf in ("multi", "solo")
    if has_amalg and price_conf in ("multi", "solo") and not should_force:
        return "anchor"
    if should_force and has_amalg and price_conf in ("multi", "solo"):
        return "formula"
    return "rule"


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

EXTRA_DAMAGE_CONDITION_MULTIPLIERS = {
    "unconditional": 1.0,
    "vs_creature_type": 0.25,
    "on_crit": 0.05,
}

# ─── Save advantage tiering ───────────────────────────────────────────────
# Base value for a BROAD save advantage (e.g. "advantage on all saving throws"
# or on all saves of one ability). CATEGORY and SITUATIONAL are discounted
# because they apply to a narrower set of effects or only in a specific state.
# Documented per spec: BROAD 1.0×, CATEGORY 0.5×, SITUATIONAL 0.25×.
SAVE_ADVANTAGE_BASE_VALUE = 400
SAVE_ADVANTAGE_CATEGORY_MULTIPLIER = 0.5
SAVE_ADVANTAGE_SITUATIONAL_MULTIPLIER = 0.25
SAVE_ADVANTAGE_TIER_BROAD = "BROAD"
SAVE_ADVANTAGE_TIER_CATEGORY = "CATEGORY"
SAVE_ADVANTAGE_TIER_SITUATIONAL = "SITUATIONAL"

# ─── Wave-1 prose criteria pricing (temp HP, HP-max, initiative) ────────────
# Documented guesses; tuned in hop 2. Mirrors existing prose-criteria pattern
# (e.g. healing_daily_hp, save_advantage_broad) — read via criteria.get and
# add to additive.
TEMP_HP_RATE = 40  # gp per avg temp-HP point before freq multiplier
TEMP_HP_FREQ_MULTIPLIER = {
    "per_action": 1.0,
    "on_kill": 0.5,
    "daily": 0.25,
    "unclassified": 0.25,
}
HP_MAX_RATE = 40  # gp per HP-max point (flat + per_level * ref_level)
HP_MAX_REF_LEVEL = 5  # reference character level for per-level HP-max scaling
INIT_BONUS_RATE = 300  # gp per +1 initiative bonus
INIT_ADVANTAGE_FLAT = 600  # gp for advantage on initiative


def extra_damage_pricing_multiplier(criteria: dict[str, Any]) -> float:
    """Return pricing-only multiplier for conditional extra damage.

    Raw ``extra_damage_avg`` remains the truthful per-hit dice average for reporting/ML.
    The multiplier only discounts rule-formula additive value for conditional uptime.
    """
    condition = str(criteria.get("extra_damage_condition") or "unconditional")
    raw_multiplier = criteria.get("extra_damage_multiplier")
    try:
        multiplier = float(raw_multiplier)
    except (TypeError, ValueError):
        multiplier = EXTRA_DAMAGE_CONDITION_MULTIPLIERS.get(condition, 1.0)
    if multiplier != multiplier:  # NaN
        multiplier = EXTRA_DAMAGE_CONDITION_MULTIPLIERS.get(condition, 1.0)
    return max(0.0, min(multiplier, 1.0))


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

# EXPENSIVE_ARMOR_BASES is now canonical in src/constants.py — imported above

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


def calculate_price(
    criteria: dict,
    criteria_coverage: Optional[int] = None,
    guide_spread: Optional[float] = None,
) -> float:
    """Calculate item price based on criteria dict.

    Tiered authority: when price_confidence is multi/solo and
    criteria_coverage >=3 and guide_spread >0.60, the rule formula
    (max floor, base+additive...) wins over the amalgamated anchor.
    Otherwise anchor wins (current behavior). Passing None for the two
    new params preserves backward-compat identical output.

    Returns price in gold pieces.
    """
    rarity = criteria.get("rarity", "unknown")
    official_price = criteria.get("official_price_gp")
    req_attune = criteria.get("req_attune", "none")
    item_name_lower = str(criteria.get("name", "")).lower().replace("'", "")
    item_type_code = str(criteria.get("item_type_code", "") or "").split("|")[0]

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
    if is_commodity_exact_price_candidate(criteria):
        return float(official_price_gp(criteria))
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
            # Tiered authority: criteria-rich + high divergence forces formula over simple anchor
            _tier_is_rich = criteria_coverage is not None and criteria_coverage >= CRITERIA_RICH_THRESHOLD
            _tier_is_div = guide_spread is not None and guide_spread > GUIDE_DIVERGENCE_THRESHOLD
            _tier_conf_raw = criteria.get("price_confidence")
            try:
                if pd.isna(_tier_conf_raw):
                    _tier_conf_raw = None
            except Exception:
                pass
            _tier_conf = str(_tier_conf_raw or "none")
            if _tier_is_rich and _tier_is_div and _tier_conf in ("multi", "solo"):
                is_simple_bonus_item = False

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
            
            # Focus premium: spellcasting focus is a convenience feature worth +300
            if criteria.get("is_focus"):
                simple_price += 300
            
            # Apply floor
            floor = RARITY_FLOORS.get(rarity, 1)
            return max(floor, simple_price)

    # Amalgamated price priority: items with multi-source amalgamated prices
    # should use that as the primary reference, with minimal rule-based adjustment.
    # This ensures items like Vorpal Sword, Defender, etc. stay close to guide prices.
    # NOTE: Do NOT apply attunement modifier here - guide prices already factor in attunement.
    amalgamated_price = criteria.get("amalgamated_price")
    _pc_raw = criteria.get("price_confidence")
    try:
        if pd.isna(_pc_raw):
            _pc_raw = None
    except Exception:
        pass
    price_confidence = str(_pc_raw or "none")
    # Tiered authority: anchor wins unless criteria-rich AND high-divergence → formula wins
    _is_rich = criteria_coverage is not None and criteria_coverage >= CRITERIA_RICH_THRESHOLD
    _is_div = guide_spread is not None and guide_spread > GUIDE_DIVERGENCE_THRESHOLD
    _should_force_formula = _is_rich and _is_div and price_confidence in ("multi", "solo")
    if pd.notna(amalgamated_price) and amalgamated_price > 0 and price_confidence in ("multi", "solo") and not _should_force_formula:
        amalg_price = float(amalgamated_price)
        # Apply floor
        floor = RARITY_FLOORS.get(rarity, 1)
        return max(floor, amalg_price)
    # else: formula wins (fall through) or no anchor — compute rule formula

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
    
    # Saving throw advantage: tiered pricing by breadth
    # BROAD (all saves or single ability, always-on) = 1.0× base (400 gp)
    # CATEGORY (vs condition/creature-type/damage/spell, e.g. "vs frightened", "vs spells", "to avoid or end paralyzed") = 0.5× (200 gp)
    # SITUATIONAL (state/position-gated, e.g. "while at 0 hp", "while mounted") = 0.25× (100 gp)
    # Backward compatible: missing tier data → all BROAD (original flat 400 gp behavior).
    # Fixes Bracers-of-Celerity class: "saving throws to avoid or end paralyzed/restrained" was BROAD but is CATEGORY.
    save_advantage = _parse_list_field(criteria.get("save_advantage"))
    if save_advantage:
        # Prefer explicit per-tier counts when present (emitted by criteria_extractor)
        broad = criteria.get("save_advantage_broad")
        category = criteria.get("save_advantage_category")
        situational = criteria.get("save_advantage_situational")
        tiers = criteria.get("save_advantage_tiers")
        has_tier_counts = broad is not None or category is not None or situational is not None
        has_tiers_list = tiers is not None
        # Normalize tier counts (handle NaN/string from CSV)
        def _int_or_zero(v):
            if v is None:
                return 0
            try:
                if isinstance(v, float) and v != v:  # NaN
                    return 0
                return int(float(v)) if isinstance(v, str) else int(v)
            except (TypeError, ValueError):
                return 0
        if has_tier_counts:
            b = max(0, _int_or_zero(broad))
            cat = max(0, _int_or_zero(category))
            sit = max(0, _int_or_zero(situational))
            n = len(save_advantage)
            # Cap category/situational counts at len(save_advantage) to never overprice
            cat = min(cat, n)
            sit = min(sit, n)
            b = min(b, n)
            # If counts are present but all zero yet save_advantage non-empty, fall back to BROAD or tiers list
            if b == 0 and cat == 0 and sit == 0 and n > 0:
                if has_tiers_list:
                    parsed_tiers = _parse_list_field(tiers)
                    if parsed_tiers:
                        # Truncate tier-list longer than targets
                        parsed_tiers = parsed_tiers[:n]
                        for t in parsed_tiers:
                            tl = str(t).upper().strip()
                            if tl == SAVE_ADVANTAGE_TIER_SITUATIONAL:
                                sit += 1
                            elif tl == SAVE_ADVANTAGE_TIER_CATEGORY:
                                cat += 1
                            else:
                                b += 1
                        cat = min(cat, n)
                        sit = min(sit, n)
                        b = min(b, n)
                    else:
                        b = n
                else:
                    b = n
            # Aggregate cap: cat + sit ≤ n (reduce sit then cat if needed); broad = remainder ≥ 0
            if cat + sit > n:
                sit = max(0, n - cat)
                if cat + sit > n:
                    cat = max(0, n - sit)
            b = max(0, n - cat - sit)
            additive += SAVE_ADVANTAGE_BASE_VALUE * b
            additive += SAVE_ADVANTAGE_BASE_VALUE * SAVE_ADVANTAGE_CATEGORY_MULTIPLIER * cat
            additive += SAVE_ADVANTAGE_BASE_VALUE * SAVE_ADVANTAGE_SITUATIONAL_MULTIPLIER * sit
        elif has_tiers_list:
            parsed_tiers = _parse_list_field(tiers)
            if parsed_tiers:
                # Truncate tier-list longer than targets → never overprice
                if len(parsed_tiers) > len(save_advantage):
                    parsed_tiers = parsed_tiers[:len(save_advantage)]
            if parsed_tiers and len(parsed_tiers) == len(save_advantage):
                for t in parsed_tiers:
                    tl = str(t).upper().strip()
                    if tl == SAVE_ADVANTAGE_TIER_SITUATIONAL:
                        additive += SAVE_ADVANTAGE_BASE_VALUE * SAVE_ADVANTAGE_SITUATIONAL_MULTIPLIER
                    elif tl == SAVE_ADVANTAGE_TIER_CATEGORY:
                        additive += SAVE_ADVANTAGE_BASE_VALUE * SAVE_ADVANTAGE_CATEGORY_MULTIPLIER
                    else:
                        additive += SAVE_ADVANTAGE_BASE_VALUE
            elif parsed_tiers:
                # Fallback: count tiers in (truncated) list — aggregate cap cat+sit≤n, broad=remainder
                b = sum(1 for t in parsed_tiers if str(t).upper().strip() == SAVE_ADVANTAGE_TIER_BROAD)
                cat = sum(1 for t in parsed_tiers if str(t).upper().strip() == SAVE_ADVANTAGE_TIER_CATEGORY)
                sit = sum(1 for t in parsed_tiers if str(t).upper().strip() == SAVE_ADVANTAGE_TIER_SITUATIONAL)
                n = len(save_advantage)
                cat = min(cat, n)
                sit = min(sit, n)
                if cat + sit > n:
                    sit = max(0, n - cat)
                    if cat + sit > n:
                        cat = max(0, n - sit)
                b = max(0, n - cat - sit)
                additive += SAVE_ADVANTAGE_BASE_VALUE * b + SAVE_ADVANTAGE_BASE_VALUE * SAVE_ADVANTAGE_CATEGORY_MULTIPLIER * cat + SAVE_ADVANTAGE_BASE_VALUE * SAVE_ADVANTAGE_SITUATIONAL_MULTIPLIER * sit
            else:
                additive += SAVE_ADVANTAGE_BASE_VALUE * len(save_advantage)
        else:
            # No tier data → backward compat: all BROAD (400 gp each)
            additive += SAVE_ADVANTAGE_BASE_VALUE * len(save_advantage)
    
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
    # NOTE: Legacy conditional path (flat 200 gp) coincides exactly with the
    # new CATEGORY tier (400 * 0.5 = 200 gp). No double-count: extractor is
    # disjoint by design — "saving throws against X" is excluded from
    # save_advantage (extract_save_targets) and captured only here, while
    # "saving throws to avoid or end X" stays in save_advantage and is
    # tiered as CATEGORY. Verified: no row is priced by both paths.
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

    # Spellcasting focus
    if criteria.get("is_focus"):
        additive += 300

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

    # Temp HP (wave-1): rate × avg × freq multiplier — mirrors healing_daily_hp pattern
    temp_hp_avg = criteria.get("temp_hp_avg") or 0.0
    try:
        temp_hp_avg_f = float(temp_hp_avg)
    except (TypeError, ValueError):
        temp_hp_avg_f = 0.0
    if temp_hp_avg_f and temp_hp_avg_f == temp_hp_avg_f and math.isfinite(temp_hp_avg_f) and temp_hp_avg_f > 0:
        freq = criteria.get("temp_hp_frequency")
        try:
            freq_str = str(freq).strip().lower() if freq is not None else "unclassified"
        except Exception:
            freq_str = "unclassified"
        mult = TEMP_HP_FREQ_MULTIPLIER.get(freq_str, TEMP_HP_FREQ_MULTIPLIER["unclassified"])
        additive += TEMP_HP_RATE * temp_hp_avg_f * mult

    # HP-max increase (wave-1): rate × (flat + per_level × ref_level) — mirrors healing pattern
    hp_max_flat = criteria.get("hp_max_flat") or 0
    hp_max_per_level = criteria.get("hp_max_per_level") or 0
    try:
        flat_f = float(hp_max_flat) if hp_max_flat is not None else 0.0
    except (TypeError, ValueError):
        flat_f = 0.0
    try:
        per_level_f = float(hp_max_per_level) if hp_max_per_level is not None else 0.0
    except (TypeError, ValueError):
        per_level_f = 0.0
    if (flat_f and flat_f == flat_f and math.isfinite(flat_f) and flat_f > 0) or (per_level_f and per_level_f == per_level_f and math.isfinite(per_level_f) and per_level_f > 0):
        if not (flat_f == flat_f and math.isfinite(flat_f)):
            flat_f = 0.0
        if not (per_level_f == per_level_f and math.isfinite(per_level_f)):
            per_level_f = 0.0
        hp_max_total = max(0.0, flat_f) + max(0.0, per_level_f) * HP_MAX_REF_LEVEL
        if hp_max_total > 0:
            additive += HP_MAX_RATE * hp_max_total

    # Initiative (wave-1): per-point bonus + flat for advantage — mirrors save_advantage pattern
    init_bonus = criteria.get("initiative_bonus") or 0
    try:
        init_bonus_f = float(init_bonus) if init_bonus is not None else 0.0
    except (TypeError, ValueError):
        init_bonus_f = 0.0
    if init_bonus_f and init_bonus_f == init_bonus_f and math.isfinite(init_bonus_f) and init_bonus_f != 0:
        # Only positive bonuses add value; negative would be a drawback (not priced here)
        if init_bonus_f > 0:
            additive += INIT_BONUS_RATE * init_bonus_f
    # Initiative advantage flag — bool check mirrors flight_full / invisibility_atwill pattern
    init_adv = criteria.get("initiative_advantage")
    _is_init_adv = False
    if isinstance(init_adv, bool):
        _is_init_adv = init_adv is True
    elif isinstance(init_adv, str):
        _is_init_adv = init_adv.strip().lower() == "true"
    elif isinstance(init_adv, (int, float)):
        # Handle numeric 1/0 from CSV or ML layers; NaN already filtered via truthiness
        try:
            if init_adv != init_adv:  # NaN
                _is_init_adv = False
            else:
                _is_init_adv = bool(init_adv)
        except Exception:
            _is_init_adv = False
    else:
        _is_init_adv = bool(init_adv) if init_adv is not None else False
        # Guard against string "false" being truthy
        if isinstance(init_adv, str):
            _is_init_adv = init_adv.strip().lower() == "true"
    if _is_init_adv:
        additive += INIT_ADVANTAGE_FLAT

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
        # Prefer per-source priced avg when present (Group 1); fallback to multiplier path for backward compat
        priced_extra_damage_avg = criteria.get("extra_damage_priced_avg")
        use_priced = False
        if priced_extra_damage_avg is not None:
            try:
                if pd.isna(priced_extra_damage_avg):
                    use_priced = False
                else:
                    priced_val = float(priced_extra_damage_avg)
                    if math.isfinite(priced_val):
                        priced_extra_damage_avg = priced_val
                        use_priced = True
                    else:
                        priced_extra_damage_avg = 0.0
                        use_priced = True
            except (TypeError, ValueError):
                priced_extra_damage_avg = 0.0
                use_priced = True
        if not use_priced:
            extra_damage_multiplier = extra_damage_pricing_multiplier(criteria)
            try:
                fallback = float(extra_damage_avg) * float(extra_damage_multiplier)
                if math.isfinite(fallback):
                    priced_extra_damage_avg = fallback
                else:
                    priced_extra_damage_avg = 0.0
            except Exception:
                priced_extra_damage_avg = 0.0
        # Scale: 3000 gp per point of average damage for legendary/artifact,
        # 1500 gp per point for lower rarities
        if rarity in ("legendary", "artifact"):
            additive += 3000 * priced_extra_damage_avg
        else:
            additive += 1500 * priced_extra_damage_avg

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
        _pc_raw = criteria.get("price_confidence")
        try:
            if pd.isna(_pc_raw):
                _pc_raw = None
        except Exception:
            pass
        price_confidence = str(_pc_raw or "none")
        has_amalgamated = pd.notna(amalgamated_price) and amalgamated_price > 0 and price_confidence in ("multi", "solo")
        if not has_amalgamated:
            price = min(price, 773)

    # Clamp any artifact not handled by tier system to 250k-1M range
    if rarity == "artifact":
        price = max(250000, min(1000000, price))

    return price


def calculate_price_with_outlier_check(
    criteria: dict,
    criteria_coverage: Optional[int] = None,
    guide_spread: Optional[float] = None,
) -> tuple[float, str]:
    """
    Calculate price with single-source outlier detection.

    Tiered-authority params propagate to calculate_price so that rich+divergent
    anchors lose to the formula. Defaults None preserve backward compat.

    Returns:
        (price, price_source): The calculated price and its source type
    """
    # Get amalgamated price info
    amalgamated_price = criteria.get("amalgamated_price")
    _pc_raw = criteria.get("price_confidence")
    try:
        if pd.isna(_pc_raw):
            _pc_raw = None
    except Exception:
        pass
    price_confidence = str(_pc_raw or "none")

    # Check for single-source outlier flag from amalgamator
    if price_confidence == "solo-outlier":
        # Use rule-based price instead of amalgamated price
        rule_price = calculate_price(
            criteria,
            criteria_coverage=criteria_coverage,
            guide_spread=guide_spread,
        )
        return (rule_price, "rule-outlier-detected")

    # Normal pricing (tiered authority forwarded)
    price = calculate_price(
        criteria,
        criteria_coverage=criteria_coverage,
        guide_spread=guide_spread,
    )

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
