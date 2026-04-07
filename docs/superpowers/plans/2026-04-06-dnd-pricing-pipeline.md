# D&D 5e Pricing Pipeline v2 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an 8-phase Python pipeline that assigns consistent, reproducible gold piece prices to all 9,422 D&D 5e items and produces a formatted Excel spreadsheet with 5e.tools hyperlinks.

**Architecture:** Standalone scripts in `scripts/` (01–08) drive each phase; shared logic lives in `src/`. Intermediate data flows through `data/processed/` CSVs. Each phase is independently runnable.

**Tech Stack:** Python 3.11+, pandas, openpyxl, rapidfuzz, scikit-learn/XGBoost, pdfplumber, requests, spacy (en_core_web_sm), pytest

---

## File Map

### Created by this plan

**src/**
- `src/utils.py` — Shared utilities: normalize_item_name, parse_value_cp, get_5etools_url
- `src/criteria_extractor.py` — JSON field extraction + NLP prose extraction
- `src/pricing_engine.py` — Rule-based formula calculation
- `src/amalgamator.py` — Fuzzy matching, outlier trimming, weighted amalgamation
- `src/anomaly_detector.py` — IQR outlier detection, deviation metrics

**scripts/**
- `scripts/01_extract_items.py` — Parse items-sublist-data.json → data/processed/items_master.csv
- `scripts/02_extract_criteria.py` — Run criteria extraction → data/processed/items_criteria.csv
- `scripts/03_ingest_external.py` — Fetch DSA, MSRP, DMPG → data/raw/
- `scripts/04_amalgamate.py` — Produce data/processed/amalgamated_prices.csv
- `scripts/05_rule_formula.py` — Apply rule formula → data/processed/items_priced.csv
- `scripts/06_ml_refine.py` — Refine coefficients → data/processed/items_ml_priced.csv
- `scripts/07_validate.py` — Anomaly detection → output/anomaly_report.md
- `scripts/08_generate_output.py` — Excel + CSV → output/

**tests/**
- `tests/test_utils.py`
- `tests/test_criteria_extractor.py`
- `tests/test_pricing_engine.py`
- `tests/test_amalgamator.py`

**Other**
- `requirements.txt`
- `CRITERIA.md` — Variable documentation

---

## Task 0: Environment Setup

**Files:**
- Create: `requirements.txt`
- Create: `src/__init__.py`, `tests/__init__.py`
- Create: `data/raw/.gitkeep`, `data/processed/.gitkeep`, `output/.gitkeep`

- [ ] **Step 1: Write requirements.txt**

```
pandas>=2.0.0
openpyxl>=3.1.0
rapidfuzz>=3.0.0
scikit-learn>=1.3.0
xgboost>=2.0.0
pdfplumber>=0.10.0
requests>=2.31.0
spacy>=3.7.0
pytest>=7.4.0
```

- [ ] **Step 2: Create directory structure and package init files**

```bash
mkdir -p src tests data/raw data/processed output
touch src/__init__.py tests/__init__.py data/raw/.gitkeep data/processed/.gitkeep output/.gitkeep
```

- [ ] **Step 3: Install dependencies**

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Expected: All packages install without error. `python -c "import pandas, openpyxl, rapidfuzz, sklearn, xgboost, pdfplumber, spacy"` produces no output.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt src/__init__.py tests/__init__.py data/raw/.gitkeep data/processed/.gitkeep output/.gitkeep
git commit -m "chore: set up project structure and requirements"
```

---

## Task 1: Shared Utilities

**Files:**
- Create: `src/utils.py`
- Create: `tests/test_utils.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_utils.py
import pytest
from src.utils import normalize_item_name, parse_value_cp, get_5etools_url


def test_normalize_item_name_lowercase():
    assert normalize_item_name("Sword of FIRE") == "sword of fire"


def test_normalize_item_name_strips_plus():
    assert normalize_item_name("+1 Longsword") == "longsword +1"


def test_normalize_item_name_strips_punctuation():
    assert normalize_item_name("Bag of Holding (Type I)") == "bag of holding type i"


def test_parse_value_cp_converts_to_gp():
    # value field is in copper pieces; 100 cp = 1 gp
    assert parse_value_cp(5000) == 50.0


def test_parse_value_cp_none_returns_none():
    assert parse_value_cp(None) is None


def test_parse_value_cp_zero_returns_none():
    assert parse_value_cp(0) is None


def test_get_5etools_url_basic():
    url = get_5etools_url("Longsword", "PHB")
    assert url == "https://5e.tools/items.html#longsword_phb"


def test_get_5etools_url_spaces():
    url = get_5etools_url("Bag of Holding", "DMG")
    assert url == "https://5e.tools/items.html#bag%20of%20holding_dmg"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_utils.py -v
```

Expected: ImportError or similar — `src/utils.py` does not exist yet.

- [ ] **Step 3: Implement `src/utils.py`**

```python
# src/utils.py
import re
from typing import Optional
from urllib.parse import quote


def normalize_item_name(name: str) -> str:
    """Normalize item name for fuzzy matching: lowercase, move leading +N to suffix."""
    name = name.strip()
    # Move leading "+N " to end: "+1 Longsword" → "longsword +1"
    leading_plus = re.match(r'^(\+\d+)\s+(.+)$', name)
    if leading_plus:
        bonus, rest = leading_plus.groups()
        name = f"{rest} {bonus}"
    # Lowercase, remove parenthetical content, strip extra punctuation
    name = name.lower()
    name = re.sub(r'\(.*?\)', '', name)
    name = re.sub(r"[',]", '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def parse_value_cp(value: Optional[int]) -> Optional[float]:
    """Convert value field (copper pieces) to gold pieces. Returns None if zero or null."""
    if value is None or value == 0:
        return None
    return value / 100.0


def get_5etools_url(item_name: str, source: str) -> str:
    """Build a 5e.tools item URL from item name and source code."""
    name_part = item_name.lower().replace(' ', '%20')
    source_part = source.lower()
    return f"https://5e.tools/items.html#{name_part}_{source_part}"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_utils.py -v
```

Expected: All 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/utils.py tests/test_utils.py
git commit -m "feat: add shared utilities (normalize, parse_value, url builder)"
```

---

## Task 2: Phase 1 — Item Extraction

**Files:**
- Create: `scripts/01_extract_items.py`

Input: `items-sublist-data.json` (9,422 items)  
Output: `data/processed/items_master.csv`

Columns: `name`, `source`, `page`, `rarity`, `type`, `official_price_gp`, `req_attune`, `url`, `raw_json` (full item as JSON string for later phases)

- [ ] **Step 1: Examine the JSON structure**

```bash
python3 -c "
import json
with open('items-sublist-data.json') as f:
    data = json.load(f)
# Print top-level keys
print(type(data), list(data.keys()) if isinstance(data, dict) else 'list of items')
print('First item keys:', list(data[0].keys()) if isinstance(data, list) else list(data[list(data.keys())[0]][0].keys()))
"
```

Expected: Understand whether items are a top-level list or under a key (likely `item`).

- [ ] **Step 2: Write `scripts/01_extract_items.py`**

```python
#!/usr/bin/env python3
"""Phase 1: Parse items-sublist-data.json into items_master.csv"""

import json
import csv
import sys
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils import parse_value_cp, get_5etools_url

INPUT_JSON = Path("items-sublist-data.json")
OUTPUT_CSV = Path("data/processed/items_master.csv")

RARITY_NORMALIZE = {
    "none": "mundane",
    "": "mundane",
    "unknown": "unknown",
    "unknown (magic)": "unknown_magic",
    "varies": "varies",
    "common": "common",
    "uncommon": "uncommon",
    "rare": "rare",
    "very rare": "very_rare",
    "legendary": "legendary",
    "artifact": "artifact",
}


def extract_items(data: list) -> list[dict]:
    rows = []
    for item in data:
        name = item.get("name", "")
        source = item.get("source", "")
        page = item.get("page", "")
        
        # Rarity normalization
        rarity_raw = item.get("rarity", "none") or "none"
        if isinstance(rarity_raw, str):
            rarity = RARITY_NORMALIZE.get(rarity_raw.lower(), rarity_raw.lower())
        else:
            rarity = "unknown"
        
        item_type = item.get("type", "")
        
        # Official price from value field (in cp)
        official_price = parse_value_cp(item.get("value"))
        
        # Attunement
        req_attune_raw = item.get("reqAttune", False)
        if req_attune_raw is True:
            req_attune = "yes"
        elif isinstance(req_attune_raw, str):
            req_attune = f"yes ({req_attune_raw})"
        else:
            req_attune = "no"
        
        url = get_5etools_url(name, source)
        
        rows.append({
            "name": name,
            "source": source,
            "page": page,
            "rarity": rarity,
            "type": item_type,
            "official_price_gp": official_price if official_price else "",
            "req_attune": req_attune,
            "url": url,
            "raw_json": json.dumps(item, ensure_ascii=False),
        })
    return rows


def main():
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    
    with open(INPUT_JSON, encoding="utf-8") as f:
        raw = json.load(f)
    
    # Handle both list and dict-wrapped formats
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict):
        # Try common keys: 'item', 'items', first key
        for key in ("item", "items"):
            if key in raw:
                items = raw[key]
                break
        else:
            items = list(raw.values())[0]
    else:
        raise ValueError(f"Unexpected JSON root type: {type(raw)}")
    
    print(f"Loaded {len(items)} items from {INPUT_JSON}")
    
    rows = extract_items(items)
    
    fieldnames = ["name", "source", "page", "rarity", "type", "official_price_gp", "req_attune", "url", "raw_json"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")
    
    # Summary stats
    from collections import Counter
    rarity_counts = Counter(r["rarity"] for r in rows)
    print("\nRarity distribution:")
    for rarity, count in sorted(rarity_counts.items(), key=lambda x: -x[1]):
        print(f"  {rarity}: {count}")
    
    priced = sum(1 for r in rows if r["official_price_gp"])
    print(f"\nItems with official prices: {priced}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the script**

```bash
python scripts/01_extract_items.py
```

Expected output: ~9,422 items loaded, rarity distribution printed, `data/processed/items_master.csv` created.

- [ ] **Step 4: Verify CSV looks correct**

```bash
python3 -c "
import pandas as pd
df = pd.read_csv('data/processed/items_master.csv')
print(df.shape)
print(df.head(3).to_string())
print('\nNull counts:')
print(df.isnull().sum())
"
```

Expected: Shape `(9422, 9)`, sample rows look reasonable, `name` column has no nulls.

- [ ] **Step 5: Commit**

```bash
git add scripts/01_extract_items.py data/processed/items_master.csv
git commit -m "feat: phase 1 - extract 9422 items from JSON to master CSV"
```

---

## Task 3: Phase 2a — Structured Criteria Extraction

**Files:**
- Create: `src/criteria_extractor.py`
- Create: `tests/test_criteria_extractor.py`

- [ ] **Step 1: Write the failing tests**

```python
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


def test_tattoo():
    item = make_item(tattoo=True)
    c = extract_structured_criteria(item)
    assert c["is_tattoo"] is True
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_criteria_extractor.py -v
```

Expected: ImportError — `src/criteria_extractor.py` does not exist.

- [ ] **Step 3: Implement `src/criteria_extractor.py` (structured section)**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_criteria_extractor.py -v
```

Expected: All 14 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/criteria_extractor.py tests/test_criteria_extractor.py
git commit -m "feat: add structured criteria extractor with tests"
```

---

## Task 4: Phase 2b — NLP Prose Criteria Extraction

**Files:**
- Modify: `src/criteria_extractor.py` — add `extract_prose_criteria()`
- Modify: `tests/test_criteria_extractor.py` — add NLP tests

- [ ] **Step 1: Add NLP tests to test_criteria_extractor.py**

```python
# Add to tests/test_criteria_extractor.py
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


def test_healing_daily():
    desc = "At dawn, you regain 10 hit points."
    c = extract_prose_criteria(desc)
    assert c["healing_daily_hp"] == 10


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
```

- [ ] **Step 2: Run new tests to verify they fail**

```bash
pytest tests/test_criteria_extractor.py::test_flight_full -v
```

Expected: ImportError on `extract_prose_criteria`.

- [ ] **Step 3: Add `extract_prose_criteria()` to `src/criteria_extractor.py`**

```python
# Add to src/criteria_extractor.py (after extract_structured_criteria)

import re


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

    # Flight detection
    has_flying = "flying speed" in desc or "fly speed" in desc
    if has_flying:
        limited_keywords = ["minute", "hour", "until you land", "limited", "short rest", "long rest",
                            "until you attack", "concentration", "action to end", "up to"]
        is_limited = any(k in desc for k in limited_keywords)
        if is_limited:
            c["flight_limited"] = True
        else:
            c["flight_full"] = True

    # Darkvision
    dv_match = re.search(r'darkvision.{0,30}(\d+)\s*feet', desc)
    if dv_match:
        c["darkvision_feet"] = int(dv_match.group(1))

    # Truesight / blindsight / tremorsense
    c["truesight"] = "truesight" in desc
    c["blindsight"] = "blindsight" in desc
    c["tremorsense"] = "tremorsense" in desc

    # Teleportation
    c["teleportation"] = bool(re.search(r'\bteleport\b', desc))

    # Invisibility (at-will, not spell-based)
    if re.search(r'\binvisible\b', desc) and re.search(r'\b(action|bonus action)\b', desc):
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
```

- [ ] **Step 4: Run all tests**

```bash
pytest tests/test_criteria_extractor.py -v
```

Expected: All tests PASS (14 structured + 11 NLP = 25 total).

- [ ] **Step 5: Commit**

```bash
git add src/criteria_extractor.py tests/test_criteria_extractor.py
git commit -m "feat: add NLP prose criteria extractor with tests"
```

---

## Task 5: Phase 2 Script — Run Criteria Extraction

**Files:**
- Create: `scripts/02_extract_criteria.py`

- [ ] **Step 1: Write `scripts/02_extract_criteria.py`**

```python
#!/usr/bin/env python3
"""Phase 2: Extract criteria for all 9422 items → items_criteria.csv"""

import json
import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.criteria_extractor import extract_structured_criteria, extract_prose_criteria

INPUT_CSV = Path("data/processed/items_master.csv")
OUTPUT_CSV = Path("data/processed/items_criteria.csv")


def main():
    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} items from {INPUT_CSV}")

    rows = []
    for _, row in df.iterrows():
        try:
            item = json.loads(row["raw_json"])
        except (json.JSONDecodeError, KeyError):
            item = {}

        struct = extract_structured_criteria(item)

        # Get prose descriptions from items-sublist.md (if matched)
        # For now use empty string — prose matching added in Task 6
        prose = extract_prose_criteria("")

        combined = {
            "name": row["name"],
            "source": row["source"],
            "rarity": row["rarity"],
            "type": row["type"],
            "official_price_gp": row["official_price_gp"],
            "req_attune": row["req_attune"],
            "url": row["url"],
        }
        combined.update(struct)
        combined.update(prose)
        rows.append(combined)

    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Wrote {len(out_df)} rows with {len(out_df.columns)} columns to {OUTPUT_CSV}")

    # Quick stats
    print(f"\nItems with weapon_bonus: {out_df['weapon_bonus'].notna().sum()}")
    print(f"Items with ac_bonus: {out_df['ac_bonus'].notna().sum()}")
    print(f"Items with spell_scroll_level: {out_df['spell_scroll_level'].notna().sum()}")
    print(f"Items with attached_spells (non-empty): {(out_df['attached_spells'].astype(str) != '[]').sum()}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the script**

```bash
python scripts/02_extract_criteria.py
```

Expected: `data/processed/items_criteria.csv` created with 9,422 rows. Counts for weapon_bonus, ac_bonus, spell_scroll_level should be ~3420, reasonable count, ~985 respectively.

- [ ] **Step 3: Commit**

```bash
git add scripts/02_extract_criteria.py data/processed/items_criteria.csv
git commit -m "feat: phase 2 - extract criteria for all 9422 items"
```

---

## Task 6: Phase 2c — Prose Matching from items-sublist.md

**Files:**
- Modify: `scripts/02_extract_criteria.py` — integrate prose lookup
- Create: `src/prose_loader.py` — parse markdown descriptions

- [ ] **Step 1: Write `src/prose_loader.py`**

```python
# src/prose_loader.py
"""Parse items-sublist.md to extract prose descriptions by item name."""

import re
from pathlib import Path
from typing import Optional


def load_prose_descriptions(md_path: Path) -> dict[str, str]:
    """
    Parse items-sublist.md and return a dict of {item_name_lower: description}.
    
    The markdown format is:
    ## Item Name
    *Source, page N*
    
    Description text...
    """
    text = md_path.read_text(encoding="utf-8")
    descriptions = {}

    # Split on h2 headers
    sections = re.split(r'^## (.+)$', text, flags=re.MULTILINE)
    
    # sections[0] = preamble, then alternating: name, content
    for i in range(1, len(sections), 2):
        name = sections[i].strip()
        content = sections[i + 1].strip() if i + 1 < len(sections) else ""
        # Remove the source/page italics line at the top
        content = re.sub(r'^\*.*?\*\s*', '', content, count=1).strip()
        descriptions[name.lower()] = content

    return descriptions
```

- [ ] **Step 2: Update `scripts/02_extract_criteria.py` to use prose**

Replace the prose extraction section in `main()`:

```python
# At the top of main(), load prose descriptions
from src.prose_loader import load_prose_descriptions
MD_PATH = Path("items-sublist.md")
if MD_PATH.exists():
    prose_map = load_prose_descriptions(MD_PATH)
    print(f"Loaded {len(prose_map)} prose descriptions from {MD_PATH}")
else:
    prose_map = {}
    print("Warning: items-sublist.md not found, skipping prose extraction")

# Then in the loop, replace:
#   prose = extract_prose_criteria("")
# with:
item_name_lower = row["name"].lower()
prose_text = prose_map.get(item_name_lower, "")
prose = extract_prose_criteria(prose_text)
```

- [ ] **Step 3: Re-run the criteria extraction**

```bash
python scripts/02_extract_criteria.py
```

Expected: Prose descriptions loaded, `flight_full`/`flight_limited`/`teleportation` counts increase from 0.

- [ ] **Step 4: Commit**

```bash
git add src/prose_loader.py scripts/02_extract_criteria.py data/processed/items_criteria.csv
git commit -m "feat: integrate prose descriptions into criteria extraction"
```

---

## Task 7: Phase 3 — Ingest External Price Guides

**Files:**
- Create: `scripts/03_ingest_external.py`

This script ingests three sources: DSA (Google Sheets CSV export), MSRP (Google Sheets CSV export), and DMPG (PDF).

- [ ] **Step 1: Write `scripts/03_ingest_external.py`**

```python
#!/usr/bin/env python3
"""Phase 3: Ingest DSA, MSRP, DMPG price guides → data/raw/ CSVs"""

import re
import sys
import requests
import pandas as pd
import pdfplumber
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils import normalize_item_name

# Google Sheets export URLs (CSV format)
DSA_URL = "https://docs.google.com/spreadsheets/d/1xckMUATltAexbI6H5JVd1sFagaxjto78wV1alj3WUwE/export?format=csv&gid=0"
MSRP_URL = "https://docs.google.com/spreadsheets/d/11-45kA6qWTFV_rDYkD49B_EQfF0kPrW2tXwQcNs1jVM/export?format=csv"
DMPG_PDF = Path.home() / "Downloads" / "DMPG.pdf"

OUT_DIR = Path("data/raw")


def fetch_dsa() -> pd.DataFrame:
    """Fetch DSA guide. Expects columns: item name, price (gp)."""
    print("Fetching DSA...")
    resp = requests.get(DSA_URL, timeout=30)
    resp.raise_for_status()
    
    from io import StringIO
    df = pd.read_csv(StringIO(resp.text), header=0)
    print(f"  DSA raw columns: {list(df.columns)}")
    print(f"  DSA shape: {df.shape}")
    
    # Find name and price columns — inspect and adapt
    # Common patterns: first col = name, second = price
    name_col = df.columns[0]
    price_col = df.columns[1] if len(df.columns) > 1 else None
    
    df = df.rename(columns={name_col: "item_name", price_col: "price_gp"})
    df = df[["item_name", "price_gp"]].dropna()
    df["item_name"] = df["item_name"].astype(str)
    df["price_gp"] = pd.to_numeric(df["price_gp"].astype(str).str.replace(r'[,gG pP]', '', regex=True), errors="coerce")
    df = df.dropna(subset=["price_gp"])
    df["normalized_name"] = df["item_name"].apply(normalize_item_name)
    df["source"] = "DSA"
    return df


def fetch_msrp() -> pd.DataFrame:
    """Fetch MSRP guide. Average low magic and high magic columns."""
    print("Fetching MSRP...")
    resp = requests.get(MSRP_URL, timeout=30)
    resp.raise_for_status()
    
    from io import StringIO
    df = pd.read_csv(StringIO(resp.text), header=0)
    print(f"  MSRP raw columns: {list(df.columns)}")
    print(f"  MSRP shape: {df.shape}")
    
    # Identify name, low magic, high magic columns
    name_col = df.columns[0]
    # Look for columns containing "low" and "high" (case-insensitive)
    low_col = next((c for c in df.columns if "low" in c.lower()), df.columns[1] if len(df.columns) > 1 else None)
    high_col = next((c for c in df.columns if "high" in c.lower()), df.columns[2] if len(df.columns) > 2 else None)
    
    df["item_name"] = df[name_col].astype(str)
    
    def clean_price(col):
        return pd.to_numeric(df[col].astype(str).str.replace(r'[,gG pP]', '', regex=True), errors="coerce")
    
    df["low_price"] = clean_price(low_col)
    df["high_price"] = clean_price(high_col)
    df["price_gp"] = (df["low_price"] + df["high_price"]) / 2
    
    df = df[["item_name", "price_gp"]].dropna(subset=["price_gp"])
    df["normalized_name"] = df["item_name"].apply(normalize_item_name)
    df["source"] = "MSRP"
    return df


def parse_dmpg() -> pd.DataFrame:
    """Parse DMPG PDF to extract item name and price."""
    print(f"Parsing DMPG from {DMPG_PDF}...")
    if not DMPG_PDF.exists():
        print(f"  WARNING: DMPG.pdf not found at {DMPG_PDF}")
        return pd.DataFrame(columns=["item_name", "price_gp", "normalized_name", "source"])
    
    rows = []
    with pdfplumber.open(DMPG_PDF) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if row and len(row) >= 2:
                        name = str(row[0] or "").strip()
                        price_str = str(row[1] or "").strip()
                        price_str = re.sub(r'[,gG pP\s]', '', price_str)
                        try:
                            price = float(price_str)
                            if price > 0 and name:
                                rows.append({"item_name": name, "price_gp": price})
                        except ValueError:
                            pass
    
    if not rows:
        # Fallback: extract text-based price patterns
        with pdfplumber.open(DMPG_PDF) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                for line in text.split('\n'):
                    m = re.match(r'^(.+?)\s+(\d[\d,]+)\s*gp?', line, re.IGNORECASE)
                    if m:
                        name = m.group(1).strip()
                        price = float(m.group(2).replace(',', ''))
                        rows.append({"item_name": name, "price_gp": price})
    
    df = pd.DataFrame(rows)
    if len(df) > 0:
        df["normalized_name"] = df["item_name"].apply(normalize_item_name)
        df["source"] = "DMPG"
    print(f"  DMPG: extracted {len(df)} items")
    return df


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    dsa = fetch_dsa()
    dsa.to_csv(OUT_DIR / "dsa_prices.csv", index=False)
    print(f"  Saved {len(dsa)} DSA items to data/raw/dsa_prices.csv")
    
    msrp = fetch_msrp()
    msrp.to_csv(OUT_DIR / "msrp_prices.csv", index=False)
    print(f"  Saved {len(msrp)} MSRP items to data/raw/msrp_prices.csv")
    
    dmpg = parse_dmpg()
    dmpg.to_csv(OUT_DIR / "dmpg_prices.csv", index=False)
    print(f"  Saved {len(dmpg)} DMPG items to data/raw/dmpg_prices.csv")
    
    print(f"\nTotal external prices: DSA={len(dsa)}, MSRP={len(msrp)}, DMPG={len(dmpg)}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the ingestion script**

```bash
python scripts/03_ingest_external.py
```

Expected: Three CSVs created in `data/raw/`. DSA ~469 items, MSRP ~557 items, DMPG ~477 items. If counts differ significantly, inspect the raw columns printed and adjust column detection logic.

- [ ] **Step 3: Verify raw files**

```bash
python3 -c "
import pandas as pd
for f in ['data/raw/dsa_prices.csv', 'data/raw/msrp_prices.csv', 'data/raw/dmpg_prices.csv']:
    df = pd.read_csv(f)
    print(f'{f}: {len(df)} items, price range: {df[\"price_gp\"].min():.0f} - {df[\"price_gp\"].max():.0f} gp')
    print(df.head(3).to_string(), '\n')
"
```

Expected: All three files present with reasonable price ranges.

- [ ] **Step 4: Commit**

```bash
git add scripts/03_ingest_external.py data/raw/dsa_prices.csv data/raw/msrp_prices.csv data/raw/dmpg_prices.csv
git commit -m "feat: phase 3 - ingest DSA, MSRP, DMPG price guides"
```

---

## Task 8: Fuzzy Matcher + Amalgamator

**Files:**
- Create: `src/amalgamator.py`
- Create: `tests/test_amalgamator.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_amalgamator.py
import pytest
import pandas as pd
from src.amalgamator import trim_outliers, calculate_weights, fuzzy_match_items


def test_trim_outliers_removes_top_and_bottom_2pct():
    prices = list(range(1, 101))  # 100 items, 1..100
    df = pd.DataFrame({"price_gp": prices})
    trimmed = trim_outliers(df, "price_gp", pct=0.02)
    # 2% of 100 = 2 items from each end (prices 1,2 and 99,100 removed)
    assert trimmed["price_gp"].min() >= 3
    assert trimmed["price_gp"].max() <= 98
    assert len(trimmed) == 96


def test_trim_outliers_small_df():
    """Should not error on tiny dataframes."""
    df = pd.DataFrame({"price_gp": [100, 200, 300]})
    trimmed = trim_outliers(df, "price_gp", pct=0.02)
    assert len(trimmed) > 0


def test_calculate_weights_all_close():
    """All three guides within 25% → equal weights."""
    prices = {"DSA": 1000.0, "MSRP": 1050.0, "DMPG": 1020.0}
    weights = calculate_weights(prices)
    assert abs(weights["DSA"] - 1/3) < 0.01
    assert abs(weights["MSRP"] - 1/3) < 0.01
    assert abs(weights["DMPG"] - 1/3) < 0.01


def test_calculate_weights_two_aligned():
    """DSA and MSRP within 25%, DMPG is outlier → DMPG weight = 0.20."""
    prices = {"DSA": 1000.0, "MSRP": 1050.0, "DMPG": 5000.0}
    weights = calculate_weights(prices)
    assert weights["DMPG"] == pytest.approx(0.20, abs=0.01)
    assert weights["DSA"] == pytest.approx(0.40, abs=0.01)
    assert weights["MSRP"] == pytest.approx(0.40, abs=0.01)


def test_calculate_weights_all_diverge():
    """All diverge → 40% DSA, 30% MSRP, 30% DMPG."""
    prices = {"DSA": 1000.0, "MSRP": 5000.0, "DMPG": 20000.0}
    weights = calculate_weights(prices)
    assert weights["DSA"] == pytest.approx(0.40, abs=0.01)
    assert weights["MSRP"] == pytest.approx(0.30, abs=0.01)
    assert weights["DMPG"] == pytest.approx(0.30, abs=0.01)


def test_fuzzy_match_exact():
    items = ["Bag of Holding", "Cloak of Elvenkind"]
    candidates = ["bag of holding", "cloak of elvenkind", "boots of speed"]
    matches = fuzzy_match_items("Bag of Holding", candidates, threshold=85)
    assert "bag of holding" in matches


def test_fuzzy_match_no_match():
    matches = fuzzy_match_items("Vorpal Sword", ["boots of speed", "ring of protection"], threshold=85)
    assert len(matches) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_amalgamator.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `src/amalgamator.py`**

```python
# src/amalgamator.py
"""Fuzzy matching, outlier trimming, and weighted amalgamation."""

import pandas as pd
from rapidfuzz import fuzz, process
from typing import Optional


def trim_outliers(df: pd.DataFrame, price_col: str, pct: float = 0.02) -> pd.DataFrame:
    """Remove the top pct and bottom pct of items by price."""
    if len(df) < 10:
        return df
    n_trim = max(1, int(len(df) * pct))
    sorted_df = df.sort_values(price_col)
    return sorted_df.iloc[n_trim:-n_trim].reset_index(drop=True)


def calculate_weights(prices: dict[str, float]) -> dict[str, float]:
    """
    Given prices from up to 3 sources {DSA, MSRP, DMPG},
    return weights summing to 1.0 based on alignment.
    """
    sources = [k for k in ("DSA", "MSRP", "DMPG") if k in prices]
    n = len(sources)

    if n == 1:
        return {sources[0]: 1.0}

    if n == 2:
        return {s: 0.5 for s in sources}

    # n == 3: check pairwise alignment (within 25% of each other)
    vals = {s: prices[s] for s in sources}
    median_price = sorted(vals.values())[1]

    def within_25(a, b):
        if a == 0 or b == 0:
            return False
        ratio = max(a, b) / min(a, b)
        return ratio <= 1.25

    aligned = {s: within_25(vals[s], median_price) for s in sources}

    if all(aligned.values()):
        # All three within 25% of median
        return {s: 1/3 for s in sources}

    # Find which pairs are aligned
    dsa_msrp = within_25(vals["DSA"], vals["MSRP"])
    dsa_dmpg = within_25(vals["DSA"], vals["DMPG"])
    msrp_dmpg = within_25(vals["MSRP"], vals["DMPG"])

    if dsa_msrp and not msrp_dmpg and not dsa_dmpg:
        return {"DSA": 0.40, "MSRP": 0.40, "DMPG": 0.20}
    if dsa_dmpg and not dsa_msrp and not msrp_dmpg:
        return {"DSA": 0.40, "MSRP": 0.20, "DMPG": 0.40}
    if msrp_dmpg and not dsa_msrp and not dsa_dmpg:
        return {"DSA": 0.20, "MSRP": 0.40, "DMPG": 0.40}

    # All diverge
    return {"DSA": 0.40, "MSRP": 0.30, "DMPG": 0.30}


def fuzzy_match_items(
    query: str,
    candidates: list[str],
    threshold: int = 85,
) -> list[str]:
    """Return candidates that fuzzy-match query above threshold."""
    results = process.extract(query.lower(), candidates, scorer=fuzz.token_sort_ratio, limit=5)
    return [r[0] for r in results if r[1] >= threshold]


def amalgamate_prices(
    items_df: pd.DataFrame,
    dsa_df: pd.DataFrame,
    msrp_df: pd.DataFrame,
    dmpg_df: pd.DataFrame,
    threshold: int = 85,
) -> pd.DataFrame:
    """
    Match items to each guide and compute weighted amalgamated price.
    
    Returns items_df with added columns:
      dsa_price, msrp_price, dmpg_price, amalgamated_price, price_sources, price_confidence
    """
    # Trim outliers from each guide
    dsa_trimmed = trim_outliers(dsa_df.copy(), "price_gp")
    msrp_trimmed = trim_outliers(msrp_df.copy(), "price_gp") if len(msrp_df) > 0 else msrp_df
    dmpg_trimmed = trim_outliers(dmpg_df.copy(), "price_gp") if len(dmpg_df) > 0 else dmpg_df

    # Build lookup dicts: normalized_name → price_gp
    dsa_lookup = dict(zip(dsa_trimmed["normalized_name"], dsa_trimmed["price_gp"]))
    msrp_lookup = dict(zip(msrp_trimmed["normalized_name"], msrp_trimmed["price_gp"])) if len(msrp_trimmed) > 0 else {}
    dmpg_lookup = dict(zip(dmpg_trimmed["normalized_name"], dmpg_trimmed["price_gp"])) if len(dmpg_trimmed) > 0 else {}

    dsa_names = list(dsa_lookup.keys())
    msrp_names = list(msrp_lookup.keys())
    dmpg_names = list(dmpg_lookup.keys())

    results = []
    for _, row in items_df.iterrows():
        norm_name = row.get("normalized_name", row["name"].lower())

        # Match in each guide
        prices = {}
        for lookup, names, source in [
            (dsa_lookup, dsa_names, "DSA"),
            (msrp_lookup, msrp_names, "MSRP"),
            (dmpg_lookup, dmpg_names, "DMPG"),
        ]:
            if not names:
                continue
            matches = fuzzy_match_items(norm_name, names, threshold)
            if matches:
                prices[source] = lookup[matches[0]]

        if prices:
            weights = calculate_weights(prices)
            amalgamated = sum(prices[s] * weights[s] for s in prices)
            sources_str = ",".join(prices.keys())
            confidence = "multi" if len(prices) > 1 else "solo"
        else:
            amalgamated = None
            sources_str = ""
            confidence = "none"

        results.append({
            **row.to_dict(),
            "dsa_price": prices.get("DSA"),
            "msrp_price": prices.get("MSRP"),
            "dmpg_price": prices.get("DMPG"),
            "amalgamated_price": amalgamated,
            "price_sources": sources_str,
            "price_confidence": confidence,
        })

    return pd.DataFrame(results)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_amalgamator.py -v
```

Expected: All 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/amalgamator.py tests/test_amalgamator.py
git commit -m "feat: add fuzzy matcher, outlier trimmer, and amalgamator with tests"
```

---

## Task 9: Phase 4 Script — Amalgamation

**Files:**
- Create: `scripts/04_amalgamate.py`

- [ ] **Step 1: Write `scripts/04_amalgamate.py`**

```python
#!/usr/bin/env python3
"""Phase 4: Amalgamate external price guides → amalgamated_prices.csv"""

import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.amalgamator import amalgamate_prices
from src.utils import normalize_item_name

ITEMS_CSV = Path("data/processed/items_criteria.csv")
DSA_CSV = Path("data/raw/dsa_prices.csv")
MSRP_CSV = Path("data/raw/msrp_prices.csv")
DMPG_CSV = Path("data/raw/dmpg_prices.csv")
OUTPUT_CSV = Path("data/processed/amalgamated_prices.csv")


def main():
    items = pd.read_csv(ITEMS_CSV)
    items["normalized_name"] = items["name"].apply(normalize_item_name)

    dsa = pd.read_csv(DSA_CSV) if DSA_CSV.exists() else pd.DataFrame()
    msrp = pd.read_csv(MSRP_CSV) if MSRP_CSV.exists() else pd.DataFrame()
    dmpg = pd.read_csv(DMPG_CSV) if DMPG_CSV.exists() else pd.DataFrame()

    print(f"Matching {len(items)} items against {len(dsa)} DSA, {len(msrp)} MSRP, {len(dmpg)} DMPG prices...")

    result = amalgamate_prices(items, dsa, msrp, dmpg)
    result.to_csv(OUTPUT_CSV, index=False)

    matched = result["amalgamated_price"].notna().sum()
    multi = (result["price_confidence"] == "multi").sum()
    solo = (result["price_confidence"] == "solo").sum()
    print(f"\nResults: {matched} items matched ({multi} multi-source, {solo} solo-source)")
    print(f"Unmatched: {len(result) - matched} items (will use rule formula only)")

    # Coverage by rarity
    print("\nMatch rate by rarity:")
    for rarity, group in result.groupby("rarity"):
        matched_count = group["amalgamated_price"].notna().sum()
        print(f"  {rarity}: {matched_count}/{len(group)} ({100*matched_count/len(group):.1f}%)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run amalgamation**

```bash
python scripts/04_amalgamate.py
```

Expected: Several hundred items matched across guides. Match rates will vary by rarity; some rarities may have < 50% coverage (expected).

- [ ] **Step 3: Commit**

```bash
git add scripts/04_amalgamate.py data/processed/amalgamated_prices.csv
git commit -m "feat: phase 4 - amalgamate external price guides"
```

---

## Task 10: Pricing Engine

**Files:**
- Create: `src/pricing_engine.py`
- Create: `tests/test_pricing_engine.py`

The engine implements the formula from the spec exactly:  
`price = max(floor, (base_rarity + sum(additive_bonuses)) × attunement × consumable × material × curse × sentient)`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_pricing_engine.py
import pytest
from src.pricing_engine import calculate_price, RARITY_BASE_PRICES, RARITY_FLOORS


def make_criteria(rarity="rare", **kwargs):
    """Build minimal criteria dict for testing."""
    defaults = {
        "rarity": rarity,
        "req_attune": "none",
        "req_attune_class": None,
        "item_type_code": "",
        "is_ammunition": False,
        "spell_scroll_level": None,
        "weapon_bonus": None,
        "weapon_attack_bonus": None,
        "weapon_damage_bonus": None,
        "ac_bonus": None,
        "saving_throw_bonus": None,
        "ability_check_bonus": None,
        "proficiency_bonus_mod": None,
        "spell_attack_bonus": None,
        "spell_save_dc_bonus": None,
        "spell_damage_bonus": None,
        "damage_resistances": [],
        "damage_immunities": [],
        "condition_immunities": [],
        "speed_mods": {},
        "is_sentient": False,
        "is_cursed": False,
        "is_tattoo": False,
        "is_wondrous": False,
        "is_shield": False,
        "is_poison": False,
        "is_firearm": False,
        "attached_spells": [],
        "charges": None,
        "recharge": None,
        "stealth_penalty": False,
        "ability_score_mods": [],
        "official_price_gp": None,
        # NLP fields
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
        "stealth_advantage": False,
        "swim_speed": False,
        "climb_speed": False,
        "burrow_speed": False,
    }
    defaults.update(kwargs)
    return defaults


def test_base_rare_price():
    """Plain rare item with no bonuses."""
    c = make_criteria(rarity="rare")
    price = calculate_price(c)
    assert price == 20000


def test_rare_with_attunement():
    """Rare item with open attunement: 20000 * 0.85 = 17000."""
    c = make_criteria(rarity="rare", req_attune="open")
    price = calculate_price(c)
    assert price == pytest.approx(17000, rel=0.01)


def test_rare_with_class_attunement():
    """Rare item with class-restricted attunement: 20000 * 0.75 = 15000."""
    c = make_criteria(rarity="rare", req_attune="class")
    price = calculate_price(c)
    assert price == pytest.approx(15000, rel=0.01)


def test_weapon_bonus_plus1():
    """Rare weapon +1 bonus: 20000 + 10000 = 30000."""
    c = make_criteria(rarity="rare", weapon_bonus=1)
    price = calculate_price(c)
    assert price == pytest.approx(30000, rel=0.01)


def test_weapon_bonus_plus3():
    """Rare weapon +3 bonus: 20000 + 200000 = 220000."""
    c = make_criteria(rarity="rare", weapon_bonus=3)
    price = calculate_price(c)
    assert price == pytest.approx(220000, rel=0.01)


def test_ac_bonus_plus2():
    """Rare armor +2 AC: 20000 + 40000 = 60000."""
    c = make_criteria(rarity="rare", ac_bonus=2)
    price = calculate_price(c)
    assert price == pytest.approx(60000, rel=0.01)


def test_cursed_item():
    """Cursed rare item: 20000 * 0.70 = 14000."""
    c = make_criteria(rarity="rare", is_cursed=True)
    price = calculate_price(c)
    assert price == pytest.approx(14000, rel=0.01)


def test_sentient_item():
    """Sentient rare item: 20000 * 1.25 = 25000."""
    c = make_criteria(rarity="rare", is_sentient=True)
    price = calculate_price(c)
    assert price == pytest.approx(25000, rel=0.01)


def test_spell_scroll_level_3():
    """Level 3 scroll = 300 gp."""
    c = make_criteria(rarity="uncommon", spell_scroll_level=3)
    price = calculate_price(c)
    assert price == pytest.approx(300, rel=0.01)


def test_floor_applied():
    """Cursed common item should not go below floor (50 gp)."""
    c = make_criteria(rarity="common", is_cursed=True)
    price = calculate_price(c)
    assert price >= RARITY_FLOORS["common"]


def test_official_price_used_directly():
    """Items with official prices bypass formula."""
    c = make_criteria(rarity="mundane", official_price_gp=15.0)
    price = calculate_price(c)
    assert price == 15.0


def test_flight_full_bonus():
    """Flight adds 15000 gp."""
    c = make_criteria(rarity="rare", flight_full=True)
    price = calculate_price(c)
    assert price == pytest.approx(35000, rel=0.01)  # 20000 + 15000


def test_teleportation_bonus():
    """Teleportation adds 20000 gp."""
    c = make_criteria(rarity="very_rare", teleportation=True)
    price = calculate_price(c)
    assert price == pytest.approx(120000, rel=0.01)  # 100000 + 20000


def test_damage_resistance():
    """Each resistance adds 2000 gp."""
    c = make_criteria(rarity="rare", damage_resistances=["fire", "cold"])
    price = calculate_price(c)
    assert price == pytest.approx(24000, rel=0.01)  # 20000 + 4000
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_pricing_engine.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `src/pricing_engine.py`**

```python
# src/pricing_engine.py
"""Rule-based pricing engine implementing the formula from the spec."""

from typing import Optional

RARITY_BASE_PRICES = {
    "mundane": 1,
    "common": 500,
    "uncommon": 2500,
    "rare": 20000,
    "very_rare": 100000,
    "legendary": 500000,
    "artifact": 1500000,
    "unknown_magic": 5000,   # fallback estimate
    "unknown": 1,
    "varies": 5000,          # fallback estimate
}

RARITY_FLOORS = {
    "mundane": 1,
    "common": 50,
    "uncommon": 100,
    "rare": 500,
    "very_rare": 5000,
    "legendary": 50000,
    "artifact": 500000,
    "unknown_magic": 50,
    "unknown": 1,
    "varies": 50,
}

SPELL_SCROLL_PRICES = {
    0: 25, 1: 75, 2: 150, 3: 300, 4: 1500,
    5: 3000, 6: 8500, 7: 20000, 8: 45000, 9: 100000,
}

WEAPON_BONUS_ADDITIVE = {1: 10000, 2: 50000, 3: 200000}
AC_BONUS_ADDITIVE = {1: 15000, 2: 40000, 3: 150000}
SPELL_ATTACK_ADDITIVE = {1: 8000, 2: 25000, 3: 80000}

CONDITION_IMMUNITY_VALUES = {
    "frightened": 2000, "charmed": 3000, "poisoned": 2500, "exhaustion": 5000,
    "petrified": 3000, "paralyzed": 4000, "blinded": 4000, "deafened": 1000,
    "stunned": 4000, "incapacitated": 6000, "prone": 1500, "restrained": 3000,
}


def calculate_price(criteria: dict) -> float:
    """Calculate item price based on criteria dict. Returns price in gold pieces."""

    rarity = criteria.get("rarity", "unknown")
    official_price = criteria.get("official_price_gp")

    # Official prices used directly for mundane items
    if official_price and rarity in ("mundane", "none"):
        return float(official_price)

    # Spell scrolls: use level price directly (skip other formula)
    scroll_level = criteria.get("spell_scroll_level")
    if scroll_level is not None:
        return float(SPELL_SCROLL_PRICES.get(int(scroll_level), 75))

    base = float(RARITY_BASE_PRICES.get(rarity, 5000))

    # --- Additive bonuses ---
    additive = 0.0

    # Weapon bonus (use the highest of weapon/attack/damage bonus)
    weapon_bonus = max(
        criteria.get("weapon_bonus") or 0,
        criteria.get("weapon_attack_bonus") or 0,
        criteria.get("weapon_damage_bonus") or 0,
    )
    if weapon_bonus > 0:
        additive += WEAPON_BONUS_ADDITIVE.get(min(weapon_bonus, 3), 200000)

    # AC bonus
    ac_bonus = criteria.get("ac_bonus") or 0
    if ac_bonus > 0:
        additive += AC_BONUS_ADDITIVE.get(min(ac_bonus, 3), 150000)

    # Spell attack / save DC bonus (take higher)
    spell_bonus = max(
        criteria.get("spell_attack_bonus") or 0,
        criteria.get("spell_save_dc_bonus") or 0,
    )
    if spell_bonus > 0:
        additive += SPELL_ATTACK_ADDITIVE.get(min(spell_bonus, 3), 80000)

    # Saving throw bonus
    save_bonus = criteria.get("saving_throw_bonus") or 0
    if save_bonus > 0:
        additive += 3000 * save_bonus

    # Ability check bonus
    check_bonus = criteria.get("ability_check_bonus") or 0
    if check_bonus > 0:
        additive += 1000 * check_bonus

    # Proficiency bonus
    prof_bonus = criteria.get("proficiency_bonus_mod") or 0
    if prof_bonus > 0:
        additive += 5000 * prof_bonus

    # Resistances
    resistances = criteria.get("damage_resistances") or []
    if isinstance(resistances, str):
        resistances = [resistances] if resistances else []
    additive += 2000 * len(resistances)

    # Immunities
    immunities = criteria.get("damage_immunities") or []
    if isinstance(immunities, str):
        immunities = [immunities] if immunities else []
    additive += 5000 * len(immunities)

    # Condition immunities
    cond_immune = criteria.get("condition_immunities") or []
    if isinstance(cond_immune, str):
        cond_immune = [cond_immune] if cond_immune else []
    for cond in cond_immune:
        additive += CONDITION_IMMUNITY_VALUES.get(str(cond).lower(), 2000)

    # Movement
    if criteria.get("flight_full"):
        additive += 15000
    elif criteria.get("flight_limited"):
        additive += 5000
    if criteria.get("swim_speed"):
        additive += 2000
    if criteria.get("climb_speed"):
        additive += 2000
    if criteria.get("burrow_speed"):
        additive += 3000

    # Vision
    darkvision_ft = criteria.get("darkvision_feet") or 0
    if darkvision_ft > 0:
        additive += min(200 * (darkvision_ft // 30), 800)
    if criteria.get("truesight"):
        additive += 15000
    if criteria.get("blindsight"):
        additive += 5000
    if criteria.get("tremorsense"):
        additive += 3000

    # Utility
    if criteria.get("stealth_advantage"):
        additive += 2000
    if criteria.get("crit_immunity"):
        additive += 10000
    if criteria.get("teleportation"):
        additive += 20000
    if criteria.get("concentration_free"):
        additive += 3000
    if criteria.get("invisibility_atwill"):
        additive += 25000

    # Healing
    healing_daily = criteria.get("healing_daily_hp") or 0
    if healing_daily > 0:
        additive += 150 * healing_daily
    healing_consumable = criteria.get("healing_consumable_avg") or 0.0
    if healing_consumable > 0:
        additive += 50 * healing_consumable

    # Tome / manual permanent boost
    if criteria.get("tome_manual_boost"):
        additive += 100000  # midpoint of 50k-200k range

    # Wish effect
    if criteria.get("wish_effect"):
        additive += 500000

    # --- Multiplicative modifiers ---
    attune_mod = 1.0
    req_attune = criteria.get("req_attune", "none")
    if req_attune == "open":
        attune_mod = 0.85
    elif req_attune == "class":
        attune_mod = 0.75

    consumable_mod = 1.0
    is_ammo = criteria.get("is_ammunition", False)
    if is_ammo:
        consumable_mod = 0.05

    material_mod = 1.0  # mithral/adamantine detection is prose-based, handled in NLP

    curse_mod = 0.70 if criteria.get("is_cursed") else 1.0
    sentient_mod = 1.25 if criteria.get("is_sentient") else 1.0

    price = (base + additive) * attune_mod * consumable_mod * material_mod * curse_mod * sentient_mod

    floor = RARITY_FLOORS.get(rarity, 1)
    return max(floor, price)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_pricing_engine.py -v
```

Expected: All 15 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/pricing_engine.py tests/test_pricing_engine.py
git commit -m "feat: add rule-based pricing engine with tests"
```

---

## Task 11: Phase 5 Script — Apply Rule Formula

**Files:**
- Create: `scripts/05_rule_formula.py`

- [ ] **Step 1: Write `scripts/05_rule_formula.py`**

```python
#!/usr/bin/env python3
"""Phase 5: Apply rule-based formula to all items → items_priced.csv"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.pricing_engine import calculate_price

INPUT_CSV = Path("data/processed/amalgamated_prices.csv")
OUTPUT_CSV = Path("data/processed/items_priced.csv")


def main():
    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} items")

    prices = []
    for _, row in df.iterrows():
        # Build criteria dict from CSV row
        c = row.to_dict()
        # Parse list fields that were stored as strings
        for list_col in ["damage_resistances", "damage_immunities", "condition_immunities",
                         "attached_spells", "weapon_properties", "ability_score_mods"]:
            val = c.get(list_col, "[]")
            if isinstance(val, str):
                try:
                    c[list_col] = json.loads(val.replace("'", '"')) if val and val != "nan" else []
                except (json.JSONDecodeError, ValueError):
                    c[list_col] = []
        # Parse boolean fields
        for bool_col in ["is_sentient", "is_cursed", "is_tattoo", "is_wondrous", "is_ammunition",
                         "is_shield", "flight_full", "flight_limited", "truesight", "blindsight",
                         "tremorsense", "teleportation", "invisibility_atwill", "tome_manual_boost",
                         "concentration_free", "crit_immunity", "wish_effect", "stealth_advantage",
                         "swim_speed", "climb_speed", "burrow_speed", "stealth_penalty"]:
            c[bool_col] = bool(c.get(bool_col))

        # Determine price source
        if pd.notna(c.get("official_price_gp")) and c.get("rarity") in ("mundane", "none"):
            price = float(c["official_price_gp"])
            price_source = "official"
        elif pd.notna(c.get("amalgamated_price")):
            price = calculate_price(c)
            price_source = "rule+amalgamated"
        else:
            price = calculate_price(c)
            price_source = "rule"

        prices.append({**c, "rule_price": price, "price_source": price_source})

    out = pd.DataFrame(prices)

    # Calculate R² against amalgamated prices
    matched = out[out["amalgamated_price"].notna() & out["rule_price"].notna()].copy()
    if len(matched) > 10:
        ss_res = ((matched["rule_price"] - matched["amalgamated_price"]) ** 2).sum()
        ss_tot = ((matched["amalgamated_price"] - matched["amalgamated_price"].mean()) ** 2).sum()
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        print(f"\nR² against amalgamated prices: {r2:.4f} (on {len(matched)} matched items)")
        print(f"Target: ≥ 0.80")

    out.to_csv(OUTPUT_CSV, index=False)
    print(f"\nWrote {len(out)} rows to {OUTPUT_CSV}")

    # Price distribution by rarity
    print("\nMedian prices by rarity:")
    for rarity, group in out.groupby("rarity"):
        median = group["rule_price"].median()
        print(f"  {rarity}: {median:,.0f} gp (n={len(group)})")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the script**

```bash
python scripts/05_rule_formula.py
```

Expected: R² printed (initial value likely 0.50–0.75 before ML refinement). Median prices by rarity printed.

- [ ] **Step 3: Commit**

```bash
git add scripts/05_rule_formula.py data/processed/items_priced.csv
git commit -m "feat: phase 5 - apply rule-based formula to all 9422 items"
```

---

## Task 12: Checkpoint 1 — Oracle Review

**Beads task:** pricing_guide_v2-bxh

- [ ] **Step 1: Mark checkpoint in beads**

```bash
bd update pricing_guide_v2-bxh --claim
```

- [ ] **Step 2: Gather metrics for oracle review**

```bash
python3 -c "
import pandas as pd, numpy as np
df = pd.read_csv('data/processed/items_priced.csv')
matched = df[df['amalgamated_price'].notna() & df['rule_price'].notna()]
ss_res = ((matched['rule_price'] - matched['amalgamated_price'])**2).sum()
ss_tot = ((matched['amalgamated_price'] - matched['amalgamated_price'].mean())**2).sum()
r2 = 1 - ss_res/ss_tot
print(f'R²={r2:.4f}, n_matched={len(matched)}')
for rarity, g in df.groupby('rarity'):
    print(f'{rarity}: median={g[\"rule_price\"].median():.0f} gp, n={len(g)}')
"
```

- [ ] **Step 3: Review formula logic via @oracle**

Present to oracle: R² value, median prices by rarity, any items with prices > 3× their rarity median. Ask oracle to validate:
1. Does +3 weapon price ($220,000) conflict with Very Rare base ($100,000)?
2. Are any additive bonuses producing counterintuitive results?
3. Are the base prices aligned with community expectations?

- [ ] **Step 4: Apply any formula corrections**

Based on oracle feedback, edit `src/pricing_engine.py` constants and re-run `scripts/05_rule_formula.py`. Commit any changes.

- [ ] **Step 5: Close checkpoint**

```bash
bd close pricing_guide_v2-bxh --reason "Oracle review complete, formula validated"
```

---

## Task 13: Phase 6 — ML Coefficient Refinement

**Files:**
- Create: `scripts/06_ml_refine.py`

- [ ] **Step 1: Write `scripts/06_ml_refine.py`**

```python
#!/usr/bin/env python3
"""Phase 6: ML coefficient refinement using Ridge regression."""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).parent.parent))

INPUT_CSV = Path("data/processed/items_priced.csv")
OUTPUT_CSV = Path("data/processed/items_ml_priced.csv")

# Features for ML: these are the additive criteria values
FEATURE_COLS = [
    "weapon_bonus", "ac_bonus", "spell_attack_bonus", "spell_save_dc_bonus",
    "saving_throw_bonus", "ability_check_bonus", "proficiency_bonus_mod",
    "spell_damage_bonus",
    "flight_full", "flight_limited", "truesight", "blindsight", "tremorsense",
    "teleportation", "invisibility_atwill", "concentration_free", "crit_immunity",
    "stealth_advantage", "swim_speed", "climb_speed", "burrow_speed",
    "healing_daily_hp", "healing_consumable_avg", "tome_manual_boost",
    "is_sentient", "is_cursed",
    "darkvision_feet",
]

RARITY_DUMMIES = ["common", "uncommon", "rare", "very_rare", "legendary", "artifact"]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build ML feature matrix from criteria columns."""
    X = pd.DataFrame()

    for col in FEATURE_COLS:
        if col in df.columns:
            X[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            X[col] = 0.0

    # One-hot rarity
    for r in RARITY_DUMMIES:
        X[f"rarity_{r}"] = (df["rarity"] == r).astype(float)

    # Attunement
    X["attune_open"] = (df["req_attune"] == "open").astype(float)
    X["attune_class"] = (df["req_attune"] == "class").astype(float)

    return X


def main():
    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} items")

    # Only train on items with amalgamated ground truth
    train_mask = df["amalgamated_price"].notna()
    train_df = df[train_mask].copy()
    print(f"Training set: {len(train_df)} items with amalgamated prices")

    X = build_features(train_df)
    y = np.log1p(train_df["amalgamated_price"].values)  # log-transform for normality

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)

    model = Ridge(alpha=1.0)
    model.fit(X_train_s, y_train)

    y_pred_val = model.predict(X_val_s)
    r2_val = r2_score(y_val, y_pred_val)
    print(f"\nValidation R² (log-space): {r2_val:.4f}")

    # Show top feature importances
    feature_importance = pd.Series(np.abs(model.coef_), index=X.columns)
    print("\nTop 10 feature importances:")
    print(feature_importance.nlargest(10).to_string())

    # Apply ML model to all items
    X_all = build_features(df)
    X_all_s = scaler.transform(X_all)
    ml_prices = np.expm1(model.predict(X_all_s))
    ml_prices = np.maximum(ml_prices, 1)  # No negative prices

    df["ml_price"] = ml_prices

    # Blend: rule price gets 40% weight, ML gets 60% for matched items
    # For unmatched items, use rule price directly
    def blend_price(row):
        if pd.notna(row["amalgamated_price"]):
            # Has ground truth: blend rule and ML
            return 0.4 * row["rule_price"] + 0.6 * row["ml_price"]
        else:
            # No ground truth: ML is more reliable than rule alone
            return 0.5 * row["rule_price"] + 0.5 * row["ml_price"]

    df["final_price"] = df.apply(blend_price, axis=1)

    # Calculate final R² against amalgamated
    matched = df[df["amalgamated_price"].notna()].copy()
    r2_final = r2_score(
        np.log1p(matched["amalgamated_price"]),
        np.log1p(matched["final_price"])
    )
    print(f"\nFinal blended R² (log-space): {r2_final:.4f}")
    print(f"Target: ≥ 0.80")

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nWrote {len(df)} rows to {OUTPUT_CSV}")

    print("\nMedian final prices by rarity:")
    for rarity, group in df.groupby("rarity"):
        median = group["final_price"].median()
        print(f"  {rarity}: {median:,.0f} gp (n={len(group)})")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run ML refinement**

```bash
python scripts/06_ml_refine.py
```

Expected: Validation R² > 0.70. Final blended R² > 0.75. If R² < 0.70, inspect feature importances for counterintuitive signs.

- [ ] **Step 3: Verify coefficient signs are sensible**

```bash
python3 -c "
# Re-run and check that these features have POSITIVE coefficients:
# weapon_bonus, ac_bonus, truesight, flight_full, teleportation, crit_immunity
# And these have NEGATIVE coefficients:
# is_cursed
# (is_sentient should be positive)
print('Check coefficient signs in the feature importance output above.')
"
```

- [ ] **Step 4: Commit**

```bash
git add scripts/06_ml_refine.py data/processed/items_ml_priced.csv
git commit -m "feat: phase 6 - ML coefficient refinement (Ridge regression)"
```

---

## Task 14: Checkpoint 2 — Oracle Review

**Beads task:** pricing_guide_v2-42z

- [ ] **Step 1: Claim task**

```bash
bd update pricing_guide_v2-42z --claim
```

- [ ] **Step 2: Prepare ML review summary**

Gather: final R², coefficient signs, validation R², feature importances, sample of 20 well-known items with their prices. Present to @oracle for review.

- [ ] **Step 3: Apply corrections if needed**

If oracle flags counterintuitive coefficients or poor R², adjust blending ratio or add/remove features. Re-run `scripts/06_ml_refine.py`.

- [ ] **Step 4: Close task**

```bash
bd close pricing_guide_v2-42z --reason "ML review complete"
```

---

## Task 15: Anomaly Detector + Phase 7

**Files:**
- Create: `src/anomaly_detector.py`
- Create: `scripts/07_validate.py`

- [ ] **Step 1: Write `src/anomaly_detector.py`**

```python
# src/anomaly_detector.py
"""Anomaly detection for priced item dataset."""

import pandas as pd
import numpy as np
from typing import Optional


def detect_anomalies(
    df: pd.DataFrame,
    price_col: str = "final_price",
    rarity_col: str = "rarity",
) -> dict:
    """
    Detect pricing anomalies using IQR method per rarity tier.
    
    Returns dict with:
      - overall_stats: dict of overall metrics
      - by_rarity: dict of per-rarity stats
      - outliers: DataFrame of outlier items
      - extreme_outliers: DataFrame of items > 3× rarity median
    """
    results = {
        "overall_stats": {},
        "by_rarity": {},
        "outliers": pd.DataFrame(),
        "extreme_outliers": pd.DataFrame(),
    }

    prices = df[price_col].dropna()
    results["overall_stats"] = {
        "count": len(prices),
        "median": prices.median(),
        "mean": prices.mean(),
        "std": prices.std(),
        "min": prices.min(),
        "max": prices.max(),
        "cv": prices.std() / prices.mean() if prices.mean() > 0 else None,
        "skewness": prices.skew(),
    }

    all_outliers = []
    all_extreme = []

    for rarity, group in df.groupby(rarity_col):
        gprices = group[price_col].dropna()
        if len(gprices) < 4:
            continue

        q1 = gprices.quantile(0.25)
        q3 = gprices.quantile(0.75)
        iqr = q3 - q1
        median = gprices.median()

        # Handle zero-width IQR (very common in common/uncommon tiers)
        if iqr == 0:
            # Fall back to 50% deviation from median
            lower = median * 0.5
            upper = median * 1.5
        else:
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

        outlier_mask = (group[price_col] < lower) | (group[price_col] > upper)
        extreme_mask = (group[price_col] > 3 * median) | (group[price_col] < median / 3)

        n_outliers = outlier_mask.sum()
        outlier_rate = n_outliers / len(group)

        results["by_rarity"][rarity] = {
            "count": len(group),
            "median": median,
            "mean": gprices.mean(),
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "lower_fence": lower,
            "upper_fence": upper,
            "n_outliers": n_outliers,
            "outlier_rate": outlier_rate,
            "zero_width_iqr": iqr == 0,
        }

        all_outliers.append(group[outlier_mask])
        all_extreme.append(group[extreme_mask])

    if all_outliers:
        results["outliers"] = pd.concat(all_outliers, ignore_index=True)
    if all_extreme:
        results["extreme_outliers"] = pd.concat(all_extreme, ignore_index=True)

    return results


def format_anomaly_report(results: dict, price_col: str = "final_price") -> str:
    """Format anomaly detection results as a markdown report."""
    lines = ["# Anomaly Detection Report\n"]

    stats = results["overall_stats"]
    lines.append("## Overall Statistics\n")
    lines.append(f"- Total items: {stats['count']:,}")
    lines.append(f"- Median price: {stats['median']:,.0f} gp")
    lines.append(f"- Mean price: {stats['mean']:,.0f} gp")
    lines.append(f"- Std dev: {stats['std']:,.0f} gp")
    lines.append(f"- CV: {stats['cv']:.2f}" if stats['cv'] else "- CV: N/A")
    lines.append(f"- Skewness: {stats['skewness']:.2f}")
    lines.append(f"- Price range: {stats['min']:,.0f} – {stats['max']:,.0f} gp\n")

    lines.append("## Outliers by Rarity\n")
    lines.append("| Rarity | Count | Median | IQR Width | Outliers | Outlier Rate |")
    lines.append("|--------|-------|--------|-----------|----------|--------------|")
    for rarity, s in sorted(results["by_rarity"].items()):
        flag = "⚠️ zero-width IQR" if s["zero_width_iqr"] else ""
        lines.append(
            f"| {rarity} | {s['count']} | {s['median']:,.0f} gp | "
            f"{s['iqr']:,.0f} | {s['n_outliers']} | {s['outlier_rate']:.1%} {flag} |"
        )

    lines.append(f"\n## Extreme Outliers (> 3× rarity median)\n")
    extreme = results["extreme_outliers"]
    lines.append(f"Total: {len(extreme)} items\n")
    if len(extreme) > 0:
        lines.append("| Name | Source | Rarity | Price | Rarity Median |")
        lines.append("|------|--------|--------|-------|---------------|")
        for _, row in extreme.head(50).iterrows():
            lines.append(
                f"| {row.get('name','')} | {row.get('source','')} | "
                f"{row.get('rarity','')} | {row.get(price_col, 0):,.0f} gp | - |"
            )

    return "\n".join(lines)
```

- [ ] **Step 2: Write `scripts/07_validate.py`**

```python
#!/usr/bin/env python3
"""Phase 7: Validation and anomaly detection → output/anomaly_report.md"""

import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.anomaly_detector import detect_anomalies, format_anomaly_report

INPUT_CSV = Path("data/processed/items_ml_priced.csv")
OUTPUT_REPORT = Path("output/anomaly_report.md")
OUTPUT_VALIDATED_CSV = Path("data/processed/items_validated.csv")


def main():
    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} items")

    # Cross-check official prices vs algorithm
    official = df[df["official_price_gp"].notna() & (df["rarity"] == "mundane")].copy()
    print(f"\nOfficial-priced mundane items: {len(official)}")

    # Run anomaly detection
    results = detect_anomalies(df, price_col="final_price")

    report = format_anomaly_report(results)
    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.write_text(report, encoding="utf-8")
    print(f"\nAnomaly report written to {OUTPUT_REPORT}")

    # Print summary to console
    print("\n=== RARITY OUTLIER RATES ===")
    for rarity, s in sorted(results["by_rarity"].items()):
        status = "🔴" if s["outlier_rate"] > 0.15 else "🟡" if s["outlier_rate"] > 0.10 else "🟢"
        print(f"{status} {rarity}: {s['outlier_rate']:.1%} ({s['n_outliers']}/{s['count']})")

    # Save validated CSV (same as input, with anomaly flags)
    df["is_outlier"] = False
    for idx in results["outliers"].index:
        if idx < len(df):
            df.loc[idx, "is_outlier"] = True
    df["is_extreme_outlier"] = False
    for idx in results["extreme_outliers"].index:
        if idx < len(df):
            df.loc[idx, "is_extreme_outlier"] = True

    df.to_csv(OUTPUT_VALIDATED_CSV, index=False)
    print(f"\nValidated data written to {OUTPUT_VALIDATED_CSV}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run validation**

```bash
python scripts/07_validate.py
```

Expected: Anomaly report generated at `output/anomaly_report.md`. Target: Common/Uncommon outlier rates < 15% (improvement over prior 30%/37%).

- [ ] **Step 4: Commit**

```bash
git add src/anomaly_detector.py scripts/07_validate.py output/anomaly_report.md data/processed/items_validated.csv
git commit -m "feat: phase 7 - anomaly detection and validation report"
```

---

## Task 16: Phase 8 — Excel + CSV Output

**Files:**
- Create: `scripts/08_generate_output.py`

- [ ] **Step 1: Write `scripts/08_generate_output.py`**

```python
#!/usr/bin/env python3
"""Phase 8: Generate Excel (with hyperlinks) and CSV output."""

import sys
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

INPUT_CSV = Path("data/processed/items_validated.csv")
OUTPUT_XLSX = Path("output/pricing_guide.xlsx")
OUTPUT_CSV = Path("output/pricing_guide.csv")

# Rarity colors (background fill)
RARITY_COLORS = {
    "mundane":      "F5F5F5",  # Light gray
    "common":       "FFFFFF",  # White
    "uncommon":     "1EFF00",  # Green (per 5e.tools)
    "rare":         "0070DD",  # Blue
    "very_rare":    "A335EE",  # Purple
    "legendary":    "FF8000",  # Orange
    "artifact":     "E6CC80",  # Gold
    "unknown_magic":"DDDDDD",  # Medium gray
    "unknown":      "EEEEEE",  # Light gray
    "varies":       "BBBBBB",  # Gray
}

RARITY_TEXT_COLORS = {
    "uncommon":    "000000",
    "rare":        "FFFFFF",
    "very_rare":   "FFFFFF",
    "legendary":   "000000",
    "artifact":    "000000",
}


def format_price(price_gp: float) -> str:
    """Format price as gp string."""
    if price_gp < 1:
        cp = int(price_gp * 100)
        return f"{cp} cp"
    elif price_gp < 10:
        return f"{price_gp:.1f} gp"
    else:
        return f"{int(price_gp):,} gp"


def determine_price_source_label(row) -> str:
    if row.get("price_source") == "official":
        return "Official"
    elif row.get("price_confidence") == "multi":
        return f"Amalgamated ({row.get('price_sources','')})"
    elif row.get("price_confidence") == "solo":
        return f"Single source ({row.get('price_sources','')})"
    else:
        return "Algorithm"


def main():
    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} items")

    # Build output rows
    output_rows = []
    for _, row in df.iterrows():
        price = row.get("final_price", row.get("rule_price", 0))
        output_rows.append({
            "Name": row["name"],
            "Source": row["source"],
            "Type": row.get("type", ""),
            "Rarity": row["rarity"].replace("_", " ").title(),
            "Attunement": row.get("req_attune", "none").replace("none", "No"),
            "Price (gp)": round(float(price), 2) if pd.notna(price) else 0,
            "Price Formatted": format_price(float(price)) if pd.notna(price) else "0 gp",
            "Price Source": determine_price_source_label(row.to_dict()),
            "URL": row.get("url", ""),
            "Is Outlier": row.get("is_outlier", False),
        })

    out_df = pd.DataFrame(output_rows)

    # Save CSV
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    csv_df = out_df.drop(columns=["URL", "Is Outlier"])
    csv_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved CSV to {OUTPUT_CSV}")

    # Build Excel workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Pricing Guide"

    # Header row
    headers = ["Name", "Source", "Type", "Rarity", "Attunement", "Price (gp)", "Price Source", "Notes"]
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = Font(bold=True, size=11)
        cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
        cell.font = Font(bold=True, color="FFFFFF")
        cell.alignment = Alignment(horizontal="center")

    # Freeze header row
    ws.freeze_panes = "A2"

    # Data rows
    for row_idx, row in enumerate(output_rows, 2):
        rarity_key = row["Rarity"].lower().replace(" ", "_")
        bg_color = RARITY_COLORS.get(rarity_key, "FFFFFF")
        text_color = RARITY_TEXT_COLORS.get(rarity_key, "000000")

        fill = PatternFill(start_color=bg_color, end_color=bg_color, fill_type="solid")
        font_normal = Font(color=text_color, size=10)
        font_link = Font(color="0563C1", underline="single", size=10)

        # Name column with hyperlink
        name_cell = ws.cell(row=row_idx, column=1, value=row["Name"])
        if row["URL"]:
            name_cell.hyperlink = row["URL"]
            name_cell.font = font_link
        else:
            name_cell.font = font_normal
        name_cell.fill = fill

        # Other columns
        values = [row["Source"], row["Type"], row["Rarity"], row["Attunement"],
                  row["Price Formatted"], row["Price Source"],
                  "⚠️" if row["Is Outlier"] else ""]
        for col_offset, val in enumerate(values, 2):
            cell = ws.cell(row=row_idx, column=col_offset, value=val)
            cell.font = font_normal
            cell.fill = fill
            cell.alignment = Alignment(horizontal="left")

    # Column widths
    col_widths = [35, 12, 15, 12, 15, 18, 30, 8]
    for col_idx, width in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    # Auto-filter
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"

    wb.save(OUTPUT_XLSX)
    print(f"Saved Excel to {OUTPUT_XLSX}")
    print(f"\nTotal items: {len(output_rows)}")
    print(f"Hyperlinked items: {sum(1 for r in output_rows if r['URL'])}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run output generation**

```bash
python scripts/08_generate_output.py
```

Expected: `output/pricing_guide.xlsx` and `output/pricing_guide.csv` created. Open Excel file to verify hyperlinks, rarity color-coding, and formatting.

- [ ] **Step 3: Spot-check the output**

```bash
python3 -c "
import pandas as pd
df = pd.read_csv('output/pricing_guide.csv')
print(f'Rows: {len(df)}')
print(df[df['Rarity'] == 'Legendary'].sort_values('Price (gp)', ascending=False).head(5).to_string())
print()
print(df[df['Rarity'] == 'Common'].head(5).to_string())
"
```

- [ ] **Step 4: Commit**

```bash
git add scripts/08_generate_output.py output/pricing_guide.xlsx output/pricing_guide.csv
git commit -m "feat: phase 8 - generate Excel and CSV pricing guide output"
```

---

## Task 17: Checkpoint 3 — Final Oracle Review

**Beads task:** pricing_guide_v2-5xg

- [ ] **Step 1: Claim task**

```bash
bd update pricing_guide_v2-5xg --claim
```

- [ ] **Step 2: Prepare final review materials**

Gather and present to @oracle:
- Final R² score
- Outlier rates by rarity tier (from anomaly report)
- Sample of 50 items spanning all rarities
- Any items flagged as ⚠️ outliers
- Overall quality targets met/missed

- [ ] **Step 3: Apply any final corrections**

- [ ] **Step 4: Close all remaining beads tasks**

```bash
bd close pricing_guide_v2-5xg --reason "Final oracle review complete"
bd close pricing_guide_v2-blf --reason "Project structure set up"
# Close all other completed tasks
```

- [ ] **Step 5: Final push**

```bash
git pull --rebase
bd dolt push
git push
git status  # Must show "up to date with origin"
```

---

## Task 18: Write CRITERIA.md Documentation

**Files:**
- Create: `CRITERIA.md`

- [ ] **Step 1: Write CRITERIA.md**

```markdown
# Criteria Variables

This document defines all pricing criteria extracted from item data.

## Structured JSON Criteria

| Variable | Source Field | Type | Description |
|----------|-------------|------|-------------|
| `weapon_bonus` | `bonusWeapon` | int or None | Overall weapon enhancement bonus (+1, +2, +3) |
| `weapon_attack_bonus` | `bonusWeaponAttack` | int or None | Attack-only weapon bonus |
| `weapon_damage_bonus` | `bonusWeaponDamage` | int or None | Damage-only weapon bonus |
| `ac_bonus` | `bonusAc` | int or None | AC enhancement bonus |
| `saving_throw_bonus` | `bonusSavingThrow` | int or None | Saving throw bonus |
| `ability_check_bonus` | `bonusAbilityCheck` | int or None | Ability check bonus |
| `proficiency_bonus_mod` | `bonusProficiencyBonus` | int or None | Proficiency bonus modifier |
| `spell_attack_bonus` | `bonusSpellAttack` | int or None | Spell attack roll bonus |
| `spell_save_dc_bonus` | `bonusSpellSaveDc` | int or None | Spell save DC bonus |
| `spell_damage_bonus` | `bonusSpellDamage` | int or None | Spell damage bonus |
| `damage_resistances` | `resist` | list[str] | Damage types resisted |
| `damage_immunities` | `immune` | list[str] | Damage types immune to |
| `condition_immunities` | `conditionImmune` | list[str] | Conditions immune to |
| `req_attune` | `reqAttune` | "none"/"open"/"class" | Attunement requirement |
| `req_attune_class` | `reqAttune` (string) | str or None | Restricting class if class-attunement |
| `spell_scroll_level` | `spellScrollLevel` | int or None | Scroll spell level (0–9) |
| `attached_spells` | `attachedSpells` | list | Spells granted by item |
| `charges` | `charges` | int or None | Number of charges |
| `recharge` | `recharge` | str or None | Recharge trigger |
| `is_sentient` | `sentient` | bool | Sentient item flag |
| `is_cursed` | `curse` | bool | Cursed item flag |
| `is_tattoo` | `tattoo` | bool | Tattoo item flag |
| `is_wondrous` | `wondrous` | bool | Wondrous item flag |
| `is_ammunition` | type == "A" | bool | Ammunition flag |
| `is_shield` | type == "S" | bool | Shield flag |
| `stealth_penalty` | `stealth` | bool | Stealth disadvantage |
| `strength_req` | `strength` | int or None | Strength requirement |
| `crit_threshold` | `critThreshold` | int or None | Modified crit range |

## NLP Prose Criteria

| Variable | Detection Pattern | Type | Description |
|----------|------------------|------|-------------|
| `flight_full` | "flying speed" + no restriction keywords | bool | Permanent unconditional flight |
| `flight_limited` | "flying speed" + time/condition restriction | bool | Limited/conditional flight |
| `darkvision_feet` | "darkvision" + distance | int | Darkvision range in feet |
| `truesight` | "truesight" | bool | Truesight granted |
| `blindsight` | "blindsight" | bool | Blindsight granted |
| `tremorsense` | "tremorsense" | bool | Tremorsense granted |
| `teleportation` | "teleport" | bool | Teleportation ability |
| `invisibility_atwill` | "invisible" + "action" (non-spell) | bool | At-will invisibility |
| `healing_daily_hp` | daily healing HP amount | int | HP healed per day |
| `healing_consumable_avg` | average HP from dice expr | float | Average consumable HP |
| `tome_manual_boost` | "manual/tome" + "score increases" | bool | Permanent stat boost |
| `concentration_free` | "doesn't require concentration" | bool | No concentration needed |
| `crit_immunity` | "critical hits...normal hit" | bool | Crit immunity |
| `wish_effect` | "wish" | bool | Wish or wish-equivalent |
| `stealth_advantage` | "advantage...stealth" | bool | Stealth advantage |
| `swim_speed` | "swimming speed" | bool | Swimming speed granted |
| `climb_speed` | "climbing speed" | bool | Climbing speed granted |
| `burrow_speed` | "burrowing speed" | bool | Burrowing speed granted |
```

- [ ] **Step 2: Commit**

```bash
git add CRITERIA.md
git commit -m "docs: add CRITERIA.md variable documentation"
```

---

## Task 19: Unit Tests — Remaining Coverage

**Beads tasks:** pricing_guide_v2-c46, pricing_guide_v2-m9i, pricing_guide_v2-x5i

- [ ] **Step 1: Add edge case tests for anomaly detector**

```python
# Add to a new file: tests/test_anomaly_detector.py
import pandas as pd
from src.anomaly_detector import detect_anomalies


def test_detect_returns_outliers():
    df = pd.DataFrame({
        "rarity": ["rare"] * 20,
        "final_price": [20000] * 18 + [500000, 1],  # two outliers
    })
    results = detect_anomalies(df)
    assert results["by_rarity"]["rare"]["n_outliers"] >= 1


def test_zero_width_iqr_handled():
    """Common items all at 500 gp shouldn't crash."""
    df = pd.DataFrame({
        "rarity": ["common"] * 20,
        "final_price": [500.0] * 19 + [50000.0],
    })
    results = detect_anomalies(df)
    assert results["by_rarity"]["common"]["zero_width_iqr"] is True
    assert results["by_rarity"]["common"]["n_outliers"] >= 1


def test_extreme_outliers_flagged():
    df = pd.DataFrame({
        "rarity": ["uncommon"] * 10,
        "final_price": [2500.0] * 9 + [100000.0],
    })
    results = detect_anomalies(df)
    assert len(results["extreme_outliers"]) >= 1
```

- [ ] **Step 2: Run all tests**

```bash
pytest tests/ -v
```

Expected: All tests pass across all modules.

- [ ] **Step 3: Commit**

```bash
git add tests/test_anomaly_detector.py
git commit -m "test: add anomaly detector edge case tests"
```

---

## Quality Targets Summary

| Metric | Target | Check |
|--------|--------|-------|
| Overall R² (log-space) | ≥ 0.80 | `scripts/06_ml_refine.py` output |
| Common outlier rate | < 15% | `output/anomaly_report.md` |
| Uncommon outlier rate | < 15% | `output/anomaly_report.md` |
| Rare outlier rate | < 10% | `output/anomaly_report.md` |
| Very Rare outlier rate | < 15% | `output/anomaly_report.md` |
| Legendary outlier rate | < 15% | `output/anomaly_report.md` |
| Items with price = 0 | 0 | `scripts/07_validate.py` |
| All tests passing | 100% | `pytest tests/ -v` |

---

## Execution Order

Run phases sequentially:

```bash
python scripts/01_extract_items.py    # Phase 1
python scripts/02_extract_criteria.py # Phase 2
python scripts/03_ingest_external.py  # Phase 3
python scripts/04_amalgamate.py       # Phase 4
python scripts/05_rule_formula.py     # Phase 5  → Checkpoint 1
python scripts/06_ml_refine.py        # Phase 6  → Checkpoint 2
python scripts/07_validate.py         # Phase 7
python scripts/08_generate_output.py  # Phase 8  → Checkpoint 3
```
