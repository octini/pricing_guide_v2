#!/usr/bin/env python3
"""Phase 6: ML coefficient refinement using Ridge regression."""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).parent.parent))

INPUT_CSV = Path("data/processed/items_priced.csv")
OUTPUT_CSV = Path("data/processed/items_ml_priced.csv")

# Features for ML: these are the additive criteria values
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
]

RARITY_DUMMIES = ["common", "uncommon", "rare", "very_rare", "legendary", "artifact"]

# Rarities that should NOT use ML blending (model trained on magic items)
NON_MAGIC_RARITIES = {"mundane", "unknown", "varies"}

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

    return X


def main():
    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} items")

    # Only train on items with amalgamated ground truth
    train_mask = df["amalgamated_price"].notna()
    train_df = df[train_mask].copy()
    print(f"Training set: {len(train_df)} items with amalgamated prices")

    X = build_features(train_df)
    y = np.log1p(train_df["amalgamated_price"].values)  # log-transform for normality

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)

    model = Ridge(alpha=1.0)
    model.fit(X_train_s, y_train)

    y_pred_val = model.predict(X_val_s)
    r2_val = r2_score(y_val, y_pred_val)
    print(f"\nValidation R² (log-space): {r2_val:.4f}")

    # Show top feature importances
    feature_importance = pd.Series(np.abs(model.coef_), index=X.columns)
    print("\nTop 10 feature importances:")
    print(feature_importance.nlargest(10).to_string())

    # Apply ML model to all items
    X_all = build_features(df)
    X_all_s = scaler.transform(X_all)
    ml_prices = np.expm1(model.predict(X_all_s))
    ml_prices = np.maximum(ml_prices, 1)  # No negative prices
    df["ml_price"] = ml_prices

    # Blend: rule price gets 40% weight, ML gets 60% for matched items
    # For unmatched items, ML with item_type features is more discriminating
    def blend_price(row):
        # Don't blend non-magic items with a model trained on magic items
        if row.get("rarity", "") in NON_MAGIC_RARITIES:
            return row["rule_price"]
        if pd.notna(row["amalgamated_price"]):
            # Has ground truth: blend rule and ML
            return 0.4 * row["rule_price"] + 0.6 * row["ml_price"]
        else:
            # No ground truth: bias toward ML after item_type feature addition
            return 0.35 * row["rule_price"] + 0.65 * row["ml_price"]

    df["final_price"] = df.apply(blend_price, axis=1)

    # Apply minimum price floor (1 copper piece)
    df["final_price"] = df["final_price"].clip(lower=0.01)

    # Calculate final R² against amalgamated
    matched = df[df["amalgamated_price"].notna()].copy()
    r2_final = r2_score(
        np.log1p(matched["amalgamated_price"]),
        np.log1p(matched["final_price"])
    )
    print(f"\nFinal blended R² (log-space): {r2_final:.4f}")
    print(f"Target: ≥ 0.80")

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nWrote {len(df)} rows to {OUTPUT_CSV}")

    print("\nMedian final prices by rarity:")
    for rarity, group in df.groupby("rarity"):
        median = group["final_price"].median()
        print(f"  {rarity}: {median:,.0f} gp (n={len(group)})")


if __name__ == "__main__":
    main()
