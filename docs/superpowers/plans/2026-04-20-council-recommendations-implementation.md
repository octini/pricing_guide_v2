# Council Recommendations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved council recommendations so the pricing pipeline handles bonus scaling, consumable pricing, and unknown-rarity data more coherently without regressing overall pricing accuracy.

**Architecture:** Phase 1 changes stay inside the existing pricing pipeline: adjust the rule engine in `src/pricing_engine.py`, tighten data extraction in `scripts/01_extract_items.py`, then validate impact by rerunning the current pipeline and anomaly reporting scripts. Phase 2 adds measurement and audit infrastructure around the existing ML and validation stages without changing the pipeline order.

**Tech Stack:** Python 3.9+, pandas, pytest, scikit-learn, XGBoost, beads (`bd`).

---

## Executive Summary

- **Immediate implementation scope:** 3 Phase 1 tasks (`1A`, `1B`, `1C`).
- **Follow-on scope:** 2 Phase 2 tasks (`2A`, `2B`).
- **Backlog scope:** 3 Phase 3 tasks (`3A`, `3B`, `3C`).
- **Beads-sized work items:** 5 major issues total for active planning (`1A`, `1B`, `1C`, `2A`, `2B`).

### Expected Accuracy Impact

| Phase | Task | Primary metric | Expected impact |
|---|---|---|---|
| Phase 1 | 1A. Rarity-scaled additive bonuses | Overall blended R² | `+0.010` to `+0.025` |
| Phase 1 | 1B. Consumable pricing reform | Consumable outlier rate, especially legendary | `+0.003` to `+0.012` overall; larger segment improvement |
| Phase 1 | 1C. Unknown/unknown magic calibration | Coverage and calibration stability | `+0.001` to `+0.006` |
| Phase 2 | 2A. Cross-validation for ML | Generalization confidence, not headline R² | `0.000` to `+0.005`; reduced overfit risk |
| Phase 2 | 2B. Internal consistency audit | Variant coherence QA | Neutral on R²; higher trust in outputs |

### File Map

- `src/pricing_engine.py` — Rule-engine constants and multiplicative modifiers.
- `tests/test_pricing_engine.py` — Unit coverage for pricing-engine regressions.
- `scripts/01_extract_items.py` — Initial rarity normalization and item-master generation.
- `data/processed/items_master.csv` — Regenerated source-of-truth extracted item catalog.
- `scripts/06_ml_refine.py` — ML training, blending, and headline R² measurement.
- `scripts/07_validate.py` — Validation entry point and anomaly reporting.
- `scripts/07b_variant_consistency.py` — New focused audit script for within-family coherence.

---

## Phase 1: Detailed Tasks

## Task 1: 1A — Rarity-Scaled Additive Bonuses

**Files:**
- Modify: `src/pricing_engine.py:67-69` (bonus constants)
- Modify: `src/pricing_engine.py:303-305` (insert helper before `calculate_price`)
- Modify: `src/pricing_engine.py:424-437` (material armor AC bonus path)
- Modify: `src/pricing_engine.py:546-552` (weapon/AC additive path)
- Test: `tests/test_pricing_engine.py:93-174`

**Goal:** Preserve the current rare-tier anchor while scaling `+N` bonuses up or down with rarity so the same flat additive is not disproportionately huge at Common and disproportionately small at Legendary.

**Suggested beads issue:**

```bash
bd create "Scale additive weapon and armor bonuses by rarity" --type task --priority 1 --description "Replace flat +N weapon and AC additive bonuses in src/pricing_engine.py with rarity-scaled values anchored at the current rare-tier calibration. Cover both the main additive path and material armor path, add pricing-engine tests, and validate that overall blended R² does not regress." --json
```

**Success metric:**
- Rare `+N` items stay within `±1%` of current rare-tier outputs.
- Common `+N` items no longer receive rare-sized flat adders.
- Blended R² improves by at least `0.010`, or does not drop more than `0.005` while Phase 1 is still incomplete.

- [ ] **Step 1: Add failing unit tests for rarity scaling**

