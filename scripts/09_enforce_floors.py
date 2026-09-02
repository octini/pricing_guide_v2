#!/usr/bin/env python3
"""Phase 9: Enforce minimum floor prices for magic item variants

Ensures no magic item variant is priced below its mundane base counterpart,
and that magic variants carry appropriate premiums based on their rarity tier.

Approach:
1. For items with a mundane base counterpart (armor, weapons, shields):
   - Apply rarity-based minimum multiplier to mundane base price
   - Only adjust if current price is below this floor
2. For purely flavor items (Gleaming, Smoldering): small premium over mundane
3. Does NOT override prices that are already above the floor
"""

import sys
import re
import ast
import math
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.pricing_engine import RARITY_FLOORS as ABSOLUTE_RARITY_FLOORS  # tripwire floors: absolute per-rarity minima
    from src.list_curation import is_commodity_exact_price_candidate as _is_commodity_candidate  # noqa: F401 (reference for policy)
except Exception:
    ABSOLUTE_RARITY_FLOORS = {
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

try:
    from src.pricing_engine import WEAPON_BONUS_VALUES, SPELL_SCROLL_PRICES  # family-min + battery parity
    from src.spell_data import get_spell_level
    # Mirror src.pricing_engine._family_min_for_criteria / _battery_min_for_criteria for final gate — see pricing_engine.py
    _FAMILY_IMPORTED = True
except Exception:
    WEAPON_BONUS_VALUES = {1: 725, 2: 3400, 3: 14950}
    SPELL_SCROLL_PRICES = {0: 25, 1: 75, 2: 150, 3: 300, 4: 1500, 5: 3000, 6: 8500, 7: 20000, 8: 45000, 9: 100000}
    _FAMILY_IMPORTED = False

    def get_spell_level(name):  # type: ignore
        return None


INPUT_CSV = Path('data/processed/items_validated.csv')
OUTPUT_CSV = Path('data/processed/items_validated.csv')

# Base item types that can have magic variants
ARMOR_BASES = {
    r'^(?:.*\s)?Breastplate$': 'Breastplate',
    r'^(?:.*\s)?Chain Mail$': 'Chain Mail',
    r'^(?:.*\s)?Chain Shirt$': 'Chain Shirt',
    r'^(?:.*\s)?Half Plate Armor$': 'Half Plate Armor',
    r'^(?:.*\s)?Hide Armor$': 'Hide Armor',
    r'^(?:.*\s)?Leather Armor$': 'Leather Armor',
    r'^(?:.*\s)?Padded Armor$': 'Padded Armor',
    r'^(?:.*\s)?Plate Armor$': 'Plate Armor',
    r'^(?:.*\s)?Ring Mail$': 'Ring Mail',
    r'^(?:.*\s)?Scale Mail$': 'Scale Mail',
    r'^(?:.*\s)?Spiked Armor$': 'Spiked Armor',
    r'^(?:.*\s)?Splint Armor$': 'Splint Armor',
    r'^(?:.*\s)?Studded Leather Armor$': 'Studded Leather Armor',
    # "of Gleaming" variants use shorter names
    r'^(?:.*\s)?Breastplate\b': 'Breastplate',
    r'^(?:.*\s)?Chain Mail\b': 'Chain Mail',
    r'^(?:.*\s)?Chain Shirt\b': 'Chain Shirt',
    r'^(?:.*\s)?Half Plate\b': 'Half Plate Armor',
    r'^(?:.*\s)?Hide\b': 'Hide Armor',
    r'^(?:.*\s)?Leather\b': 'Leather Armor',
    r'^(?:.*\s)?Padded\b': 'Padded Armor',
    r'^(?:.*\s)?Plate\b': 'Plate Armor',
    r'^(?:.*\s)?Ring Mail\b': 'Ring Mail',
    r'^(?:.*\s)?Scale Mail\b': 'Scale Mail',
    r'^(?:.*\s)?Splint\b': 'Splint Armor',
    r'^(?:.*\s)?Studded Leather\b': 'Studded Leather Armor',
}

WEAPON_BASES = {
    r'^(?:.*\s)?Battleaxe$': 'Battleaxe',
    r'^(?:.*\s)?Club$': 'Club',
    r'^(?:.*\s)?Dagger$': 'Dagger',
    r'^(?:.*\s)?Flail$': 'Flail',
    r'^(?:.*\s)?Glaive$': 'Glaive',
    r'^(?:.*\s)?Greataxe$': 'Greataxe',
    r'^(?:.*\s)?Greatclub$': 'Greatclub',
    r'^(?:.*\s)?Greatsword$': 'Greatsword',
    r'^(?:.*\s)?Halberd$': 'Halberd',
    r'^(?:.*\s)?Handaxe$': 'Handaxe',
    r'^(?:.*\s)?Javelin$': 'Javelin',
    r'^(?:.*\s)?Lance$': 'Lance',
    r'^(?:.*\s)?Light Hammer$': 'Light Hammer',
    r'^(?:.*\s)?Longsword$': 'Longsword',
    r'^(?:.*\s)?Mace$': 'Mace',
    r'^(?:.*\s)?Maul$': 'Maul',
    r'^(?:.*\s)?Morningstar$': 'Morningstar',
    r'^(?:.*\s)?Pike$': 'Pike',
    r'^(?:.*\s)?Quarterstaff$': 'Quarterstaff',
    r'^(?:.*\s)?Rapier$': 'Rapier',
    r'^(?:.*\s)?Scimitar$': 'Scimitar',
    r'^(?:.*\s)?Shortsword$': 'Shortsword',
    r'^(?:.*\s)?Sickle$': 'Sickle',
    r'^(?:.*\s)?Spear$': 'Spear',
    r'^(?:.*\s)?Trident$': 'Trident',
    r'^(?:.*\s)?War Pick$': 'War Pick',
    r'^(?:.*\s)?Warhammer$': 'Warhammer',
    r'^(?:.*\s)?Whip$': 'Whip',
    r'^(?:.*\s)?Hand Crossbow$': 'Hand Crossbow',
    r'^(?:.*\s)?Heavy Crossbow$': 'Heavy Crossbow',
    r'^(?:.*\s)?Light Crossbow$': 'Light Crossbow',
    r'^(?:.*\s)?Longbow$': 'Longbow',
    r'^(?:.*\s)?Shortbow$': 'Shortbow',
    r'^(?:.*\s)?Blowgun$': 'Blowgun',
    r'^(?:.*\s)?Dart$': 'Dart',
    r'^(?:.*\s)?Sling$': 'Sling',
    r'^(?:.*\s)?Musket$': 'Musket',
    r'^(?:.*\s)?Pistol$': 'Pistol',
}

SHIELD_BASE = {
    r'^(?:.*\s)?Shield$': 'Shield',
}

ALL_BASES = {**ARMOR_BASES, **WEAPON_BASES, **SHIELD_BASE}

# Items that should NOT be matched as variants of mundane items
EXCLUDE_PATTERNS = [
    r'Crystal$',
    r'Crystal\b.*Delerium',
    r'Fernian.*Crystal',
    r'Irian.*Crystal',
    r'Kythrian.*Crystal',
    r'Lamannian.*Crystal',
    r'Mabaran.*Crystal',
    r'Risian.*Crystal',
    r'Shavarran.*Crystal',
    r'Xorian.*Crystal',
    r'Mind Crystal',
    r'Psi Crystal',
    r'Sentira Shard',
    r'Dark Shard',
    r'Backpack Parachute',
]

# Purely flavor items: no real mechanical benefit beyond appearance
FLAVOR_KEYWORDS = [
    'gleaming', 'smoldering', 'cast-off',
]

# Rarity-based minimum multipliers for magic items with mundane counterparts
# These ensure magic items are never priced at mundane levels
# The multiplier is applied to the mundane base price
RARITY_MINIMUMS = {
    'common': 1.5,       # 1.5x mundane base (e.g., Plate 1500 → 2250 min)
    'uncommon': 2.0,     # 2.0x mundane base (e.g., Plate 1500 → 3000 min)
    'rare': 3.0,         # 3.0x mundane base (e.g., Plate 1500 → 4500 min)
    'very_rare': 5.0,    # 5.0x mundane base (e.g., Plate 1500 → 7500 min)
    'legendary': 10.0,   # 10.0x mundane base (e.g., Plate 1500 → 15000 min)
    'artifact': 20.0,    # 20.0x mundane base
    'unknown': 1.5,
    'unknown_magic': 1.5,
    'varies': 1.5,
}


def find_mundane_prices(df):
    """Build a lookup of mundane item names to their prices."""
    mundane = df[df['rarity'] == 'mundane'].copy()
    return mundane.groupby('name')['official_price_gp'].max().to_dict()


def find_base_item(magic_name, mundane_prices):
    """Find the mundane base item for a magic item variant."""
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, magic_name, re.IGNORECASE):
            return None, None
    
    for pattern, base_name in ALL_BASES.items():
        if re.search(pattern, magic_name, re.IGNORECASE):
            if base_name in mundane_prices:
                return base_name, mundane_prices[base_name]
    
    return None, None


