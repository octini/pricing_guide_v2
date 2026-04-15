# src/variant_adjuster.py
"""Category-aware variant price adjustment system."""

import math
import pandas as pd
from typing import Optional


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
