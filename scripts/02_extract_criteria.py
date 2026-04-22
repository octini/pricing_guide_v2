#!/usr/bin/env python3
"""Phase 2: Extract criteria for all 9422 items → items_criteria.csv"""

import json
import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.criteria_extractor import extract_structured_criteria, extract_prose_criteria, extract_entries_criteria
from src.prose_loader import load_prose_descriptions

INPUT_CSV = Path("data/processed/items_master.csv")
OUTPUT_CSV = Path("data/processed/items_criteria.csv")
MD_PATH = Path("items-sublist.md")
SUBLIST_DATA_PATH = Path("items-sublist-data.json")


def build_generic_parent_lookup(df: pd.DataFrame) -> dict:
    """Build a lookup of generic parent entries by name.
    
    Generic parents are items that have variants (specific items link to them via genericVariant).
    Their entries contain the mechanical properties that specific variants lack.
    """
    parent_lookup = {}
    for _, row in df.iterrows():
        try:
            item = json.loads(row["raw_json"])
        except (json.JSONDecodeError, KeyError):
            continue
        
        # Check if this item has variants (is a generic parent)
        if "variants" in item:
            name = item.get("name", "")
            if name:
                # Collect all entries from the parent and its variants
                all_entries = list(item.get("entries", []))
                for variant in item["variants"]:
                    if isinstance(variant, dict):
                        all_entries.extend(variant.get("entries", []))
                parent_lookup[name.lower()] = all_entries
    
    return parent_lookup


def get_parent_entries(item: dict, parent_lookup: dict) -> list:
    """Get generic parent entries for a specific variant item."""
    gv_link = item.get("genericVariant")
    if not gv_link:
        return []
    
    if isinstance(gv_link, dict):
        parent_name = gv_link.get("name", "")
    else:
        parent_name = str(gv_link)
    
    if not parent_name:
        return []
    
    return parent_lookup.get(parent_name.lower(), [])


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

    # Build generic parent lookup (first pass)
    print("Building generic parent lookup...")
    parent_lookup = build_generic_parent_lookup(df)
    print(f"Found {len(parent_lookup)} generic parent items from items_master.csv")

    # Supplement with parents from items-sublist-data.json (contains generic parents
    # like Holy Avenger that aren't in items_master.csv because only variants are listed)
    if SUBLIST_DATA_PATH.exists():
        with open(SUBLIST_DATA_PATH, encoding="utf-8") as f:
            sublist_items = json.load(f)
        added = 0
        for item in sublist_items:
            if "variants" in item and "entries" in item:
                name = item.get("name", "").lower()
                if name and name not in parent_lookup:
                    parent_lookup[name] = list(item["entries"])
                    added += 1
        print(f"Added {added} generic parents from items-sublist-data.json")
    print(f"Total generic parent items: {len(parent_lookup)}")

    rows = []
    variants_with_parent_entries = 0
    for _, row in df.iterrows():
        try:
            item = json.loads(row["raw_json"])
        except (json.JSONDecodeError, KeyError):
            item = {}

        struct = extract_structured_criteria(item)

        # Get prose descriptions from items-sublist.md
        item_name_lower = row["name"].lower()
        prose_text = prose_map.get(item_name_lower, "")

        # Get generic parent entries and merge them
        parent_entries = get_parent_entries(item, parent_lookup)
        if parent_entries:
            variants_with_parent_entries += 1
            # Merge parent entries into item for extraction
            if "entries" not in item:
                item["entries"] = []
            # Prepend parent entries so they're processed first
            item["entries"] = parent_entries + item["entries"]

        # Extract entries criteria, passing prose text for items with empty entries
        entries = extract_entries_criteria(item, prose_text)

        prose = extract_prose_criteria(prose_text)

        combined = {
            "name": row["name"],
            "source": row["source"],
            "rarity": row["rarity"],
            "type": row["type"],
            "official_price_gp": row["official_price_gp"],
            "req_attune": row["req_attune"],
            "url": row["url"],
            "alias": row.get("alias", ""),
        }
        combined.update(struct)
        combined.update(entries)
        combined.update(prose)

        rows.append(combined)

    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Wrote {len(out_df)} rows with {len(out_df.columns)} columns to {OUTPUT_CSV}")
    print(f"Variants enriched with parent entries: {variants_with_parent_entries}")

    # Quick stats
    print(f"\nItems with weapon_bonus: {out_df['weapon_bonus'].notna().sum()}")
    print(f"Items with ac_bonus: {out_df['ac_bonus'].notna().sum()}")
    print(f"Items with spell_scroll_level: {out_df['spell_scroll_level'].notna().sum()}")
    print(f"Items with attached_spells (non-empty): {(out_df['attached_spells'].astype(str) != '[]').sum()}")

    # Prose-extracted stats
    print(f"\nItems with flight_full: {out_df['flight_full'].sum()}")
    print(f"Items with flight_limited: {out_df['flight_limited'].sum()}")
    print(f"Items with teleportation: {out_df['teleportation'].sum()}")
    print(f"Items with swim_speed: {out_df['swim_speed'].sum()}")
    print(f"Items with save_advantage (non-empty): {(out_df['save_advantage'].astype(str) != '[]').sum()}")
    print(f"Items with condition_immunity_prose (non-empty): {(out_df['condition_immunity_prose'].astype(str) != '[]').sum()}")
    print(f"Items with curse_effects (non-empty): {(out_df['curse_effects'].astype(str) != '[]').sum()}")

    # Entries-extracted stats
    print(f"\nItems with extra_damage_avg > 0: {(out_df['extra_damage_avg'] > 0).sum()}")
    print(f"Items with minor_beneficial > 0: {(out_df['minor_beneficial'] > 0).sum()}")
    print(f"Items with major_beneficial > 0: {(out_df['major_beneficial'] > 0).sum()}")
    print(f"Items with minor_detrimental > 0: {(out_df['minor_detrimental'] > 0).sum()}")
    print(f"Items with major_detrimental > 0: {(out_df['major_detrimental'] > 0).sum()}")
    print(f"Items with has_fixed_beneficial: {out_df['has_fixed_beneficial'].sum()}")
    print(f"Items with has_fixed_detrimental: {out_df['has_fixed_detrimental'].sum()}")


if __name__ == "__main__":
    main()
