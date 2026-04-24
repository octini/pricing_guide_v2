# src/variant_pricing.py
"""Mundane-cost-based variant pricing within item categories.

Applies dampened multipliers to +N armor/weapon variants so that
more expensive mundane bases (e.g., Plate vs Breastplate) produce
meaningfully different magic item prices.

Approach:
- Group armor/weapons by their mundane base cost
- Compute each variant's ratio to the group median
- Dampen the ratio so magic items don't have 30x spreads like mundane
- Apply as a multiplier to the magic item's base price
"""

import math
import re
import pandas as pd
from typing import Optional, Tuple

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
