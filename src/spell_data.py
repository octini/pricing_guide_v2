"""Spell level lookup for attached_spells pricing."""

import json
from pathlib import Path

SPELL_LEVELS = {}

_SPELLS_FILE = Path(__file__).parent.parent / "spells-sublist.json"
if _SPELLS_FILE.exists():
    with open(_SPELLS_FILE) as f:
        _spells_data = json.load(f)
        for spell in _spells_data:
            name = spell["name"].lower()
            level = spell.get("level", 0)
            SPELL_LEVELS[name] = level

MANUAL_SPELL_LEVELS = {
    "protection from evil and good": 1,
    "false life": 1,
    "haste": 3,
    "control water": 4,
    "protection from energy": 3,
    "freedom of movement": 4,
    "barkskin": 2,
    "warding bond": 2,
    "death ward": 4,
    "fire shield": 4,
    "stoneskin": 4,
    "polymorph": 4,
    "fabricate": 4,
    "move earth": 6,
    "wish": 9,
    "word of recall": 6,
    "suggestion": 2,
    "scrying": 5,
    "thunderwave": 1,
    "create or destroy water": 1,
    "enlarge/reduce": 2,
    "invisibility": 2,
    "major image": 3,
    "fireball": 3,
}
SPELL_LEVELS.update(MANUAL_SPELL_LEVELS)


def normalize_spell_name(name: str) -> str:
    """Normalize spell name for lookup.

    - Lowercase
    - Remove source suffixes (|xphb, |phb, etc.)
    - Remove count suffixes (#4, etc.)

    Args:
        name: Raw spell name from attached_spells field

    Returns:
        Normalized spell name

    Examples:
        >>> normalize_spell_name("fireball|xphb")
        'fireball'
        >>> normalize_spell_name("thunderwave#4")
        'thunderwave'
    """
    normalized = name.lower()
    normalized = normalized.split("|")[0]
    normalized = normalized.split("#")[0]
    return normalized


def get_spell_level(name: str) -> int:
    """Get spell level from lookup table.

    Args:
        name: Spell name (may include source/count suffixes)

    Returns:
        Spell level (0-9), defaults to 1 if unknown

    Examples:
        >>> get_spell_level("fireball")
        3
        >>> get_spell_level("wish|xphb")
        9
        >>> get_spell_level("unknown spell")
        1
    """
    normalized = normalize_spell_name(name)
    return SPELL_LEVELS.get(normalized, 1)
