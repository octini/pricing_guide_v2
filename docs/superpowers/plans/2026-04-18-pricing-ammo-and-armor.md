# Ammo and +N Armor Pricing Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix two systematic overpricing issues: (1) +N ammunition prices are 10–22x too high because amalgamated reference prices are bypassed, and (2) +N armor has no amalgamated reference prices at all and is priced 3–4x too high by the rule formula.

**Architecture:**
- **Ammo fix:** In `scripts/06_ml_refine.py`, the `blend_price` function exits early (line 288-289) whenever `variant_price` is set — this skips the amalgamated price entirely for ammo. Add an `is_ammunition` exception that uses the amalgamated price when available.
- **Armor fix:** In `src/amalgamator.py`, the generic fallback (lines 252–286) builds queries for ammo, shield, and weapon but not armor. Add an `is_armor` branch that looks up `armor +N` entries in DSA/MSRP. The reference sources have: DSA `Armor, +1`=1,980gp / `+2`=8,910gp / `+3`=29,700gp and MSRP `Armor, +1`=1,312.5gp / `+2`=7,500gp / `+3`=30,000gp.
- After both fixes, re-run the full pipeline from `04_amalgamate.py` onward and regenerate HTML.

**Tech Stack:** Python 3, pandas, scripts in `scripts/`, source in `src/`

---

## Context: Pipeline Flow

```
01_extract_items.py → 02_extract_criteria.py → 03_normalize.py → 04_amalgamate.py
→ 05_rule_formula.py → 05b_variant_adjust.py → 06_ml_refine.py → 07_validate.py
→ 09_enforce_floors.py → 10_generate_output.py → 11_generate_html.py
```

Key intermediate files:
- `data/processed/amalgamated_prices.csv` — output of step 04
- `data/processed/items_priced.csv` — output of step 05
- `data/processed/items_variant_adjusted.csv` — output of step 05b
- `data/processed/items_ml_priced.csv` — output of step 06
- `output/pricing_guide.csv` — final output

## Files to Modify

- `src/amalgamator.py` — add `is_armor` branch to generic fallback (lines ~252–286)
- `scripts/06_ml_refine.py` — add ammo exception in `blend_price` function (lines ~284–304)

## Files to Run After

```bash
python3 scripts/04_amalgamate.py    # re-run to get armor amalgamated prices
python3 scripts/05_rule_formula.py  # re-run (reads amalgamated_prices.csv)
python3 scripts/05b_variant_adjust.py
python3 scripts/06_ml_refine.py
python3 scripts/07_validate.py
python3 scripts/09_enforce_floors.py
python3 scripts/10_generate_output.py
python3 scripts/11_generate_html.py
```

---

## Task 1: Fix Ammo Pricing — Use Amalgamated Price in blend_price

**Files:**
- Modify: `scripts/06_ml_refine.py` (lines 275–304, the `blend_price` function)

### Background

In `06_ml_refine.py`, the `blend_price` function (line 275) determines the final price for each item. Line 288-289 is:

```python
if pd.notna(row.get("variant_price")):
    return row["rule_price"]
```

This returns early whenever `variant_price` is set — which it is for ALL +N ammunition (e.g., +1 Arrow has `variant_price=686.70` but `amalgamated_price=32.88`). The amalgamated reference price is completely ignored.

Reference prices (from `data/processed/amalgamated_prices.csv`):
- +1 ammo: amalgamated=32.88gp, rule=686–817gp (22x too high)
- +2 ammo: amalgamated=124.60gp, rule=3,220–3,835gp (25x too high)
- +3 ammo: amalgamated=635.88gp, rule=14,160–16,860gp (22x too high)

- [ ] **Step 1: Locate the blend_price function**

Open `scripts/06_ml_refine.py`. The `blend_price` function starts at line 275. Find this block (lines 288–291):

```python
        if pd.notna(row.get("variant_price")):
            return row["rule_price"]
        if row.get("price_confidence") == "solo-outlier":
            return row["rule_price"]
```

- [ ] **Step 2: Add the ammo amalgamated-price exception**

Add an `is_ammunition` helper function (near `is_high_rarity_ammunition` around line 99) and modify `blend_price`. The fix: if an item is ammunition AND has an amalgamated price, use amalgamated (bypassing the variant_price early-exit).

Add this helper function **before** `blend_price` (around line 99, after `is_high_rarity_ammunition`):

```python
def is_ammunition_item(row):
    """Check if item is any ammunition (any rarity)."""
    is_ammo = row.get("is_ammunition", False)
    item_type = str(row.get("item_type_code", "")).split("|")[0]
    item_name = str(row.get("name", "")).lower()
    return (is_ammo or item_type == "A" or
            any(a in item_name for a in ["arrow", "bolt", "bullet", "needle"]))
```

Then in `blend_price`, change the `variant_price` early-exit block from:

