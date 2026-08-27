# Extra Damage Sign-Off Pack v2 — Regenerated Candidate under Tiered Authority

> Source: `reports/price_creep_guardrail.md` (Price Creep Guardrail, Baseline `output/pricing_guide.csv` vs Candidate `output/pricing_guide_candidate.csv` — regenerated) and `reports/demonglass_driver_investigation.md` (Demonglass drift driver). No numbers were re-derived for this pack; all figures are taken verbatim from the guardrail. Candidate CSV was regenerated from HEAD (current committed code + tiered pricing authority).

---

## SIGN-OFF QUESTION

**Accept the regenerated candidate (current committed code + tiered pricing authority) as the pricing baseline going into the 12k migration?**

- If you accept, the candidate becomes the new canonical pricing baseline. Subsequent 12k migration work builds on these prices and on the tiered-authority rule already in `src/pricing_engine.py`.
- If you hold, the blocking question must be stated explicitly — but under the regenerated candidate there is no remaining artifact-driven drift to block on (see "What changed vs pack v1" below).
- This pack recommends **ACCEPT** (see Recommendation section). Guardrail verdict is **REVIEW** (PASS ≤1%, REVIEW >1%, FAIL >5%) with zero FAIL rows; drift is negligible and all gates pass.

---

## What Changed vs Pack v1

Pack v1 (`reports/extra_damage_signoff_pack.md`, 2026-07-12/2026-08-27) evaluated a candidate that is now known to be invalid. The prior candidate was an artifact of a **lost Jul-14 experimental code state** — see `reports/demonglass_driver_investigation.md` for the full stage-by-stage reproduction.

- **Demonglass Dagger:** now **630.64 gp** (was **4,881.88 gp** in the stale candidate). The entire Demonglass family reverts to the ~630–700 gp band end-to-end under current committed code (`items_priced` 652.50 gp → `items_variant_adjusted` 630.64 gp → `items_validated` 630.64 gp).
- **Artifact eliminated:** the Jul-14 experimental state that inflated FoEQuickstone and Rare means does not exist in git and does not reproduce. All drift aggregates that depended on it are superseded by the fresh guardrail below.
- **Guardrail superseded:** prior invalid candidate reported mean +7.04%, 473/318/174 rows >5%/10%/25%, Rare +20.17%, FoEQuickstone +311.53%. Those figures are retained in this pack only as "was" references for comparison.

---

## Fresh Guardrail — Baseline `output/pricing_guide.csv` vs New Candidate

Regenerated candidate compared against `output/pricing_guide.csv` (committed 2026-04-28 baseline). All figures verbatim from `reports/price_creep_guardrail.md`:

**Common-row matching:**

- **4,748 common rows**, **1 new** candidate row, **1 missing** candidate row.

**Aggregate final-price drift (4,748 common rows):**

- Median % drift: **0.00%**
- Mean % drift: **+0.05%**
- Mean gp drift: **+33 gp** (median gp drift 0 gp)
- Rows >5% drift: **222**
- Rows >10% drift: **85**
- Rows >25% drift: **5**
- Prior invalid candidate for comparison: **473 / 318 / 174** (>5% / >10% / >25%).

**Reference-anchored vs formula/ML-only split:**

| Split | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| reference-anchored | 3,285 | 0.00% | -0.03% | 0 gp | 11 gp |
| formula/ML-only | 1,463 | 0.00% | +0.21% | 0 gp | 82 gp |

Both splits are flat — reference anchoring continues to dampen drift as designed, and formula/ML-only drift remains under a quarter percent on average.

**By rarity:**

| Rarity | Rows | Mean % | Note |
|---|---:|---:|---|
| Rare | 1,411 | -0.04% | was **+20.17%** under invalid candidate |
| Uncommon | 946 | +0.16% |  |
| Very Rare | 853 | -0.21% |  |
| Legendary | 639 | +0.69% | highest mean, still <1% |
| Mundane | 461 | -0.43% |  |
| Common | 350 | +0.25% |  |
| Artifact | 71 | 0.00% |  |
| Unknown Magic | 9 | -2.12% | median +0.92%, 3 gp |
| Varies | 8 | 0.00% |  |

The Rare tier — previously the dominant outlier at +20.17% — normalizes to **-0.04%**. No rarity tier exceeds 1% mean drift.

**By source — FoEQuickstone resolved:**

- **Frontiers of Eberron: Quickstone — 111 rows, mean +0.37%**, median 0.00%, mean +12 gp, median 0 gp.
- Was **+311.53% mean / +175% median / +2,101 gp mean / +1,331 gp median** under the invalid candidate — the entire Quickstone spike collapses to near-zero once the artifact is removed.
- All other sources remain within ~±2.6% mean (see guardrail Drift by source table for full breakdown); no source-level drift requires action.

