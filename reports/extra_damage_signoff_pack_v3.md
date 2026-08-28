# Extra-Damage / Extraction Sign-off Pack v3

## SIGN-OFF QUESTION

Accept the post-extraction-fix candidate (output/pricing_guide_candidate.csv)
as the pricing baseline for the migration gate (go/no-go on the 12k big-bang)?

## What changed since pack v2

1. Piwafwi (Cloak of Elvenkind) now inherits the original's price: 514 -> 4,067 gp
   (+690%, intentional - reskin inheritance fix, commit c950c00). Piwafwi of Fire
   Resistance correctly stays standalone (distinct item: adds fire resistance).
2. Five Waterdeep: Dungeon of the Mad Mage items corrected from Uncommon to
   Unknown Magic rarity (input data says "unknown (magic)"; a WDMM-only default
   was overriding it): Dagger of Guitar Solos, Falkir's Helm of Pigheadedness,
   Jade Serpent Staff, Mind Flayer Skull, Pearl of Undead Detection (b6557e2).
3. The Horowitz-mandated extraction corrections (8836921) re-priced formula-side
   items: generic crit-only detection (on-crit damage now 0.05x, was 1.0x),
   per-source extra-damage multipliers, token-aware creature-condition
   rejection, save-advantage tier attribution hardening.

## Corrected guardrail (split fixed in 39e564a)

- Common rows: 4,748 (1 new, 1 missing)
- Median drift: 0.00% - Mean drift: +7.08% (mean gp -27)
- Rows >5%: 446 - >10%: 322 - >25%: 180
- formula/ML-only: 3,708 rows, median 0.00%, mean +8.78%
- reference-anchored: 1,040 rows, median -0.03%, mean +1.02%

## Anchor verdicts (the system held)

- Vorpal family: -0.95% (PASS)
- +3 Breastplate/Chain Shirt: -0.88% (PASS); other +3 armors -0.82% to -0.59%
- Known-good status: REVIEW - zero FAILs (>5%)

## Attribution (see drift_attribution_post_extraction_fixes.md)

Of the 446 rows >5%: 28 extra-damage corrections, 49 save-advantage tier
shifts, 369 (83%) ML retrain variance with unchanged criteria. The retrained
model (trained on ~156 shifted rows) moves high-variance legendary
formula/ML-only prices; anchors bound the variance.

## Reading the +7.08% mean

Median is 0.00%: most items did not move. The mean is dragged by (a) the
intentional Piwafwi correction, (b) justified downward corrections to
crit-only damage items, and (c) ML variance on legendary formula-only items -
the population the tiered-triage queue (reference-anchored + extreme movers)
is designed to govern at the 12k run.

## Recommendation

ACCEPT - direct corrections are justified and verified, anchors bound the
variance, and ML-sensitive tail items are governed by the triage policy at
the 12k run. Residual risk is documented, not hidden.
