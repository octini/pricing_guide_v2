# src/generic_variant_mapper.py
"""Extract generic variant relationships from raw JSON data."""

import json
import re
import pandas as pd
from typing import Optional


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
    import math
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
