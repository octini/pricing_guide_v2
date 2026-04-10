#!/usr/bin/env python3
"""Phase 5b: Apply variant-adjusted pricing to items with generic parent links."""

import sys
import re
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generic_variant_mapper import extract_generic_variant_mapping, compute_generic_group_stats
from src.generic_pricing import compute_generic_base_prices, merge_variant_prices

INPUT_CSV = Path("data/processed/items_priced.csv")
AMALGAMATED_CSV = Path("data/processed/amalgamated_prices.csv")
MASTER_CSV = Path("data/processed/items_master.csv")
OUTPUT_CSV = Path("data/processed/items_variant_adjusted.csv")


def main():
    items_df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(items_df)} items from {INPUT_CSV}")
    
    master_df = pd.read_csv(MASTER_CSV)
    print(f"Loaded {len(master_df)} items from {MASTER_CSV}")
    
    amalgamated_df = pd.read_csv(AMALGAMATED_CSV) if AMALGAMATED_CSV.exists() else None
    if amalgamated_df is not None:
        print(f"Loaded {len(amalgamated_df)} items from {AMALGAMATED_CSV}")
    
    mapping_df = extract_generic_variant_mapping(master_df)
    print(f"Extracted {len(mapping_df)} generic variant mappings")
    
    group_stats_df = compute_generic_group_stats(mapping_df)
    print(f"Computed stats for {len(group_stats_df)} generic variant groups")
    
    base_prices_df = compute_generic_base_prices(mapping_df, items_df, amalgamated_df)
    print(f"Computed base prices for {len(base_prices_df)} generic variants")
    
    items_with_variants = merge_variant_prices(
        items_df, mapping_df, base_prices_df, group_stats_df
    )
    
    variant_count = items_with_variants['variant_price'].notna().sum()
    print(f"Applied variant adjustments to {variant_count} items")
    
    blended_count = 0
    skipped_official = 0
    for idx, row in items_with_variants.iterrows():
        if not pd.notna(row.get('variant_price')):
            continue

        # Skip variant adjustment for items with official prices (already authoritative)
        if pd.notna(row.get('official_price_gp')) and row.get('official_price_gp', 0) > 0:
            skipped_official += 1
            continue

        # Skip variant adjustment for sentient items (they have their own pricing formula)
        # Sentient items like Moonblade have complex abilities that the variant system can't handle
        if row.get('is_sentient', False):
            continue

        # Skip variant adjustment for material armor (mithral/adamantine)
        # These have their own pricing formula that accounts for base armor cost
        material = row.get('material', '')
        if material in ('mithral', 'adamantine'):
            continue

        # Skip variant adjustment for enspelled items
        # These have their own DSA-based pricing formula
        item_name = str(row.get('name', '')).lower()
        if 'enspelled' in item_name:
            continue

        # Skip variant adjustment for Moon-Touched items
        # These use additive pricing (base weapon + 85 gp)
        if 'moon-touched' in item_name:
            continue

        # Skip variant adjustment for simple +N weapons/armor
        # These have their own amalgamated pricing in the pricing engine
        bonus_match = re.search(r'\+(\d+)\s+(sword|longsword|greatsword|dagger|battleaxe|axe|hammer|bow|spear|staff|plate|chain|leather|scale|breastplate|shield)', item_name)
        if bonus_match:
            bonus = int(bonus_match.group(1))
            # Check if this is a simple +N item (no other modifiers)
            # Simple items are just "+N Weapon" without additional properties
            is_simple = True
            # Check for modifiers that make it non-simple
            if any(mod in item_name for mod in ['vicious', 'drow', 'mithral', 'adamantine', 'silvered', 'enspelled']):
                is_simple = False
            if is_simple and bonus in (1, 2, 3):
                continue

        rule_price = row.get('rule_price', 0)
        variant_price = row.get('variant_price', rule_price)

        # For ammunition items, use variant_price directly (not blended with weapon price)
        # Ammunition has its own generic pricing that's much lower than weapon pricing
        # e.g., +1 Arrow should be ~33gp (generic ammunition price), not 378gp (blended with weapon price)
        item_type = str(row.get('item_type_code', '')).split('|')[0] if row.get('item_type_code') else ''
        is_ammunition = (
            item_type == 'A' or
            'arrow' in item_name or
            'bolt' in item_name or
            'ammunition' in item_name
        )

        if is_ammunition and pd.notna(row.get('variant_price')):
            # Use variant price directly for ammunition
            final_variant_price = variant_price
        else:
            # For other items, blend rule price with variant price
            final_variant_price = 0.5 * rule_price + 0.5 * variant_price

        if 'variant_adjusted_price' not in items_with_variants.columns:
            items_with_variants['variant_adjusted_price'] = None

        items_with_variants.loc[idx, 'variant_adjusted_price'] = final_variant_price
        blended_count += 1

    print(f"Blended variant prices for {blended_count} items")
    print(f"Skipped {skipped_official} items with official prices")
    
    if 'variant_adjusted_price' in items_with_variants.columns:
        has_variant = items_with_variants['variant_adjusted_price'].notna()
        items_with_variants.loc[has_variant, 'rule_price'] = items_with_variants.loc[has_variant, 'variant_adjusted_price']
        items_with_variants.loc[has_variant, 'price_source'] = 'rule+variant'
        # Variant-adjusted items have reference from their generic parent
        if 'has_reference_source' in items_with_variants.columns:
            items_with_variants.loc[has_variant, 'has_reference_source'] = True
    
    items_with_variants.to_csv(OUTPUT_CSV, index=False)
    print(f"\nWrote {len(items_with_variants)} rows to {OUTPUT_CSV}")
    
    if 'variant_price' in items_with_variants.columns:
        slaying = items_with_variants[items_with_variants['name'].str.contains('slaying', case=False, na=False)]
        if len(slaying) > 0:
            print("\nSlaying item prices after adjustment:")
            for _, r in slaying.head(10).iterrows():
                print(f"  {r['name']}: {r.get('rule_price', 0):.0f} gp (base={r.get('variant_base_price', 'N/A')}, adj={r.get('variant_adjustment', 'N/A')})")


if __name__ == "__main__":
    main()
