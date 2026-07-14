#!/usr/bin/env python3
"""Compare baseline vs candidate pricing CSVs for extraction-driven price creep."""

from __future__ import annotations

import argparse
import csv
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


DEFAULT_BASELINE = Path("output/pricing_guide.csv")
DEFAULT_CANDIDATE = Path("output/pricing_guide_candidate.csv")
DEFAULT_OUTPUT = Path("reports/price_creep_guardrail.md")

KNOWN_GOOD_PATTERNS = (
    "holy avenger",
    "defender",
    "vorpal sword",
    "+1 weapon",
    "+2 weapon",
    "+3 weapon",
    "+1 armor",
    "+2 armor",
    "+3 armor",
    "dragon slayer",
    "giant slayer",
    "vicious weapon",
)


Row = dict[str, Any]


def _column(row: Row, *names: str) -> str:
    normalized = {str(key).casefold(): key for key in row.keys()}
    for name in names:
        key = normalized.get(name.casefold())
        if key is not None:
            return str(row.get(key) or "")
    return ""


def _parse_money(value: Any) -> float:
    text = str(value or "").replace(",", "").replace("gp", "").replace("$", "").strip()
    if not text:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def _key(row: Row) -> tuple[str, str]:
    return (_column(row, "Name", "name").strip().casefold(), _column(row, "Source", "source").strip().casefold())


def _price(row: Row) -> float:
    return _parse_money(_column(row, "Price (gp)", "price_gp", "final_price", "price"))


def _name(row: Row) -> str:
    return _column(row, "Name", "name")


def _source(row: Row) -> str:
    return _column(row, "Source", "source") or "unknown"


def _rarity(row: Row) -> str:
    return _column(row, "Rarity", "rarity") or "unknown"


def _type(row: Row) -> str:
    return _column(row, "Type", "type", "Type Code", "item_type_code") or "unknown"


def _has_reference(row: Row) -> bool:
    raw = _column(row, "Has Reference", "has_reference_source", "Reference Sources", "reference_sources")
    if raw:
        return raw.strip().casefold() in {"true", "yes", "1"} or raw.strip() not in {"", "False", "false", "0"}
    return bool(_column(row, "amalgamated_price", "dsa_price", "msrp_price", "dmpg_price"))


def _split_label(row: Row) -> str:
    return "reference-anchored" if _has_reference(row) else "formula/ML-only"


def _is_known_good(name: str) -> bool:
    lowered = re.sub(r"\s+", " ", name.casefold().strip())
    if any(pattern in lowered for pattern in KNOWN_GOOD_PATTERNS):
        return True
    if re.match(r"^\+[123]\s+.+", lowered):
        return True
    if re.match(r"^vicious\s+.+", lowered):
        return True
    return False


def load_price_rows(path: str | Path) -> list[Row]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {"count": 0, "median": 0.0, "mean": 0.0}
    return {
        "count": len(values),
        "median": statistics.median(values),
        "mean": statistics.mean(values),
    }


def _summarize(rows: list[Row]) -> dict[str, float]:
    return {
        "count": len(rows),
        "median_pct": _stats([row["pct_delta"] for row in rows])["median"],
        "mean_pct": _stats([row["pct_delta"] for row in rows])["mean"],
        "median_gp": _stats([row["gp_delta"] for row in rows])["median"],
        "mean_gp": _stats([row["gp_delta"] for row in rows])["mean"],
    }


def _group_summary(rows: list[Row], field: str) -> dict[str, dict[str, float]]:
    groups: dict[str, list[Row]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(field) or "unknown")].append(row)
    return {key: _summarize(value) for key, value in sorted(groups.items())}


def _known_good_status(rows: list[Row], *, review_threshold_pct: float = 1.0, fail_threshold_pct: float = 5.0) -> str:
    if not rows:
        return "PASS"
    max_abs = max(abs(row["pct_delta"]) for row in rows)
    if max_abs > fail_threshold_pct:
        return "FAIL"
    if max_abs > review_threshold_pct:
        return "REVIEW"
    return "PASS"


