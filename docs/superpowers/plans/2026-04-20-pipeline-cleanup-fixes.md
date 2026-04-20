# Pipeline Cleanup - All Remaining Fixes Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all 11 remaining medium and low-priority bugs from the pipeline audit.

**Architecture:** 8 independent fixes across 8 files. Each fix is isolated and can be executed in parallel.

**Tech Stack:** Python 3.9+, pandas, XGBoost

---

## Task 1: Consolidate RARITY_MEDIANS Constant

**Files:**
- Create: `src/constants.py`
- Modify: `src/amalgamator.py:10`, `src/pricing_engine.py:897`

**Issue:** `RARITY_MEDIANS` is duplicated in two files with identical values. Maintenance risk.

- [ ] **Step 1: Create src/constants.py**

```python
"""Shared constants for the pricing pipeline."""

# Empirical median prices by rarity (from external sources)
RARITY_MEDIANS = {
    'common': 100,
    'uncommon': 500,
    'rare': 4000,
    'very_rare': 14000,
    'legendary': 47000,
    'artifact': 185000,
}

# Condition immunity values (gp premium per condition)
CONDITION_IMMUNITY_VALUES = {
    'blinded': 400,
    'charmed': 400,
    'deafened': 400,
    'frightened': 400,
    'grappled': 400,
    'paralyzed': 400,
    'petrified': 400,
    'poisoned': 400,
    'prone': 400,
    'restrained': 400,
    'stunned': 400,
    'unconscious': 400,
}
```

- [ ] **Step 2: Update amalgamator.py**

```python
# Remove line 10 (RARITY_MEDIANS definition)
# Add at top with other imports:
from src.constants import RARITY_MEDIANS
```

- [ ] **Step 3: Update pricing_engine.py**

```python
# Remove line 897 (RARITY_MEDIANS definition)
# Add at top with other imports:
from src.constants import RARITY_MEDIANS, CONDITION_IMMUNITY_VALUES

# Remove line 69 (CONDITION_IMMUNITY_VALUES definition)
# Update references to use imported constant
```

- [ ] **Step 4: Test**

```bash
python3 scripts/04_amalgamate.py && python3 scripts/05_rule_formula.py
```

Expected: No errors, prices unchanged

- [ ] **Step 5: Commit**

```bash
git add src/constants.py src/amalgamator.py src/pricing_engine.py
git commit -m "refactor: consolidate RARITY_MEDIANS and CONDITION_IMMUNITY_VALUES to constants.py"
```

---

## Task 2: Fix Misleading "rule+amalgamated" Label

**Files:**
- Modify: `src/pricing_engine.py:930`

**Issue:** Source label says "rule+amalgamated" but price is pure rule-based (no blending).

- [ ] **Step 1: Find the code**

Around line 930 in `calculate_price_with_outlier_check`:
```python
# Current (MISLEADING):
if pd.notna(amalgamated_price):
    return rule_price, 'rule+amalgamated', confidence
```

- [ ] **Step 2: Fix the label**

```python
# Change to:
if pd.notna(amalgamated_price):
    # Note: amalgamated price is used for R² comparison only, not blended
    return rule_price, 'rule', confidence
```

- [ ] **Step 3: Test**

```bash
python3 scripts/05_rule_formula.py
```

Check output CSV - source column should say "rule" not "rule+amalgamated"

- [ ] **Step 4: Commit**

```bash
git add src/pricing_engine.py
git commit -m "fix: misleading 'rule+amalgamated' source label (price is pure rule, not blended)"
```

---

## Task 3: Fix Fragile Index Check in Validation

**Files:**
- Modify: `scripts/07_validate.py:46-53`

**Issue:** Uses `idx < len(df)` which assumes integer RangeIndex. Should use `idx in df.index`.

- [ ] **Step 1: Find the code**

```python
# Current (FRAGILE):
for idx in results['outliers'].index:
    if idx < len(df):  # Wrong for non-RangeIndex
        df.loc[idx, 'is_outlier'] = True
```

- [ ] **Step 2: Fix the check**

```python
# Change to:
for idx in results['outliers'].index:
    if idx in df.index:  # Works for any index type
        df.loc[idx, 'is_outlier'] = True
```

