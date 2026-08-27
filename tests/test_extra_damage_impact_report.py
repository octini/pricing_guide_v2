from __future__ import annotations

import importlib.util
import csv
import json
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "extra_damage_impact_2026_07_12.py"


def load_script_module():
    spec = importlib.util.spec_from_file_location("extra_damage_impact_2026_07_12", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_skips_cleanly_when_required_inputs_are_missing(tmp_path, capsys):
    module = load_script_module()
    output = tmp_path / "extra_damage.md"

    exit_code = module.run(
        master_path=tmp_path / "missing_items_master.csv",
        prose_path=tmp_path / "missing_items.md",
        output_path=output,
    )

    assert exit_code == 0
    assert not output.exists()
    assert "Skipping extra_damage impact" in capsys.readouterr().out


def test_analyze_items_reports_prose_driven_extra_damage_delta():
    module = load_script_module()
    item = {
        "name": "Burning Blade",
        "source": "SRC",
        "rarity": "rare",
        "type": "M",
        "entries": [],
    }
    prose_map = {"burning blade": "When you hit, the attack deals an extra 1d8 damage."}

    analysis = module.analyze_items([item], prose_map, price_lookup={})

    assert analysis["changed_count"] == 1
    assert analysis["old_total_extra_damage_avg"] == 0
    assert analysis["new_total_extra_damage_avg"] == 4.5
    assert analysis["new_total_weighted_extra_damage_avg"] == 4.5
    assert analysis["direct_formula_exposure_gp"] == 6750
    row = analysis["rows"][0]
    assert row["name"] == "Burning Blade"
    assert row["old_extra_damage_avg"] == 0
    assert row["new_extra_damage_avg"] == 4.5
    assert row["new_extra_damage_multiplier"] == 1.0
    assert row["delta_exposure_gp"] == 6750
    assert "extra 1d8 damage" in row["evidence"]


def test_existing_dragons_wrath_override_is_not_reported_as_new_impact():
    module = load_script_module()
    item = {
        "name": "Ascendant Dragon's Wrath Longsword",
        "source": "FTD",
        "rarity": "legendary",
        "type": "M",
        "entries": [],
    }
    prose_map = {
        "ascendant dragon's wrath longsword": "On a hit, the weapon deals an extra 3d6 damage of the type dealt by the dragon's breath weapon."
    }

    analysis = module.analyze_items([item], prose_map, price_lookup={})

    assert analysis["changed_count"] == 0
    assert analysis["old_total_extra_damage_avg"] == 10.5
    assert analysis["new_total_extra_damage_avg"] == 10.5
    assert analysis["new_total_weighted_extra_damage_avg"] == 10.5
    assert analysis["direct_formula_exposure_gp"] == 0


def test_slumbering_dragons_wrath_raw_average_changes_but_weighted_exposure_does_not():
    module = load_script_module()
    item = {
        "name": "Slumbering Dragon's Wrath Longsword",
        "source": "FTD",
        "rarity": "uncommon",
        "type": "M",
        "entries": [],
    }

    analysis = module.analyze_items([item], {}, price_lookup={})

    row = analysis["rows"][0]
    assert row["old_extra_damage_avg"] == 0.175
    assert row["new_extra_damage_avg"] == 3.5
    assert row["new_extra_damage_multiplier"] == 0.05
    assert row["delta_exposure_gp"] == pytest.approx(0)


def test_conditional_creature_type_damage_uses_multiplier_for_exposure():
    module = load_script_module()
    item = {
        "name": "Stonebane Longsword",
        "source": "FoEQuickstone",
        "rarity": "uncommon",
        "type": "M",
        "entries": [],
    }
    prose_map = {
        "stonebane longsword": "Whenever you hit a Gargoyle with this weapon, the target takes an extra 1d6 damage."
    }

    analysis = module.analyze_items([item], prose_map, price_lookup={})

    row = analysis["rows"][0]
    assert row["new_extra_damage_avg"] == 3.5
    assert row["new_extra_damage_condition"] == "vs_creature_type"
    assert row["new_extra_damage_multiplier"] == 0.25
    assert row["delta_exposure_gp"] == 1500 * 3.5 * 0.25


def test_report_includes_summary_rows_and_direct_exposure_note():
    module = load_script_module()
    analysis = {
        "item_count": 1,
        "changed_count": 1,
        "old_total_extra_damage_avg": 0.0,
        "new_total_extra_damage_avg": 7.0,
        "total_delta_extra_damage_avg": 7.0,
        "new_total_weighted_extra_damage_avg": 7.0,
        "direct_formula_exposure_gp": 21000.0,
        "high_rarity_count": 1,
        "artifact_count": 0,
        "known_good_anchor_count": 1,
        "rows": [
            {
                "name": "Frostfire Blade",
                "source": "SRC",
                "rarity": "legendary",
                "type": "M",
                "old_extra_damage_avg": 0.0,
                "new_extra_damage_avg": 7.0,
                "delta_extra_damage_avg": 7.0,
                "new_extra_damage_multiplier": 1.0,
                "delta_weighted_extra_damage_avg": 7.0,
                "delta_exposure_gp": 21000.0,
                "current_output_price": "12,000 gp",
                "known_good_anchor": True,
                "evidence": "additional 2d6 fire or cold damage",
            }
        ],
    }

    report = module.build_report(analysis)

    assert "# extra_damage_avg Current Canonical Impact" in report
    assert "Changed current canonical rows: 1" in report
    assert "Direct formula exposure: 21,000 gp" in report
    assert "not a full pipeline price delta" in report
    assert "Frostfire Blade" in report
    assert "additional 2d6 fire or cold damage" in report


def test_run_handles_large_raw_json_fields(tmp_path):
    module = load_script_module()
    master = tmp_path / "items_master.csv"
    prose = tmp_path / "items-sublist.md"
    output = tmp_path / "extra_damage.md"
    large_entry = "x" * 150_000
    raw_json = json.dumps({"name": "Large Entry Blade", "source": "SRC", "entries": [large_entry]})

    with master.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "source", "rarity", "type", "raw_json"])
        writer.writeheader()
        writer.writerow(
            {
                "name": "Large Entry Blade",
                "source": "SRC",
                "rarity": "rare",
                "type": "M",
                "raw_json": raw_json,
            }
        )
    prose.write_text("#### Large Entry Blade\n\nWeapon\n\n---\n\nNo extra damage.\n", encoding="utf-8")

    assert module.run(master_path=master, prose_path=prose, output_path=output) == 0
    assert output.exists()
