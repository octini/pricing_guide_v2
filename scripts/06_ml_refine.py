#!/usr/bin/env python3
"""Phase 6: ML coefficient refinement using XGBoost with quantile regression."""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

sys.path.insert(0, str(Path(__file__).parent.parent))

INPUT_CSV = Path("data/processed/items_variant_adjusted.csv")
INPUT_FALLBACK_CSV = Path("data/processed/items_priced.csv")
OUTPUT_CSV = Path("data/processed/items_ml_priced.csv")

# Features for ML: these are the additive criteria values + composite features
FEATURE_COLS = [
    "weapon_bonus",
    "ac_bonus",
    "spell_attack_bonus",
    "spell_save_dc_bonus",
    "saving_throw_bonus",
    "ability_check_bonus",
    "proficiency_bonus_mod",
    "spell_damage_bonus",
    "flight_full",
    "flight_limited",
    "truesight",
    "blindsight",
    "tremorsense",
    "teleportation",
    "invisibility_atwill",
    "concentration_free",
    "crit_immunity",
    "stealth_advantage",
    "swim_speed",
    "climb_speed",
    "burrow_speed",
    "healing_daily_hp",
    "healing_consumable_avg",
    "tome_manual_boost",
    "is_sentient",
    "is_cursed",
    "darkvision_feet",
    "is_ammunition",
    # Composite features
    "power_score",
    "defensive_score",
    "spell_complexity",
    "interaction_weapon_damage",
    "interaction_flight_invisibility",
]

RARITY_DUMMIES = ["common", "uncommon", "rare", "very_rare", "legendary", "artifact"]

# Rarities that should NOT use ML blending (model trained on magic items)
NON_MAGIC_RARITIES = {"mundane", "unknown", "varies", "artifact"}

# Tiered blend weights: (amalgamated_weight, rule_weight)
# For items WITH amalgamated_price: use confidence-based weights
# For items WITHOUT amalgamated_price: use rule-based weights
CONFIDENCE_WEIGHTS = {
    "multi": (0.85, 0.15),      # 3 sources: high trust in amalgamated
    "solo": (0.40, 0.60),       # 1 source: lean toward ML/rule
    "solo-outlier": (0.0, 1.0), # Already handled separately, uses rule
    "none": (0.0, 1.0),         # No sources, uses rule+ML blend
}

# For items without amalgamated_price, use rule+ML blend
DEFAULT_RULE_WEIGHT = 0.35  # 35% rule, 65% ML

# Items that should NOT use ML blending (use rule price directly)
# Material armor uses DSA formula which is already calibrated
def is_material_armor(row):
    """Check if item is material armor (mithral/adamantine armor)."""
    material = row.get("material", "")
    if material in ("mithral", "adamantine"):
        # Check if it's armor (has a base_item_cost from armor matching)
        item_type = str(row.get("item_type_code", "")).split("|")[0]
        if item_type in ("LA", "MA", "HA", "S"):
            return True
    return False

def is_spell_scroll(row):
    """Check if item is a spell scroll (has spell_scroll_level)."""
    spell_level = row.get("spell_scroll_level")
    # NaN check: spell_level == spell_level is False for NaN
    return spell_level is not None and spell_level == spell_level

def is_high_rarity_ammunition(row):
    """Check if item is very_rare+ ammunition (priced per piece, not as full item)."""
    is_ammo = row.get("is_ammunition", False)
    rarity = row.get("rarity", "")
    return is_ammo and rarity in ("very_rare", "legendary", "artifact")

