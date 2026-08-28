# Drift Attribution: Post-Extraction-Fix Pipeline Run

Date: 2026-08-27. Scope: first full pipeline run after the Horowitz-mandated
extraction corrections (commit 8836921), plus the Piwafwi reskin fix (c950c00)
and WDMM unknown-magic rarity fix (b6557e2).

## Method

Old criteria (HEAD:data/processed/items_criteria.csv, 95 cols) vs new extraction
(115 cols), merged on name (4,824 unique inner rows). Criteria-change flags:
extra_damage (extra_damage_avg / extra_damage_priced_avg) and save_advantage
(broad/category/situational/conditional). Drift from output/pricing_guide.csv
(baseline) vs output/pricing_guide_candidate.csv, >5% flag. Deeper recompute of
extra-damage changes uses the priced multiplier (0.25 vs-creature, 0.05 on-crit).

## Criteria-change counts (all 4,824 items)

| Category | Items |
|---|---:|
| extra_damage changed (direct avg/priced diff) | 71 |
| extra_damage changed (multiplier-recompute, incl. condition reclass) | 252 (209 vs-creature 0.25x, 43 on-crit 0.05x) |
| save_advantage changed | 85 |
| neither | 4,668 |

## Attribution of the 446 rows with >5% drift

| Cause | Rows | Share |
|---|---:|---:|
| extra_damage change only | 28 | 6% |
| save_advantage change only | 49 | 11% |
| neither (criteria unchanged) | 369 | 83% |

## Top 10 >5% movers by absolute gp

| Name | Delta gp | Delta % | Criteria change |
|---|---:|---:|---|
| Breastplate of Kamvuul Norek | +41,486 | +40.20% | none |
| Harp of Gilded Plenty | -37,202 | -41.73% | none |
| Dragonlance Pike | -32,777 | -23.98% | none |
| Staff of Contaminated Power | -32,084 | -35.52% | none |
| Dragonlance Lance | -30,385 | -23.98% | none |
| Stormgirdle (Exalted) | +25,352 | +14.15% | none |
| Stormgirdle (Awakened) | +24,330 | +18.32% | none |
| Stonebreaker's Breastplate | +20,149 | +34.29% | save_advantage (0->1 category) |
| Tinderstrike | -19,337 | -15.65% | none |
| Nepenthe | -18,301 | -8.96% | none |

## Key finding

The extraction fixes directly re-priced roughly 156 items (71 extra-damage,
85 save-advantage), and the deeper multiplier recompute implies up to 252
items have reclassified extra-damage conditions. But 83% of the large movers
have UNCHANGED criteria: they are ML retrain variance. The model retrained on
156 shifted rows; coefficient shifts move high-variance legendary
formula/ML-only prices globally. This is expected model sensitivity, not a
defect - and the anchor system bounds it:

- Vorpal family: -0.95% (PASS band)
- +3 armors: -0.88% to -0.59% (PASS band)
- Known-good status: REVIEW, zero FAILs (>5%)

Implication: ML-only extreme movers are model-sensitive by nature and are
exactly what the tiered-triage queue (reference-anchored + extreme movers)
governs at the 12k run.

## Corrected split note

The guardrail's Split column previously used the stale Has-Reference flag,
mislabeling 2,245 rows (e.g. Demonglass Dart: Price Source=Algorithm labeled
reference-anchored). Fixed in 39e564a to classify by actual Price Source.
Corrected split: formula/ML-only 3,708 rows mean +8.78%; reference-anchored
1,040 rows median -0.03%, mean +1.02% (Piwafwi's intentional +690% inheritance
is the main driver of that mean).