def analyze_price_drift(baseline_rows: list[Row], candidate_rows: list[Row]) -> dict[str, Any]:
    baseline_by_key = {_key(row): row for row in baseline_rows}
    candidate_by_key = {_key(row): row for row in candidate_rows}
    common_keys = sorted(set(baseline_by_key) & set(candidate_by_key))
    new_keys = sorted(set(candidate_by_key) - set(baseline_by_key))
    missing_keys = sorted(set(baseline_by_key) - set(candidate_by_key))

    rows: list[Row] = []
    for key in common_keys:
        base = baseline_by_key[key]
        candidate = candidate_by_key[key]
        base_price = _price(base)
        candidate_price = _price(candidate)
        gp_delta = candidate_price - base_price
        pct_delta = (gp_delta / base_price * 100) if base_price else 0.0
        rows.append(
            {
                "Name": _name(base),
                "Source": _source(base),
                "Rarity": _rarity(base),
                "Type": _type(base),
                "baseline_price": base_price,
                "candidate_price": candidate_price,
                "gp_delta": gp_delta,
                "pct_delta": pct_delta,
                "reference_split": _split_label(base),
                "known_good": _is_known_good(_name(base)),
            }
        )

    rows_by_abs_delta = sorted(rows, key=lambda row: (abs(row["gp_delta"]), abs(row["pct_delta"])), reverse=True)
    known_good_rows = [row for row in rows_by_abs_delta if row["known_good"]]
    artifact_legendary_rows = [
        row for row in rows_by_abs_delta if str(row["Rarity"]).casefold() in {"artifact", "legendary"}
    ]
    reference_split = _group_summary(rows, "reference_split")
    return {
        "common_count": len(common_keys),
        "new_count": len(new_keys),
        "missing_count": len(missing_keys),
        "new_rows": [candidate_by_key[key] for key in new_keys],
        "missing_rows": [baseline_by_key[key] for key in missing_keys],
        "rows": rows,
        "aggregate": _summarize(rows),
        "threshold_counts": {
            ">5%": sum(1 for row in rows if abs(row["pct_delta"]) > 5),
            ">10%": sum(1 for row in rows if abs(row["pct_delta"]) > 10),
            ">25%": sum(1 for row in rows if abs(row["pct_delta"]) > 25),
        },
        "reference_split": reference_split,
        "rarity_split": _group_summary(rows, "Rarity"),
        "type_split": _group_summary(rows, "Type"),
        "source_split": _group_summary(rows, "Source"),
        "known_good_rows": known_good_rows,
        "known_good_status": _known_good_status(known_good_rows),
        "artifact_legendary_rows": artifact_legendary_rows,
        "largest_movers": rows_by_abs_delta[:25],
    }


def _money(value: float) -> str:
    return f"{value:,.0f} gp"


def _pct(value: float) -> str:
    return f"{value:.2f}%"


def _md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _summary_table(summary: dict[str, dict[str, float]], label: str, *, limit: int = 20) -> list[str]:
    lines = [f"| {label} | Rows | Median % | Mean % | Median gp | Mean gp |", "|---|---:|---:|---:|---:|---:|"]
    rows = sorted(summary.items(), key=lambda item: (-item[1]["count"], item[0]))[:limit]
    if not rows:
        return [*lines, "| — | 0 | 0.00% | 0.00% | 0 gp | 0 gp |"]
    for key, stats in rows:
        lines.append(
            f"| {_md(key)} | {int(stats['count'])} | {_pct(stats['median_pct'])} | {_pct(stats['mean_pct'])} | {_money(stats['median_gp'])} | {_money(stats['mean_gp'])} |"
        )
    return lines


def _mover_table(rows: list[Row], *, limit: int = 20) -> list[str]:
    lines = [
        "| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |",
        "|---|---|---|---|---:|---:|---:|---:|---|",
    ]
    if not rows:
        return [*lines, "| — | — | — | — | 0 gp | 0 gp | 0 gp | 0.00% | — |"]
    for row in rows[:limit]:
        lines.append(
            f"| {_md(row['Name'])} | {_md(row['Source'])} | {_md(row['Rarity'])} | {_md(row['Type'])} | {_money(row['baseline_price'])} | {_money(row['candidate_price'])} | {_money(row['gp_delta'])} | {_pct(row['pct_delta'])} | {_md(row['reference_split'])} |"
        )
    return lines


