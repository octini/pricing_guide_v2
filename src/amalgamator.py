# src/amalgamator.py
"""Fuzzy matching, outlier trimming, and weighted amalgamation."""

import pandas as pd
from rapidfuzz import fuzz, process
from typing import Optional


def trim_outliers(df: pd.DataFrame, price_col: str, pct: float = 0.02) -> pd.DataFrame:
    """Remove the top pct and bottom pct of items by price."""
    if len(df) < 10:
        return df
    n_trim = max(1, int(len(df) * pct))
    sorted_df = df.sort_values(price_col)
    return sorted_df.iloc[n_trim:-n_trim].reset_index(drop=True)


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
    
    results = process.extract(
        query.lower(),
        candidates,
        scorer=fuzz.token_sort_ratio,
        limit=5
    )
    
    matched = []
    for result in results:
        candidate = result[0]
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
    # Trim outliers from each guide
    dsa_trimmed = trim_outliers(dsa_df.copy(), "price_gp") if len(dsa_df) >= 10 else dsa_df
    msrp_trimmed = trim_outliers(msrp_df.copy(), "price_gp") if len(msrp_df) >= 10 else msrp_df
    dmpg_trimmed = trim_outliers(dmpg_df.copy(), "price_gp") if len(dmpg_df) >= 10 else dmpg_df
    
    # Build lookup dicts: normalized_name → price_gp
    dsa_lookup = dict(zip(dsa_trimmed["normalized_name"], dsa_trimmed["price_gp"])) if len(dsa_trimmed) > 0 else {}
    msrp_lookup = dict(zip(msrp_trimmed["normalized_name"], msrp_trimmed["price_gp"])) if len(msrp_trimmed) > 0 else {}
    dmpg_lookup = dict(zip(dmpg_trimmed["normalized_name"], dmpg_trimmed["price_gp"])) if len(dmpg_trimmed) > 0 else {}
    
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
        
        if prices:
            weights = calculate_weights(prices)
            amalgamated = sum(prices[s] * weights[s] for s in prices)
            sources_str = ",".join(prices.keys())
            confidence = "multi" if len(prices) > 1 else "solo"
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
