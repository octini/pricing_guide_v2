#!/usr/bin/env python3
"""Phase 0: Automated Pre-Checks for Pricing Guide Review

Generates a comprehensive flagged-items CSV with multiple checks:
1. Rarity hierarchy violations
2. Algorithm-only Legendary/Artifact items
3. Variant family CV analysis (per-item breakdown)
4. Price below mundane base
5. Amalgamated vs final deviation > 50%
6. Sub-1gp non-ammunition items
7. Suspiciously round prices
8. Unknown rarity items
9. Floor violations
10. Ceiling proximity (near 1M)

Usage:
    python scripts/review_checks.py

Output:
    output/review_flags.csv — all flagged items with check type and details
    output/review_summary.md — human-readable summary
"""

from typing import Optional
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

INPUT_CSV = Path('data/processed/items_ml_priced.csv')
OUTPUT_FLAGS = Path('output/review_flags.csv')
OUTPUT_SUMMARY = Path('output/review_summary.md')

# Mundane base prices for common armor/weapon types
MUNDANE_BASES = {
    # Armor
    'leather armor': 10, 'studded leather': 45, 'hide': 10,
    'chain shirt': 50, 'scale mail': 50, 'breastplate': 400, 'half plate': 750,
    'ring mail': 30, 'chain mail': 75, 'splint': 200, 'plate': 1500,
    # Weapons (melee)
    'club': 0.1, 'dagger': 2, 'greatclub': 0.2, 'handaxe': 5, 'javelin': 0.5,
    'light hammer': 2, 'mace': 5, 'quarterstaff': 0.2, 'sickle': 1, 'spear': 1,
    'morningstar': 15, 'shortsword': 10, 'rapier': 25, 'scimitar': 25,
    'longsword': 15, 'greatsword': 50, 'greataxe': 30, 'maul': 10,
    'glaive': 20, 'halberd': 20, 'lance': 10, 'longspear': 1, 'trident': 5,
    'war pick': 5, 'battleaxe': 10, 'flail': 10, 'whip': 2,
    'yklwa': 1, 'double-bladed scimitar': 100, 'rushlight': 0.1,
    # Ranged
    'light crossbow': 25, 'heavy crossbow': 50, 'shortbow': 25, 'longbow': 50,
    'dart': 0.05, 'blowgun': 10, 'hand crossbow': 75, 'net': 1, 'sling': 0.1,
    # Shields
    'shield': 10,
}

# Drow weapon pattern (intentional sunlight discount — exclude from hierarchy checks)
DROW_PATTERN = 'drow +'


def extract_base_name(name: str) -> str:
    """Strip +N prefix/suffix and common modifiers to get base item name."""
    name_lower = name.lower().strip()
    # Remove +N prefix (e.g., "+1 Longsword" → "longsword")
    import re
    name_lower = re.sub(r'^\+\d+\s+', '', name_lower)
    name_lower = re.sub(r'\s+\+\d+$', '', name_lower)
    # Remove "of X" suffixes (e.g., "Longsword of Wounding" → "longsword")
    name_lower = re.sub(r'\s+of\s+\S+', '', name_lower)
    # Remove common prefixes for variant detection
    for prefix in ['silvered ', 'adamantine ', 'mithral ', 'drow ']:
        name_lower = name_lower.replace(prefix, '')
    return name_lower.strip()


def extract_enhancement_family(name: str) -> Optional[str]:
    """Extract the enhancement family for hierarchy checks.
    Only returns a family for +N items (weapons, armor, shields, ammunition).
    Returns None for named variants, material variants, etc.
    """
    import re
    name_lower = name.lower().strip()
    # Match +N prefix
    m = re.match(r'^\+(\d+)\s+(.+)$', name_lower)
    if m:
        bonus = int(m.group(1))
        base = m.group(2)
        # Only include pure +N items (no material prefixes, no 'of X')
        if ' of ' not in base and not any(base.startswith(p) for p in ['adamantine ', 'mithral ', 'drow ', 'silvered ']):
            return f"+{bonus} {base}"
    return None


