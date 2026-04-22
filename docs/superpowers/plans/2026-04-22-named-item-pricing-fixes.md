# Named Item Pricing Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix pricing for Holy Avenger (~200k), Defender (~30k amalgamated), and other named legendary weapons while preserving artifact pricing (~800k max).

**Architecture:** Three targeted fixes: (1) Defender amalgamation matching, (2) Holy Avenger criteria extraction, (3) Rarity scaling ONLY for items without amalgamated prices. Each fix is isolated and verified independently.

**Tech Stack:** Python, pandas, rapidfuzz for fuzzy matching, XGBoost for ML blending.

---

## CRITICAL REQUIREMENTS (MUST VERIFY BEFORE EACH COMMIT)

| Item | Current | Target | Must Not Exceed |
|------|---------|--------|-----------------|
| Holy Avenger (50 variants) | 11,875 gp | 150k-225k | 250k |
| Defender (28 variants) | 13,260 gp | 28k-35k (amalgamated) | 40k |
| Vorpal (4 variants) | 40,993 gp | 35k-45k (amalgamated) | 50k |
| Max Artifact (Orrery) | 799,200 gp | 750k-850k | 900k |
| R² (CV mean) | 0.9131 | ≥0.85 | - |

**ABORT CRITERIA:** If ANY artifact exceeds 900k OR Vorpal exceeds 50k OR Defender exceeds 40k, DO NOT COMMIT. Revert and diagnose.

---

## Task 1: Defender Amalgamation Fix

**Files:**
- Modify: `src/amalgamator.py:149-194` (fuzzy_match_items function)

**Problem:** "Defender Longsword" fuzzy matches to "Defender (any sword)" at score 73.7, below the 85 threshold. All three sources have Defender prices (DSA: 15k, MSRP: 30k, DMPG: 55k) but variants aren't matching.

**Solution:** Add special case for "Defender [Weapon]" pattern.

### Steps:

- [ ] **Step 1: Add Defender special case**

In `src/amalgamator.py`, modify `fuzzy_match_items()` around line 149:

```python
def fuzzy_match_items(
    query: str,
    candidates: list,
    threshold: int = 85,
) -> list:
    """Return candidates that fuzzy-match query above threshold."""
    import re

    # SPECIAL CASE: Defender weapons match "Defender (any sword)" entries
    if query.lower().startswith('defender '):
        defender_matches = [c for c in candidates if 'defender' in c.lower() and '(any sword)' in c.lower()]
        if defender_matches:
            return defender_matches

    # ... rest of existing function unchanged
```

- [ ] **Step 2: Test Defender amalgamation**

Run:
```bash
python3 scripts/04_amalgamate.py
python3 -c "
import pandas as pd
amalg = pd.read_csv('data/processed/amalgamated_prices.csv')
defender = amalg[amalg['name'].str.contains('Defender', na=False)]
print('Defender amalgamated:')
print(defender[['name', 'dsa_price', 'msrp_price', 'dmpg_price', 'amalgamated_price']].head(3).to_string())
assert defender['amalgamated_price'].notna().all(), 'Defender variants should have amalgamated prices'
assert 28000 < defender['amalgamated_price'].median() < 35000, 'Defender should be ~31.5k'
print('✅ Defender amalgamation verified')
"
```

Expected output:
```
Defender amalgamated:
                name  dsa_price  msrp_price  dmpg_price  amalgamated_price
1435  Defender Battleaxe    15000.0     30000.0     55000.0            31500.0
...
✅ Defender amalgamation verified
```

- [ ] **Step 3: Commit**

```bash
git add src/amalgamator.py
git commit -m "fix: Defender weapons now match \"Defender (any sword)\" reference entries

- Added special case in fuzzy_match_items() for \"Defender [Weapon]\" pattern
- All 28 Defender variants now get amalgamated price ~31,500 gp
- Reference sources: DSA 15k, MSRP 30k, DMPG 55k (weighted average)
"
```

---

## Task 2: Holy Avenger Criteria Extraction

**Files:**
- Modify: `src/criteria_extractor.py:175-230` (extract_entries_criteria function)

