"""Helpers for bounded source-list curation dry runs and exact commodity policy."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable

from .utils import parse_value_cp


NESTED_GENERIC_VARIATION_PHRASE = "Multiple variations of this item exist"
EXCLUDED_SOURCE_NAME_PAIRS = frozenset(
    {
        ("QftIS", "Concussion Grenade"),
        ("QftIS", "Sleep Grenade"),
    }
)
PURE_COMMODITY_TYPE_CODES = frozenset({"$A", "$G", "$C", "TG", "TB"})
MATERIAL_KEYWORDS = ("adamantine", "mithral", "silvered", "byeshk")
NON_MAGIC_RARITIES = frozenset({"", "none", "mundane", "unknown"})


@dataclass(frozen=True)
class CuratedItems:
    """Result of applying bounded source-list curation policy."""

    kept_items: list[dict[str, Any]]
    excluded_items: list[dict[str, Any]]
    report: dict[str, Any]


def base_type_code(item_or_row: dict[str, Any] | Any) -> str:
    """Return the 5e.tools type code without any source suffix."""
    if hasattr(item_or_row, "get"):
        raw_type = item_or_row.get("type") or item_or_row.get("item_type_code") or ""
    else:
        raw_type = item_or_row or ""
    return str(raw_type).split("|")[0].strip()


def official_price_gp(item_or_row: dict[str, Any]) -> float | None:
    """Return a positive official price in gp from raw JSON or processed rows."""
    raw_official_price = item_or_row.get("official_price_gp")
    if raw_official_price not in (None, ""):
        try:
            official = float(raw_official_price)
        except (TypeError, ValueError):
            official = None
        if official is not None and official == official and official > 0:
            return official

    return parse_value_cp(item_or_row.get("value"))


def is_excluded_item(item: dict[str, Any]) -> bool:
    """Return True for exact source/name exclusions from the approved policy."""
    return (str(item.get("source", "")), str(item.get("name", ""))) in EXCLUDED_SOURCE_NAME_PAIRS


def is_nested_generic_parent(item: dict[str, Any]) -> bool:
    """Detect parent/template rows signaled only inside entries prose."""
    entries_text = json.dumps(item.get("entries", ""), ensure_ascii=False)
    return NESTED_GENERIC_VARIATION_PHRASE.lower() in entries_text.lower()


def is_commodity_exact_price_candidate(item_or_row: dict[str, Any]) -> bool:
    """Return True when an item is pure wealth/commodity with an exact value.

    These rows are treasure/art/coin/trade-good value records, not magic item
    variants. Magic/material rows can have raw values too, but their type codes
    are equipment/magic types and must continue through formula/anchor behavior.
    """
    return (
        base_type_code(item_or_row) in PURE_COMMODITY_TYPE_CODES
        and official_price_gp(item_or_row) is not None
    )


def _generic_variant_text(item: dict[str, Any]) -> str:
    generic_variant = item.get("genericVariant")
    if isinstance(generic_variant, dict):
        return str(generic_variant.get("name", ""))
    return str(generic_variant or "")


def _has_material_keyword(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in MATERIAL_KEYWORDS)


def _material_label(item: dict[str, Any]) -> str:
    combined_text = f"{item.get('name', '')} {_generic_variant_text(item)}".lower()
    for keyword in MATERIAL_KEYWORDS:
        if keyword in combined_text:
            return keyword
    return "unknown material"


def _has_magic_bonus_marker(text: str, item: dict[str, Any]) -> bool:
    if "+1" in text or "+2" in text or "+3" in text:
        return True
    return any(
        item.get(field) not in (None, "", 0)
        for field in ("bonusWeapon", "bonusWeaponAttack", "bonusWeaponDamage", "bonusAc")
    )


def is_magic_material_official_price_conflict_candidate(item: dict[str, Any]) -> bool:
    """Flag raw official values on magic/material variants for dry-run review."""
    if official_price_gp(item) is None or is_commodity_exact_price_candidate(item):
        return False

    name = str(item.get("name", ""))
    variant_text = _generic_variant_text(item)
    combined_text = f"{name} {variant_text}"
    rarity = str(item.get("rarity", "")).lower().replace(" ", "_")

    has_variant_link = bool(item.get("genericVariant"))
    has_material = _has_material_keyword(combined_text)
    has_bonus = _has_magic_bonus_marker(combined_text, item)
    has_magic_rarity = rarity not in NON_MAGIC_RARITIES

    return has_variant_link and has_material and (has_bonus or has_magic_rarity)


def _name_source(item: dict[str, Any]) -> dict[str, str]:
    return {"name": str(item.get("name", "")), "source": str(item.get("source", ""))}


def _split_curated_items(items: Iterable[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    kept_items = []
    excluded_items = []
    for item in items:
        if is_excluded_item(item):
            excluded_items.append(item)
        else:
            kept_items.append(item)
    return kept_items, excluded_items


def _build_curation_report(
    *,
    total_items: int,
    kept_items: list[dict[str, Any]],
    excluded_items: list[dict[str, Any]],
    conflict_example_limit: int,
) -> dict[str, Any]:
    excluded = [_name_source(item) for item in excluded_items]
    nested_generic = [_name_source(item) for item in kept_items if is_nested_generic_parent(item)]

    commodity_counts = Counter(
        base_type_code(item) for item in kept_items if is_commodity_exact_price_candidate(item)
    )

    conflict_candidates = [
        item for item in kept_items if is_magic_material_official_price_conflict_candidate(item)
    ]
    source_material_counts = Counter(
        f"{item.get('source', '')} / {_material_label(item)}" for item in conflict_candidates
    )
    conflict_examples = []
    for item in conflict_candidates[:conflict_example_limit]:
        conflict_examples.append(
            {
                "name": str(item.get("name", "")),
                "source": str(item.get("source", "")),
                "type": base_type_code(item),
                "rarity": str(item.get("rarity", "")),
                "official_price_gp": official_price_gp(item),
            }
        )

    return {
        "total_items": total_items,
        "curated_items_count": len(kept_items),
        "excluded_items_count": len(excluded),
        "excluded_items": excluded,
        "nested_generic_phrase_count": len(nested_generic),
        "nested_generic_phrase_items": nested_generic,
        "commodity_exact_price_candidate_counts_by_type": dict(sorted(commodity_counts.items())),
        "magic_material_official_price_conflict_candidate_count": len(conflict_candidates),
        "magic_material_official_price_conflict_examples": conflict_examples,
        "magic_material_official_price_conflict_examples_truncated": len(conflict_candidates)
        > len(conflict_examples),
        "magic_material_official_price_conflict_source_material_counts": dict(
            sorted(source_material_counts.items())
        ),
    }


def curate_items(items: Iterable[dict[str, Any]], conflict_example_limit: int = 25) -> CuratedItems:
    """Apply bounded 2026-list curation without mutating or replacing inputs."""
    item_list = list(items)
    kept_items, excluded_items = _split_curated_items(item_list)
    report = _build_curation_report(
        total_items=len(item_list),
        kept_items=kept_items,
        excluded_items=excluded_items,
        conflict_example_limit=conflict_example_limit,
    )
    return CuratedItems(kept_items=kept_items, excluded_items=excluded_items, report=report)


def build_curation_report(items: Iterable[dict[str, Any]], conflict_example_limit: int = 25) -> dict[str, Any]:
    """Build deterministic dry-run counts for the approved 2026-07-12 policy."""
    return curate_items(items, conflict_example_limit=conflict_example_limit).report


def load_item_list(path: Path) -> list[dict[str, Any]]:
    """Load a 5e.tools item list from list or dict-wrapped JSON."""
    with path.open(encoding="utf-8") as f:
        raw = json.load(f)

    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for key in ("item", "items"):
            value = raw.get(key)
            if isinstance(value, list):
                return value
        for value in raw.values():
            if isinstance(value, list):
                return value

    raise ValueError(f"Unexpected item-list JSON shape in {path}")


def format_curation_report_markdown(report: dict[str, Any]) -> str:
    """Render a human-readable dry-run report."""
    lines = [
        "# 2026-07-12 Item List Curation Dry Run",
        "",
        f"Total items: {report['total_items']}",
        f"Curated items after exclusions: {report['curated_items_count']}",
        "",
        f"Excluded QftIS grenades: {report['excluded_items_count']}",
    ]

    for item in report["excluded_items"]:
        lines.append(f"- {item['source']} — {item['name']}")

    lines.extend(
        [
            "",
            f"Nested generic/template parents: {report['nested_generic_phrase_count']}",
        ]
    )
    for item in report["nested_generic_phrase_items"]:
        lines.append(f"- {item['source']} — {item['name']}")

    lines.extend(
        [
            "",
            "## Commodity exact-price candidates by type",
            "",
            "| Type | Count |",
            "| --- | ---: |",
        ]
    )
    counts = report["commodity_exact_price_candidate_counts_by_type"]
    if counts:
        for item_type, count in counts.items():
            lines.append(f"| {item_type} | {count} |")
    else:
        lines.append("| — | 0 |")

    lines.extend(
        [
            "",
            (
                "Magic/material official-price conflict candidates: "
                f"{report['magic_material_official_price_conflict_candidate_count']}"
            ),
        ]
    )
    if report.get("magic_material_official_price_conflict_examples_truncated"):
        lines.append(
            "Showing first "
            f"{len(report['magic_material_official_price_conflict_examples'])} of "
            f"{report['magic_material_official_price_conflict_candidate_count']} conflict examples."
        )
    for item in report["magic_material_official_price_conflict_examples"]:
        lines.append(
            f"- {item['source']} — {item['name']} "
            f"({item['type']}, {item['rarity']}, official {item['official_price_gp']} gp)"
        )

    lines.extend(
        [
            "",
            "## Magic/material conflict candidates by source/material",
            "",
            "| Source / material | Count |",
            "| --- | ---: |",
        ]
    )
    source_material_counts = report["magic_material_official_price_conflict_source_material_counts"]
    if source_material_counts:
        for source_material, count in source_material_counts.items():
            lines.append(f"| {source_material} | {count} |")
    else:
        lines.append("| — | 0 |")

    return "\n".join(lines) + "\n"


def write_curation_report(items: Iterable[dict[str, Any]], output_path: Path) -> dict[str, Any]:
    """Write the markdown dry-run report and return the report dictionary."""
    report = curate_items(items).report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(format_curation_report_markdown(report), encoding="utf-8")
    return report
