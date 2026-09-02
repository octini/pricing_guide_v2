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


## Hop C5 — family-min gated to non-amalgamated + needle-weight root fix (2026-09-02) — sej view

### Objective
Same as 913 Hop C5 — family-min reference-authority gating + Adamantine Weapon ammo exclusion. Guardrail known-good 495→5, reference 663→74, median 0.00%. Tail 1083 rows, Drow authority-correct.

### Touch set
- Same src/scripts/tests as 913 Hop C5 (see 913 progress)
- `reports/sej_913_q7b_ritual.md` Hop C5 section added (gate summary, root-fix Adamantine 0.02→1.0 +N/Drow clean, guardrail verbatim 5/1768 + 74/2533, needler remained low 8000)
- `reports/tail_attribution_sej913.csv` refreshed 1083 rows (78 intended, 7 floor, 998 variance) — Drow floor-tripwire
- `reports/price_creep_guardrail.md` regenerated (5/1768 collapsing vs 495)
- `data/processed/*.csv` re-ran 05→10 (12241 rows)

### Decisions
- As 913: gating restores authority; variant exclusion narrow; Drow 8000 floor not 14950 — authority-correct.
- Hop C5 does not change sej tripwire policy; floors remain tripwire backstop (absolute floors still exempt official/consumable).

### Blockers
- None.

### Status
Complete — hop C5 complete, 372 tests pass, guardrail collapsed, tail refreshed, ritual updated. Commit 1b7ea83 pushed.

## Hop C6 — rejected-anchor gate fix + honest tail re-bucketing (2026-09-02) — sej view

### Objective
Same as 913 Hop C6 — rejected-anchor gate (price_authority formula not protected) + battery-parity re-bucketing (4 rows) + policy disclosures. No sej policy change; tripwire remains backstop.

### Touch set
- Same src/scripts/tests as 913 Hop C6 (see 913 progress)
- `reports/tail_attribution_sej913.csv` — 4 battery-parity rows re-bucketed 78/7/998 → 82/7/994 (Cottage Chest, Mudslick Tower, Unknown Elixir, Jade Serpent Staff)
- `reports/price_creep_guardrail.md` — regenerated: Known-good 6/1768 (+ Vertebrae), Reference 75/2533, median 0.00%
- `reports/sej_913_q7b_ritual.md` — Hop C6 section added (R1 rejected-anchor, R3a 6 honest known-good + ≥8 floor + 47/59 Adamantine collateral, R3b battery 82, R3c Drow premium-exempt + battery binds anchored zero)
- `data/processed/items_validated.csv` — +3 Adamantine Vertebrae 12647→14950 final gate

### Decisions
- As 913: rejected anchors not winning; Drow winning anchors remain floor-clamped (premium-exempt per approved scope); battery parity binds anchored rows theoretically but zero amalgamated battery rows currently — flagged for future waves.
- Sej tripwire floors unchanged (still tripwire, not destination; consumable-exempt).

### Blockers
- None. R2 deferred to adoption commit.

### Status
Hop C6 complete — 373 tests pass, candidate 11942 with Vertebrae 14950, guardrail 6/1768 & 75/2533 honest, tail 82/7/994, R2 deferred.


## Adoption — wave-1.5 candidate as canonical baseline (user sign-off 2026-09-01) — 2026-09-02

### Objective
Adopt wave-1.5 candidate as canonical — tripwire floors, battery parity, family-min gated.

### Touch set
- Same output/ adoption as 913 (cp, 10, 07_validate, official_audit, 09, 10)
- Verification identical 11942, Diamond 100000, diff 16071

### Decisions
- Tripwire floors remain backstop: official+consumable exempt; 13 floor-lifts (8000/1000/200) + 2 final-gate (Vertebrae 14950, Dart 8000); Drow premium-exempt floor-clamped approved scope.

### Blockers
- None.

### Status
Adoption complete — committed f598b97, sej closed, pushed, verified. R2 regenerated.

