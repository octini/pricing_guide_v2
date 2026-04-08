#!/usr/bin/env python3
"""Phase 5b: Apply variant-adjusted pricing to items with generic parent links."""

import sys
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
        if pd.notna(row.get('variant_price')):
            # Skip variant adjustment for items with official prices (already authoritative)
            if pd.notna(row.get('official_price_gp')) and row.get('official_price_gp', 0) > 0:
                skipped_official += 1
                continue

            # Skip variant adjustment for material armor (mithral/adamantine)
            # These have their own pricing formula that accounts for base armor cost
            material = row.get('material', '')
            if material in ('mithral', 'adamantine'):
                continue

            rule_price = row.get('rule_price', 0)
            variant_price = row.get('variant_price', rule_price)

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
