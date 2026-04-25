# Pricing Guide Review Plan

> Generated: 2026-04-24 | Current R²: ~0.96 | Pipeline: Idempotent ✅

---

## Executive Summary

The pricing guide is in **good health**. All known bugs have been fixed, the pipeline is idempotent, R² is strong at 0.96, and most automated pre-checks pass clean. However, Phase 0 automated analysis identified **301 items flagged for review** across 5 categories. None are critical, but they represent the remaining polish work.

### Completed Work (All Committed & Pushed)
- Holy Avenger (~213k GP), Defender (31.5k GP), Artifact tiers (250k-1M)
- Belt of Giant Strength, Bloodrage Greataxe, Winged Bolt blocklists
- Dragon Slayer, Giant Slayer, Of Wounding special-case matchers
- Hag-Stitched charge diminishing, Ammunition pricing
- Monster Hunter blocklist (MH +3: 14k→46k GP)
- Plate Armor of Gleaming (330→1,650), Spiked Armor (1→75)
- Variant spacing idempotency, Armor floor enforcement

### Automated Pre-Checks (Phase 0) — Results

| Check | Items Flagged | Status |
|-------|:------------:|:------:|
| Rarity hierarchy violations | **0** ✅ | Clean |
| Algorithm-only Legendary/Artifact | **0** ✅ | Clean |
| Below mundane base price | **0** ✅ | Clean |
| Sub-1gp non-ammunition items | **0** ✅ | Clean |
| **Variant family outliers** (CV > 0.3) | **88** ⚠️ | Review needed |
| **Amalgamated deviation >50%** | **75** ⚠️ | Review needed |
| **Round prices** (possible placeholders) | **106** ℹ️ | Low severity |
| **Unknown rarity items** | **29** ℹ️ | Needs classification |
| **Ceiling proximity (>900k GP)** | **3** ℹ️ | Review needed |

---

## Phase 1: Variant Family Consistency Audit

**Priority:** High  
**Items affected:** 88 outliers across +N weapon/armor families  
**Effort:** ~1 session

### The Problem
Variant families (e.g., all "+1 Weapon" items) show very high coefficient of variation:
- weapon+1 family: **CV = 6.9** (should be <0.3)
- armor+1 family: **CV = 0.88**
- weapon+3 family: **CV = 2.1**

### Root Cause (from analysis)
Named legendary weapons (Luck Blade, Moonblade, Holy Avenger, etc.) are being **grouped into generic +N families** because they share a `weapon_bonus: +1/+2/+3` property. But these items have massive additional properties justifying much higher prices. They're not "variants" — they're unique named items that happen to have a +N bonus.

### Checklist
- [ ] Exclude named legendary items (Holy Avenger, Moonblade, Luck Blade, Defender, Vorpal, etc.) from generic +N variant family calculations
- [ ] Verify CV drops below 0.3 for all standard weapon/armor families
- [ ] Confirm that legitimate +N items (generic +1/+2/+3 weapons/armor) still show proper differentiation (dagger < longsword < greatsword)

### Success Criteria
- weapon+1 family CV < 0.3
- armor+1 family CV < 0.3
- No legitimate +N items excluded from grouping

---

## Phase 2: Amalgamated Price Deviation Audit

**Priority:** High  
**Items affected:** 75 where rule_price deviates >50% from amalgamated_price  
**Effort:** ~1-2 sessions

### The Problem
75 items have a significant gap between their algorithmic price and their amalgamated reference price. Some of these may be:
- Items with special properties the algorithm overvalues
- Items where amalgamation is wrong (like Monster Hunter was)
- Items where the algorithm correctly identifies value that reference sources don't capture

### Checklist
- [ ] Review each flagged item (or sample) to categorize the deviation
- [ ] Determine if the deviation is justified (special properties) or a bug
- [ ] Fix any false amalgamations (add blocklist/special case)
- [ ] Fix any algorithmic overvaluation (tune additives)

### Known Examples (from prior work)
- **Monster Hunter weapons** (now fixed): algorithm correctly values concentration-free spells
- **Drow +N items**: lower price due to sunlight sensitivity — may be justified
- **Rod of the Pact Keeper / Arcane Grimoire**: algorithm adds spell attack bonus on top of guide prices — may be double-counting

### Success Criteria
- All deviations understood and categorized
- ≤5 items with unexplained deviation
- Fix any confirmed bugs

---

## Phase 3: Ceiling Proximity Review

**Priority:** Medium  
**Items affected:** 3 (Rod of Seven Parts, Sword of Kas, Wand of Orcus)  
**Effort:** ~30 min

### The Items

| Item | Price | Tier |
|------|-------|------|
| Rod of Seven Parts | ~985,000 GP | S (sub-score 0.95) |
| Sword of Kas | ~970,000 GP | S (sub-score 0.90) |
| Wand of Orcus | ~970,000 GP | S (sub-score 0.90) |

