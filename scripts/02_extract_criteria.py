#!/usr/bin/env python3
"""Phase 2: Extract criteria for all 9422 items → items_criteria.csv"""

import json
import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.criteria_extractor import extract_structured_criteria, extract_prose_criteria
from src.prose_loader import load_prose_descriptions

INPUT_CSV = Path("data/processed/items_master.csv")
OUTPUT_CSV = Path("data/processed/items_criteria.csv")
MD_PATH = Path("items-sublist.md")


def main():
    # Load prose descriptions
    if MD_PATH.exists():
        prose_map = load_prose_descriptions(MD_PATH)
        print(f"Loaded {len(prose_map)} prose descriptions from {MD_PATH}")
    else:
        prose_map = {}
        print("Warning: items-sublist.md not found, skipping prose extraction")

    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} items from {INPUT_CSV}")

    rows = []
    for _, row in df.iterrows():
        try:
            item = json.loads(row["raw_json"])
        except (json.JSONDecodeError, KeyError):
            item = {}

        struct = extract_structured_criteria(item)

        # Get prose descriptions from items-sublist.md
        item_name_lower = row["name"].lower()
        prose_text = prose_map.get(item_name_lower, "")
        prose = extract_prose_criteria(prose_text)

        combined = {
            "name": row["name"],
            "source": row["source"],
            "rarity": row["rarity"],
            "type": row["type"],
            "official_price_gp": row["official_price_gp"],
            "req_attune": row["req_attune"],
            "url": row["url"],
        }
        combined.update(struct)
        combined.update(prose)

        rows.append(combined)

    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Wrote {len(out_df)} rows with {len(out_df.columns)} columns to {OUTPUT_CSV}")

    # Quick stats
    print(f"\nItems with weapon_bonus: {out_df['weapon_bonus'].notna().sum()}")
    print(f"Items with ac_bonus: {out_df['ac_bonus'].notna().sum()}")
    print(f"Items with spell_scroll_level: {out_df['spell_scroll_level'].notna().sum()}")
    print(f"Items with attached_spells (non-empty): {(out_df['attached_spells'].astype(str) != '[]').sum()}")

    # Prose-extracted stats
    print(f"\nItems with flight_full: {out_df['flight_full'].sum()}")
    print(f"Items with flight_limited: {out_df['flight_limited'].sum()}")
    print(f"Items with teleportation: {out_df['teleportation'].sum()}")


if __name__ == "__main__":
    main()
