# Implementation Plan: Attached Spells Pricing

## Overview

Implement spell value calculation for the `attached_spells` field in magic items, following the approved design spec.

## Prerequisites

- Design spec approved: `docs/superpowers/specs/2026-04-10-attached-spells-pricing-design.md`
- Data source available: `spells-sublist.json` (614 spells)
- Issue tracked: `pricing_guide_v2-3gv`

## Implementation Steps

### Phase 1: Spell Level Lookup (30 min)

**Task 1.1: Create spell level data module**
- Create `src/spell_data.py` module
- Load `spells-sublist.json` at module level
- Add `MANUAL_SPELL_LEVELS` dict for 14 SRD spells not in JSON
- Export `SPELL_LEVELS` dict (normalized name → level)

**Task 1.2: Implement spell name normalization**
- Function: `normalize_spell_name(name: str) -> str`
- Lowercase conversion
- Remove source suffixes (`|xphb`, `|phb`, etc.)
- Remove count suffixes (`#4`, etc.)
- Example: `"fireball|xphb"` → `"fireball"`

**Task 1.3: Implement spell level lookup**
- Function: `get_spell_level(name: str) -> int`
- Normalize name
- Return level from `SPELL_LEVELS`
- Default to 1 if unknown (conservative)

### Phase 2: Spell Value Calculation (45 min)

**Task 2.1: Define constants**
- `USAGE_MULTIPLIERS` dict in `pricing_engine.py`:
  - `will`: 3.0 (at-will, highest value)
  - `daily`: 1.5 (reliable daily recharge)
  - `charges`: 1.0 (consumable, base value)
  - `rest`: 0.75 (short/long rest recharge)
  - `limited`: 0.5 (restricted/situational)
  - `other`: 0.5 (unclear usage)
  - `list`: 2.0 (unlimited use)

**Task 2.2: Implement `calculate_spell_value()`**
- Input: `attached_spells` field (Any)
- Output: Total spell value in gp (float)
- Handle three formats:
  1. **List format**: `['spell1', 'spell2']` → unlimited use (2.0x)
  2. **Dict with nested dict**: `{'daily': {'1': ['spell']}}` → frequency × multiplier
  3. **Dict with list**: `{'will': ['spell']}` → just multiplier

**Task 2.3: Handle edge cases**
- Empty/None attached_spells → return 0.0
- Unknown spells → default to level 1
- Ability score references (`['int', 'wis', 'cha']`) → level 0, value 0
- Frequency with 'e' suffix (`'1e'`) → treat as regular frequency

### Phase 3: Integration (20 min)

**Task 3.1: Integrate into `calculate_price()`**
- Location: After charges handling (~line 610 in `pricing_engine.py`)
- Add spell value to `additive` component
- Log spell value for debugging

**Task 3.2: Update imports**
- Import `get_spell_level` from `spell_data` module
- Or inline the lookup if preferred (simpler)

### Phase 4: Testing (40 min)

**Task 4.1: Unit tests for spell level lookup**
- Test normalization with various spell names
- Test lookup for known spells
- Test default for unknown spells
- Test ability score edge case

**Task 4.2: Unit tests for spell value calculation**
- Test list format (unlimited use)
- Test dict format with daily/charges/will
- Test frequency multiplier
- Test multiple usage types
- Test empty/None input

**Task 4.3: Integration tests**
- Test Adze of Annam calculation
- Test Wand of Fireballs calculation
- Test Blast Scepter calculation
- Verify ML blending still works

### Phase 5: Validation (30 min)

**Task 5.1: Run full pricing pipeline**
- Execute `scripts/05_rule_formula.py`
- Compare artifact prices before/after
- Check for anomalies

**Task 5.2: Validate specific items**
- Adze of Annam: Should increase from 50,000 gp to ~89,000 gp
- Wand of Fireballs: Should increase from 7,135 gp to ~11,635 gp
- Calimemnon Crystal: Should increase from 167,400 gp to ~185,400 gp

**Task 5.3: Check for overpricing**
- Review items that gained >50% price increase
- Verify spell values are reasonable
- Adjust multipliers if needed

## File Changes

| File | Changes |
|------|---------|
| `src/spell_data.py` | NEW - Spell level lookup module |
| `src/pricing_engine.py` | Add `USAGE_MULTIPLIERS`, `calculate_spell_value()`, integration |
| `tests/test_spell_data.py` | NEW - Unit tests for spell lookup |
| `tests/test_pricing_engine.py` | Add tests for spell value calculation |

## Dependencies

- No external dependencies
- Uses existing `spells-sublist.json` data file
- No changes to ML blending or other pricing components

## Rollback Plan

If issues arise:
1. Remove spell value from `additive` calculation
2. Spell value calculation is isolated and can be disabled without affecting other pricing
3. No database or external service dependencies

## Success Criteria

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Adze of Annam price increases to ~89,000 gp
- [ ] No items become unreasonably overpriced
- [ ] ML blending still functions correctly
- [ ] Code follows existing style and patterns

## Estimated Time

- Phase 1: 30 min
- Phase 2: 45 min
- Phase 3: 20 min
- Phase 4: 40 min
- Phase 5: 30 min
- **Total: ~2.5 hours**

## Notes

- Spell value is **additive** to base price, not multiplicative
- Conservative defaults (unknown spells = level 1) prevent overpricing
- Usage multipliers are based on power analysis, not arbitrary
