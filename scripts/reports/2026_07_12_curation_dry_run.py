#!/usr/bin/env python3
"""Generate a dry-run report for the 2026-07-12 source-list curation policy."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.list_curation import curate_items, format_curation_report_markdown, load_item_list


DEFAULT_INPUT = Path("2026_07_12_item_list.json")
DEFAULT_OUTPUT = Path("output/2026_07_12_curation_dry_run.md")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    items = load_item_list(args.input)
    curated = curate_items(items)
    report = curated.report
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(format_curation_report_markdown(report), encoding="utf-8")

    print(f"Wrote dry-run report to {args.output}")
    print(f"Total items: {report['total_items']}")
    print(f"Curated items after exclusions: {report['curated_items_count']}")
    print(f"Excluded QftIS grenades: {report['excluded_items_count']}")
    print(f"Nested generic/template parents: {report['nested_generic_phrase_count']}")
    print(
        "Magic/material official-price conflict candidates: "
        f"{report['magic_material_official_price_conflict_candidate_count']}"
    )


if __name__ == "__main__":
    main()
