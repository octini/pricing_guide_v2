# src/criteria_extractor.py
import re
import json
from typing import Any, Optional

# Condition immunity values (shared with pricing_engine.py)
CONDITION_IMMUNITY_VALUES = {
    "frightened": 400,
    "charmed": 400,
    "poisoned": 400,
    "exhaustion": 400,
    "petrified": 400,
    "paralyzed": 400,
    "blinded": 400,
    "deafened": 400,
    "stunned": 400,
    "incapacitated": 400,
    "prone": 400,
    "restrained": 400,
}

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

    # Name (needed for ammunition type detection)
    c["name"] = item.get("name", "")

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
    # Note: bonusWeapon is used for items that grant weapon bonuses (e.g., Demon Armor's
    # unarmed strike bonus), not for the item being a +N weapon. Don't extract it for armor.
    item_type = item.get("type", "")
    is_armor = any(armor in item_type for armor in ["HA", "MA", "LA"])
    if not is_armor:
        c["weapon_bonus"] = _parse_bonus(item.get("bonusWeapon"))
    else:
        c["weapon_bonus"] = None
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

def extract_entries_criteria(item: dict, prose_text: str = "") -> dict:
    """Extract criteria from the entries field (prose with structured markers).
    
    Args:
        item: The raw item JSON dict
        prose_text: Optional prose description text (from items-sublist.md)
    """
    c = {
        "extra_damage_avg": 0.0,
        "extra_damage_dice": None, # Original dice string for reference
        "minor_beneficial": 0,
        "major_beneficial": 0,
        "minor_detrimental": 0,
        "major_detrimental": 0,
        "has_fixed_beneficial": False,
        "has_fixed_detrimental": False,
        "moonblade_properties": 0, # Average number of Moonblade properties
        "staff_forgotten_one_beneficial": 0, # Value of Staff of Forgotten One beneficial
        "staff_forgotten_one_detrimental": 0, # Value of Staff of Forgotten One detrimental
    }

    entries = item.get("entries", [])
    entries_str = str(entries)
    item_name = item.get("name", "")
    
    # Combine entries and prose for pattern matching
    combined_text = entries_str + " " + prose_text
    
    # Extract extra/additional damage
    # Pattern: "additional {@damage XdY}" or "extra {@damage XdY}"
    damage_matches = re.findall(r'(?:additional|extra) {@damage ([^}]+)}', combined_text)
    if damage_matches:
        # Sum all extra damage sources
        total_avg = 0.0
        for dmg_str in damage_matches:
            total_avg += _avg_dice(dmg_str)
        c["extra_damage_avg"] = total_avg
        # Store the first (or most significant) dice string
        c["extra_damage_dice"] = damage_matches[0] if len(damage_matches) == 1 else f"{len(damage_matches)} sources"
    
    # Extract artifact random properties
    # Pattern: "2 {@table Artifact Properties; Minor Beneficial Properties|dmg|minor beneficial} properties"
    # Or "1 randomly determined {@table Artifact Properties; Minor Beneficial Properties|dmg|minor beneficial}"
    artifact_pattern = r'(?<!\d)(\d+)\s*(?:randomly\s+determined\s*)?\{@table[^}]*Artifact Properties; (Minor|Major) (Beneficial|Detrimental)'
    for match in re.finditer(artifact_pattern, combined_text, re.IGNORECASE):
        count = int(match.group(1))
        size = match.group(2).lower() # "minor" or "major"
        prop_type = match.group(3).lower() # "beneficial" or "detrimental"
        key = f"{size}_{prop_type}"
        c[key] = count
    
    # Check for Moonblade's custom property table
    # Moonblade has 1d6+1 runes, first gives +1, rest give random properties
    # Average: 4.5 runes - 1 (for +1) = 3.5 random properties
    # Note: Moonblade variants are named "Moonblade Greatsword", "Moonblade Longsword", etc.
    if "Moonblade" in item_name:
        # Check for Moonblade Properties table in prose text
        if "Moonblade Properties" in prose_text or "Moonblade Properties" in entries_str:
            # Average number of properties: 1d6+1 - 1 = 3.5
            c["moonblade_properties"] = 3.5
    
    # Check for Staff of the Forgotten One's fixed properties
    # This item has specific beneficial and detrimental properties that need individual analysis
    if item_name == "Staff of the Forgotten One":
        # Beneficial: Expertise (5k), 6 condition immunities (12k), undead non-aggression (2k)
        c["staff_forgotten_one_beneficial"] = 19000
        # Detrimental: 50% possession chance on charge use (major detrimental)
        c["staff_forgotten_one_detrimental"] = 15000
    
    # Check for fixed beneficial/detrimental properties (non-random)
    # These are sections like "Beneficial Properties" or "Detrimental Properties"
    # that list specific abilities rather than random table references
    for entry in entries:
        if isinstance(entry, dict) and entry.get("type") == "entries":
            name = entry.get("name", "").lower()
            if name == "beneficial properties":
                c["has_fixed_beneficial"] = True
            elif name == "detrimental properties":
                c["has_fixed_detrimental"] = True
    
    return c

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
        "save_advantage": [],
        "condition_immunity_prose": [],
        "language_known": [],
        "unarmed_strike_bonus": None,
        "unarmed_strike_damage": None,
        "spell_casting_abilities": [],
        "curse_effects": [],
    }
    
    desc = description.lower()

    # Flight detection - must be about the user gaining flight ability
    # Look for phrases like "you can fly", "flying speed", "gain a fly speed"
    has_flying = (
        "flying speed" in desc or
        "fly speed" in desc or
        re.search(r'\byou can fly\b', desc) or
        re.search(r'\bgain.*fly\w* speed\b', desc) or
        re.search(r'\bfly\w* speed of \d+', desc) or
        re.search(r'\baction to fly\b', desc)
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
    daily_heal = re.search(r'(?:at dawn|each dawn|per day|once per day|next dawn).{0,100}regain\s+(\d+d?\d*[+\d]*)\s+hit points', desc)
    if not daily_heal:
        daily_heal = re.search(r'regain\s+(\d+d?\d*[+\d]*)\s+hit points.{0,50}(?:at dawn|each dawn|per day|next dawn|until the next dawn)', desc)
    if daily_heal:
        c["healing_daily_hp"] = int(_avg_dice(daily_heal.group(1)))
    
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
    
    # Wish effect - check for casting the Wish spell or explicitly granting a wish
    c["wish_effect"] = bool(re.search(r'\bcast\b[^.]{0,40}(?:the\s+)?(?:\*wish\*|\bwish\b\s*spell)|grant(?:s|ed|ing)?[^.]{0,40}\b(?:a|your|one)\s+(?:\*wishes?\*|\bwishes?\b)', desc, re.IGNORECASE))
    
    # Spell absorption
    c["spell_absorption"] = bool(re.search(r'(absorb|negate).{0,30}spell', desc))
    
    # Stealth advantage
    # Must be "advantage" not "disadvantage" - use negative lookbehind
    c["stealth_advantage"] = bool(
        re.search(r'(?<!dis)advantage.{0,30}(stealth|dexterity \(stealth\))', desc) or
        re.search(r'stealth.{0,30}(?<!dis)advantage', desc)
    )
    
    # Legendary resistance
    c["legendary_resistance"] = "legendary resistance" in desc
    
    # Speed types
    c["swim_speed"] = bool(re.search(r'\bswim(?:ming)? speed\b', desc))
    c["climb_speed"] = bool(re.search(r'\bclimb(?:ing)? speed\b', desc))
    c["burrow_speed"] = bool(re.search(r'\bburrow(?:ing)? speed\b', desc))
    
    # Saving throw advantage: "advantage on Intelligence, Wisdom, and Charisma saving throws"
    save_match = re.search(r'advantage on ([\w,\s]+?) saving throws', desc)
    if save_match:
        abilities = [a.strip().lower() for a in save_match.group(1).replace(' and ', ',').split(',')]
        c["save_advantage"] = [a for a in abilities if a in ('intelligence', 'wisdom', 'charisma', 'strength', 'dexterity', 'constitution')]
    
    # Condition immunity from prose (in addition to structured conditionImmune field)
    ci_match = re.search(r'immune to the ([\w\s]+?) condition', desc)
    if ci_match:
        conditions = [cond.strip().lower() for cond in ci_match.group(1).replace(' and ', ',').split(',')]
        c["condition_immunity_prose"] = [cond for cond in conditions if cond in CONDITION_IMMUNITY_VALUES]
    
    # Language known: "you know Abyssal"
    lang_match = re.search(r'you know (\w+)', desc)
    if lang_match:
        c["language_known"] = [lang_match.group(1)]
    
    # Unarmed strike bonus: "Unarmed Strike deals 1d8 slashing damage and you have a +1 bonus"
    us_bonus = re.search(r'unarmed strike.*?\+([-\d]+)\s*bonus', desc)
    if us_bonus:
        c["unarmed_strike_bonus"] = int(us_bonus.group(1))
    us_dmg = re.search(r'unarmed strike.*?(\d+d\d+)\s+(\w+)\s+damage', desc)
    if us_dmg:
        c["unarmed_strike_damage"] = f"{us_dmg.group(1)} {us_dmg.group(2)}"
    
    # Spell casting abilities: "cast *Speak with Dead* or *Animate Dead* once per dawn"
    # Spell names in 5e.tools prose are wrapped in asterisks (markdown italics)
    # Pattern: cast [*spell name*] or [*spell name*] [frequency]
    spell_match = re.findall(
        r'\bcast\s+(?:either\s+)?'           # "cast" or "cast either"
        r'\*([^*]+)\*'                        # *spell name*
        r'(?:\s+or\s+\*([^*]+)\*)?'           # optional " or *spell2*"
        r'(?:\s+(?:once|at will|per day|at-will))?',  # optional frequency
        desc
    )
    if spell_match:
        for m in spell_match:
            # m is a tuple: (spell1, spell2_or_empty)
            for spell_text in m:
                if spell_text:
                    spell_name = spell_text.strip()
                    # Filter out non-spell words
                    if spell_name and len(spell_name) > 2 and spell_name.lower() not in ('a', 'an', 'the', 'either', 'spell', 'spells'):
                        c["spell_casting_abilities"].append(spell_name)
    
    # Curse effects: look for curse-related text
    if re.search(r'curse|cursed|disadvantage against|disadvantage on.*saving throw', desc):
        curse_parts = []
        if re.search(r'disadvantage on.*saving throw.*demon', desc) or re.search(r'disadvantage against.*demon', desc):
            curse_parts.append("disadvantage_vs_demons")
        if re.search(r'armor.*destroyed', desc):
            curse_parts.append("armor_destroyed_on_death")
        if re.search(r'you die.*attuned', desc):
            curse_parts.append("death_while_attuned")
        c["curse_effects"] = curse_parts
    
    # Also check for curse-like effects even without the 'curse' keyword
    # Some items have curse-like effects but aren't flagged as cursed in JSON
    if not c["curse_effects"]:
        curse_parts = []
        if re.search(r'armor.*destroyed', desc) and re.search(r'you die.*attuned', desc):
            curse_parts.append("armor_destroyed_on_death")
            curse_parts.append("death_while_attuned")
        if curse_parts:
            c["curse_effects"] = curse_parts
    
    return c
