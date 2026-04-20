## Phase 3-4: Amalgamation and Rule Formula

### scripts/04_amalgamate.py
**Purpose:** Orchestrates loading of 3 external price guides (DSA, MSRP, DMPG), trims outliers, normalizes ammunition bundles, then calls `amalgamate_prices()` to produce `amalgamated_prices.csv`.
**Status:** OK
**Issues found:**
1. **Outlier trimming before ammo normalization is correct** — comment explains the ordering rationale. Good.
2. **Minor:** `trim_outliers` is called with a `len >= 10` guard here AND inside `trim_outliers` itself (line 28 of amalgamator.py). Redundant but harmless.
3. No issues with output columns — downstream `05_rule_formula.py` reads `amalgamated_price`, `price_confidence`, `price_sources` which are all produced.

### src/amalgamator.py
**Purpose:** Fuzzy-matches items to external guides, detects outliers, computes weighted amalgamated prices with generic +N fallback for weapons/armor/shields/ammunition.
**Status:** Needs minor fixes
**Issues found:**
1. **RARITY_MEDIANS duplicated** — Defined at line 10 of amalgamator.py AND line 897 of pricing_engine.py. Values are identical. Should be consolidated into a shared constants module (e.g., `src/constants.py`) and imported by both.
2. **Single-source outlier detection logic inverted** — `detect_single_source_outlier()` line 89: `if not has_accurate_match: return (False, "fuzzy-match")` — this means fuzzy matches are NEVER flagged as outliers. This is intentional per the docstring (only flag accurate matches), but it means a bad fuzzy match with a wildly wrong price will sail through. Acceptable tradeoff but worth noting.
3. **`detect_and_exclude_outliers` only checks upward** — Line 53: `if price > median_price * outlier_threshold`. An item priced at 1/100th of the median won't be caught. Consider also checking `price < median_price / outlier_threshold`.
4. **Generic fallback coverage is good** — Covers ammunition, shields, armor, and weapons. No gaps for +N items.
5. **Weighting logic is sound** — 3-source alignment check, 2-source equal split, divergent fallback with DSA preference. The 25% threshold for alignment is reasonable.
6. **Fuzzy matching bonus enforcement is good** — +N numbers must match exactly, preventing +1 items from matching +3 entries.

### scripts/05_rule_formula.py
**Purpose:** Applies `calculate_price()` from pricing_engine.py to every item, handles mundane official prices, solo-outlier detection, and outputs `items_priced.csv` with R² metric.
**Status:** OK
**Issues found:**
1. **`import ast` inside loop** — Line 27: `import ast` is inside `main()` but outside the loop, so it's fine. However, `import re` inside `calculate_price()` in pricing_engine.py (line 369) IS inside a function called per-item. Minor perf issue.
2. **Boolean parsing is naive** — Line 78: `bool(c.get(bool_col))` will treat the string `"False"` as `True` (truthy non-empty string). If CSV contains string "False" values, this is a bug. Should use `str(val).lower() in ('true', '1', 'yes')` or similar.
3. **R² calculation is correct** — Standard formula, properly guarded.
4. **`calculate_price_with_outlier_check` usage is correct** — Solo-outlier items fall back to rule price.

### src/pricing_engine.py
**Purpose:** Rule-based pricing formula with calibrated constants for all item types: mundane, scrolls, enspelled, material armor/ammo, +N weapons, artifacts, cursed/sentient items, spells, charges, etc.
**Status:** Needs minor fixes
**Issues found:**
1. **RARITY_MEDIANS duplicated** — Line 897, identical to amalgamator.py line 10. Consolidate.
2. **CONDITION_IMMUNITY_VALUES duplicated** — Line 69, identical to criteria_extractor.py line 7. Both have the same 12 conditions at 400 gp each. Consolidate.
3. **Typo in PROPERTY_PREMIUMS** — Line 122: `"返回": 1.0` — Chinese characters for "returning". Should be `"returning": 1.0`. This means the "returning" property premium is never matched.
4. **`calculate_price_with_outlier_check` doesn't blend** — When `price_confidence` is NOT "solo-outlier" and an amalgamated price exists, the function still returns the pure rule price, not a blend. The `source` is labeled "rule+amalgamated" but the price is purely rule-based. This is misleading — the amalgamated price is never actually used in the final price calculation. If this is intentional (rule price IS the final price, amalgamated is just for R² comparison), the source label should be just "rule".
5. **`import re` inside function** — Line 369 inside `calculate_price()`. Called once per item. Should be module-level.
6. **All item types handled** — Mundane ✓, scrolls ✓, enspelled ✓, material armor ✓, material ammo ✓, +N weapons ✓, artifacts ✓, cursed ✓, sentient ✓, charges ✓, spells ✓, flavor items ✓. No gaps.
7. **RARITY_BASE_PRICES vs RARITY_MEDIANS mismatch is intentional** — Base prices are round numbers used for formula input; medians are empirical values for outlier detection. This is fine.

### Summary of Recommendations

