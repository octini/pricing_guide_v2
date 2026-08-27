# Demonglass Drift Driver Investigation

Date: 2026-08-27
Investigator: Dylan (TGO)
Scope: `output/pricing_guide_candidate.csv` drift for Demonglass family vs `output/pricing_guide.csv` baseline

## (a) Verdict

**Candidate CSV is an artifact of a lost Jul-14 experimental code state; current committed code prices Demonglass at ~630 gp with no drift. Do not sign off on drift; regenerate the candidate before any further guardrail evaluation.**

Empirical reproduction across every committed stage prices `Demonglass Dagger` at ~630 gp (items_priced rule_price 652.5 gp → variant-adjusted 630.64 gp → validated final 630.64 gp). The candidate's 4,881.88 gp does not reproduce under current `src/pricing_engine.py` (HEAD 2026-07-14 17:04:48) or any committed `data/processed` stage. Historical `src/pricing_engine.py.bak` (2026-04-10 02:19:57) and `.orig` (2026-04-10 20:11:52) corroborate sizable intervening refactors (extra-damage conditional multipliers, artifact tier system, mundane base costs, `is_commodity_exact_price_candidate` anchoring), but the precise Jul-14 experimental state that produced the candidate CSV is not in git and cannot be reconstructed. Recommendation: regenerate `output/pricing_guide_candidate.csv` from HEAD, then re-run `reports/price_creep_guardrail.md` comparison; treat all drift aggregates derived from the current candidate as invalid until then.

## (b) Stage-by-Stage Price Table — Demonglass Dagger + 2 Variants

All prices in gp. `blend R² (log-space)` from `06_ml_refine.py` post-fix: **CV mean 0.9175 (std 0.0149, folds 0.9451/0.9007/0.9140/0.9170/0.9105), final blended R² 0.9723** (target ≥0.80).

| Stage | Artifact | Demonglass Dagger | Demonglass Battleaxe | Demonglass Greatsword |
|---|---|---:|---:|---:|
| **Baseline** `output/pricing_guide.csv` (committed 2026-04-28) | — | 630.64 | 671.37 | 700.76 |
| **Candidate** `output/pricing_guide_candidate.csv` (stale, Jul-14 experimental) | artifact | **4,881.88** | **5,179.83** | **5,394.87** |
| `data/processed/items_priced.csv` `rule_price` (fresh, 02) | pre-fix = post-fix | 652.50 | 652.50 | 652.50 |
| `data/processed/items_variant_adjusted.csv` `rule_price` (=`variant_adjusted_price`, `price_source=rule+variant`) | pre-fix **stale** (2026-07-10 21:51, 05b crash left this stage not regenerated) | 630.64* | 671.37* | 700.76* |
| `data/processed/items_variant_adjusted.csv` `rule_price` (=`variant_adjusted_price`) | **post-fix fresh** (2026-08-27, after dtype fix) | **630.64** | **671.37** | **700.76** |
| `data/processed/items_ml_priced.csv` `ml_price` / `final_price` | post-fix fresh | ml 949.18 → final **630.64** | ml 949.18 → final **671.37** | ml 949.18 → final **700.76** |
| `data/processed/items_validated.csv` `final_price` (=`rule_price`, via `09_enforce_floors.py`) | post-fix fresh | **630.64** | **671.37** | **700.76** |

`*` Pre-fix stale variant file coincidentally held the same family-spaced values (rule blended 0.5× rule + 0.5× variant) because the prior successful Jul-10 run used identical variant logic; the bug only prevented *refresh* after subsequent `items_priced.csv` changes. Post-fix values were re-derived and remain in the ~600–700 gp band end-to-end.

Collapsed Dagger family detail (post-fix fresh variant stage):
- `variant_base_price` (Demonglass Weapon generic) 658.88 gp, `variant_adjustment` −0.2534, `variant_price` 608.79 gp → blended `variant_adjusted_price` 630.64 gp.
- All three variants share rare / M|XPHB / `genericVariant: Demonglass Weapon` / `is_focus=False`; `has_reference_source=True` after variant stage.

No drift is observed through any committed transform. The only mover is the candidate CSV itself.

## (c) 05b Crash Bug and Fix

**Bug:** `scripts/05b_variant_adjust.py` crashed at line 169 with `pandas.errors.LossySetitemError` / `TypeError: Invalid value '[np.float64(...)]' for dtype 'float64'` during `items_with_variants.loc[has_variant, 'rule_price'] = items_with_variants.loc[has_variant, 'variant_adjusted_price']`.

Root cause was dtype incompatibility in two places:

1. **Initialization (line 159):** `items_with_variants['variant_adjusted_price'] = None` created an `object`-dtype column (pandas stores `None` as object). Per-row `.loc[idx, 'variant_adjusted_price'] = final_variant_price` then inserted boxed `np.float64` objects, not a float64 series.

2. **Bulk assignment (line 169):** assigning an object-dtype series into `rule_price` (float64) triggered `coerce_to_target_dtype` failure. Pandas refused to coerce boxed floats via `np_can_hold_element`.

This left `data/processed/items_variant_adjusted.csv` stale — every rerun of 05b failed, so downstream 06/07/09 operated on the Jul-10 file.

