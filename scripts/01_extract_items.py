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


def override_known_rarity(item: dict, rarity: str) -> str:
    """Reassign obvious unknown/unknown_magic items to proper rarities."""
    name_lower = str(item.get("name", "")).lower()
    source = str(item.get("source", ""))
    raw_text = json.dumps(item, ensure_ascii=False)

    # Drow +N weapons
    if "drow +1" in name_lower:
        return "rare"
    if "drow +2" in name_lower:
        return "very_rare"
    if "drow +3" in name_lower:
        return "legendary"

    # Ammunition/material families
    generic_variant_name = item.get("genericVariant", {}).get("name", "")
    if generic_variant_name == "Silvered Ammunition":
        return "common"
    if generic_variant_name == "Adamantine Ammunition":
        return "uncommon"
    if generic_variant_name == "Byeshk Weapon":
        return "common"

    # unknown_magic items with clear magical properties
    if rarity == "unknown_magic":
        if any(token in raw_text for token in ('"bonusWeapon"', '"bonusAc"', '"attachedSpells"', '"charges"', '"sentient"')):
            return "uncommon"
        if source in {"ToA", "BGDIA", "WDMM", "SKT", "PotA", "CoS"}:
            return "uncommon"

    # unknown items: magical ones → uncommon, adventure herbs/plants → mundane
    if rarity == "unknown":
        if any(token in raw_text for token in ('"bonusWeapon"', '"bonusAc"', '"attachedSpells"', '"charges"', '"sentient"')):
            return "uncommon"
        # ToA herbs, berries, roots are mundane consumables
        if source == "ToA" and any(w in name_lower for w in ("leaves", "berries", "root", "nut")):
            return "mundane"
        # Adventure source simple gear
        if source in {"BGDIA", "WDMM"}:
            return "common"

        # Known mundane items that aren't marked as such in source data
        known_mundane = {
            "adjustable stilts",
            "alchemist's doom",
            "backpack parachute",
            "barking box",
            "catapult munition",
            "hooked shortspear",
            "iron ball",
            "light repeating crossbow",
            "matchless pipe",
            "murgaxor's elixir of life",
            "nimblewright detector",
            "oversized longbow",
            "spiked armor",
            "survival mantle",
            "the incantations of iriolarthas",
        }
        if name_lower in known_mundane:
            return "mundane"
        if name_lower.startswith("flensing claws"):
            return "mundane"

    return rarity


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

        rarity = override_known_rarity(item, rarity)

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

        # Fix source data error: Sling Bullets (20) is listed at 4cp total in 5e.tools,
        # but should be 20cp (20 × 1cp each), consistent with other ammo bundles.
        if name == "Sling Bullets (20)" and official_price and official_price < 0.10:
            official_price = 0.20

        # Extract alias field (used for reskin items that duplicate another item)
        alias_list = item.get("alias", [])
        alias = alias_list[0] if alias_list else ""

        rows.append({
            "name": name,
            "source": source,
            "page": page,
            "rarity": rarity,
            "type": item_type,
            "official_price_gp": official_price if official_price else "",
            "req_attune": req_attune,
            "url": url,
            "alias": alias,
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

    fieldnames = ["name", "source", "page", "rarity", "type", "official_price_gp", "req_attune", "url", "alias", "raw_json"]

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
