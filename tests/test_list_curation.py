from pathlib import Path

import pytest

from src.list_curation import (
    build_curation_report,
    curate_items,
    format_curation_report_markdown,
    is_commodity_exact_price_candidate,
    is_excluded_item,
    is_magic_material_official_price_conflict_candidate,
    is_nested_generic_parent,
    load_item_list,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_2026_ITEM_LIST = REPO_ROOT / "2026_07_12_item_list.json"


def test_policy_excludes_only_exact_qftis_grenades():
    assert is_excluded_item({"name": "Concussion Grenade", "source": "QftIS"}) is True
    assert is_excluded_item({"name": "Sleep Grenade", "source": "QftIS"}) is True
    assert is_excluded_item({"name": "Concussion Grenade", "source": "TEST"}) is False
    assert is_excluded_item({"name": "Frag Grenade", "source": "QftIS"}) is False


def test_curate_items_excludes_exact_qftis_grenades_and_keeps_safe_neighbors():
    concussion = {"name": "Concussion Grenade", "source": "QftIS", "type": "EXP"}
    sleep = {"name": "Sleep Grenade", "source": "QftIS", "type": "EXP"}
    fantasy_airship = {"name": "Airship", "source": "AAG", "type": "VEH"}
    skyship = {"name": "Skyship", "source": "TEST", "type": "VEH"}
    non_qftis_concussion = {"name": "Concussion Grenade", "source": "TEST", "type": "EXP"}
    fantasy_explosive = {"name": "Alchemist's Fire Grenade", "source": "HB", "type": "EXP"}

    curated = curate_items(
        [concussion, sleep, fantasy_airship, skyship, non_qftis_concussion, fantasy_explosive]
    )

    assert curated.excluded_items == [concussion, sleep]
    assert curated.kept_items == [fantasy_airship, skyship, non_qftis_concussion, fantasy_explosive]
    assert curated.report["total_items"] == 6
    assert curated.report["curated_items_count"] == 4
    assert curated.report["excluded_items_count"] == 2


@pytest.mark.skipif(
    not RAW_2026_ITEM_LIST.exists(),
    reason="2026_07_12_item_list.json is intentionally untracked; skip raw-file integration test",
)
def test_curate_items_for_2026_input_removes_only_two_qftis_grenades():
    items = load_item_list(RAW_2026_ITEM_LIST)

    curated = curate_items(items)

    assert curated.report["total_items"] == 12243
    assert curated.report["curated_items_count"] == curated.report["total_items"] - 2
    assert [item["name"] for item in curated.excluded_items] == [
        "Concussion Grenade",
        "Sleep Grenade",
    ]
    assert {item["source"] for item in curated.excluded_items} == {"QftIS"}


def test_nested_generic_parent_detection_searches_entries_text_only():
    parent = {
        "name": "Aussie Creature: Hairy-Nosed Wombat",
        "source": "GriffonsSaddlebag2",
        "rarity": "varies",
        "entries": [
            {
                "type": "entries",
                "entries": ["Multiple variations of this item exist, as listed below."],
            }
        ],
    }
    unrelated_varies = {
        "name": "Variable Charm",
        "source": "TEST",
        "rarity": "varies",
        "entries": ["The charm has a value that varies by settlement."],
    }

    assert is_nested_generic_parent(parent) is True
    assert is_nested_generic_parent(unrelated_varies) is False


@pytest.mark.parametrize("item_type", ["$A", "$G|XDMG", "$C", "TG", "TB"])
def test_commodity_exact_price_candidates_are_limited_to_pure_wealth_types(item_type):
    item = {
        "name": "Trade Good",
        "source": "XDMG",
        "rarity": "varies",
        "type": item_type,
        "value": 50000,
    }

    assert is_commodity_exact_price_candidate(item) is True


def test_magic_material_variants_with_raw_values_are_not_commodity_exact_candidates():
    item = {
        "name": "+1 Adamantine Longsword",
        "source": "CallfromtheDeep",
        "rarity": "uncommon",
        "type": "M",
        "value": 10000,
        "genericVariant": {"name": "+1 Adamantine Weapon"},
    }

    assert is_commodity_exact_price_candidate(item) is False
    assert is_magic_material_official_price_conflict_candidate(item) is True


def test_build_curation_report_counts_policy_findings_without_modifying_items():
    qftis_grenades = [
        {"name": "Concussion Grenade", "source": "QftIS", "type": "EXP", "value": 50000},
        {"name": "Sleep Grenade", "source": "QftIS", "type": "EXP", "value": 50000},
    ]
    nested_parent = {
        "name": "Template Parent",
        "source": "GriffonsSaddlebag2",
        "rarity": "varies",
        "entries": ["Multiple variations of this item exist, as listed below."],
    }
    commodity = {
        "name": "Ruby",
        "source": "XDMG",
        "rarity": "varies",
        "type": "$G|XDMG",
        "value": 50000,
    }
    conflict = {
        "name": "+1 Adamantine Longsword",
        "source": "CallfromtheDeep",
        "rarity": "uncommon",
        "type": "M",
        "value": 10000,
        "genericVariant": {"name": "+1 Adamantine Weapon"},
    }
    items = [*qftis_grenades, nested_parent, commodity, conflict]

    report = build_curation_report(items)

    assert report["total_items"] == 5
    assert report["curated_items_count"] == 3
    assert report["excluded_items_count"] == 2
    assert report["excluded_items"] == [
        {"name": "Concussion Grenade", "source": "QftIS"},
        {"name": "Sleep Grenade", "source": "QftIS"},
    ]
    assert report["nested_generic_phrase_count"] == 1
    assert report["nested_generic_phrase_items"] == [
        {"name": "Template Parent", "source": "GriffonsSaddlebag2"}
    ]
    assert report["commodity_exact_price_candidate_counts_by_type"] == {"$G": 1}
    assert report["magic_material_official_price_conflict_candidate_count"] == 1
    assert report["magic_material_official_price_conflict_examples"] == [
        {
            "name": "+1 Adamantine Longsword",
            "source": "CallfromtheDeep",
            "type": "M",
            "rarity": "uncommon",
            "official_price_gp": 100.0,
        }
    ]
    assert report["magic_material_official_price_conflict_examples_truncated"] is False
    assert report["magic_material_official_price_conflict_source_material_counts"] == {
        "CallfromtheDeep / adamantine": 1
    }


def test_format_curation_report_markdown_includes_required_dry_run_sections():
    report = {
        "total_items": 5,
        "curated_items_count": 3,
        "excluded_items_count": 2,
        "excluded_items": [
            {"name": "Concussion Grenade", "source": "QftIS"},
            {"name": "Sleep Grenade", "source": "QftIS"},
        ],
        "nested_generic_phrase_count": 1,
        "nested_generic_phrase_items": [
            {"name": "Template Parent", "source": "GriffonsSaddlebag2"}
        ],
        "commodity_exact_price_candidate_counts_by_type": {"$G": 1},
        "magic_material_official_price_conflict_candidate_count": 1,
        "magic_material_official_price_conflict_examples": [
            {
                "name": "+1 Adamantine Longsword",
                "source": "CallfromtheDeep",
                "type": "M",
                "rarity": "uncommon",
                "official_price_gp": 100.0,
            }
        ],
        "magic_material_official_price_conflict_examples_truncated": False,
        "magic_material_official_price_conflict_source_material_counts": {
            "CallfromtheDeep / adamantine": 1
        },
    }

    markdown = format_curation_report_markdown(report)

    assert "# 2026-07-12 Item List Curation Dry Run" in markdown
    assert "Total items: 5" in markdown
    assert "Curated items after exclusions: 3" in markdown
    assert "Excluded QftIS grenades: 2" in markdown
    assert "Concussion Grenade" in markdown
    assert "Nested generic/template parents: 1" in markdown
    assert "| $G | 1 |" in markdown
    assert "Magic/material official-price conflict candidates: 1" in markdown
    assert "| CallfromtheDeep / adamantine | 1 |" in markdown


def test_format_curation_report_markdown_notes_truncated_conflict_examples():
    report = build_curation_report(
        [
            {
                "name": f"+1 Adamantine Test Weapon {index}",
                "source": "CallfromtheDeep",
                "rarity": "uncommon",
                "type": "M",
                "value": 10000,
                "genericVariant": {"name": "+1 Adamantine Weapon"},
            }
            for index in range(3)
        ],
        conflict_example_limit=2,
    )

    markdown = format_curation_report_markdown(report)

    assert report["magic_material_official_price_conflict_examples_truncated"] is True
    assert "Showing first 2 of 3 conflict examples." in markdown
