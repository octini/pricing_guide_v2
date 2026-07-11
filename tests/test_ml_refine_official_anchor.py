import importlib.util
from pathlib import Path

import pandas as pd
import pytest


def load_ml_refine_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "06_ml_refine.py"
    spec = importlib.util.spec_from_file_location("ml_refine", module_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_apply_post_blend_official_price_anchors_updates_final_price_and_returns_audit():
    ml_refine = load_ml_refine_module()
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
            }
        ]
    )

    anchored_df, audit_df = ml_refine.apply_post_blend_official_price_anchors(df)

    assert anchored_df.loc[0, "pre_anchor_final_price"] == pytest.approx(65.18)
    assert anchored_df.loc[0, "final_price"] == pytest.approx(51.75)
    assert audit_df.loc[0, "name"] == "Potion of Healing"
    assert audit_df.loc[0, "anchored_final_price"] == pytest.approx(51.75)
