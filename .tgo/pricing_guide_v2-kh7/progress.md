# pricing_guide_v2-kh7 — Wave 1 Progress (hop 2 of 2)

## Objective
Calibration ritual: retrain ML, run SAFE dance (02→05→05b→06→07→09→10→mv candidate→git checkout), guardrail + anchor review, impact report for wave-1 prose criteria (temp HP, HP-max, initiative).

## Touch set
- src/criteria_extractor.py (no change — hop 1 committed)
- src/pricing_engine.py (no change — GUESS constants retained)
- data/processed/items_criteria.csv (regenerated via 02: 95→121 cols, 22 temp / 9 hp / 14 initiative carriers; restored to HEAD after dance)
- data/processed/items_priced.csv / items_variant_adjusted.csv / items_ml_priced.csv / items_validated.csv (regenerated via dance; restored)
- output/pricing_guide.csv (regenerated via 10: 4,749 rows; restored to HEAD)
- output/pricing_guide_candidate.csv (new candidate, 4,749 rows, untracked)
- reports/price_creep_guardrail.md (regenerated: median 0.00% mean 0.19% 223>5% 6>25% REVIEW 0 FAILs)
- reports/wave1_criteria_impact.md (new, this hop)
- data/processed/coefficients.json (retrain: fingerprint b22382a291023fbf R² 0.9723; gitignored)

## Decisions
- No constant tuning: GUESS values hold (TEMP_HP_RATE 40, HP_MAX_RATE 40, HP_MAX_REF 5, INIT_BONUS 300, INIT_ADV 600, freq mult 1.0/0.5/0.25/0.25). First-pass guardrail PASS (median 0.00% mean 0.19% 223>5% vs tiering 222), anchors REVIEW with 0 FAILs (max 1.68% Moon Sickle, Vorpal -1.55%). Bounded loop used 1/3 attempts.
- Attribution: only 5/223 >5% movers carry new criteria (temp 4, hp 1, init 0); 218 unexplained = ML retrain variance (same mechanism as prior 369/446). This validates no double-count and that new additive terms are not driving systemic creep.
- docs/QUALITY_GATES.md is minimal (R² + fingerprint only); guardrail/anchor/SAFE definitions taken from PROJECT_CONTEXT.md §3 + HANDOFF.md (doc wins where defined, prompt SEQUENCE otherwise; noted in report §5).
- Candidate source-alias drift (Concertina) is 1 new / 1 missing due to `translate_source` long-form vs short code; common 4748, total 4749 each.

## Blockers
- None. Fingerprint stale after final `git checkout -- output/ data/processed/` is expected (canonical restored to old 3bb3, stored coeff b223 remains new, ignored). R² PASS verified before restore (0.9723). After restore, `check_r2.py` on old data retrains to 0.9723 with 3bb3 and also PASS; either state is clean.

## Status
COMPLETE — hop 2 SAFE dance done, guardrail PASS, anchors 0 FAILs, R² 0.9723 fingerprint b223, impact report written, canonical restored. Ready to commit `reports/wave1_criteria_impact.md` (and updated guardrail) via `feat(kh7): wave-1 ML retrain + impact report + guardrail/anchor review`.