```python
        if pd.notna(row.get("variant_price")):
            return row["rule_price"]
```

To:

```python
        if pd.notna(row.get("variant_price")):
            # Exception: ammunition with amalgamated price should use amalgamated
            # The variant system prices ammo at weapon-level (rule formula), but
            # the actual reference prices (DSA/MSRP/DMPG) are 10-22x lower.
            if is_ammunition_item(row) and pd.notna(row.get("amalgamated_price")):
                confidence = row.get("price_confidence", "none")
                w_amalg, _ = CONFIDENCE_WEIGHTS.get(confidence, (0.85, 0.15))
                return w_amalg * row["amalgamated_price"] + (1 - w_amalg) * row["ml_price"]
            return row["rule_price"]
```

- [ ] **Step 3: Verify the fix logic**

After editing, run a quick sanity check (does NOT run full pipeline yet — just imports the module):

```bash
cd /Users/ryan/OpenCode/TTRPG/pricing_guide_v2
python3 -c "import scripts.run_helpers 2>/dev/null || python3 -c 'import sys; sys.path.insert(0, \".\"); exec(open(\"scripts/06_ml_refine.py\").read().split(\"if __name__\")[0])'; print('OK')"
```

If that errors, just verify the file has no syntax errors:

```bash
python3 -m py_compile scripts/06_ml_refine.py && echo "Syntax OK"
```

Expected: `Syntax OK`

- [ ] **Step 4: Commit**

```bash
git add scripts/06_ml_refine.py
git commit -m "fix: use amalgamated price for ammunition, bypassing incorrect variant pricing"
```

---

## Task 2: Fix +N Armor — Add Armor Branch to Amalgamator Generic Fallback

**Files:**
- Modify: `src/amalgamator.py` (lines ~252–286, the generic fallback section)

### Background

In `src/amalgamator.py`, the generic fallback (lines 243–286) only handles ammo, shield, and weapon. +N armor items have no amalgamated price, so they get priced purely by the rule formula at 3–4x the reference prices.

Reference data available (from `data/raw/dsa_prices.csv` and `data/raw/msrp_prices.csv`):
- DSA: `Armor, +1`=1,980gp | `Armor, +2`=8,910gp | `Armor, +3`=29,700gp
- MSRP: `Armor, +1`=1,312.5gp | `Armor, +2`=7,500gp | `Armor, +3`=30,000gp
- These are *generic* armor prices (not specific to plate/half plate/breastplate).
- The specific variant delta (e.g., plate armor costs 1,500gp mundane vs 400gp breastplate, a 1,100gp difference) will be added on top of the amalgamated price via the rule formula's `base_item_cost` term.

Current `is_armor` detection: `item_type in ("LA", "MA", "HA")` (light/medium/heavy armor).

- [ ] **Step 1: Locate the generic fallback in amalgamator.py**

Open `src/amalgamator.py`. Find the generic fallback block starting around line 243:

```python
        # Fallback: generic variant matching for items that didn't match
        # Build a generic query from item properties and try matching against
        # each guide's generic entries (e.g., "+3 Weapon", "+1 Ammunition")
        if not prices:
            import re
            item_name = row.get("name", "")
            item_type = str(row.get("item_type_code", "")).split("|")[0] if pd.notna(row.get("item_type_code")) else ""
            rarity = row.get("rarity", "")

            # Check for +N bonus items
            bonus_match = re.search(r'\+(\d+)', item_name)
            if bonus_match:
                bonus = bonus_match.group(1)
                # Determine item category
                is_ammo = (item_type == "A" or ...)
                is_shield = (item_type == "S" or ...)
                is_weapon = (item_type in ("M", "R") or ...)

                # Build generic query names for each guide's naming convention
                generic_queries = []
                if is_ammo:
                    generic_queries = [f"ammunition +{bonus}", ...]
                elif is_shield:
                    generic_queries = [f"shield +{bonus}"]
                elif is_weapon:
                    generic_queries = [f"weapon +{bonus}", ...]
```

- [ ] **Step 2: Add is_armor detection and query**

After the `is_weapon` definition and before the `generic_queries = []` line, add `is_armor` detection:

```python
                is_armor = (item_type in ("LA", "MA", "HA") or
                           any(a in item_name.lower() for a in ["plate", "chain", "leather", "scale", "hide", "splint", "ring mail", "studded"]))
                # Exclude shields from armor detection
                if is_shield:
                    is_armor = False
```

Then add the armor branch in the `if is_ammo:` / `elif is_shield:` / `elif is_weapon:` chain:

```python
                generic_queries = []
                if is_ammo:
                    generic_queries = [f"ammunition +{bonus}", f"ammunition any +{bonus}", f"ammunition +{bonus} ea"]
                elif is_shield:
                    generic_queries = [f"shield +{bonus}"]
                elif is_armor:
                    # DSA uses "Armor, +N", MSRP uses "Armor, +N"
                    generic_queries = [f"armor +{bonus}", f"armor, +{bonus}"]
                elif is_weapon:
                    generic_queries = [f"weapon +{bonus}", f"weapon any +{bonus}"]
```

- [ ] **Step 3: Verify the fix logic**

```bash
cd /Users/ryan/OpenCode/TTRPG/pricing_guide_v2
python3 -m py_compile src/amalgamator.py && echo "Syntax OK"
```

Expected: `Syntax OK`

- [ ] **Step 4: Commit**

```bash
git add src/amalgamator.py
git commit -m "fix: add armor generic fallback to amalgamator for +N armor pricing"
```

---

## Task 3: Run Pipeline and Verify Results

**Files:** No code changes — run the pipeline and check output.

- [ ] **Step 1: Run pipeline from amalgamation step onward**

```bash
cd /Users/ryan/OpenCode/TTRPG/pricing_guide_v2
python3 scripts/04_amalgamate.py
python3 scripts/05_rule_formula.py
python3 scripts/05b_variant_adjust.py
python3 scripts/06_ml_refine.py
python3 scripts/07_validate.py
python3 scripts/09_enforce_floors.py
python3 scripts/10_generate_output.py
python3 scripts/11_generate_html.py
```

Expected: All scripts complete without errors. Step 04 should show `+1 Plate Armor` now has `amalgamated_price` set.

- [ ] **Step 2: Verify +N ammo prices**

```bash
python3 -c "
import pandas as pd
df = pd.read_csv('output/pricing_guide.csv')
ammo = df[df['name'].str.match(r'^\+[123]\s+(Arrow|Bolt|Sling Bullet|Firearm Bullet)', na=False)].sort_values('name')
print(ammo[['name','rarity','final_price','price_source']].to_string())
"
```

Expected prices (approximate — will be blend of amalgamated + ML):
- +1 Arrow: ~33–50gp (was 686gp, reference amalgamated=32.88gp)
- +2 Arrow: ~125–200gp (was 3,220gp, reference amalgamated=124.60gp)
- +3 Arrow: ~636–900gp (was 14,160gp, reference amalgamated=635.88gp)

- [ ] **Step 3: Verify +N armor prices**

```bash
python3 -c "
import pandas as pd
df = pd.read_csv('output/pricing_guide.csv')
armor = df[df['name'].str.match(r'^\+[123]\s+.*(Plate|Half Plate|Breastplate|Chain|Leather)', na=False)].sort_values('name')
print(armor[['name','rarity','final_price','price_source']].to_string())
"
```

Expected: +1 armor ~1,500–2,500gp (was 5,900–7,000gp), +2 armor ~8,000–12,000gp (was 17,000–19,000gp), +3 armor ~28,000–35,000gp (was 63,000–64,000gp). Specific armor types (Plate > Half Plate > Breastplate) should maintain correct ordering.

- [ ] **Step 4: Verify no floor violations**

```bash
python3 -c "
import pandas as pd
df = pd.read_csv('output/pricing_guide.csv')
mundane_prices = {}
for _, row in df[df['rarity']=='mundane'].iterrows():
    mundane_prices[row['name']] = row['final_price']
violations = []
for _, row in df[df['rarity']!='mundane'].iterrows():
    name = row['name']
    price = row['final_price']
    for mname, mprice in mundane_prices.items():
        if mname.lower() in name.lower() and price < mprice:
            violations.append(f'{name}: {price:.2f}gp < {mname}: {mprice:.2f}gp')
print(f'Floor violations: {len(violations)}')
for v in violations[:10]:
    print(f'  {v}')
"
```

Expected: 0 floor violations (or very few — the floor enforcement in step 09 handles these).

- [ ] **Step 5: Commit final results**

```bash
git add output/pricing_guide.csv index.html
git commit -m "feat: fix ammo and +N armor pricing, regenerate guide"
git push
```

---

## Self-Review Checklist

- [x] **Ammo fix:** `blend_price` in `06_ml_refine.py` now uses amalgamated price for ammo with reference prices (32.88gp → ~33–50gp for +1 Arrow)
- [x] **Armor fix:** `amalgamator.py` generic fallback now queries `armor +{bonus}` against DSA/MSRP for +N armor items
- [x] **Pipeline flow:** Both fixes are in the right stages (amalgamation is stage 04, blending is stage 06)
- [x] **Ordering preserved:** Plate > Half Plate > Breastplate ordering is maintained by the `09_enforce_floors.py` armor tier constraint
- [x] **No regression:** The ammo exception only fires when `is_ammunition_item` AND `amalgamated_price` is not null — other variant-adjusted items are unaffected
- [x] **Floor violations:** The floor enforcement script will catch any magic items that end up below their mundane counterparts after repricing