def check_rarity_hierarchy(df: pd.DataFrame) -> pd.DataFrame:
    """Check 1: Higher rarity costs less than lower rarity in same +N family."""
    flags = []
    rarity_order = {'mundane': 0, 'common': 1, 'uncommon': 2, 'rare': 3,
                    'very_rare': 4, 'legendary': 5, 'artifact': 6}

    # Group by enhancement family (only +N items)
    df_copy = df.copy()
    df_copy['enhancement_family'] = df_copy['name'].apply(extract_enhancement_family)

    # Filter to only +N items
    enhanced = df_copy[df_copy['enhancement_family'].notna()].copy()

    for family, group in enhanced.groupby('enhancement_family'):
        if len(group) < 2:
            continue
        priced = group[group['final_price'].notna() & group['rarity'].isin(rarity_order)].copy()
        if len(priced) < 2:
            continue
        priced['rarity_rank'] = priced['rarity'].map(rarity_order)

        # Check all pairs
        for _, item_a in priced.iterrows():
            for _, item_b in priced.iterrows():
                if item_a['rarity_rank'] > item_b['rarity_rank']:
                    if item_a['final_price'] < item_b['final_price'] * 0.9:
                        if DROW_PATTERN in str(item_a['name']).lower():
                            continue
                        flags.append({
                            'check': 'rarity_hierarchy',
                            'name': item_a['name'],
                            'rarity': item_a['rarity'],
                            'final_price': item_a['final_price'],
                            'base_name': family,
                            'details': (f"Higher rarity ({item_a['rarity']}, "
                                       f"{item_a['final_price']:.0f}gp) < "
                                       f"lower rarity ({item_b['rarity']}, "
                                       f"{item_b['final_price']:.0f}gp)"),
                            'severity': 'high',
                        })

    return pd.DataFrame(flags)


def check_algorithm_only_high_rarity(df: pd.DataFrame) -> pd.DataFrame:
    """Check 2: Algorithm-only pricing for Legendary/Artifact items."""
    mask = (
        (df['price_source'] == 'algorithm') &
        (df['rarity'].isin(['legendary', 'artifact']))
    )
    items = df[mask].copy()
    if len(items) == 0:
        return pd.DataFrame(columns=['check', 'name', 'rarity', 'final_price', 'base_name', 'details', 'severity'])
    items['check'] = 'algorithm_only_high_rarity'
    items['base_name'] = items['name'].apply(extract_base_name)
    items['details'] = items.apply(
        lambda r: f"Rarity: {r['rarity']}, Price: {r['final_price']:.0f}gp, "
                  f"Confidence: {r.get('price_confidence', 'N/A')}", axis=1)
    items['severity'] = items['rarity'].apply(lambda r: 'high' if r == 'artifact' else 'medium')
    return items[['check', 'name', 'rarity', 'final_price', 'base_name', 'details', 'severity']]


