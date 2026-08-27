#!/usr/bin/env python3
"""Generate a criteria-only preflight report for the 2026-07-12 item list."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.criteria_extractor import extract_entries_criteria, extract_prose_criteria, extract_structured_criteria


DEFAULT_INPUT = Path("2026_07_12_item_list.json")
DEFAULT_OUTPUT = Path("reports/criteria_preflight_2026_07_12.md")
EXAMPLE_LIMIT = 5

VEHICLE_CRITERIA_FIELDS = [
    "vehicle_speed",
    "vehicle_ac",
    "vehicle_hp",
    "vehicle_crew",
    "vehicle_cargo_capacity",
]
VEHICLE_RAW_FIELDS = ["vehSpeed", "vehAc", "vehHp", "crew", "capCargo"]

PREFERRED_ENTRY_KEYS = (
    "name",
    "entry",
    "entries",
    "items",
    "rows",
    "rowLabels",
    "colLabels",
    "caption",
    "text",
)


Record = dict[str, Any]
Predicate = Callable[[Record], bool]
Formatter = Callable[[Record], str]


def _has_value(value: Any) -> bool:
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return value is not None and value != ""


def _has_raw_field(item: dict[str, Any], field_name: str) -> bool:
    return field_name in item


def _has_criteria(record: Record, field_name: str) -> bool:
    return _has_value(record["criteria"].get(field_name))


def _has_prose_criteria(record: Record, field_name: str) -> bool:
    return _has_value(record["prose_criteria"].get(field_name))


def _has_entries_criteria(record: Record, field_name: str) -> bool:
    return _has_value(record["entries_criteria"].get(field_name))


def _entry_text(value: Any) -> str:
    """Flatten 5e.tools entry structures into stable plain-ish text for extraction."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(part for part in (_entry_text(item) for item in value) if part)
    if isinstance(value, dict):
        parts: list[str] = []
        seen_keys = set(PREFERRED_ENTRY_KEYS)
        for key in PREFERRED_ENTRY_KEYS:
            if key in value:
                text = _entry_text(value[key])
                if text:
                    parts.append(text)
        for key in sorted(k for k in value if k not in seen_keys and k != "type"):
            text = _entry_text(value[key])
            if text:
                parts.append(text)
        return " ".join(parts)
    return str(value)


def _item_label(item: dict[str, Any]) -> str:
    name = item.get("name") or "<unnamed>"
    source = item.get("source") or "unknown source"
    return f"{name} ({source})"


def _source(record: Record) -> str:
    return str(record["item"].get("source") or "unknown")


def _top_sources(records: list[Record], predicate: Predicate, limit: int = 5) -> str:
    counts = Counter(_source(record) for record in records if predicate(record))
    if not counts:
        return "—"
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    return ", ".join(f"{source} ({count})" for source, count in ordered)


def _count(records: list[Record], predicate: Predicate) -> int:
    return sum(1 for record in records if predicate(record))


def _raw_field_predicate(field_name: str) -> Predicate:
    return lambda record: _has_raw_field(record["item"], field_name)


def _criteria_predicate(field_name: str) -> Predicate:
    return lambda record: _has_criteria(record, field_name)


def _prose_criteria_predicate(field_name: str) -> Predicate:
    return lambda record: _has_prose_criteria(record, field_name)


def _entries_criteria_predicate(field_name: str) -> Predicate:
    return lambda record: _has_entries_criteria(record, field_name)


def _positive_entries_criteria_predicate(field_name: str) -> Predicate:
    return lambda record: (record["entries_criteria"].get(field_name) or 0) > 0


def _any_vehicle_raw(record: Record) -> bool:
    return any(_has_raw_field(record["item"], field_name) for field_name in VEHICLE_RAW_FIELDS)


def _any_vehicle_criteria(record: Record) -> bool:
    return any(_has_criteria(record, field_name) for field_name in VEHICLE_CRITERIA_FIELDS)


def _check_advantage_candidate(record: Record) -> bool:
    return bool(re.search(r"\badvantage\b[^.;]{0,160}\bchecks?\b", record["prose_text"], re.IGNORECASE))