def is_flavor_item(name):
    """Check if an item is purely cosmetic/flavor."""
    name_lower = name.lower()
    return any(kw in name_lower for kw in FLAVOR_KEYWORDS)


def _base_type_code(value) -> str:
    """Return base type code before '|' — mirrors pricing_engine / list_curation handling."""
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    return str(value).split("|")[0].strip()


def _is_official_price_row(row) -> bool:
    """True when row's price came from the official/commodity-exact path.  Those rows bypass floors."""
    # Primary signal in the pipeline output is price_source == 'official'.
    # Observed values: 'official', 'rule', 'rule+variant', 'rule-outlier-detected'.
    ps = row.get("price_source", "")
    try:
        if pd.isna(ps):
            ps = ""
    except Exception:
        pass
    if isinstance(ps, str) and ps.strip().lower() == "official":
        return True
    # Fallback: legacy check via is_commodity_exact_candidate shape would require raw JSON; the
    # price_source signal is authoritative for the validated CSV.  No additional fallback needed.
    return False


def _is_consumable_modifier_row(row) -> bool:
    """True for items whose price was intentionally discounted via get_consumable_modifier.

    Mirrors src/pricing_engine.get_consumable_modifier detection but limited to the four
    spec-exempt types: ammunition, potion, scroll, poison ( Grenades/wondrous remain clamped ).
    Detection uses the same flags the engine uses, as they appear in 09's CSV: is_ammunition,
    is_poison, item_type_code pipe-prefix, and name tokens for potion/elixir.
    """
    # ammunition: is_ammunition flag
    ammo = row.get("is_ammunition", False)
    try:
        if pd.notna(ammo) and bool(ammo):
            return True
    except Exception:
        if ammo is True or str(ammo).lower() == "true":
            return True
    # poison: is_poison flag
    poison = row.get("is_poison", False)
    try:
        if pd.notna(poison) and bool(poison):
            return True
    except Exception:
        if poison is True or str(poison).lower() == "true":
            return True
    # type-based: P (potion), SC (scroll)
    base = _base_type_code(row.get("item_type_code", ""))
    if base == "P":
        return True
    if base == "SC":
        return True
    # name-based potion/elixir (engine checks name regardless of type)
    name_val = row.get("name", "")
    try:
        if pd.isna(name_val):
            name_val = ""
    except Exception:
        pass
    name_lower = str(name_val).lower()
    if "potion" in name_lower or "elixir" in name_lower:
        return True
    # G + oil/ointment is intentionally NOT exempt per spec (only the four types above); do not return True here.
    return False