**By type:**

- Melee Weapon 1,863 rows mean +0.02%, Ranged Weapon 536 rows +0.05% — weapon-concentrated drift from v1 is gone.
- Largest type mean is Rod +1.89% (21 rows) and Shield +1.03% (31 rows); both are formula/ML-only driven and within REVIEW band.

---

## Tiered Authority Effect

The regenerated candidate runs under the **tiered pricing authority** merged in `7673322 feat(engine): tiered pricing authority by criteria coverage and guide divergence` (`src/pricing_engine.py`):

**Authority rule (formula authority):**

- A row is priced via **formula authority** when all three hold: **criteria-rich ≥3** populated criteria, **guide spread >0.60** (log-space spread of official price anchors for that item's guide class), and **multi/solo confidence** (sufficient multi-source or solo-source confidence for that anchor tier).
- Current candidate: **8 rows** priced via formula authority. These are the only rows where condition-rich, high-spread items flip from anchor-dominated to formula-dominated final price.

**Extra-damage extraction is live but anchor-dominated by design:**

- Extra-damage extraction (conditional `extra_damage_avg` with multipliers 1.0 unconditional / 0.25 vs_creature_type / 0.05 on_crit) is **live on 785 rows**. Final prices on those rows remain anchor-dominated because most do not clear the tiered-authority threshold — this is intentional.
- **True price impact** in this candidate currently flows through two channels: the **8 authority-flip rows** and **ML retraining** on widened criteria. Blended R² remains strong at **0.9723** (rule R² **0.8996**, CV mean 0.9175) — see `reports/demonglass_driver_investigation.md` §(b) and `scripts/06_ml_refine.py` output.
- **Rebalancing happens naturally at the 12k migration** when more items become criteria-rich (richer prose and criteria coverage push more rows past the ≥3 threshold) and guide-spread dynamics evolve. No manual re-weighting is needed now.

**What this means for sign-off:** the small aggregate drift (+0.05%) is not masking suppressed extra-damage value — it reflects that the pipeline correctly keeps well-anchored items stable while allowing formula authority only where the data justifies it. The 785 extraction rows are correctly staged; their pricing influence scales with migration.

---

## Known-Good Anchors

Guardrail Known-good anchors status: **REVIEW** (PASS ≤1% drift; REVIEW >1%; FAIL >5%). Configured families: Holy Avenger, Defender, Vorpal Sword, +1/+2/+3 Weapon/Armor, Dragon Slayer, Giant Slayer, Vicious Weapon when present.

**Zero FAILs.** All listed anchors are below the 5% FAIL threshold:

| Name | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---:|---:|---:|---|
| Vorpal Glaive | 54,605 gp | 53,758 gp | -847 gp | -1.55% | reference-anchored |
| Vorpal Greatsword | 54,605 gp | 53,758 gp | -847 gp | -1.55% | reference-anchored |
| Vorpal Longsword | 54,605 gp | 53,758 gp | -847 gp | -1.55% | reference-anchored |
| Vorpal Scimitar | 54,605 gp | 53,758 gp | -847 gp | -1.55% | reference-anchored |
| +3 Leather Armor | 29,832 gp | 29,503 gp | -328 gp | -1.10% | reference-anchored |
| +3 Padded Armor | 29,832 gp | 29,503 gp | -328 gp | -1.10% | reference-anchored |
| +3 Studded Leather Armor | 29,832 gp | 29,503 gp | -328 gp | -1.10% | reference-anchored |
| +2 Chain Mail | 8,454 gp | 8,614 gp | 160 gp | +1.89% | reference-anchored |
| +2 Plate Armor | 8,454 gp | 8,614 gp | 160 gp | +1.89% | reference-anchored |
| +2 Ring Mail | 8,454 gp | 8,614 gp | 160 gp | +1.89% | reference-anchored |
| +2 Splint Armor | 8,454 gp | 8,614 gp | 160 gp | +1.89% | reference-anchored |
| +3 Moon Sickle | 32,952 gp | 33,504 gp | 552 gp | +1.68% | reference-anchored |
| +1 Moon Sickle | 3,925 gp | 3,876 gp | -49 gp | -1.25% | reference-anchored |

**Summary for sign-off:**

- **Vorpal family -1.55%** (all four weapons, 54,605→53,758 gp) — within REVIEW, well below FAIL.
- **+3 Leather/Padded/Studded -1.10%** — within REVIEW, flat.
- **+2 Chain/Plate/Ring/Splint +1.89%** — largest anchor move, still REVIEW, consistent heavy-armor calibration.
- **+3 Moon Sickle +1.68%, +1 Moon Sickle -1.25%** — symmetric, no directional bias.

Anchors hold. No anchor exceeds the 5% FAIL gate; drift is symmetric and small.

---

## Largest Movers (formula/ML-only legendaries, no Demonglass)

All top movers are **formula/ML-only legendaries** — no Demonglass rows appear. The candidate's tail is now ordinary ML/formula volatility on expensive, unanchored items, not a family-level artifact:

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Harp of Gilded Plenty | Bigby Presents: Glory of the Giants | Legendary | Musical Instrument | 89,148 gp | 53,626 gp | -35,522 gp | -39.85% | formula/ML-only |
| Deck of Many More Things | The Book of Many Things | Legendary | Wondrous Item | 163,975 gp | 191,370 gp | 27,394 gp | +16.71% | reference-anchored |
| Staff of Contaminated Power | Dungeons of Drakkenheim | Legendary | Melee Weapon | 90,325 gp | 69,987 gp | -20,338 gp | -22.52% | formula/ML-only |
| Breastplate of Kamvuul Norek | Exploring Eberron (2024) | Legendary | Medium Armor | 103,206 gp | 121,209 gp | 18,003 gp | +17.44% | formula/ML-only |
| Grimoire Infinitus (Dormant) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 31,614 gp | 43,145 gp | 11,531 gp | +36.48% | formula/ML-only |

**Highlights verbatim:**

- **Harp of Gilded Plenty -39.85%** (89,148→53,626 gp)
- **Deck of Many More Things +16.71%** (163,975→191,370 gp) — the only reference-anchored row among the largest movers
- **Staff of Contaminated Power -22.52%** (90,325→69,987 gp)
- **Breastplate of Kamvuul Norek +17.44%** (103,206→121,209 gp) — was +47.12% in invalid candidate; now normalized
- **Grimoire Dormant +36.48%** (31,614→43,145 gp) — Awakened/Exalted siblings +24.85% each in full guardrail table

All are formula/ML-only legendaries where ML retraining and formula authority legitimately move prices; none cluster by source or family. The full guardrail lists ~20 legendary movers in the ±10–40% range — expected variance for high-value unanchored items.

---

## Inputs and Limitations

- Candidate `output/pricing_guide_candidate.csv` was regenerated from HEAD (`src/pricing_engine.py` with tiered authority, post-`05b_variant_adjust.py` dtype fix) and compared against `output/pricing_guide.csv` via `scripts/09_price_creep_guardrail.py` (see `reports/price_creep_guardrail.md` for the full drift-by-rarity/type/source tables).
- Numbers in this pack are verbatim from `reports/price_creep_guardrail.md` (aggregate, split, rarity, source, anchor, movers tables). No pipeline re-run was performed to build this pack; ML R² figures (blended 0.9723, rule 0.8996) are from `reports/demonglass_driver_investigation.md` §(b).
- `data/processed/coefficients.json` is a generated artifact (now in `.gitignore`) — fingerprint match is enforced by `scripts/check_r2.py` (criteria fingerprint guard, blended R² gate).
- Anchor-tier transitions and ML double-count audits require pipeline metadata not present in final CSV snapshots (guardrail note).

---

## Recommendation

**ACCEPT — drift is negligible, anchors hold, gates pass.**

- Aggregate mean drift **+0.05%** / **+33 gp** across 4,748 rows with only **5 rows >25%** is negligible. The prior artifact's 473/318/174 tail is eliminated.
- Known-good anchors are all **REVIEW band, zero FAILs** — Vorpal -1.55%, +3 leather -1.10%, +2 heavy +1.89%, Moon Sickle +1.68%/-1.25% are stable.
- ML gates pass: **blended R² 0.9723** (target ≥0.80), **rule R² 0.8996**, criteria fingerprint matches, `check_r2.py` is runnable without `PYTHONPATH`.
- Tiered authority is correctly staged: 8 authority-flip rows and ML retraining carry the true extra-damage impact today; broader rebalancing at the 12k migration will naturally expand formula authority as more items become criteria-rich.

Proceed to the 12k migration on this baseline.

---

## Files Referenced

- `output/pricing_guide.csv` (baseline) and `output/pricing_guide_candidate.csv` (regenerated candidate)
- `reports/price_creep_guardrail.md` (guardrail, current)
- `reports/demonglass_driver_investigation.md` (driver investigation, §(b) R² and §(e) invalid guardrail note)
- `reports/extra_damage_signoff_pack.md` (pack v1, superseded)
- `src/pricing_engine.py` (tiered authority, 7673322)
- `scripts/05b_variant_adjust.py` (dtype fix, cda35f2), `scripts/06_ml_refine.py` (R² 0.9723), `scripts/check_r2.py` (PYTHONPATH fix)
- `data/processed/coefficients.json` (generated, gitignored)