def _disadvantage_candidate(record: Record) -> bool:
    return bool(
        re.search(
            r"\bdisadvantage\b[^.;]{0,160}\b(?:checks?|saving throws?)\b",
            record["prose_text"],
            re.IGNORECASE,
        )
    )


def _extra_damage_candidate(record: Record) -> bool:
    return bool(
        re.search(r"\b(?:extra|additional)\s+\{@damage\s+[^}]+\}", record["prose_text"], re.IGNORECASE)
        or re.search(
            r"\b(?:extra|additional)\s+\d+d\d+(?:\s+[a-z]+(?:\s+or\s+[a-z]+)?)?\s+damage\b",
            record["prose_text"],
            re.IGNORECASE,
        )
    )


def _format_scalar(prefix: str, value: Any) -> str:
    return f"{prefix}={value}"


def _format_raw_field(field_name: str) -> Formatter:
    return lambda record: _format_scalar(field_name, record["item"][field_name])


def _format_criteria_field(field_name: str) -> Formatter:
    return lambda record: _format_scalar(field_name, record["criteria"][field_name])


def _format_target_list(field_name: str) -> Formatter:
    return lambda record: ", ".join(str(value) for value in record["prose_criteria"][field_name])


def _format_prose_field(field_name: str) -> Formatter:
    return lambda record: _format_scalar(field_name, record["prose_criteria"][field_name])


def _format_extra_damage(record: Record) -> str:
    entries_criteria = record["entries_criteria"]
    return (
        f"extra_damage_avg={entries_criteria['extra_damage_avg']}, "
        f"extra_damage_dice={entries_criteria['extra_damage_dice']}"
    )


def _format_vehicle_criteria(record: Record) -> str:
    criteria = record["criteria"]
    return ", ".join(
        f"{field_name}={criteria[field_name]}"
        for field_name in VEHICLE_CRITERIA_FIELDS
        if _has_value(criteria.get(field_name))
    )


def _example_lines(
    records: list[Record],
    predicate: Predicate,
    formatter: Formatter,
    limit: int = EXAMPLE_LIMIT,
) -> list[str]:
    examples: list[str] = []
    for record in records:
        if predicate(record):
            examples.append(f"- {_item_label(record['item'])}: `{formatter(record)}`")
        if len(examples) >= limit:
            break
    return examples or ["- None."]


def _analysis_records(items: list[dict[str, Any]]) -> list[Record]:
    records: list[Record] = []
    for item in items:
        prose_text = _entry_text(item.get("entries", []))
        records.append(
            {
                "item": item,
                "criteria": extract_structured_criteria(item),
                "prose_text": prose_text,
                "prose_criteria": extract_prose_criteria(prose_text),
                "entries_criteria": extract_entries_criteria(item),
            }
        )
    return records


def _count_row(records: list[Record], label: str, predicate: Predicate) -> str:
    return f"| {label} | {_count(records, predicate)} | {_top_sources(records, predicate)} |"


