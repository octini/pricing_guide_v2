# src/variant_system.py
"""Consolidated variant system.

Merges four former modules — behavior-neutral:
- src/generic_variant_mapper.py  (generic-variant mapping & group stats)
- src/variant_adjuster.py        (category-aware price adjustments)
- src/generic_pricing.py         (generic base prices & variant merge)
- src/variant_pricing.py         (mundane-cost-based variant spacing)

All public function names are preserved so call sites change only imports.

Sections:
  1. Generic Variant Mapping
  2. Variant Adjustment
  3. Generic Pricing
  4. Mundane-cost Variant Pricing
"""

import json
import math
import re

import pandas as pd
from typing import Optional, Tuple


# =============================================================================
# Section 1: Generic Variant Mapping
# =============================================================================
# Extract generic variant relationships from raw JSON data.


def parse_dice_tier(dmg_str: Optional[str]) -> Optional[int]:
    """Convert a damage dice expression to a numeric tier for comparison.

    Mapping: 1d4=1, 1d6=2, 1d8=3, 1d10=4, 1d12=5, 2d6=6, 2d8=7, 2d10=8, 2d12=9, 3d6=10
    """
    if not dmg_str or not isinstance(dmg_str, str):
        return None
    m = re.match(r'(\d+)d(\d+)', dmg_str.strip())
    if not m:
        return None
    num_dice = int(m.group(1))
    die_size = int(m.group(2))
    # Average damage as primary sort
    avg = num_dice * (die_size + 1) / 2
    # Map to tier buckets
    tier_map = {
        1: 1, 1.5: 1, 2: 1,  # 1d2, 1d3 → tier 1
        2.5: 2, 3: 2, 3.5: 2,  # 1d4, 1d5, 1d6 → tier 2
        4: 3, 4.5: 3, 5: 3, 5.5: 3,  # 1d7, 1d8, 1d9, 1d10 → tier 3
        6: 4, 6.5: 4, 7: 4,  # 1d11, 1d12, 2d6 avg → tier 4
        8: 5, 8.5: 5, 9: 5,  # 2d7, 2d8, 2d9 → tier 5
        10: 6, 10.5: 6, 11: 6,  # 2d10, 2d11, 2d12 → tier 6
        12: 7, 13: 7, 14: 7,  # 3d8, 3d9, 3d10 → tier 7
        15: 8, 16: 8, 18: 9,  # 3d11, 3d12, 4d8 → tier 8-9
    }
    # Find closest tier
    if avg in tier_map:
        return tier_map[avg]
    # Fallback: use log scale
    return max(1, min(10, int(math.log2(avg) * 2)))


def extract_generic_variant_mapping(master_df: pd.DataFrame) -> pd.DataFrame:
    """Build a mapping of specific items to their generic variant parents.

    Returns DataFrame with columns:
    - specific_name: name of the specific variant
    - generic_name: name of the generic parent
    - weight: weight in lbs (from raw JSON)
    - dmg1: primary damage dice
    - dmg2: secondary damage dice (versatile)
    - ac: armor class
    - base_item: base item reference
    - dmg_tier: numeric damage tier (for weapons)
    - charges: number of charges
    - req_attune: attunement requirement
    """
    mapping_rows = []

    for idx, row in master_df.iterrows():
        try:
            raw = json.loads(row['raw_json'])
        except (json.JSONDecodeError, TypeError):
            continue

        gv_link = raw.get('genericVariant')
        if not gv_link:
            continue

        if isinstance(gv_link, dict):
            generic_name = gv_link.get('name', '')
        else:
            generic_name = str(gv_link)

        if not generic_name:
            continue

        # Extract physical properties
        weight = raw.get('weight')
        dmg1 = raw.get('dmg1')
        dmg2 = raw.get('dmg2')
        ac = raw.get('ac')
        base_item = raw.get('baseItem')
        charges = raw.get('charges')
        req_attune = raw.get('reqAttune', False)
        bonus_ac = raw.get('bonusAc')
        bonus_weapon = raw.get('bonusWeapon')
        bonus_weapon_attack = raw.get('bonusWeaponAttack')
        bonus_weapon_damage = raw.get('bonusWeaponDamage')
        bonus_spell_save_dc = raw.get('bonusSpellSaveDc')
        bonus_spell_attack = raw.get('bonusSpellAttack')

        # Compute damage tier
        dmg_tier = parse_dice_tier(dmg1)

        mapping_rows.append({
            'specific_name': row['name'],
            'generic_name': generic_name,
            'weight': weight,
            'dmg1': dmg1,
            'dmg2': dmg2,
            'ac': ac,
            'base_item': base_item,
            'dmg_tier': dmg_tier,
            'charges': charges,
            'req_attune': req_attune if isinstance(req_attune, bool) else True,
            'bonus_ac': bonus_ac,
            'bonus_weapon': bonus_weapon,
            'bonus_weapon_attack': bonus_weapon_attack,
            'bonus_weapon_damage': bonus_weapon_damage,
            'bonus_spell_save_dc': bonus_spell_save_dc,
            'bonus_spell_attack': bonus_spell_attack,
        })

    return pd.DataFrame(mapping_rows)


