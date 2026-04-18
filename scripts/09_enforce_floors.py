#!/usr/bin/env python3
"""Phase 9: Enforce minimum floor prices for magic item variants

Ensures no magic item variant is priced below its mundane base counterpart.
This prevents situations where a magic armor (e.g., Demon Plate) costs less
than the mundane armor it's based on.
"""

import re
import pandas as pd
from pathlib import Path

INPUT_CSV = Path('data/processed/items_validated.csv')
OUTPUT_CSV = Path('data/processed/items_validated.csv')

# Base item types that can have magic variants
# Format: {pattern: base_mundane_name}
# Patterns are matched against the magic item's name.
# The base_mundane_name must match a mundane item's name exactly.

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

# Combined pattern map
ALL_BASES = {**ARMOR_BASES, **WEAPON_BASES, **SHIELD_BASE}

# Items that should NOT be matched as variants of mundane items
# These are different item categories that happen to contain similar words
EXCLUDE_PATTERNS = [
    # Crystal trade goods vs spellcasting focus / Delerium
    r'Crystal$',  # "Crystal" as standalone mundane is a spellcasting focus (10gp)
    r'Crystal\b.*Delerium',  # Delerium crystals
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
    # Shard (Delerium) vs mundane "Shard"
    r'Sentira Shard',
    r'Dark Shard',
    # Backpack Parachute is a different item category
    r'Backpack Parachute',
]


def find_mundane_prices(df):
    """Build a lookup of mundane item names to their prices."""
    mundane = df[df['rarity'] == 'mundane'].copy()
    # Some mundane items appear multiple times (e.g., Crystal from different sources)
    # Take the highest price to be conservative
    return mundane.groupby('name')['official_price_gp'].max().to_dict()


# Rarity-based premium multipliers
# Magic items should always cost MORE than their mundane counterparts.
# Higher rarity = higher minimum premium.
RARITY_PREMIUM = {
    'common': 0.10,       # 10% minimum premium for common magic items
    'uncommon': 0.15,     # 15% minimum premium
    'rare': 0.20,         # 20% minimum premium
    'very_rare': 0.25,    # 25% minimum premium
    'legendary': 0.30,    # 30% minimum premium
    'artifact': 0.50,     # 50% minimum premium
    'unknown': 0.10,      # 10% minimum for unknown rarity
    'unknown_magic': 0.10,
    'varies': 0.10,
}


def find_base_item(magic_name, mundane_prices):
    """Find the mundane base item for a magic item variant.
    
    Returns (base_name, base_price) or (None, None) if no match.
    """
    # Check exclusion patterns first
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, magic_name, re.IGNORECASE):
            return None, None
    
    # Try to match against known base patterns
    for pattern, base_name in ALL_BASES.items():
        if re.search(pattern, magic_name, re.IGNORECASE):
            if base_name in mundane_prices:
                return base_name, mundane_prices[base_name]
    
    return None, None


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
        
        base_name, base_price = find_base_item(name, mundane_prices)
        
        if base_name is not None and base_price is not None:
            # Calculate minimum price with rarity-based premium
            rarity_key = row['rarity'].lower().replace(' ', '_')
            premium = RARITY_PREMIUM.get(rarity_key, 0.10)
            min_price = base_price * (1 + premium)
            
            if current_price < min_price - 0.01:  # Small tolerance for floating point
                old_price = current_price
                df.loc[idx, 'final_price'] = round(min_price, 2)
                adjustments.append({
                    'name': name,
                    'base': base_name,
                    'old_price': old_price,
                    'new_price': round(min_price, 2),
                    'rarity': row['rarity'],
                    'premium': premium,
                })
    
    # Re-calculate Price Low/High based on new final_price
    # Price Low = final_price * 0.8, Price High = final_price * 1.2
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
        # Group by base item
        by_base = {}
        for adj in adjustments:
            base = adj['base']
            if base not in by_base:
                by_base[base] = []
            by_base[base].append(adj)
        
        for base, items in sorted(by_base.items()):
            base_price = items[0]['new_price']
            premium = items[0].get('premium', 0)
            print(f'\n  {base} (floor: {base_price:.2f} gp, +{premium:.0%} premium):')
            for item in sorted(items, key=lambda x: x['old_price']):
                print(f"    {item['name']:45s} | {item['rarity']:15s} | {item['old_price']:>10.2f} -> {item['new_price']:>10.2f} gp")
    
    # Verify no remaining violations
    violations = 0
    for idx, row in df[magic_mask].iterrows():
        name = row['name']
        price = row.get('final_price', 0)
        if pd.isna(price) or price <= 0:
            continue
        base_name, base_price = find_base_item(name, mundane_prices)
        if base_name is not None and base_price is not None:
            rarity_key = row['rarity'].lower().replace(' ', '_')
            premium = RARITY_PREMIUM.get(rarity_key, 0.10)
            min_price = base_price * (1 + premium)
            if price < min_price - 0.01:  # Small tolerance for floating point
                violations += 1
                print(f"  REMAINING VIOLATION: {name} ({price:.2f} gp) < {base_name} floor ({min_price:.2f} gp)")
    
    if violations == 0:
        print(f'\nNo remaining violations found.')
    else:
        print(f'\n{violations} remaining violations found!')


if __name__ == '__main__':
    main()
