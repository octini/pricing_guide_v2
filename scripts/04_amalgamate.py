#!/usr/bin/env python3
"""Phase 4: Amalgamate external price guides → amalgamated_prices.csv"""

import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.amalgamator import amalgamate_prices
from src.utils import normalize_item_name

ITEMS_CSV = Path("data/processed/items_criteria.csv")
DSA_CSV = Path("data/raw/dsa_prices.csv")
MSRP_CSV = Path("data/raw/msrp_prices.csv")
DMPG_CSV = Path("data/raw/dmpg_prices.csv")
OUTPUT_CSV = Path("data/processed/amalgamated_prices.csv")


def main():
    items = pd.read_csv(ITEMS_CSV)
    items["normalized_name"] = items["name"].apply(normalize_item_name)
    
    dsa = pd.read_csv(DSA_CSV) if DSA_CSV.exists() else pd.DataFrame()
    msrp = pd.read_csv(MSRP_CSV) if MSRP_CSV.exists() else pd.DataFrame()
    dmpg = pd.read_csv(DMPG_CSV) if DMPG_CSV.exists() else pd.DataFrame()
    
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
