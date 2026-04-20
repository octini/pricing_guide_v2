#!/usr/bin/env python3
"""Phase 7: Validation and anomaly detection"""

import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.anomaly_detector import detect_anomalies, format_anomaly_report

INPUT_CSV = Path('data/processed/items_ml_priced.csv')
OUTPUT_REPORT = Path('output/anomaly_report.md')
OUTPUT_VALIDATED_CSV = Path('data/processed/items_validated.csv')


def main():
    df = pd.read_csv(INPUT_CSV)
    print(f'Loaded {len(df)} items')

    # Derive is_consumable for anomaly bucketing
    # Consumables typically include potions (P), scrolls (SC), ammunition, and poisons.
    # Note that 'type' can be 'P|XPHB', so we use .str.startswith or just regex/contains
    is_potion = df['type'].astype(str).str.startswith('P')
    is_scroll = df['type'].astype(str).str.startswith('SC')
    is_ammo = df.get('is_ammunition', False) == True
    is_poison = df.get('is_poison', False) == True
    df['is_consumable'] = is_potion | is_scroll | is_ammo | is_poison

    official = df[df['official_price_gp'].notna() & (df['rarity'] == 'mundane')].copy()
    print(f'\nOfficial-priced mundane items: {len(official)}')

    results = detect_anomalies(df, price_col='final_price')
    report = format_anomaly_report(results)

    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.write_text(report, encoding='utf-8')
    print(f'\nAnomaly report written to {OUTPUT_REPORT}')

    print('\n=== RARITY OUTLIER RATES ===')
    for rarity, s in sorted(results['by_rarity'].items()):
        status = '🔴' if s['outlier_rate'] > 0.15 else '🟡' if s['outlier_rate'] > 0.10 else '🟢'
        print(f"{status} {rarity}: {s['outlier_rate']:.1%} ({s['n_outliers']}/{s['count']})")

    df['is_outlier'] = False
    for idx in results['outliers'].index:
        if idx in df.index:
            df.loc[idx, 'is_outlier'] = True

    df['is_extreme_outlier'] = False
    for idx in results['extreme_outliers'].index:
        if idx in df.index:
            df.loc[idx, 'is_extreme_outlier'] = True

    df.to_csv(OUTPUT_VALIDATED_CSV, index=False)
    print(f'\nValidated data written to {OUTPUT_VALIDATED_CSV}')


if __name__ == '__main__':
    main()