### Checklist
- [ ] Verify S-tier pricing is appropriate relative to peer S artifacts
- [ ] Are these 3 the "right" items to be at the ceiling?
- [ ] Is the distribution within the S tier (700k-1M) reasonable?

---

## Phase 4: Round Price / Placeholder Check

**Priority:** Low  
**Items affected:** 106 items with suspiciously round prices  
**Effort:** ~30 min

### Examples
Items ending in .00, .50, specific round numbers that may indicate:
- Hardcoded or estimated prices that weren't refined
- Data entry artifacts
- Genuinely round prices (some official prices ARE round numbers)

### Checklist
- [ ] Sample 20-30 items to check if round prices are justified
- [ ] Flag any that look like placeholder values
- [ ] No action needed for well-understood cases

---

## Phase 5: Unknown Rarity Classification

**Priority:** Medium  
**Items affected:** 29 items with "Unknown" rarity  
**Effort:** ~1 session

### The Problem
Items without rarity classification get algorithm-only pricing, which may not be calibrated correctly. Some may be data errors (items missing rarity in source material).

### Checklist
- [ ] Review each of the 29 items
- [ ] Assign correct rarity based on item description and comparable items
- [ ] If rarity cannot be determined, note for future data-source improvement
- [ ] After rarity assignment, re-run pipeline to see if pricing improves

---

## Phase 6: Amalgamation Gap Audit

**Priority:** Medium  
**Items affected:** Unknown (need to identify items that SHOULD have amalgamated prices but don't)  
**Effort:** ~1 session

### Background
Previous issues (Dragon Slayer, Giant Slayer, "of Wounding") were all cases where items should have matched to reference sources but didn't due to fuzzy matching limitations. There may be more.

### Checklist
- [ ] Run a cross-reference: items with no amalgamated price whose name/type suggests a reference source should have a matching entry
- [ ] Compare reference source item lists to current amalgamation coverage
- [ ] Add special-case matchers or fuzzy matching improvements for misses
- [ ] Check for false negatives in the amalgamator's generic fallback path

---

## Phase 7: Floor Violation Audit

**Priority:** Low  
**Items affected:** 10 pre-existing known violations  
**Effort:** ~30 min

### Background
10 items remain below their floor price. These are "intentional" edge cases — items with unusual rarity/type combinations where the floor logic doesn't cleanly apply.

### Checklist
- [ ] Review all 10 violations
- [ ] Document why each is exempted (or fix if fixable)
- [ ] Confirm none are regressions from recent changes

---

## Phase 8: Statistical Spot-Check

**Priority:** Medium  
**Items affected:** ~50-100 sampled across rarity/type  
**Effort:** ~1 session

### Method
1. Stratified random sample: pick 10 items from each rarity tier
2. Manual sanity check each:
   - Does the price feel right for its properties?
   - Does it compare well to similar items?
   - Does the price source match expectations?
3. If >10% of sampled items seem off → broader investigation needed

---

## Issue Tracker Cleanup

### Open Issues
| Issue | Status | Recommended Action |
|-------|--------|-------------------|
| `pricing_guide_v2-7xw` (Manual review) | Open, P3 | **Keep open** — this plan is its execution |
| `pricing_guide_v2-dss` (Artifact creep) | In Progress | **Close** — fixed, artifact median 413k ✅ |
| `pricing_guide_v2-dyl` (Holy Avenger) | In Progress | **Close** — fixed at ~213k ✅ |
| `pricing_guide_v2-8o3` (Consumable multipliers) | Open, P1 | **Close** — already implemented ✅ |

---

## Prioritized Execution Order

### Must Do (High Priority)
1. **Phase 1** — Fix variant family grouping (CV pollution from named items) — ~1 session
2. **Phase 2** — Review 75 amalgamated deviations — ~1-2 sessions

### Should Do (Medium Priority)
3. **Phase 5** — Classify 29 unknown rarity items — ~1 session
4. **Phase 6** — Identify amalgamation gaps — ~1 session
5. **Phase 8** — Statistical spot-check — ~1 session

### Nice to Do (Low Priority)
6. **Phase 3** — Ceiling proximity review — ~30 min
7. **Phase 4** — Round price check — ~30 min
8. **Phase 7** — Floor violation audit — ~30 min

**Total estimated effort:** ~5-8 focused sessions

---

## Success Criteria

The review is complete when:

| Criteria | Target | How to Measure |
|----------|--------|----------------|
| Variant family CV | <0.3 for all standard +N families | `variant_consistency_report.csv` |
| Unexplained amalgamated deviations | ≤5 items | Manual audit log |
| Unknown rarity items | 0 remaining | Count of `rarity="Unknown"` |
| Floor violations | ≤10 (documented exceptions) | `floor_violations.csv` |
| Sampled item accuracy | ≥90% seem reasonable | Spot-check results |
| R² | ≥0.95 (no regression) | Anomaly report |
| Open issues | Only `pricing_guide_v2-7xw` (closed when review done) | `bd list --json` |