- [ ] **Step 3: Test**

```bash
python3 scripts/07_validate.py
```

Expected: No errors, outliers flagged correctly

- [ ] **Step 4: Commit**

```bash
git add scripts/07_validate.py
git commit -m "fix: fragile index check in validation (use 'in df.index' not '< len(df)')"
```

---

## Task 4: Move import re to Module Level

**Files:**
- Modify: `src/pricing_engine.py:369`

**Issue:** `import re` inside `calculate_price()` function (called per-item). Minor perf issue.

- [ ] **Step 1: Find the code**

```python
def calculate_price(item_data, ...):
    import re  # Inside function
    # ... uses re.search()
```

- [ ] **Step 2: Move to top**

```python
# At top of file with other imports:
import re

# In calculate_price(), remove the import line
```

- [ ] **Step 3: Test**

```bash
python3 scripts/05_rule_formula.py
```

Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add src/pricing_engine.py
git commit -m "perf: move 'import re' to module level (was inside per-item function)"
```

---

## Task 5: Remove StandardScaler from ML Pipeline

**Files:**
- Modify: `scripts/06_ml_refine.py`

**Issue:** StandardScaler is unnecessary for XGBoost (tree-based model doesn't need feature scaling).

- [ ] **Step 1: Find the code**

Around lines 100-150:
```python
from sklearn.preprocessing import StandardScaler

# ...
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
# ... uses X_train_scaled in training
```

- [ ] **Step 2: Remove scaling**

```python
# Remove: from sklearn.preprocessing import StandardScaler
# Remove: scaler = StandardScaler()
# Remove: scaler.fit_transform() calls
# Use X_train directly instead of X_train_scaled
```

- [ ] **Step 3: Test**

```bash
python3 scripts/06_ml_refine.py
```

Expected: R² similar (±0.01), no errors

- [ ] **Step 4: Commit**

```bash
git add scripts/06_ml_refine.py
git commit -m "refactor: remove StandardScaler (unnecessary for XGBoost tree-based model)"
```

---

## Task 6: Fix Indentation in ML Script

**Files:**
- Modify: `scripts/06_ml_refine.py:261`

**Issue:** Cosmetic indentation inconsistency.

- [ ] **Step 1: Find the code**

```python
# Line 261 - price_high is dedented relative to surrounding code
price_low = np.maximum(...)
    price_high = np.maximum(...)  # Wrong indentation
```

- [ ] **Step 2: Fix indentation**

```python
price_low = np.maximum(...)
price_high = np.maximum(...)  # Aligned with price_low
```

- [ ] **Step 3: Test**

```bash
python3 scripts/06_ml_refine.py
```

Expected: No syntax errors

- [ ] **Step 4: Commit**

```bash
git add scripts/06_ml_refine.py
git commit -m "style: fix indentation inconsistency line 261"
```

---

## Task 7: Document Price Band Override

**Files:**
- Modify: `scripts/09_enforce_floors.py:276-281`

**Issue:** ML quantile-based price bands replaced with flat ±20%. Should document why.

- [ ] **Step 1: Find the code**

```python
# Lines 276-281 - overwrites ML quantile bands
df['price_low'] = df['final_price'] * 0.8
df['price_high'] = df['final_price'] * 1.2
```

- [ ] **Step 2: Add comment**

```python
# Override ML quantile-based price bands with flat ±20% range.
# Rationale: ML quantile bounds were too wide for common items (>50% range)
# and too narrow for legendary items (<10% range). Flat ±20% provides
# consistent uncertainty bands across all rarities for the HTML UI.
df['price_low'] = df['final_price'] * 0.8
df['price_high'] = df['final_price'] * 1.2
```

- [ ] **Step 3: Test**

```bash
python3 scripts/09_enforce_floors.py
```

Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add scripts/09_enforce_floors.py
git commit -m "docs: add rationale for flat ±20% price bands (override ML quantiles)"
```

---

## Task 8: Fix Docstring Phase Number

**Files:**
- Modify: `scripts/10_generate_output.py:2`

**Issue:** Docstring says "Phase 8" but this is script 10.