# Top item type codes (normalized, stripping source suffix after '|')
# Chosen for density in training set: covers majority of matched items
ITEM_TYPE_DUMMIES = ["M", "P", "SCF", "MA", "HA", "RG", "SC", "WD", "LA", "RD", "S", "INS", "A"]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build ML feature matrix from criteria columns."""
    X = pd.DataFrame()
    for col in FEATURE_COLS:
        if col in df.columns:
            X[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            X[col] = 0.0

    # One-hot rarity
    for r in RARITY_DUMMIES:
        X[f"rarity_{r}"] = (df["rarity"] == r).astype(float)

    # Attunement
    X["attune_open"] = (df["req_attune"] == "open").astype(float)
    X["attune_class"] = (df["req_attune"] == "class").astype(float)

    # One-hot item type (normalize by stripping source suffix after '|')
    base_type = df["item_type_code"].fillna("").str.split("|").str[0]
    for t in ITEM_TYPE_DUMMIES:
        X[f"type_{t}"] = (base_type == t).astype(float)

    # Derived feature: has ability score mods (items like Gauntlets of Ogre Power)
    # Parse ability_score_mods JSON string
    def has_ability_mods(val):
        if pd.isna(val) or val == "[]":
            return 0.0
        if isinstance(val, str):
            # Check for static mods like {"static": {"str": 19}}
            if "static" in val and any(stat in val for stat in ["str", "dex", "con", "int", "wis", "cha"]):
                return 1.0
        return 0.0
    X["has_ability_mods"] = df["ability_score_mods"].apply(has_ability_mods)

    return X


def main():
    import os
    if INPUT_CSV.exists():
        df = pd.read_csv(INPUT_CSV)
        print(f"Loaded {len(df)} items from {INPUT_CSV}")
    else:
        df = pd.read_csv(INPUT_FALLBACK_CSV)
        print(f"Loaded {len(df)} items from {INPUT_FALLBACK_CSV} (variant-adjusted not found)")

    # Train on items with amalgamated ground truth OR variant_price (scaled from generic parents)
    train_mask = df["amalgamated_price"].notna() | df["variant_price"].notna()
    train_df = df[train_mask].copy()
    print(f"Training set: {len(train_df)} items with amalgamated or variant prices")

    X = build_features(train_df)
    # Use amalgamated_price where available, fall back to variant_price
    target_prices = train_df["amalgamated_price"].combine_first(train_df["variant_price"])
    y = np.log1p(target_prices.values)  # log-transform for normality

    # Split with indices to maintain ability to reference original DataFrames
    indices = np.arange(len(train_df))
    train_idx, val_idx = train_test_split(indices, test_size=0.2, random_state=42)
    X_train = X.iloc[train_idx]
    X_val = X.iloc[val_idx]
    y_train = y[train_idx]
    y_val = y[val_idx]

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)

    # Train main XGBoost model
    print("\nTraining XGBoost model...")
    model = XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_s, y_train)

    y_pred_val = model.predict(X_val_s)
    r2_val = r2_score(y_val, y_pred_val)
    print(f"Validation R² (log-space): {r2_val:.4f}")

    # Train quantile models for price bands
    print("\nTraining quantile models for price bounds...")
    model_lower = XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        objective='reg:quantileerror',
        quantile_alpha=0.1
    )
    model_lower.fit(X_train_s, y_train)

    model_upper = XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        objective='reg:quantileerror',
        quantile_alpha=0.9
    )
    model_upper.fit(X_train_s, y_train)

    # Feature importance (main model)
    feature_importance = pd.Series(model.feature_importances_, index=X.columns)
    print("\nTop 10 feature importances:")
    print(feature_importance.nlargest(10).to_string())

    # Apply ML models to all items
    X_all = build_features(df)
    X_all_s = scaler.transform(X_all)

    ml_prices = np.expm1(model.predict(X_all_s))
    ml_prices = np.maximum(ml_prices, 1)  # No negative prices

    price_low = np.expm1(model_lower.predict(X_all_s))
    price_low = np.maximum(price_low, 0.01)

    price_high = np.expm1(model_upper.predict(X_all_s))
    price_high = np.maximum(price_high, 0.01)

# Ensure price_low <= price_high (quantile models can sometimes cross)
    price_high = np.maximum(price_high, price_low)

    df["ml_price"] = ml_prices
    df["price_low"] = price_low
    df["price_high"] = price_high

    # --- Tiered blend weights based on price_confidence ---
    print("\nUsing tiered blend weights based on price_confidence:")
    for conf, (amalg_w, rule_w) in CONFIDENCE_WEIGHTS.items():
        print(f"  {conf}: amalgamated_weight={amalg_w:.2f}, rule_weight={rule_w:.2f}")
    print(f"  DEFAULT_RULE_WEIGHT (for no amalgamated): {DEFAULT_RULE_WEIGHT:.2f}")

    # Confidence scoring
    print("\nAssigning confidence levels...")
    def get_confidence(row):
        # High: official price OR (amalgamated from >=3 sources)
        if pd.notna(row.get("official_price_gp")):
            return "High"
        if row.get("price_confidence") == "multi":
            sources = str(row.get("price_sources", "")).split(",")
            if len(sources) >= 3:
                return "High"
        # Medium: amalgamated from 2 sources
        if row.get("price_confidence") == "multi":
            sources = str(row.get("price_sources", "")).split(",")
            if len(sources) == 2:
                return "Medium"
        # Low: rule-only, ML-only, or single source
        return "Low"

    df["confidence"] = df.apply(get_confidence, axis=1)

    # Blend function using confidence-based tiered weights
    def blend_price(row):
        rarity = row.get("rarity", "")
        # Non-magic, special cases override
        if rarity in NON_MAGIC_RARITIES:
            return row["rule_price"]
        if is_material_armor(row):
            return row["rule_price"]
        if is_spell_scroll(row):
            return row["rule_price"]
        if is_high_rarity_ammunition(row):
            return row["rule_price"]
        if pd.notna(row.get("variant_price")):
            return row["rule_price"]
        if row.get("price_confidence") == "solo-outlier":
            return row["rule_price"]

        # Get confidence level
        confidence = row.get("price_confidence", "none")

        if pd.notna(row["amalgamated_price"]):
            # Has amalgamated price: use confidence-based weights
            w_amalg, _ = CONFIDENCE_WEIGHTS.get(confidence, (0.7, 0.35))
            return w_amalg * row["amalgamated_price"] + (1 - w_amalg) * row["ml_price"]
        else:
            # No amalgamated price: use rule + ML blend
            w_rule = DEFAULT_RULE_WEIGHT
            return w_rule * row["rule_price"] + (1 - w_rule) * row["ml_price"]

    df["final_price"] = df.apply(blend_price, axis=1)

    # Apply minimum price floor (1 copper piece)
    df["final_price"] = df["final_price"].clip(lower=0.01)

    # Ensure price bounds encompass final_price (ML quantile predictions don't account for blend)
    df["price_low"] = df[["price_low", "final_price"]].min(axis=1)
    df["price_high"] = df[["price_high", "final_price"]].max(axis=1)

    # Calculate final R² against amalgamated
    matched = df[df["amalgamated_price"].notna()].copy()
    r2_final = r2_score(
        np.log1p(matched["amalgamated_price"]),
        np.log1p(matched["final_price"])
    )
    print(f"\nFinal blended R² (log-space): {r2_final:.4f}")
    print(f"Target: ≥ 0.80")

    # Save output
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nWrote {len(df)} rows to {OUTPUT_CSV}")

    print("\nMedian final prices by rarity:")
    for rarity, group in df.groupby("rarity"):
        median = group["final_price"].median()
        print(f" {rarity}: {median:,.0f} gp (n={len(group)})")

    print("\nConfidence distribution:")
    conf_counts = df["confidence"].value_counts()
    for conf, count in conf_counts.items():
        print(f" {conf}: {count} items ({count/len(df)*100:.1f}%)")

if __name__ == '__main__':
    main()
