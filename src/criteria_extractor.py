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
    # Check for ammo flag in raw JSON (for generic variants like "+1 Ammunition")
    # Item type may include source suffix (e.g., "A|XPHB"), so check prefix
    item_type_base = item_type.split("|")[0] if isinstance(item_type, str) else item_type
    c["is_ammunition"] = item_type_base == "A" or item.get("ammo", False)
    c["is_shield"] = item_type_base == "S"
    
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

    # Generic variant detection
    # Items with 'items' field are generic variants (e.g., "Horn of Valhalla" has variants like "Horn of Valhalla, Brass")
    # These should be excluded from pricing guide since specific variants are already included
    c["is_generic_variant"] = "items" in item

    # Material detection (mithral, adamantine, silvered)
    # Check item name for material keywords
    item_name = item.get("name", "").lower()
    c["material"] = None
    if "mithral" in item_name:
        c["material"] = "mithral"
    elif "adamantine" in item_name:
        c["material"] = "adamantine"
    elif "silvered" in item_name or "silver" in item_name:
        # "Silvered" is the coating, "Silver" might be the material
        # Check if it's a silvered weapon (coating) vs silver item
        if "silvered" in item_name:
            c["material"] = "silvered"
        elif item_type in ("M", "R", "A"):  # Melee, Ranged, Ammunition
            c["material"] = "silvered"

    return c

def _avg_dice(dice_str: str) -> float:
    """Compute average of a dice expression like '2d4+2'."""
    total = 0.0
    # Match NdM parts
    for m in re.finditer(r'(\d+)d(\d+)', dice_str):
        n, d = int(m.group(1)), int(m.group(2))
        total += n * (d + 1) / 2
    # Add flat modifiers
    for m in re.finditer(r'[+](\d+)(?!d)', dice_str):
        total += int(m.group(1))
    return total

def extract_prose_criteria(description: str) -> dict:
    """Extract pricing-relevant criteria from prose item description."""
    c = {
        "flight_full": False,
        "flight_limited": False,
        "darkvision_feet": 0,
        "truesight": False,
        "blindsight": False,
        "tremorsense": False,
        "teleportation": False,
        "invisibility_atwill": False,
        "healing_daily_hp": 0,
        "healing_consumable_avg": 0.0,
        "healing_permanent_hp": 0,
        "tome_manual_boost": False,
        "concentration_free": False,
        "crit_immunity": False,
        "wish_effect": False,
        "spell_absorption": False,
        "stealth_advantage": False,
        "legendary_resistance": False,
        "swim_speed": False,
        "climb_speed": False,
        "burrow_speed": False,
    }
    
    desc = description.lower()

    # Flight detection - must be about the user gaining flight ability
    # Look for phrases like "you can fly", "flying speed", "gain a fly speed"
    has_flying = (
        "flying speed" in desc or
        "fly speed" in desc or
        re.search(r'\byou can fly\b', desc) or
        re.search(r'\bgain.*fly\w* speed\b', desc) or
        re.search(r'\bfly\w* speed of \d+', desc)
    )
    if has_flying:
        limited_keywords = ["minute", "hour", "until you land", "limited", "short rest", "long rest", "until you attack", "concentration", "action to end", "up to"]
        is_limited = any(k in desc for k in limited_keywords)
        if is_limited:
            c["flight_limited"] = True
        else:
            c["flight_full"] = True
    
    # Darkvision
    dv_match = re.search(r'darkvision.*?(\d+)\s*feet', desc)
    if dv_match:
        c["darkvision_feet"] = int(dv_match.group(1))
    
    # Truesight / blindsight / tremorsense
    c["truesight"] = "truesight" in desc
    c["blindsight"] = "blindsight" in desc
    c["tremorsense"] = "tremorsense" in desc
    
    # Teleportation
    c["teleportation"] = bool(re.search(r'\bteleport\b', desc))
    
    # Invisibility (at-will, not spell-based)
    # Must be about the user turning invisible, not just "invisible writing" or similar
    # Look for phrases like "turn invisible", "become invisible", "you are invisible"
    if re.search(r'\b(turn|become|you are|you can become)\s+invisible\b', desc):
        if "spell" not in desc[:desc.find("invisible")] if "invisible" in desc else True:
            c["invisibility_atwill"] = True
    
    # Healing: consumable
    heal_match = re.search(r'regain\s+(\d+d?\d*[+\d]*)\s+hit points', desc)
    if heal_match:
        c["healing_consumable_avg"] = _avg_dice(heal_match.group(1))
    
    # Healing: daily
    daily_heal = re.search(r'(?:at dawn|each dawn|per day|once per day).{0,100}regain\s+(\d+)\s+hit points', desc)
    if not daily_heal:
        daily_heal = re.search(r'regain\s+(\d+)\s+hit points.{0,50}(?:at dawn|each dawn|per day)', desc)
    if daily_heal:
        c["healing_daily_hp"] = int(daily_heal.group(1))
    
    # Tome/Manual permanent boost
    c["tome_manual_boost"] = bool(
        re.search(r'(manual|tome).{0,200}(score increases|score increase)', desc)
    )
    
    # Concentration-free
    c["concentration_free"] = "doesn't require concentration" in desc or "does not require concentration" in desc
    
    # Critical hit immunity
    c["crit_immunity"] = bool(
        re.search(r'critical hits?.{0,50}(treated as|normal hit)', desc)
    )
    
    # Wish effect
    c["wish_effect"] = bool(re.search(r'\bwish\b', desc))
    
    # Spell absorption
    c["spell_absorption"] = bool(re.search(r'(absorb|negate).{0,30}spell', desc))
    
    # Stealth advantage
    c["stealth_advantage"] = bool(
        re.search(r'advantage.{0,30}(stealth|dexterity \(stealth\))', desc) or
        re.search(r'stealth.{0,30}advantage', desc)
    )
    
    # Legendary resistance
    c["legendary_resistance"] = "legendary resistance" in desc
    
    # Speed types
    c["swim_speed"] = bool(re.search(r'\bswim(?:ming)? speed\b', desc))
    c["climb_speed"] = bool(re.search(r'\bclimb(?:ing)? speed\b', desc))
    c["burrow_speed"] = bool(re.search(r'\bburrow(?:ing)? speed\b', desc))
    
    return c
