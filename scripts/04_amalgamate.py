#!/usr/bin/env python3
"""Phase 4: Amalgamate external price guides → amalgamated_prices.csv"""

import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.amalgamator import amalgamate_prices, trim_outliers
from src.utils import normalize_item_name

ITEMS_CSV = Path("data/processed/items_criteria.csv")
DSA_CSV = Path("data/raw/dsa_prices.csv")
MSRP_CSV = Path("data/raw/msrp_prices.csv")
DMPG_CSV = Path("data/raw/dmpg_prices.csv")
OUTPUT_CSV = Path("data/processed/amalgamated_prices.csv")


def normalize_ammo_bundles(df: pd.DataFrame, source: str) -> pd.DataFrame:
    """Normalize ammunition prices that were priced as bundles instead of individually."""
    if df.empty or 'item_name' not in df.columns:
        return df
        
    for idx, row in df.iterrows():
        name = str(row['item_name']).lower()
        price = row['price_gp']
        
        # Explicit bundles
        if '(20)' in name:
            df.loc[idx, 'price_gp'] = price / 20.0
            continue
        if '(10)' in name:
            df.loc[idx, 'price_gp'] = price / 10.0
            continue
        if '(50)' in name:
            df.loc[idx, 'price_gp'] = price / 50.0
            continue
            
        # Known implicit bundles in DSA
        if source == "DSA":
            if name == "adamantine ammunition":
                df.loc[idx, 'price_gp'] = price / 20.0
            elif name in ["ammunition, +1", "ammunition, +2", "ammunition, +3", "unbreakable arrow"]:
                # Appears to be bundles of 10 based on comparison to MSRP/DMPG
                df.loc[idx, 'price_gp'] = price / 10.0
                
    return df

def main():
    items = pd.read_csv(ITEMS_CSV)
    items["normalized_name"] = items["name"].apply(normalize_item_name)
    
    dsa = pd.read_csv(DSA_CSV) if DSA_CSV.exists() else pd.DataFrame()
    msrp = pd.read_csv(MSRP_CSV) if MSRP_CSV.exists() else pd.DataFrame()
    dmpg = pd.read_csv(DMPG_CSV) if DMPG_CSV.exists() else pd.DataFrame()

    # Trim outliers BEFORE normalizing ammo bundles (so we don't delete valid ammo as "too cheap")
    dsa = trim_outliers(dsa, "price_gp") if len(dsa) >= 10 else dsa
    msrp = trim_outliers(msrp, "price_gp") if len(msrp) >= 10 else msrp
    dmpg = trim_outliers(dmpg, "price_gp") if len(dmpg) >= 10 else dmpg

    dsa = normalize_ammo_bundles(dsa, "DSA")
    msrp = normalize_ammo_bundles(msrp, "MSRP")
    dmpg = normalize_ammo_bundles(dmpg, "DMPG")
    
    print(f"Matching {len(items)} items against {len(dsa)} DSA, {len(msrp)} MSRP, {len(dmpg)} DMPG prices...")
    
    result = amalgamate_prices(items, dsa, msrp, dmpg)
    result.to_csv(OUTPUT_CSV, index=False)
    
    matched = result["amalgamated_price"].notna().sum()
    multi = (result["price_confidence"] == "multi").sum()
    solo = (result["price_confidence"] == "solo").sum()
    
    print(f"\nResults: {matched} items matched ({multi} multi-source, {solo} solo-source)")
    print(f"Unmatched: {len(result) - matched} items (will use rule formula only)")
    
    # Coverage by rarity
    print("\nMatch rate by rarity:")
    for rarity, group in result.groupby("rarity"):
        matched_count = group["amalgamated_price"].notna().sum()
        print(f"  {rarity}: {matched_count}/{len(group)} ({100*matched_count/len(group):.1f}%)")


if __name__ == "__main__":
    main()
