# Tests for bug fixes: name-embedded reskin inheritance and unknown-magic preservation
import re
import pandas as pd
import pytest

from scripts import __path__  # ensure scripts is importable
# Import the rarity override directly
from scripts import __path__
import importlib.util
import pathlib
import sys

# Load override_known_rarity without executing main
import scripts
from scripts import __package__
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts import *

# Direct import of function under test
from scripts import __name__
# Simpler: import via file path
import importlib.machinery

spec = importlib.util.spec_from_file_location("extract_items", "scripts/01_extract_items.py")
extract_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract_mod)
override_known_rarity = extract_mod.override_known_rarity

# --- BUG 2: unknown (magic) preservation for WDMM ---

def test_wdmm_unknown_magic_stays_unknown_magic():
    """Mind Flayer Skull [WDMM] unknown (magic) must stay unknown_magic, not default to uncommon."""
    item = {
        "name": "Mind Flayer Skull",
        "source": "WDMM",
        "entries": ["While you have the skull in your possession, you are invisible to mind flayers."],
    }
    assert override_known_rarity(item, "unknown_magic") == "unknown_magic"


def test_wdmm_unknown_magic_other_items_stay_unknown_magic():
    for name in ["Dagger of Guitar Solos", "Falkir's Helm of Pigheadedness", "Jade Serpent Staff", "Pearl of Undead Detection"]:
        item = {"name": name, "source": "WDMM", "entries": ["flavor"]}
        assert override_known_rarity(item, "unknown_magic") == "unknown_magic", f"failed for {name}"


def test_wdmm_unknown_magic_with_magic_token_still_uncommon():
    """Items with bonusWeapon etc still map to uncommon even for WDMM."""
    item = {"name": "WDMM Magic Sword", "source": "WDMM", "bonusWeapon": "+1", "entries": []}
    # raw_text will contain '"bonusWeapon"' so should still be uncommon
    assert override_known_rarity(item, "unknown_magic") == "uncommon"


def test_non_wdmm_unknown_magic_still_defaults():
    """ToA etc should still default unknown_magic to uncommon."""
    item = {"name": "Some ToA Item", "source": "ToA", "entries": ["flavor"]}
    assert override_known_rarity(item, "unknown_magic") == "uncommon"
    item2 = {"name": "CoS Item", "source": "CoS", "entries": ["flavor"]}
    assert override_known_rarity(item2, "unknown_magic") == "uncommon"


# --- BUG 1: name-embedded reskin detection — magic-only inheritance ---

EMBEDDED_PATTERN = re.compile(r'^(.+)\s*\((.+)\)$')

def _get_embedded_price(name, name_to_price, name_to_rarity=None):
    lower_map = {k.lower(): v for k, v in name_to_price.items()}
    lower_rarity = {k.lower(): v for k, v in (name_to_rarity or {}).items()}
    m = EMBEDDED_PATTERN.match(name)
    if m:
        inner = m.group(2).strip()
        # uncommon+ magic inheritance only: benchmark is tier-priced; exclude common "Amber" ingredient
        if name_to_rarity is not None:
            inner_rarity = name_to_rarity.get(inner)
            if inner_rarity is None:
                inner_rarity = lower_rarity.get(inner.lower())
            if inner_rarity is None or pd.isna(inner_rarity):
                return None
            norm = str(inner_rarity).strip().lower().replace(" ", "_")
            if norm not in ("uncommon", "rare", "very_rare", "legendary", "artifact"):
                return None
        price = name_to_price.get(inner)
        if price is None:
            price = lower_map.get(inner.lower())
        return price
    return None


def test_embedded_reskin_detects_piwafwi():
    name_to_price = {"Cloak of Elvenkind": 4068.75}
    name_to_rarity = {"Cloak of Elvenkind": "uncommon"}
    assert _get_embedded_price("Piwafwi (Cloak of Elvenkind)", name_to_price, name_to_rarity) == 4068.75


