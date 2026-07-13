import pandas as pd
import pytest

from src.official_price_anchor import (
    apply_official_price_anchors,
    anchor_official_price,
    build_official_price_audit,
)


def test_anchor_near_agreement_uses_official_and_rule_only_for_potion_like_rows():
    result = anchor_official_price(
        official_price=50.0,
        rule_price=58.75,
        computed_final=65.18,
    )

    assert result.tier == "near_agreement_official_heavy"
    assert result.final_price == pytest.approx(51.75)


def test_anchor_moderate_disagreement_uses_40_official_60_computed():
    result = anchor_official_price(
        official_price=100.0,
        rule_price=200.0,
        computed_final=300.0,
    )

    assert result.tier == "moderate_disagreement_blended"
    assert result.final_price == pytest.approx(220.0)


@pytest.mark.parametrize(
    ("official_price", "rule_price", "computed_final", "expected_final"),
    [
        (5.0, 1150.0, 858.7331512451171, 773.3598361206054),
        (250.0, 1250.0, 970.7769561767578, 898.6992605590821),
    ],
)
def test_anchor_high_disagreement_keeps_computed_heavy_values(
    official_price,
    rule_price,
    computed_final,
    expected_final,
):
    result = anchor_official_price(
        official_price=official_price,
        rule_price=rule_price,
        computed_final=computed_final,
    )

    assert result.tier == "high_disagreement_computed_heavy"
    assert result.final_price == pytest.approx(expected_final)


@pytest.mark.parametrize("official_price", [None, "", "not-a-number", float("nan"), float("inf"), 0, -50])
def test_anchor_invalid_official_price_keeps_computed_final_unchanged(official_price):
    result = anchor_official_price(
        official_price=official_price,
        rule_price=58.75,
        computed_final=65.18,
    )

    assert result.tier == "no_official_price"
    assert result.final_price == pytest.approx(65.18)
    assert result.ratio is None


@pytest.mark.parametrize("rule_price", [None, "", "not-a-number", float("nan"), float("inf"), 0, -58.75])
def test_anchor_invalid_rule_price_keeps_computed_final_unchanged(rule_price):
    result = anchor_official_price(
        official_price=50.0,
        rule_price=rule_price,
        computed_final=65.18,
    )

    assert result.tier == "missing_rule_price"
    assert result.final_price == pytest.approx(65.18)
    assert result.ratio is None


@pytest.mark.parametrize("computed_final", [None, "", "not-a-number", float("nan"), float("inf")])
def test_anchor_invalid_computed_final_does_not_raise_or_return_nonfinite(computed_final):
    result = anchor_official_price(
        official_price=100.0,
        rule_price=200.0,
        computed_final=computed_final,
    )

    assert result.tier == "invalid_computed_final"
    assert result.final_price == pytest.approx(0.0)
    assert result.ratio == pytest.approx(2.0)


def test_anchor_near_agreement_does_not_require_computed_final():
    result = anchor_official_price(
        official_price=50.0,
        rule_price=58.75,
        computed_final=None,
    )

    assert result.tier == "near_agreement_official_heavy"
    assert result.final_price == pytest.approx(51.75)
    assert result.ratio == pytest.approx(1.175)


@pytest.mark.parametrize("computed_final", [0, -10])
def test_anchor_zero_or_negative_computed_final_remains_finite(computed_final):
    result = anchor_official_price(
        official_price=100.0,
        rule_price=200.0,
        computed_final=computed_final,
    )

    assert result.tier == "moderate_disagreement_blended"
    assert result.final_price == pytest.approx(0.40 * 100.0 + 0.60 * computed_final)


def test_apply_official_price_anchors_records_pre_anchor_columns_and_deltas():
    df = pd.DataFrame(
        [
            {
                "name": "Potion of Healing",
                "source": "XDMG",
                "official_price_gp": 50.0,
                "rule_price": 58.75,
                "ml_price": 101.63,
                "final_price": 65.18,
            },
            {
                "name": "No Official Price",
                "source": "TEST",
                "official_price_gp": None,
                "rule_price": 100.0,
                "ml_price": 150.0,
                "final_price": 132.5,
            },
        ]
    )

    anchored = apply_official_price_anchors(df)

    assert anchored.loc[0, "pre_anchor_final_price"] == pytest.approx(65.18)
    assert anchored.loc[0, "final_price"] == pytest.approx(51.75)
    assert anchored.loc[0, "official_anchor_delta"] == pytest.approx(51.75 - 65.18)
    assert anchored.loc[1, "final_price"] == pytest.approx(132.5)
    assert anchored.loc[1, "official_anchor_tier"] == "no_official_price"


