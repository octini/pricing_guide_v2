# sej — Enforce rarity floors for ALL items (tripwire) — ritual 913+q7b+sej hop C2

## Objective
Extend 09_enforce_floors.py to clamp ALL items to RARITY_FLOORS absolute (currently only weapons/armor/shields via mundane-relative multiplier). Policy: rarity floor is a TRIPWIRE, not a destination; absolute floors enforce on all items EXCEPT (1) official/commodity-exact prices and (2) consumable-modifier items (ammunition, potion, scroll, poison). Grenades/wondrous DO clamp.

## Touch set
- src/pricing_engine.py:50-56 RARITY_FLOORS
- scripts/09_enforce_floors.py — tripwire helpers
- tests/test_floor_enforcement.py — 14 tests
- reports/sej_913_q7b_ritual.md, reports/tail_attribution_sej913.csv, reports/price_creep_guardrail.md
- output/pricing_guide_candidate.csv — 11941 rows (candidate)

## Decisions
- Tripwire absolute clamp runs after mundane-relative block; exempts official (price_source==official) and consumable-modifier (is_ammunition/is_poison/type P|SC/name potion/elixir).
- Ritual retrain 122-col matrix: R2 0.9700 fingerprint 169a3914358c0f7a PASS, guardrail median 0.00% mean 2.27% >5% 2652 >25% 1008, anchor FAIL 1 (Defender Cavalry Hammer 42% family-min intentional).
- Mechanism verification: 1 PASS (Universal Solvent 8800), 9 GAPs (Mule etc validated correct but output reskin bug masks: Mule 11508→8 via embedded reskin).
- Attribution: 1008 movers → intended-913/q7b 272, floor-tripwire 1, ml-variance 735.

## Blockers
- Embedded reskin bug in 10_generate_output.py (any "(Inner)" copies generic price) — blocks Masks, Spell Gem, etc. from reaching output.
- Needler family-min not reaching output: rule 44850 but ML/anchor 2480→floor 8000.
- Guardrail anchor FAIL intentional; no documented constants to calibrate.

## Status
Ritual complete — pipeline 03-10 retrained, guardrail, mechanism verification, tail attribution done; commit 94a64dc pushed (bd dolt + git). Canonical preserved. Gaps documented.


## Hop C4 — capped family-min + reskin uncommon-or-higher + guardrail header fix (2026-09-02)

### Objective
Same as 913 Hop C4 — capped family-min (benchmark already tier-priced) + reskin uncommon+ (22->1 Piwafwi) + guardrail scope fix. Completes post-watchdog-abort.

### Touch set
- Same files as 913 Hop C4 (see above)
- `reports/sej_913_q7b_ritual.md` Hop C4 section added (capped rationale, reskin 22->1 Amber freed, final anchor verdict FAIL 495/1768 + reference FAIL 663/2533 + median 0.00%, 13-row mechanism table)
- `reports/price_creep_guardrail.md` regenerated with corrected header (counts + reference line + scope note)

### Decisions
- As 913: capped discount-only, reskin uncommon+, header honest scope.

### Blockers
- None.

### Status
Complete — hop C4 complete, 367 tests pass, candidate 11942 correct, guardrail header fixed, ritual doc updated. Commit pending.