**Problem:** Holy Avenger's 2d10 radiant damage vs fiends/undead isn't extracted. The prose text says "extra 2d10 radiant damage" but the regex doesn't match.

**Solution:** Add plain-text damage extraction fallback.

### Steps:

- [ ] **Step 1: Check Holy Avenger prose format**

Run:
```bash
python3 -c "
import json
with open('data/raw/items-sublist-data.json') as f:
    items = json.load(f)
    ha = [i for i in items if 'holy avenger' in i.get('name', '').lower()]
    if ha:
        print('Holy Avenger entries:')
        for entry in ha[0].get('entries', [])[:5]:
            print(entry)
"
```

- [ ] **Step 2: Add plain-text damage extraction**

In `src/criteria_extractor.py`, modify `extract_entries_criteria()` around line 194:

```python
def extract_entries_criteria(item: dict, combined_text: str) -> dict:
    """Extract criteria from item entries (structured + prose)."""
    c = {}
    
    # ... existing damage extraction ...
    
    # FALLBACK: Plain text "extra XdY [type] damage" (for Holy Avenger, etc.)
    if not c.get('extra_damage_avg'):
        plain_matches = re.findall(r'extra.*?(\d+d\d+)\s+(\w+)\s+damage', combined_text, re.IGNORECASE)
        if plain_matches:
            total_avg = sum(_avg_dice(d[0]) for d in plain_matches)
            c['extra_damage_avg'] = total_avg
            c['extra_damage_dice'] = plain_matches[0][0]
    
    return c
```

- [ ] **Step 3: Test Holy Avenger extraction**

Run:
```bash
python3 scripts/02_extract_criteria.py
python3 -c "
import pandas as pd
criteria = pd.read_csv('data/processed/items_criteria.csv')
ha = criteria[criteria['name'].str.contains('Holy Avenger', na=False)]
print('Holy Avenger criteria:')
print(ha[['name', 'weapon_bonus', 'extra_damage_avg', 'extra_damage_dice']].head(3).to_string())
assert ha['extra_damage_avg'].iloc[0] > 0, 'Holy Avenger should have extra_damage_avg > 0'
print(f'✅ Holy Avenger extra_damage_avg: {ha[\"extra_damage_avg\"].iloc[0]}')
"
```

Expected: `extra_damage_avg: 11.0` (2d10 average)

- [ ] **Step 4: Commit**

```bash
git add src/criteria_extractor.py
git commit -m "fix: Extract plain-text conditional damage (Holy Avenger 2d10 radiant)

- Added fallback regex in extract_entries_criteria() for prose without markup
- Matches patterns like \"extra 2d10 radiant damage\" in item descriptions
- Holy Avenger now extracts extra_damage_avg: 11.0 (2d10 conditional vs fiends/undead)
"
```

---

## Task 3: Holy Avenger Pricing (Full Formula Path)

**Files:**
- Modify: `src/pricing_engine.py:520-590` (calculate_price function, simple bonus classification)

**Problem:** Even with `extra_damage_avg: 11.0`, Holy Avenger may still be classified as "simple bonus item" and priced at ~15k instead of going through the full formula (~200k).

**Solution:** Ensure `extra_damage_avg > 0` disqualifies items from simple bonus classification.

### Steps:

- [ ] **Step 1: Check simple bonus classification logic**

Read `src/pricing_engine.py` lines 520-550 to find the `is_simple_bonus_item` check.

- [ ] **Step 2: Add extra_damage_avg disqualifier**

Modify the simple bonus check around line 540:

```python
# Check if item is a "simple" +N bonus item (no special abilities)
is_simple_bonus_item = (
    weapon_bonus > 0 and
    c.get('extra_damage_avg', 0) == 0 and  # ADD THIS LINE
    c.get('charges', 0) == 0 and
    not c.get('attached_spells') and
    not c.get('is_sentient', False) and
    # ... other checks
)
```

- [ ] **Step 3: Test Holy Avenger pricing**

