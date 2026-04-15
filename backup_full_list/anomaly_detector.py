# src/anomaly_detector.py
"""Anomaly detection for priced item dataset."""

import pandas as pd
import numpy as np


def detect_anomalies(df, price_col='final_price', rarity_col='rarity', consumable_col='is_consumable'):
    results = {'overall_stats': {}, 'by_rarity': {}, 'outliers': pd.DataFrame(), 'extreme_outliers': pd.DataFrame()}

    prices = df[price_col].dropna()

    results['overall_stats'] = {
        'count': len(prices),
        'median': prices.median(),
        'mean': prices.mean(),
        'std': prices.std(),
        'min': prices.min(),
        'max': prices.max(),
        'cv': prices.std()/prices.mean() if prices.mean() > 0 else None,
        'skewness': prices.skew(),
    }

    all_outliers, all_extreme = [], []

    for (rarity, is_consumable), group in df.groupby([rarity_col, consumable_col]):
        gprices = group[price_col].dropna()
        if len(gprices) < 4:
            continue

        q1, q3 = gprices.quantile(0.25), gprices.quantile(0.75)
        iqr = q3 - q1
        median = gprices.median()

        if iqr == 0:
            lower, upper = median * 0.5, median * 1.5
        else:
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr

        outlier_mask = (group[price_col] < lower) | (group[price_col] > upper)
        extreme_mask = (group[price_col] > 3 * median) | (group[price_col] < median / 3)

        n_outliers = outlier_mask.sum()

        # Create composite key for output
        consumable_str = 'consumable' if is_consumable else 'persistent'
        composite_key = f"{rarity} ({consumable_str})"
        
        results['by_rarity'][composite_key] = {
            'count': len(group),
            'median': median,
            'mean': gprices.mean(),
            'q1': q1,
            'q3': q3,
            'iqr': iqr,
            'lower_fence': lower,
            'upper_fence': upper,
            'n_outliers': n_outliers,
            'outlier_rate': n_outliers / len(group),
            'zero_width_iqr': iqr == 0,
        }

        all_outliers.append(group[outlier_mask])
        all_extreme.append(group[extreme_mask])

    if all_outliers:
        results['outliers'] = pd.concat(all_outliers, ignore_index=False)
    if all_extreme:
        results['extreme_outliers'] = pd.concat(all_extreme, ignore_index=False)

    return results


def format_anomaly_report(results, price_col='final_price'):
    lines = ['# Anomaly Detection Report\n']

    stats = results['overall_stats']
    lines.append('## Overall Statistics\n')
    lines.append(f"- Total items: {stats['count']:,}")
    lines.append(f"- Median price: {stats['median']:,.0f} gp")
    lines.append(f"- Mean price: {stats['mean']:,.0f} gp")
    lines.append(f"- Std dev: {stats['std']:,.0f} gp")
    lines.append(f"- CV: {stats['cv']:.2f}" if stats['cv'] else '- CV: N/A')
    lines.append(f"- Skewness: {stats['skewness']:.2f}")
    lines.append(f"- Price range: {stats['min']:,.0f} – {stats['max']:,.0f} gp\n")

    lines.append('## Outliers by Rarity & Type\n')
    lines.append('| Rarity/Type | Count | Median | IQR Width | Outliers | Outlier Rate |')
    lines.append('|--------------|-------|--------|-----------|----------|--------------|')
    for rarity_type, s in sorted(results['by_rarity'].items()):
        flag = '⚠️ zero-width IQR' if s['zero_width_iqr'] else ''
        lines.append(f"| {rarity_type} | {s['count']} | {s['median']:,.0f} gp | {s['iqr']:,.0f} | {s['n_outliers']} | {s['outlier_rate']:.1%} {flag} |")

    lines.append(f"\n## Extreme Outliers (> 3× rarity median)\n")
    extreme = results['extreme_outliers']
    lines.append(f'Total: {len(extreme)} items\n')
    if len(extreme) > 0:
        lines.append('| Name | Source | Rarity | Price | Rarity Median |')
        lines.append('|------|--------|--------|-------|---------------|')
        for _, row in extreme.head(50).iterrows():
            lines.append(f"| {row.get('name','')} | {row.get('source','')} | {row.get('rarity','')} | {row.get(price_col, 0):,.0f} gp | - |")

    return '\n'.join(lines)