**Fix (minimal diff, `fix(variants): resolve dtype crash in variant adjustment stage`):**

```diff
- items_with_variants['variant_adjusted_price'] = None
+ items_with_variants['variant_adjusted_price'] = float('nan')
```
Initializes the column as `float64` NaN, so per-row inserts stay float64.

```diff
- items_with_variants.loc[has_variant, 'rule_price'] = items_with_variants.loc[has_variant, 'variant_adjusted_price']
+ items_with_variants.loc[has_variant, 'rule_price'] = items_with_variants.loc[has_variant, 'variant_adjusted_price'].astype(float)
```
Forces float64 on the bulk copy, matching `rule_price` dtype.

Post-fix: `python3 scripts/05b_variant_adjust.py` completes cleanly (4837 rows, 1663 blended, 41 skipped official, 2942 variant mappings), followed by `06_ml_refine.py` (see R² above), `07_validate.py`, `09_enforce_floors.py`. Verified end-to-end Demonglass prices remain ~630–700 gp.

## (d) Side-Findings Requiring Authority-Policy Verification

### 1. Stale staged `save_advantage` criteria

`git show HEAD:data/processed/items_criteria.csv` vs fresh `data/processed/items_criteria.csv` after `02` extraction shows `save_advantage` extraction is stale in the index:

- Fresh: `save_advantage` = `['saving throws']` for Demonglass family and many others (generic save advantage prose parsed).
- HEAD staged: `save_advantage` = `[]` for those rows.

Diff count (post-fix): **85 rows** where `save_advantage` string differs (`staged != current`). Prior triage noted 95 rows affected; post-fix count is 85 (sampling matches: `Belt of Dwarvenkind`, `Bracers of Celerity`, `Demonglass Battleaxe` all show `[] → ['saving throws']`; converse rows like `Dancing Monkey Fruit` `['dexterity'] → []` also present, reflecting broadened extraction). Pricing impact under current engine is minor (save advantage value is modest), but correctness of staged `items_criteria.csv` must be verified and refreshed under the authority-policy work; do **not** carry the staged file forward.

### 2. `is_focus` spurious flag on Demonglass — not reproduced

Prior investigation flagged `is_focus=True` on Demonglass with `is_focus_prose=False` as suspect. Fresh comparison vs HEAD finds:

- `is_focus` diff vs HEAD: **0 rows**.
- Current and staged both: `Demonglass Dagger` `is_focus=False, is_focus_prose=False`; all Demonglass melee/ranged variants `False/False`; only `Demonglass Wooden Staff` is `True/True` (legitimate, consistent in both).
- **Verdict: not reproduced.** Mark earlier spurious-`is_focus` report as resolved-pending-recheck; no action needed except to re-verify `criteria_extractor` focus logic during authority-policy work to ensure no regression.

Both items need verification during the authority-policy work but do not affect the Demonglass verdict.

## (e) Guardrail Mean +7% Figure — Invalid Until Candidate Regeneration

`reports/price_creep_guardrail.md` (generated from current candidate) reports:

- Aggregate: median 0.00%, **mean +7.04%**, median 0 gp, mean −7 gp, 473 rows >5%, 318 >10%, 174 >25%.
- By rarity, Rare mean +20.17% (`−116 gp`) is dominated by….
- By source, **Frontiers of Eberron: Quickstone +311.53% mean, +175% median, +1,331 gp median / +2,101 gp mean across 111 rows** — exactly the Demonglass family and its siblings.

That FoEQuickstone spike *is* the candidate-artifact-driven drift. Baseline median for FoEQuickstone rare weapons is ~650 gp; candidate inflates to ~5k gp, producing the entire guardrail tail. Since the candidate is not reproducible, **the +7.04% mean / +9.83% reference-anchored / +20.17% rare figures are all invalid.** They reflect the lost Jul-14 experimental engine state, not a committed pricing change.

After candidate regeneration the guardrail must be re-rendered. Expected outcome under current code: FoEQuickstone source drift collapses to ~0%, aggregate mean drifts to ~0–1%, rare mean normalizes. Do not use the current `price_creep_guardrail.md` for sign-off.

---

### Reproduction Commands (post-fix)

```bash
python3 scripts/05b_variant_adjust.py   # now clean: 4837 rows, 1663 blended
python3 scripts/06_ml_refine.py         # CV mean R² 0.9175, final 0.9723
python3 scripts/07_validate.py
python3 scripts/09_enforce_floors.py
grep "Demonglass Dagger" data/processed/items_variant_adjusted.csv data/processed/items_validated.csv
# expected: 630.64 gp in both, ~600–700 gp family band
```

### Files Referenced

- `src/pricing_engine.py`, `src/pricing_engine.py.bak`, `src/pricing_engine.py.orig`
- `scripts/05b_variant_adjust.py` (fixed lines 159, 169)
- `data/processed/items_priced.csv`, `items_variant_adjusted.csv`, `items_ml_priced.csv`, `items_validated.csv`, `items_criteria.csv`
- `output/pricing_guide.csv`, `output/pricing_guide_candidate.csv`, `output/official_price_anchor_audit.csv`, `output/anomaly_report.md`, `output/variant_consistency_report.csv`
- `reports/price_creep_guardrail.md` (invalid until regeneration)