def _is_amalgamated_row(row) -> bool:
    """Hop C5: True when row has valid amalgamated reference (multi/solo).

    Mirrors src.pricing_engine._is_amalgamated_reference: amalgamated_price >0
    AND price_confidence in ("multi", "solo"). Also handles candidate CSV where
    Price Source starts with "Amalgamated" (e.g. "Amalgamated (DSA,MSRP,DMPG)").
    Solo-outlier/Algorithm (none, pd.NA) returns False → family-min *may* clamp.
    """
    try:
        # Candidate CSV signal: Price Source starting with "Amalgamated"
        ps = row.get("price_source", "")
        try:
            if pd.notna(ps) and isinstance(ps, str) and ps.strip().lower().startswith("amalgamated"):
                return True
        except Exception:
            pass
        # Validated signal: amalgamated_price + price_confidence
        amalg = row.get("amalgamated_price")
        if amalg is None:
            return False
        try:
            if pd.isna(amalg):
                return False
        except Exception:
            pass
        try:
            f = float(amalg)  # type: ignore[arg-type]
            if not math.isfinite(f) or f <= 0:
                return False
        except Exception:
            return False
        pc = row.get("price_confidence")
        try:
            if pd.isna(pc):  # type: ignore[arg-type]
                return False
        except Exception:
            pass
        if pc is None:
            return False
        return str(pc) in ("multi", "solo")
    except Exception:
        return False


