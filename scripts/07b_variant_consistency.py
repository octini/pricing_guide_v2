#!/usr/bin/env python3
"""Variant consistency audit: flags item families with suspicious internal price spread."""

from pathlib import Path

import pandas as pd

INPUT_CSV = Path('data/processed/items_ml_priced.csv')
OUTPUT_CSV = Path('output/variant_consistency_report.csv')


def consistency_group(row: pd.Series):
    """Assign an item to a consistency group based on its properties.

    Named legendary items (Holy Avenger, Moonblade, Luck Blade, etc.) share
    weapon_bonus/ac_bonus numeric bonuses with generic +N variants but have
    much higher prices due to unique properties. They're excluded from +N
    groups by checking generic_parent — only items whose generic_parent
    matches the literal "+N Weapon" or "+N Armor" pattern are included.
    """
    wb = row.get('weapon_bonus')
    gp = str(row.get('generic_parent', ''))
    
    if pd.notna(wb) and wb > 0:
        if gp == f"+{int(wb)} Weapon" or gp == f"+{int(wb)} Ammunition":
            return f"weapon+{int(wb)}"
        return None
    
    ab = row.get('ac_bonus')
    if pd.notna(ab) and ab > 0:
        if gp == f"+{int(ab)} Armor" or gp == f"+{int(ab)} Shield":
            return f"armor+{int(ab)}"
        return None

    name = str(row.get('name', '')).lower()
    if 'gleaming' in name:
        return 'gleaming-armor'
    if 'slaying' in name:
        return 'slaying-ammunition'
    return None


def main():
    df = pd.read_csv(INPUT_CSV)
    df['consistency_group'] = df.apply(consistency_group, axis=1)
    grouped = df[df['consistency_group'].notna()].copy()

    rows = []
    for group_name, group in grouped.groupby('consistency_group'):
        if len(group) < 3:
            continue
        median_price = group['final_price'].median()
        std_price = group['final_price'].std(ddof=0)
        coeff_var = 0.0 if median_price == 0 else std_price / median_price
        rows.append({
            'consistency_group': group_name,
            'count': len(group),
            'median_price': median_price,
            'std_price': std_price,
            'coefficient_of_variation': round(coeff_var, 4),
            'flagged': coeff_var > 0.60,
        })

    report_df = pd.DataFrame(rows).sort_values(
        ['flagged', 'coefficient_of_variation'], ascending=[False, False]
    )
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    report_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Variant consistency: {len(report_df)} families, "
          f"{report_df['flagged'].sum()} flagged (CV > 0.60)")
    print(f"Report written to {OUTPUT_CSV}")


if __name__ == '__main__':
    main()
