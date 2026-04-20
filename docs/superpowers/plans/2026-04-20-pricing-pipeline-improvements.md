# Pricing Pipeline Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix systemic pricing issues in the D&D 5e Magic Item Pricing Guide pipeline to improve accuracy, reduce conflicts between components, and ensure logical pricing across all 4,759 items.

**Architecture:** The pipeline has 9 phases: extraction → criteria → amalgamation → rule formula → variant adjustment → ML refinement → validation → floor enforcement → output. We'll address issues in each phase systematically, starting with foundational problems (amalgamator matching, variant adjustment conflicts) before moving to specific item families and comprehensive audit.

**Tech Stack:** Python 3.9+, pandas, XGBoost, RapidFuzz, Dolt (beads) for issue tracking.

---

## Task 1: Improve Amalgamator Item Matching

**Files:**
- Modify: `src/amalgamator.py:240-290` (generic fallback matching)
- Modify: `src/amalgamator.py:100-180` (fuzzy matching logic)
- Test: `tests/test_amalgamator.py` (create if doesn't exist)

**Goal:** Increase match rate for +N armor, +N weapons, and other items currently missing reference prices.

- [ ] **Step 1: Analyze current match failures**

Run this diagnostic to identify items that should match but don't:

```python
import pandas as pd
df = pd.read_csv('data/processed/amalgamated_prices.csv')
unmatched = df[df['price_confidence'] == 'none']
print(f"Unmatched items: {len(unmatched)}")
print(unmatched[unmatched['name'].str.contains('\+[123]', na=False)][['name', 'rarity', 'type']].head(20))
```

Expected: List of +N items without reference prices (should find DMPG matches)

- [ ] **Step 2: Check DMPG source data for +N armor**

```python
import pandas as pd
dmpg = pd.read_csv('data/raw/dmpg_prices.csv')
print(dmpg[dmpg['name'].str.contains('armor', case=False, na=False)].head(20))
print(dmpg[dmpg['name'].str.contains('\+[123]', na=False)].head(20))
```

Expected: DMPG entries for +N armor (e.g., "Armor, +1", "Armor, +2", "Armor, +3")

- [ ] **Step 3: Improve generic fallback matching for armor**

Modify `src/amalgamator.py` lines 259-270 to check more DMPG naming patterns:

```python
# Current armor matching (lines ~259-270):
is_armor = (item_type in ("LA", "MA", "HA") or
           "armor" in item_name.lower() or
           any(a in item_name.lower() for a in ["plate armor", "half plate", "breastplate", "chain mail", "chain shirt", "scale mail", "splint", "ring mail", "studded leather", "hide armor"]))

# Add DMPG-specific pattern matching after line 270:
# DMPG uses formats like "Armor, +1", "Weapon, +1", "Shield, +1"
if pd.notna(row.get('ac_bonus')) and row.get('ac_bonus') > 0:
    # This is +N armor - try DMPG format "Armor, +N"
    bonus = int(row.get('ac_bonus'))
    dmpg_key = f"Armor, +{bonus}"
    if dmpg_key in dmpg_normalized:
        matches.append(('dmpg', dmpg_key, dmpg_normalized[dmpg_key]))
```

- [ ] **Step 4: Test amalgamator improvements**

Run: `python3 scripts/04_amalgamate.py`

Expected: Increased match rate for +N armor items, DMPG prices now found

- [ ] **Step 5: Verify +N armor prices**

```python
import pandas as pd
df = pd.read_csv('data/processed/amalgamated_prices.csv')
armor = df[df['name'].str.contains('\+3 Plate', na=False)]
print(armor[['name', 'amalgamated_price', 'dsa_price', 'msrp_price', 'dmpg_price', 'price_sources']])
```

Expected: dmpg_price should now have a value (~30,000gp), price_sources includes DMPG

- [ ] **Step 6: Commit**

```bash
git add src/amalgamator.py data/processed/
git commit -m "feat: improve amalgamator matching for +N armor with DMPG sources"
```

---

## Task 2: Investigate and Fix Variant Adjustment System

**Files:**
- Modify: `scripts/05b_variant_adjust.py:1-159` (adjustment logic)
- Modify: `src/generic_pricing.py:140-160` (variant price computation)
- Test: Compare prices before/after variant adjustment

**Goal:** Understand variant adjustment purpose and prevent it from overriding good amalgamated prices.

- [ ] **Step 1: Document which items currently use variant adjustment**

```python
import pandas as pd
df = pd.read_csv('data/processed/items_variant_adjusted.csv')
adjusted = df[df['variant_price'].notna()]
print(f"Items with variant_price: {len(adjusted)}")
print(adjusted.groupby('rarity').size())
print(adjusted[['name', 'variant_price', 'rule_price', 'price_source']].head(30))
```

Expected: List of items being variant-adjusted, see patterns

- [ ] **Step 2: Check skip list in 05b_variant_adjust.py**

Read lines 80-120 to see what's already being skipped. Look for patterns like:
- `if 'adamantine' in name.lower(): continue`
- `if row.get('is_sentient'): continue`

- [ ] **Step 3: Add skip for items with multi-source amalgamated prices**

Modify `scripts/05b_variant_adjust.py` around line 95 (after existing skip checks):

```python
# Skip items with good amalgamated reference prices
if (pd.notna(row.get('amalgamated_price')) and 
    row.get('price_confidence') in ('multi', 'solo')):
    # Trust the reference sources over variant math
    continue
```

- [ ] **Step 4: Test variant adjustment changes**

Run: `python3 scripts/05b_variant_adjust.py`

Expected: Fewer items adjusted, +N armor skipped

- [ ] **Step 5: Verify +N armor not variant-adjusted**

```python
import pandas as pd
df = pd.read_csv('data/processed/items_variant_adjusted.csv')
armor = df[df['name'].str.contains('\+3 Plate', na=False)]
print(armor[['name', 'variant_price', 'rule_price', 'price_source']])
```

Expected: variant_price should be NaN or unchanged, price_source still shows amalgamated

- [ ] **Step 6: Commit**

```bash
git add scripts/05b_variant_adjust.py
git commit -m "fix: skip variant adjustment for items with amalgamated reference prices"
```

---

## Task 3: Improve Specific Variant Pricing Within Categories

**Files:**
- Create: `src/variant_pricing.py` (new module)
- Modify: `scripts/05b_variant_adjust.py:100-140` (variant adjustment math)
- Test: Compare +N Half Plate vs +N Plate pricing

**Goal:** Create meaningful price differences between specific variants (e.g., +3 Half Plate vs +3 Plate) while keeping prices reasonable.

- [ ] **Step 1: Calculate mundane baseline prices by category**

Create analysis script:

```python
import pandas as pd
df = pd.read_csv('data/processed/items_criteria.csv')
mundane = df[df['rarity'] == 'mundane']

# Armor baselines
armor = mundane[mundane['type'].str.contains('armor', case=False, na=False)]
print("Mundane armor prices:")
print(armor.groupby('name')['official_price_gp'].agg(['mean', 'median', 'min', 'max']))

# Calculate median armor cost
armor_median = armor['official_price_gp'].median()
print(f"\nMedian mundane armor: {armor_median}gp")

# Specific armor variants
for name in ['Breastplate', 'Half Plate Armor', 'Plate Armor']:
    price = armor[armor['name'] == name]['official_price_gp'].values[0]
    ratio = price / armor_median
    print(f"{name}: {price}gp (ratio: {ratio:.2f}x)")
```

Expected: Mundane price ratios (Plate ~2x Half Plate, etc.)

- [ ] **Step 2: Create variant pricing module**

Create `src/variant_pricing.py`:

```python
"""Variant pricing within item categories."""
import pandas as pd
import numpy as np

def calculate_category_baseline(df, category_pattern):
    """Calculate baseline price for an item category.
    
    Args:
        df: DataFrame with mundane items and official_price_gp
        category_pattern: Regex to match category items
        
    Returns:
        median_price: Median price of mundane items in category
    """
    mundane = df[df['rarity'] == 'mundane']
    category = mundane[mundane['name'].str.contains(category_pattern, case=False, na=False)]
    return category['official_price_gp'].median()

def calculate_variant_multiplier(specific_name, baseline_price, mundane_prices):
    """Calculate price multiplier for a specific variant.
    
    Args:
        specific_name: Name of specific variant (e.g., "Plate Armor")
        baseline_price: Category median baseline
        mundane_prices: Dict of mundane item names to prices
        
    Returns:
        multiplier: Float multiplier (e.g., 2.0 for Plate vs median armor)
    """
    if specific_name in mundane_prices:
        return mundane_prices[specific_name] / baseline_price
    return 1.0  # Default to baseline

def apply_variant_multiplier(base_price, multiplier, dampening=0.5):
    """Apply variant multiplier with dampening for high rarities.
    
    Args:
        base_price: Base price (e.g., amalgamated +N armor price)
        multiplier: Mundane variant multiplier
        dampening: How much to dampen the multiplier (0=full, 1=none)
        
    Returns:
        adjusted_price: Price adjusted for variant
    """
    # Dampen multiplier for high-value items
    # At dampening=0.5, a 2.0x mundane ratio becomes ~1.4x for magic items
    dampened_multiplier = 1 + (multiplier - 1) * (1 - dampening)
    return base_price * dampened_multiplier
```

- [ ] **Step 3: Integrate variant pricing into 05b_variant_adjust.py**

Add after variant adjustment skip logic:

```python
# Apply specific variant pricing for +N armor
if row.get('ac_bonus') and row.get('ac_bonus') > 0:
    # This is +N armor - apply variant multiplier
    baseline = calculate_category_baseline(items_criteria, 'armor')
    mundane_prices = {
        'Breastplate': 400,
        'Half Plate Armor': 750,
        'Plate Armor': 1500,
    }
    
    # Determine specific armor type
    if 'plate armor' in name.lower() and 'half' not in name.lower():
        multiplier = calculate_variant_multiplier('Plate Armor', baseline, mundane_prices)
    elif 'half plate' in name.lower():
        multiplier = calculate_variant_multiplier('Half Plate Armor', baseline, mundane_prices)
    elif 'breastplate' in name.lower():
        multiplier = calculate_variant_multiplier('Breastplate', baseline, mundane_prices)
    else:
        multiplier = 1.0
    
    # Apply with dampening
    adjusted_price = apply_variant_multiplier(row['final_price'], multiplier, dampening=0.5)
    df.loc[idx, 'final_price'] = adjusted_price
```

- [ ] **Step 4: Test variant pricing**

Run full pipeline: `python3 scripts/05b_variant_adjust.py && python3 scripts/06_ml_refine.py`

Check results:
```python
df = pd.read_csv('output/pricing_guide.csv')
armor = df[df['Name'].str.contains('\+3.*(Plate|Half Plate|Breastplate)', na=False)]
print(armor[['Name', 'Rarity', 'Price (gp)']])
```

Expected: +3 Plate > +3 Half Plate > +3 Breastplate with meaningful gaps (~30-50% differences)

- [ ] **Step 5: Commit**

```bash
git add src/variant_pricing.py scripts/05b_variant_adjust.py
git commit -m "feat: apply dampened variant multipliers for specific +N armor types"
```

---

## Task 4: Comprehensive Pipeline Audit

**Files:** All pipeline scripts and src modules
**Output:** `docs/pipeline_audit_findings.md`

**Goal:** Verify every component is serving a purpose, not conflicting, and fundamentally sound.

- [ ] **Step 1: Audit scripts/01_extract_items.py**

Check:
- [ ] Item extraction logic is correct
- [ ] Price extraction handles all edge cases
- [ ] No hardcoded values that should be dynamic
- [ ] Alias field is extracted and passed through

Create findings doc section:
```markdown
## 01_extract_items.py
**Purpose:** Extract raw items from 5e.tools JSON
**Status:** OK / Needs fixes
**Issues:** [list any]
**Dependencies:** None
**Downstream:** items_master.csv → 02_extract_criteria.py
```

- [ ] **Step 2: Audit scripts/02_extract_criteria.py**

Check:
- [ ] Generic parent entry inheritance working
- [ ] All criteria fields extracted
- [ ] No duplicate extraction logic with src/criteria_extractor.py

- [ ] **Step 3: Audit src/criteria_extractor.py**

Check:
- [ ] All property extraction patterns correct
- [ ] CONDITION_IMMUNITY_VALUES and other constants match usage in pricing_engine.py
- [ ] Prose extraction catching key properties

- [ ] **Step 4: Audit src/pricing_engine.py**

Check:
- [ ] Rule formula constants are reasonable
- [ ] All item types handled
- [ ] No conflicts with variant adjustment
- [ ] Outlier handling correct

- [ ] **Step 5: Audit scripts/04_amalgamate.py and src/amalgamator.py**

Check:
- [ ] Fuzzy matching thresholds appropriate
- [ ] Generic fallback covers all item types
- [ ] Weighting logic sound
- [ ] Outlier detection working

- [ ] **Step 6: Audit scripts/05_rule_formula.py**

Check:
- [ ] Correctly applies pricing_engine.py
- [ ] Handles all edge cases
- [ ] No conflicts with amalgamated prices

- [ ] **Step 7: Audit scripts/05b_variant_adjust.py**

Check:
- [ ] Skip list comprehensive
- [ ] Variant math correct
- [ ] Doesn't override good reference prices
- [ ] Ammunition handling correct

- [ ] **Step 8: Audit scripts/06_ml_refine.py**

Check:
- [ ] Training set selection appropriate
- [ ] Blend weights reasonable
- [ ] Special case handlers (ammo, armor, scrolls) correct
- [ ] No conflicts with variant adjustment

- [ ] **Step 9: Audit scripts/07_validate.py**

Check:
- [ ] Anomaly detection thresholds appropriate
- [ ] Outlier flagging correct

- [ ] **Step 10: Audit scripts/09_enforce_floors.py**

Check:
- [ ] Floor multipliers reasonable
- [ ] Skip logic for amalgamated items working
- [ ] Armor tier ordering correct
- [ ] No syntax/indentation issues (verify line 263-267)

- [ ] **Step 11: Audit scripts/10_generate_output.py**

Check:
- [ ] Output formatting correct
- [ ] Alias price copying working
- [ ] Generic variant exclusion correct

- [ ] **Step 12: Create consolidated findings document**

Write `docs/pipeline_audit_findings.md` with:
- Summary of all components
- List of conflicts found
- List of redundancies
- Recommended fixes
- Priority ranking

- [ ] **Step 13: Commit**

```bash
git add docs/pipeline_audit_findings.md
git commit -m "docs: comprehensive pipeline audit findings"
```

---

## Task 5: Review Dragon's Wrath Weapon Pricing

**Files:**
- Analyze: `output/pricing_guide.csv` (Dragon's Wrath items)
- Modify: `src/criteria_extractor.py` (if criteria extraction is wrong)
- Modify: `src/pricing_engine.py` (if formula is wrong)

**Goal:** Ensure Dragon's Wrath weapons have logical pricing across all rarities and weapon types.

- [ ] **Step 1: Identify all Dragon's Wrath variants**

```python
import pandas as pd
df = pd.read_csv('output/pricing_guide.csv')
dw = df[df['Name'].str.contains('Dragon.*Wrath', case=False, na=False)]
print(f"Dragon's Wrath items: {len(dw)}")
print(dw[['Name', 'Rarity', 'Price (gp)', 'Price Source']].sort_values(['Rarity', 'Name']))
```

Expected: List of all Dragon's Wrath weapons with prices

- [ ] **Step 2: Check criteria extraction for Dragon's Wrath**

```python
import pandas as pd
df = pd.read_csv('data/processed/items_criteria.csv')
dw = df[df['name'].str.contains('Dragon.*Wrath', case=False, na=False)]
print(dw[['name', 'rarity', 'weapon_bonus', 'damage_resistances', 'extra_damage_dice', 'extra_damage_avg']].head(10))
```

Expected: See what properties were extracted

- [ ] **Step 3: Check raw JSON for Dragon's Wrath**

```python
import pandas as pd
df = pd.read_csv('data/processed/items_master.csv')
dw = df[df['name'].str.contains('Dragon.*Wrath', case=False, na=False)]
print(dw[['name', 'source', 'rarity']].head())
# Check one item's raw JSON
import json
item = dw.iloc[0]
print(json.loads(item['raw_json'])['entries'][:5])
```

Expected: See actual item properties in 5e.tools format

- [ ] **Step 4: Verify Dragon's Wrath properties**

Dragon's Wrath weapons should have:
- [ ] +N bonus (varies by rarity)
- [ ] Extra damage vs dragons (2d6)
- [ ] Resistance to dragon's breath damage type
- [ ] Attunement required

Check if these are being extracted in criteria_extractor.py

- [ ] **Step 5: Compare to similar items**

```python
import pandas as pd
df = pd.read_csv('output/pricing_guide.csv')
# Find other +N weapons with extra damage
similar = df[df['Name'].str.contains('\+[123].*Slayer', na=False)]
print(similar[['Name', 'Rarity', 'Price (gp)']])
```

Expected: Dragon Slayer, Giant Slayer, etc. for comparison

- [ ] **Step 6: Fix criteria extraction if needed**

If properties are missing, add extraction patterns to `src/criteria_extractor.py`:

```python
# In extract_entries_criteria or extract_prose_criteria:
if 'dragon\'s wrath' in item_name.lower():
    # Extract extra damage vs dragons
    if '2d6' in entries_text:
        result['extra_damage_dice'] = '2d6'
    # Extract damage resistance
    if 'resistance' in entries_text and 'damage' in entries_text:
        result['damage_resistances'] = extract_resistance_type(entries_text)
```

- [ ] **Step 7: Re-run pipeline and verify**

Run: `python3 scripts/02_extract_criteria.py && python3 scripts/05_rule_formula.py && python3 scripts/06_ml_refine.py`

Check:
```python
df = pd.read_csv('output/pricing_guide.csv')
dw = df[df['Name'].str.contains('Dragon.*Wrath', na=False)]
print(dw[['Name', 'Rarity', 'Price (gp)']].sort_values(['Rarity', 'Name']))
```

Expected: Prices should be higher than base +N weapons, logical across rarities

- [ ] **Step 8: Commit**

```bash
git add src/criteria_extractor.py output/
git commit -m "fix: Dragon's Wrath weapon criteria extraction and pricing"
```

---

## Task 6: Manual Review Framework (Back Pocket)

**Files:**
- Create: `docs/manual_review_process.md`
- Create: `scripts/review_helpers.py`

**Goal:** Prepare infrastructure for comprehensive manual review of all 4,759 items.

**Note:** Do not execute this task yet. Complete Tasks 1-5 first. This task is on hold until foundational issues are resolved.

- [ ] **Step 1: Create review batching script**

Create `scripts/review_helpers.py`:

```python
"""Helpers for manual pricing review."""
import pandas as pd

def batch_items_by_rarity_type(output_csv='output/pricing_guide.csv'):
    """Group items by rarity and type for review."""
    df = pd.read_csv(output_csv)
    batches = {}
    for rarity in df['Rarity'].unique():
        for type_code in df['Type Code'].unique():
            subset = df[(df['Rarity'] == rarity) & (df['Type Code'] == type_code)]
            if len(subset) > 0:
                key = f"{rarity}_{type_code}"
                batches[key] = subset
    return batches

def export_review_batch(batch_name, items, output_dir='review_batches/'):
    """Export a batch for manual review."""
    from pathlib import Path
    Path(output_dir).mkdir(exist_ok=True)
    items.to_csv(f'{output_dir}/{batch_name}.csv', index=False)
    print(f"Exported {len(items)} items to {output_dir}/{batch_name}.csv")
```

- [ ] **Step 2: Create review checklist template**

Create `docs/manual_review_process.md`:

```markdown
# Manual Pricing Review Process

## Review Criteria

For each item, check:
1. **Reference Price Match**: Does it have amalgamated reference? If yes, is final price within 20%?
2. **Rarity Appropriateness**: Does price fit rarity tier? (Common <1k, Uncommon 1-5k, Rare 5-20k, Very Rare 20-100k, Legendary 100k+)
3. **Variant Consistency**: Is it priced appropriately vs similar variants? (e.g., +3 Plate > +3 Half Plate)
4. **Property Valuation**: Do beneficial properties add appropriate value?
5. **Curse/Drawback Discount**: Are drawbacks properly reflected in lower price?

## Review Order

1. Mundane items (verify base prices)
2. Common magic items
3. Uncommon magic items
4. Rare magic items
5. Very Rare magic items
6. Legendary items
7. Artifacts

## Flagging Issues

Create `review_flags.csv` with columns:
- item_name
- source
- issue_type (overpriced/underpriced/missing_properties/etc)
- suggested_price
- notes
```

- [ ] **Step 3: Generate review batches (when ready)**

When Tasks 1-5 are complete, run:

```python
from review_helpers import batch_items_by_rarity_type, export_review_batch

batches = batch_items_by_rarity_type()
for name, items in batches.items():
    export_review_batch(name, items)
```

Expected: ~50-100 batch files organized by rarity/type

- [ ] **Step 4: Commit (when executed)**

```bash
git add docs/manual_review_process.md scripts/review_helpers.py
git commit -m "feat: manual review framework and batching helpers"
```

---

## Execution Strategy

**Recommended approach:** Use subagent-driven-development with one subagent per task.

**Task dependencies:**
- Task 1 (Amalgamator) → Task 2 (Variant Adjustment) → Task 3 (Variant Pricing)
- Task 4 (Audit) can run in parallel with Tasks 1-3
- Task 5 (Dragon's Wrath) depends on Task 4 findings
- Task 6 (Manual Review) waits for all others

**Estimated timeline:**
- Tasks 1-3: 2-3 hours each (6-9 hours total)
- Task 4: 4-6 hours (comprehensive)
- Task 5: 1-2 hours (depends on findings)
- Task 6: Framework creation 1 hour, actual review 20-40 hours (future work)

**Verification after each task:**
1. Run full pipeline
2. Check anomaly report for changes
3. Verify specific items mentioned in task
4. Ensure no regressions in unrelated items