def check_variant_family_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Check 3: Items in variant families with extreme CV that are themselves outliers."""
    flags = []

    # Reuse consistency group logic
    def consistency_group(row):
        wb = row.get('weapon_bonus')
        if pd.notna(wb) and wb > 0:
            return f"weapon+{int(wb)}"
        ab = row.get('ac_bonus')
        if pd.notna(ab) and ab > 0:
            return f"armor+{int(ab)}"
        name = str(row.get('name', '')).lower()
        if 'gleaming' in name:
            return 'gleaming-armor'
        if 'slaying' in name:
            return 'slaying-ammunition'
        return None

    df_copy = df.copy()
    df_copy['consistency_group'] = df_copy.apply(consistency_group, axis=1)
    grouped = df_copy[df_copy['consistency_group'].notna()].copy()

    for group_name, group in grouped.groupby('consistency_group'):
        if len(group) < 3:
            continue

        # Exclude artifacts from weapon+1/2/3 groups (they have their own pricing)
        if group_name.startswith('weapon+') or group_name.startswith('armor+'):
            group = group[group['rarity'] != 'artifact'].copy()
            if len(group) < 3:
                continue

        median_price = group['final_price'].median()
        std_price = group['final_price'].std(ddof=0)
        cv = std_price / median_price if median_price > 0 else 0

        if cv > 0.5:  # Flag families with high CV
            # Find individual outliers in this family (>2 std from median)
            threshold = 2 * std_price
            for _, item in group.iterrows():
                deviation = abs(item['final_price'] - median_price)
                if deviation > threshold:
                    flags.append({
                        'check': 'variant_family_outlier',
                        'name': item['name'],
                        'rarity': item['rarity'],
                        'final_price': item['final_price'],
                        'base_name': group_name,
                        'details': (f"Family CV={cv:.2f}, "
                                   f"deviation={deviation:.0f}gp "
                                   f"(threshold={threshold:.0f}gp), "
                                   f"family median={median_price:.0f}gp"),
                        'severity': 'high' if cv > 5 else 'medium',
                    })

    return pd.DataFrame(flags)


def check_below_mundane(df: pd.DataFrame) -> pd.DataFrame:
    """Check 4: Magic item priced below mundane counterpart."""
    flags = []
    df_copy = df.copy()
    df_copy['base_name'] = df_copy['name'].apply(extract_base_name)

    for _, item in df_copy.iterrows():
        if item['rarity'] == 'mundane' or pd.isna(item['final_price']):
            continue
        if item.get('is_ammunition', False):
            continue
        base = item['base_name']
        if base in MUNDANE_BASES:
            mundane_price = MUNDANE_BASES[base]
            if item['final_price'] < mundane_price:
                flags.append({
                    'check': 'below_mundane',
                    'name': item['name'],
                    'rarity': item['rarity'],
                    'final_price': item['final_price'],
                    'base_name': base,
                    'details': (f"Magic item ({item['final_price']:.0f}gp) < "
                               f"mundane {base} ({mundane_price}gp)"),
                    'severity': 'high',
                })

    return pd.DataFrame(flags)


def check_amalgamated_deviation(df: pd.DataFrame) -> pd.DataFrame:
    """Check 5: Final price deviates >50% from amalgamated price."""
    mask = (
        df['amalgamated_price'].notna() &
        (df['amalgamated_price'] > 0) &
        (df['final_price'].notna())
    )
    subset = df[mask].copy()
    subset['deviation'] = (
        abs(subset['final_price'] - subset['amalgamated_price']) /
        subset['amalgamated_price']
    )
    flagged = subset[subset['deviation'] > 0.5].copy()
    if len(flagged) == 0:
        return pd.DataFrame(columns=['check', 'name', 'rarity', 'final_price', 'base_name', 'details', 'severity'])
    flagged['check'] = 'amalgamated_deviation'
    flagged['base_name'] = flagged['name'].apply(extract_base_name)
    flagged['details'] = flagged.apply(
        lambda r: f"Final: {r['final_price']:.0f}gp, "
                  f"Amalgamated: {r['amalgamated_price']:.0f}gp, "
                  f"Deviation: {r['deviation']:.0%}", axis=1)
    flagged['severity'] = flagged['deviation'].apply(lambda d: 'high' if d > 1.0 else 'medium')
    return flagged[['check', 'name', 'rarity', 'final_price', 'base_name', 'details', 'severity']]


def check_sub_one_gp(df: pd.DataFrame) -> pd.DataFrame:
    """Check 6: Items priced <1gp that aren't ammunition or mundane."""
    mask = (
        (df['final_price'] < 1) &
        (~df.get('is_ammunition', False)) &
        (df['rarity'] != 'mundane') &
        (df['final_price'] > 0)
    )
    items = df[mask].copy()
    if len(items) == 0:
        return pd.DataFrame(columns=['check', 'name', 'rarity', 'final_price', 'base_name', 'details', 'severity'])
    items['check'] = 'sub_one_gp'
    items['base_name'] = items['name'].apply(extract_base_name)
    items['details'] = items.apply(
        lambda r: f"Price: {r['final_price']:.2f}gp, Rarity: {r['rarity']}", axis=1)
    items['severity'] = 'medium'
    return items[['check', 'name', 'rarity', 'final_price', 'base_name', 'details', 'severity']]


