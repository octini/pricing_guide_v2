# tests/test_criteria_extractor.py
import json
import pytest
from src.criteria_extractor import extract_structured_criteria

def make_item(**kwargs):
    """Helper: build a minimal item dict."""
    base = {"name": "Test Item", "source": "PHB", "rarity": "rare"}
    base.update(kwargs)
    return base

def test_weapon_bonus_string():
    item = make_item(bonusWeapon="+2")
    c = extract_structured_criteria(item)
    assert c["weapon_bonus"] == 2

def test_weapon_bonus_int():
    item = make_item(bonusWeapon=1)
    c = extract_structured_criteria(item)
    assert c["weapon_bonus"] == 1

def test_ac_bonus():
    item = make_item(bonusAc="+1")
    c = extract_structured_criteria(item)
    assert c["ac_bonus"] == 1

def test_req_attune_open():
    item = make_item(reqAttune=True)
    c = extract_structured_criteria(item)
    assert c["req_attune"] == "open"
    assert c["req_attune_class"] is None

def test_req_attune_class_restricted():
    item = make_item(reqAttune="by a wizard")
    c = extract_structured_criteria(item)
    assert c["req_attune"] == "class"
    assert "wizard" in c["req_attune_class"]

def test_no_attune():
    item = make_item()
    c = extract_structured_criteria(item)
    assert c["req_attune"] == "none"

def test_is_sentient():
    item = make_item(sentient=True)
    c = extract_structured_criteria(item)
    assert c["is_sentient"] is True

def test_is_cursed():
    item = make_item(curse=True)
    c = extract_structured_criteria(item)
    assert c["is_cursed"] is True

def test_spell_scroll_level():
    item = make_item(spellScrollLevel=3)
    c = extract_structured_criteria(item)
    assert c["spell_scroll_level"] == 3

def test_damage_resistances():
    item = make_item(resist=["fire", "cold"])
    c = extract_structured_criteria(item)
    assert c["damage_resistances"] == ["fire", "cold"]

def test_charges():
    item = make_item(charges=7)
    c = extract_structured_criteria(item)
    assert c["charges"] == 7

def test_is_ammunition():
    item = make_item(type="A")
    c = extract_structured_criteria(item)
    assert c["is_ammunition"] is True

def test_is_wondrous():
    item = make_item(wondrous=True)
    c = extract_structured_criteria(item)
    assert c["is_wondrous"] is True


def test_nested_variation_phrase_marks_generic_parent():
    item = make_item(
        name="Aussie Creature: Hairy-Nosed Wombat",
        source="GriffonsSaddlebag2",
        rarity="varies",
        entries=[
            {
                "type": "entries",
                "entries": [
                    "Multiple variations of this item exist, as listed below.",
                    {"type": "list", "items": ["Common", "Uncommon"]},
                ],
            }
        ],
    )

    c = extract_structured_criteria(item)

    assert c["is_generic_variant"] is True


def test_varies_rarity_without_nested_variation_phrase_is_not_generic_parent():
    item = make_item(
        name="Elemental Essence Shard",
        source="TEST",
        rarity="varies",
        entries=["The shard's power varies according to the plane where it formed."],
    )

    c = extract_structured_criteria(item)

    assert c["is_generic_variant"] is False

def test_tattoo():
    item = make_item(tattoo=True)
    c = extract_structured_criteria(item)
    assert c["is_tattoo"] is True


def test_structured_extracts_firearm_reload():
    item = make_item(type="MF", firearm=True, reload=6)

    c = extract_structured_criteria(item)

    assert c["reload"] == 6


def test_structured_extracts_armor_ac_and_strength_requirement():
    item = make_item(type="HA|XPHB", ac=18, strength="15")

    c = extract_structured_criteria(item)

    assert c["armor_ac"] == 18
    assert c["armor_strength_req"] == 15


def test_structured_ignores_non_armor_ac_for_armor_columns():
    item = make_item(type="RG", ac=16)

    c = extract_structured_criteria(item)

    assert c["armor_ac"] is None


def test_structured_does_not_conflate_shield_bonus_with_armor_ac():
    item = make_item(type="S", ac=2)

    c = extract_structured_criteria(item)

    assert c["armor_ac"] is None