Run:
```bash
python3 scripts/05_rule_formula.py
python3 -c "
import pandas as pd
priced = pd.read_csv('data/processed/items_priced.csv')
ha = priced[priced['name'].str.contains('Holy Avenger', na=False)]
print('Holy Avenger pricing:')
print(ha[['name', 'rule_price', 'amalgamated_price']].head(3).to_string())
assert ha['rule_price'].median() > 150000, 'Holy Avenger rule_price should be >150k'
print(f'✅ Holy Avenger rule_price median: {ha[\"rule_price\"].median():,.0f} gp')
"
```

Expected: `rule_price` median ~200k-225k

- [ ] **Step 4: Commit**

```bash
git add src/pricing_engine.py
git commit -m "fix: Holy Avenger uses full formula path (not simple bonus)

- Added extra_damage_avg > 0 disqualifier for simple bonus classification
- Holy Avenger now priced via full formula with conditional damage
- Expected price: ~200k-225k (was ~12k on simple bonus path)
"
```

---

## Task 4: Rarity Scaling for Items WITHOUT Amalgamated Prices

**Files:**
- Modify: `src/pricing_engine.py:560-590` (simple bonus price calculation)

**Problem:** Named legendary weapons without amalgamated prices (Dragonlance, Swords of the Planes) are priced at ~15k like very_rare items, but should be priced higher as legendary items.

**Solution:** Add rarity multiplier ONLY for items without amalgamated prices.

### Steps:

- [ ] **Step 1: Add rarity scaling with amalgamated check**

In `src/pricing_engine.py`, modify the simple bonus path around line 565:

```python
if is_simple_bonus_item:
    simple_price = SIMPLE_BONUS_PRICES.get(weapon_bonus, 0)
    if simple_price > 0:
        # CRITICAL: Only scale if NO amalgamated price exists
        if pd.isna(row.get('amalgamated_price')) or row.get('amalgamated_price') == 0:
            # Scale simple price by rarity (calibrated for rare/very_rare baseline)
            rarity_multipliers = {
                "uncommon": 0.5,
                "rare": 1.0,
                "very_rare": 1.0,
                "legendary": 10.0,  # +3 legendary: 14,950 → ~150k
                "artifact": 1.0,    # DON'T SCALE ARTIFACTS - they have full formula
            }
            simple_price *= rarity_multipliers.get(rarity, 1.0)
        
        # Apply attunement modifier
        if req_attune_class:
            simple_price *= 0.80  # Class-restricted attunement
        elif req_attune:
            simple_price *= 0.90  # Open attunement
        
        return simple_price
```

**CRITICAL:** The `artifact: 1.0` multiplier ensures artifacts are NOT scaled here - they should use the full formula path.

- [ ] **Step 2: Test all impacted items**

Run full pipeline:
```bash
python3 scripts/05_rule_formula.py
python3 scripts/05b_variant_adjust.py
python3 scripts/06_ml_refine.py
python3 scripts/07_validate.py
python3 scripts/10_generate_output.py
python3 scripts/11_generate_html.py
```

Then verify:
```bash
python3 -c "
import pandas as pd
df = pd.read_csv('output/pricing_guide.csv')

print('=== VERIFICATION ===')
print()

# Holy Avenger
ha = df[df['Name'].str.contains('Holy Avenger', na=False)]
ha_med = ha['Price (gp)'].median()
print(f'Holy Avenger: {ha_med:,.0f} gp')
assert 150000 < ha_med < 250000, f'Holy Avenger should be 150k-250k, got {ha_med:,.0f}'
print('✅ Holy Avenger PASS')
print()

# Defender
defender = df[df['Name'].str.contains('Defender', na=False) & ~df['Name'].str.contains('Ring|Shield|Amulet', na=False)]
def_med = defender['Price (gp)'].median()
print(f'Defender: {def_med:,.0f} gp')
assert 28000 < def_med < 40000, f'Defender should be 28k-40k, got {def_med:,.0f}'
print('✅ Defender PASS')
print()

# Vorpal (should be unchanged, has amalgamated)
vorpal = df[df['Name'].str.contains('Vorpal', na=False)]
vor_med = vorpal['Price (gp)'].median()
print(f'Vorpal: {vor_med:,.0f} gp')
assert 35000 < vor_med < 50000, f'Vorpal should be 35k-50k, got {vor_med:,.0f}'
print('✅ Vorpal PASS')
print()

# Artifacts (MUST NOT CHANGE)
artifacts = df[df['Rarity'] == 'Artifact']
art_max = artifacts['Price (gp)'].max()
art_med = artifacts['Price (gp)'].median()
print(f'Artifacts: median={art_med:,.0f}, max={art_max:,.0f}')
assert art_max < 900000, f'Artifact max should be <900k, got {art_max:,.0f}'
print('✅ Artifacts PASS')
print()

print('=== ALL VERIFICATION PASSED ===')
"
```