def check_round_prices(df: pd.DataFrame) -> pd.DataFrame:
    """Check 7: Suspiciously round prices (possible placeholders)."""
    mask = (
        df['final_price'].notna() &
        (df['final_price'] >= 1000) &
        (df['final_price'] % 1000 == 0) &
        (df['price_source'] != 'amalgamated')
    )
    items = df[mask].copy()
    if len(items) == 0:
        return pd.DataFrame(columns=['check', 'name', 'rarity', 'final_price', 'base_name', 'details', 'severity'])
    items['check'] = 'round_price'
    items['base_name'] = items['name'].apply(extract_base_name)
    items['details'] = items.apply(
        lambda r: f"Round price: {r['final_price']:.0f}gp, Source: {r['price_source']}", axis=1)
    items['severity'] = 'low'
    return items[['check', 'name', 'rarity', 'final_price', 'base_name', 'details', 'severity']]


def check_unknown_rarity(df: pd.DataFrame) -> pd.DataFrame:
    """Check 8: Items with unknown/unclear rarity."""
    mask = df['rarity'].isin(['unknown', 'unknown_magic'])
    items = df[mask].copy()
    if len(items) == 0:
        return pd.DataFrame(columns=['check', 'name', 'rarity', 'final_price', 'base_name', 'details', 'severity'])
    items['check'] = 'unknown_rarity'
    items['base_name'] = items['name'].apply(extract_base_name)
    items['details'] = items.apply(
        lambda r: f"Rarity: '{r['rarity']}', Price: {r['final_price']:.0f}gp", axis=1)
    items['severity'] = 'medium'
    return items[['check', 'name', 'rarity', 'final_price', 'base_name', 'details', 'severity']]


def check_ceiling_proximity(df: pd.DataFrame) -> pd.DataFrame:
    """Check 9: Items near the 1M ceiling (within 5%)."""
    CEILING = 1_000_000
    mask = df['final_price'] > CEILING * 0.95
    items = df[mask].copy()
    if len(items) == 0:
        return pd.DataFrame(columns=['check', 'name', 'rarity', 'final_price', 'base_name', 'details', 'severity'])
    items['check'] = 'ceiling_proximity'
    items['base_name'] = items['name'].apply(extract_base_name)
    items['details'] = items.apply(
        lambda r: f"Price: {r['final_price']:.0f}gp ({r['final_price']/CEILING:.1%} of ceiling)", axis=1)
    items['severity'] = 'medium'
    return items[['check', 'name', 'rarity', 'final_price', 'base_name', 'details', 'severity']]


