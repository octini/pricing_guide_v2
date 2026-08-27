# D&D 5e Item Pricing Guide v2 — Project Context

**Last updated:** 2026-08-27
**Working directory:** `/Users/ryan/opencode/TTRPG/pricing_guide_v2/`
**Spec:** `docs/superpowers/specs/2026-04-06-dnd-pricing-guide-design.md` (April scope superseded — see below)
**Tracker:** beads (`bd ready` is authoritative)

---

## Project Goal

Objective, data-driven pricing for the **curated 5e item list**. Output: Excel + CSV (`output/pricing_guide.xlsx` / `.csv`).

Original April scope — 9,422 items via `items-sublist-data.json` (Standard + Drakkenheim + Eberron sources) — is **superseded**. That file is legacy and unused.

---

## Input Files

| File | Count | Role |
|------|-------|------|
| `trimmed_5etools_list.json` | **4,837** | **Canonical** pipeline input (curated) |
| `items-sublist-data.json` | 9,422 | Legacy — do not use |
| `2026_07_12_item_list.json` | **12,243** | Expansion — audited, approved-pending-migration (see `pricing_guide_v2-9xv`); expect ~12k output rows post-migration |
| `items-sublist.md` | — | Prose descriptions for NLP extraction (must align with canonical list) |
| `~/Downloads/DMPG.pdf` | — | Discerning Merchant's Price Guide (external guide) |
| External | — | DSA + MSRP Google Sheets (external guides) |

### Funnel (canonical)

```
trimmed_5etools_list.json (4,837)
  → pipeline (01–09, 11)
  → 10_generate_output excludes generic variants + dedupes identical Name/Price/Type
     (prefers 2024 core books: DMG2024, PHB2024)
  → 4,749 output rows
```

Expansion funnel will be ~12,243 → ~12k rows (same exclusions/dedupe).

---

## Architecture

### Numbered pipeline scripts

```
scripts/
  01_extract_items.py        → data/processed/items_master.csv
  02_extract_criteria.py     → data/processed/items_criteria.csv
  03_ingest_external.py      → data/raw/{dsa,msrp,dmpg}_prices.csv
  04_amalgamate.py           → data/processed/amalgamated_prices.csv
  05_rule_formula.py         → data/processed/rule_prices.csv (price_authority flag)
  05b_variant_adjust.py      → variant-adjusted intermediate (via src/variant_system)
  06_ml_refine.py            → data/processed/coefficients.json + items_ml_priced.csv
  07_validate.py             → output/anomaly_report.md
  07b_variant_consistency.py → output/variant_consistency_report.csv
  09_enforce_floors.py       → floor enforcement (uses src/constants.EXPENSIVE_ARMOR_BASES)
  10_generate_output.py      → output/pricing_guide.xlsx + .csv (generic exclusion + dedupe)
  11_generate_html.py        → HTML output
```

Scripts 01–11 are stable entry points — docs/issues reference them by number; do not renumber.

### Library modules (`src/`)

```
src/
  criteria_extractor.py      # JSON + NLP criteria extraction
  pricing_engine.py          # Formula, authority, save-advantage tiers, extra-damage multipliers
  variant_system.py          # Merged from 4 modules: variant_adjuster, variant_pricing,
                             #   generic_pricing, generic_variant_mapper
  amalgamator.py             # Weighted mean with trimming
  anomaly_detector.py        # Outlier/anomaly detection
  constants.py               # Shared constants (EXPENSIVE_ARMOR_BASES, RARITY_MEDIANS, etc.)
  list_curation.py           # Curation / filtering helpers
  official_price_anchor.py   # Official-price anchoring post-blend
  prose_loader.py            # Prose loading for NLP
  source_names.py            # Source name normalization
  spell_data.py              # Spell data helpers
  ml_fingerprint.py          # Criteria fingerprint (sha256 of feature + criteria cols)
  utils.py                   # Shared helpers
```

### One-off report tooling (`scripts/reports/`)

Not part of the numbered pipeline — run ad hoc:

- `check_r2.py` — R² quality gate (see below)
- `price_creep_guardrail.py` — baseline vs candidate drift + known-good anchors
- `curation_preflight_2026_07_12.py`, `criteria_preflight_2026_07_12.py` — expansion preflights
- `extra_damage_impact_2026_07_12.py`, `triage_absent_canonical_2026_07_12.py`, `2026_07_12_curation_dry_run.py`, `review_checks.py` — impact/triage reports

---

## Quality Gates

All must pass before merge/release:

1. **R² ≥ 0.80** via `python3 scripts/reports/check_r2.py` — runs `06_ml_refine` and checks blended R² (log-space). Currently **0.9723** (baseline 0.80, max drop 0.02). Gate also enforces **ML criteria fingerprint**: stale `coefficients.json` (feature/criteria columns changed without retrain) fails.
2. **Price-creep guardrail** via `python3 scripts/reports/price_creep_guardrail.py` — compares baseline vs candidate CSVs; reports drift by reference-anchored vs formula-only and by source. **Known-good anchors** must stay ≤1% drift (REVIEW >1%, FAIL >5%): `+1/+2/+3 weapon`, `+1/+2/+3 armor`, Vorpal Sword family, Holy Avenger, Defender, Dragon Slayer, Giant Slayer, Vicious Weapon families.
3. **Full test suite** — `python3 -m pytest tests/ -q` (2 known pre-existing failures excluded via `--ignore=tests/test_hospitality.py` for quick sanity; full suite for gate).

---