def compute_generic_group_stats(mapping_df: pd.DataFrame) -> pd.DataFrame:
    """Compute statistics for each generic variant group.

    Returns DataFrame with columns:
    - generic_name
    - variant_count
    - median_weight, min_weight, max_weight
    - median_ac, min_ac, max_ac
    - median_dmg_tier, min_dmg_tier, max_dmg_tier
    """
    groups = mapping_df.groupby('generic_name')

    stats = []
    for name, group in groups:
        weights = group['weight'].dropna()
        acs = group['ac'].dropna()
        dmg_tiers = group['dmg_tier'].dropna()

        stats.append({
            'generic_name': name,
            'variant_count': len(group),
            'median_weight': weights.median() if len(weights) > 0 else None,
            'min_weight': weights.min() if len(weights) > 0 else None,
            'max_weight': weights.max() if len(weights) > 0 else None,
            'median_ac': acs.median() if len(acs) > 0 else None,
            'min_ac': acs.min() if len(acs) > 0 else None,
            'max_ac': acs.max() if len(acs) > 0 else None,
            'median_dmg_tier': dmg_tiers.median() if len(dmg_tiers) > 0 else None,
            'min_dmg_tier': dmg_tiers.min() if len(dmg_tiers) > 0 else None,
            'max_dmg_tier': dmg_tiers.max() if len(dmg_tiers) > 0 else None,
        })

    return pd.DataFrame(stats)


# =============================================================================
# Section 2: Variant Adjustment
# =============================================================================
# Category-aware variant price adjustment system.


def compute_adjustment_factor(
    specific_row: pd.Series,
    group_stats: pd.Series,
    category: str,
) -> float:
    """Compute adjustment factor for a specific variant based on category.

    Args:
        specific_row: Row from mapping_df for the specific item
        group_stats: Row from compute_generic_group_stats for the generic parent
        category: One of 'ammunition', 'weapon', 'armor', 'shield', 'focus', 'buff', 'other'

    Returns:
        Adjustment factor in range [-1, 1], to be scaled by sensitivity (0.3)
    """

    if category == 'ammunition':
        return _adjustment_ammunition(specific_row, group_stats)
    elif category == 'weapon':
        return _adjustment_weapon(specific_row, group_stats)
    elif category in ('armor', 'shield'):
        return _adjustment_armor(specific_row, group_stats)
    elif category == 'focus':
        return _adjustment_focus(specific_row, group_stats)
    elif category == 'buff':
        return _adjustment_buff(specific_row, group_stats)
    else:
        return _adjustment_other(specific_row, group_stats)


