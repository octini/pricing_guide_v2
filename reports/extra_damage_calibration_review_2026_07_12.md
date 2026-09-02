# Extra Damage Calibration Review — Current Canonical Candidate

## Scope

This review uses current canonical inputs only. It does **not** accept or publish a full pricing run and does **not** migrate the 2026 list. The candidate CSV was generated in a temporary worktree and copied to `output/pricing_guide_candidate.csv` solely for comparison against the committed baseline `output/pricing_guide.csv`.

Related reports:

- `reports/extra_damage_impact_2026_07_12.md` — extraction/formula-exposure report for `extra_damage_avg`.
- `reports/price_creep_guardrail.md` — realized final-price guardrail report comparing baseline vs candidate output CSVs.

## Implemented calibration model under review

- Raw `extra_damage_avg` remains the truthful dice average.
- New metadata separates conditionality from raw damage:
  - `extra_damage_condition`
  - `extra_damage_condition_detail`
  - `extra_damage_multiplier`
- Pricing formula applies the multiplier only to the extra-damage additive channel.
- Current first-pass pricing multipliers:
  - unconditional: `1.0`
  - creature-type conditional: `0.25`
  - crit-only: `0.05`
- ML/composite features still see raw `extra_damage_avg`; this is intentional for now but remains a possible double-count channel to evaluate before sign-off.

## Headline guardrail results after conditional weighting

From `reports/price_creep_guardrail.md`:

- Common rows: 4,748
- New candidate rows: 1
- Missing candidate rows: 1
- Median drift: 0.00%
- Mean drift: 7.04%
- Rows >5% drift: 473
- Rows >10% drift: 318
- Rows >25% drift: 174
- Reference-anchored mean drift: 9.83%
- Formula/ML-only mean drift: 0.79%
- Known-good status: **REVIEW**

From `reports/extra_damage_impact_2026_07_12.md`:

- Changed current canonical rows: 331
- Old raw `extra_damage_avg` total: 3,680.53
- New raw `extra_damage_avg` total: 5,641.00
- Old weighted `extra_damage_avg` total: 3,680.53
- New weighted `extra_damage_avg` total: 4,321.65
- Direct weighted formula exposure: +870,562 gp

## Root cause: Quickstone / Stonebane

Quickstone remains the largest source-level issue after conditional weighting:

- Quickstone common rows: 111
- Median drift: +175.00%
- Mean drift: +311.53%

Examples:

| Item | Baseline | Candidate | Drift | Rarity/type | Price source | Reference flag | Extracted extra damage |
|---|---:|---:|---:|---|---|---|---|
| Stonebane Dagger | 697 gp | 1,918 gp | +175.0% | uncommon melee weapon | Algorithm | True | `1d6`, `vs_creature_type=aberration`, multiplier `0.25` |
| Stonebane Longsword | 747 gp | 2,054 gp | +175.0% | uncommon melee weapon | Algorithm | True | `1d6`, `vs_creature_type=aberration`, multiplier `0.25` |
| Stonebane Maul | 798 gp | 2,196 gp | +175.0% | uncommon melee weapon | Algorithm | True | `1d6`, `vs_creature_type=aberration`, multiplier `0.25` |

Interpretation:

- Stonebane movement is caused by the newly extracted `extra_damage_avg` entering the rule-price additive channel.
- The formula contribution after weighting is about `1,500 gp * 3.5 * 0.25 = 1,312.5 gp`, which explains the ~+1.2k–1.4k gp movement from baseline prices around 700–800 gp.
- These rows show `Has Reference=True` in output, but the final `Price Source` is still `Algorithm`, so they are not being protected like high-confidence amalgamated rows.
- This is not a raw-extraction false positive: the Stonebane prose really says the target takes extra 1d6 damage against Aberrations.

## Root cause: Quickstone / Demonglass

The largest percent movers now come from Demonglass, not Stonebane:

| Item | Baseline | Candidate | Drift | Rarity/type | Price source | Reference flag | Extracted extra damage |
|---|---:|---:|---:|---|---|---|---|
| Demonglass Dart | 615 gp | 4,765 gp | +675.2% | rare ranged weapon | Algorithm | True | none |
| Demonglass Longsword | 668 gp | 5,156 gp | +671.7% | rare melee weapon | Algorithm | True | none |

Interpretation:

- Demonglass movement is **not** caused by `extra_damage_avg`; extraction remains zero.
- Demonglass items have `bonusWeapon=+1`, rare rarity, attunement, and generic-variant/reference metadata, but are still final-output `Price Source=Algorithm`.
- The movement appears to come from candidate regeneration interacting with existing rule/ML/variant/reference mechanics, not from the extra-damage calibration itself.
- This means `pricing_guide_v2-r1o` cannot be signed off based only on extra-damage damping; the candidate pipeline output also needs a broader guardrail review of reference-flagged algorithm rows.

## Known-good anchors

The guardrail known-good section is now type-aware and includes Vorpal variants. Current status is **REVIEW**, not PASS.

Examples driving review-level drift:

- Vorpal Glaive / Greatsword / Longsword / Scimitar: about -1.10%.
- +2 armor variants: about +1.66%.
- +1 Moon Sickle: about -1.70%.

These are review-level drifts, not catastrophic, but they confirm full pricing should remain gated.

## Options considered

1. **Keep truthful extraction and conditional multiplier; accept current candidate**
   - Pros: extraction is semantically correct; conditional damage no longer receives full unconditional valuation.
   - Cons: guardrail remains REVIEW, Quickstone median/mean drift remains high, Demonglass movement is unresolved.

2. **Further dampen creature-type conditional multiplier**
   - Pros: reduces Stonebane/Dragon Slayer/Giant Slayer/Corpse Slayer formula exposure.
   - Cons: does not fix Demonglass; risks under-valuing real slayer mechanics; multiplier would become arbitrary without more calibration.

3. **Suppress extra-damage additive for reference-flagged algorithm rows**
   - Pros: directly targets reference-flagged known-good price creep.
   - Cons: `Has Reference=True` currently includes rows whose final source is still Algorithm; semantics need clarification before using it as a hard suppressor.

4. **Add a separate “reference-protected algorithm row” policy/gate**
   - Pros: addresses both Stonebane and Demonglass class of problems; keeps extraction truthful; avoids overfitting extra damage alone.
   - Cons: requires explicit policy and implementation/testing in pricing pipeline.

5. **Defer pricing use while keeping extraction/reporting**
   - Pros: safest for avoiding price creep; keeps newly extracted fields available for review.
   - Cons: delays realizing value from correct extraction.

## Recommendation

Do **not** sign off the candidate pricing run yet.

Recommended next step: create/perform a narrowly scoped calibration task for reference-flagged algorithm rows before full pricing, with special focus on Quickstone/Demonglass and Stonebane. Keep raw `extra_damage_avg` and condition metadata, but do not accept full candidate output until either:

1. reference-flagged algorithm rows are protected or calibrated, and
2. `reports/price_creep_guardrail.md` returns PASS or an explicitly accepted REVIEW with documented exceptions.

The current first-pass creature-type multiplier (`0.25`) is directionally useful but insufficient as a standalone approval mechanism.
