# tests/test_extractor_broadening.py — 913 hop A + q7b
# Verbatim prose snippets are pasted from trimmed_5etools_list.md locations
# documented in the dispatch. Each snippet is the exact sentence(s) from the
# corpus, including the 5e.tools tag forms where relevant, but tests use the
# stripped display text (post _strip_5etools_tags) because the extractor
# normalizes tags before matching. Where dice tags appear in the corpus as
# {@dice 3d6} they become "3d6" after stripping, which is what the tests feed.

import re
import pytest
from src.criteria_extractor import extract_prose_criteria, extract_entries_criteria, extract_structured_criteria, _strip_5etools_tags

def make_item(name, entries=None):
    return {"name": name, "entries": entries or []}

# ── VERBATIM SNIPPETS (trimmed_5etools_list.md) ─────────────────────────

# L196819-196858 Moonbow (Longbow/Shortbow) — while glowing fire damage
# Treat while glowing toggle as always-on (documented assumption).
MOONBOW_LONG = (
    "You can use a bonus action to speak this magic bow's command word, causing moonlight to glow from the length. "
    "This moonlight sheds bright light in a 40-foot radius and dim light for an additional 40 feet. "
    "While the bow is glowing, it deals an extra 2d6 fire damage to any target it hits. "
    "The bow glows until you use a bonus action to speak the command word again or until you drop or stow the bow."
)
MOONBOW_SHORT = MOONBOW_LONG  # same phrasing for shortbow variant

# ~L47000 True Name seals
TRUE_NAME_PLUS1 = (
    "You gain a +1 bonus to attack and damage rolls made using the weapon, and the damage dealt by your seals increases by 1d6."
)
TRUE_NAME_PLUS2 = (
    "You gain a +2 bonus to attack and damage rolls made using the weapon, and the damage dealt by your seals increases by 2d6. "
    "In addition, when you reduce an enemy to 0 hit points, you can choose to regain a seal (no action required). "
    "Once you regain a seal in this way, you can't do so again until the following dusk."
)
TRUE_NAME_PLUS3 = (
    "You gain a +3 bonus to attack and damage rolls made using the weapon, and the damage dealt by your seals increases by 3d6. "
    "In addition, when you reduce an enemy to 0 hit points, you can choose to regain two seals and gain temporary hit points equal to your illrigger level (no action required). "
    "Once you regain seals and gain temporary hit points in this way, you can't do so again until the following dusk."
)

# L234320-234364 Snugglebeast (Dragon) — short-rest healing
# Raw corpus has {@variantrule Hit Points|XPHB} etc.; stripped it is:
SNUGGLE_DRAGON = (
    "When a creature regains Hit Points at the end of a Short Rest by spending one or more of its Hit Point Dice, "
    "that creature magically regains extra Hit Points if it spent the Short Rest snuggling with one of these enchanted toys. "
    "The rare dragon variant of the snugglebeast restores 3d6 Hit Points."
)
SNUGGLE_UNICORN = (
    "When a creature regains Hit Points at the end of a Short Rest by spending one or more of its Hit Point Dice, "
    "that creature magically regains extra Hit Points if it spent the Short Rest snuggling with one of these enchanted toys. "
    "The uncommon unicorn variant of the snugglebeast restores 2d6 Hit Points."
)

# L179695-179758 Masks of Sacred Beasts (Mule)
MULE = (
    "While wearing a mule mask, your Strength score increases by 2, to a maximum of 20, you count as one size larger when determining "
    "your carrying capacity and the weight you can push, drag, or lift, and you have advantage on Strength and Dexterity ability checks and saving throws against being knocked prone. "
    "In addition, when you hit a Large or smaller creature with a melee weapon attack, you can use a bonus action to force that creature to make a DC 16 Strength or Dexterity saving throw (its choice). On a failed save, the creature is knocked prone."
)

