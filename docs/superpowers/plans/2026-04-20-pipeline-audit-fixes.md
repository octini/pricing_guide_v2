# Pipeline Audit High-Priority Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 4 high-priority bugs identified in the pipeline audit that affect pricing accuracy and output quality.

**Architecture:** Four independent fixes across 3 files (pricing_engine.py, 06_ml_refine.py, 10_generate_output.py). Each fix is isolated and can be executed in parallel.

**Tech Stack:** Python 3.9+, pandas, XGBoost

---

## Task 1: Fix "returning" Property Premium Typo

**Files:**
- Modify: `src/pricing_engine.py:122`
- Test: Verify returning weapons get +1.0 multiplier

**Issue:** Line 122 has `"返回": 1.0` (Chinese characters) instead of `"returning": 1.0`. The returning weapon property premium is never applied.

- [ ] **Step 1: Verify the typo exists**

Run:
```python
import pandas as pd
df = pd.read_csv('data/processed/items_criteria.csv')
returning = df[df['name'].str.contains('returning', case=False, na=False)]
print(returning[['name', 'weapon_properties']].head())
```

Expected: Some weapons should have "returning" in weapon_properties

- [ ] **Step 2: Fix the typo**

Edit `src/pricing_engine.py` line 122:

```python
# Change from:
"返回": 1.0,

# To:
"returning": 1.0,
```

- [ ] **Step 3: Test the fix**

Run:
```bash
python3 scripts/05_rule_formula.py
```

Then verify a returning weapon (e.g., "Returning Dagger") increased in price:
```python
import pandas as pd
df = pd.read_csv('data/processed/items_priced.csv')
returning = df[df['name'].str.contains('returning', case=False, na=False)]
print(returning[['name', 'rule_price']].head())
```

Expected: Returning weapons should be ~10% higher than non-returning variants

- [ ] **Step 4: Commit**

```bash
git add src/pricing_engine.py
git commit -m "fix: 'returning' weapon property premium typo (was Chinese characters)

Line 122 had '返回' instead of 'returning'
Returning weapons now correctly get +1.0 (10%) price premium"
```

---

## Task 2: Fix ML Fallback Confidence Weights

**Files:**
- Modify: `scripts/06_ml_refine.py:333`
- Test: Verify fallback weights sum to 1.0

**Issue:** Line 333 has `CONFIDENCE_WEIGHTS.get(confidence, (0.7, 0.35))` where fallback sums to 1.05 instead of 1.0.

- [ ] **Step 1: Verify the issue**

Read line 333:
```python
# Current (WRONG):
amalgam_weight, ml_weight = CONFIDENCE_WEIGHTS.get(confidence, (0.7, 0.35))
```

- [ ] **Step 2: Fix the weights**

Edit `scripts/06_ml_refine.py` line 333:

```python
# Change from:
amalgam_weight, ml_weight = CONFIDENCE_WEIGHTS.get(confidence, (0.7, 0.35))

# To (match 'multi' default):
amalgam_weight, ml_weight = CONFIDENCE_WEIGHTS.get(confidence, (0.85, 0.15))
```

- [ ] **Step 3: Test the fix**

Run:
```bash
python3 scripts/06_ml_refine.py
```

Verify no errors and check a few items:
```python
import pandas as pd
df = pd.read_csv('data/processed/items_ml_priced.csv')
print(df[['name', 'final_price', 'confidence']].head(10))
```

Expected: No errors, prices reasonable

- [ ] **Step 4: Commit**

```bash
git add scripts/06_ml_refine.py
git commit -m "fix: ML fallback confidence weights sum to 1.05 → 1.0

Line 333 fallback (0.7, 0.35) changed to (0.85, 0.15)
Matches 'multi' confidence tier default"
```

---

## Task 3: Fix Output Generator Notes Logic

**Files:**
- Modify: `scripts/10_generate_output.py:258, 336`
- Test: Verify algorithmic items show 🤖 emoji in output

**Issue:** Line 258 has `notes = '🤖' if notes else '🤖'` (both branches identical). Line 336 ignores computed notes field.

- [ ] **Step 1: Verify the issue**

Read lines 255-260 and 333-340:
```python
# Line 258 (BROKEN):
notes = '🤖' if notes else '🤖'

# Line 336 (BROKEN):
'⚠️' if row['Is Outlier'] else ''  # Never shows 🤖
```

- [ ] **Step 2: Fix line 258 - combine outlier and algorithmic flags**

Edit `scripts/10_generate_output.py` line 258:

```python
# Change from:
notes = '🤖' if notes else '🤖'

# To:
if row.get('is_outlier'):
    notes = '⚠️'
if row.get('price_source') == 'Algorithm':
    notes = notes + ' 🤖' if notes else '🤖'
```

- [ ] **Step 3: Fix line 336 - use computed notes field**

Edit `scripts/10_generate_output.py` line 336:

```python
# Change from:
'Notes': '⚠️' if row['Is Outlier'] else '',

# To:
'Notes': row.get('notes', ''),
```

- [ ] **Step 4: Test the fix**

Run:
```bash
python3 scripts/10_generate_output.py
```

Verify output:
```python
import pandas as pd
df = pd.read_csv('output/pricing_guide.csv')
algo = df[df['Price Source'] == 'Algorithm']
print(algo[['Name', 'Notes']].head(10))
```

Expected: Algorithm items show 🤖 in Notes column

- [ ] **Step 5: Commit**

```bash
git add scripts/10_generate_output.py
git commit -m "fix: output generator notes logic broken

Line 258: Both branches produced '🤖' - now combines outlier + algorithmic flags
Line 336: Ignored computed notes field - now uses it
Algorithm items now correctly show 🤖 emoji in output"
```

---

## Task 4: Fix Excel Header/Data Column Mismatch

**Files:**
- Modify: `scripts/10_generate_output.py:380-450` (sheets 3-4)
- Test: Verify Excel sheets have matching headers and data

**Issue:** Sheets 3 (Very Rare) and 4 (Legendary) define 11 headers but write only 8 values per row.

- [ ] **Step 1: Verify the issue**

Read lines 380-400 (sheet 3) and 420-440 (sheet 4):
```python
# Headers (11 items):
headers = ['Name', 'Type', 'Rarity', 'Price (gp)', ...]  # 11 items

# Data rows (8 values):
for idx, row in df.iterrows():
    ws.append([row['Name'], row['Type'], ...])  # Only 8 values
```

- [ ] **Step 2: Count actual columns needed**

Check what columns are actually being written:
```python
# Should be these 8:
['Name', 'Type', 'Rarity', 'Price (gp)', 'Price Source', 'Confidence', 'Is Outlier', 'Notes']
```

- [ ] **Step 3: Fix headers to match data**

Edit `scripts/10_generate_output.py` around line 385 (sheet 3):

```python
# Change from (11 headers):
headers = ['Name', 'Type', 'Rarity', 'Price (gp)', 'Price Source', 'Confidence', 'Is Outlier', 'Notes', 'Extra1', 'Extra2', 'Extra3']

# To (8 headers):
headers = ['Name', 'Type', 'Rarity', 'Price (gp)', 'Price Source', 'Confidence', 'Is Outlier', 'Notes']
```

Repeat for sheet 4 around line 425.

- [ ] **Step 4: Test the fix**

Run:
```bash
python3 scripts/10_generate_output.py
```

Open `output/pricing_guide.xlsx` and verify:
- Sheet 3 (Very Rare): Headers align with data
- Sheet 4 (Legendary): Headers align with data
- No empty columns

- [ ] **Step 5: Commit**

```bash
git add scripts/10_generate_output.py
git commit -m "fix: Excel sheets 3-4 header/data column mismatch

Sheets defined 11 headers but wrote 8 values per row
Reduced headers to match actual data columns:
['Name', 'Type', 'Rarity', 'Price (gp)', 'Price Source', 'Confidence', 'Is Outlier', 'Notes']"
```

---

## Task 5: Regenerate Full Pipeline and Verify

**Files:**
- All pipeline outputs

- [ ] **Step 1: Run full pipeline**

```bash
python3 scripts/05_rule_formula.py && \
python3 scripts/05b_variant_adjust.py && \
python3 scripts/06_ml_refine.py && \
python3 scripts/07_validate.py && \
python3 scripts/09_enforce_floors.py && \
python3 scripts/10_generate_output.py && \
python3 scripts/11_generate_html.py
```

Expected: All scripts complete without errors

- [ ] **Step 2: Verify returning weapons**

```python
import pandas as pd
df = pd.read_csv('output/pricing_guide.csv')
returning = df[df['Name'].str.contains('returning', case=False, na=False)]
print("Returning weapons:")
print(returning[['Name', 'Price (gp)', 'Notes']])
```

Expected: Returning weapons priced ~10% higher than base

- [ ] **Step 3: Verify algorithmic items show emoji**

```python
algo = df[df['Price Source'] == 'Algorithm']
print("\nAlgorithm items (should show 🤖):")
print(algo[['Name', 'Notes']].head(10))
```

Expected: Notes column contains 🤖

- [ ] **Step 4: Check anomaly report**

```bash
cat output/anomaly_report.md | head -50
```

Expected: Report generated, no errors

- [ ] **Step 5: Final commit**

```bash
git add data/processed/ output/ index.html
git commit -m "chore: regenerate pipeline with high-priority fixes

- Returning weapons now priced correctly
- Algorithm items show 🤖 emoji
- Excel sheets have aligned headers
- ML fallback weights corrected"
```

---

## Execution Strategy

**Dispatch 4 parallel @fixer agents** - one per task (Tasks 1-4).
Then execute Task 5 (pipeline regeneration) sequentially after all fixes complete.

**Estimated time:** 15-20 minutes total (parallel execution)
