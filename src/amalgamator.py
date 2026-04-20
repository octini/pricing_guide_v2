# src/amalgamator.py
"""Fuzzy matching, outlier trimming, and weighted amalgamation."""

import pandas as pd
from rapidfuzz import fuzz, process
from typing import Optional

from src.constants import RARITY_MEDIANS


def trim_outliers(df: pd.DataFrame, price_col: str, pct: float = 0.02) -> pd.DataFrame:
    """Remove items with zero price (likely joke/error items in DSA).

    We don't trim high-priced items anymore - legitimate expensive items like
    Rod of Resurrection were being incorrectly removed. Instead, we only remove
    items with 0 price, which are joke items or cursed items that DSA priced at 0.
    """
    if len(df) < 10:
        return df
    # Only remove items with zero price (not serious prices)
    return df[df[price_col] > 0].reset_index(drop=True)


def detect_and_exclude_outliers(prices: dict, outlier_threshold: float = 5.0) -> dict:
    """
    Detect outlier prices and exclude them from calculation.

    For items with 3 sources, if any price is > outlier_threshold times the median,
    exclude that source and recalculate using only the remaining sources.

    Returns the filtered prices dict.
    """
    sources = list(prices.keys())
    if len(sources) < 3:
        return prices  # Can't detect outliers with less than 3 sources

    vals = list(prices.values())
    median_price = sorted(vals)[1]  # middle value of 3

    # Check for outliers
    filtered = {}
    for source, price in prices.items():
        if price > median_price * outlier_threshold:
            # Skip this source as it's an outlier
            continue
        filtered[source] = price

    return filtered


def detect_single_source_outlier(
    prices: dict,
    rarity: str,
    rarity_medians: dict,
    outlier_threshold: float = 5.0,
    has_accurate_match: bool = True
) -> tuple[bool, str]:
    """
    Detect if a single-source item is an outlier compared to its rarity median.
    
    Args:
        prices: Dict of source -> price (will have only 1 entry for single-source)
        rarity: Item rarity (common, uncommon, rare, very_rare, legendary, artifact)
        rarity_medians: Dict of rarity -> median price for that rarity
        outlier_threshold: Multiplier above which to flag as outlier (default 5x)
        has_accurate_match: Whether the fuzzy match was accurate (True if exact match)
    
    Returns:
        (is_outlier: bool, reason: str)
    
    Note: Only flags items that:
    1. Have a single source
    2. Have an accurate match (not fuzzy)
    3. Exceed rarity median by > outlier_threshold or fall below median / outlier_threshold
    """
    if len(prices) != 1:
        return (False, "multi-source")
    
    if not has_accurate_match:
        return (False, "fuzzy-match")
    
    source = list(prices.keys())[0]
    price = list(prices.values())[0]
    
    # Normalize rarity key
    rarity_key = rarity.lower().replace(" ", "_").replace("-", "_")
    if rarity_key not in rarity_medians:
        return (False, f"unknown-rarity-{rarity}")
    
    median = rarity_medians[rarity_key]
    
    if price > median * outlier_threshold:
        return (True, f"single-source-{source}-exceeds-{outlier_threshold}x-median-high")
    
    if price < median / outlier_threshold:
        return (True, f"single-source-{source}-below-{outlier_threshold}x-median-low")
    
    return (False, "within-range")