## Pricing Policies

### Pricing authority (`price_authority` in `rule_prices`)

- **Default: anchor wins** — if `amalgamated_price` exists and `price_confidence` is `multi` (3 guides) or `solo` (1 guide), use the amalgamated/guide price.
- **Formula wins** only when **criteria-rich (≥3)** AND **guide-divergent (>0.60)** AND `multi`/`solo` — i.e. the item has enough extracted criteria to trust the formula and guides disagree enough to distrust the anchor. Flagged as `price_authority=formula`.
- Other branches: `rule` (no amalgamated price), `rule-outlier` (solo-outlier), `official` (official-price lane).

Implementation: `src/pricing_engine.derive_price_authority()` — re-evaluates branch conditions; keep identical to pricing branch logic.

### Save-advantage tiers

Flat 400 gp base, tiered:

| Tier | Multiplier | GP | Meaning |
|------|-----------|----|---------|
| **BROAD** | 1.0× | **400** | All saves or single ability, always-on |
| **CATEGORY** | 0.5× | **200** | vs condition/creature-type/damage/spell (e.g. vs frightened, vs spells) |
| **SITUATIONAL** | 0.25× | **100** | State/position-gated (e.g. while at 0 hp, while mounted) |

Legacy `conditional_save_advantage` path (flat 200 gp) is **disjoint by design** — extractor never double-counts; new CATEGORY tier (400×0.5=200) coincides exactly, so no additive overlap.

### Extra damage

- **Raw** `extra_damage_avg` — truthful per-hit dice average, stored for reporting/ML.
- **Priced** `extra_damage_priced_avg` — raw × condition multiplier, used only for rule-formula additive value.

| Condition | Multiplier |
|-----------|-----------|
| `unconditional` | **1.0** |
| `vs_creature_type` | **0.25** |
| `on_crit` | **0.05** |

Helper: `src/pricing_engine.extra_damage_pricing_multiplier()`.

---

## Key Decisions

| Decision | Choice |
|----------|--------|
| Mundane items with official prices | Use `value` field directly (÷100, field is in cp) |
| Mundane items with guidance-only pricing | Use algorithm |
| MSRP pricing | Average of low/high magic columns |
| Attunement (open) | ×0.85 multiplier |
| Attunement (class-restricted) | ×0.75 multiplier |
| Consumable: potion | ×0.50 |
| Consumable: scroll | ×0.20 |
| Consumable: ammunition (single) | ×0.05 |
| Material: Mithral | ×2.00 |
| Material: Adamantine | ×2.50 |
| Cursed item | ×0.70 |
| Sentient item | ×1.25 |
| Algorithm approach | Rule-based formula + XGBoost refinement (hybrid) |
| ML method | XGBoost with quantile regression (prior: Ridge; prior project R²=0.66) |
| R² target | ≥ 0.80 (currently 0.9723 blended) |
| ML retrain discipline | Criteria fingerprint (sha256 of feature + criteria cols); stale coefficients fail gate |
| Outlier target | < 15% per rarity tier (prior: 30–44%) |
| Fuzzy match threshold | 85% name similarity |
| Price trimming | 2% top and bottom from each guide before amalgamation |
| Amalgamation weighting | Dynamic: aligned guides 40/40/20 vs outlier; all aligned 33/33/33; all diverge 40/30/30 |
| Pricing authority | Anchors win by default; formula wins if criteria-rich (≥3) + guide-divergent (>0.60) multi/solo |
| Save advantage | BROAD 400 / CATEGORY 200 / SITUATIONAL 100; legacy conditional path disjoint |
| Extra damage | Raw avg preserved; priced avg = raw × condition multiplier (1.0 / 0.25 / 0.05) |
| Generic variants | Excluded in 10_generate_output (`is_generic_variant`); deduped on Name/Price/Type preferring 2024 books |
| Output format | Excel (primary) + CSV (backup) + HTML (11) |
| Task tracker | Beads (`bd`) — live board is authoritative |

---

## Current State

- **Live board is authoritative:** `bd ready` / `bd list` — do not trust this doc for issue status.
- **Next milestone:** 12k migration gate — `pricing_guide_v2-kxc` (re-audit board, go/no-go) → `pricing_guide_v2-9xv` (big-bang migration to `2026_07_12_item_list.json`). Curation decisions from `pricing_guide_v2-1mv` audit apply (exclude QftIS Concussion/Sleep grenades; keep fantasy airships/skyships; nested generics via "Multiple variations of this item exist"; commodities at official values; Renaissance cap; exclude space/modern/future sources).

---

## Prior Project Reference

Located at `/Users/ryan/opencode/TTRPG/pricing_guide_2/`
- Had 2,766 items (this project canonical: 4,837; expansion: 12,243)
- Achieved R²=0.6639, significant outlier problems
- Good reference for: criteria extraction logic, fuzzy matching, DSA/MSRP/DMPG ingestion scripts
- Do NOT copy prices or algorithm weights — start fresh

Useful prior files to reference:
- `scripts/criteria_extractor.py` — NLP prose detection patterns
- `scripts/03_fetch_external_prices.py` — External guide fetching
- `scripts/04_amalgamate_prices.py` — Amalgamation logic
- `data/raw/dsa_prices_clean.csv` — Pre-cleaned DSA data (469 items)
- `data/raw/msrp_prices_clean.csv` — Pre-cleaned MSRP data (557 items)
- `data/raw/dmpg_prices_clean.csv` — Pre-cleaned DMPG data (477 items)
