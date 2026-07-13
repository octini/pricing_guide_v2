from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "curation_preflight_2026_07_12.py"


def load_script_module():
    spec = importlib.util.spec_from_file_location("curation_preflight_2026_07_12", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_skips_cleanly_when_raw_input_is_missing(tmp_path, capsys):
    module = load_script_module()
    missing_input = tmp_path / "missing_2026_items.json"
    canonical_input = tmp_path / "trimmed_5etools_list.json"
    canonical_input.write_text("[]", encoding="utf-8")
    output = tmp_path / "reports" / "curation.md"

    exit_code = module.run(input_path=missing_input, canonical_path=canonical_input, output_path=output)

    assert exit_code == 0
    assert not output.exists()
    assert "Skipping curation preflight" in capsys.readouterr().out


def test_build_report_includes_required_curation_sections_and_sensitive_checks():
    module = load_script_module()
    raw_items = [
        {"name": "Concussion Grenade", "source": "QftIS", "type": "EXP"},
        {"name": "Sleep Grenade", "source": "QftIS", "type": "EXP"},
        {"name": "Crystal", "source": "PHB", "type": "$G", "value": 10000},
        {"name": "Crystal", "source": "DungeonsOfDrakkenheim", "type": "G", "rarity": "uncommon"},
        {"name": "Zeal", "source": "PHB", "type": "$G", "value": 10000},
        {"name": "Zeal", "source": "ObojimaTallGrass", "type": "G", "rarity": "common"},
        {"name": "Airship", "source": "NewOnlySource", "type": "SHP", "vehSpeed": 8},
        {"name": "Alchemical Fire Bomb", "source": "NewOnlySource", "type": "EXP"},
        {
            "name": "+1 Longsword",
            "source": "XDMG",
            "type": "M",
            "rarity": "uncommon",
            "genericVariant": {"name": "+1 Weapon"},
        },
        {
            "name": "+1 Shortsword",
            "source": "XDMG",
            "type": "M",
            "rarity": "uncommon",
            "genericVariant": {"name": "+1 Weapon"},
        },
    ]
    canonical_items = [
        {"name": "Crystal", "source": "PHB", "type": "$G", "value": 10000},
        {"name": "Abacus", "source": "PHB", "type": "G", "value": 200},
    ]

    report = module.build_report(
        raw_items,
        canonical_items,
        input_path=Path("2026_07_12_item_list.json"),
        canonical_path=Path("trimmed_5etools_list.json"),
    )

    assert "# 2026-07-12 Curation Preflight" in report
    assert "Raw 2026 items: 10" in report
    assert "Curated items after hard exclusions: 8" in report
    assert "## Source count delta summary" in report
    assert "NewOnlySource" in report
    assert "## Hard exclusions" in report
    assert "QftIS — Concussion Grenade" in report
    assert "QftIS — Sleep Grenade" in report
    assert "## Potential scope review items" in report
    assert "Alchemical Fire Bomb" in report
    assert "Airship" in report
    assert "## Duplicate/name collision summary" in report
    assert "Crystal" in report
    assert "keep-separate" in report
    assert "## Variant family and UI grouping candidates" in report
    assert "+1 Weapon" in report
    assert "## Readiness matrix" in report
    assert "Safe to migrate" in report
    assert "Needs user decision" in report
    assert "Needs extractor/pricing work" in report
    assert "Deferred" in report
    assert "raw 2026 files remain untracked" in report
