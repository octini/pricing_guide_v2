#!/usr/bin/env python3
"""Phase 1: Parse items-sublist-data.json into items_master.csv"""

import json
import csv
import sys
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import parse_value_cp, get_5etools_url

INPUT_JSON = Path("trimmed_5etools_list.json")
OUTPUT_CSV = Path("data/processed/items_master.csv")

RARITY_NORMALIZE = {
    "none": "mundane",
    "": "mundane",
    "unknown": "unknown",
    "unknown (magic)": "unknown_magic",
    "varies": "varies",
    "common": "common",
    "uncommon": "uncommon",
    "rare": "rare",
    "very rare": "very_rare",
    "legendary": "legendary",
    "artifact": "artifact",
}


def extract_items(data: list) -> list[dict]:
    rows = []
    for item in data:
        name = item.get("name", "")
        source = item.get("source", "")
        page = item.get("page", "")

        # Rarity normalization
        rarity_raw = item.get("rarity", "none") or "none"
        if isinstance(rarity_raw, str):
            rarity = RARITY_NORMALIZE.get(rarity_raw.lower(), rarity_raw.lower())
        else:
            rarity = "unknown"

        item_type = item.get("type", "")

        # Official price from value field (in cp)
        official_price = parse_value_cp(item.get("value"))

        # Attunement
        req_attune_raw = item.get("reqAttune", False)
        if req_attune_raw is True:
            req_attune = "yes"
        elif isinstance(req_attune_raw, str):
            req_attune = f"yes ({req_attune_raw})"
        else:
            req_attune = "no"

        url = get_5etools_url(name, source)

        rows.append({
            "name": name,
            "source": source,
            "page": page,
            "rarity": rarity,
            "type": item_type,
            "official_price_gp": official_price if official_price else "",
            "req_attune": req_attune,
            "url": url,
            "raw_json": json.dumps(item, ensure_ascii=False),
        })

    return rows


def main():
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    with open(INPUT_JSON, encoding="utf-8") as f:
        raw = json.load(f)

    # Handle both list and dict-wrapped formats
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict):
        # Try common keys: 'item', 'items', first key
        for key in ("item", "items"):
            if key in raw:
                items = raw[key]
                break
        else:
            items = list(raw.values())[0]
    else:
        raise ValueError(f"Unexpected JSON root type: {type(raw)}")

    print(f"Loaded {len(items)} items from {INPUT_JSON}")

    rows = extract_items(items)

    # Override rarity for Drow items based on bonus level
    def override_drow_rarity(row):
        name = str(row.get("name", "")).lower()
        if "drow" in name:
            if "+3" in name:
                return "legendary"
            elif "+2" in name:
                return "very_rare"
            elif "+1" in name:
                return "rare"
        return row.get("rarity", "")

    for row in rows:
        row["rarity"] = override_drow_rarity(row)

    fieldnames = ["name", "source", "page", "rarity", "type", "official_price_gp", "req_attune", "url", "raw_json"]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")

    # Summary stats
    from collections import Counter

    rarity_counts = Counter(r["rarity"] for r in rows)
    print("\nRarity distribution:")
    for rarity, count in sorted(rarity_counts.items(), key=lambda x: -x[1]):
        print(f"  {rarity}: {count}")

    priced = sum(1 for r in rows if r["official_price_gp"])
    print(f"\nItems with official prices: {priced}")


if __name__ == "__main__":
    main()