def build_template_report(baseline_path: Path, candidate_path: Path) -> str:
    return "\n".join(
        [
            "# Price Creep Guardrail",
            "",
            f"Baseline CSV: `{baseline_path}`",
            f"Candidate CSV: `{candidate_path}`",
            "",
            "No candidate CSV supplied/found. Provide a candidate pricing CSV to compare realized final-price drift before full pricing/canonical migration.",
            "",
            "Formula exposure reports (for example, extra_damage impact) are not final-price deltas.",
            "",
        ]
    )


def build_report(analysis: dict[str, Any], *, baseline_path: Path, candidate_path: Path) -> str:
    aggregate = analysis["aggregate"]
    lines = [
        "# Price Creep Guardrail",
        "",
        f"Baseline CSV: `{baseline_path}`",
        f"Candidate CSV: `{candidate_path}`",
        "",
        "## Input row matching",
        "",
        f"- Common rows: {analysis['common_count']}",
        f"- New candidate rows: {analysis['new_count']}",
        f"- Missing candidate rows: {analysis['missing_count']}",
        "",
        "## Aggregate final-price drift",
        "",
        f"- Median % drift: {_pct(aggregate['median_pct'])}",
        f"- Mean % drift: {_pct(aggregate['mean_pct'])}",
        f"- Median gp drift: {_money(aggregate['median_gp'])}",
        f"- Mean gp drift: {_money(aggregate['mean_gp'])}",
        f"- Rows >5% drift: {analysis['threshold_counts']['>5%']}",
        f"- Rows >10% drift: {analysis['threshold_counts']['>10%']}",
        f"- Rows >25% drift: {analysis['threshold_counts']['>25%']}",
        "",
        "## Reference anchored vs formula/ML-only",
        "",
        *_summary_table(analysis["reference_split"], "Split"),
        "",
        "## Drift by rarity",
        "",
        *_summary_table(analysis["rarity_split"], "Rarity"),
        "",
        "## Drift by type",
        "",
        *_summary_table(analysis["type_split"], "Type"),
        "",
        "## Drift by source",
        "",
        *_summary_table(analysis["source_split"], "Source"),
        "",
        "## Known-good anchors",
        "",
        "Known-good status: **" + analysis["known_good_status"] + "** (PASS ≤1% drift; REVIEW >1%; FAIL >5%).",
        "Configured anchors include Holy Avenger, Defender, Vorpal Sword, +1/+2/+3 Weapon/Armor, Dragon Slayer, Giant Slayer, and Vicious Weapon families when present.",
        "",
        *_mover_table(analysis["known_good_rows"], limit=20),
        "",
        "## Artifact/legendary movers",
        "",
        *_mover_table(analysis["artifact_legendary_rows"], limit=20),
        "",
        "## Largest movers",
        "",
        *_mover_table(analysis["largest_movers"], limit=25),
        "",
        "## Anchor-tier transitions / ML R² / double-count audit",
        "",
        "- Anchor-tier transition and ML R² checks require pipeline metadata not present in final CSV snapshots; add those columns to future candidate snapshots if needed.",
        "- Use the known-good and reference-anchored sections above as the first-pass double-count audit for extraction-driven price creep.",
        "- Formula exposure reports (for example, extra_damage impact) are not final-price deltas.",
        "",
    ]
    return "\n".join(lines)


def run(*, baseline_path: str | Path, candidate_path: str | Path, output_path: str | Path) -> int:
    baseline_path = Path(baseline_path)
    candidate_path = Path(candidate_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not candidate_path.exists():
        output_path.write_text(build_template_report(baseline_path, candidate_path), encoding="utf-8")
        print(f"No candidate CSV supplied/found at {candidate_path}; wrote guardrail template to {output_path}")
        return 0
    if not baseline_path.exists():
        output_path.write_text(build_template_report(baseline_path, candidate_path), encoding="utf-8")
        print(f"No baseline CSV supplied/found at {baseline_path}; wrote guardrail template to {output_path}")
        return 0

    analysis = analyze_price_drift(load_price_rows(baseline_path), load_price_rows(candidate_path))
    output_path.write_text(build_report(analysis, baseline_path=baseline_path, candidate_path=candidate_path), encoding="utf-8")
    print(f"Wrote price creep guardrail report to {output_path}")
    print(f"Common rows: {analysis['common_count']}")
    print(f"Known-good status: {analysis['known_good_status']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    return run(baseline_path=args.baseline, candidate_path=args.candidate, output_path=args.output)


if __name__ == "__main__":
    raise SystemExit(main())