Append these tests to `tests/test_pricing_engine.py` after the current bonus and consumable assertions:

```python
def test_common_weapon_bonus_scales_by_rarity():
    """Common +1 weapons should use a common-scaled additive, not the rare anchor."""
    c = make_criteria(rarity="common", weapon_bonus=1)
    price = calculate_price(c)
    assert price == pytest.approx(137.5, rel=0.01)


def test_legendary_weapon_bonus_scales_by_rarity():
    """Legendary +1 weapons should scale the additive above the rare anchor."""
    c = make_criteria(rarity="legendary", weapon_bonus=1)
    price = calculate_price(c)
    assert price == pytest.approx(64625.0, rel=0.01)


def test_rare_ac_bonus_keeps_existing_anchor():
    """Rare +2 armor remains pinned to the current calibrated rare output."""
    c = make_criteria(rarity="rare", ac_bonus=2)
    price = calculate_price(c)
    assert price == pytest.approx(8000.0, rel=0.01)
```

- [ ] **Step 2: Run the targeted tests to confirm they fail first**

Run: `pytest tests/test_pricing_engine.py -k "scales_by_rarity or keeps_existing_anchor" -v`

Expected: `2` failures for the new scaling tests and `1` pass for the rare anchor after implementation is still missing.

- [ ] **Step 3: Add a shared scaling helper in `src/pricing_engine.py`**

Insert this helper immediately above `calculate_price`:

```python
RARITY_SCALING_BASE = float(RARITY_BASE_PRICES["rare"])


def get_scaled_bonus_additive(additive_table: dict[int, float], bonus: int, rarity: str) -> float:
    """Scale calibrated rare-tier adders to the current item's rarity base."""
    if bonus <= 0:
        return 0.0

    capped_bonus = min(int(bonus), 3)
    fallback_bonus = additive_table[max(additive_table)]
    anchored_additive = float(additive_table.get(capped_bonus, fallback_bonus))
    rarity_base = float(RARITY_BASE_PRICES.get(rarity, RARITY_BASE_PRICES["uncommon"]))
    return anchored_additive * (rarity_base / RARITY_SCALING_BASE)
```

- [ ] **Step 4: Replace the flat additive calls with the helper**

Update the material armor branch and the main additive branch like this:

```python
        ac_bonus = criteria.get("ac_bonus") or 0
        if ac_bonus > 0:
            material_armor_price += get_scaled_bonus_additive(
                AC_BONUS_ADDITIVE,
                ac_bonus,
                rarity,
            )
```

```python
    if weapon_bonus > 0:
        additive += get_scaled_bonus_additive(
            WEAPON_BONUS_ADDITIVE,
            weapon_bonus,
            rarity,
        )

    ac_bonus = criteria.get("ac_bonus") or 0
    if ac_bonus > 0:
        additive += get_scaled_bonus_additive(
            AC_BONUS_ADDITIVE,
            ac_bonus,
            rarity,
        )
```

- [ ] **Step 5: Re-run the pricing-engine test file**

Run: `pytest tests/test_pricing_engine.py -v`

Expected: All pricing-engine tests pass, including the three new rarity-scaling assertions.

- [ ] **Step 6: Re-run the downstream pricing pipeline and quality gate**

Run: `python3 scripts/05_rule_formula.py && python3 scripts/05b_variant_adjust.py && python3 scripts/06_ml_refine.py && python3 scripts/07_validate.py && python3 scripts/check_r2.py --baseline 0.80`

Expected:
- `scripts/06_ml_refine.py` prints a final blended R² at or above the pre-change baseline band.
- `scripts/07_validate.py` completes and rewrites `output/anomaly_report.md`.
- `scripts/check_r2.py` exits successfully.

- [ ] **Step 7: Commit**

```bash
git add src/pricing_engine.py tests/test_pricing_engine.py data/processed/items_priced.csv data/processed/items_variant_adjusted.csv data/processed/items_ml_priced.csv data/processed/items_validated.csv output/anomaly_report.md
git commit -m "fix: scale additive bonus pricing by rarity"
```

---

## Task 2: 1B — Consumable Pricing Reform