def generate_summary(all_flags: pd.DataFrame, df: pd.DataFrame) -> str:
    """Generate human-readable summary markdown."""
    lines = ['# Review Checks Summary\n']

    # Overall stats
    lines.append(f"**Dataset:** {len(df)} items")
    lines.append(f"**Total flags:** {len(all_flags)}")
    lines.append(f"**Unique items flagged:** {all_flags['name'].nunique()}\n")

    # By check type
    lines.append('## Flags by Check Type\n')
    lines.append('| Check | Count | Severity Breakdown |')
    lines.append('|-------|-------|---------------------|')
    for check, group in all_flags.groupby('check'):
        high = (group['severity'] == 'high').sum()
        med = (group['severity'] == 'medium').sum()
        low = (group['severity'] == 'low').sum()
        lines.append(f"| {check} | {len(group)} | {high}H / {med}M / {low}L |")

    # Top flagged items (appearing in multiple checks)
    lines.append('\n## Items Flagged Multiple Times\n')
    item_counts = all_flags['name'].value_counts()
    multi_flagged = item_counts[item_counts > 1]
    if len(multi_flagged) > 0:
        lines.append('| Item | Flags | Checks |')
        lines.append('|------|-------|--------|')
        for name, count in multi_flagged.head(20).items():
            checks = ', '.join(all_flags[all_flags['name'] == name]['check'].unique())
            lines.append(f"| {name} | {count} | {checks} |")
    else:
        lines.append('No items flagged by multiple checks.\n')

    # High severity items
    lines.append('\n## High Severity Flags\n')
    high_flags = all_flags[all_flags['severity'] == 'high']
    if len(high_flags) > 0:
        lines.append('| Item | Rarity | Price | Check | Details |')
        lines.append('|------|--------|-------|-------|---------|')
        for _, row in high_flags.head(50).iterrows():
            lines.append(f"| {row['name']} | {row['rarity']} | {row['final_price']:.0f}gp | {row['check']} | {row['details']} |")
    else:
        lines.append('No high severity flags.\n')

    # Variant family summary
    lines.append('\n## Variant Family CV Summary\n')
    variant_flags = all_flags[all_flags['check'] == 'variant_family_outlier']
    if len(variant_flags) > 0:
        for family, group in variant_flags.groupby('base_name'):
            lines.append(f"### {family} ({len(group)} outliers)\n")
            for _, row in group.sort_values('final_price', ascending=False).head(10).iterrows():
                lines.append(f"- **{row['name']}** ({row['rarity']}): {row['final_price']:.0f}gp — {row['details']}")
            if len(group) > 10:
                lines.append(f"- ... and {len(group) - 10} more")
            lines.append('')

    return '\n'.join(lines)


def main():
    print(f"Loading {INPUT_CSV}...")
    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} items with {len(df.columns)} columns\n")

    checks = [
        ('Rarity hierarchy violations', check_rarity_hierarchy),
        ('Algorithm-only Legendary/Artifact', check_algorithm_only_high_rarity),
        ('Variant family outliers', check_variant_family_outliers),
        ('Below mundane base', check_below_mundane),
        ('Amalgamated deviation >50%', check_amalgamated_deviation),
        ('Sub-1gp non-ammunition', check_sub_one_gp),
        ('Round prices', check_round_prices),
        ('Unknown rarity', check_unknown_rarity),
        ('Ceiling proximity', check_ceiling_proximity),
    ]

    all_flags = []
    for name, check_fn in checks:
        print(f"Running: {name}...")
        try:
            result = check_fn(df)
            if len(result) > 0:
                all_flags.append(result)
                print(f"  → {len(result)} flags")
            else:
                print(f"  → 0 flags ✓")
        except Exception as e:
            print(f"  → ERROR: {e}")

    if all_flags:
        combined = pd.concat(all_flags, ignore_index=True)
    else:
        combined = pd.DataFrame(columns=['check', 'name', 'rarity', 'final_price', 'base_name', 'details', 'severity'])

    # Write outputs
    OUTPUT_FLAGS.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_FLAGS, index=False)
    print(f"\nFlags written to {OUTPUT_FLAGS}")

    summary = generate_summary(combined, df)
    OUTPUT_SUMMARY.write_text(summary, encoding='utf-8')
    print(f"Summary written to {OUTPUT_SUMMARY}")

    # Print quick summary
    print(f"\n{'='*60}")
    print(f"REVIEW CHECKS SUMMARY")
    print(f"{'='*60}")
    print(f"Total flags: {len(combined)}")
    print(f"Unique items: {combined['name'].nunique()}")
    print(f"\nBy check:")
    for check, count in combined['check'].value_counts().items():
        print(f"  {check}: {count}")
    print(f"\nBy severity:")
    for sev in ['high', 'medium', 'low']:
        count = (combined['severity'] == sev).sum()
        print(f"  {sev.upper()}: {count}")


if __name__ == '__main__':
    main()