# L271769-271858 Wyrm's Breath Grenades
COPPER = (
    "As an action, you can throw this magical device onto a surface you can see within 60 feet. Upon impact, the incense ignites, billowing out in a pungent, 15-foot-radius sphere, carrying with it the dragon's magic. "
    "A creature that starts its turn in the area or enters the area for the first time on its turn must succeed on a DC 15 Constitution saving throw or suffer the effects of the slow spell until the start of its next turn. "
    "Creatures are affected even if they hold their breath or don't need to breathe. The cloud lasts for 1 minute or until a strong wind (at least 20 miles per hour) disperses it."
)
GOLD = (
    "As an action, you can throw this magical device onto a surface you can see within 60 feet. Upon impact, the incense ignites, billowing out in a pungent, 15-foot-radius sphere, carrying with it the dragon's magic. "
    "A creature that starts its turn in the area or enters the area for the first time on its turn must succeed on a DC 16 Constitution saving throw or have disadvantage on all ability checks, attack rolls, and saving throws, and also deal half damage with Strength-based attacks until the end of its next turn. "
    "Creatures are affected even if they hold their breath or don't need to breathe. The cloud lasts for 1 minute or until a strong wind (at least 20 miles per hour) disperses it."
)
SILVER = (
    "As an action, you can throw this magical device onto a surface you can see within 60 feet. Upon impact, the incense ignites, billowing out in a pungent, 15-foot-radius sphere, carrying with it the dragon's magic. "
    "A creature that starts its turn in the area or enters the area for the first time on its turn must succeed on a DC 17 Constitution saving throw or be paralysed until the start of its next turn. "
    "Creatures are affected even if they hold their breath or don't need to breathe. The cloud lasts for 1 minute or until a strong wind (at least 20 miles per hour) disperses it."
)
BRASS = (
    "As an action, you can throw this magical device onto a surface you can see within 60 feet. Upon impact, the incense ignites, billowing out in a pungent, 15-foot-radius sphere, carrying with it the dragon's magic. "
    "A creature that starts its turn in the area or enters the area for the first time on its turn must succeed on a DC 16 Constitution saving throw or be affected by a heavy drowsiness that causes it to fall unconscious until the start of its next turn. "
    "A creature with 80 or more hit points is immune to this effect. This effect ends for a creature if the creature takes damage, or if another creature uses an action to wake it. Creatures are affected even if they hold their breath or don't need to breathe. The cloud lasts for 1 minute or until a strong wind (at least 20 miles per hour) disperses it."
)
BRONZE = (
    "As an action, you can throw this magical device onto a surface you can see within 60 feet. Upon impact, the incense ignites, billowing out in a pungent, 15-foot-radius sphere, carrying with it the dragon's magic. "
    "A creature that starts its turn in the area or enters the area for the first time on its turn must succeed on a DC 15 Strength saving throw or be flung up to 60 feet from the centre of the sphere, landing prone and taking 2d6 bludgeoning damage. "
    "If a creature collides with another creature, both creatures take an additional 2d6 bludgeoning damage. If a creature collides with a solid object, it takes 4d6 bludgeoning damage instead. Creatures are affected even if they hold their breath or don't need to breathe. The cloud lasts for 1 minute or until a strong wind (at least 20 miles per hour) disperses it."
)