def test_structured_extracts_vehicle_stats():
    item = make_item(
        type="SHP",
        vehSpeed=2,
        vehAc=15,
        vehHp=200,
        crew=15,
        capCargo=100,
    )

    c = extract_structured_criteria(item)

    assert c["vehicle_speed"] == 2
    assert c["vehicle_ac"] == 15
    assert c["vehicle_hp"] == 200
    assert c["vehicle_crew"] == 15
    assert c["vehicle_cargo_capacity"] == 100

# NLP prose criteria tests
from src.criteria_extractor import extract_prose_criteria

def test_flight_full():
    desc = "While wearing this cloak, you have a flying speed of 30 feet."
    c = extract_prose_criteria(desc)
    assert c["flight_full"] is True
    assert c["flight_limited"] is False

def test_flight_limited():
    desc = "You can use an action to fly for up to 1 minute."
    c = extract_prose_criteria(desc)
    assert c["flight_full"] is False
    assert c["flight_limited"] is True

def test_darkvision():
    desc = "You gain darkvision out to a range of 60 feet."
    c = extract_prose_criteria(desc)
    assert c["darkvision_feet"] == 60

def test_truesight():
    desc = "You gain truesight out to a range of 30 feet."
    c = extract_prose_criteria(desc)
    assert c["truesight"] is True

def test_teleportation():
    desc = "As an action, you can teleport to any unoccupied space."
    c = extract_prose_criteria(desc)
    assert c["teleportation"] is True

def test_invisibility_at_will():
    desc = "As an action, you become invisible until you attack."
    c = extract_prose_criteria(desc)
    assert c["invisibility_atwill"] is True

def test_healing_consumable():
    desc = "You regain 2d4+2 hit points when you drink this potion."
    c = extract_prose_criteria(desc)
    assert c["healing_consumable_avg"] > 0


@pytest.mark.parametrize(
    ("desc", "expected_avg"),
    [
        ("The creature regains 2d4 + 2 hit points when it drinks this potion.", 7.0),
        ("You regain 2d4 + 2 hit points when you drink this potion.", 7.0),
        ("You regain 10 hit points when you drink this potion.", 10.0),
    ],
)
def test_healing_consumable_handles_regains_spaced_dice_and_flat_text(desc, expected_avg):
    c = extract_prose_criteria(desc)
    assert c["healing_consumable_avg"] == pytest.approx(expected_avg)


@pytest.mark.parametrize(
    "desc",
    [
        "If you hit an Undead with this weapon, you take 1d10 Necrotic damage, and the target regains 1d10 Hit Points.",
        "The target regains 2d8 + 2 hit points, and all diseases and poisons affecting it are removed. The tooth regains all expended charges daily at dawn.",
        "One creature you can see within 30 feet either takes radiant damage or regains hit points equal to the total.",
        "The target regains 2d4 + 2 hit points.",
        "The enemy regains 10 hit points.",
        "The object regains 10 hit points.",
        "When the treant finishes a long rest, it repairs the ship's hull, enabling the ship to regain 4d12 hit points.",
        "You gain 2d4 + 2 temporary hit points when you press this medal to your mouth.",
        "The target can't regain 10 hit points until the curse ends.",
    ],
)
def test_healing_consumable_ignores_non_consumable_or_harmful_contexts(desc):
    c = extract_prose_criteria(desc)
    assert c["healing_consumable_avg"] == 0
    assert c["healing_daily_hp"] == 0

def test_healing_daily():
    desc = "At dawn, you regain 10 hit points."
    c = extract_prose_criteria(desc)
    assert c["healing_daily_hp"] == 10
    assert c["healing_consumable_avg"] == 0

def test_tome_manual():
    desc = "This tome contains wisdom and insight. After 48 hours of study, your Wisdom score increases by 2."
    c = extract_prose_criteria(desc)
    assert c["tome_manual_boost"] is True

def test_concentration_free():
    desc = "This effect doesn't require concentration."
    c = extract_prose_criteria(desc)
    assert c["concentration_free"] is True

def test_crit_immunity():
    desc = "While you wear this armor, critical hits against you are treated as normal hits."
    c = extract_prose_criteria(desc)
    assert c["crit_immunity"] is True


def test_prose_extracts_advantage_on_ability_and_skill_checks():
    desc = "While wearing this cloak, you have advantage on Strength checks and Dexterity (Stealth) checks."

    c = extract_prose_criteria(desc)

    assert c["check_advantage"] == ["strength", "dexterity (stealth)"]