def calculate_weights(prices: dict) -> dict:
    """
    Given prices from up to 3 sources {DSA, MSRP, DMPG}, return weights summing to 1.0
    based on alignment.
    """
    sources = [k for k in ("DSA", "MSRP", "DMPG") if k in prices]
    n = len(sources)
    
    if n == 1:
        return {sources[0]: 1.0}
    
    if n == 2:
        return {s: 0.5 for s in sources}
    
    # n == 3: check pairwise alignment (within 25% of each other)
    vals = {s: prices[s] for s in sources}
    median_price = sorted(vals.values())[1]
    
    def within_25(a, b):
        if a == 0 or b == 0:
            return False
        ratio = max(a, b) / min(a, b)
        return ratio <= 1.25
    
    aligned = {s: within_25(vals[s], median_price) for s in sources}
    
    if all(aligned.values()):
        # All three within 25% of median
        return {s: 1/3 for s in sources}
    
    # Find which pairs are aligned
    dsa_msrp = within_25(vals["DSA"], vals["MSRP"])
    dsa_dmpg = within_25(vals["DSA"], vals["DMPG"])
    msrp_dmpg = within_25(vals["MSRP"], vals["DMPG"])
    
    if dsa_msrp and not msrp_dmpg and not dsa_dmpg:
        return {"DSA": 0.40, "MSRP": 0.40, "DMPG": 0.20}
    
    if dsa_dmpg and not dsa_msrp and not msrp_dmpg:
        return {"DSA": 0.40, "MSRP": 0.20, "DMPG": 0.40}
    
    if msrp_dmpg and not dsa_msrp and not dsa_dmpg:
        return {"DSA": 0.20, "MSRP": 0.40, "DMPG": 0.40}
    
    # All diverge
    return {"DSA": 0.40, "MSRP": 0.30, "DMPG": 0.30}


def fuzzy_match_items(
    query: str,
    candidates: list,
    threshold: int = 85,
) -> list:
    """Return candidates that fuzzy-match query above threshold.

    Special handling for bonus numbers: +1, +2, +3 must match exactly.
    """
    import re

    # Extract bonus number from query (e.g., "+3 Shortsword" → "3")
    query_bonus_match = re.search(r'\+(\d+)', query)
    query_bonus = query_bonus_match.group(1) if query_bonus_match else None

    # Lowercase both query and candidates for case-insensitive matching
    query_lower = query.lower()
    candidates_lower = [c.lower() for c in candidates]

    results = process.extract(
        query_lower,
        candidates_lower,
        scorer=fuzz.token_sort_ratio,
        limit=5
    )

    matched = []
    for result in results:
        # Use the original (non-lowercased) candidate name
        candidate = candidates[result[2]]
        score = result[1]

        if score < threshold:
            continue

        # Check bonus number matches
        if query_bonus:
            candidate_bonus_match = re.search(r'\+(\d+)', candidate)
            candidate_bonus = candidate_bonus_match.group(1) if candidate_bonus_match else None
            if query_bonus != candidate_bonus:
                continue  # Skip if bonus numbers don't match

        matched.append(candidate)

    return matched


