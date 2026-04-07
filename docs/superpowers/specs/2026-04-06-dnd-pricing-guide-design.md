# D&D 5e Item Pricing Guide v2 — Design Specification

**Date:** 2026-04-06  
**Status:** Approved  
**Working directory:** `/Users/ryan/OpenCode/TTRPG/pricing_guide_v2/`

---

## 1. Project Goal

Create an objective, data-driven pricing algorithm for all D&D 5e mundane and magic items found in:
- All Standard Sources on 5e.tools (9,422 items total)
- Dungeons of Drakkenheim + Monsters of Drakkenheim
- All Eberron sources (Eberron: Rising from the Last War, Exploring Eberron 2024, etc.)

The algorithm must assign consistent, reproducible prices to any item — including homebrewed items — using only objective, fact-based criteria derivable from the item's own description. No subjective scoring allowed.

**Deliverables:**
- `output/pricing_guide.xlsx` — Excel spreadsheet with 5e.tools hyperlinks, formatted columns, conditional formatting
- `output/pricing_guide.csv` — Machine-readable backup

---

## 2. Input Data

- **Primary:** `/Users/ryan/OpenCode/TTRPG/pricing_guide_v2/items-sublist-data.json` (9,422 items)
- **Markdown descriptions:** `/Users/ryan/OpenCode/TTRPG/pricing_guide_v2/items-sublist.md`
- **External price guides:**
  - DSA (Dump Stat Adventures): https://docs.google.com/spreadsheets/d/1xckMUATltAexbI6H5JVd1sFagaxjto78wV1alj3WUwE
  - MSRP (Merchant's Sorcerous Rarities Pricelist): https://docs.google.com/spreadsheets/d/11-45kA6qWTFV_rDYkD49B_EQfF0kPrW2tXwQcNs1jVM
  - DMPG (Discerning Merchant's Price Guide): `~/Downloads/DMPG.pdf`
- **Prior project reference:** `/Users/ryan/OpenCode/TTRPG/pricing_guide_2/` (see data/raw/, output/)

---

## 3. Architecture

Python pipeline with 8 phases. Each phase is a standalone script in `scripts/`. Shared logic lives in `src/`.

```
pricing_guide_v2/
├── items-sublist-data.json     # Input: 9422 items
├── items-sublist.md            # Input: prose descriptions
├── scripts/
│   ├── 01_extract_items.py     # Phase 1: Parse JSON into master list
│   ├── 02_extract_criteria.py  # Phase 2: Extract all objective criteria
│   ├── 03_ingest_external.py   # Phase 3: Fetch/parse DSA, MSRP, DMPG
│   ├── 04_amalgamate.py        # Phase 4: Trim, match, weighted mean
│   ├── 05_rule_formula.py      # Phase 5: Rule-based formula baseline
│   ├── 06_ml_refine.py         # Phase 6: ML coefficient refinement
│   ├── 07_validate.py          # Phase 7: Validation & anomaly detection
│   └── 08_generate_output.py   # Phase 8: Excel + CSV generation
├── src/
│   ├── criteria_extractor.py   # JSON field + NLP prose extraction
│   ├── pricing_engine.py       # Formula calculation
│   ├── amalgamator.py          # Price amalgamation logic
│   ├── fuzzy_matcher.py        # Item name matching across guides
│   └── utils.py                # Shared utilities
├── data/
│   ├── raw/                    # External guide CSVs (raw)
│   └── processed/              # Intermediate outputs
├── output/
│   ├── pricing_guide.xlsx      # Final Excel output
│   └── pricing_guide.csv       # Final CSV output
├── docs/
│   └── superpowers/specs/      # This spec
├── tests/                      # Unit tests for each module
├── PROJECT_CONTEXT.md          # Living context document (always updated)
├── CRITERIA.md                 # Variable documentation
└── requirements.txt
```

---

## 4. Phase Descriptions

### Phase 1: Item Extraction
- Parse `items-sublist-data.json` → `data/processed/items_master.csv`
- Normalize all item types, rarities, and source codes
- Handle variant items (e.g., "+1 Longsword" as a variant of "Longsword")
- Tag items with official prices (use `value` field directly — no algorithm needed)
- Handle "unknown (magic)" and "varies" rarities

### Phase 2: Criteria Extraction
- Extract all objective criteria from JSON fields (see Section 5)
- Run NLP on prose entries for criteria not in structured fields
- Output: `data/processed/items_criteria.csv`
- Must process ALL 9,422 items

### Phase 3: External Price Ingestion
- **DSA:** Fetch Google Sheets (gid=0), parse item names and prices
- **MSRP:** Fetch Google Sheets, take average of "low magic" and "high magic" columns
- **DMPG:** Parse `~/Downloads/DMPG.pdf`, extract item/price table
- Output: `data/raw/dsa_prices.csv`, `msrp_prices.csv`, `dmpg_prices.csv`

### Phase 4: Price Amalgamation
- For each guide: trim the most expensive 2% and cheapest 2% of items
- Fuzzy-match item names across guides (threshold: 85% similarity)
- For items present in multiple guides, compute weighted mean:
  - If two guides cluster closely (within 25% of each other) and one is outlier: weight the two 40/40/20
  - If all three are close: weight evenly 33/33/33
  - If all three diverge: weight 40/30/30 favoring DSA (most documented methodology)
- Items in only one guide: use that price with a solo-source flag
- Output: `data/processed/amalgamated_prices.csv`

### Phase 5: Rule-Based Formula
- Implement formula from Section 6 as starting point
- Produce initial prices for all 9,422 items
- Calculate R² and RMSE against amalgamated ground truth
- **Peer Review Checkpoint #1:** @oracle reviews formula design and initial results

### Phase 6: ML Coefficient Refinement
- Use gradient boosting regression (XGBoost or sklearn) to refine additive bonus values
- Train on items that have amalgamated prices (ground truth)
- Validate on held-out set (20% of matched items)
- Preserve rule-based structure; ML refines the magnitude of individual bonuses
- Target: R² ≥ 0.80, outlier rate < 15% per rarity tier
- **Peer Review Checkpoint #2:** @oracle reviews ML coefficients and accuracy metrics

### Phase 7: Validation & Anomaly Detection
- Run anomaly detector on all 9,422 priced items
- Flag items >3x or <0.3x their rarity median
- Cross-check items with official canonical prices (value field)
- Generate `output/anomaly_report.md`

### Phase 8: Output Generation
- Excel: Item Name (hyperlinked to 5e.tools), Rarity, Type, Source, Price (gp), Attunement, Price Source (official/amalgamated/algorithm)
- Conditional formatting: color-code by rarity tier
- CSV: same columns, no formatting
- **Peer Review Checkpoint #3:** @oracle performs final quality review

---

## 5. Criteria Variables

### 5a. From Structured JSON Fields

| Variable | Source Field | Description |
|----------|-------------|-------------|
| `rarity` | `rarity` | Item rarity tier |
| `item_type` | `type` | 5e.tools type code |
| `official_price_gp` | `value` | Official canonical price (÷100 since value is in cp) |
| `req_attune` | `reqAttune` | Attunement required |
| `req_attune_class` | `reqAttune` (string) | Class-restricted attunement |
| `weapon_bonus` | `bonusWeapon` | Overall weapon enhancement bonus |
| `weapon_attack_bonus` | `bonusWeaponAttack` | Attack-only weapon bonus |
| `weapon_damage_bonus` | `bonusWeaponDamage` | Damage-only weapon bonus |
| `ac_bonus` | `bonusAc` | AC enhancement bonus |
| `saving_throw_bonus` | `bonusSavingThrow` | Saving throw bonus |
| `ability_check_bonus` | `bonusAbilityCheck` | Ability check bonus |
| `proficiency_bonus_bonus` | `bonusProficiencyBonus` | Proficiency bonus modifier |
| `spell_attack_bonus` | `bonusSpellAttack` | Spell attack roll bonus |
| `spell_save_dc_bonus` | `bonusSpellSaveDc` | Spell save DC bonus |
| `spell_damage_bonus` | `bonusSpellDamage` | Spell damage bonus |
| `damage_resistances` | `resist` | List of damage types resisted |
| `damage_immunities` | `immune` | List of damage types immune to |
| `damage_vulnerabilities` | `vulnerable` | List of damage types vulnerable to |
| `condition_immunities` | `conditionImmune` | List of conditions immune to |
| `ability_score_mods` | `ability` | Ability score bonuses/sets |
| `attached_spells` | `attachedSpells` | Spells (charges, daily, unlimited) |
| `spell_scroll_level` | `spellScrollLevel` | Spell scroll level (0-9) |
| `charges` | `charges` | Number of charges |
| `recharge` | `recharge` | Recharge condition (dawn, dusk, etc.) |
| `recharge_amount` | `rechargeAmount` | Charges regained on recharge |
| `speed_mods` | `modifySpeed` | Speed modifications (fly/swim/climb/burrow) |
| `is_sentient` | `sentient` | Sentient item |
| `is_cursed` | `curse` | Cursed item |
| `is_tattoo` | `tattoo` | Tattoo item |
| `item_tier` | `tier` | Minor/major tier |
| `stealth_penalty` | `stealth` | Stealth disadvantage on armor |
| `strength_req` | `strength` | Strength requirement on armor |
| `crit_threshold` | `critThreshold` | Modified critical hit range |
| `is_focus` | `focus` | Spellcasting focus type |
| `is_poison` | `poison` | Poison item |
| `weapon_properties` | `property` | Weapon properties list |
| `base_damage_dice` | `dmg1`, `dmg2` | Base weapon damage |
| `damage_type` | `dmgType` | Damage type |
| `weapon_range` | `range` | Ranged weapon range |
| `is_wondrous` | `wondrous` | Wondrous item flag |
| `is_ammunition` | type=A | Ammunition type |
| `is_shield` | type=S | Shield type |
| `is_firearm` | `firearm` | Firearm flag |

### 5b. From Prose (NLP Extraction)

| Variable | Detection Method |
|----------|-----------------|
| `healing_daily_hp` | "regain/restore" + HP amount + "dawn/day/per day" |
| `healing_consumable_hp` | is_consumable + HP amount regex |
| `healing_permanent_hp` | Non-consumable permanent healing |
| `flight_full` | "flying speed" + no restrictions |
| `flight_limited` | "flying speed" + time/condition restriction |
| `darkvision_feet` | "darkvision" + distance regex |
| `stealth_advantage` | "advantage" + "stealth" + "dexterity" |
| `crit_immunity` | "critical hit" + "normal hit/treated as" |
| `concentration_free` | "doesn't require concentration" |
| `teleportation` | "teleport" keyword |
| `invisibility_atwill` | "invisible" + "action/bonus action" (non-spell) |
| `wish_effect` | "wish" spell or wish-equivalent |
| `spell_absorption` | "absorb/negate" + "spell" |
| `advantage_checks` | "advantage on" + check type |
| `disadvantage_removal` | "no disadvantage" or "removes disadvantage" |
| `strength_req_removed` | base_obj.strength field + "no longer applies" |
| `multi_dose` | "doses/uses/charges" count in consumables |
| `tome_manual_boost` | "manual/tome" in name + permanent stat boost |
| `class_restriction_attune` | "only [class]" + "attune" |
| `burrow_speed` | "burrowing speed" regex |
| `truesight` | "truesight" keyword |
| `blindsight` | "blindsight" keyword |
| `tremorsense` | "tremorsense" keyword |
| `legendary_resistance` | "legendary resistance" effect |
| `spell_immunity` | Immune to specific spell or school |

---

## 6. Pricing Formula

### 6a. Base Prices by Rarity

| Rarity | Base Price (gp) | Price Floor (gp) | Consumable Floor (gp) |
|--------|----------------|------------------|-----------------------|
| Mundane (official price) | Use `value` field | — | — |
| Mundane (no official price) | 1 gp | 1 | 1 |
| Common | 500 | 50 | 25 |
| Uncommon | 2,500 | 100 | 50 |
| Rare | 20,000 | 500 | 250 |
| Very Rare | 100,000 | 5,000 | 2,500 |
| Legendary | 500,000 | 50,000 | 25,000 |
| Artifact | 1,500,000 | 500,000 | — |
| Unknown (magic) | Estimated from criteria | Rarity guess | — |

### 6b. Multiplicative Modifiers

| Condition | Multiplier |
|-----------|-----------|
| Attunement (open) | ×0.85 |
| Attunement (class-restricted, 1 class) | ×0.75 |
| Attunement (alignment-restricted) | ×0.80 |
| Consumable: Potion | ×0.50 |
| Consumable: Scroll | ×0.20 |
| Consumable: Ammunition (single) | ×0.05 |
| Consumable: Multi-dose (per dose) | ×0.30 per dose |
| Material: Mithral | ×2.00 |
| Material: Adamantine | ×2.50 |
| Cursed item | ×0.70 |
| Sentient item | ×1.25 |
| Is Shield (vs armor, for AC bonus) | ×0.25 |

### 6c. Additive Bonuses (gp)

**Weapon bonuses:**
- +1: +10,000 gp
- +2: +50,000 gp
- +3: +200,000 gp

**AC bonuses:**
- +1: +15,000 gp
- +2: +40,000 gp
- +3: +150,000 gp

**Spell attack / save DC bonus:**
- +1: +8,000 gp
- +2: +25,000 gp
- +3: +80,000 gp

**Other combat bonuses:**
- Saving throw bonus +1: +3,000 gp per applicable saving throw
- Ability check bonus +1: +1,000 gp
- Proficiency bonus mod: +5,000 gp per +1

**Resistances & immunities:**
- Damage resistance: +2,000 gp per type
- Damage immunity: +5,000 gp per type
- Condition immunity: priced individually (see below)
  - Frightened: +2,000
  - Charmed: +3,000
  - Poisoned: +2,500
  - Exhaustion: +5,000
  - Petrified: +3,000
  - Paralyzed: +4,000
  - Blinded: +4,000
  - Deafened: +1,000
  - Stunned: +4,000
  - Incapacitated: +6,000
  - Prone: +1,500
  - Restrained: +3,000

**Movement:**
- Full flight: +15,000 gp
- Limited flight: +5,000 gp
- Swim speed: +2,000 gp
- Climb speed: +2,000 gp
- Burrow speed: +3,000 gp
- Darkvision: +200 gp per 30 ft (cap: 120 ft / +800 gp)
- Truesight: +15,000 gp
- Blindsight: +5,000 gp
- Tremorsense: +3,000 gp

**Utility:**
- Stealth advantage: +2,000 gp
- Stealth disadvantage removed: +1,000 gp
- Strength requirement removed: +500 gp
- Critical hit immunity: +10,000 gp
- Teleportation: +20,000 gp
- Concentration-free: +3,000 gp
- Invisibility (at-will): +25,000 gp

**Spells:**
- Spell scroll by level: 0=25, 1=75, 2=150, 3=300, 4=1,500, 5=3,000, 6=8,500, 7=20,000, 8=45,000, 9=100,000
- Spell (charges, cast per day): 0.75× scroll price per charge (charges on recharge)
- Spell (daily use): 1.0× scroll price per use
- Spell (unlimited/at-will): 3.0× scroll price equivalent
- Attached spells as raw list (unlimited): 3.0× highest-level spell scroll price

**Special:**
- Tome/Manual (permanent stat boost): +50,000 to +200,000 depending on stat and amount
- Ability flat bonus: +500 gp per +1 per ability
- Ability set score (vs 10): +1,000 gp per point above 10
- Healing (daily): +150 gp per HP
- Healing (consumable): +50 gp per HP
- Wish or reality-altering effect: +500,000 gp

### 6d. Formula

```
price = max(
    rarity_floor,
    (base_rarity_price + sum(additive_bonuses)) 
    × attunement_mod 
    × consumable_mod 
    × material_mod 
    × curse_mod 
    × sentient_mod
)
```

For official-priced mundane items: `price = official_price_gp` (no formula applied)

---

## 7. Amalgamation Methodology

1. Trim 2% most expensive and 2% cheapest items from each guide independently
2. Fuzzy-match items across guides (85% name similarity threshold)
3. Compute weighted mean per item:
   - Two guides within 25% of each other → outlier guide weight 20%, aligned guides 40% each
   - All three aligned (within 25% of median) → 33/33/33
   - All three diverge → 40% DSA, 30% MSRP, 30% DMPG
4. Solo-source items: use price as-is, flagged as single-source
5. MSRP averaging: take mean of "low magic" and "high magic" columns before amalgamation

---

## 8. Quality Targets

| Metric | Target | Prior Project |
|--------|--------|--------------|
| Overall R² | ≥ 0.80 | 0.66 |
| Common outlier rate | < 15% | 30.3% |
| Uncommon outlier rate | < 15% | 43.9% |
| Rare outlier rate | < 10% | 8.1% |
| Very Rare outlier rate | < 15% | 21.3% |
| Legendary outlier rate | < 15% | 20.7% |
| Items with price = 0 | 0 | several |
| Items priced > 3× rarity median | < 10% | 9.2% |

---

## 9. Quality Checkpoints

**Checkpoint #1** — After Phase 5 (rule-based formula baseline):
- @oracle reviews formula design, base prices, and modifier logic
- Check for internal contradictions (e.g., does +3 weapon cost more than a Legendary item?)
- Verify formula produces expected prices for 10 known reference items

**Checkpoint #2** — After Phase 6 (ML refinement):
- @oracle reviews ML coefficients and accuracy metrics
- Ensure no coefficient has counterintuitive sign (e.g., flight should be positive)
- Confirm R² ≥ 0.80 and outlier targets met

**Checkpoint #3** — After Phase 8 (final output):
- @oracle performs full spreadsheet quality review
- Spot-check 50 items across all rarities
- Verify all hyperlinks work
- Check for formatting issues, missing data, duplicate entries

---

## 10. Task Management

Tasks tracked in:
1. **Beads issue tracker** (primary)
2. **PROJECT_CONTEXT.md** (living context document — updated after each phase)

---

## 11. Key Decisions

- Mundane items with official prices: use price directly, no algorithm
- Mundane items with only guidance pricing (DMG/XGE): use algorithm
- MSRP: average low/high magic columns before amalgamation
- Attunement: open = 0.85×; class-restricted = 0.75×
- Consumable type scroll: 0.20× (reflects limited utility vs permanent item)
- Ammunition: 0.05× per single piece (vs set)
- R² target: ≥ 0.80 (significant improvement over prior 0.66)
- Output: Excel (primary) + CSV (backup)
- Fuzzy match threshold: 85% for external guide matching
- "Unknown (magic)" rarity: estimate from criteria scoring

---

## 12. Reference Resources

- Dump Stat Adventures writeup: https://dumpstatadventures.com/the-gm-is-always-right/pricing-magic-items-part-8
- 5e.tools items: https://5e.tools/items.html
- Prior project code reference: `/Users/ryan/OpenCode/TTRPG/pricing_guide_2/`
- Reddit community pricing resources: https://www.reddit.com/r/dndnext/comments/1dmqcaj/magic_item_price_charts/