**Files:**
- Modify: `src/pricing_engine.py:810-836` (replace inline consumable logic)
- Modify: `src/pricing_engine.py:303-305` (insert helper near the new rarity-scaling helper)
- Test: `tests/test_pricing_engine.py:170-174`

**Goal:** Replace the current potion-heavy inline discount logic with one explicit consumable multiplier helper so potions, scrolls, poisons, oils, and ammunition all receive deliberate pricing treatment.

**Suggested beads issue:**

```bash
bd create "Reform consumable multipliers in pricing engine" --type task --priority 1 --description "Refactor consumable pricing in src/pricing_engine.py into a dedicated helper with explicit multipliers for potions, scrolls, poisons, oils, and ammunition. Add pricing-engine tests and validate that legendary consumable outlier rates improve in scripts/07_validate.py output." --json
```

**Success metric:**
- Legendary consumable outlier rate drops from `30.8%` to `15%` or lower.
- Potions, scrolls, and poisons have explicit code paths instead of mixed inline adjustments.
- Overall blended R² stays flat or improves.

- [ ] **Step 1: Replace the current potion-only regression test with broader consumable tests**

Replace `test_potion_consumable_discount` and append the additional assertions below:

```python
def test_potion_consumable_discount():
    """Potions use the new explicit 0.5x consumable multiplier."""
    c = make_criteria(rarity="rare", item_type_code="P")
    price = calculate_price(c)
    assert price == pytest.approx(2000.0, rel=0.01)


def test_scroll_consumable_discount():
    """Non-spell-scroll consumables with scroll type use the 0.7x multiplier."""
    c = make_criteria(rarity="very_rare", item_type_code="SC")
    price = calculate_price(c)
    assert price == pytest.approx(9450.0, rel=0.01)


def test_poison_consumable_discount():
    """Poisons use the explicit poison multiplier instead of the default 1.0 path."""
    c = make_criteria(rarity="rare", is_poison=True)
    price = calculate_price(c)
    assert price == pytest.approx(2400.0, rel=0.01)
```

- [ ] **Step 2: Run the new consumable tests and confirm they fail before the refactor**

Run: `pytest tests/test_pricing_engine.py -k "consumable_discount or poison_consumable_discount" -v`

Expected: Failures for the three new expectations because the existing logic still uses the old inline discounts.

- [ ] **Step 3: Introduce a dedicated helper for consumable modifiers**

Insert this helper near `get_scaled_bonus_additive` in `src/pricing_engine.py`:

```python
def get_consumable_modifier(criteria: dict) -> float:
    """Return the explicit consumable multiplier for the current item."""
    rarity = criteria.get("rarity", "unknown")
    item_type = str(criteria.get("item_type_code", "") or "").split("|")[0]
    item_name_lower = str(criteria.get("name", "")).lower()

    if criteria.get("is_ammunition", False):
        modifier = 0.02
        if rarity in ("very_rare", "legendary", "artifact"):
            modifier *= 0.05
        return modifier

    if item_type == "P" or any(token in item_name_lower for token in ("potion", "elixir")):
        return 0.50
    if item_type == "SC":
        return 0.70
    if criteria.get("is_poison", False):
        return 0.60
    if item_type == "G" and any(token in item_name_lower for token in ("oil", "ointment")):
        return 0.50
    return 1.0
```

- [ ] **Step 4: Replace the inline consumable section with the helper call**

Replace the current block starting at `consumable_mod = 1.0` with:

```python
    consumable_mod = get_consumable_modifier(criteria)
```

Keep the earlier spell-scroll early return in place; that logic is still authoritative for real spell scrolls with `spell_scroll_level` set.

- [ ] **Step 5: Re-run unit tests and validation**

Run: `pytest tests/test_pricing_engine.py -v && python3 scripts/05_rule_formula.py && python3 scripts/05b_variant_adjust.py && python3 scripts/06_ml_refine.py && python3 scripts/07_validate.py`

Expected:
- Pricing-engine tests pass.
- `output/anomaly_report.md` shows a lower outlier rate for consumable-heavy buckets, especially `legendary (consumable)`.