def amalgamate_prices(
    items_df: pd.DataFrame,
    dsa_df: pd.DataFrame,
    msrp_df: pd.DataFrame,
    dmpg_df: pd.DataFrame,
    threshold: int = 85,
) -> pd.DataFrame:
    """
    Match items to each guide and compute weighted amalgamated price.

    Returns items_df with added columns:
    dsa_price, msrp_price, dmpg_price, amalgamated_price, price_sources, price_confidence
    """
    # Build lookup dicts: normalized_name → price_gp
    # Note: outlier trimming should be done BEFORE calling this function
    dsa_lookup = dict(zip(dsa_df["normalized_name"], dsa_df["price_gp"])) if len(dsa_df) > 0 else {}
    msrp_lookup = dict(zip(msrp_df["normalized_name"], msrp_df["price_gp"])) if len(msrp_df) > 0 else {}
    dmpg_lookup = dict(zip(dmpg_df["normalized_name"], dmpg_df["price_gp"])) if len(dmpg_df) > 0 else {}

    dsa_names = list(dsa_lookup.keys())
    msrp_names = list(msrp_lookup.keys())
    dmpg_names = list(dmpg_lookup.keys())

    results = []
    for _, row in items_df.iterrows():
        norm_name = row.get("normalized_name", row["name"].lower())

        # Match in each guide
        prices = {}
        for lookup, names, source in [
            (dsa_lookup, dsa_names, "DSA"),
            (msrp_lookup, msrp_names, "MSRP"),
            (dmpg_lookup, dmpg_names, "DMPG"),
        ]:
            if not names:
                continue
            matches = fuzzy_match_items(norm_name, names, threshold)
            if matches:
                prices[source] = lookup[matches[0]]

        # Fallback: generic variant matching for sources that didn't match
        # Build a generic query from item properties and try matching against
        # each guide's generic entries (e.g., "+3 Weapon", "+1 Ammunition")
        # Runs even if some sources already matched, to fill in missing ones
        missing_sources = [s for s in ("DSA", "MSRP", "DMPG") if s not in prices]
        if missing_sources:
            import re
            item_name = row.get("name", "")
            item_type = str(row.get("item_type_code", "")).split("|")[0] if pd.notna(row.get("item_type_code")) else ""
            rarity = row.get("rarity", "")

            # Check for +N bonus items
            bonus_match = re.search(r'\+(\d+)', item_name)
            if bonus_match:
                bonus = bonus_match.group(1)
                # Determine item category
                is_ammo = (item_type == "A" or
                          "ammunition" in item_name.lower() or
                          any(a in item_name.lower() for a in ["arrow", "bolt", "bullet", "needle"]))
                is_shield = (item_type == "S" or "shield" in item_name.lower())
                is_armor = (item_type in ("LA", "MA", "HA") or
                           "armor" in item_name.lower() or
                           any(a in item_name.lower() for a in ["plate armor", "half plate", "breastplate", "chain mail", "chain shirt", "scale mail", "splint", "ring mail", "studded leather", "hide armor"]))
                # Exclude shields from armor detection
                if is_shield:
                    is_armor = False
                # Exclude non-armor items (e.g., leatherworker's tools)
                if "leatherworker" in item_name.lower() or "tool" in item_name.lower():
                    is_armor = False

                is_weapon = (item_type in ("M", "R") or
                            any(w in item_name.lower() for w in ["sword", "axe", "hammer", "dagger", "bow", "crossbow", "spear", "mace", "flail", "rapier", "scimitar", "lance", "halberd", "glaive", "pike", "trident", "whip", "net", "club", "greatclub", "handaxe", "light hammer", "sickle", "javelin", "quarterstaff", "light crossbow", "dart", "shortbow", "sling", "blowgun", "hand crossbow", "heavy crossbow", "longbow"]))

                # Build generic query names for each guide's naming convention
                generic_queries = []
                if is_ammo:
                    generic_queries = [f"ammunition +{bonus}", f"ammunition any +{bonus}", f"ammunition +{bonus} ea"]
                elif is_shield:
                    generic_queries = [f"shield +{bonus}"]
                elif is_armor:
                    # DSA uses "Armor, +N", MSRP uses "Armor, +N"
                    generic_queries = [f"armor, +{bonus}", f"armor +{bonus}"]
                elif is_weapon:
                    generic_queries = [f"weapon +{bonus}", f"weapon any +{bonus}"]

                # Try matching generic queries against guides missing prices
                for query in generic_queries:
                    for lookup, names, source in [
                        (dsa_lookup, dsa_names, "DSA"),
                        (msrp_lookup, msrp_names, "MSRP"),
                        (dmpg_lookup, dmpg_names, "DMPG"),
                    ]:
                        if source not in missing_sources:
                            continue  # Already have a price from this guide
                        if not names:
                            continue
                        matches = fuzzy_match_items(query, names, threshold)
                        if matches:
                            prices[source] = lookup[matches[0]]

        if prices:
            # Detect and exclude outlier prices before calculating weighted average
            filtered_prices = detect_and_exclude_outliers(prices)
            
            # Check for single-source outliers
            rarity = row.get("rarity", "unknown")
            is_outlier, outlier_reason = detect_single_source_outlier(
                filtered_prices, rarity, RARITY_MEDIANS, outlier_threshold=5.0
            )
            
            if is_outlier:
                # Flag as outlier but keep the price for now
                # The pricing engine will handle this
                confidence = "solo-outlier"
            else:
                confidence = "multi" if len(filtered_prices) > 1 else "solo"

            weights = calculate_weights(filtered_prices)
            amalgamated = sum(filtered_prices[s] * weights[s] for s in filtered_prices)
            sources_str = ",".join(filtered_prices.keys())
        else:
            amalgamated = None
            sources_str = ""
            confidence = "none"

        results.append({
            **row.to_dict(),
            "dsa_price": prices.get("DSA"),
            "msrp_price": prices.get("MSRP"),
            "dmpg_price": prices.get("DMPG"),
            "amalgamated_price": amalgamated,
            "price_sources": sources_str,
            "price_confidence": confidence,
        })

    return pd.DataFrame(results)
