# Attached Spells Pricing Design

## Overview

The pricing engine currently ignores the `attached_spells` field, causing some artifacts and magic items to be underpriced. This spec defines how to calculate the value of spells attached to magic items.

## Problem Statement

- **Adze of Annam**: Has fabricate + move earth daily, priced at 50,000 gp (artifact floor)
- **Blade of Avernus**: Has word of recall, priced at 50,000 gp (artifact floor)
- **Wand of Fireballs**: Has 1 charge of fireball, priced at 7,135 gp (may be underpriced)

These items have powerful spell abilities that should increase their price beyond the base rarity value.

## Data Analysis

### attached_spells Structure Types

The `attached_spells` field has multiple structure types:

| Structure | Count | Example |
|-----------|-------|---------|
| `{'charges': {...}}` | 198 | `{'charges': {'1': ['fireball|xphb']}}` |
| `{'daily': {...}}` | 129 | `{'daily': {'1': ['fabricate', 'move earth']}}` |
| `['spell1', 'spell2']` | 77 | `['invisibility|xphb', 'fly|xphb']` |
| `{'will': {...}}` | 16 | `{'will': ['thunderwave#4']}` |
| `{'will', 'daily'}` | 9 | `{'will': ['scrying'], 'daily': {'1e': ['suggestion']}}` |
| `{'other': {...}}` | 8 | `{'other': ['teleport|xphb']}` |
| `{'limited': {...}}` | 7 | `{'limited': {'1': ['wish']}}` |
| Other combinations | 28 | Various |

### Spell Coverage

- **Total unique spells in items**: 270
- **Matched in spells-sublist.json**: 256 (94.8%)
- **Manual additions needed**: 14 (common SRD spells)

## Design

### 1. Spell Level Lookup

**Source**: `spells-sublist.json` (614 spells) + manual additions

**Implementation**:
```python
# Load at module level
SPELL_LEVELS = {}

# From spells-sublist.json
for spell in spells_data:
    name = spell['name'].lower()
    level = spell['level']
    SPELL_LEVELS[name] = level

# Manual additions for common SRD spells
MANUAL_SPELL_LEVELS = {
    'protection from evil and good': 1,
    'false life': 1,
    'haste': 3,
    'control water': 4,
    'protection from energy': 3,
    'freedom of movement': 4,
    'barkskin': 2,
    'warding bond': 2,
    'death ward': 4,
    'fire shield': 4,
    'stoneskin': 4,
}
SPELL_LEVELS.update(MANUAL_SPELL_LEVELS)
```

**Spell name normalization**:
- Convert to lowercase
- Remove source suffixes (e.g., `|xphb`, `#4`)
- Example: `"fireball|xphb"` → `"fireball"`

### 2. Spell Value Formula

**Base value per spell level**: `level² × 500` gp

| Level | Value | Example Spells |
|-------|-------|----------------|
| 0 (cantrip) | 0 gp | Acid Splash, Mage Hand |
| 1 | 500 gp | Magic Missile, Shield, Cure Wounds |
| 2 | 2,000 gp | Invisibility, Misty Step, Hold Person |
| 3 | 4,500 gp | Fireball, Haste, Fly |
| 4 | 8,000 gp | Dimension Door, Polymorph, Banishment |
| 5 | 12,500 gp | Teleport, Wall of Force, Scrying |
| 6 | 18,000 gp | Disintegrate, True Seeing, Heal |
| 7 | 24,500 gp | Forcecage, Teleport (Greater), Finger of Death |
| 8 | 32,000 gp | Dominate Monster, Glibness, Demiplane |
| 9 | 40,500 gp | Wish, Time Stop, Gate |

**Rationale**: The quadratic scaling reflects that higher-level spells are exponentially more powerful and valuable. A 9th-level spell (Wish) is worth 81× a 1st-level spell, which aligns with their relative impact.

### 3. Usage Type Multipliers

| Usage Type | Multiplier | Rationale |
|------------|------------|-----------|
| `will` (at-will) | 3.0x | Unlimited use, highest value |
| `daily` | 1.5x | Reliable daily recharge |
| `charges` | 1.0x | Consumable, base value |
| `rest` | 0.75x | Short/long rest recharge |
| `limited` | 0.5x | Restricted/situational use |
| `other` | 0.5x | Unclear usage pattern |
| `list` (unlimited) | 2.0x | No explicit limit stated |

**Rationale**:
- At-will spells can be cast every round, providing immense utility
- Daily spells are reliable but limited to once per day
- Charge-based spells are consumable and should be valued at base
- Rest-recharge is between daily and charges in value
- Limited/other are situational and hard to value

### 4. Frequency Modifier

For `daily` and `charges` types, multiply by the frequency count:

- `{'daily': {'3': ['fireball']}}` → 3 × (spell_value × daily_multiplier)
- `{'charges': {'1': ['wish']}}` → 1 × (spell_value × charges_multiplier)

**Special cases**:
- `{'daily': {'1e': ['spell']}}` - "1e" means "1, expended" - same as regular daily
- `{'daily': {'3': ['spell1', 'spell2']}}` - 3 uses shared between spells. Each spell can be cast up to 3 times per day, so value each spell at: spell_value × 1.5 (daily) × 3 (frequency)

### 5. Calculation Function