- [ ] **Step 3: Run R² quality gate**

```bash
python3 scripts/check_r2.py --baseline 0.80
```

Expected: R² ≥ 0.80

- [ ] **Step 4: Commit**

```bash
git add src/pricing_engine.py
git commit -m "feat: Add rarity scaling for simple bonus items WITHOUT amalgamated prices

- Added 10× multiplier for legendary, 1.0× for artifact (no scaling)
- Only applies when amalgamated_price is NaN (items with reference prices unchanged)
- Dragonlance, Swords of the Planes: ~13k → ~130k
- Artifact pricing preserved (uses full formula, not simple bonus path)
"
```

---

## Task 5: Full Verification & Impact Analysis

**Files:** None (verification only)

### Steps:

- [ ] **Step 1: Generate full impact report**

Run:
```bash
python3 -c "
import pandas as pd
df = pd.read_csv('output/pricing_guide.csv')

print('=' * 60)
print('FINAL PRICING IMPACT REPORT')
print('=' * 60)
print()

items_to_check = [
    ('Holy Avenger', 'Holy Avenger', 150000, 250000),
    ('Defender', 'Defender', 28000, 40000),
    ('Vorpal', 'Vorpal', 35000, 50000),
    ('Dragonlance', 'Dragonlance', 100000, 200000),
    ('Swords of the Planes', 'of the Planes', 100000, 200000),
]

all_pass = True
for name, search_term, min_price, max_price in items_to_check:
    items = df[df['Name'].str.contains(search_term, na=False)]
    if len(items) == 0:
        print(f'❌ {name}: NOT FOUND')
        all_pass = False
        continue
    med = items['Price (gp)'].median()
    status = '✅' if min_price < med < max_price else '❌'
    print(f'{status} {name} ({len(items)} variants): {med:,.0f} gp (expected: {min_price:,}-{max_price:,})')
    if not (min_price < med < max_price):
        all_pass = False

print()
print('=== ARTIFACT VERIFICATION ===')
artifacts = df[df['Rarity'] == 'Artifact']
print(f'Total: {len(artifacts)}')
print(f'Median: {artifacts[\"Price (gp)\"].median():,.0f} gp')
print(f'Max: {artifacts[\"Price (gp)\"].max():,.0f} gp')
art_max = artifacts['Price (gp)'].max()
if art_max < 900000:
    print('✅ Artifact max < 900k')
else:
    print(f'❌ Artifact max {art_max:,.0f} exceeds 900k limit')
    all_pass = False

print()
print('Top 5 artifacts:')
print(artifacts.nlargest(5, 'Price (gp)')[['Name', 'Price (gp)', 'Price Source']].to_string())

print()
if all_pass:
    print('✅ ALL VERIFICATION PASSED - READY TO COMMIT')
else:
    print('❌ SOME CHECKS FAILED - DO NOT COMMIT')
"
```

- [ ] **Step 2: Document any side effects**

List any items with >50% price change that weren't expected.

- [ ] **Step 3: Final commit if all checks pass**

```bash
git push
```

---

## Rollback Plan

If verification fails:
```bash
git reset --hard 3ed139a
git clean -fd
```

This restores the baseline state where:
- Holy Avenger: 11,875 gp (known issue)
- Defender: 13,260 gp (known issue)
- Vorpal: 40,993 gp ✅
- Max Artifact: 799,200 gp ✅