- [ ] **Step 1: Find the code**

```python
"""
Phase 8: Generate Output
# ...
"""
```

- [ ] **Step 2: Fix the docstring**

```python
"""
Phase 10: Generate Output
Generates Excel (multi-sheet) and CSV output from validated data.
# ...
"""
```

- [ ] **Step 3: Test**

```bash
python3 scripts/10_generate_output.py
```

Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add scripts/10_generate_output.py
git commit -m "docs: fix docstring phase number (8 → 10)"
```

---

## Task 9: Fix Boolean Parsing Edge Case

**Files:**
- Modify: `scripts/05_rule_formula.py:78`

**Issue:** `bool(c.get(bool_col))` treats string `"False"` as truthy.

- [ ] **Step 1: Find the code**

```python
# Line 78:
item_bools = {bool_col: bool(c.get(bool_col)) for bool_col in BOOL_COLS}
```

- [ ] **Step 2: Fix parsing**

```python
def parse_bool(val):
    """Parse boolean from CSV, handling string 'False' correctly."""
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ('true', '1', 'yes')
    return bool(val)

item_bools = {bool_col: parse_bool(c.get(bool_col)) for bool_col in BOOL_COLS}
```

- [ ] **Step 3: Test**

```bash
python3 scripts/05_rule_formula.py
```

Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add scripts/05_rule_formula.py
git commit -m "fix: boolean parsing treats string 'False' as false (not truthy)"
```

---

## Task 10: Fix One-Sided Outlier Detection

**Files:**
- Modify: `src/amalgamator.py:53`

**Issue:** Only catches prices that are too HIGH (>5x median), not too LOW (<1/5x median).

- [ ] **Step 1: Find the code**

```python
# Line 53:
if price > median_price * outlier_threshold:
    return (True, "single-source-outlier")
```

- [ ] **Step 2: Add lower bound check**

```python
# Check both high and low outliers:
if price > median_price * outlier_threshold:
    return (True, "single-source-outlier-high")
if price < median_price / outlier_threshold:
    return (True, "single-source-outlier-low")
```

- [ ] **Step 3: Test**

```bash
python3 scripts/04_amalgamate.py
```

Check anomaly report for new low outliers

- [ ] **Step 4: Commit**

```bash
git add src/amalgamator.py
git commit -m "fix: outlier detection now catches both high (>5x) and low (<1/5x) outliers"
```

---

## Task 11: Regenerate Full Pipeline and Verify

**Files:**
- All pipeline outputs

- [ ] **Step 1: Run full pipeline**

```bash
python3 scripts/04_amalgamate.py && \
python3 scripts/05_rule_formula.py && \
python3 scripts/05b_variant_adjust.py && \
python3 scripts/06_ml_refine.py && \
python3 scripts/07_validate.py && \
python3 scripts/09_enforce_floors.py && \
python3 scripts/10_generate_output.py && \
python3 scripts/11_generate_html.py
```

Expected: All scripts complete without errors

- [ ] **Step 2: Verify constants consolidation**

```python
from src.constants import RARITY_MEDIANS, CONDITION_IMMUNITY_VALUES
print("Constants imported successfully")
print(f"RARITY_MEDIANS: {RARITY_MEDIANS}")
print(f"CONDITION_IMMUNITY_VALUES: {CONDITION_IMMUNITY_VALUES}")
```

- [ ] **Step 3: Verify source labels**

```python
import pandas as pd
df = pd.read_csv('output/pricing_guide.csv')
print(df['Price Source'].value_counts())
# Should NOT see 'rule+amalgamated'
```

- [ ] **Step 4: Check for new low outliers**

```bash
cat output/anomaly_report.md | grep -i "low"
```

- [ ] **Step 5: Final commit**

```bash
git add data/processed/ output/ index.html
git commit -m "chore: regenerate pipeline with all cleanup fixes"
```

---

## Execution Strategy

**Dispatch 8 parallel @fixer agents** - one per task (Tasks 1-10 can run in parallel).
Then execute Task 11 (pipeline regeneration) sequentially after all fixes complete.

**Estimated time:** 20-30 minutes total (parallel execution)