def _family_min_for_row(row) -> float | None:
    """Family-flat minimum for magic weapons (+1/+2/+3) — mirror src.pricing_engine._family_min_for_criteria."""
    try:
        wb = row.get("weapon_bonus")
        if wb is None or pd.isna(wb):  # type: ignore[arg-type]
            return None
        try:
            wb_int = int(float(wb))  # type: ignore[arg-type]
        except Exception:
            return None
        if wb_int not in WEAPON_BONUS_VALUES:
            return None
        # ammunition never gets family-min
        try:
            if pd.notna(row.get("is_ammunition")) and bool(row.get("is_ammunition")):  # type: ignore[arg-type]
                return None
        except Exception:
            if row.get("is_ammunition") is True:
                return None
        item_type_code = str(row.get("item_type_code", "") or "").split("|")[0].strip()
        if item_type_code not in ("M", "R"):
            return None
        rarity = str(row.get("rarity", "unknown") or "unknown").lower().replace(" ", "_")
        # benchmark is already tier-priced; multiplier only discounts sub-norm rarity
        rarity_mults = {"common": 0.25, "mundane": 0.25, "uncommon": 0.5, "rare": 1.0, "very_rare": 1.0, "legendary": 1.0, "artifact": 1.0}
        mult = rarity_mults.get(rarity, 1.0)
        family_raw = float(WEAPON_BONUS_VALUES[wb_int]) * mult
        req_attune = str(row.get("req_attune", "none") or "none").strip().lower()
        if req_attune == "open":
            attune_mod = 0.90
        elif req_attune == "class":
            attune_mod = 0.80
        else:
            attune_mod = 1.0
        return family_raw * attune_mod
    except Exception:
        return None


def _battery_min_for_row(row) -> float | None:
    """Scroll-parity battery floor — mirror src.pricing_engine._battery_min_for_criteria."""
    try:
        battery_level = None
        sb = row.get("spell_battery_max_level")
        if sb is not None:
            try:
                if not pd.isna(sb):  # type: ignore[arg-type]
                    lvl = int(float(sb))  # type: ignore[arg-type]
                    if 0 <= lvl <= 9:
                        battery_level = lvl
            except Exception:
                pass
        if battery_level is None:
            charges_raw = row.get("charges")
            charges_val = None
            if charges_raw is not None:
                try:
                    if pd.isna(charges_raw):  # type: ignore[arg-type]
                        charges_val = None
                    elif isinstance(charges_raw, str):
                        m = re.search(r"(\d+)", charges_raw)
                        if m:
                            charges_val = int(m.group(1))
                    else:
                        charges_val = int(float(charges_raw))  # type: ignore[arg-type]
                except Exception:
                    charges_val = None
            if charges_val and charges_val > 0:
                attached = row.get("attached_spells")
                if attached is not None:
                    try:
                        if pd.isna(attached):  # type: ignore[arg-type]
                            attached = None
                    except Exception:
                        pass
                    if attached is not None:
                        parsed = None
                        try:
                            if isinstance(attached, str):
                                s = attached.strip()
                                if s and s not in ("", "[]", "nan"):
                                    parsed = ast.literal_eval(s)
                                else:
                                    parsed = []
                            else:
                                parsed = attached
                        except Exception:
                            parsed = None
                        has = False
                        levels: list[int] = []
                        if isinstance(parsed, dict):
                            for k, upd in parsed.items():
                                if k in ("ability", "choose", "options"):
                                    continue
                                if isinstance(upd, list):
                                    if len(upd) > 0:
                                        has = True
                                    for sp in upd:
                                        lvl = get_spell_level(sp)
                                        if lvl is not None and lvl >= 0:
                                            levels.append(lvl)
                                elif isinstance(upd, dict):
                                    for freq, spells in upd.items():
                                        if isinstance(spells, list) and len(spells) > 0:
                                            has = True
                                        if isinstance(spells, list):
                                            for sp in spells:
                                                lvl = get_spell_level(sp)
                                                if lvl is not None and lvl >= 0:
                                                    levels.append(lvl)
                        elif isinstance(parsed, list):
                            if len(parsed) > 0:
                                has = True
                            for sp in parsed:
                                lvl = get_spell_level(sp)
                                if lvl is not None and lvl >= 0:
                                    levels.append(lvl)
                        if has and levels:
                            battery_level = max(levels)
        if battery_level is not None:
            price = SPELL_SCROLL_PRICES.get(battery_level)
            return float(price) if price is not None else None
    except Exception:
        return None
    return None