def test_apply_official_price_anchors_preserves_no_official_rows_exactly():
    df = pd.DataFrame(
        [
            {
                "name": "No Official Price",
                "source": "TEST",
                "official_price_gp": None,
                "rule_price": 100.0,
                "ml_price": 150.0,
                "final_price": 132.5,
            }
        ]
    )

    anchored = apply_official_price_anchors(df)

    assert anchored.loc[0, "final_price"] == df.loc[0, "final_price"]
    assert anchored.loc[0, "official_anchor_delta"] == 0


def test_apply_official_price_anchors_preserves_rows_with_invalid_rule_price():
    df = pd.DataFrame(
        [
            {
                "name": "Official Price With Invalid Rule",
                "source": "TEST",
                "official_price_gp": 50.0,
                "rule_price": None,
                "ml_price": 101.63,
                "final_price": 65.18,
            }
        ]
    )

    anchored = apply_official_price_anchors(df)

    assert anchored.loc[0, "final_price"] == df.loc[0, "final_price"]
    assert anchored.loc[0, "official_anchor_delta"] == 0
    assert anchored.loc[0, "official_anchor_tier"] == "missing_rule_price"


def test_apply_official_price_anchors_exactly_preserves_commodity_official_prices():
    df = pd.DataFrame(
        [
            {
                "name": "Ruby",
                "source": "XDMG",
                "rarity": "varies",
                "type": "$G|XDMG",
                "official_price_gp": 500.0,
                "rule_price": 900.0,
                "ml_price": 1200.0,
                "final_price": 1100.0,
            }
        ]
    )

    anchored = apply_official_price_anchors(df)

    assert anchored.loc[0, "final_price"] == pytest.approx(500.0)
    assert anchored.loc[0, "official_anchor_tier"] == "exact_commodity_official_price"
    assert anchored.loc[0, "official_anchor_delta"] == pytest.approx(-600.0)


def test_apply_official_price_anchors_does_not_exact_override_magic_material_variants():
    df = pd.DataFrame(
        [
            {
                "name": "+1 Adamantine Longsword",
                "source": "CallfromtheDeep",
                "rarity": "uncommon",
                "type": "M",
                "genericVariant": {"name": "+1 Adamantine Weapon"},
                "official_price_gp": 100.0,
                "rule_price": 2225.0,
                "ml_price": 2400.0,
                "final_price": 2500.0,
            }
        ]
    )

    anchored = apply_official_price_anchors(df)

    assert anchored.loc[0, "final_price"] != pytest.approx(100.0)
    assert anchored.loc[0, "official_anchor_tier"] == "high_disagreement_computed_heavy"


def test_build_official_price_audit_outputs_required_columns_for_official_rows_only():
    df = pd.DataFrame(
        [
            {
                "name": "Potion of Healing",
                "source": "XDMG",
                "rarity": "common",
                "type": "P|XPHB",
                "official_price_gp": 50.0,
                "rule_price": 58.75,
                "ml_price": 101.63,
                "final_price": 65.18,
            },
            {
                "name": "No Official Price",
                "source": "TEST",
                "rarity": "common",
                "type": "OTH",
                "official_price_gp": None,
                "rule_price": 100.0,
                "ml_price": 150.0,
                "final_price": 132.5,
            },
        ]
    )
    anchored = apply_official_price_anchors(df)

    audit = build_official_price_audit(anchored)

    assert audit.to_dict("records") == [
        {
            "name": "Potion of Healing",
            "source": "XDMG",
            "rarity": "common",
            "type": "P|XPHB",
            "official_price_gp": 50.0,
            "rule_price": 58.75,
            "ml_price": 101.63,
            "pre_anchor_final_price": 65.18,
            "anchored_final_price": pytest.approx(51.75),
            "official_anchor_ratio": pytest.approx(1.175),
            "official_anchor_tier": "near_agreement_official_heavy",
            "official_anchor_delta": pytest.approx(51.75 - 65.18),
        }
    ]