- [ ] **Step 6: Spot-check the anomaly report for the target bucket**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
report = Path('output/anomaly_report.md').read_text(encoding='utf-8')
for line in report.splitlines():
    if 'legendary (consumable)' in line.lower():
        print(line)
PY
```

Expected: The `legendary (consumable)` line shows a lower outlier rate than the pre-change `30.8%` baseline.

- [ ] **Step 7: Commit**

```bash
git add src/pricing_engine.py tests/test_pricing_engine.py data/processed/items_priced.csv data/processed/items_variant_adjusted.csv data/processed/items_ml_priced.csv data/processed/items_validated.csv output/anomaly_report.md
git commit -m "fix: apply explicit multipliers to consumable pricing"
```

---

## Task 3: 1C — Unknown / Unknown Magic Calibration

**Files:**
- Modify: `scripts/01_extract_items.py:17-29` (normalization constants)
- Modify: `scripts/01_extract_items.py:32-84` (row extraction)
- Modify: `scripts/01_extract_items.py:111-124` (replace the narrow Drow override with a general override function)
- Modify: `data/processed/items_master.csv` (regenerated output)

**Goal:** Reduce the current `147` unknown-rarity rows (`81` `unknown_magic`, `66` `unknown`) by converting obvious families into explicit rarities during extraction instead of carrying ambiguous rarity labels downstream.

**Suggested beads issue:**

```bash
bd create "Calibrate unknown and unknown-magic rarity assignments" --type task --priority 1 --description "Extend scripts/01_extract_items.py so obvious item families with unknown rarity are reassigned during extraction, then regenerate data/processed/items_master.csv and verify unknown rarity counts drop materially. Keep the existing Drow override behavior, fold it into a generalized override function, and record the post-change counts." --json
```

**Success metric:**
- `unknown_magic` count drops from `81` to `0`.
- Total `unknown` + `unknown_magic` drops from `147` to `30` or fewer.
- Regenerated `items_master.csv` feeds the downstream pipeline without schema changes.

- [ ] **Step 1: Add an extraction-time override function that covers the known families**

Replace `override_drow_rarity` with this generalized function in `scripts/01_extract_items.py`:

```python
def override_known_rarity(item: dict, rarity: str) -> str:
    name = str(item.get("name", ""))
    name_lower = name.lower()
    source = str(item.get("source", ""))
    raw_text = json.dumps(item, ensure_ascii=False)

    if "drow +1" in name_lower:
        return "rare"
    if "drow +2" in name_lower:
        return "very_rare"
    if "drow +3" in name_lower:
        return "legendary"

    if '"genericVariant": {"name": "Silvered Ammunition"' in raw_text:
        return "common"
    if '"genericVariant": {"name": "Adamantine Ammunition"' in raw_text:
        return "uncommon"
    if '"genericVariant": {"name": "Byeshk Weapon"' in raw_text:
        return "common"

    if rarity == "unknown_magic":
        if any(token in raw_text for token in ('"bonusWeapon"', '"bonusAc"', '"attachedSpells"', '"charges"', '"sentient"')):
            return "uncommon"
        if source in {"ToA", "BGDIA", "WDMM", "SKT", "PotA", "CoS"}:
            return "uncommon"

    return rarity
```

- [ ] **Step 2: Apply the override during row extraction**

Change the extraction loop so the final rarity assignment is computed per item before the row is appended:

```python
        if isinstance(rarity_raw, str):
            rarity = RARITY_NORMALIZE.get(rarity_raw.lower(), rarity_raw.lower())
        else:
            rarity = "unknown"

        rarity = override_known_rarity(item, rarity)