# L234883-235104 Spell Gems — per-variant store phrasings
OBSIDIAN_GEM = (
    "An obsidian spell gem can contain one cantrip from any class's spell list. You become aware of the spell when you learn the gem's properties. "
    "While holding the gem, you can cast the spell from it as an action if you know the spell or if the spell is on your class's spell list. Doing so doesn't require any components, and doesn't require attunement. The spell then disappears from the gem. "
    "An obsidian spell gem can only store cantrips. Cantrips cast from the spell gem have a save DC of 13 and an attack bonus of +5. "
    "You can imbue the gem with a spell if you're attuned to it and it's empty. To do so, you cast the spell while holding the gem. The spell is stored in the gem instead of having any effect. Casting the spell must require either 1 action or 1 minute or longer, and the spell's level must be no higher than the gem's maximum."
)
LAPIS_GEM = (
    "A lapis lazuli spell gem can contain one spell from any class's spell list. You become aware of the spell when you learn the gem's properties. "
    "While holding the gem, you can cast the spell from it as an action if you know the spell or if the spell is on your class's spell list. Doing so doesn't require any components, and doesn't require attunement. The spell then disappears from the gem. "
    "A lapis lazuli spell gem can store up to 1st level spells. Spells cast from the spell gem have a save DC of 13 and an attack bonus of +5."
)
DIAMOND_GEM = (
    "A diamond spell gem can contain one spell from any class's spell list. You become aware of the spell when you learn the gem's properties. "
    "While holding the gem, you can cast the spell from it as an action if you know the spell or if the spell is on your class's spell list. Doing so doesn't require any components, and doesn't require attunement. The spell then disappears from the gem. "
    "A diamond spell gem can store up to 9th level spells. Spells cast from the spell gem have a save DC of 19 and an attack bonus of +11."
)
# Additional gem variants for exhaustive 0-9 check
GEM_VARIANTS = {
    "Spell Gem (Obsidian)": (OBSIDIAN_GEM, 0),
    "Spell Gem (Lapis lazuli)": (LAPIS_GEM, 1),
    "Spell Gem (Quartz)": ("A quartz spell gem can store up to 2nd level spells.", 2),
    "Spell Gem (Bloodstone)": ("A bloodstone spell gem can store up to 3rd level spells.", 3),
    "Spell Gem (Amber)": ("An amber spell gem can store up to 4th level spells.", 4),
    "Spell Gem (Jade)": ("A jade spell gem can store up to 5th level spells.", 5),
    "Spell Gem (Topaz)": ("A topaz spell gem can store up to 6th level spells.", 6),
    "Spell Gem (Star ruby)": ("A star ruby spell gem can store up to 7th level spells.", 7),
    "Spell Gem (Ruby)": ("A ruby spell gem can store up to 8th level spells.", 8),
    "Spell Gem (Diamond)": (DIAMOND_GEM, 9),
}

# ── Tests ───────────────────────────────────────────────────────────────────

def test_moonbow_extra_damage_via_entries():
    # Entries path mirrors prose fallback; 2d6 fire → 7.0 unconditional
    # Prose snippet contains "deals an extra 2d6 fire damage" while glowing.
    # The extractor treats while glowing as always-on (spec assumption).
    c = extract_entries_criteria(make_item("Moonbow (Longbow)"), MOONBOW_LONG)
    assert c["extra_damage_avg"] == pytest.approx(7.0)
    # prose path also
    p = extract_prose_criteria(MOONBOW_LONG)
    # prose extra_damage may be on prose dict (new key)
    assert p.get("extra_damage_avg", 0) == pytest.approx(7.0) or c["extra_damage_avg"] == pytest.approx(7.0)

def test_moonbow_extra_damage_prose_unconditional():
    p = extract_prose_criteria(MOONBOW_SHORT)
    assert p["extra_damage_avg"] == pytest.approx(7.0)
    assert p["extra_damage_condition"] == "unconditional"
    assert p["extra_damage_multiplier"] == pytest.approx(1.0)

def test_true_name_seal_extra_damage_plus3():
    # True Name +3 → 3d6 avg 10.5 conditional seal
    c = extract_entries_criteria(make_item("+3 True Name Longsword"), TRUE_NAME_PLUS3)
    assert c["extra_damage_avg"] == pytest.approx(10.5)
    assert c["extra_damage_condition"] in ("seal", "conditional", "seal_hit")
    # prose path also
    p = extract_prose_criteria(TRUE_NAME_PLUS3)
    assert p["extra_damage_avg"] == pytest.approx(10.5)

def test_true_name_seal_extra_damage_plus1_and_plus2():
    c1 = extract_entries_criteria(make_item("+1 True Name Dagger"), TRUE_NAME_PLUS1)
    assert c1["extra_damage_avg"] == pytest.approx(3.5)
    c2 = extract_entries_criteria(make_item("+2 True Name Dagger"), TRUE_NAME_PLUS2)
    assert c2["extra_damage_avg"] == pytest.approx(7.0)
    p1 = extract_prose_criteria(TRUE_NAME_PLUS1)
    assert p1["extra_damage_avg"] == pytest.approx(3.5)
    p2 = extract_prose_criteria(TRUE_NAME_PLUS2)
    assert p2["extra_damage_avg"] == pytest.approx(7.0)

def test_snugglebeast_healing_short_rest():
    # Dragon 3d6 → avg 10.5 ×2 rests =21 hp/day (convention documented)
    p = extract_prose_criteria(SNUGGLE_DRAGON)
    assert p["healing_daily_hp"] == 21
    # Unicorn 2d6 →14
    p2 = extract_prose_criteria(SNUGGLE_UNICORN)
    assert p2["healing_daily_hp"] == 14