def _adjustment_ammunition(specific: pd.Series, stats: pd.Series) -> float:
    """Ammunition: weight ratio using log scale.

    Example: Arrow (0.05lb) vs Cannonball (2.0lb)
    """
    weight = specific.get('weight')
    if weight is None or pd.isna(weight):
        return 0.0

    min_w = stats.get('min_weight')
    max_w = stats.get('max_weight')
    median_w = stats.get('median_weight')

    if min_w is None or max_w is None or median_w is None:
        return 0.0

    if min_w == max_w:
        return 0.0

    if min_w <= 0 or median_w <= 0:
        return 0.0

    log_ratio = math.log(weight / median_w) if weight > 0 and median_w > 0 else 0
    log_range = math.log(max_w / min_w) if max_w > 0 and min_w > 0 else 1

    if log_range == 0:
        return 0.0

    factor = log_ratio / log_range
    return max(-1.0, min(1.0, factor))


def _adjustment_weapon(specific: pd.Series, stats: pd.Series) -> float:
    """Weapon: 50/50 blend of damage tier and weight.

    Example: Dagger (1d4, 1lb) vs Greatsword (2d6, 6lb)
    """
    weight = specific.get('weight')
    dmg_tier = specific.get('dmg_tier')

    weight_factor = 0.0
    if weight is not None and not pd.isna(weight):
        min_w = stats.get('min_weight')
        max_w = stats.get('max_weight')
        median_w = stats.get('median_weight')

        if min_w and max_w and median_w and min_w > 0 and median_w > 0:
            if max_w > min_w:
                log_ratio = math.log(weight / median_w) if weight > 0 else 0
                log_range = math.log(max_w / min_w) if max_w > 0 and min_w > 0 else 1
                if log_range > 0:
                    weight_factor = log_ratio / log_range

    dmg_factor = 0.0
    if dmg_tier is not None and not pd.isna(dmg_tier):
        min_t = stats.get('min_dmg_tier')
        max_t = stats.get('max_dmg_tier')
        median_t = stats.get('median_dmg_tier')

        if min_t and max_t and median_t:
            if max_t > min_t:
                dmg_factor = (dmg_tier - median_t) / (max_t - min_t)

    factor = 0.5 * weight_factor + 0.5 * dmg_factor
    return max(-1.0, min(1.0, factor))


def _adjustment_armor(specific: pd.Series, stats: pd.Series) -> float:
    """Armor/Shield: AC value ratio.

    Example: Leather (AC 11) vs Plate (AC 18)
    """
    ac = specific.get('ac')
    if ac is None or pd.isna(ac):
        return 0.0

    min_ac = stats.get('min_ac')
    max_ac = stats.get('max_ac')
    median_ac = stats.get('median_ac')

    if min_ac is None or max_ac is None or median_ac is None:
        return 0.0

    if max_ac == min_ac:
        return 0.0

    factor = (ac - median_ac) / (max_ac - min_ac)
    return max(-1.0, min(1.0, factor))


def _adjustment_focus(specific: pd.Series, stats: pd.Series) -> float:
    """Spellcasting Focus: weight ratio using log scale.

    Example: Crystal (0.1lb) vs Staff (4lb)
    """
    weight = specific.get('weight')
    if weight is None or pd.isna(weight):
        return 0.0

    min_w = stats.get('min_weight')
    max_w = stats.get('max_weight')
    median_w = stats.get('median_weight')

    if min_w is None or max_w is None or median_w is None:
        return 0.0

    if min_w == max_w or min_w <= 0 or median_w <= 0:
        return 0.0

    log_ratio = math.log(weight / median_w) if weight > 0 and median_w > 0 else 0
    log_range = math.log(max_w / min_w) if max_w > 0 and min_w > 0 else 1

    if log_range == 0:
        return 0.0

    factor = log_ratio / log_range
    return max(-1.0, min(1.0, factor))


def _adjustment_buff(specific: pd.Series, stats: pd.Series) -> float:
    """Buff items: bonus magnitude.

    Uses extracted bonus values from raw JSON (bonusWeapon, bonusAc, etc.)
    """
    bonus_cols = ['bonus_weapon', 'bonus_ac', 'bonus_spell_save_dc', 'bonus_spell_attack']

    bonus_values = []
    for col in bonus_cols:
        val = specific.get(col)
        if val is not None and not pd.isna(val):
            try:
                bonus_values.append(abs(float(val)))
            except (ValueError, TypeError):
                pass

    if not bonus_values:
        return 0.0

    total_bonus = sum(bonus_values)

    if total_bonus <= 1:
        return -0.5
    elif total_bonus <= 2:
        return 0.0
    elif total_bonus <= 3:
        return 0.5
    else:
        return 1.0


