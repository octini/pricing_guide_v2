# src/criteria_extractor.py
import re
import json
from typing import Any, Optional

def _parse_bonus(val: Any) -> Optional[int]:
    """Parse bonus value which may be '+2', '2', 2, or None."""
    if val is None:
        return None
    if isinstance(val, int):
        return val
    if isinstance(val, str):
        m = re.match(r'^[+]?(-?\d+)$', val.strip())
        if m:
            return int(m.group(1))
    return None

def extract_structured_criteria(item: dict) -> dict:
    """Extract all objective criteria from JSON fields."""
    c = {}
    
    # Attunement
    req_attune_raw = item.get("reqAttune", False)
    if req_attune_raw is True:
        c["req_attune"] = "open"
        c["req_attune_class"] = None
    elif isinstance(req_attune_raw, str):
        c["req_attune"] = "class"
        c["req_attune_class"] = req_attune_raw
    else:
        c["req_attune"] = "none"
        c["req_attune_class"] = None
    
    # Bonuses
    c["weapon_bonus"] = _parse_bonus(item.get("bonusWeapon"))
    c["weapon_attack_bonus"] = _parse_bonus(item.get("bonusWeaponAttack"))
    c["weapon_damage_bonus"] = _parse_bonus(item.get("bonusWeaponDamage"))
    c["ac_bonus"] = _parse_bonus(item.get("bonusAc"))
    c["saving_throw_bonus"] = _parse_bonus(item.get("bonusSavingThrow"))
    c["ability_check_bonus"] = _parse_bonus(item.get("bonusAbilityCheck"))
    c["proficiency_bonus_mod"] = _parse_bonus(item.get("bonusProficiencyBonus"))
    c["spell_attack_bonus"] = _parse_bonus(item.get("bonusSpellAttack"))
    c["spell_save_dc_bonus"] = _parse_bonus(item.get("bonusSpellSaveDc"))
    c["spell_damage_bonus"] = _parse_bonus(item.get("bonusSpellDamage"))
    
    # Resistances/immunities
    c["damage_resistances"] = item.get("resist", []) or []
    c["damage_immunities"] = item.get("immune", []) or []
    c["damage_vulnerabilities"] = item.get("vulnerable", []) or []
    c["condition_immunities"] = item.get("conditionImmune", []) or []
    
    # Spells
    c["spell_scroll_level"] = item.get("spellScrollLevel")
    c["attached_spells"] = item.get("attachedSpells", []) or []
    
    # Charges
    c["charges"] = item.get("charges")
    c["recharge"] = item.get("recharge")
    c["recharge_amount"] = item.get("rechargeAmount")
    
    # Speed
    speed_mods = item.get("modifySpeed", {}) or {}
    c["speed_mods"] = speed_mods
    
    # Flags
    c["is_sentient"] = bool(item.get("sentient"))
    c["is_cursed"] = bool(item.get("curse"))
    c["is_tattoo"] = bool(item.get("tattoo"))
    c["is_wondrous"] = bool(item.get("wondrous"))
    c["is_focus"] = bool(item.get("focus"))
    c["is_poison"] = bool(item.get("poison"))
    c["is_firearm"] = bool(item.get("firearm"))
    
    # Type-derived flags
    item_type = item.get("type", "")
    c["is_ammunition"] = item_type == "A"
    c["is_shield"] = item_type == "S"
    
    # Stealth/strength
    c["stealth_penalty"] = bool(item.get("stealth"))
    c["strength_req"] = item.get("strength")
    c["crit_threshold"] = item.get("critThreshold")
    
    # Tier
    c["item_tier"] = item.get("tier")
    
    # Ability score mods
    c["ability_score_mods"] = item.get("ability", []) or []
    
    # Weapon properties
    c["weapon_properties"] = item.get("property", []) or []
    
    # Item type classification helpers
    c["item_type_code"] = item_type
    
    return c
