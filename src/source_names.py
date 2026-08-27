"""Source-code display names for 5e.tools sources.

Names are loaded from ``docs/reference/ttrpg-convert-cli-sourceMap.md``, a saved
reference copy of ebullient/ttrpg-convert-cli's ``docs/sourceMap.md``. This keeps
the pricing guide aligned with the reference map without adding a Java CLI
runtime dependency.
"""

from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path
from typing import Final


SOURCE_MAP_REFERENCE_PATH: Final[Path] = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "reference"
    / "ttrpg-convert-cli-sourceMap.md"
)

# Local supplements for legitimate project sources that appear in current
# pipeline data/output but are absent from the saved ttrpg-convert sourceMap.
# These entries are carried forward from the previous hand-curated script maps;
# they are not guesses for unknown codes.
LOCAL_SOURCE_NAME_SUPPLEMENTS: Final[dict[str, str]] = {
    "MonstersOfDrakkenheim": "Monsters of Drakkenheim",
    "DungeonsDrakkenheim": "Dungeons of Drakkenheim",
    "ExploringEberron24": "Exploring Eberron (2024)",
    "ChroniclesOfEberron": "Chronicles of Eberron",
    "FoEQuickstone": "Frontiers of Eberron: Quickstone",
    "SAT": "Sigil and the Outlands",
    "24GriffonsSaddlebag1": "The Griffon's Saddlebag: Book One",
    "GriffonsSaddlebag2": "The Griffon's Saddlebag: Book Two",
    "ObojimaTallGrass": "Obojima: Tales from the Tall Grass",
    "HelianasGuidetoMonsterHunting": "Heliana's Guide to Monster Hunting",
    "CallfromtheDeep": "Call from the Deep",
    "IllriggerRevised": "The Illrigger Revised",
    "GrimHollowCG24": "Grim Hollow: Campaign Guide (2024/Transformed)",
    "WhereEvilLives": "Where Evil Lives: The MCDM Book of Boss Battles",
    "TalDoreiCampaignSettingReborn": "Tal'Dorei Campaign Setting Reborn",
    "GrimHollowPG24": "Grim Hollow: Player's Guide (2024)",
    "GrimHollowLairsEtharis": "Grim Hollow: Lairs of Etharis",
    "BookOfEbonTides": "Book of Ebon Tides",
    "CrookedMoon24": "The Crooked Moon",
    "HumblewoodTales": "Humblewood Tales",
    "Pugilist2024": "The Pugilist Class (2024)",
    "HumblewoodCampaignSetting": "Humblewood Campaign Setting",
    "OneShotWondersHolidayPack": "One-Shot Wonders: Holiday Adventure Pack",
    "GrimHollowPlayerPack": "Grim Hollow: Player Pack",
    "FleeMortals": "Flee, Mortals! The MCDM Monster Book",
    "TalesFromTheShadows": "Tales from the Shadows",
    "ValdaGunslinger": "Valda's Spire of Secrets: Gunslinger",
    "ValdaPlayerPack": "Valda's Spire of Secrets: Player Pack",
    "CthulhuTorchlight": "Cthulhu by Torchlight",
}


def _is_missing_source_code(source_code: object) -> bool:
    """Return True for missing scalar values from CSV/Pandas inputs."""
    if source_code is None:
        return True
    if isinstance(source_code, float) and math.isnan(source_code):
        return True
    return str(source_code).strip() in {"", "nan", "NaN", "<NA>"}


@lru_cache(maxsize=1)
def load_source_name_map() -> dict[str, str]:
    """Load 5e.tools source display names from the saved sourceMap reference."""
    source_names: dict[str, str] = {}
    aliases: dict[str, str] = {}
    section: str | None = None

    for raw_line in SOURCE_MAP_REFERENCE_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "### 5eTools Abbreviations to long name":
            section = "source_names"
            continue
        if line == "### 5eTools Alternate abbreviation mapping":
            section = "aliases"
            continue
        if line.startswith("### ") or line.startswith("## "):
            section = None
            continue
        if not section or not line.startswith("|"):
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells or cells[0] == "Abbreviation" or set(cells[0]) == {"-"}:
            continue

        if section == "source_names" and len(cells) >= 2:
            abbreviation, long_name = cells[0], cells[1]
            if abbreviation and long_name:
                source_names[abbreviation] = long_name
        elif section == "aliases" and len(cells) >= 2:
            abbreviation, alias = cells[0], cells[1]
            if abbreviation and alias:
                aliases[abbreviation] = alias

    for abbreviation, alias in aliases.items():
        if alias in source_names:
            source_names[abbreviation] = source_names[alias]

    source_names.update(LOCAL_SOURCE_NAME_SUPPLEMENTS)

    return source_names


def translate_source(source_code: object) -> str:
    """Translate source code(s) to display names, falling back to the raw code.

    Multiple source codes can be pipe-separated, matching the shape emitted by
    5e.tools item data. Unknown codes intentionally fall back to the code rather
    than an invented title.
    """
    if _is_missing_source_code(source_code):
        return "Unknown"

    source_names = load_source_name_map()
    translated: list[str] = []
    for code in str(source_code).split("|"):
        source = code.strip()
        if not source:
            continue
        translated.append(source_names.get(source, source))
    return ", ".join(translated) if translated else "Unknown"