```python
def calculate_spell_value(attached_spells: Any) -> float:
    """
    Calculate the additive value of attached spells.
    
    Args:
        attached_spells: The attached_spells field from criteria
        
    Returns:
        Total spell value in gold pieces
    """
    if not attached_spells:
        return 0.0
    
    total_value = 0.0
    
    # Handle list format (unlimited use)
    if isinstance(attached_spells, list):
        for spell_name in attached_spells:
            spell_level = get_spell_level(spell_name)
            spell_value = spell_level ** 2 * 500
            total_value += spell_value * 2.0  # Unlimited multiplier
        return total_value
    
    # Handle dict format
    if isinstance(attached_spells, dict):
        for usage_type, usage_data in attached_spells.items():
            multiplier = USAGE_MULTIPLIERS.get(usage_type, 0.5)
            
            if isinstance(usage_data, dict):
                # {'1': ['spell1'], '3': ['spell2']}
                for frequency, spells in usage_data.items():
                    freq = int(frequency.replace('e', ''))  # Handle '1e' -> 1
                    for spell_name in spells:
                        spell_level = get_spell_level(spell_name)
                        spell_value = spell_level ** 2 * 500
                        total_value += spell_value * multiplier * freq
            elif isinstance(usage_data, list):
                # {'will': ['spell1', 'spell2']}
                for spell_name in usage_data:
                    spell_level = get_spell_level(spell_name)
                    spell_value = spell_level ** 2 * 500
                    total_value += spell_value * multiplier
    
    return total_value

def get_spell_level(spell_name: str) -> int:
    """Get spell level from lookup table."""
    # Normalize: lowercase, remove source suffixes
    normalized = spell_name.lower().split('|')[0].split('#')[0]
    return SPELL_LEVELS.get(normalized, 1)  # Default to 1st level if unknown
```

### 6. Integration Point

Add in `calculate_price()` after charges handling (around line 610):

```python
# Attached spells: calculate value based on spell levels and usage
attached_spells = criteria.get("attached_spells")
if attached_spells:
    spell_value = calculate_spell_value(attached_spells)
    additive += spell_value
```

## Example Calculations

### Adze of Annam (Artifact)
- `attached_spells`: `{'daily': {'1': ['fabricate', 'move earth']}}`
- fabricate (4th): 8,000 gp × 1.5 (daily) = 12,000 gp
- move earth (6th): 18,000 gp × 1.5 (daily) = 27,000 gp
- **Spell value**: 39,000 gp
- Current price: 50,000 gp (floor)
- New price: 50,000 + 39,000 = **89,000 gp** (before other modifiers)

### Wand of Fireballs (Rare)
- `attached_spells`: `{'charges': {'1': ['fireball|xphb']}}`
- fireball (3rd): 4,500 gp × 1.0 (charges) = 4,500 gp
- **Spell value**: 4,500 gp
- Current price: 7,135 gp
- New price: 7,135 + 4,500 = **11,635 gp** (before ML blending)

### Calimemnon Crystal (Artifact)
- `attached_spells`: `['create or destroy water|xphb', 'enlarge/reduce|xphb', 'invisibility|xphb', 'major image|xphb']`
- create or destroy water (1st): 500 gp × 2.0 (unlimited) = 1,000 gp
- enlarge/reduce (2nd): 2,000 gp × 2.0 (unlimited) = 4,000 gp
- invisibility (2nd): 2,000 gp × 2.0 (unlimited) = 4,000 gp
- major image (3rd): 4,500 gp × 2.0 (unlimited) = 9,000 gp
- **Spell value**: 18,000 gp
- Current price: 167,400 gp
- New price: 167,400 + 18,000 = **185,400 gp** (before ML blending)

### Blast Scepter (Very Rare)
- `attached_spells`: `{'will': ['thunderwave#4']}`
- thunderwave (1st): 500 gp × 3.0 (at-will) = 1,500 gp
- **Spell value**: 1,500 gp
- Current price: 6,405 gp
- New price: 6,405 + 1,500 = **7,905 gp** (before ML blending)

## Edge Cases

### Unknown Spells
If a spell is not in the lookup table, default to 1st level (500 gp base value). This is conservative and avoids overpricing items with obscure spells.

### Ability Score References
Some items have `attached_spells` like `['int', 'wis', 'cha']`. These are not spells but ability score references. The lookup will return level 0 (cantrip), resulting in 0 gp value, which is correct.

### Multiple Usage Types
Items like Crystal Ball of Telepathy have multiple usage types:
- `{'will': ['scrying|xphb'], 'daily': {'1e': ['suggestion|xphb']}}`
- Calculate each separately and sum:
  - scrying (5th): 12,500 gp × 3.0 (at-will) = 37,500 gp
  - suggestion (2nd): 2,000 gp × 1.5 (daily) = 3,000 gp
  - **Total**: 40,500 gp

## Testing

### Unit Tests
1. Test spell level lookup with various spell names
2. Test spell value calculation for each usage type
3. Test frequency multiplier
4. Test edge cases (unknown spells, ability scores)
5. Test integration with existing pricing formula

### Validation
1. Run pricing pipeline with new formula
2. Compare artifact prices before/after
3. Check for anomalies (items that become overpriced)
4. Verify ML blending still works correctly

## Implementation Checklist

- [ ] Load spells-sublist.json at module level
- [ ] Add manual spell level lookup
- [ ] Implement `get_spell_level()` function
- [ ] Implement `calculate_spell_value()` function
- [ ] Add USAGE_MULTIPLIERS constant
- [ ] Integrate into `calculate_price()` function
- [ ] Add unit tests
- [ ] Run full pipeline and validate results
- [ ] Update anomaly detection to account for spell values

## Files to Modify

1. `src/pricing_engine.py` - Add spell value calculation
2. `tests/test_pricing_engine.py` - Add unit tests
3. `scripts/05_rule_formula.py` - No changes needed (uses calculate_price)
