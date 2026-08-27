#!/usr/bin/env python3
"""Generate a current-canonical extra_damage_avg impact report for the regex broadening."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys as _sys
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.criteria_extractor import extract_entries_criteria
from src.pricing_engine import extra_damage_pricing_multiplier
from src.prose_loader import load_prose_descriptions


DEFAULT_MASTER = Path("data/processed/items_master.csv")
DEFAULT_PROSE = Path("items-sublist.md")
DEFAULT_PRICING = Path("output/pricing_guide.csv")
DEFAULT_OUTPUT = Path("reports/extra_damage_impact_2026_07_12.md")
DIRECT_GP_PER_AVG_POINT = 3000

csv.field_size_limit(_sys.maxsize)

Item = dict[str, Any]
PriceLookup = dict[str, dict[str, str]]


def _rarity_extra_damage_coefficient(rarity: str) -> int:
    return 3000 if str(rarity).lower() in {"legendary", "artifact"} else 1500


def old_extra_damage_criteria(item: Item, prose_text: str = "") -> dict[str, Any]:
    """Reproduce pre-broadened extra damage extraction for comparison."""
    criteria = {"extra_damage_avg": 0.0, "extra_damage_dice": None}
    combined_text = str(item.get("entries", [])) + " " + prose_text
    item_name = _name(item)
    damage_matches = re.findall(r"(?:additional|extra) {@damage ([^}]+)}", combined_text)
    if damage_matches:
        total = sum(_avg_dice(damage) for damage in damage_matches)
        criteria["extra_damage_avg"] = total
        criteria["extra_damage_dice"] = damage_matches[0] if len(damage_matches) == 1 else f"{len(damage_matches)} sources"
        return criteria

    plain_matches = re.findall(
        r"(?:additional|extra)\s+(\d+d\d+)\s+(\w+)\s+damage",
        combined_text,
        re.IGNORECASE,
    )
    if plain_matches:
        criteria["extra_damage_avg"] = sum(_avg_dice(match[0]) for match in plain_matches)
        criteria["extra_damage_dice"] = plain_matches[0][0]
    if "Dragon's Wrath" in item_name or "Dragon’s Wrath" in item_name:
        if "Slumbering" in item_name:
            criteria["extra_damage_avg"] = 0.175
            criteria["extra_damage_dice"] = "1d6 (crit only)"
        elif "Stirring" in item_name:
            criteria["extra_damage_avg"] = 3.5
            criteria["extra_damage_dice"] = "1d6"
        elif "Wakened" in item_name:
            criteria["extra_damage_avg"] = 7.0
            criteria["extra_damage_dice"] = "2d6"
        elif "Ascendant" in item_name:
            criteria["extra_damage_avg"] = 10.5
            criteria["extra_damage_dice"] = "3d6"
    return criteria


def _avg_dice(dice_str: str) -> float:
    dice_str = dice_str.replace(" ", "")
    if dice_str.isdigit():
        return float(dice_str)
    total = 0.0
    for match in re.finditer(r"(\d+)d(\d+)", dice_str):
        count, sides = int(match.group(1)), int(match.group(2))
        total += count * (sides + 1) / 2
    for match in re.finditer(r"[+](\d+)(?!d)", dice_str):
        total += int(match.group(1))
    return total


def load_master_items(master_path: Path) -> list[Item]:
    with master_path.open(newline="", encoding="utf-8") as handle:
        items = []
        for row in csv.DictReader(handle):
            try:
                raw_item = json.loads(row.get("raw_json") or "{}")
            except json.JSONDecodeError:
                raw_item = {}
            raw_item.setdefault("name", row.get("name") or "")
            raw_item.setdefault("source", row.get("source") or "")
            raw_item.setdefault("rarity", row.get("rarity") or "")
            raw_item.setdefault("type", row.get("type") or "")
            items.append(raw_item)
    return items


def load_price_lookup(pricing_path: Path) -> PriceLookup:
    if not pricing_path.exists():
        return {}
    lookup: PriceLookup = {}
    with pricing_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            name = str(row.get("Name") or "").casefold()
            if name:
                lookup[name] = row
    return lookup


def _current_price(name: str, price_lookup: PriceLookup) -> str:
    row = price_lookup.get(name.casefold())
    if not row:
        return "—"
    return str(row.get("Price Formatted") or row.get("Price (gp)") or "—")


def _known_good_anchor(name: str, price_lookup: PriceLookup) -> bool:
    row = price_lookup.get(name.casefold())
    return bool(row and str(row.get("Has Reference") or "").lower() == "true")


def _evidence(prose_text: str) -> str:
    clean = re.sub(r"\s+", " ", prose_text).strip()
    match = re.search(
        r"[^.]{0,120}\b(?:extra|additional)\s+\d+d\d+(?:\s+[a-z]+(?:\s+or\s+[a-z]+)?)?\s+damage\b[^.]{0,120}",
        clean,
        re.IGNORECASE,
    )
    if match:
        return match.group(0).strip()
    return clean[:240]


def _rarity(item: Item) -> str:
    return str(item.get("rarity") or "")


def _item_type(item: Item) -> str:
    return str(item.get("type") or "")


def _name(item: Item) -> str:
    return str(item.get("name") or "")


def _source(item: Item) -> str:
    return str(item.get("source") or "")


def analyze_items(items: list[Item], prose_map: dict[str, str], price_lookup: PriceLookup) -> dict[str, Any]:
    rows = []
    old_total = 0.0
    new_total = 0.0
    old_weighted_total = 0.0
    new_weighted_total = 0.0
    for item in items:
        name = _name(item)
        prose_text = prose_map.get(name.casefold(), "")
        old = old_extra_damage_criteria(item, prose_text)
        new = extract_entries_criteria(dict(item), prose_text)
        old_avg = float(old.get("extra_damage_avg") or 0)
        new_avg = float(new.get("extra_damage_avg") or 0)
        old_multiplier = 1.0
        new_multiplier = extra_damage_pricing_multiplier(new)
        old_weighted = old_avg * old_multiplier
        new_weighted = new_avg * new_multiplier
        old_total += old_avg
        new_total += new_avg
        old_weighted_total += old_weighted
        new_weighted_total += new_weighted
        if old_avg == new_avg and old_weighted == new_weighted:
            continue
        delta = new_avg - old_avg
        weighted_delta = new_weighted - old_weighted
        coefficient = _rarity_extra_damage_coefficient(_rarity(item))
        rows.append(
            {
                "name": name,
                "source": _source(item),
                "rarity": _rarity(item),
                "type": _item_type(item),
                "old_extra_damage_avg": old_avg,
                "new_extra_damage_avg": new_avg,
                "delta_extra_damage_avg": delta,
                "new_extra_damage_condition": new.get("extra_damage_condition"),
                "new_extra_damage_multiplier": new_multiplier,
                "delta_weighted_extra_damage_avg": weighted_delta,
                "delta_exposure_gp": weighted_delta * coefficient,
                "exposure_coefficient_gp": coefficient,
                "current_output_price": _current_price(name, price_lookup),
                "known_good_anchor": _known_good_anchor(name, price_lookup),
                "evidence": _evidence(prose_text or str(item.get("entries", []))),
            }
        )

    high_rarity = {"very rare", "legendary", "artifact"}
    return {
        "item_count": len(items),
        "changed_count": len(rows),
        "old_total_extra_damage_avg": old_total,
        "new_total_extra_damage_avg": new_total,
        "old_total_weighted_extra_damage_avg": old_weighted_total,
        "new_total_weighted_extra_damage_avg": new_weighted_total,
        "total_delta_extra_damage_avg": new_total - old_total,
        "total_delta_weighted_extra_damage_avg": new_weighted_total - old_weighted_total,
        "direct_formula_exposure_gp": sum(row["delta_exposure_gp"] for row in rows),
        "high_rarity_count": sum(1 for row in rows if str(row["rarity"]).lower() in high_rarity),
        "artifact_count": sum(1 for row in rows if str(row["rarity"]).lower() == "artifact"),
        "known_good_anchor_count": sum(1 for row in rows if row["known_good_anchor"]),
        "rows": sorted(rows, key=lambda row: (-row["delta_exposure_gp"], row["name"], row["source"])),
    }


def _money(value: float) -> str:
    return f"{value:,.0f} gp"


def _num(value: float) -> str:
    return f"{value:g}"


def _md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def build_report(analysis: dict[str, Any]) -> str:
    lines = [
        "# extra_damage_avg Current Canonical Impact",
        "",
        "This report compares old vs new `extra_damage_avg` extraction on CURRENT canonical items using markdown prose, matching the criteria pipeline input shape. It is not a full pipeline price delta; it is direct criterion exposure using rarity-specific coefficients (1,500 gp/point below legendary, 3,000 gp/point for legendary/artifact) after extra-damage condition multipliers.",
        "",
        "## Summary",
        "",
        f"- Current canonical rows analyzed: {analysis['item_count']}",
        f"- Changed current canonical rows: {analysis['changed_count']}",
        f"- Old total extra_damage_avg: {_num(analysis['old_total_extra_damage_avg'])}",
        f"- New total extra_damage_avg: {_num(analysis['new_total_extra_damage_avg'])}",
        f"- Total delta extra_damage_avg: {_num(analysis['total_delta_extra_damage_avg'])}",
        f"- Old weighted extra_damage_avg: {_num(analysis.get('old_total_weighted_extra_damage_avg', 0.0))}",
        f"- New weighted extra_damage_avg: {_num(analysis.get('new_total_weighted_extra_damage_avg', 0.0))}",
        f"- Total delta weighted extra_damage_avg: {_num(analysis.get('total_delta_weighted_extra_damage_avg', 0.0))}",
        f"- Direct formula exposure: {_money(analysis['direct_formula_exposure_gp'])}",
        f"- High-rarity changed rows: {analysis['high_rarity_count']}",
        f"- Artifact changed rows: {analysis['artifact_count']}",
        f"- Known-good/reference-anchor changed rows: {analysis['known_good_anchor_count']}",
        "",
        "## Changed rows",
        "",
        "| # | Name | Source | Rarity | Type | Old avg | New avg | Condition | Multiplier | Weighted delta | Direct exposure | Current output price | Reference anchor | Evidence |",
        "|---:|---|---|---|---|---:|---:|---|---:|---:|---:|---:|---|---|",
    ]
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
                    _num(row["old_extra_damage_avg"]),
                    _num(row["new_extra_damage_avg"]),
                    _md(row.get("new_extra_damage_condition")),
                    _num(row.get("new_extra_damage_multiplier", 1.0)),
                    _num(row.get("delta_weighted_extra_damage_avg", row["delta_extra_damage_avg"])),
                    _money(row["delta_exposure_gp"]),
                    _md(row["current_output_price"]),
                    "yes" if row["known_good_anchor"] else "no",
                    _md(row["evidence"]),
                ]
            )
            + " |"
        )
    if not analysis["rows"]:
        lines.append("| — | — | — | — | — | 0 | 0 | 0 gp | — | — | — |")
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            "Treat this as a pricing-impact gate. The extraction may be semantically correct, but because `extra_damage_avg` is price-bearing, full pricing should wait for review/sign-off of these rows.",
            "",
        ]
    )
    return "\n".join(lines)


def run(*, master_path: str | Path, prose_path: str | Path, output_path: str | Path) -> int:
    master_path = Path(master_path)
    prose_path = Path(prose_path)
    output_path = Path(output_path)
    missing = [path for path in (master_path, prose_path) if not path.exists()]
    if missing:
        print("Skipping extra_damage impact: missing required input(s): " + ", ".join(str(path) for path in missing))
        return 0

    items = load_master_items(master_path)
    prose_map = load_prose_descriptions(prose_path)
    price_lookup = load_price_lookup(DEFAULT_PRICING)
    analysis = analyze_items(items, prose_map, price_lookup)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_report(analysis), encoding="utf-8")
    print(f"Wrote extra_damage impact report to {output_path}")
    print(f"Changed current canonical rows: {analysis['changed_count']}")
    print(f"Direct formula exposure: {_money(analysis['direct_formula_exposure_gp'])}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", type=Path, default=DEFAULT_MASTER)
    parser.add_argument("--prose", type=Path, default=DEFAULT_PROSE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    return run(master_path=args.master, prose_path=args.prose, output_path=args.output)


if __name__ == "__main__":
    raise SystemExit(main())
