# pricing_guide_v2-q7b — spell-storage valuation (scroll-parity battery floor)

## Objective
Spell-storage valuation rule (scroll-parity pricing for gems/shards/enspelled) per user ruling 2026-09-01: reusable spell batteries priced >= scroll price of stored spell (SPELL_SCROLL_PRICES 0:25…9:100000), parity not premium, material cost unpriceable.

## Touch set
- `src/criteria_extractor.py` — spell_battery_max_level 0-9 via _SPELL_GEM_NAME_LEVEL_MAP + name fallback, grenade mapping etc. (shared with 913)
- `src/pricing_engine.py` — _battery_min_for_criteria via SPELL_SCROLL_PRICES, binds formula rows in calculate_price paths (battery floor max)
- `scripts/09_enforce_floors.py` — _battery_min_for_row final gate (official exempt only, binds even amalgamated but zero amalgamated battery rows today — theoretical)
- `data/processed/items_criteria.csv` — 12241 rows, spell_battery_max_level column
- `reports/tail_attribution_sej913.csv` — 82 battery-parity intended (Cottage Chest 45000 L8 etc., Diamond 100000 L9, Ruby 45000 L8, shards)
- `output/pricing_guide_candidate.csv` — 11942 candidate (Diamond 100000, Ruby 45000, shards 69421, Obsidian 772 etc.)

## Decisions
- Battery parity binds anchored rows too (engine :1705-1711) — currently ZERO amalgamated battery rows (theoretical note recorded); all battery lifts are Algorithm formula rows.
- Parity not premium: max(price, battery) no multiplier; copy-into-spellbook learning value cancels daily-reuse advantage per user ruling.
- Zero amalgamated battery rows flagged for future waves.

## Blockers
- None.

## Status
Complete — battery floor landed via f38356f extractor + 82540c0 engine + cda8a73 floors + hop C4-6 gating; 373 tests pass; candidate mechanism verified (Diamond 100000).

## Adoption — wave-1.5 candidate as canonical baseline (user sign-off 2026-09-01) — 2026-09-02

### Objective
Adopt candidate as canonical — battery parity verified.

### Touch set
- Same adoption as 913 (cp, 10, 07_validate, official_audit, 09, 10) — canonical 11942 identical
- Commit f598b97 feat(913,q7b,sej) — 6 output files

### Decisions
- Battery parity unchanged post-adoption; audit artifacts regenerated.

### Blockers
- None.

### Status
Adoption complete — committed f598b97, q7b closed, pushed, verified 11942 identical, Diamond 100000 present. R2 regenerated.