```

Then remove the old post-processing loop that called `override_drow_rarity`.

- [ ] **Step 3: Regenerate the item master file**

Run: `python3 scripts/01_extract_items.py`

Expected: `data/processed/items_master.csv` is rewritten and the script prints a new rarity distribution with materially fewer unknown buckets.

- [ ] **Step 4: Verify the post-change rarity counts explicitly**

Run:

```bash
python3 - <<'PY'
import pandas as pd
df = pd.read_csv('data/processed/items_master.csv')
print(df['rarity'].value_counts().to_string())
print('\nunknown_magic', (df['rarity'] == 'unknown_magic').sum())
print('unknown', (df['rarity'] == 'unknown').sum())
PY
```

Expected:
- `unknown_magic` prints `0`.
- `unknown` is `30` or lower.

- [ ] **Step 5: Re-run the dependent pipeline stages**

Run: `python3 scripts/02_extract_criteria.py && python3 scripts/04_amalgamate.py && python3 scripts/05_rule_formula.py && python3 scripts/05b_variant_adjust.py && python3 scripts/06_ml_refine.py && python3 scripts/07_validate.py`

Expected: All downstream files rebuild successfully from the regenerated `items_master.csv`.

- [ ] **Step 6: Commit**

```bash
git add scripts/01_extract_items.py data/processed/items_master.csv data/processed/items_criteria.csv data/processed/amalgamated_prices.csv data/processed/items_priced.csv data/processed/items_variant_adjusted.csv data/processed/items_ml_priced.csv data/processed/items_validated.csv output/anomaly_report.md
git commit -m "fix: calibrate extracted item rarities for unknown families"
```

---

## Phase 2: Overview Tasks

## Task 4: 2A — Cross-Validation for ML

**Files:**
- Modify: `scripts/06_ml_refine.py:9-10` (imports)
- Modify: `scripts/06_ml_refine.py:166-208` (replace single holdout validation)
- Modify: `scripts/06_ml_refine.py:343-349` (retain final blended R² output after CV)

**Goal:** Replace the one-off 80/20 split with 5-fold validation so the reported model quality is harder to overfit and easier to trust across runs.

**Suggested beads issue:**

```bash
bd create "Add five-fold cross-validation to ML refinement" --type task --priority 2 --description "Update scripts/06_ml_refine.py to report five-fold cross-validation metrics before fitting the final full-data model. Keep the existing final blended R² output, but add fold-by-fold and mean/std reporting so model quality is measured across multiple splits." --json
```

**Success metric:**
- `scripts/06_ml_refine.py` prints five fold scores plus mean and standard deviation.
- Cross-validation mean is within `0.02` of the current full-training blended R².
- Cross-validation standard deviation is `0.03` or lower.

- [ ] **Step 1: Replace the `train_test_split` import with `KFold`**

Update the import block to:

```python
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score
```

- [ ] **Step 2: Add a model factory and cross-validation helper**

Insert these functions above `main()`:

```python
def make_xgb_regressor(**kwargs):
    return XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        **kwargs,
    )


def run_cross_validation(X: pd.DataFrame, y: np.ndarray, n_splits: int = 5) -> list[float]:
    kfold = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    scores: list[float] = []

    for fold_idx, (train_idx, val_idx) in enumerate(kfold.split(X), start=1):
        model = make_xgb_regressor()
        model.fit(X.iloc[train_idx], y[train_idx])
        y_pred = model.predict(X.iloc[val_idx])
        score = r2_score(y[val_idx], y_pred)
        print(f"Fold {fold_idx} R² (log-space): {score:.4f}")
        scores.append(score)

    print(f"Cross-validation mean R² (log-space): {np.mean(scores):.4f}")
    print(f"Cross-validation std. dev.: {np.std(scores):.4f}")
    return scores
```

- [ ] **Step 3: Run cross-validation before fitting the final models on all training rows**

Replace the current index split and holdout section with:

```python
    X = build_features(train_df)
    target_prices = train_df["amalgamated_price"].combine_first(train_df["variant_price"])
    y = np.log1p(target_prices.values)

    print("\nRunning 5-fold cross-validation...")
    cv_scores = run_cross_validation(X, y, n_splits=5)

    print("\nTraining final XGBoost model on full training set...")
    model = make_xgb_regressor()
    model.fit(X, y)

    print("\nTraining quantile models on full training set...")
    model_lower = make_xgb_regressor(objective='reg:quantileerror', quantile_alpha=0.1)
    model_lower.fit(X, y)

    model_upper = make_xgb_regressor(objective='reg:quantileerror', quantile_alpha=0.9)
    model_upper.fit(X, y)