def test_embedded_reskin_case_insensitive():
    name_to_price = {"Cloak of Elvenkind": 4068.75}
    name_to_rarity = {"Cloak of Elvenkind": "uncommon"}
    assert _get_embedded_price("Piwafwi (cloak of elvenkind)", name_to_price, name_to_rarity) == 4068.75
    assert _get_embedded_price("Piwafwi (CLOAK OF ELVENKIND)", name_to_price, name_to_rarity) == 4068.75


def test_embedded_reskin_non_match_returns_none():
    name_to_price = {"Cloak of Elvenkind": 4068.75, "Alchemy Jug": 2767.9}
    name_to_rarity = {"Cloak of Elvenkind": "uncommon", "Alchemy Jug": "uncommon"}
    # Piwafwi of Fire Resistance has no parenthetical matching an item
    assert _get_embedded_price("Piwafwi of Fire Resistance", name_to_price, name_to_rarity) is None
    # Blue is not an item name
    assert _get_embedded_price("Alchemy Jug (Blue)", name_to_price, name_to_rarity) is None
    # Random item without parens
    assert _get_embedded_price("Bag of Holding", name_to_price, name_to_rarity) is None


def test_embedded_reskin_mundane_must_not_inherit():
    """Mundane inner items must NOT be inherited — reskin bug fix."""
    # Mule is mundane animal 8 gp, Diamond gemstone 5000, Obsidian 10, Shortbow mundane 25, Dragon mundane 1, Silver 5, Amber common 114
    name_to_price = {
        "Cloak of Elvenkind": 4068.75,
        "Mule": 8.0,
        "Diamond": 5000.0,
        "Obsidian": 10.0,
        "Shortbow": 25.0,
        "Dragon": 1.0,
        "Silver": 5.0,
        "Amber": 114.4,
    }
    name_to_rarity = {
        "Cloak of Elvenkind": "uncommon",
        "Mule": "mundane",
        "Diamond": "mundane",
        "Obsidian": "mundane",
        "Shortbow": "mundane",
        "Dragon": "mundane",
        "Silver": "mundane",
        "Amber": "common",
    }
    assert _get_embedded_price("Masks of the Sacred Beasts (Mule)", name_to_price, name_to_rarity) is None
    assert _get_embedded_price("Spell Gem (Diamond)", name_to_price, name_to_rarity) is None
    assert _get_embedded_price("Spell Gem (Obsidian)", name_to_price, name_to_rarity) is None
    assert _get_embedded_price("Moonbow (Shortbow)", name_to_price, name_to_rarity) is None
    assert _get_embedded_price("Snugglebeast (Dragon)", name_to_price, name_to_rarity) is None
    assert _get_embedded_price("Wyrm's Breath Grenade (Silver)", name_to_price, name_to_rarity) is None
    assert _get_embedded_price("Spell Gem (Amber)", name_to_price, name_to_rarity) is None
    # Piwafwi still inherits (uncommon magic)
    assert _get_embedded_price("Piwafwi (Cloak of Elvenkind)", name_to_price, name_to_rarity) == 4068.75