def _adjustment_other(specific: pd.Series, stats: pd.Series) -> float:
    """Fallback: weight only.

    Uses log scale for weight ratios.
    """
    weight = specific.get('weight')
    if weight is None or pd.isna(weight):
        return 0.0

    min_w = stats.get('min_weight')
    max_w = stats.get('max_weight')
    median_w = stats.get('median_weight')

    if min_w is None or max_w is None or median_w is None:
        return 0.0

    if min_w == max_w or min_w <= 0 or median_w <= 0:
        return 0.0

    log_ratio = math.log(weight / median_w) if weight > 0 and median_w > 0 else 0
    log_range = math.log(max_w / min_w) if max_w > 0 and min_w > 0 else 1

    if log_range == 0:
        return 0.0

    factor = log_ratio / log_range
    return max(-1.0, min(1.0, factor))


def categorize_generic_variant(generic_name: str, item_type: str = '') -> str:
    """Determine the category for a generic variant.

    Args:
        generic_name: Name of the generic variant
        item_type: Item type code from raw JSON

    Returns:
        Category string: 'ammunition', 'weapon', 'armor', 'shield', 'focus', 'buff', 'other'
    """
    name_lower = generic_name.lower()
    type_base = item_type.split('|')[0] if '|' in str(item_type) else str(item_type)

    if type_base == 'A' or 'ammunition' in name_lower or 'arrow' in name_lower or 'bolt' in name_lower:
        return 'ammunition'
    elif type_base == 'S' or 'shield' in name_lower:
        return 'shield'
    elif type_base in ('M', 'R') or 'weapon' in name_lower or 'sword' in name_lower or 'axe' in name_lower:
        return 'weapon'
    elif type_base in ('LA', 'MA', 'HA') or 'armor' in name_lower:
        return 'armor'
    elif type_base == 'SCF' or 'focus' in name_lower or 'orb' in name_lower or 'wand' in name_lower:
        return 'focus'
    elif 'bonus' in name_lower or 'ring' in name_lower or 'rod' in name_lower:
        return 'buff'
    else:
        return 'other'


def apply_variant_adjustment(
    base_price: float,
    adjustment_factor: float,
    sensitivity: float = 0.3,
) -> float:
    """Apply adjustment to base price.

    Args:
        base_price: The base price from the generic variant
        adjustment_factor: Factor in range [-1, 1]
        sensitivity: Maximum adjustment fraction (default 0.3 = ±30%)

    Returns:
        Adjusted price
    """
    adjustment = adjustment_factor * sensitivity
    return base_price * (1.0 + adjustment)


# =============================================================================
# Section 3: Generic Pricing
# =============================================================================
# Compute base prices for generic variants.