def apply_final_guarantees(df):
    """Path-independent final gate post-blend: final_price = max(final_price, (a) absolute floor, (b) family-min, (c) battery parity).

    (a) uses existing official/consumable exemptions; (b) family-min uses official + amalgamated exemptions (Hop C5: reference authority — solo-outlier/Algorithm still clamp); (c) battery uses official exemption only (no consumable exemption — gems are wondrous).
    Extends apply_absolute_rarity_floor semantics for the final gate — see pricing_engine helpers.
    """
    adjustments: list[dict] = []
    for idx, row in df.iterrows():
        rarity_raw = row.get("rarity", "")
        try:
            if pd.isna(rarity_raw):  # type: ignore[arg-type]
                continue
        except Exception:
            pass
        if not isinstance(rarity_raw, str):
            rarity_raw = str(rarity_raw)
        rarity_key = rarity_raw.lower().replace(" ", "_")
        final = row.get("final_price", 0)
        try:
            if pd.isna(final):  # type: ignore[arg-type]
                continue
        except Exception:
            pass
        try:
            current = float(final)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        if not current or current <= 0:
            continue
        # compute target as max of all floors
        target = current
        # (a) absolute floor with both exemptions
        floor = ABSOLUTE_RARITY_FLOORS.get(rarity_key)
        if floor is not None and not _is_official_price_row(row) and not _is_consumable_modifier_row(row):
            if float(floor) > target:
                target = float(floor)
        # (b) family-min (official + amalgamated exemptions; ammunition already excluded in helper)
        # Hop C5: gate to non-amalgamated items only (reference authority)
        fam = _family_min_for_row(row)
        if fam is not None and not _is_official_price_row(row) and not _is_amalgamated_row(row):
            if fam > target:
                target = fam
        # (c) battery parity (official exemption only, no consumable exemption)
        batt = _battery_min_for_row(row)
        if batt is not None and not _is_official_price_row(row):
            if batt > target:
                target = batt
        if target > current + 0.01:
            old_price = current
            df.loc[idx, "final_price"] = round(target, 2)
            adjustments.append({
                "name": row.get("name", ""),
                "rarity": rarity_raw,
                "old_price": old_price,
                "new_price": float(target),
                "floor": float(target),
                "kind": "final_gate",
            })
    return adjustments


def apply_absolute_rarity_floor(df):
    """Apply tripwire absolute floor to df in-place; return list of adjustments."""
    adjustments = []
    for idx, row in df.iterrows():
        rarity_raw = row.get("rarity", "")
        try:
            if pd.isna(rarity_raw):
                continue
        except Exception:
            pass
        if not isinstance(rarity_raw, str):
            rarity_raw = str(rarity_raw)
        rarity_key = rarity_raw.lower().replace(" ", "_")
        floor = ABSOLUTE_RARITY_FLOORS.get(rarity_key)
        if floor is None:
            continue
        final = row.get("final_price", 0)
        try:
            if pd.isna(final):
                continue
        except Exception:
            pass
        try:
            current = float(final)
        except (TypeError, ValueError):
            continue
        if not current or current <= 0:
            continue
        if _is_official_price_row(row):
            continue
        if _is_consumable_modifier_row(row):
            continue
        if current < float(floor) - 0.01:
            old_price = current
            df.loc[idx, "final_price"] = round(float(floor), 2)
            adjustments.append({
                "name": row.get("name", ""),
                "rarity": rarity_raw,
                "old_price": old_price,
                "new_price": float(floor),
                "floor": float(floor),
            })
    return adjustments