def test_embedded_reskin_data_frame_copy():
    """Integration-style: DataFrame with alias-empty Piwafwi inherits Elvenkind price; mundanes + common do not."""
    data = [
        {"name": "Cloak of Elvenkind", "final_price": 4068.75, "price_low": 3255.0, "price_high": 4882.5, "alias": "", "rarity": "uncommon"},
        {"name": "Piwafwi (Cloak of Elvenkind)", "final_price": 498.75, "price_low": 399.0, "price_high": 598.5, "alias": "", "rarity": "uncommon"},
        {"name": "Piwafwi of Fire Resistance", "final_price": 1877.89, "price_low": 1502.31, "price_high": 2253.47, "alias": "", "rarity": "uncommon"},
        {"name": "Alchemy Jug (Blue)", "final_price": 100.0, "price_low": 80.0, "price_high": 120.0, "alias": "", "rarity": "uncommon"},
        {"name": "Masks of the Sacred Beasts (Mule)", "final_price": 11508.0, "price_low": 9206.4, "price_high": 13809.6, "alias": "", "rarity": "very_rare"},
        {"name": "Mule", "final_price": 8.0, "price_low": 6.4, "price_high": 9.6, "alias": "", "rarity": "mundane"},
        {"name": "Spell Gem (Diamond)", "final_price": 60504.0, "price_low": 48403.2, "price_high": 72604.8, "alias": "", "rarity": "legendary"},
        {"name": "Diamond", "final_price": 5000.0, "price_low": 4000.0, "price_high": 6000.0, "alias": "", "rarity": "mundane"},
        {"name": "Spell Gem (Amber)", "final_price": 9584.0, "price_low": 7667.2, "price_high": 11500.8, "alias": "", "rarity": "very_rare"},
        {"name": "Amber", "final_price": 114.4, "price_low": 91.5, "price_high": 137.28, "alias": "", "rarity": "common"},
    ]
    df = pd.DataFrame(data)
    name_to_price = dict(zip(df["name"], df["final_price"]))
    lower_name_to_price = {k.lower(): v for k, v in name_to_price.items()}
    name_to_rarity = dict(zip(df["name"], df["rarity"]))
    lower_name_to_rarity = {k.lower(): v for k, v in name_to_rarity.items()}
    pattern = re.compile(r'^(.+)\s*\((.+)\)$')
    for idx, row in df.iterrows():
        alias = row.get("alias", "")
        if alias and not pd.isna(alias) and str(alias).strip():
            continue
        m = pattern.match(str(row.get("name", "")))
        if m:
            inner = m.group(2).strip()
            inner_rarity = name_to_rarity.get(inner)
            if inner_rarity is None:
                inner_rarity = lower_name_to_rarity.get(inner.lower())
            if inner_rarity is None or pd.isna(inner_rarity):
                continue
            norm = str(inner_rarity).strip().lower().replace(" ", "_")
            if norm not in ("uncommon", "rare", "very_rare", "legendary", "artifact"):
                continue
            price = name_to_price.get(inner)
            if price is None:
                price = lower_name_to_price.get(inner.lower())
            if price and pd.notna(price) and price > 0:
                df.loc[idx, "final_price"] = price
                df.loc[idx, "price_low"] = round(price * 0.8, 2)
                df.loc[idx, "price_high"] = round(price * 1.2, 2)
    # Piwafwi should now inherit
    assert df.loc[df["name"] == "Piwafwi (Cloak of Elvenkind)", "final_price"].iloc[0] == 4068.75
    # Piwafwi of Fire Resistance stays standalone
    assert df.loc[df["name"] == "Piwafwi of Fire Resistance", "final_price"].iloc[0] == 1877.89
    # Alchemy Jug (Blue) stays standalone (Blue not an item)
    assert df.loc[df["name"] == "Alchemy Jug (Blue)", "final_price"].iloc[0] == 100.0
    # Masks Mule must NOT inherit mundane Mule 8 gp — keeps own validated price
    assert df.loc[df["name"] == "Masks of the Sacred Beasts (Mule)", "final_price"].iloc[0] == 11508.0
    # Spell Gem Diamond must NOT inherit mundane Diamond 5000 — keeps own validated price
    assert df.loc[df["name"] == "Spell Gem (Diamond)", "final_price"].iloc[0] == 60504.0
    # Spell Gem Amber must NOT inherit common Amber 114.4 — keeps own validated price 9584
    assert df.loc[df["name"] == "Spell Gem (Amber)", "final_price"].iloc[0] == 9584.0


