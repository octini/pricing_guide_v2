# src/generic_pricing.py
"""Compute base prices for generic variants."""

import pandas as pd
from typing import Optional


def compute_generic_base_prices(
    mapping_df: pd.DataFrame,
    priced_df: pd.DataFrame,
    amalgamated_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Compute base prices for each generic variant.
    
    Args:
        mapping_df: Output from extract_generic_variant_mapping
        priced_df: Items with final_price column
        amalgamated_df: Optional items with amalgamated_price column
    
    Returns:
        DataFrame with columns: generic_name, base_price, price_source, variant_count
    """
    from src.generic_variant_mapper import compute_generic_group_stats
    
    group_stats = compute_generic_group_stats(mapping_df)
    
    base_prices = []
    for generic_name in group_stats['generic_name']:
        variants = mapping_df[mapping_df['generic_name'] == generic_name]
        variant_names = variants['specific_name'].tolist()

        # PRIORITY 1: Check if the generic itself has a price in priced_df
        price_col = 'rule_price' if 'rule_price' in priced_df.columns else 'final_price'
        generic_row = priced_df[priced_df['name'] == generic_name]
        if len(generic_row) > 0:
            generic_price = generic_row.iloc[0].get(price_col)
            if generic_price is not None and not pd.isna(generic_price) and generic_price > 0:
                base_prices.append({
                    'generic_name': generic_name,
                    'base_price': generic_price,
                    'price_source': 'generic_rule_price',
                    'variant_count': len(variants),
                })
                continue

        # PRIORITY 2: Check if the generic has an amalgamated_price
        if amalgamated_df is not None:
            generic_amal_row = amalgamated_df[amalgamated_df['name'] == generic_name]
            if len(generic_amal_row) > 0:
                generic_amal = generic_amal_row.iloc[0].get('amalgamated_price')
                if generic_amal is not None and not pd.isna(generic_amal) and generic_amal > 0:
                    base_prices.append({
                        'generic_name': generic_name,
                        'base_price': generic_amal,
                        'price_source': 'generic_amalgamated',
                        'variant_count': len(variants),
                    })
                    continue

        # PRIORITY 3: Average of variant prices
        variant_prices = priced_df[priced_df['name'].isin(variant_names)]
        if len(variant_prices) > 0:
            avg_price = variant_prices[price_col].mean()
            if not pd.isna(avg_price) and avg_price > 0:
                base_prices.append({
                    'generic_name': generic_name,
                    'base_price': avg_price,
                    'price_source': 'variant_average',
                    'variant_count': len(variants),
                })
                continue

        # FALLBACK: Use rarity median
        rarity = variants.iloc[0]['generic_rarity']
        rarity_medians = {
            'common': 132,
            'uncommon': 852,
            'rare': 3890,
            'very_rare': 13450,
            'legendary': 46500,
            'artifact': 150000,
            'mundane': 1,
            'unknown': 1,
        }
        median_price = rarity_medians.get(rarity, 750)
        base_prices.append({
            'generic_name': generic_name,
            'base_price': median_price,
            'price_source': 'rarity_median',
            'variant_count': len(variants),
        })

    return pd.DataFrame(base_prices)


def merge_variant_prices(
    items_df: pd.DataFrame,
    mapping_df: pd.DataFrame,
    base_prices_df: pd.DataFrame,
    group_stats_df: pd.DataFrame,
) -> pd.DataFrame:
    """Merge variant-adjusted prices into items DataFrame.
    
    Args:
        items_df: Full items DataFrame
        mapping_df: Output from extract_generic_variant_mapping
        base_prices_df: Output from compute_generic_base_prices
        group_stats_df: Output from compute_generic_group_stats
    
    Returns:
        items_df with added columns: generic_parent, variant_base_price, variant_adjustment, variant_price
    """
    from src.variant_adjuster import compute_adjustment_factor, categorize_generic_variant, apply_variant_adjustment
    
    items = items_df.copy()
    
    items['generic_parent'] = None
    items['variant_base_price'] = None
    items['variant_adjustment'] = None
    items['variant_price'] = None
    
    for idx, row in items.iterrows():
        item_name = row['name']
        # Skip gleaming items - they have their own premium in the rule pricing
        if "gleaming" in item_name.lower():
            continue

        variant_row = mapping_df[mapping_df['specific_name'] == item_name]
        if len(variant_row) == 0:
            continue

        variant_row = variant_row.iloc[0]
        generic_name = variant_row['generic_name']

        base_price_row = base_prices_df[base_prices_df['generic_name'] == generic_name]
        if len(base_price_row) == 0:
            continue

        base_price = base_price_row.iloc[0]['base_price']
        if base_price is None or pd.isna(base_price):
            continue

        group_stats_row = group_stats_df[group_stats_df['generic_name'] == generic_name]
        if len(group_stats_row) == 0:
            continue

        group_stats = group_stats_row.iloc[0]

        category = categorize_generic_variant(generic_name, row.get('item_type_code', ''))
        adjustment_factor = compute_adjustment_factor(variant_row, group_stats, category)
        variant_price = apply_variant_adjustment(base_price, adjustment_factor)

        items.loc[idx, 'generic_parent'] = generic_name
        items.loc[idx, 'variant_base_price'] = base_price
        items.loc[idx, 'variant_adjustment'] = adjustment_factor
        items.loc[idx, 'variant_price'] = variant_price
    
    return items