```

- [ ] **Step 4: Validate the new measurement path**

Run: `python3 scripts/06_ml_refine.py && python3 scripts/check_r2.py --baseline 0.80`

Expected:
- Five fold scores print.
- Mean and standard deviation print.
- Final blended R² still prints at the end.
- The quality gate still parses the final blended R² successfully.

---

## Task 5: 2B — Internal Consistency Audit

**Files:**
- Create: `scripts/07b_variant_consistency.py`
- Modify: `scripts/07_validate.py:17-55` (call the new audit and surface its output path)

**Goal:** Flag price families whose internal spread is suspicious even when the global anomaly detector stays quiet.

**Suggested beads issue:**

```bash
bd create "Add variant consistency audit to validation phase" --type task --priority 2 --description "Create a dedicated variant consistency audit that groups related item families such as +N armor and +N weapons, computes coefficient of variation, and writes a report that scripts/07_validate.py references during validation." --json
```

**Success metric:**
- Validation produces a machine-readable family-consistency report.
- Families with coefficient of variation above `0.60` are explicitly flagged.
- The main validation entry point prints where the consistency report was written.

- [ ] **Step 1: Create the new audit script**

Create `scripts/07b_variant_consistency.py` with this implementation:

```python
#!/usr/bin/env python3
from pathlib import Path

import pandas as pd

INPUT_CSV = Path('data/processed/items_ml_priced.csv')
OUTPUT_CSV = Path('output/variant_consistency_report.csv')


def consistency_group(row: pd.Series) -> str | None:
    if pd.notna(row.get('weapon_bonus')) and row.get('weapon_bonus', 0) > 0:
        return f"weapon+{int(row['weapon_bonus'])}"
    if pd.notna(row.get('ac_bonus')) and row.get('ac_bonus', 0) > 0:
        return f"armor+{int(row['ac_bonus'])}"

    name = str(row.get('name', '')).lower()
    if 'gleaming' in name:
        return 'gleaming-armor'
    if 'slaying' in name:
        return 'slaying-ammunition'
    return None


def main():
    df = pd.read_csv(INPUT_CSV)
    df['consistency_group'] = df.apply(consistency_group, axis=1)
    grouped = df[df['consistency_group'].notna()].copy()

    rows = []
    for group_name, group in grouped.groupby('consistency_group'):
        if len(group) < 3:
            continue
        median_price = group['final_price'].median()
        std_price = group['final_price'].std(ddof=0)
        coeff_var = 0.0 if median_price == 0 else std_price / median_price
        rows.append({
            'consistency_group': group_name,
            'count': len(group),
            'median_price': median_price,
            'std_price': std_price,
            'coefficient_of_variation': coeff_var,
            'flagged': coeff_var > 0.60,
        })

    report_df = pd.DataFrame(rows).sort_values(['flagged', 'coefficient_of_variation'], ascending=[False, False])
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    report_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Wrote {len(report_df)} consistency rows to {OUTPUT_CSV}")


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Invoke the audit from `scripts/07_validate.py`**

Add the import and execution hook:

```python
from scripts.07b_variant_consistency import main as run_variant_consistency_audit
```

```python
    run_variant_consistency_audit()
    print('\nVariant consistency report written to output/variant_consistency_report.csv')
```

If importing `scripts.07b_variant_consistency` directly is awkward in this repository layout, move the shared logic into `src/variant_consistency.py` and have both scripts import from there before wiring the same call into `scripts/07_validate.py`.

- [ ] **Step 3: Validate the audit output**

Run: `python3 scripts/07b_variant_consistency.py && python3 scripts/07_validate.py`

Expected:
- `output/variant_consistency_report.csv` exists.
- `scripts/07_validate.py` prints the report path.
- High-variance families are visible in the CSV and can be reviewed before Phase 3 work.

---

## Phase 3: Backlog

### 3A — Property-Based ML Features