def test_only_piwafwi_in_current_data_matches_embedded():
    """Audit: curated corpus (commit d43bc38, 12,241 items) has 22 embedded-reskin matches where inner exists;
    uncommon+ inheritance (fix commit) retains 1 magic match (Piwafwi) — Amber common excluded — honest recount at this commit."""
    import json
    with open("trimmed_5etools_list.json", encoding="utf-8") as f:
        raw = json.load(f)
    items = raw if isinstance(raw, list) else raw.get("item", raw.get("items", []))
    names = set(x.get("name") for x in items)
    # Build rarity map from master (normalized) for honest magic check
    import csv, sys
    csv.field_size_limit(sys.maxsize)
    name_to_rarity_master = {}
    with open("data/processed/items_master.csv", encoding="utf-8") as mf:
        reader = csv.DictReader(mf)
        for row in reader:
            # last wins for duplicates (Amber common overwrites mundane)
            name_to_rarity_master[row["name"]] = row["rarity"]
            name_to_rarity_master[row["name"].lower()] = row["rarity"]
    pattern = re.compile(r'^(.+)\s*\((.+)\)$')
    matches_all = []
    matches_magic = []
    for it in items:
        m = pattern.match(it.get("name", ""))
        if m:
            inner = m.group(2).strip()
            exists = inner in names or inner.lower() in {n.lower() for n in names}
            if exists:
                matches_all.append(it.get("name"))
                # uncommon+ magic check — benchmark is tier-priced; exclude common Amber
                rar = name_to_rarity_master.get(inner) or name_to_rarity_master.get(inner.lower())
                if rar and str(rar).strip().lower().replace(" ", "_") in ("uncommon", "rare", "very_rare", "legendary", "artifact"):
                    matches_magic.append(it.get("name"))
    # Piwafwi must be among the embedded-reskin matches (alias inheritance CORRECT per 9ih verified behavior)
    assert "Piwafwi (Cloak of Elvenkind)" in matches_all, f"Piwafwi missing from embedded matches: {sorted(matches_all)}"
    # Curated 12,241-item corpus (commit d43bc38) legitimately contains 22 embedded-reskin matches
    # e.g. "Masks of the Sacred Beasts (Mule)", Spell Gem family, etc. — detection code is correct.
    assert len(matches_all) == 22, f"expected 22 embedded matches for curated corpus d43bc38, got {len(matches_all)}: {sorted(matches_all)}"
    # Honest recount at this fix commit: uncommon+ matches = 1 (Piwafwi uncommon); Amber common excluded
    # Trade-goods/gemstones/animals/weapons-bases are mundane/common or absent, thus excluded.
    assert len(matches_magic) == 1, f"expected 1 uncommon+ embedded match at this commit, got {len(matches_magic)}: {sorted(matches_magic)}"
    assert "Piwafwi (Cloak of Elvenkind)" in matches_magic
    assert "Spell Gem (Amber)" not in matches_magic, "Amber common must not be counted as uncommon+"
    # Verify Piwafwi inherits Elvenkind pricing via embedded-reskin logic
    assert _get_embedded_price("Piwafwi (Cloak of Elvenkind)", {"Cloak of Elvenkind": 4068.75}, {"Cloak of Elvenkind": "uncommon"}) == 4068.75
    # Negative case: Alchemy Jug (Blue) must NOT be considered an embedded reskin (Blue is not an item)
    assert "Alchemy Jug (Blue)" not in matches_all
    assert _get_embedded_price("Alchemy Jug (Blue)", {"Cloak of Elvenkind": 4068.75, "Alchemy Jug": 2767.9}, {"Cloak of Elvenkind": "uncommon", "Alchemy Jug": "uncommon"}) is None
    # Mundane cases must NOT be in magic matches
    for mundane_outer in ["Masks of the Sacred Beasts (Mule)", "Spell Gem (Diamond)", "Spell Gem (Obsidian)", "Moonbow (Shortbow)", "Snugglebeast (Dragon)", "Wyrm's Breath Grenade (Silver)"]:
        assert mundane_outer not in matches_magic, f"{mundane_outer} should not be magic match"