def build_report(items: list[dict[str, Any]], input_path: Path) -> str:
    records = _analysis_records(items)
    reload_predicate = _criteria_predicate("reload")
    raw_ac_predicate = _raw_field_predicate("ac")
    armor_ac_predicate = _criteria_predicate("armor_ac")
    raw_strength_predicate = _raw_field_predicate("strength")
    armor_strength_predicate = _criteria_predicate("armor_strength_req")
    check_advantage_predicate = _prose_criteria_predicate("check_advantage")
    check_disadvantage_predicate = _prose_criteria_predicate("check_disadvantage")
    save_disadvantage_predicate = _prose_criteria_predicate("save_disadvantage")
    save_dc_predicate = _prose_criteria_predicate("save_dc")
    extra_damage_predicate = _positive_entries_criteria_predicate("extra_damage_avg")

    lines = [
        "# 2026-07-12 Criteria Preflight (Phase 1)",
        "",
        f"Raw file: `{input_path.as_posix()}` (left untracked; no canonical replacement or pricing pipeline run).",
        f"Total items analyzed: {len(items)}",
        "",
        "## Count summary",
        "",
        "| Metric | Count | Top sources |",
        "|---|---:|---|",
        _count_row(records, "`reload`", reload_predicate),
        _count_row(records, "raw `ac`", raw_ac_predicate),
        _count_row(records, "extracted `armor_ac`", armor_ac_predicate),
        _count_row(records, "raw `strength`", raw_strength_predicate),
        _count_row(records, "extracted `armor_strength_req`", armor_strength_predicate),
        _count_row(records, "raw vehicle stats (any)", _any_vehicle_raw),
        _count_row(records, "any `vehicle_*`", _any_vehicle_criteria),
        _count_row(records, "raw prose `advantage ... checks`", _check_advantage_candidate),
        _count_row(records, "raw prose `disadvantage ... checks/saves`", _disadvantage_candidate),
        _count_row(records, "extracted `check_advantage`", check_advantage_predicate),
        _count_row(records, "extracted `check_disadvantage`", check_disadvantage_predicate),
        _count_row(records, "extracted `save_disadvantage`", save_disadvantage_predicate),
        _count_row(records, "extracted `save_dc`", save_dc_predicate),
        _count_row(records, "raw prose extra/additional damage candidates", _extra_damage_candidate),
        _count_row(records, "extracted `extra_damage_avg`", extra_damage_predicate),
        "",
        "## Structured field examples",
        "",
        "### Reload",
        *_example_lines(records, reload_predicate, _format_criteria_field("reload")),
        "",
        "### Raw AC",
        *_example_lines(records, raw_ac_predicate, _format_raw_field("ac")),
        "",
        "### Extracted armor_ac",
        *_example_lines(records, armor_ac_predicate, _format_criteria_field("armor_ac")),
        "",
        "### Raw strength",
        *_example_lines(records, raw_strength_predicate, _format_raw_field("strength")),
        "",
        "### Extracted armor_strength_req",
        *_example_lines(records, armor_strength_predicate, _format_criteria_field("armor_strength_req")),
        "",
        "### Vehicle stats",
        *_example_lines(records, _any_vehicle_criteria, _format_vehicle_criteria),
        "",
        "## Advantage/disadvantage prose examples",
        "",
        "Examples show normalized extractor targets only, not raw prose snippets.",
        "",
        "### check_advantage",
        *_example_lines(records, check_advantage_predicate, _format_target_list("check_advantage")),
        "",
        "### check_disadvantage",
        *_example_lines(records, check_disadvantage_predicate, _format_target_list("check_disadvantage")),
        "",
        "### save_disadvantage",
        *_example_lines(records, save_disadvantage_predicate, _format_target_list("save_disadvantage")),
        "",
        "### save_dc",
        *_example_lines(records, save_dc_predicate, _format_prose_field("save_dc")),
        "",
        "## Extra damage examples",
        "",
        "The extra damage rows below use raw 2026 JSON entries only. Current canonical markdown-prose impact is price-bearing and is reported separately in `reports/extra_damage_impact_2026_07_12.md`.",
        "",
        "### extra_damage_avg",
        *_example_lines(records, extra_damage_predicate, _format_extra_damage),
        "",
        "## Pipeline safety",
        "",
        "- Did not edit `trimmed_5etools_list.*`.",
        "- Did not run full pricing or write `data/processed`/published outputs.",
        "- Report reflects current `src.criteria_extractor` behavior only.",
        "",
    ]
    return "\n".join(lines)


def run(*, input_path: str | Path, output_path: str | Path) -> int:
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        print(f"Skipping criteria preflight: raw input file not found at {input_path}")
        return 0

    items = json.loads(input_path.read_text(encoding="utf-8"))
    report = build_report(items, input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"Wrote criteria preflight report to {output_path}")
    print(f"Total items analyzed: {len(items)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    return run(input_path=args.input, output_path=args.output)


if __name__ == "__main__":
    raise SystemExit(main())