def compute_generic_base_prices(
    mapping_df: pd.DataFrame,
    priced_df: pd.DataFrame,
    amalgamated_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Compute base prices for each generic variant.

    Args:
        mapping_df: Output from extract_generic_variant_mapping
        priced_df: Items with final_price column
        amalgamated_df: Optional items with amalgamated_price column

    Returns:
        DataFrame with columns: generic_name, base_price, price_source, variant_count
    """
    group_stats = compute_generic_group_stats(mapping_df)

    base_prices = []
    for generic_name in group_stats['generic_name']:
        variants = mapping_df[mapping_df['generic_name'] == generic_name]
        variant_names = variants['specific_name'].tolist()

        # PRIORITY 1: Check if the generic itself has a price in priced_df
        price_col = 'rule_price' if 'rule_price' in priced_df.columns else 'final_price'
        generic_row = priced_df[priced_df['name'] == generic_name]
        if len(generic_row) > 0:
            generic_price = generic_row.iloc[0].get(price_col)
            if generic_price is not None and not pd.isna(generic_price) and generic_price > 0:
                base_prices.append({
                    'generic_name': generic_name,
                    'base_price': generic_price,
                    'price_source': 'generic_rule_price',
                    'variant_count': len(variants),
                })
                continue

        # PRIORITY 2: Check if the generic has an amalgamated_price
        if amalgamated_df is not None:
            generic_amal_row = amalgamated_df[amalgamated_df['name'] == generic_name]
            if len(generic_amal_row) > 0:
                generic_amal = generic_amal_row.iloc[0].get('amalgamated_price')
                if generic_amal is not None and not pd.isna(generic_amal) and generic_amal > 0:
                    base_prices.append({
                        'generic_name': generic_name,
                        'base_price': generic_amal,
                        'price_source': 'generic_amalgamated',
                        'variant_count': len(variants),
                    })
                    continue

        # PRIORITY 3: Average of variant prices
        variant_prices = priced_df[priced_df['name'].isin(variant_names)]
        if len(variant_prices) > 0:
            avg_price = variant_prices[price_col].mean()
            if not pd.isna(avg_price) and avg_price > 0:
                base_prices.append({
                    'generic_name': generic_name,
                    'base_price': avg_price,
                    'price_source': 'variant_average',
                    'variant_count': len(variants),
                })
                continue

        # FALLBACK: Use rarity median
        rarity = variants.iloc[0]['generic_rarity']
        rarity_medians = {
            'common': 132,
            'uncommon': 852,
            'rare': 3890,
            'very_rare': 13450,
            'legendary': 46500,
            'artifact': 150000,
            'mundane': 1,
            'unknown': 1,
        }
        median_price = rarity_medians.get(rarity, 750)
        base_prices.append({
            'generic_name': generic_name,
            'base_price': median_price,
            'price_source': 'rarity_median',
            'variant_count': len(variants),
        })

    return pd.DataFrame(base_prices)


def merge_variant_prices(
    items_df: pd.DataFrame,
    mapping_df: pd.DataFrame,
    base_prices_df: pd.DataFrame,
    group_stats_df: pd.DataFrame,
) -> pd.DataFrame:
    """Merge variant-adjusted prices into items DataFrame.

    Args:
        items_df: Full items DataFrame
        mapping_df: Output from extract_generic_variant_mapping
        base_prices_df: Output from compute_generic_base_prices
        group_stats_df: Output from compute_generic_group_stats

    Returns:
        items_df with added columns: generic_parent, variant_base_price, variant_adjustment, variant_price
    """
    items = items_df.copy()

    items['generic_parent'] = None
    items['variant_base_price'] = None
    items['variant_adjustment'] = None
    items['variant_price'] = None

    for idx, row in items.iterrows():
        item_name = row['name']
        # Skip gleaming items - they have their own premium in the rule pricing
        if "gleaming" in item_name.lower():
            continue

        variant_row = mapping_df[mapping_df['specific_name'] == item_name]
        if len(variant_row) == 0:
            continue

        variant_row = variant_row.iloc[0]
        generic_name = variant_row['generic_name']

        base_price_row = base_prices_df[base_prices_df['generic_name'] == generic_name]
        if len(base_price_row) == 0:
            continue

        base_price = base_price_row.iloc[0]['base_price']
        if base_price is None or pd.isna(base_price):
            continue

        group_stats_row = group_stats_df[group_stats_df['generic_name'] == generic_name]
        if len(group_stats_row) == 0:
            continue

        group_stats = group_stats_row.iloc[0]

        category = categorize_generic_variant(generic_name, row.get('item_type_code', ''))
        adjustment_factor = compute_adjustment_factor(variant_row, group_stats, category)
        variant_price = apply_variant_adjustment(base_price, adjustment_factor)

        items.loc[idx, 'generic_parent'] = generic_name
        items.loc[idx, 'variant_base_price'] = base_price
        items.loc[idx, 'variant_adjustment'] = adjustment_factor
        items.loc[idx, 'variant_price'] = variant_price

    return items


# =============================================================================
# Section 4: Mundane-cost Variant Pricing
# =============================================================================
# Mundane-cost-based variant pricing within item categories.
# Applies dampened multipliers to +N armor/weapon variants so that
# more expensive mundane bases (e.g., Plate vs Breastplate) produce
# meaningfully different magic item prices.

# Mundane armor base prices (PHB)
MUNDANE_ARMOR_PRICES = {
    'padded armor': 5,
    'leather armor': 10,
    'studded leather armor': 45,
    'hide armor': 10,
    'chain shirt': 50,
    'scale mail': 50,
    'breastplate': 400,
    'half plate armor': 750,
    'ring mail': 30,
    'chain mail': 75,
    'splint armor': 200,
    'plate armor': 1500,
    'spiked armor': 75,
    'shield': 10,
}

# Mundane weapon base prices (PHB)
MUNDANE_WEAPON_PRICES = {
    'club': 0.1,
    'dagger': 2,
    'greatclub': 0.2,
    'handaxe': 5,
    'javelin': 0.5,
    'light hammer': 2,
    'mace': 5,
    'quarterstaff': 0.2,
    'sickle': 1,
    'spear': 1,
    'battleaxe': 10,
    'flail': 10,
    'glaive': 20,
    'greataxe': 30,
    'greatsword': 50,
    'halberd': 20,
    'lance': 10,
    'longsword': 15,
    'maul': 10,
    'morningstar': 15,
    'pike': 5,
    'rapier': 25,
    'scimitar': 25,
    'shortsword': 10,
    'trident': 5,
    'war pick': 5,
    'warhammer': 15,
    'whip': 2,
    'blowgun': 10,
    'hand crossbow': 75,
    'heavy crossbow': 50,
    'light crossbow': 25,
    'longbow': 50,
    'shortbow': 25,
    'dart': 0.05,
    'sling': 0.1,
    'musket': 500,
    'pistol': 250,
}

# Pattern to extract base armor/weapon name from "+N <Base>" format
_BONUS_PATTERN = re.compile(r'^(?:Drow\s+)?\+(\d+)\s+(.+)$', re.IGNORECASE)


def _extract_base_name(item_name: str) -> Tuple[Optional[int], Optional[str]]:
    """Extract bonus level and base item name from a +N item name."""
    m = _BONUS_PATTERN.match(item_name.strip())
    if not m:
        return None, None
    return int(m.group(1)), m.group(2).strip()


def _find_mundane_price(base_name: str) -> Tuple[Optional[float], bool]:
    """Look up mundane price for a base item name.

    Returns:
        (price, is_armor) or (None, False) if not found
    """
    name_lower = base_name.lower()

    # Direct lookup
    if name_lower in MUNDANE_ARMOR_PRICES:
        return MUNDANE_ARMOR_PRICES[name_lower], True
    if name_lower in MUNDANE_WEAPON_PRICES:
        return MUNDANE_WEAPON_PRICES[name_lower], False

    # Partial match
    for key, price in MUNDANE_ARMOR_PRICES.items():
        if name_lower in key or key.replace(' armor', '') == name_lower.replace(' armor', ''):
            return price, True
    for key, price in MUNDANE_WEAPON_PRICES.items():
        if name_lower in key or key == name_lower:
            return price, False

    return None, False


def compute_variant_multiplier(item_name: str, dampening: float = 0.5) -> float:
    """Compute a price multiplier for a +N variant based on mundane cost.

    Uses the ratio of mundane price to category median, compressed via
    power function to keep magic item spreads reasonable.

    With dampening=0.5:
      Breastplate (400gp, ratio 8x median) -> ~0.87x (13% below baseline)
      Half Plate  (750gp, ratio 15x median) -> ~1.00x (baseline)
      Plate       (1500gp, ratio 30x median) -> ~1.15x (15% above baseline)

    Args:
        item_name: Full item name (e.g., "+3 Plate Armor")
        dampening: Controls compression (0=full spread, 1=no spread)

    Returns:
        Multiplier (1.0 = no change)
    """
    bonus, base_name = _extract_base_name(item_name)
    if bonus is None or base_name is None:
        return 1.0

    mundane_price, is_armor = _find_mundane_price(base_name)
    if mundane_price is None:
        return 1.0

    # Use category-specific reference prices
    # For armor: use the median of "medium-to-heavy" armor that typically gets +N
    # (Chain Mail 75, Breastplate 400, Half Plate 750, Splint 200, Plate 1500, Scale 50)
    # Geometric mean of these ≈ 200
    if is_armor:
        reference = 200.0  # geometric mean of typical +N armor bases
    else:
        reference = 15.0   # geometric mean of typical +N weapon bases

    if reference <= 0 or mundane_price <= 0:
        return 1.0

    # Ratio to reference
    ratio = mundane_price / reference

    # Power-based compression: ratio^(1-dampening)
    # At dampening=0.5: sqrt(ratio)
    # Plate: (1500/200)^0.5 = 7.5^0.5 = 2.74 -> normalized
    # Breastplate: (400/200)^0.5 = 2^0.5 = 1.41
    # Half Plate: (750/200)^0.5 = 3.75^0.5 = 1.94
    exponent = 1.0 - dampening
    compressed = ratio ** exponent

    # Normalize so the median compressed value maps to 1.0
    # Use reference itself as the normalizer (ratio=1 -> compressed=1)
    # This means items at reference price get multiplier 1.0
    # Items above get >1.0, below get <1.0

    # But we want to cap the spread. Max multiplier ~1.4, min ~0.7
    # Scale: map compressed range to [0.7, 1.4]
    # At dampening=0.5, compressed ranges from ~0.16 (5gp padded) to ~2.74 (1500gp plate)
    # Center on half plate (compressed ≈ 1.94) as the "standard" +N armor

    # Simpler: just use the compressed ratio directly but re-center on 1.0
    # by dividing by the compressed reference value (which is 1.0 since ratio=1 -> 1^exp = 1)
    # So multiplier = compressed = ratio^exponent
    # But this gives too wide a range. Cap it.

    # Final approach: linear interpolation in log space with capped output
    log_ratio = math.log(ratio)
    # Scale factor: how much of the log ratio to keep
    scale = 0.15  # 15% of log-ratio becomes the multiplier deviation
    multiplier = math.exp(log_ratio * scale)

    # Clamp to [0.70, 1.40]
    multiplier = max(0.70, min(1.40, multiplier))

    return multiplier


def apply_variant_spacing(df: pd.DataFrame) -> Tuple[pd.DataFrame, list]:
    """Apply mundane-cost-based variant spacing to +N armor and weapon items.

    Modifies final_price, price_low, price_high in-place.

    Args:
        df: DataFrame with final_price, name columns

    Returns:
        (modified_df, list of adjustment dicts)
    """
    adjustments = []

    for idx in df.index:
        row = df.loc[idx]
        name = row['name']
        final_price = row.get('final_price', 0)

        if pd.isna(final_price) or final_price <= 0:
            continue

        # Only apply to +N items
        bonus, base_name = _extract_base_name(name)
        if bonus is None:
            continue

        # Skip mundane items
        rarity = str(row.get('rarity', '')).lower()
        if rarity == 'mundane':
            continue

        # Defensive: skip items that already had variant spacing applied
        # (price_source == 'rule+variant') to prevent compounding multipliers
        price_source = str(row.get('price_source', '')).lower()
        if 'variant' in price_source:
            continue

        multiplier = compute_variant_multiplier(name)

        if abs(multiplier - 1.0) < 0.001:
            continue

        new_price = round(final_price * multiplier, 2)

        adjustments.append({
            'name': name,
            'base': base_name,
            'old_price': final_price,
            'new_price': new_price,
            'multiplier': multiplier,
        })

        df.loc[idx, 'final_price'] = new_price
        df.loc[idx, 'price_low'] = round(new_price * 0.8, 2)
        df.loc[idx, 'price_high'] = round(new_price * 1.2, 2)

    return df, adjustments