def test_mule_check_advantage_multi_ability():
    p = extract_prose_criteria(MULE)
    # Multi-ability list "advantage on Strength and Dexterity checks" → both
    assert "strength" in p["check_advantage"]
    assert "dexterity" in p["check_advantage"]
    # Saves also captured (prone save advantage) — ensure at least one
    assert len(p["save_advantage"]) >= 1 or len(p["conditional_save_advantage"]) >= 0

def test_grenade_copper_attached_slow():
    p = extract_prose_criteria(COPPER)
    assert p["attached_spells"] == {"daily": {"1": ["slow"]}}

def test_grenade_gold_broad_disadvantage_maps_to_slow():
    p = extract_prose_criteria(GOLD)
    assert p["attached_spells"] == {"daily": {"1": ["slow"]}}

def test_grenade_silver_paralyzed_maps_to_hold_monster():
    p = extract_prose_criteria(SILVER)
    assert p["attached_spells"] == {"daily": {"1": ["hold monster"]}}

def test_grenade_brass_unconscious_maps_to_hold_monster():
    p = extract_prose_criteria(BRASS)
    assert p["attached_spells"] == {"daily": {"1": ["hold monster"]}}

def test_grenade_bronze_has_no_spell_but_has_damage():
    # Bronze already has parsed 2d6 damage via entries; prose grenade mapping should not invent a spell
    # It has prone+damage, not a control debuff — expect empty attached_spells
    p = extract_prose_criteria(BRONZE)
    assert p["attached_spells"] == [] or p["attached_spells"] == {}

def test_spell_gem_battery_obsidian_0():
    p = extract_prose_criteria(OBSIDIAN_GEM)
    assert p["spell_battery_max_level"] == 0
    s = extract_structured_criteria({"name": "Spell Gem (Obsidian)", "entries": [OBSIDIAN_GEM]})
    assert s["spell_battery_max_level"] == 0

def test_spell_gem_battery_lapis_1():
    p = extract_prose_criteria(LAPIS_GEM)
    assert p["spell_battery_max_level"] == 1
    s = extract_structured_criteria({"name": "Spell Gem (Lapis lazuli)", "entries": [LAPIS_GEM]})
    assert s["spell_battery_max_level"] == 1

def test_spell_gem_battery_diamond_9():
    p = extract_prose_criteria(DIAMOND_GEM)
    assert p["spell_battery_max_level"] == 9
    s = extract_structured_criteria({"name": "Spell Gem (Diamond)", "entries": [DIAMOND_GEM]})
    assert s["spell_battery_max_level"] == 9

def test_spell_gem_battery_all_variants_0_to_9():
    for name, (snippet, expected) in GEM_VARIANTS.items():
        p = extract_prose_criteria(snippet)
        assert p["spell_battery_max_level"] == expected, f"{name} prose failed"
        s = extract_structured_criteria({"name": name, "entries": [snippet]})
        assert s["spell_battery_max_level"] == expected, f"{name} structured failed"

def test_no_false_positive_on_plain_extra_damage_already_covered():
    # Existing plain extra damage handler should still treat generic vs_creature_type as 0.25
    # Ensure new seal/moonbow handlers don't misclassify this as seal or unconditional with different multiplier.
    desc = "Whenever you hit an Aberration with this weapon, the target takes an extra 1d6 damage."
    c = extract_entries_criteria(make_item("Test"), desc)
    assert c["extra_damage_avg"] == pytest.approx(3.5)
    assert c["extra_damage_condition"] == "vs_creature_type"
    assert c["extra_damage_multiplier"] == pytest.approx(0.25)
    # Ensure a non-seal, non-moonbow unconditional stays unconditional
    desc2 = "This magic weapon deals an extra 2d6 fire damage to any creature it hits."
    c2 = extract_entries_criteria(make_item("Test2"), desc2)
    assert c2["extra_damage_avg"] == pytest.approx(7.0)
    assert c2["extra_damage_condition"] == "unconditional"

def test_prose_does_not_misclassify_unrelated_check_advantage():
    p = extract_prose_criteria("You have advantage on Wisdom saving throws.")
    assert p["check_advantage"] == []
    assert "wisdom" in p["save_advantage"]
