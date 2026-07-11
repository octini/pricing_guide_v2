"""Official-price anchoring helpers for post-blend price adjustment."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any

import pandas as pd


NEAR_AGREEMENT_MAX_RATIO = 1.25
MODERATE_DISAGREEMENT_MAX_RATIO = 2.5

NO_OFFICIAL_PRICE_TIER = "no_official_price"
MISSING_RULE_PRICE_TIER = "missing_rule_price"
INVALID_COMPUTED_FINAL_TIER = "invalid_computed_final"
NEAR_AGREEMENT_TIER = "near_agreement_official_heavy"
MODERATE_DISAGREEMENT_TIER = "moderate_disagreement_blended"
HIGH_DISAGREEMENT_TIER = "high_disagreement_computed_heavy"


@dataclass(frozen=True)
class OfficialPriceAnchorResult:
    final_price: float
    tier: str
    ratio: float | None


def _coerce_finite_number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _coerce_positive_number(value: Any) -> float | None:
    number = _coerce_finite_number(value)
    if number is None or number <= 0:
        return None
    return number


def _is_positive_number(value: Any) -> bool:
    return _coerce_positive_number(value) is not None


def anchor_official_price(
    *,
    official_price: Any,
    rule_price: Any,
    computed_final: Any,
) -> OfficialPriceAnchorResult:
    """Return the post-blend price anchored by an official price, if available.

    The anchor is deliberately not an absolute override. It compares the rule
    engine price to the official price and reduces ML/community-guide influence
    only when the deterministic rule engine already agrees with the official
    price.
    """
    computed = _coerce_finite_number(computed_final)
    official = _coerce_positive_number(official_price)
    rule = _coerce_positive_number(rule_price)

    safe_computed = computed if computed is not None else 0.0

    if official is None:
        return OfficialPriceAnchorResult(safe_computed, NO_OFFICIAL_PRICE_TIER, None)
    if rule is None:
        return OfficialPriceAnchorResult(safe_computed, MISSING_RULE_PRICE_TIER, None)

    ratio = rule / official

    if ratio <= NEAR_AGREEMENT_MAX_RATIO:
        final_price = 0.80 * official + 0.20 * rule
        tier = NEAR_AGREEMENT_TIER
    elif computed is None:
        return OfficialPriceAnchorResult(safe_computed, INVALID_COMPUTED_FINAL_TIER, ratio)
    elif ratio <= MODERATE_DISAGREEMENT_MAX_RATIO:
        final_price = 0.40 * official + 0.60 * computed
        tier = MODERATE_DISAGREEMENT_TIER
    else:
        final_price = 0.10 * official + 0.90 * computed
        tier = HIGH_DISAGREEMENT_TIER

    return OfficialPriceAnchorResult(final_price, tier, ratio)


def apply_official_price_anchors(df: pd.DataFrame) -> pd.DataFrame:
    """Apply official-price anchors to final_price and record audit columns."""
    anchored = df.copy()
    anchored["pre_anchor_final_price"] = anchored["final_price"]

    results = anchored.apply(
        lambda row: anchor_official_price(
            official_price=row.get("official_price_gp"),
            rule_price=row.get("rule_price"),
            computed_final=row.get("pre_anchor_final_price"),
        ),
        axis=1,
    )

    anchored["final_price"] = results.apply(lambda result: result.final_price)
    anchored["official_anchor_tier"] = results.apply(lambda result: result.tier)
    anchored["official_anchor_ratio"] = results.apply(lambda result: result.ratio)
    anchored["official_anchor_delta"] = anchored.apply(
        lambda row: (
            row["final_price"] - row["pre_anchor_final_price"]
            if _coerce_finite_number(row.get("pre_anchor_final_price")) is not None
            else 0.0
        ),
        axis=1,
    )

    return anchored


def build_official_price_audit(df: pd.DataFrame) -> pd.DataFrame:
    """Build a deterministic report for all rows with official prices."""
    if "pre_anchor_final_price" not in df.columns or "official_anchor_tier" not in df.columns:
        df = apply_official_price_anchors(df)

    official_mask = df["official_price_gp"].apply(_is_positive_number)
    audit = df.loc[official_mask].copy()
    audit["anchored_final_price"] = audit["final_price"]
    audit["abs_official_anchor_delta"] = audit["official_anchor_delta"].abs()

    columns = [
        "name",
        "source",
        "rarity",
        "type",
        "official_price_gp",
        "rule_price",
        "official_anchor_ratio",
        "ml_price",
        "pre_anchor_final_price",
        "anchored_final_price",
        "official_anchor_tier",
        "official_anchor_delta",
    ]
    existing_columns = [column for column in columns if column in audit.columns]

    sorted_audit = (
        audit.sort_values(
            by=["abs_official_anchor_delta", "name", "source"],
            ascending=[False, True, True],
            kind="mergesort",
        )
        .loc[:, existing_columns]
        .reset_index(drop=True)
    )
    numeric_columns = sorted_audit.select_dtypes(include="number").columns
    sorted_audit[numeric_columns] = sorted_audit[numeric_columns].round(6)
    return sorted_audit


def write_official_price_audit(df: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    """Write the official-price anchor audit CSV and return the report frame."""
    audit = build_official_price_audit(df)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(output_path, index=False)
    return audit