def test_prose_extracts_advantage_on_tool_checks():
    desc = "You have advantage on ability checks you make with jeweler's tools."

    c = extract_prose_criteria(desc)

    assert c["check_advantage"] == ["jeweler's tools"]


def test_prose_keeps_later_generic_advantage_clause_after_specific_check():
    desc = "You have advantage on Dexterity (Stealth) checks. You have advantage on ability checks that rely on smell."

    c = extract_prose_criteria(desc)

    assert c["check_advantage"] == ["dexterity (stealth)", "ability checks"]


def test_prose_keeps_later_generic_disadvantage_clause_after_specific_check():
    desc = "You have disadvantage on Dexterity checks. You have disadvantage on ability checks that rely on smell."

    c = extract_prose_criteria(desc)

    assert c["check_disadvantage"] == ["dexterity", "ability checks"]


def test_prose_normalizes_5etools_skill_markup_in_check_targets():
    desc = "You have advantage on Charisma ({@skill Intimidation}) checks."

    c = extract_prose_criteria(desc)

    assert c["check_advantage"] == ["charisma (intimidation)"]


def test_prose_matches_variantrule_advantage_tag_on_check_surface():
    desc = "You have {@variantrule Advantage|XPHB} on Wisdom (Perception) checks."

    c = extract_prose_criteria(desc)

    assert c["check_advantage"] == ["wisdom (perception)"]


def test_prose_matches_variantrule_disadvantage_tag_on_save_surface():
    desc = "You have {@variantrule Disadvantage|XPHB} on Wisdom saving throws."

    c = extract_prose_criteria(desc)

    assert c["save_disadvantage"] == ["wisdom"]


def test_prose_tag_normalization_preserves_condition_immunity_extraction():
    desc = "While wearing this ring, you are immune to the {@condition Blinded|XPHB} condition."

    c = extract_prose_criteria(desc)

    assert c["condition_immunity_prose"] == ["blinded"]


def test_prose_extracts_all_targets_from_compound_ability_skill_check_phrase():
    desc = "You have advantage on Wisdom (Insight) and Charisma (Persuasion) checks."

    c = extract_prose_criteria(desc)

    assert c["check_advantage"] == ["wisdom (insight)", "charisma (persuasion)"]


def test_prose_maps_bare_skill_check_names_to_canonical_targets():
    desc = "You have advantage on Perception checks, Survival checks, and Stealth checks."

    c = extract_prose_criteria(desc)

    assert c["check_advantage"] == ["wisdom (perception)", "wisdom (survival)", "dexterity (stealth)"]


def test_prose_extracts_generic_advantage_on_all_saving_throws():
    desc = "You have advantage on all saving throws."

    c = extract_prose_criteria(desc)

    assert c["save_advantage"] == ["saving throws"]


def test_prose_preserves_compound_ability_save_advantage_order():
    desc = "You have advantage on Intelligence, Wisdom, and Charisma saving throws."

    c = extract_prose_criteria(desc)

    assert c["save_advantage"] == ["intelligence", "wisdom", "charisma"]


def test_prose_extracts_generic_disadvantage_on_saving_throws():
    desc = "You have disadvantage on saving throws."

    c = extract_prose_criteria(desc)

    assert c["save_disadvantage"] == ["saving throws"]



def test_prose_does_not_treat_target_tagged_disadvantage_as_wearer_drawback():
    desc = "The target has {@variantrule Disadvantage|XPHB} on all saving throws until the end of its next turn."

    c = extract_prose_criteria(desc)

    assert c["save_disadvantage"] == []


def test_prose_extracts_disadvantage_on_checks_and_saves_as_drawbacks():
    desc = "While cursed, you have disadvantage on Dexterity checks and Wisdom saving throws."

    c = extract_prose_criteria(desc)

    assert c["check_disadvantage"] == ["dexterity"]
    assert c["save_disadvantage"] == ["wisdom"]


def test_prose_does_not_treat_target_disadvantage_as_drawback():
    desc = "When you hit a creature, the target has disadvantage on Strength checks until the end of its next turn."

    c = extract_prose_criteria(desc)

    assert c["check_disadvantage"] == []