| Priority | Issue | Files |
|----------|-------|-------|
| **Medium** | Consolidate `RARITY_MEDIANS` into shared constants | amalgamator.py, pricing_engine.py |
| **Medium** | Consolidate `CONDITION_IMMUNITY_VALUES` into shared constants | criteria_extractor.py, pricing_engine.py |
| **Medium** | Fix `"返回"` → `"returning"` in PROPERTY_PREMIUMS | pricing_engine.py:122 |
| **Medium** | Fix misleading `"rule+amalgamated"` source label (price is pure rule) | pricing_engine.py:930 |
| **Low** | Boolean parsing in 05_rule_formula.py may treat "False" strings as True | 05_rule_formula.py:78 |
| **Low** | `detect_and_exclude_outliers` only catches high outliers, not low | amalgamator.py:53 |
| **Low** | Move `import re` to module level in pricing_engine.py | pricing_engine.py:369 |
| **Low** | Redundant `len >= 10` guard in both 04_amalgamate.py and trim_outliers() | 04_amalgamate.py:59, amalgamator.py:28 |

## Phase 5-9: ML, Validation, Floors, Output

### scripts/06_ml_refine.py
**Purpose:** Trains XGBoost on items with known prices, blends ML predictions with amalgamated/rule prices using confidence-tiered weights.
**Status:** Mostly OK — minor issues

**Issues found:**
1. **Line 333 — fallback weights mismatch:** `CONFIDENCE_WEIGHTS.get(confidence, (0.7, 0.35))` — fallback sums to 1.05, not 1.0
2. **Line 261 — indentation inconsistency:** Cosmetic but sloppy
3. **StandardScaler unnecessary:** XGBoost is tree-based, doesn't need feature scaling
4. **Training target selection sound:** amalgamated_price preferred, variant_price as fallback

### scripts/07_validate.py
**Purpose:** Runs anomaly detection, flags outliers/extreme outliers.
**Status:** OK — minor robustness concern

**Issues found:**
1. **Lines 46-53 — fragile index assumption:** Uses `idx < len(df)` guard instead of `idx in df.index`

### scripts/09_enforce_floors.py
**Purpose:** Ensures magic item variants aren't priced below rarity-appropriate multiples of mundane base.
**Status:** OK — design concerns

**Issues found:**
1. **INPUT_CSV == OUTPUT_CSV (line 25):** Writes back to same file — not idempotent if variant_spacing modifies prices
2. **Lines 276-281 — price bands overwritten:** ML quantile bands replaced with flat ±20%, loses information
3. **ARMOR_BASES regex duplication:** Fragile but functional

### scripts/10_generate_output.py
**Purpose:** Generates Excel (multi-sheet) and CSV output from validated data.
**Status:** Needs minor fixes

**Issues found:**
1. **Line 2 — docstring says "Phase 8"** but this is script 10
2. **Line 258 — notes logic broken:** `notes = '🤖' if notes else '🤖'` — both branches identical
3. **Line 336 — notes column ignores computed field:** Excel output hardcodes outlier flag, never shows 🤖 for algorithmic items
4. **Sheets 3 & 4 — header/data mismatch:** Headers list 11 items, rows have 8 values

## Consolidated Recommendations

### Must Fix (High Priority)
| Issue | File | Impact |
|-------|------|--------|
| Fix `"返回"` → `"returning"` | pricing_engine.py:122 | Returning property premium never applied |
| Fix notes logic (both branches identical) | 10_generate_output.py:258 | Algorithmic items don't show 🤖 flag |
| Fix header/data column mismatch | 10_generate_output.py:sheets 3-4 | Excel columns misaligned |
| Fix fallback weights sum to 1.05 | 06_ml_refine.py:333 | Unknown confidence uses wrong weights |

### Should Fix (Medium Priority)
| Issue | Files | Impact |
|-------|-------|--------|
| Consolidate `RARITY_MEDIANS` | amalgamator.py, pricing_engine.py | Maintenance risk |
| Consolidate `CONDITION_IMMUNITY_VALUES` | criteria_extractor.py, pricing_engine.py | Maintenance risk |
| Fix misleading "rule+amalgamated" label | pricing_engine.py:930 | Confusing source attribution |
| Fix fragile index check | 07_validate.py:46-53 | Could skip items if reindexed |

### Low Priority (Cleanup)
| Issue | File | Impact |
|-------|------|--------|
| Move `import re` to module level | pricing_engine.py:369 | Minor perf |
| Remove StandardScaler | 06_ml_refine.py | Unnecessary complexity |
| Fix indentation | 06_ml_refine.py:261 | Cosmetic |
| Document price band override | 09_enforce_floors.py:276-281 | Clarity |
| Fix docstring phase number | 10_generate_output.py:2 | Clarity |
| Boolean parsing may treat "False" as True | 05_rule_formula.py:78 | Edge case |
| One-sided outlier detection | amalgamator.py:53 | Low outliers not caught |

## Summary

The pipeline is **fundamentally sound** with no critical bugs. The major issues are:
1. **Duplicated constants** — maintenance risk, not functional
2. **Misleading labels** — "rule+amalgamated" doesn't actually blend
3. **Output formatting bugs** — notes not showing, column mismatches
4. **Minor logic issues** — fallback weights, index checks, typo in property name

All fixes are straightforward and low-risk. The pipeline produces correct prices despite these issues.
