from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "reports" / "price_creep_guardrail.py"


def load_script_module():
    spec = importlib.util.spec_from_file_location("price_creep_guardrail", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_price_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = ["Name", "Source", "Type", "Rarity", "Price (gp)", "Price Source", "Has Reference"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_run_writes_template_when_candidate_is_missing(tmp_path, capsys):
    module = load_script_module()
    baseline = tmp_path / "baseline.csv"
    candidate = tmp_path / "missing_candidate.csv"
    output = tmp_path / "guardrail.md"
    write_price_csv(
        baseline,
        [{"Name": "Holy Avenger", "Source": "DMG", "Type": "Weapon", "Rarity": "Legendary", "Price (gp)": "100000", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"}],
    )

    assert module.run(baseline_path=baseline, candidate_path=candidate, output_path=output) == 0

    report = output.read_text(encoding="utf-8")
    assert "# Price Creep Guardrail" in report
    assert "No candidate CSV supplied/found" in report
    assert str(candidate) in capsys.readouterr().out


def test_analyze_price_drift_splits_reference_formula_and_thresholds(tmp_path):
    module = load_script_module()
    baseline = tmp_path / "baseline.csv"
    candidate = tmp_path / "candidate.csv"
    write_price_csv(
        baseline,
        [
            {"Name": "Holy Avenger", "Source": "DMG", "Type": "Weapon", "Rarity": "Legendary", "Price (gp)": "100000", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"},
            {"Name": "Formula Wand", "Source": "HB", "Type": "Wand", "Rarity": "Rare", "Price (gp)": "1000", "Price Source": "Algorithm", "Has Reference": "False"},
            {"Name": "Defender", "Source": "DMG", "Type": "Weapon", "Rarity": "Legendary", "Price (gp)": "80000", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"},
            {"Name": "Missing Item", "Source": "HB", "Type": "Wondrous", "Rarity": "Uncommon", "Price (gp)": "500", "Price Source": "Algorithm", "Has Reference": "False"},
        ],
    )
    write_price_csv(
        candidate,
        [
            {"Name": "Holy Avenger", "Source": "DMG", "Type": "Weapon", "Rarity": "Legendary", "Price (gp)": "106000", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"},
            {"Name": "Formula Wand", "Source": "HB", "Type": "Wand", "Rarity": "Rare", "Price (gp)": "1200", "Price Source": "Algorithm", "Has Reference": "False"},
            {"Name": "Defender", "Source": "DMG", "Type": "Weapon", "Rarity": "Legendary", "Price (gp)": "80000", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"},
            {"Name": "New Item", "Source": "HB", "Type": "Wondrous", "Rarity": "Uncommon", "Price (gp)": "750", "Price Source": "Algorithm", "Has Reference": "False"},
        ],
    )

    analysis = module.analyze_price_drift(module.load_price_rows(baseline), module.load_price_rows(candidate))

    assert analysis["common_count"] == 3
    assert analysis["new_count"] == 1
    assert analysis["missing_count"] == 1
    assert analysis["aggregate"]["median_pct"] == pytest.approx(6.0)
    assert analysis["aggregate"]["mean_pct"] == pytest.approx((6.0 + 20.0 + 0.0) / 3)
    assert analysis["aggregate"]["median_gp"] == pytest.approx(200.0)
    assert analysis["threshold_counts"][">5%"] == 2
    assert analysis["threshold_counts"][">10%"] == 1
    assert analysis["threshold_counts"][">25%"] == 0
    assert analysis["reference_split"]["reference-anchored"]["count"] == 2
    assert analysis["reference_split"]["formula/ML-only"]["count"] == 1
    assert analysis["known_good_status"] == "FAIL"
    assert analysis["known_good_rows"][0]["Name"] == "Holy Avenger"


def test_split_classification_uses_price_source_not_has_reference(tmp_path):
    """Regression: Demonglass-Dart pattern — Has Reference=True but Price Source=Algorithm must be formula/ML-only."""
    module = load_script_module()
    baseline = tmp_path / "baseline.csv"
    candidate = tmp_path / "candidate.csv"
    # Demonglass Dart: stale Has Reference=True but actual Price Source is Algorithm → formula/ML-only
    # Holy Avenger: canonical Amalgamated → reference-anchored even if Has Reference=False (stale flag ignored)
    write_price_csv(
        baseline,
        [
            {"Name": "Demonglass Dart", "Source": "FoEQuickstone", "Type": "Weapon", "Rarity": "Rare", "Price (gp)": "1000", "Price Source": "Algorithm", "Has Reference": "True"},
            {"Name": "Holy Avenger", "Source": "DMG", "Type": "Weapon", "Rarity": "Legendary", "Price (gp)": "100000", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "False"},
            {"Name": "Official Item", "Source": "DMG", "Type": "Wondrous", "Rarity": "Uncommon", "Price (gp)": "500", "Price Source": "Official", "Has Reference": "True"},
            {"Name": "Single Source Item", "Source": "HB", "Type": "Wand", "Rarity": "Rare", "Price (gp)": "800", "Price Source": "Single source (DSA)", "Has Reference": "True"},
        ],
    )
    write_price_csv(
        candidate,
        [
            # Same Price Source values in candidate — split is taken from candidate row
            {"Name": "Demonglass Dart", "Source": "FoEQuickstone", "Type": "Weapon", "Rarity": "Rare", "Price (gp)": "1100", "Price Source": "Algorithm", "Has Reference": "True"},
            {"Name": "Holy Avenger", "Source": "DMG", "Type": "Weapon", "Rarity": "Legendary", "Price (gp)": "100000", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "False"},
            {"Name": "Official Item", "Source": "DMG", "Type": "Wondrous", "Rarity": "Uncommon", "Price (gp)": "500", "Price Source": "Official", "Has Reference": "True"},
            {"Name": "Single Source Item", "Source": "HB", "Type": "Wand", "Rarity": "Rare", "Price (gp)": "800", "Price Source": "Single source (DSA)", "Has Reference": "True"},
        ],
    )

    analysis = module.analyze_price_drift(module.load_price_rows(baseline), module.load_price_rows(candidate))
    # Only Holy Avenger is Amalgamated → reference-anchored; all others are formula/ML-only
    assert analysis["reference_split"]["reference-anchored"]["count"] == 1
    assert analysis["reference_split"]["formula/ML-only"]["count"] == 3
    # Verify per-row split assignment (candidate Price Source drives split)
    by_name = {row["Name"]: row["reference_split"] for row in analysis["rows"]}
    assert by_name["Demonglass Dart"] == "formula/ML-only"
    assert by_name["Holy Avenger"] == "reference-anchored"
    assert by_name["Official Item"] == "formula/ML-only"
    assert by_name["Single Source Item"] == "formula/ML-only"


def test_known_good_detection_covers_real_variant_families(tmp_path):
    module = load_script_module()
    baseline = tmp_path / "baseline.csv"
    candidate = tmp_path / "candidate.csv"
    anchor_names = ["+1 Battleaxe", "+2 Longsword", "+3 Plate Armor", "+1 Leather Armor", "Vicious Longsword"]
    write_price_csv(
        baseline,
        [
            {"Name": name, "Source": "XDMG", "Type": "Weapon" if "Armor" not in name else "Armor", "Rarity": "Rare", "Price (gp)": "1000", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"}
            for name in anchor_names
        ],
    )
    write_price_csv(
        candidate,
        [
            {"Name": name, "Source": "XDMG", "Type": "Weapon" if "Armor" not in name else "Armor", "Rarity": "Rare", "Price (gp)": "1010", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"}
            for name in anchor_names
        ],
    )

    analysis = module.analyze_price_drift(module.load_price_rows(baseline), module.load_price_rows(candidate))

    assert sorted(row["Name"] for row in analysis["known_good_rows"]) == sorted(anchor_names)
    assert analysis["known_good_status"] == "PASS"


def test_known_good_detection_does_not_treat_non_weapon_armor_plus_items_as_anchor(tmp_path):
    module = load_script_module()
    baseline = tmp_path / "baseline.csv"
    candidate = tmp_path / "candidate.csv"
    write_price_csv(
        baseline,
        [
            {"Name": "+3 Fate Dealer's Deck", "Source": "BMT", "Type": "Wondrous Item", "Rarity": "Legendary", "Price (gp)": "1000", "Price Source": "Algorithm", "Has Reference": "False"},
            {"Name": "+2 Dragonhide Belt", "Source": "FTD", "Type": "Wondrous Item", "Rarity": "Rare", "Price (gp)": "1000", "Price Source": "Algorithm", "Has Reference": "False"},
        ],
    )
    write_price_csv(
        candidate,
        [
            {"Name": "+3 Fate Dealer's Deck", "Source": "BMT", "Type": "Wondrous Item", "Rarity": "Legendary", "Price (gp)": "1200", "Price Source": "Algorithm", "Has Reference": "False"},
            {"Name": "+2 Dragonhide Belt", "Source": "FTD", "Type": "Wondrous Item", "Rarity": "Rare", "Price (gp)": "1200", "Price Source": "Algorithm", "Has Reference": "False"},
        ],
    )

    analysis = module.analyze_price_drift(module.load_price_rows(baseline), module.load_price_rows(candidate))

    assert analysis["known_good_rows"] == []
    assert analysis["known_good_status"] == "PASS"


def test_variant_family_known_good_drift_drives_review_and_fail_status(tmp_path):
    module = load_script_module()
    baseline = tmp_path / "baseline.csv"
    candidate = tmp_path / "candidate.csv"
    write_price_csv(
        baseline,
        [
            {"Name": "+1 Battleaxe", "Source": "XDMG", "Type": "Weapon", "Rarity": "Uncommon", "Price (gp)": "1000", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"},
            {"Name": "Vicious Rapier", "Source": "XDMG", "Type": "Weapon", "Rarity": "Rare", "Price (gp)": "1000", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"},
        ],
    )
    write_price_csv(
        candidate,
        [
            {"Name": "+1 Battleaxe", "Source": "XDMG", "Type": "Weapon", "Rarity": "Uncommon", "Price (gp)": "1020", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"},
            {"Name": "Vicious Rapier", "Source": "XDMG", "Type": "Weapon", "Rarity": "Rare", "Price (gp)": "1020", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"},
        ],
    )
    review_analysis = module.analyze_price_drift(module.load_price_rows(baseline), module.load_price_rows(candidate))
    assert review_analysis["known_good_status"] == "REVIEW"

    write_price_csv(
        candidate,
        [
            {"Name": "+1 Battleaxe", "Source": "XDMG", "Type": "Weapon", "Rarity": "Uncommon", "Price (gp)": "1060", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"},
            {"Name": "Vicious Rapier", "Source": "XDMG", "Type": "Weapon", "Rarity": "Rare", "Price (gp)": "1000", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"},
        ],
    )
    fail_analysis = module.analyze_price_drift(module.load_price_rows(baseline), module.load_price_rows(candidate))
    assert fail_analysis["known_good_status"] == "FAIL"


def test_generic_anchor_names_are_known_good_even_without_type_context(tmp_path):
    module = load_script_module()
    baseline = tmp_path / "baseline.csv"
    candidate = tmp_path / "candidate.csv"
    generic_names = ["+1 Weapon", "+2 Armor", "+3 Weapon"]
    write_price_csv(
        baseline,
        [
            {"Name": name, "Source": "XDMG", "Type": "", "Rarity": "Rare", "Price (gp)": "1000", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"}
            for name in generic_names
        ],
    )
    write_price_csv(
        candidate,
        [
            {"Name": name, "Source": "XDMG", "Type": "", "Rarity": "Rare", "Price (gp)": "1010", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"}
            for name in generic_names
        ],
    )

    analysis = module.analyze_price_drift(module.load_price_rows(baseline), module.load_price_rows(candidate))

    assert sorted(row["Name"] for row in analysis["known_good_rows"]) == sorted(generic_names)
    assert analysis["known_good_status"] == "PASS"


def test_known_good_detection_covers_vorpal_weapon_variants(tmp_path):
    module = load_script_module()
    baseline = tmp_path / "baseline.csv"
    candidate = tmp_path / "candidate.csv"
    vorpal_names = ["Vorpal Longsword", "Vorpal Rapier"]
    write_price_csv(
        baseline,
        [
            {"Name": name, "Source": "XDMG", "Type": "Weapon", "Rarity": "Legendary", "Price (gp)": "100000", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"}
            for name in vorpal_names
        ],
    )
    write_price_csv(
        candidate,
        [
            {"Name": name, "Source": "XDMG", "Type": "Weapon", "Rarity": "Legendary", "Price (gp)": "102000", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"}
            for name in vorpal_names
        ],
    )

    analysis = module.analyze_price_drift(module.load_price_rows(baseline), module.load_price_rows(candidate))

    assert sorted(row["Name"] for row in analysis["known_good_rows"]) == sorted(vorpal_names)
    assert analysis["known_good_status"] == "REVIEW"


def test_vorpal_anchor_detection_requires_weapon_context(tmp_path):
    module = load_script_module()
    baseline = tmp_path / "baseline.csv"
    candidate = tmp_path / "candidate.csv"
    write_price_csv(
        baseline,
        [{"Name": "Vorpal Hat", "Source": "HB", "Type": "Wondrous Item", "Rarity": "Legendary", "Price (gp)": "100000", "Price Source": "Algorithm", "Has Reference": "False"}],
    )
    write_price_csv(
        candidate,
        [{"Name": "Vorpal Hat", "Source": "HB", "Type": "Wondrous Item", "Rarity": "Legendary", "Price (gp)": "120000", "Price Source": "Algorithm", "Has Reference": "False"}],
    )

    analysis = module.analyze_price_drift(module.load_price_rows(baseline), module.load_price_rows(candidate))

    assert analysis["known_good_rows"] == []
    assert analysis["known_good_status"] == "PASS"


def test_report_includes_guardrail_sections_and_anchor_guidance(tmp_path):
    module = load_script_module()
    baseline = tmp_path / "baseline.csv"
    candidate = tmp_path / "candidate.csv"
    output = tmp_path / "guardrail.md"
    write_price_csv(
        baseline,
        [
            {"Name": "Holy Avenger", "Source": "DMG", "Type": "Weapon", "Rarity": "Legendary", "Price (gp)": "100000", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"},
            {"Name": "Formula Wand", "Source": "HB", "Type": "Wand", "Rarity": "Rare", "Price (gp)": "1000", "Price Source": "Algorithm", "Has Reference": "False"},
        ],
    )
    write_price_csv(
        candidate,
        [
            {"Name": "Holy Avenger", "Source": "DMG", "Type": "Weapon", "Rarity": "Legendary", "Price (gp)": "106000", "Price Source": "Amalgamated (DSA,MSRP,DMPG)", "Has Reference": "True"},
            {"Name": "Formula Wand", "Source": "HB", "Type": "Wand", "Rarity": "Rare", "Price (gp)": "1200", "Price Source": "Algorithm", "Has Reference": "False"},
        ],
    )

    assert module.run(baseline_path=baseline, candidate_path=candidate, output_path=output) == 0
    report = output.read_text(encoding="utf-8")

    assert "## Aggregate final-price drift" in report
    assert "## Reference anchored vs formula/ML-only" in report
    assert "## Drift by rarity" in report
    assert "## Drift by type" in report
    assert "## Drift by source" in report
    assert "## Known-good anchors" in report
    assert "Known-good status: **FAIL**" in report
    assert "Holy Avenger" in report
    assert "## Artifact/legendary movers" in report
    assert "## Largest movers" in report
    assert "## Largest percent movers" in report
    assert "Formula exposure reports" in report


def test_report_largest_percent_movers_are_sorted_by_absolute_percent(tmp_path):
    module = load_script_module()
    baseline = tmp_path / "baseline.csv"
    candidate = tmp_path / "candidate.csv"
    output = tmp_path / "guardrail.md"
    write_price_csv(
        baseline,
        [
            {"Name": "Expensive Small Drift", "Source": "HB", "Type": "Wondrous", "Rarity": "Rare", "Price (gp)": "100000", "Price Source": "Algorithm", "Has Reference": "False"},
            {"Name": "Tiny Huge Drift", "Source": "HB", "Type": "Wondrous", "Rarity": "Common", "Price (gp)": "10", "Price Source": "Algorithm", "Has Reference": "False"},
            {"Name": "Middle Drift", "Source": "HB", "Type": "Wondrous", "Rarity": "Uncommon", "Price (gp)": "100", "Price Source": "Algorithm", "Has Reference": "False"},
        ],
    )
    write_price_csv(
        candidate,
        [
            {"Name": "Expensive Small Drift", "Source": "HB", "Type": "Wondrous", "Rarity": "Rare", "Price (gp)": "101000", "Price Source": "Algorithm", "Has Reference": "False"},
            {"Name": "Tiny Huge Drift", "Source": "HB", "Type": "Wondrous", "Rarity": "Common", "Price (gp)": "100", "Price Source": "Algorithm", "Has Reference": "False"},
            {"Name": "Middle Drift", "Source": "HB", "Type": "Wondrous", "Rarity": "Uncommon", "Price (gp)": "150", "Price Source": "Algorithm", "Has Reference": "False"},
        ],
    )

    assert module.run(baseline_path=baseline, candidate_path=candidate, output_path=output) == 0
    report = output.read_text(encoding="utf-8")
    percent_section = report.split("## Largest percent movers", 1)[1]

    assert percent_section.index("Tiny Huge Drift") < percent_section.index("Middle Drift")
    assert percent_section.index("Middle Drift") < percent_section.index("Expensive Small Drift")