def main():
    df = pd.read_csv(INPUT_CSV)
    print(f'Loaded {len(df)} items')
    
    mundane_prices = find_mundane_prices(df)
    print(f'Found {len(mundane_prices)} unique mundane item prices')
    
    # Only process magic items (non-mundane)
    magic_mask = df['rarity'] != 'mundane'
    magic_items = df[magic_mask].copy()
    
    adjustments = []
    
    for idx, row in magic_items.iterrows():
        name = row['name']
        current_price = row.get('final_price', 0)
        
        if pd.isna(current_price) or current_price <= 0:
            continue
        
        has_amalgamated = pd.notna(row.get('amalgamated_price')) and row.get('price_confidence') in ('multi', 'solo')
        
        base_name, base_price = find_base_item(name, mundane_prices)
        
        if base_name is not None and base_price is not None:
            rarity_key = row['rarity'].lower().replace(' ', '_')
            rarity_mult = RARITY_MINIMUMS.get(rarity_key, 1.5)
            
            if is_flavor_item(name):
                # Purely flavor items: small premium over mundane
                min_price = base_price * 1.10  # 10% premium for flavor
            elif has_amalgamated:
                # Items with amalgamated prices: only enforce mundane floor (1.1x)
                # Don't apply full rarity multiplier — trust the reference sources
                min_price = base_price * 1.10
            else:
                # Items with mechanical benefits: rarity-based minimum
                min_price = base_price * rarity_mult
            
            if current_price < min_price - 0.01:
                old_price = current_price
                df.loc[idx, 'final_price'] = round(min_price, 2)
                adjustments.append({
                    'name': name,
                    'base': base_name,
                    'old_price': old_price,
                    'new_price': round(min_price, 2),
                    'rarity': row['rarity'],
                    'is_flavor': is_flavor_item(name),
                })
    
    # --- Absolute rarity floor (tripwire) ---
    # RARITY_FLOORS is a tripwire, not a destination: clamp any item priced below its
    # rarity's absolute floor to that floor, except (1) official/commodity-exact prices
    # (they never reach this clamp; preserve exactly) and (2) consumable-modifier items
    # (ammunition/potion/scroll/poison) whose deliberately discounted per-unit pricing
    # intentionally sits below the generic floor.  Grenades and wondrous items DO clamp.
    # This runs AFTER the mundane-relative weapons/armor clamp and does not alter it.
    absolute_adjustments = apply_absolute_rarity_floor(df)
    if absolute_adjustments:
        print(f"\n=== ABSOLUTE RARITY FLOOR (TRIPWIRE) ===")
        print(f"Total absolute adjustments: {len(absolute_adjustments)}")
        for adj in sorted(absolute_adjustments, key=lambda x: (x["rarity"], x["old_price"]))[:40]:
            print(f"  {adj['name']:45s} | {adj['rarity']:15s} | {adj['old_price']:>10.2f} -> {adj['new_price']:>10.2f} gp (floor {adj['floor']:.0f})")
        if len(absolute_adjustments) > 40:
            print(f"  ... and {len(absolute_adjustments)-40} more")
    else:
        print(f"\n=== ABSOLUTE RARITY FLOOR (TRIPWIRE) ===")
        print(f"Total absolute adjustments: 0")
    
    # --- Fix: Use official_price_gp as floor for items with unknown/non-magic rarity ---
    # Items like Spiked Armor have official_price_gp=75 but rule_price=1 because
    # the pricing engine doesn't handle "unknown" rarity well.
    official_fixes = []
    for idx, row in df.iterrows():
        final = row.get('final_price', 0)
        official = row.get('official_price_gp', 0)
        if pd.notna(official) and official > 0 and pd.notna(final) and final < official * 0.5:
            # If final price is less than half the official price, use official price
            old_price = final
            df.loc[idx, 'final_price'] = official
            official_fixes.append(f"  {row['name']}: {old_price:.2f} -> {official:.2f} gp (official price floor)")
    
    if official_fixes:
        print(f'\n=== OFFICIAL PRICE FLOOR FIXES ===')
        for msg in official_fixes:
            print(msg)

    # --- Fix: Apply variant spacing to +N weapons ---
    # Script 05b computes variant_adjustment factors but skips simple +N weapons
    # because they use amalgamated pricing. However, the amalgamated price is flat
    # (e.g., "+1 Weapon" = 615 GP for all weapon types). We need to apply the
    # variant adjustment AFTER amalgamation to differentiate weapon types.
    # IDEMPOTENT: Always compute from amalgamated_price * (1 + adj), not from final_price.
    variant_spacing_adjustments = []
    if 'variant_adjustment' in df.columns:
        for idx, row in df.iterrows():
            adj = row.get('variant_adjustment', 0)
            if pd.isna(adj) or adj == 0:
                continue
            name = str(row.get('name', ''))
            # Only apply to simple +N weapons (not Drow, Vicious, etc.)
            if not re.match(r'^\+\d\s+\w', name):
                continue
            # Check it's a weapon type
            item_type = str(row.get('item_type_code', '')).split('|')[0]
            if item_type not in ('M', 'R'):
                continue
            # Use amalgamated price as the base (idempotent)
            base_price_for_adj = row.get('amalgamated_price', 0)
            if pd.isna(base_price_for_adj) or base_price_for_adj <= 0:
                continue
            current_price = row.get('final_price', 0)
            if pd.isna(current_price) or current_price <= 0:
                continue
            # Compute adjusted price from amalgamated base
            new_price = round(base_price_for_adj * (1 + adj), 2)
            if abs(new_price - current_price) > 0.01:
                df.loc[idx, 'final_price'] = new_price
                variant_spacing_adjustments.append(
                    f"  {name}: {current_price:.2f} -> {new_price:.2f} gp (variant adj={adj:+.4f})"
                )
    
    if variant_spacing_adjustments:
        print(f'\n=== VARIANT SPACING ADJUSTMENTS ===')
        print(f'Total: {len(variant_spacing_adjustments)}')
        for msg in variant_spacing_adjustments[:20]:
            print(msg)
        if len(variant_spacing_adjustments) > 20:
            print(f'  ... and {len(variant_spacing_adjustments) - 20} more')

    # --- Fix: Apply post-amalgamation variant spacing to named weapon families ---
    # Named weapon families like Defender have a flat amalgamated price across all
    # weapon variants. Apply the pre-computed variant_adjustment (dampened by 0.3)
    # to differentiate variants while keeping the amalgamated price as the base.
    NAMED_WEAPON_FAMILIES = {'Defender'}
    named_variant_adjustments = []
    if 'variant_adjustment' in df.columns and 'generic_parent' in df.columns:
        for idx, row in df.iterrows():
            adj = row.get('variant_adjustment', 0)
            if pd.isna(adj) or adj == 0:
                continue
            generic_parent = str(row.get('generic_parent', ''))
            if generic_parent not in NAMED_WEAPON_FAMILIES:
                continue
            base_price_for_adj = row.get('amalgamated_price', 0)
            if pd.isna(base_price_for_adj) or base_price_for_adj <= 0:
                continue
            current_price = row.get('final_price', 0)
            if pd.isna(current_price) or current_price <= 0:
                continue
            # Apply dampened variant adjustment: 0.3 factor compresses the spread
            new_price = round(base_price_for_adj * (1 + adj * 0.3), 2)
            if abs(new_price - current_price) > 0.01:
                df.loc[idx, 'final_price'] = new_price
                named_variant_adjustments.append(
                    f"  {row['name']}: {current_price:.2f} -> {new_price:.2f} gp "
                    f"(variant adj={adj:+.4f}, family={generic_parent})"
                )

    if named_variant_adjustments:
        print(f'\n=== NAMED WEAPON FAMILY VARIANT SPACING ===')
        print(f'Total: {len(named_variant_adjustments)}')
        for msg in named_variant_adjustments:
            print(msg)

    # Enforce armor tier ordering: Plate Armor >= Half Plate Armor >= Breastplate
    # for the same enhancement bonus (+1, +2, +3), to prevent ML adjustments from
    # inverting the natural price relationship that reflects the higher mundane cost.
    import re as _re
    bonus_pattern = _re.compile(r'\+(\d)\s+(.+)')
    armor_tiers = ['Breastplate', 'Half Plate Armor', 'Plate Armor']
    tier_order = {name: i for i, name in enumerate(armor_tiers)}

    # Group by bonus level
    bonus_groups = {}
    for idx, row in df.iterrows():
        name = row['name']
        m = bonus_pattern.match(name)
        if m:
            bonus, base = m.group(1), m.group(2).strip()
            if base in tier_order:
                key = bonus
                if key not in bonus_groups:
                    bonus_groups[key] = {}
                bonus_groups[key][base] = idx

    # For each bonus level, enforce plate >= half plate >= breastplate
    tier_ordering_adjustments = []
    for bonus, bases in bonus_groups.items():
        # Walk up the tier chain and ensure each is >= the previous
        prev_price = None
        prev_name = None
        for tier_name in armor_tiers:
            if tier_name not in bases:
                continue
            idx = bases[tier_name]
            price = df.loc[idx, 'final_price']
            if pd.notna(price) and prev_price is not None and price < prev_price:
                old = price
                df.loc[idx, 'final_price'] = round(prev_price + 1, 2)
                tier_ordering_adjustments.append(
                    f"+{bonus} {tier_name}: {old:.2f} -> {prev_price + 1:.2f} gp "
                    f"(must be >= +{bonus} {prev_name} at {prev_price:.2f} gp)"
                )
                prev_price = prev_price + 1
            else:
                prev_price = float(price) if pd.notna(price) else prev_price
            prev_name = tier_name

    if tier_ordering_adjustments:
        print(f'\n=== ARMOR TIER ORDERING FIXES ===')
        for msg in tier_ordering_adjustments:
            print(f'  {msg}')

    # NOTE: Variant spacing is already applied in script 05b.
    # Do NOT re-apply here — it compounds multipliers on every run (non-idempotent).
    # See commit history for details on this fix.

    # --- Final guarantees gate (path-independent) — post-blend max of (a) absolute floor, (b) family-min, (c) battery parity ---
    final_gate_adjustments = apply_final_guarantees(df)
    if final_gate_adjustments:
        print(f"\n=== FINAL GUARANTEES GATE (PATH-INDEPENDENT) ===")
        print(f"Total final-gate adjustments: {len(final_gate_adjustments)}")
        for adj in sorted(final_gate_adjustments, key=lambda x: (x["rarity"], x["old_price"]))[:60]:
            print(f"  {adj['name']:45s} | {adj['rarity']:15s} | {adj['old_price']:>10.2f} -> {adj['new_price']:>10.2f} gp (final gate)")
        if len(final_gate_adjustments) > 60:
            print(f"  ... and {len(final_gate_adjustments)-60} more")
    else:
        print(f"\n=== FINAL GUARANTEES GATE (PATH-INDEPENDENT) ===")
        print(f"Total final-gate adjustments: 0")

    # Override ML quantile-based price bands with flat ±20% range.
    # Rationale: ML quantile bounds were too wide for common items (>50% range)
    # and too narrow for legendary items (<10% range). Flat ±20% provides
    # consistent uncertainty bands across all rarities for the HTML UI.
    for idx in df.index:
        final = df.loc[idx, 'final_price']
        if pd.notna(final) and final > 0:
            df.loc[idx, 'price_low'] = round(final * 0.8, 2)
            df.loc[idx, 'price_high'] = round(final * 1.2, 2)
    
    df.to_csv(OUTPUT_CSV, index=False)
    print(f'Saved adjusted data to {OUTPUT_CSV}')
    
    print(f'\n=== FLOOR PRICE ADJUSTMENTS ===')
    print(f'Total adjustments: {len(adjustments)}')
    
    if adjustments:
        by_base = {}
        for adj in adjustments:
            base = adj['base']
            if base not in by_base:
                by_base[base] = []
            by_base[base].append(adj)
        
        for base, items in sorted(by_base.items()):
            print(f'\n  {base}:')
            for item in sorted(items, key=lambda x: x['old_price']):
                flavor_tag = ' [flavor]' if item['is_flavor'] else ''
                print(f"    {item['name']:45s} | {item['rarity']:15s} | {item['old_price']:>10.2f} -> {item['new_price']:>10.2f} gp{flavor_tag}")
    
    # Verify no remaining violations
    violations = 0
    for idx, row in df[magic_mask].iterrows():
        name = row['name']
        price = row.get('final_price', 0)
        if pd.isna(price) or price <= 0:
            continue
        base_name, base_price = find_base_item(name, mundane_prices)
        if base_name is not None and base_price is not None:
            has_amalgamated = pd.notna(row.get('amalgamated_price')) and row.get('price_confidence') in ('multi', 'solo')
            rarity_key = row['rarity'].lower().replace(' ', '_')
            rarity_mult = RARITY_MINIMUMS.get(rarity_key, 1.5)
            
            if is_flavor_item(name):
                min_price = base_price * 1.10
            elif has_amalgamated:
                min_price = base_price * 1.10
            else:
                min_price = base_price * rarity_mult
            
            if price < min_price - 0.01:
                violations += 1
                print(f"  REMAINING VIOLATION: {name} ({price:.2f} gp) < floor ({min_price:.2f} gp)")
    
    if violations == 0:
        print(f'\nNo remaining violations found.')
    else:
        print(f'\n{violations} remaining violations found!')


if __name__ == '__main__':
    main()
