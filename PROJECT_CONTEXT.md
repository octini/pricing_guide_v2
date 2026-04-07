# D&D 5e Item Pricing Guide v2 — Project Context

**Last updated:** 2026-04-06  
**Working directory:** `/Users/ryan/OpenCode/TTRPG/pricing_guide_v2/`  
**Spec:** `docs/superpowers/specs/2026-04-06-dnd-pricing-guide-design.md`

---

## Project Goal

Create an objective, data-driven pricing algorithm for all 9,422 D&D 5e items (mundane + magic) found in 5e.tools Standard Sources, Drakkenheim sources, and Eberron sources. Deliver results as Excel + CSV.

---

## Input Files

- `items-sublist-data.json` — 9,422 items (primary structured data)
- `items-sublist.md` — Prose descriptions for NLP extraction
- `~/Downloads/DMPG.pdf` — Discerning Merchant's Price Guide
- External: DSA Google Sheet, MSRP Google Sheet

---

## Architecture (8 Phases)

```
scripts/
  01_extract_items.py      → data/processed/items_master.csv
  02_extract_criteria.py   → data/processed/items_criteria.csv
  03_ingest_external.py    → data/raw/{dsa,msrp,dmpg}_prices.csv
  04_amalgamate.py         → data/processed/amalgamated_prices.csv
  05_rule_formula.py       → data/processed/rule_prices.csv + baseline R²
  06_ml_refine.py          → data/processed/coefficients.json + refined prices
  07_validate.py           → output/anomaly_report.md
  08_generate_output.py    → output/pricing_guide.xlsx + output/pricing_guide.csv

src/
  criteria_extractor.py    # All criteria extraction logic (JSON + NLP)
  pricing_engine.py        # Formula implementation
  amalgamator.py           # Weighted mean with trimming
  fuzzy_matcher.py         # 85% similarity threshold name matching
  utils.py                 # Shared helpers
```

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
| Algorithm approach | Rule-based formula + ML refinement (hybrid) |
| ML method | Gradient boosting or Ridge regression |
| R² target | ≥ 0.80 (prior project: 0.66) |
| Outlier target | < 15% per rarity tier (prior: 30–44%) |
| Fuzzy match threshold | 85% name similarity |
| Price trimming | 2% top and bottom from each guide before amalgamation |
| Amalgamation weighting | Dynamic: aligned guides 40/40/20 vs outlier; all aligned 33/33/33; all diverge 40/30/30 |
| Output format | Excel (primary) + CSV (backup) |
| Task tracker | Beads (primary) + this file (context) |

---

## Item Data Summary

- **Total items:** 9,422
- **Rarities:** rare (2571), uncommon (1710), very rare (1700), unknown magic (1209), legendary (1118), none/mundane (444), common (435), unknown (115), artifact (78), varies (42)
- **Top types:** M|XPHB (2650), M (2083), R|XPHB (1240), none (777), R (580)
- **Top sources:** XDMG (3395), MonstersOfDrakkenheim (632), TLotRR (605), FTD (555), MM (440), ExploringEberron24 (432)
- **Has official price (value field):** 446 items
- **Has attachedSpells:** 1,029 items
- **Has bonusWeapon:** 3,420 items
- **Has reqAttune:** 5,264 items
- **Has spellScrollLevel:** 985 items

---

## Quality Checkpoints

1. **After Phase 5** — @oracle reviews formula design and initial results
2. **After Phase 6** — @oracle reviews ML coefficients and R² / outlier metrics
3. **After Phase 8** — @oracle performs final spreadsheet quality review

---

## Status

- [x] Input files confirmed (9,422 items)
- [x] Spec written: `docs/superpowers/specs/2026-04-06-dnd-pricing-guide-design.md`
- [x] PROJECT_CONTEXT.md created
- [ ] Phase 1: Item extraction
- [ ] Phase 2: Criteria extraction
- [ ] Phase 3: External price ingestion
- [ ] Phase 4: Price amalgamation
- [ ] Checkpoint #1: Oracle review
- [ ] Phase 5: Rule-based formula
- [ ] Phase 6: ML coefficient refinement
- [ ] Checkpoint #2: Oracle review
- [ ] Phase 7: Validation
- [ ] Phase 8: Output generation
- [ ] Checkpoint #3: Final quality review

---

## Prior Project Reference

Located at `/Users/ryan/OpenCode/TTRPG/pricing_guide_2/`
- Had 2,766 items (this project: 9,422)
- Achieved R²=0.6639, significant outlier problems
- Good reference for: criteria extraction logic, fuzzy matching, DSA/MSRP/DMPG ingestion scripts
- Do NOT copy prices or algorithm weights — start fresh with new item set

Useful prior files to reference:
- `scripts/criteria_extractor.py` — NLP prose detection patterns
- `scripts/03_fetch_external_prices.py` — External guide fetching
- `scripts/04_amalgamate_prices.py` — Amalgamation logic
- `data/raw/dsa_prices_clean.csv` — Pre-cleaned DSA data (469 items)
- `data/raw/msrp_prices_clean.csv` — Pre-cleaned MSRP data (557 items)
- `data/raw/dmpg_prices_clean.csv` — Pre-cleaned DMPG data (477 items)