- **Goal:** Feed extracted properties such as sentience, random beneficial/detrimental counts, material markers, and attached-spell richness into the ML feature matrix.
- **Likely files:** `src/criteria_extractor.py`, `src/pricing_engine.py`, `scripts/06_ml_refine.py`.
- **Entry condition:** Phase 1 and 2 are stable and cross-validation mean R² has plateaued below the desired target.
- **Success metric:** Cross-validation mean R² improves by at least `0.010` without widening fold variance.

### 3B — Source-Specific Weights

- **Goal:** Weight DSA, MSRP, and DMPG differently based on historical residual error instead of simple equal aggregation.
- **Likely files:** `src/amalgamator.py`, `scripts/04_amalgamate.py`, `scripts/06_ml_refine.py`.
- **Entry condition:** The internal consistency audit shows stable family behavior and Phase 1 outlier reduction has landed.
- **Success metric:** Multi-source items gain a measurable R² improvement over the equal-weight baseline.

### 3C — Interactive Manual Review Tool

- **Goal:** Add an item-by-item review surface for pricing outliers, family inconsistencies, and unknown-family edge cases.
- **Likely files:** `scripts/11_generate_html.py`, `output/`, and a new lightweight review UI directory.
- **Entry condition:** The Phase 2 audit outputs are trustworthy enough to drive manual review queues.
- **Success metric:** Reviewers can filter by anomaly type, inspect the item inputs, and export accepted overrides for later pipeline runs.

---

## Success Metrics by Phase

### Phase 1

- Overall blended R² improves by `0.014` to `0.043` cumulatively, or at minimum does not regress below the current quality gate.
- `legendary (consumable)` outlier rate is `15%` or lower.
- Unknown rarity rows fall from `147` to `30` or fewer, with `unknown_magic` eliminated.

### Phase 2

- Five-fold cross-validation mean and final blended R² remain within `0.02` of each other.
- Cross-validation standard deviation is `0.03` or lower.
- Variant consistency report flags only a small, reviewable set of families rather than broad systemic spread.

### Phase 3

- Any Phase 3 work must beat the Phase 2 cross-validation baseline, not just the single-run headline R².
- Manual review throughput should increase without introducing a second source of truth outside the pipeline inputs.

---

## Rollback Plan

1. **Rollback 1A only:** revert the `get_scaled_bonus_additive` helper and restore the direct `WEAPON_BONUS_ADDITIVE` / `AC_BONUS_ADDITIVE` lookups in `src/pricing_engine.py`.
2. **Rollback 1B only:** keep the helper scaffolding if desired, but restore `consumable_mod` to the current inline logic block and re-run `scripts/06_ml_refine.py` plus `scripts/07_validate.py`.
3. **Rollback 1C only:** revert `scripts/01_extract_items.py` and regenerate `data/processed/items_master.csv` from the previous extraction logic.
4. **Rollback 2A only:** restore `train_test_split` validation in `scripts/06_ml_refine.py` and keep the final blended R² output unchanged so `scripts/check_r2.py` continues to parse it.
5. **Rollback 2B only:** remove `scripts/07b_variant_consistency.py` and the call site in `scripts/07_validate.py`; this audit is additive and can be backed out without touching model outputs.
6. **Operational rollback command:** after reverting the affected commit, run `python3 scripts/01_extract_items.py && python3 scripts/02_extract_criteria.py && python3 scripts/04_amalgamate.py && python3 scripts/05_rule_formula.py && python3 scripts/05b_variant_adjust.py && python3 scripts/06_ml_refine.py && python3 scripts/07_validate.py` to restore all derived files to a coherent state.

---

## Self-Review

- **Placeholder scan:** This plan contains no `TBD`, `TODO`, or unresolved placeholder sections.
- **Coverage check:** All council recommendations are covered: `1A`, `1B`, `1C`, `2A`, `2B`, `3A`, `3B`, and `3C`.
- **Path check:** Every referenced existing file path is present in the repository; new work is confined to `scripts/07b_variant_consistency.py`.
- **Execution model:** Each active recommendation maps cleanly to one beads issue and one independent implementation task.
