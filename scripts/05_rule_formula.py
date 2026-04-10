#!/usr/bin/env python3
"""Phase 5: Apply rule-based formula to all items → items_priced.csv"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.pricing_engine import calculate_price, calculate_price_with_outlier_check

INPUT_CSV = Path("data/processed/amalgamated_prices.csv")
OUTPUT_CSV = Path("data/processed/items_priced.csv")


def main():
    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} items")

    prices = []
    for _, row in df.iterrows():
        # Build criteria dict from CSV row
        c = row.to_dict()

        # Parse list fields that were stored as strings
        for list_col in [
            "damage_resistances",
            "damage_immunities",
            "condition_immunities",
            "attached_spells",
            "weapon_properties",
            "ability_score_mods",
        ]:
            val = c.get(list_col, "[]")
            if isinstance(val, str):
                try:
                    c[list_col] = json.loads(val.replace("'", '"')) if val and val != "nan" else []
                except (json.JSONDecodeError, ValueError):
                    c[list_col] = []

        # Parse boolean fields
        for bool_col in [
            "is_sentient",
            "is_cursed",
            "is_tattoo",
            "is_wondrous",
            "is_ammunition",
            "is_shield",
            "flight_full",
            "flight_limited",
            "truesight",
            "blindsight",
            "tremorsense",
            "teleportation",
            "invisibility_atwill",
            "tome_manual_boost",
            "concentration_free",
            "crit_immunity",
            "wish_effect",
            "stealth_advantage",
            "swim_speed",
            "climb_speed",
            "burrow_speed",
            "stealth_penalty",
        ]:
            c[bool_col] = bool(c.get(bool_col))

        # Handle NaN numeric fields - convert to None
        for num_col in [
            "spell_scroll_level",
            "weapon_bonus",
            "weapon_attack_bonus",
            "weapon_damage_bonus",
            "ac_bonus",
            "saving_throw_bonus",
            "ability_check_bonus",
            "proficiency_bonus_mod",
            "spell_attack_bonus",
            "spell_save_dc_bonus",
            "spell_damage_bonus",
            "charges",
            "darkvision_feet",
            "healing_daily_hp",
            "healing_consumable_avg",
            "healing_permanent_hp",
            "official_price_gp",
            "amalgamated_price",
        ]:
            val = c.get(num_col)
            if pd.isna(val):
                c[num_col] = None

        # Determine price source
        if pd.notna(c.get("official_price_gp")) and c.get("rarity") in ("mundane", "none"):
            price = float(c["official_price_gp"])
            price_source = "official"
        else:
            # Use outlier check function to handle solo-outlier items
            price, price_source = calculate_price_with_outlier_check(c)

        # Flag indicating whether any external reference was used
        has_reference = (
            price_source == "official" or 
            pd.notna(c.get("amalgamated_price"))
        )

        prices.append({**c, "rule_price": price, "price_source": price_source, "has_reference_source": has_reference})

    out = pd.DataFrame(prices)

    # Calculate R² against amalgamated prices
    matched = out[out["amalgamated_price"].notna() & out["rule_price"].notna()].copy()
    if len(matched) > 10:
        ss_res = ((matched["rule_price"] - matched["amalgamated_price"]) ** 2).sum()
        ss_tot = ((matched["amalgamated_price"] - matched["amalgamated_price"].mean()) ** 2).sum()
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        print(f"\nR² against amalgamated prices: {r2:.4f} (on {len(matched)} matched items)")
        print(f"Target: ≥ 0.80")

    out.to_csv(OUTPUT_CSV, index=False)
    print(f"\nWrote {len(out)} rows to {OUTPUT_CSV}")

    # Price distribution by rarity
    print("\nMedian prices by rarity:")
    for rarity, group in out.groupby("rarity"):
        median = group["rule_price"].median()
        print(f"  {rarity}: {median:,.0f} gp (n={len(group)})")


if __name__ == "__main__":
    main()
