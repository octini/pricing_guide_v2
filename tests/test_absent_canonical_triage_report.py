from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "triage_absent_canonical_2026_07_12.py"


def load_script_module():
    spec = importlib.util.spec_from_file_location("triage_absent_canonical_2026_07_12", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_skips_cleanly_when_raw_input_is_missing(tmp_path, capsys):
    module = load_script_module()
    missing_raw = tmp_path / "missing_2026_items.json"
    canonical = tmp_path / "trimmed_5etools_list.json"
    canonical.write_text("[]", encoding="utf-8")
    output = tmp_path / "reports" / "absent.md"

    exit_code = module.run(input_path=missing_raw, canonical_path=canonical, output_path=output)

    assert exit_code == 0
    assert not output.exists()
    assert "Skipping absent-canonical triage" in capsys.readouterr().out


def test_analyze_absent_rows_distinguishes_raw_absent_from_curated_absent():
    module = load_script_module()
    canonical_items = [
        {"name": "Concussion Grenade", "source": "QftIS"},
        {"name": "Sleep Grenade", "source": "QftIS"},
        {"name": "Spelljamming Helm", "source": "AAG"},
    ]
    raw_items = [
        {"name": "Concussion Grenade", "source": "QftIS"},
        {"name": "Sleep Grenade", "source": "QftIS"},
    ]

    analysis = module.analyze_absent_rows(canonical_items, raw_items, price_lookup={})

    assert analysis["raw_absent_count"] == 1
    assert analysis["curated_absent_count"] == 3
    assert analysis["hard_exclusion_absent_count"] == 2
    classifications = {row["name"]: row["classification"] for row in analysis["rows"]}
    assert classifications["Concussion Grenade"].startswith("hard exclusion")
    assert classifications["Sleep Grenade"].startswith("hard exclusion")
    assert classifications["Spelljamming Helm"].startswith("intentional scope exclusion")


def test_report_includes_harkons_bite_rename_and_crystal_keep_separate_checks():
    module = load_script_module()
    canonical_items = [
        {"name": "Harkon's Bite", "source": "VRGR", "rarity": "rare", "type": "WD"},
        {"name": "Crystal", "source": "PHB", "type": "$G"},
        {"name": "Crystal", "source": "MonstersOfDrakkenheim", "rarity": "uncommon", "type": "G"},
    ]
    raw_items = [
        {"name": "Harkon's Bite", "source": "RHW", "rarity": "rare", "type": "WD"},
        {"name": "Crystal", "source": "XPHB", "type": "$G"},
        {"name": "Crystal", "source": "MonstersOfDrakkenheim", "rarity": "uncommon", "type": "G"},
    ]

    report = module.build_report(
        canonical_items,
        raw_items,
        input_path=Path("2026_07_12_item_list.json"),
        canonical_path=Path("trimmed_5etools_list.json"),
        price_lookup={},
    )

    assert "Harkon's Bite" in report
    assert "source-code rename" in report
    assert "VRGR → RHW" in report
    assert "Crystal" in report
    assert "keep-separate" in report
    assert "Crystal (XPHB)" in report
    assert "Crystal (MonstersOfDrakkenheim)" in report
    assert "Recommendation: approve all classified omissions" in report


def test_report_identifies_wtthc_and_rmbre_as_collaboration_tie_ins_without_draft_labels():
    module = load_script_module()
    canonical_items = [
        {"name": "Cap of Vanishing", "source": "WttHC", "rarity": "uncommon"},
        {"name": "Cloak of Billowing", "source": "WttHC", "rarity": "common"},
        {"name": "Concertina", "source": "RMBRE", "rarity": "rare"},
    ]
    raw_items = [
        {"name": "Cloak of Billowing", "source": "XDMG", "rarity": "common"},
    ]

    report = module.build_report(
        canonical_items,
        raw_items,
        input_path=Path("2026_07_12_item_list.json"),
        canonical_path=Path("trimmed_5etools_list.json"),
        price_lookup={},
    )

    assert "Welcome to the Hellfire Club" in report
    assert "Stranger Things collaboration" in report
    assert "The Lost Dungeon of Rickedness: Big Rick Energy" in report
    assert "Rick and Morty collaboration" in report
    assert "collaboration-only row — user-approved drop" in report
    assert "superseded collaboration row — XDMG replacement" in report
    assert "absent from the 2026 export and not a known-good/core carry-forward row" in report
    assert "draft" not in report.lower()
