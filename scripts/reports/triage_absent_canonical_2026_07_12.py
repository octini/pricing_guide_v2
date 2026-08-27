#!/usr/bin/env python3
"""Triage canonical rows absent from the curated 2026-07-12 item list."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.list_curation import curate_items, is_excluded_item, load_item_list


DEFAULT_INPUT = Path("2026_07_12_item_list.json")
DEFAULT_CANONICAL = Path("trimmed_5etools_list.json")
DEFAULT_PRICING = Path("output/pricing_guide.csv")
DEFAULT_OUTPUT = Path("reports/absent_canonical_triage_2026_07_12.md")

SPELLJAMMER_SOURCES = frozenset({"AAG", "BAM"})
WTTHC_SUPERSEDED_BY_XDMG = frozenset({"Cloak of Billowing", "Dread Helm"})
WTTHC_COLLABORATION_ONLY = frozenset(
    {
        "Cap of Vanishing",
        "Holly's Handy Haversack",
        "Pipes of Pestilence",
        "Poison Soaked Kukri",
        "Speaking Stones",
        "Spiked Shield",
    }
)
SOURCE_RENAMES = {
    ("VRGR", "Harkon's Bite"): ("RHW", "source-code rename — VRGR → RHW"),
}
RICK_AND_MORTY_COLLABORATION_ROWS = frozenset({("RMBRE", "Concertina")})


Item = dict[str, Any]
PriceLookup = dict[tuple[str, str], str]


def _name(item: Item) -> str:
    return str(item.get("name") or "")


def _source(item: Item) -> str:
    return str(item.get("source") or "")


def _key(item: Item) -> tuple[str, str]:
    return (_name(item).casefold(), _source(item).casefold())


def _source_name_key(source: str, name: str) -> tuple[str, str]:
    return (name.casefold(), source.casefold())


def _label(item: Item) -> str:
    return f"{_name(item)} ({_source(item)})"


def _row_source_name(item: Item) -> tuple[str, str]:
    return (_source(item), _name(item))


def load_price_lookup(path: Path) -> PriceLookup:
    if not path.exists():
        return {}

    exact: PriceLookup = {}
    by_name: dict[str, list[str]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            name = str(row.get("Name") or "")
            source = str(row.get("Source") or "")
            price = str(row.get("Price Formatted") or row.get("Price (gp)") or "")
            if not name or not price:
                continue
            exact[(name.casefold(), source.casefold())] = price
            by_name.setdefault(name.casefold(), []).append(price)

    for name_key, prices in by_name.items():
        unique_prices = sorted(set(prices))
        if len(unique_prices) == 1:
            exact[(name_key, "")] = unique_prices[0]
    return exact


def _price_for(item: Item, price_lookup: PriceLookup) -> str:
    exact = price_lookup.get(_key(item))
    if exact:
        return exact
    by_name = price_lookup.get((_name(item).casefold(), ""))
    if by_name:
        return f"{by_name} (name-only)"
    return "—"


def _items_by_name(items: list[Item]) -> dict[str, list[Item]]:
    by_name: dict[str, list[Item]] = {}
    for item in items:
        by_name.setdefault(_name(item).casefold(), []).append(item)
    return by_name


def _present_as(name: str, items_by_name: dict[str, list[Item]]) -> str:
    matches = items_by_name.get(name.casefold(), [])
    if not matches:
        return "—"
    return ", ".join(_label(item) for item in sorted(matches, key=lambda item: (_source(item), _name(item))))


def classify_absent_row(item: Item, raw_items_by_name: dict[str, list[Item]]) -> tuple[str, str, str]:
    source, name = _row_source_name(item)
    present_as = _present_as(name, raw_items_by_name)

    if is_excluded_item(item):
        return "hard exclusion — QftIS grenade", "Approved exact hard exclusion from curation policy.", present_as
    if source in SPELLJAMMER_SOURCES:
        return (
            "intentional scope exclusion — Spelljammer/space",
            "AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate.",
            present_as,
        )
    if source == "WttHC" and name in WTTHC_SUPERSEDED_BY_XDMG:
        return (
            "superseded collaboration row — XDMG replacement",
            "Welcome to the Hellfire Club (Stranger Things collaboration) row is superseded by the 2024 XDMG entry.",
            present_as,
        )
    if source == "WttHC" and name in WTTHC_COLLABORATION_ONLY:
        return (
            "collaboration-only row — user-approved drop",
            "Welcome to the Hellfire Club (Stranger Things collaboration) row is absent from the 2026 export and not a known-good/core carry-forward row; user approved dropping it.",
            present_as,
        )
    if (source, name) in RICK_AND_MORTY_COLLABORATION_ROWS:
        return (
            "collaboration-only row — user-approved drop",
            "The Lost Dungeon of Rickedness: Big Rick Energy (Rick and Morty collaboration) row is absent from the 2026 export and not a known-good/core carry-forward row; user approved dropping it.",
            present_as,
        )
    if (source, name) in SOURCE_RENAMES:
        new_source, classification = SOURCE_RENAMES[(source, name)]
        expected = [item for item in raw_items_by_name.get(name.casefold(), []) if _source(item) == new_source]
        expected_present = ", ".join(_label(item) for item in expected) or present_as
        return classification, "Same item is present under the updated source code.", expected_present
    if name == "Crystal" and present_as != "—":
        return (
            "source-list migration — Crystal present by source-specific rows",
            "Crystal rows are present and should remain keep-separate by source.",
            present_as,
        )

    return "needs manual review — unclassified", "No deterministic classification rule matched.", present_as


def analyze_absent_rows(
    canonical_items: list[Item], raw_items: list[Item], *, price_lookup: PriceLookup
) -> dict[str, Any]:
    curated_items = curate_items(raw_items).kept_items
    raw_keys = {_key(item) for item in raw_items}
    curated_keys = {_key(item) for item in curated_items}
    raw_items_by_name = _items_by_name(raw_items)
    curated_items_by_name = _items_by_name(curated_items)

    raw_absent = [item for item in canonical_items if _key(item) not in raw_keys]
    curated_absent = [item for item in canonical_items if _key(item) not in curated_keys]

    rows = []
    for item in sorted(curated_absent, key=lambda row: (_source(row), _name(row))):
        classification, rationale, present_as = classify_absent_row(item, raw_items_by_name)
        rows.append(
            {
                "name": _name(item),
                "source": _source(item),
                "type": str(item.get("type") or item.get("item_type_code") or ""),
                "rarity": str(item.get("rarity") or ""),
                "raw_present": _key(item) in raw_keys,
                "curated_present": _key(item) in curated_keys,
                "present_by_name_in_raw": present_as,
                "present_by_name_in_curated": _present_as(_name(item), curated_items_by_name),
                "classification": classification,
                "rationale": rationale,
                "price": _price_for(item, price_lookup),
            }
        )

    classification_counts = Counter(row["classification"] for row in rows)
    unclassified_count = sum(
        1 for row in rows if str(row["classification"]).startswith("needs manual review")
    )

    return {
        "canonical_count": len(canonical_items),
        "raw_count": len(raw_items),
        "curated_count": len(curated_items),
        "raw_absent_count": len(raw_absent),
        "curated_absent_count": len(curated_absent),
        "hard_exclusion_absent_count": len(curated_absent) - len(raw_absent),
        "classification_counts": dict(sorted(classification_counts.items())),
        "unclassified_count": unclassified_count,
        "rows": rows,
        "crystal_raw_rows": _present_as("Crystal", raw_items_by_name),
        "crystal_curated_rows": _present_as("Crystal", curated_items_by_name),
    }


def _md(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def build_report(
    canonical_items: list[Item],
    raw_items: list[Item],
    *,
    input_path: Path,
    canonical_path: Path,
    price_lookup: PriceLookup,
) -> str:
    analysis = analyze_absent_rows(canonical_items, raw_items, price_lookup=price_lookup)

    recommendation = (
        "Recommendation: approve all classified omissions; no manual carry-forward required."
        if analysis["unclassified_count"] == 0
        else "Recommendation: resolve unclassified rows before canonical migration."
    )

    lines = [
        "# 2026-07-12 Absent Canonical Row Triage",
        "",
        f"Raw input: `{input_path.as_posix()}` (left untracked).",
        f"Canonical reference: `{canonical_path.as_posix()}`.",
        "No canonical migration, full pricing run, or processed/published output generation was performed.",
        "",
        "## Summary",
        "",
        f"- Canonical rows: {analysis['canonical_count']}",
        f"- Raw 2026 rows: {analysis['raw_count']}",
        f"- Curated 2026 rows after hard exclusions: {analysis['curated_count']}",
        f"- Canonical rows absent from raw 2026 by exact `(name, source)`: {analysis['raw_absent_count']}",
        f"- Canonical rows absent from curated 2026 by exact `(name, source)`: {analysis['curated_absent_count']}",
        f"- Additional curated-absent rows caused by hard exclusions: {analysis['hard_exclusion_absent_count']}",
        f"- Unclassified rows: {analysis['unclassified_count']}",
        f"- {recommendation}",
        "",
        "## Classification counts",
        "",
        "| Classification | Rows |",
        "|---|---:|",
    ]
    for classification, count in analysis["classification_counts"].items():
        lines.append(f"| {_md(classification)} | {count} |")
    if not analysis["classification_counts"]:
        lines.append("| — | 0 |")

    lines.extend(
        [
            "",
            "## Sensitive presence checks",
            "",
            f"- Crystal raw rows: {analysis['crystal_raw_rows']}; classification: keep-separate.",
            f"- Crystal curated rows: {analysis['crystal_curated_rows']}; classification: keep-separate.",
            "- Harkon's Bite source-code rename is classified explicitly as VRGR → RHW when present.",
            "",
            "## Full absent row triage",
            "",
            "| # | Name | Source | Rarity | Type | Raw exact present | Curated exact present | Present by name in raw | Price | Classification | Rationale |",
            "|---:|---|---|---|---|---|---|---|---:|---|---|",
        ]
    )
    for index, row in enumerate(analysis["rows"], start=1):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(index),
                    _md(row["name"]),
                    _md(row["source"]),
                    _md(row["rarity"]),
                    _md(row["type"]),
                    "yes" if row["raw_present"] else "no",
                    "yes" if row["curated_present"] else "no",
                    _md(row["present_by_name_in_raw"]),
                    _md(row["price"]),
                    _md(row["classification"]),
                    _md(row["rationale"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Migration recommendation",
            "",
            recommendation,
            "Proceed only after this report is reviewed; do not manually carry forward these rows unless the recommendation changes.",
            "",
        ]
    )
    return "\n".join(lines)


def run(*, input_path: str | Path, canonical_path: str | Path, output_path: str | Path) -> int:
    input_path = Path(input_path)
    canonical_path = Path(canonical_path)
    output_path = Path(output_path)

    if not input_path.exists():
        print(f"Skipping absent-canonical triage: raw input file not found at {input_path}")
        return 0

    canonical_items = load_item_list(canonical_path)
    raw_items = load_item_list(input_path)
    price_lookup = load_price_lookup(DEFAULT_PRICING)
    report = build_report(
        canonical_items,
        raw_items,
        input_path=input_path,
        canonical_path=canonical_path,
        price_lookup=price_lookup,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    analysis = analyze_absent_rows(canonical_items, raw_items, price_lookup=price_lookup)
    print(f"Wrote absent-canonical triage report to {output_path}")
    print(f"Raw absent rows: {analysis['raw_absent_count']}")
    print(f"Curated absent rows: {analysis['curated_absent_count']}")
    print(f"Unclassified rows: {analysis['unclassified_count']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--canonical", type=Path, default=DEFAULT_CANONICAL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    return run(input_path=args.input, canonical_path=args.canonical, output_path=args.output)


if __name__ == "__main__":
    raise SystemExit(main())
