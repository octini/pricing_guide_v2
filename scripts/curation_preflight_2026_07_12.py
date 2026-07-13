#!/usr/bin/env python3
"""Generate a broader curation preflight report for the 2026-07-12 item list."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.list_curation import base_type_code, curate_items, load_item_list


DEFAULT_INPUT = Path("2026_07_12_item_list.json")
DEFAULT_CANONICAL = Path("trimmed_5etools_list.json")
DEFAULT_OUTPUT = Path("reports/curation_preflight_2026_07_12.md")
EXAMPLE_LIMIT = 8


Item = dict[str, Any]


def _item_name(item: Item) -> str:
    return str(item.get("name") or "<unnamed>")


def _source(item: Item) -> str:
    return str(item.get("source") or "unknown")


def _item_label(item: Item) -> str:
    return f"{_item_name(item)} ({_source(item)})"


def _item_key(item: Item) -> tuple[str, str]:
    return (_item_name(item).casefold(), _source(item).casefold())


def _name_key(item: Item) -> str:
    return _item_name(item).casefold()


def _type_code(item: Item) -> str:
    return base_type_code(item)


def _format_count_table(rows: list[tuple[str, int, int, int]], *, limit: int = 15) -> list[str]:
    lines = ["| Source | 2026 curated | Current canonical | Delta |", "|---|---:|---:|---:|"]
    for source, new_count, old_count, delta in rows[:limit]:
        lines.append(f"| {source} | {new_count} | {old_count} | {delta:+d} |")
    if not rows:
        lines.append("| — | 0 | 0 | 0 |")
    return lines


def _format_examples(items: list[Item], *, limit: int = EXAMPLE_LIMIT) -> list[str]:
    if not items:
        return ["- None found."]
    return [f"- {_item_label(item)}" for item in items[:limit]]


def _source_counts(items: list[Item]) -> Counter[str]:
    return Counter(_source(item) for item in items)


def _generic_variant_name(item: Item) -> str:
    generic_variant = item.get("genericVariant")
    if isinstance(generic_variant, dict):
        return str(generic_variant.get("name") or "")
    return str(generic_variant or "")


def _is_specific_variant(item: Item) -> bool:
    return bool(_generic_variant_name(item))


def _is_vehicleish(item: Item) -> bool:
    name = _item_name(item).casefold()
    type_code = _type_code(item)
    return (
        type_code in {"SHP", "VEH", "AIR", "SPC"}
        or any(key in item for key in ("vehSpeed", "vehAc", "vehHp", "crew", "capCargo"))
        or any(term in name for term in ("airship", "skyship", "ship", "boat", "caravel", "bireme"))
    )


def _is_ammunition(item: Item) -> bool:
    name = _item_name(item).casefold()
    return _type_code(item) == "A" or "arrow" in name or "bolt" in name or "ammunition" in name


def _is_firearm(item: Item) -> bool:
    name = _item_name(item).casefold()
    if _is_ammunition(item):
        return False
    property_text = " ".join(str(value).casefold() for value in item.get("property", []) or [])
    if "firearm" in property_text:
        return True
    return any(
        term in name
        for term in (
            "pistol",
            "musket",
            "rifle",
            "firearm",
            "blunderbuss",
            "shotgun",
            "revolver",
            "pepperbox",
            "tommybow",
        )
    )


def _scope_review_items(items: list[Item]) -> dict[str, list[Item]]:
    def name_has(*terms: str) -> list[Item]:
        return [item for item in items if any(term in _item_name(item).casefold() for term in terms)]

    explosives = name_has("grenade", "bomb", "explosive", "dynamite", "blasting powder", "firework")
    airships = [item for item in items if any(term in _item_name(item).casefold() for term in ("airship", "skyship"))]
    firearms = [item for item in items if _is_firearm(item)]
    return {
        "Fantasy explosives/alchemical ordnance (keep pending final human confirmation)": explosives,
        "Airships/skyships/fantasy vehicles (currently in scope)": airships,
        "Source-specific firearms/Renaissance-tech review": firearms,
    }


def _duplicate_groups(items: list[Item]) -> list[tuple[str, list[Item]]]:
    grouped: dict[str, list[Item]] = defaultdict(list)
    for item in items:
        grouped[_item_name(item)].append(item)
    return sorted(
        ((name, group) for name, group in grouped.items() if len(group) > 1),
        key=lambda item: (-len(item[1]), item[0].casefold()),
    )


def _classify_duplicate(name: str, group: list[Item]) -> str:
    name_key = name.casefold()
    sources = {_source(item).casefold() for item in group}
    if name_key in {"crystal", "zeal"}:
        return "keep-separate — sensitive gem/ingredient/source collision"
    if "dungeonsofdrakkenheim" in sources or "drakkenheim" in " ".join(sorted(sources)):
        return "keep-separate — Drakkenheim/source-specific collision"
    if all(_is_vehicleish(item) for item in group):
        return "likely collapsible — vehicle/source variants"
    if all(_is_ammunition(item) for item in group):
        return "likely collapsible — ammunition variants"
    if any(_is_firearm(item) for item in group):
        return "review/keep-separate — source-specific firearms"
    return "review — same-name cross-source collision"


def _format_duplicate_examples(groups: list[tuple[str, list[Item]]], *, limit: int = EXAMPLE_LIMIT) -> list[str]:
    if not groups:
        return ["- None found."]
    lines = []
    for name, group in groups[:limit]:
        sources = ", ".join(sorted({_source(item) for item in group}))
        lines.append(f"- {name}: {len(group)} rows; {sources}; {_classify_duplicate(name, group)}")
    return lines


def _variant_family_counts(items: list[Item]) -> Counter[str]:
    return Counter(_generic_variant_name(item) for item in items if _is_specific_variant(item))


def _format_variant_families(counts: Counter[str], *, limit: int = 15) -> list[str]:
    lines = ["| Generic parent / family | Specific variants |", "|---|---:|"]
    rows = sorted(counts.items(), key=lambda item: (-item[1], item[0].casefold()))[:limit]
    if not rows:
        lines.append("| — | 0 |")
    for family, count in rows:
        lines.append(f"| {family} | {count} |")
    return lines


def _name_presence(items: list[Item], name: str) -> list[Item]:
    key = name.casefold()
    return [item for item in items if _name_key(item) == key]


def _source_presence(items: list[Item], source: str) -> bool:
    source_key = source.casefold()
    return any(_source(item).casefold() == source_key for item in items)


def build_report(raw_items: list[Item], canonical_items: list[Item], *, input_path: Path, canonical_path: Path) -> str:
    curated = curate_items(raw_items)
    kept_items = curated.kept_items
    curation = curated.report

    canonical_sources = _source_counts(canonical_items)
    curated_sources = _source_counts(kept_items)
    all_sources = sorted(set(canonical_sources) | set(curated_sources))
    source_delta_rows = [
        (source, curated_sources[source], canonical_sources[source], curated_sources[source] - canonical_sources[source])
        for source in all_sources
    ]
    top_expansions = sorted(source_delta_rows, key=lambda row: (-row[3], row[0]))
    new_only_sources = sorted(source for source in curated_sources if source not in canonical_sources)

    duplicate_groups = _duplicate_groups(kept_items)
    duplicate_class_counts = Counter(_classify_duplicate(name, group) for name, group in duplicate_groups)
    variant_families = _variant_family_counts(kept_items)
    specific_variant_count = sum(variant_families.values())
    nested_generic_count = int(curation.get("nested_generic_phrase_count", 0))
    raw_keys = {_item_key(item) for item in kept_items}
    canonical_keys = {_item_key(item) for item in canonical_items}
    new_item_count = len(raw_keys - canonical_keys)
    removed_item_count = len(canonical_keys - raw_keys)

    crystal_rows = _name_presence(kept_items, "Crystal")
    zeal_rows = _name_presence(kept_items, "Zeal")
    scope_review = _scope_review_items(kept_items)

    lines = [
        "# 2026-07-12 Curation Preflight",
        "",
        f"Raw file: `{input_path.as_posix()}` (raw 2026 files remain untracked; no canonical replacement or pricing pipeline run).",
        f"Canonical reference: `{canonical_path.as_posix()}`.",
        f"Raw 2026 items: {len(raw_items)}",
        f"Current canonical items: {len(canonical_items)}",
        f"Curated items after hard exclusions: {len(kept_items)}",
        f"Hard exclusions applied: {len(curated.excluded_items)}",
        f"New exact `(name, source)` rows after curation: {new_item_count}",
        f"Canonical exact `(name, source)` rows absent from curated 2026 list: {removed_item_count}",
        "",
        "## Source count delta summary",
        "",
        f"Curated 2026 sources: {len(curated_sources)}; canonical sources: {len(canonical_sources)}; new-only sources: {len(new_only_sources)}.",
        f"Spelljammer scope check: AAG present={_source_presence(kept_items, 'AAG')}; BAM present={_source_presence(kept_items, 'BAM')} (expected absent unless explicitly approved).",
        "",
        "### Top source expansions",
        *_format_count_table([row for row in top_expansions if row[3] > 0]),
        "",
        "### New-only sources (first 25)",
        *(f"- {source} ({curated_sources[source]})" for source in new_only_sources[:25]),
        *( ["- None."] if not new_only_sources else [] ),
        "",
        "## Hard exclusions",
        "",
        "Exact QftIS grenade exclusions applied by `src.list_curation.curate_items()`:",
        *(
            f"- {item['source']} — {item['name']}"
            for item in curation.get("excluded_items", [])
        ),
        *( ["- None."] if not curation.get("excluded_items") else [] ),
        "",
        "## Potential scope review items",
        "",
    ]

    for label, items in scope_review.items():
        lines.extend([f"### {label}", f"Count: {len(items)}", *_format_examples(items), ""])

    lines.extend(
        [
            "## Duplicate/name collision summary",
            "",
            f"Same-name groups after hard exclusions: {len(duplicate_groups)}",
            "",
            "### Collision classification counts",
            "| Classification | Groups |",
            "|---|---:|",
        ]
    )
    for label, count in sorted(duplicate_class_counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| {label} | {count} |")
    if not duplicate_class_counts:
        lines.append("| — | 0 |")

    lines.extend(
        [
            "",
            "### Collision examples",
            *_format_duplicate_examples(duplicate_groups),
            "",
            "### Sensitive collision checks",
            f"- Crystal rows present: {len(crystal_rows)} — {', '.join(_item_label(item) for item in crystal_rows) or 'none'}; classification: keep-separate.",
            f"- Zeal rows present: {len(zeal_rows)} — {', '.join(_item_label(item) for item in zeal_rows) or 'none'}; classification: keep-separate.",
            "- Obojima ingredient vs DMG/PHB gem-style name collisions should remain source-specific unless manually collapsed.",
            "- Source-specific firearms should remain source-specific pending source/tech review.",
            "",
            "## Variant family and UI grouping candidates",
            "",
            f"Specific variants with `genericVariant`: {specific_variant_count}",
            f"Nested generic/template phrase parents: {nested_generic_count}",
            "",
            "### Top generic variant families",
            *_format_variant_families(variant_families),
            "",
            "### UI grouping candidates",
            "- Large generic variant families above should be grouped/collapsed in UI review rather than manually deleted.",
            "- Same-name ammunition and vehicle/source variants are likely collapsible display groups after source review.",
            "- Keep source-specific named collisions such as Crystal/Zeal separate until a human approves any merge.",
            "",
            "## Readiness matrix",
            "",
            "| Bucket | Status | Examples / next action |",
            "|---|---|---|",
            f"| Safe to migrate | Hard exclusions only | {len(kept_items)} curated rows after excluding QftIS Concussion/Sleep Grenade; raw 2026 files remain untracked. |",
            "| Needs user decision | Scope/curation | Fantasy explosives/alchemical ordnance; new-only source scope; source-specific firearm handling. |",
            "| Needs extractor/pricing work | Criteria/pricing follow-up | Variant family/UI grouping, duplicate collision review, party-benefit/conditional-save follow-ups already tracked separately. |",
            "| Deferred | Out of scope for this preflight | Full pricing run, canonical replacement, data/processed or published output generation. |",
            "",
            "## Pipeline safety",
            "",
            "- Did not edit `trimmed_5etools_list.*`.",
            "- Did not run full pricing or generate `data/processed`/published outputs.",
            "- Raw `2026_07_12_item_list.json/.md` remain untracked under Option A.",
            "",
        ]
    )
    return "\n".join(lines)


def run(*, input_path: str | Path, canonical_path: str | Path, output_path: str | Path) -> int:
    input_path = Path(input_path)
    canonical_path = Path(canonical_path)
    output_path = Path(output_path)

    if not input_path.exists():
        print(f"Skipping curation preflight: raw input file not found at {input_path}")
        return 0

    raw_items = load_item_list(input_path)
    canonical_items = load_item_list(canonical_path) if canonical_path.exists() else []
    report = build_report(raw_items, canonical_items, input_path=input_path, canonical_path=canonical_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    curated_count = len(curate_items(raw_items).kept_items)
    print(f"Wrote curation preflight report to {output_path}")
    print(f"Raw 2026 items: {len(raw_items)}")
    print(f"Curated items after hard exclusions: {curated_count}")
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
