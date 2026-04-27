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
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


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
