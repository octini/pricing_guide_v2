#!/usr/bin/env python3
"""Generate HTML interface for the pricing guide.

Usage (from repo root):
    python scripts/11_generate_html.py

Reads:
    output/pricing_guide.csv          pricing pipeline output (11,941 rows)
    items-sublist-data.json           5e.tools metadata (descriptions, links)

Writes:
    index.html                        Mistystep-styled shop page (small shell)
    items-data.js                     item payload as window.MISTYSTEP_ITEMS

The payload lives in items-data.js (loaded via a classic <script src>,
relative path) so the ~5MB data weight stays out of index.html while both
Cloudflare Pages and local file:// open keep working (classic scripts are
not CORS-blocked on file://, unlike fetch).
"""

import json
import csv
import re
import sys
import pandas as pd
from pathlib import Path

# Allow imports from project root when executed as python3 scripts/11_generate_html.py
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.source_names import translate_source

INPUT_CSV = Path('output/pricing_guide.csv')
OUTPUT_HTML = Path('index.html')
ITEMS_JSON = Path('items-sublist-data.json')
ITEMS_JS = Path('items-data.js')

# Item type mapping: 5e.tools code -> common name
TYPE_NAMES = {
    # Standard types
    "M": "Melee Weapon",
    "R": "Ranged Weapon",
    "A": "Ammunition",
    "G": "Adventuring Gear",
    "P": "Potion",
    "S": "Shield",
    "W": "Wondrous Item",
    "OTH": "Other",

    # Armor types
    "MA": "Medium Armor",
    "LA": "Light Armor",
    "HA": "Heavy Armor",

    # Specific item types
    "SCF": "Spellcasting Focus",
    "AT": "Artisan's Tools",
    "INS": "Musical Instrument",
    "T": "Tool",
    "TG": "Trade Goods",
    "FD": "Food & Drink",
    "GS": "Gaming Set",
    "EXP": "Explosive",
    "MNT": "Mount or Vehicle (Land)",

    # Magic item categories
    "RG": "Ring",
    "WD": "Wand",
    "RD": "Rod",
    "SC": "Scroll",

    # Vehicles
    "SHP": "Ship/Vehicle (Water)",
    "VEH": "Vehicle (Land)",
    "AIR": "Vehicle (Air)",

    # Special
    "SPC": "Vehicle (Space)",  # From Astral Adventurer's Guide
    "Dele": "Delerium",  # From Monsters of Drakkenheim
    "EM": "Eldritch Machine",  # From Exploring Eberron
    "TAH": "Tack & Harness",

    # Treasure / currency codes (5e.tools "$" family)
    "$": "Currency",
    "$A": "Art Object",
    "$C": "Currency",
    "$G": "Gemstone",

    # Third-party / variant codes
    "AdvEq": "Adventuring Gear",
    "IDG": "Other",  # Drakkenheim substances; no player-facing category
    "Ingred": "Ingredient",
    "LTG": "Trade Goods",
    "MF": "Ranged Weapon",  # Firearms are ranged weapons
    "TB": "Trade Goods",
}

def translate_type(type_code):
    """Translate 5e.tools type code to common name.

    Type codes are pipe-separated as 'TYPE|SOURCE' (e.g., 'M|XPHB').
    The second part is a sourcebook identifier, not a type — we ignore it.
    The column also carries plain display names (no pipe); those pass through.
    Anything else buckets as Other so a raw system code never reaches the UI.
    """
    if pd.isna(type_code):
        return 'Wondrous Item'
    base_type = str(type_code).split('|')[0].strip()
    if base_type in TYPE_NAMES:
        return TYPE_NAMES[base_type]
    if base_type in _TYPE_DISPLAY:
        return base_type
    return 'Other'


_TYPE_DISPLAY = set(TYPE_NAMES.values())


def format_price(price_gp):
    if price_gp < 1:
        return f"{int(price_gp * 100)} cp"
    elif price_gp < 10:
        return f"{price_gp:.1f} gp"
    else:
        return f"{int(price_gp):,} gp"


def strip_5e_tags(text):
    """Remove 5e.tools {@tag ...} markup, keeping the display text."""
    # {@tag text|extra|extra} -> text
    # {@tag text} -> text
    return re.sub(r'\{@\w+\s+([^|}]+)[^}]*\}', r'\1', str(text))


def extract_description(entries, max_len=400):
    """Extract a short plain-text description from 5e.tools entries."""
    parts = []
    for entry in (entries or []):
        if isinstance(entry, str):
            parts.append(strip_5e_tags(entry))
        elif isinstance(entry, dict) and entry.get('type') == 'entries':
            # Recurse into nested entries
            for sub in entry.get('entries', []):
                if isinstance(sub, str):
                    parts.append(strip_5e_tags(sub))
        if len(' '.join(parts)) >= max_len:
            break
    desc = ' '.join(parts).strip()
    if len(desc) > max_len:
        desc = desc[:max_len].rsplit(' ', 1)[0] + '…'
    return desc


def build_5etools_url(name, source):
    """Build a 5e.tools item URL from name and source."""
    slug = name.lower().replace(' ', '%20')
    src = source.lower() if source else 'dmg'
    return f"https://5e.tools/items.html#{slug}_{src}"


def load_item_metadata():
    """Load descriptions and source info from the 5e.tools JSON."""
    if not ITEMS_JSON.exists():
        print(f"Warning: {ITEMS_JSON} not found, skipping descriptions/links")
        return {}

    data = json.loads(ITEMS_JSON.read_text(encoding='utf-8'))
    lookup = {}
    for item in data:
        name = item.get('name', '')
        source = item.get('source', '')
        desc = extract_description(item.get('entries', []))
        # Also check inherits.entries as fallback
        if not desc and item.get('inherits', {}).get('entries'):
            desc = extract_description(item['inherits']['entries'])
        lookup[name.lower()] = {
            'url': build_5etools_url(name, source),
            'description': desc,
        }
    return lookup


def escape_html_attr(text):
    """Escape text for use in HTML attributes."""
    return text.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')


def main():
    df = pd.read_csv(INPUT_CSV)
    print(f'Loaded {len(df)} items')

    # Load item metadata (descriptions, URLs)
    item_meta = load_item_metadata()
    print(f'Loaded metadata for {len(item_meta)} items from JSON')

    # Translate source and type for the UI
    df['Source Display'] = df['Source'].apply(translate_source)
    df['Type Display'] = df['Type'].apply(translate_type)

    # Build unique filter options
    sources = sorted(df['Source Display'].unique())
    types = sorted(df['Type Display'].unique())

    # Sort rarities in increasing order (not alphabetically)
    RARITY_ORDER = {'Mundane': 0, 'Unknown': 1, 'Unknown Magic': 2, 'Common': 3, 'Uncommon': 4, 'Rare': 5, 'Very Rare': 6, 'Legendary': 7, 'Artifact': 8, 'Varies': 9}
    rarities = sorted(df['Rarity'].unique(), key=lambda r: RARITY_ORDER.get(r, 99))

    # Convert data to JSON
    items_data = []
    linked_count = 0
    for _, row in df.iterrows():
        name = row['Name']
        meta = item_meta.get(name.lower(), {})
        url = meta.get('url', '')
        desc = meta.get('description', '')
        if url:
            linked_count += 1
        # Fallback: use URL from CSV data (which has correct source codes)
        if not url and 'URL' in row.index and pd.notna(row.get('URL')) and str(row['URL']).startswith('http'):
            url = str(row['URL'])
        # Last resort: construct URL from name and source code
        if not url:
            source_code = str(row['Source']).split('|')[0].strip() if pd.notna(row['Source']) else 'dmg'
            url = build_5etools_url(name, source_code)
        items_data.append({
            'name': name,
            'source': row['Source Display'],
            'sourceCode': row['Type'],
            'type': row['Type Display'],
            'typeCode': row['Type'],
            'rarity': row['Rarity'],
            'attunement': row['Attunement'],
            'price': row['Price (gp)'],
            'priceFormatted': row['Price Formatted'],
            'url': url,
            'desc': desc,
        })
    print(f'Linked {linked_count}/{len(df)} items to JSON metadata')

    # Price bounds for the range slider (log scale in the client)
    price_min = float(df['Price (gp)'].min())
    price_max = float(df['Price (gp)'].max())

    # Build filter option markup (escaped)
    def checkbox_options(values, prefix, filter_name):
        out = []
        for i, s in enumerate(values):
            safe = escape_html_attr(str(s))
            out.append(
                f'<label class="checkbox-item"><input type="checkbox" id="{prefix}_{i}"'
                f' value="{safe}" data-filter="{filter_name}"><span>{safe}</span></label>'
            )
        return ''.join(out)

    src_opts = checkbox_options(sources, 'src', 'source')
    type_opts = checkbox_options(types, 'typ', 'type')
    sources_json = json.dumps(sources)
    types_json = json.dumps(types)

    rar_chips = ''.join(
        f'<button type="button" class="chip" data-rarity="{escape_html_attr(str(r))}"'
        f' aria-pressed="false">{escape_html_attr(str(r))}</button>'
        for r in rarities
    )

    # Generate HTML shell — Mistystep Shop System ("The Screen").
    # Item payload is external (items-data.js); this file holds tokens + logic only.
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mistystep &mdash; Magic Item Pricing Guide</title>
    <style>
        :root {{
            --vellum: #f4f1ea;
            --leaf: #ffffff;
            --leaf-deep: #e8e2d4;
            --ink: #161616;
            --faded-ink: #525252;
            --ruled-line: #c6c0b2;
            --coin-edge: #6f6a5e;
            --ember: #9e2b1e;
            --ember-deep: #7c2117;
            --ember-wash: #f9e9e4;
            --witchlight: #0f62fe;
            --blood-mark: #b81922;
            --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif;
            --ledger: ui-monospace, "SF Mono", "Cascadia Code", Menlo, Consolas, "Courier New", monospace;
        }}
        * {{ box-sizing: border-box; }}
        html {{ -webkit-text-size-adjust: 100%; }}
        body {{
            font-family: var(--sans);
            font-size: 16px;
            line-height: 1.5;
            background: var(--vellum);
            color: var(--ink);
            margin: 0;
            padding: 0;
        }}
        :focus-visible {{
            outline: 2px solid var(--witchlight);
            outline-offset: 2px;
        }}
        .container {{ max-width: 1100px; margin: 0 auto; padding: 0 16px 64px; }}

        /* Header bar: leaf over a ruled divider */
        .masthead {{
            background: var(--leaf);
            border-bottom: 1px solid var(--ruled-line);
        }}
        .masthead-inner {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 16px;
            display: flex;
            align-items: baseline;
            gap: 16px;
            flex-wrap: wrap;
        }}
        .wordmark {{
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--faded-ink);
        }}
        h1 {{ font-size: 28px; line-height: 1.2; font-weight: 700; margin: 0; }}
        .subtitle {{ color: var(--faded-ink); margin: 0; font-size: 14px; }}

        /* Spine: sticky filter bar */
        .spine {{
            position: sticky;
            top: 0;
            z-index: 500;
            background: var(--leaf);
            border-bottom: 1px solid var(--ruled-line);
        }}
        .spine-inner {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 12px 16px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .search-row {{ display: flex; gap: 8px; }}
        #search {{
            flex: 1;
            height: 40px;
            padding: 8px 16px;
            font-size: 16px;
            font-family: var(--sans);
            color: var(--ink);
            background: var(--leaf);
            border: 1px solid var(--coin-edge);
            border-radius: 2px;
        }}
        .filter-groups {{ display: none; gap: 12px; flex-wrap: wrap; }}
        .filter-groups.open {{ display: flex; }}
        .filter-group {{ display: flex; flex-direction: column; gap: 4px; min-width: 0; }}
        .filter-group > .group-label {{
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--faded-ink);
        }}
        .chip-row {{ display: flex; gap: 4px; flex-wrap: wrap; }}
        .chip {{
            font-family: var(--sans);
            font-size: 16px;
            color: var(--faded-ink);
            background: var(--leaf);
            border: 1px solid var(--coin-edge);
            border-radius: 2px;
            padding: 4px 16px;
            cursor: pointer;
            min-height: 44px; /* D1: 44px touch target (rarity + attunement chips) */
            display: inline-flex;
            align-items: center;
        }}
        .chip[aria-pressed="true"] {{
            background: var(--ember);
            border-color: var(--ember);
            color: var(--leaf);
            font-weight: 600;
        }}

        /* Dropdowns for long option lists (source, type) */
        .dropdown {{ position: relative; display: inline-block; }}
        .dropdown-btn {{
            font-family: var(--sans);
            font-size: 14px;
            color: var(--ink);
            background: var(--leaf);
            border: 1px solid var(--coin-edge);
            border-radius: 2px;
            padding: 8px 16px;
            min-width: 180px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 8px;
        }}
        .dropdown-btn:hover {{ border-color: var(--ember); }}
        .dropdown-btn .filter-count, .filters-toggle .filter-count {{
            background: var(--ember);
            color: var(--leaf);
            padding: 2px 6px;
            border-radius: 2px;
            font-size: 12px;
            font-weight: 600;
        }}
        .filter-count.quiet {{ background: var(--ruled-line); color: var(--faded-ink); }}

        /* Filters disclosure (all widths): search stays visible, groups collapse behind the toggle */
        .filters-toggle {{
            display: inline-flex;
            font-family: var(--sans);
            font-size: 14px;
            color: var(--ink);
            background: var(--leaf);
            border: 1px solid var(--coin-edge);
            border-radius: 2px;
            padding: 8px 16px;
            cursor: pointer;
            align-items: center;
            gap: 8px;
            align-self: flex-start;
        }}
        @media (max-width: 700px) {{
            .col-source, .col-type, .col-attune {{ display: none; }}
        }}
        .dropdown-content {{
            display: none;
            position: absolute;
            background: var(--leaf);
            min-width: 250px;
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid var(--coin-edge);
            border-radius: 4px;
            z-index: 600;
            margin-top: 4px;
        }}
        .dropdown.open .dropdown-content {{ display: block; }}
        .checkbox-list {{ padding: 8px; }}
        .dropdown-actions {{
            display: flex;
            gap: 8px;
            padding-bottom: 6px;
        }}
        .dropdown-actions .btn-ghost {{
            padding: 4px 12px;
        }}
        .dropdown-search {{
            width: 100%;
            height: 40px;
            padding: 8px 16px;
            margin-bottom: 6px;
            font-size: 14px;
            font-family: var(--sans);
            color: var(--ink);
            background: var(--leaf);
            border: 1px solid var(--coin-edge);
            border-radius: 2px;
        }}
        .checkbox-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 4px 8px;
            cursor: pointer;
            border-radius: 2px;
            font-size: 14px;
        }}
        .checkbox-item:hover {{ background: var(--leaf-deep); }}
        .checkbox-item input {{ accent-color: var(--ember); }}

        /* Price range: log-scale single-track dual-handle slider + numeric fields.
           Two overlapping range inputs share one visible track (.dual-track);
           native tracks are transparent, thumbs take pointer events. */
        .price-controls {{ display: flex; flex-direction: column; gap: 4px; }}
        .price-sliders {{ position: relative; width: 280px; max-width: 100%; height: 44px; }} /* D1: 44px slider touch target; one visible track */
        .dual-track {{
            position: absolute; left: 0; right: 0; top: 50%;
            height: 4px; transform: translateY(-50%);
            background: var(--ruled-line); border-radius: 2px;
        }}
        .dual-fill {{ position: absolute; top: 0; bottom: 0; background: var(--ember); border-radius: 2px; }}
        .price-sliders input[type="range"] {{
            position: absolute; inset: 0; width: 100%; height: 44px; margin: 0;
            background: transparent; pointer-events: none;
            -webkit-appearance: none; appearance: none;
        }}
        .price-sliders input[type="range"]::-webkit-slider-runnable-track {{ background: transparent; height: 44px; }}
        .price-sliders input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none; appearance: none;
            pointer-events: auto; cursor: pointer;
            width: 20px; height: 20px; margin-top: 12px;
            border-radius: 50%; background: var(--leaf);
            border: 2px solid var(--ember);
        }}
        .price-sliders input[type="range"]::-moz-range-track {{ background: transparent; height: 44px; }}
        .price-sliders input[type="range"]::-moz-range-thumb {{
            pointer-events: auto; cursor: pointer;
            width: 16px; height: 16px; border-radius: 50%;
            background: var(--leaf); border: 2px solid var(--ember);
        }}
        .price-sliders input[type="range"]::-moz-range-progress {{ background: transparent; }}
        #price-min-r {{ z-index: 3; }}
        #price-max-r {{ z-index: 4; }}
        .price-numbers {{ display: flex; gap: 8px; align-items: center; }}
        .price-numbers input[type="number"] {{
            width: 110px;
            height: 40px;
            padding: 8px 16px;
            font-family: var(--ledger);
            font-size: 14px;
            color: var(--ink);
            background: var(--leaf);
            border: 1px solid var(--coin-edge);
            border-radius: 2px;
        }}
        .price-readout {{
            font-family: var(--ledger);
            font-size: 14px;
            color: var(--faded-ink);
        }}
        .field-note {{ font-size: 12px; color: var(--faded-ink); }}
        .sr-only {{ position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }}
        #reset-undo[hidden] {{ display: none; }}

        /* Buttons: one flat command key */
        .btn-primary {{
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--leaf);
            background: var(--ember);
            border: 1px solid var(--ember);
            border-radius: 2px;
            padding: 8px 24px;
            cursor: pointer;
            align-self: flex-start;
        }}
        .btn-primary:hover {{ background: var(--ember-deep); border-color: var(--ember-deep); }}
        .btn-primary:disabled {{ background: var(--ruled-line); border-color: var(--ruled-line); color: var(--faded-ink); cursor: not-allowed; }}

        /* Sort control */
        #sort {{
            height: 40px;
            padding: 8px 16px;
            font-size: 14px;
            font-family: var(--sans);
            color: var(--ink);
            background: var(--leaf);
            border: 1px solid var(--coin-edge);
            border-radius: 2px;
        }}

        /* Results */
        .results-info {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 16px;
            flex-wrap: wrap;
            padding: 16px 0 8px;
        }}
        .results-count {{ font-weight: 700; }}
        .results-note {{
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--faded-ink);
        }}
        .panel {{
            background: var(--leaf);
            border: 1px solid var(--ruled-line);
            border-radius: 4px;
            overflow-x: auto;
        }}
        table.results-table {{ width: 100%; border-collapse: collapse; }}
        .results-table th {{
            text-align: left;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--faded-ink);
            border-bottom: 1px solid var(--ruled-line);
            padding: 0;
            white-space: nowrap;
        }}
        .sort-th {{
            font: inherit;
            letter-spacing: inherit;
            text-transform: inherit;
            color: inherit;
            background: none;
            border: 0;
            padding: 8px 16px;
            cursor: pointer;
            white-space: nowrap;
        }}
        th[aria-sort="ascending"] .sort-th::after {{ content: " \\25B2"; }}
        th[aria-sort="descending"] .sort-th::after {{ content: " \\25BC"; }}
        /* Plate measure: every row one invariant 44px measure */
        tr.plate {{ height: 44px; background: var(--leaf); cursor: pointer; }}
        tr.plate:hover {{ background: var(--leaf-deep); }}
        tr.plate.stepped {{ background: var(--ember-wash); font-weight: 600; }}
        .results-table td {{
            padding: 0 16px;
            border-bottom: 1px solid var(--ruled-line);
            vertical-align: middle;
        }}
        .ledger {{
            font-family: var(--ledger);
            font-weight: 700;
            font-size: 16px;
            font-variant-numeric: tabular-nums;
            font-feature-settings: "tnum";
            text-align: right;
            white-space: nowrap;
        }}
        th.col-price {{ text-align: right; }}
        th.col-price .sort-th {{ width: 100%; text-align: right; }}
        .empty-row td {{ padding: 24px 16px; color: var(--faded-ink); cursor: default; }}

        /* Rarity bands: label word always present; pattern + hue are redundant cues */
        .band {{
            display: inline-block;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 4px 8px;
            border-radius: 2px;
            white-space: nowrap;
        }}
        .band-common {{ color: #525252; background-color: #e8e4d8; }}
        .band-uncommon {{
            color: #1e6b34; background-color: #e3ecdf;
            background-image: repeating-linear-gradient(45deg, rgba(30,107,52,0.18) 0 2px, transparent 2px 5px);
        }}
        .band-rare {{
            color: #0b4fa0; background-color: #e0e9f5;
            background-image: repeating-linear-gradient(90deg, rgba(11,79,160,0.20) 0 2px, transparent 2px 6px);
        }}
        .band-very-rare {{
            color: #6b2fa0; background-color: #e9e2f4;
            background-image: radial-gradient(circle, rgba(107,47,160,0.35) 1px, transparent 1.3px);
            background-size: 6px 6px;
        }}
        .band-legendary {{
            color: #7a4a00; background-color: #f3e8cf;
            background-image:
                repeating-linear-gradient(45deg, rgba(122,74,0,0.16) 0 2px, transparent 2px 6px),
                repeating-linear-gradient(-45deg, rgba(122,74,0,0.16) 0 2px, transparent 2px 6px);
        }}
        .band-artifact {{ color: #5c3d00; background-color: #efe3c2; }}
        .band-mundane {{ color: #525252; background-color: #e8e4d8; }}
        .band-unknown {{ color: #525252; background-color: #e4e0d4; }}
        .band-unknown-magic {{ color: #0b4fa0; background-color: #e4e0d4; }}
        .band-varies {{ color: #525252; background-color: #e4e0d4; }}

        /* Pagination */
        .pagination {{ display: flex; justify-content: center; gap: 8px; margin-top: 24px; flex-wrap: wrap; }}
        .pagination button {{
            font-family: var(--sans);
            font-size: 14px;
            min-width: 40px;
            padding: 8px 16px;
            color: var(--ink);
            background: var(--leaf);
            border: 1px solid var(--coin-edge);
            border-radius: 2px;
            cursor: pointer;
        }}
        .pagination button:hover {{ border-color: var(--ember); }}
        .pagination button:disabled {{ color: var(--faded-ink); border-color: var(--ruled-line); background: var(--leaf-deep); cursor: not-allowed; }}
        .pagination button.active {{ background: var(--ember); border-color: var(--ember); color: var(--leaf); font-weight: 700; }}

        /* Detail sheet: the one lifted plane, one committed pull */
        .sheet-backdrop {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(22, 22, 22, 0.4);
            z-index: 800;
        }}
        .sheet-backdrop.open {{ display: block; }}
        .sheet {{
            position: fixed;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 900;
            background: var(--leaf);
            border-top: 2px solid var(--coin-edge);
            transform: translateY(100%);
            transition: transform 0.18s ease-out;
            max-height: 85vh;
            overflow-y: auto;
        }}
        .sheet.open {{ transform: translateY(0); }}
        .sheet-inner {{ max-width: 720px; margin: 0 auto; padding: 8px 16px 32px; }}
        .grab-handle {{
            width: 48px;
            height: 4px;
            border-radius: 2px;
            background: var(--ruled-line);
            margin: 8px auto 16px;
        }}
        .sheet-eyebrow {{ margin-bottom: 8px; }}
        .sheet h2 {{ font-size: 28px; line-height: 1.2; margin: 0 0 8px; }}
        .sheet-price {{
            font-family: var(--ledger);
            font-weight: 700;
            font-size: 16px;
            font-variant-numeric: tabular-nums;
            font-feature-settings: "tnum";
            margin: 0 0 16px;
        }}
        .sheet-facts {{ display: grid; grid-template-columns: auto 1fr; gap: 4px 16px; margin: 0 0 16px; }}
        .sheet-facts dt {{
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--faded-ink);
        }}
        .sheet-facts dd {{ margin: 0; }}
        .sheet-desc {{ max-width: 65ch; margin: 0 0 16px; }}
        .sheet-actions {{ display: flex; gap: 8px; flex-wrap: wrap; }}
        .btn-ghost {{
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--ink);
            background: var(--leaf);
            border: 1px solid var(--coin-edge);
            border-radius: 2px;
            padding: 8px 24px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }}
        .btn-ghost:hover {{ border-color: var(--ember); color: var(--ember); }}

        footer.footer {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 24px 16px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--faded-ink);
        }}
        @media (min-width: 900px) {{
            .sheet {{ left: auto; width: 480px; top: 0; bottom: 0; max-height: none; border-top: 0; border-left: 2px solid var(--coin-edge); transform: translateX(100%); }}
            .sheet.open {{ transform: translateX(0); }}
        }}
    </style>
</head>
<body>
    <header class="masthead">
        <div class="masthead-inner">
            <span class="wordmark">Mistystep</span>
            <h1>Magic Item Pricing Guide</h1>
            <p class="subtitle">{len(df):,} items &middot; prices in gp</p>
        </div>
    </header>

    <div class="spine">
        <div class="spine-inner">
            <div class="search-row">
                <input type="text" id="search" placeholder="Search name, type, source, rules&hellip;" autocomplete="off" aria-label="Search items">
            </div>
            <button class="filters-toggle" id="filters-toggle" type="button" aria-expanded="false" aria-controls="filter-groups"><span id="filters-toggle-label">Show filters</span> <span class="filter-count quiet" id="filters-count">0</span></button>
            <div class="filter-groups" id="filter-groups">
                <div class="filter-group">
                    <span class="group-label" id="rarity-label">Rarity</span>
                    <div class="chip-row" role="group" aria-labelledby="rarity-label">
                        {rar_chips}
                    </div>
                </div>
                <div class="filter-group">
                    <span class="group-label">Sourcebook</span>
                    <div class="dropdown">
                        <button class="dropdown-btn" id="source-btn" type="button" aria-haspopup="true" aria-expanded="false">All <span class="filter-count quiet">0</span></button>
                        <div class="dropdown-content">
                            <div class="checkbox-list">
                                <input type="text" class="dropdown-search" placeholder="Search sources..." data-search="source" aria-label="Search sources">
                                <div class="dropdown-actions">
                                    <button type="button" class="btn-ghost dropdown-select-all" data-target="source">Clear</button>
                                </div>
                                {src_opts}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="filter-group">
                    <span class="group-label">Item Type</span>
                    <div class="dropdown">
                        <button class="dropdown-btn" id="type-btn" type="button" aria-haspopup="true" aria-expanded="false">All <span class="filter-count quiet">0</span></button>
                        <div class="dropdown-content">
                            <div class="checkbox-list">
                                <input type="text" class="dropdown-search" placeholder="Search types..." data-search="type" aria-label="Search types">
                                <div class="dropdown-actions">
                                    <button type="button" class="btn-ghost dropdown-select-all" data-target="type">Clear</button>
                                </div>
                                {type_opts}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="filter-group">
                    <span class="group-label" id="attune-label">Attunement</span>
                    <div class="chip-row" role="group" aria-labelledby="attune-label">
                        <button type="button" class="chip" data-attune="" aria-pressed="true">Any</button>
                        <button type="button" class="chip" data-attune="Yes" aria-pressed="false">Requires attunement</button>
                        <button type="button" class="chip" data-attune="No" aria-pressed="false">No attunement</button>
                    </div>
                </div>
                <div class="filter-group">
                    <span class="group-label" id="price-label">Price range (gp, log scale)</span>
                    <div class="price-controls" role="group" aria-labelledby="price-label">
                        <div class="price-sliders">
                            <div class="dual-track" aria-hidden="true"><div class="dual-fill" id="price-fill"></div></div>
                            <input type="range" id="price-min-r" min="0" max="1000" value="0" aria-label="Minimum price">
                            <input type="range" id="price-max-r" min="0" max="1000" value="1000" aria-label="Maximum price">
                        </div>
                        <div class="price-numbers">
                            <input type="number" id="price-min-n" min="0" aria-label="Minimum price in gp">
                            <span class="field-note">to</span>
                            <input type="number" id="price-max-n" min="0" aria-label="Maximum price in gp">
                        </div>
                        <span class="price-readout" id="price-readout" aria-hidden="true"></span>
                        <span class="sr-only" id="price-status" aria-live="polite"></span>
                    </div>
                </div>
                <div class="filter-group">
                    <span class="group-label">Sort</span>
                    <select id="sort" aria-label="Sort items">
                        <option value="name">Name A&ndash;Z</option>
                        <option value="price">Price low&ndash;high</option>
                        <option value="rarity">Rarity low&ndash;high</option>
                        <option value="source">Source A&ndash;Z</option>
                        <option value="type">Type A&ndash;Z</option>
                        <option value="attunement">Attunement</option>
                    </select>
                </div>
                <div class="filter-group">
                    <span class="group-label">&nbsp;</span>
                    <button class="btn-primary" id="reset-btn" type="button">Reset filters</button>
                     <button class="btn-ghost" id="reset-undo" type="button" hidden>Undo reset</button>
                </div>
            </div>
        </div>
    </div>

    <main class="container">
        <div class="results-info">
            <span class="results-count" id="results-count" role="status">Showing {len(df):,} items</span>
            <span class="results-note">50 per page &middot; select a row for details</span>
        </div>

        <div class="panel">
            <table class="results-table">
                <thead>
                    <tr>
                        <th data-col="name" aria-sort="ascending"><button type="button" class="sort-th" data-sort="name">Name</button></th>
                        <th data-col="source" class="col-source" aria-sort="none"><button type="button" class="sort-th" data-sort="source">Source</button></th>
                        <th data-col="type" class="col-type" aria-sort="none"><button type="button" class="sort-th" data-sort="type">Type</button></th>
                        <th data-col="rarity" aria-sort="none"><button type="button" class="sort-th" data-sort="rarity">Rarity</button></th>
                        <th data-col="attunement" class="col-attune" aria-sort="none"><button type="button" class="sort-th" data-sort="attunement">Attune</button></th>
                        <th data-col="price" class="col-price" aria-sort="none"><button type="button" class="sort-th" data-sort="price">Price</button></th>
                    </tr>
                </thead>
                <tbody id="results-body">
                </tbody>
            </table>
        </div>

        <div class="pagination" id="pagination"></div>
    </main>

    <div class="sheet-backdrop" id="sheet-backdrop"></div>
    <section class="sheet" id="sheet" role="dialog" aria-modal="true" aria-labelledby="sheet-title" hidden>
        <div class="sheet-inner">
            <div class="grab-handle" aria-hidden="true"></div>
            <div class="sheet-eyebrow"><span class="band" id="sheet-band">Common</span></div>
            <h2 id="sheet-title" tabindex="-1"></h2>
            <p class="sheet-price" id="sheet-price"></p>
            <dl class="sheet-facts">
                <dt>Type</dt><dd id="sheet-type"></dd>
                <dt>Source</dt><dd id="sheet-source"></dd>
                <dt>Attunement</dt><dd id="sheet-attune"></dd>
            </dl>
            <p class="sheet-desc" id="sheet-desc"></p>
            <div class="sheet-actions">
                <a class="btn-ghost" id="sheet-link" href="#" target="_blank" rel="noopener">Open on 5e.tools</a>
                <button class="btn-primary" id="sheet-close" type="button">Close</button>
            </div>
        </div>
    </section>

    <footer class="footer">Mistystep shop system &middot; the screen &middot; prices in gp</footer>

    <script src="items-data.js" defer></script>
    <script>
        'use strict';
        var items = window.MISTYSTEP_ITEMS || [];
        var ITEMS_PER_PAGE = 50;
        var PRICE_MIN = {price_min};
        var PRICE_MAX = {price_max};
        var RARITY_ORDER = {{ 'Mundane': 0, 'Unknown': 1, 'Unknown Magic': 2, 'Common': 3, 'Uncommon': 4, 'Rare': 5, 'Very Rare': 6, 'Legendary': 7, 'Artifact': 8, 'Varies': 9 }};
        var SORTABLE = ['name', 'source', 'type', 'rarity', 'attunement', 'price'];
        var ALL_SOURCES = {sources_json};
        var ALL_TYPES = {types_json};
        var state = {{ q: '', rarity: [], type: ALL_TYPES.slice(), source: ALL_SOURCES.slice(), attune: '', min: PRICE_MIN, max: PRICE_MAX, sort: 'name', dir: 'asc', page: 1 }};
        var pageItems = [];
        var lastFocus = null;
        var preResetState = null; /* D4: one-step Reset undo snapshot */

        function $(id) {{ return document.getElementById(id); }}
        function esc(s) {{
            return String(s == null ? '' : s)
                .replace(/&/g, '&amp;').replace(/</g, '&lt;')
                .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
        }}
        function debounce(fn, ms) {{
            var t = null;
            return function() {{
                var args = arguments, ctx = this;
                clearTimeout(t);
                t = setTimeout(function() {{ fn.apply(ctx, args); }}, ms);
            }};
        }}
        function bandClass(rarity) {{
            return 'band-' + String(rarity).toLowerCase().replace(/\\s+/g, '-');
        }}
        function fmtPrice(gp) {{
            if (gp < 1) return Math.round(gp * 100) + ' cp';
            if (gp < 10) return (Math.round(gp * 10) / 10) + ' gp';
            return Math.round(gp).toLocaleString('en-US') + ' gp';
        }}

        /* Log-scale price slider mapping (prices span cp to millions) */
        var LOG_LO = Math.log10(Math.max(PRICE_MIN, 0.001));
        var LOG_HI = Math.log10(Math.max(PRICE_MAX, 0.001));
        function posToVal(p) {{
            var v = Math.pow(10, LOG_LO + (LOG_HI - LOG_LO) * (p / 1000));
            if (v >= 100) return Math.round(v);
            if (v >= 10) return Math.round(v * 10) / 10;
            return Math.round(v * 100) / 100;
        }}
        function valToPos(v) {{
            v = Math.max(v, 0.001);
            var span = (LOG_HI - LOG_LO) || 1;
            return Math.round(1000 * (Math.log10(v) - LOG_LO) / span);
        }}

        function getFilteredItems() {{
            var tokens = state.q.toLowerCase().split(/\\s+/).filter(Boolean);
            return items.filter(function(item) {{
                if (tokens.length) {{
                    var hay = (item.name + ' ' + item.type + ' ' + item.source + ' ' + (item.desc || '')).toLowerCase();
                    for (var i = 0; i < tokens.length; i++) {{
                        if (hay.indexOf(tokens[i]) === -1) return false;
                    }}
                }}
                if (state.source.indexOf(item.source) === -1) return false;
                if (state.type.indexOf(item.type) === -1) return false;
                if (state.rarity.length && state.rarity.indexOf(item.rarity) === -1) return false;
                if (state.attune && item.attunement !== state.attune) return false;
                if (item.price < state.min || item.price > state.max) return false;
                return true;
            }});
        }}

        function sortFilteredItems(filtered) {{
            var col = state.sort, asc = state.dir === 'asc';
            return filtered.sort(function(a, b) {{
                var aVal = a[col], bVal = b[col];
                if (col === 'rarity') {{
                    var ao = RARITY_ORDER[aVal] != null ? RARITY_ORDER[aVal] : 99;
                    var bo = RARITY_ORDER[bVal] != null ? RARITY_ORDER[bVal] : 99;
                    if (ao < bo) return asc ? -1 : 1;
                    if (ao > bo) return asc ? 1 : -1;
                    return 0;
                }}
                if (typeof aVal === 'string') {{
                    aVal = aVal.toLowerCase();
                    bVal = String(bVal).toLowerCase();
                }}
                if (aVal < bVal) return asc ? -1 : 1;
                if (aVal > bVal) return asc ? 1 : -1;
                return 0;
            }});
        }}

        function syncSortHeaders() {{
            document.querySelectorAll('th[data-col]').forEach(function(th) {{
                if (th.dataset.col === state.sort) {{
                    th.setAttribute('aria-sort', state.dir === 'asc' ? 'ascending' : 'descending');
                }} else {{
                    th.setAttribute('aria-sort', 'none');
                }}
            }});
            var sel = $('sort');
            if (sel && SORTABLE.indexOf(state.sort) !== -1) {{
                sel.value = state.sort;
            }}
        }}

        function writeURL() {{
            var p = new URLSearchParams();
            if (state.q) p.set('q', state.q);
            if (state.rarity.length) p.set('rarity', state.rarity.join(','));
            if (state.type.length < ALL_TYPES.length) p.set('type', state.type.join(','));
            if (state.source.length < ALL_SOURCES.length) p.set('source', state.source.join(','));
            if (state.attune) p.set('attune', state.attune);
            if (state.min !== PRICE_MIN) p.set('min', String(state.min));
            if (state.max !== PRICE_MAX) p.set('max', String(state.max));
            if (state.sort !== 'name') p.set('sort', state.sort);
            if (state.dir !== 'asc') p.set('dir', state.dir);
            if (state.page !== 1) p.set('page', String(state.page));
            var qs = p.toString();
            try {{
                history.replaceState(null, '', qs ? ('?' + qs) : location.pathname);
            }} catch (e) {{ /* file:// viewers may refuse replaceState; filters still work */ }}
        }}

        function readURL() {{
            var p = new URLSearchParams(location.search);
            if (p.get('q')) state.q = p.get('q');
            if (p.get('rarity')) state.rarity = p.get('rarity').split(',');
            if (p.has('type')) {{ var tv = p.get('type'); state.type = tv ? tv.split(',') : []; }}
            else state.type = ALL_TYPES.slice();
            if (p.has('source')) {{ var sv = p.get('source'); state.source = sv ? sv.split(',') : []; }}
            else state.source = ALL_SOURCES.slice();
            if (p.get('attune')) state.attune = p.get('attune');
            if (p.get('min') !== null && !isNaN(parseFloat(p.get('min')))) state.min = parseFloat(p.get('min'));
            if (p.get('max') !== null && !isNaN(parseFloat(p.get('max')))) state.max = parseFloat(p.get('max'));
            var urlSort = p.get('sort');
            if (urlSort && SORTABLE.indexOf(urlSort) !== -1) state.sort = urlSort;
            if (p.get('dir') === 'desc' || p.get('dir') === 'asc') state.dir = p.get('dir');
            if (p.get('page') !== null && parseInt(p.get('page'), 10) >= 1) state.page = parseInt(p.get('page'), 10);
        }}

        function renderTable() {{
            var tbody = $('results-body');
            if (!items.length) {{
                tbody.innerHTML = '<tr class="empty-row"><td colspan="6">Item data could not be loaded. Open this page next to items-data.js (same folder) or serve the folder over HTTP.</td></tr>';
                $('results-count').textContent = 'Showing 0 items';
                $('pagination').innerHTML = '';
                return;
            }}
            var filtered = sortFilteredItems(getFilteredItems());
            var totalPages = Math.max(1, Math.ceil(filtered.length / ITEMS_PER_PAGE));
            if (state.page > totalPages) state.page = totalPages;
            var start = (state.page - 1) * ITEMS_PER_PAGE;
            var end = Math.min(start + ITEMS_PER_PAGE, filtered.length);
            pageItems = filtered.slice(start, end);

            if (!pageItems.length) {{
                $('results-count').textContent = 'Showing 0 of ' + filtered.length.toLocaleString('en-US') + ' items';
                tbody.innerHTML = '<tr class="empty-row"><td colspan="6">No items match these filters. <button type="button" class="btn-ghost" id="empty-clear-price">Clear price</button> <button type="button" class="btn-ghost" id="empty-reset">Reset filters</button></td></tr>';
            }} else {{
                $('results-count').textContent =
                    'Showing ' + (start + 1).toLocaleString('en-US') + '\\u2013' + end.toLocaleString('en-US') +
                    ' of ' + filtered.length.toLocaleString('en-US') + ' items';
                tbody.innerHTML = pageItems.map(function(item, i) {{
                    return '<tr class="plate" tabindex="0" data-i="' + i + '">' +
                        '<td>' + esc(item.name) + '</td>' +
                        '<td class="col-source">' + esc(item.source) + '</td>' +
                        '<td class="col-type">' + esc(item.type) + '</td>' +
                        '<td><span class="band ' + bandClass(item.rarity) + '">' + esc(item.rarity) + '</span></td>' +
                        '<td class="col-attune">' + esc(item.attunement) + '</td>' +
                        '<td class="ledger">' + esc(item.priceFormatted) + '</td>' +
                        '</tr>';
                }}).join('');
            }}

            var pg = $('pagination');
            var h = '';
            h += '<button data-page="1"' + (state.page === 1 ? ' disabled' : '') + ' aria-label="First page">\\u00AB\\u00AB</button>';
            h += '<button data-page="' + (state.page - 1) + '"' + (state.page === 1 ? ' disabled' : '') + ' aria-label="Previous page">\\u00AB</button>';
            for (var i = Math.max(1, state.page - 2); i <= Math.min(totalPages, state.page + 2); i++) {{
                h += '<button data-page="' + i + '"' + (i === state.page ? ' class="active" aria-current="page"' : '') + '>' + i + '</button>';
            }}
            h += '<button data-page="' + (state.page + 1) + '"' + (state.page === totalPages ? ' disabled' : '') + ' aria-label="Next page">\\u00BB</button>';
            h += '<button data-page="' + totalPages + '"' + (state.page === totalPages ? ' disabled' : '') + ' aria-label="Last page">\\u00BB\\u00BB</button>';
            pg.innerHTML = h;
            updateFilterCount();
            syncSortHeaders();
            writeURL();
        }}

        function goToPage(page) {{
            state.page = Math.max(1, page);
            renderTable();
        }}

        function setSort(column) {{
            if (state.sort === column) {{
                state.dir = state.dir === 'asc' ? 'desc' : 'asc';
            }} else {{
                state.sort = column;
                state.dir = 'asc';
            }}
            state.page = 1;
            renderTable();
        }}

        /* Detail sheet: one committed pull, no intermediate states */
        function openSheet(item, row) {{
            document.querySelectorAll('tr.plate.stepped').forEach(function(r) {{ r.classList.remove('stepped'); }});
            if (row) row.classList.add('stepped');
            lastFocus = document.activeElement;
            var band = $('sheet-band');
            band.className = 'band ' + bandClass(item.rarity);
            band.textContent = item.rarity;
            $('sheet-title').textContent = item.name;
            $('sheet-price').textContent = item.priceFormatted;
            $('sheet-type').textContent = item.type;
            $('sheet-source').textContent = item.source;
            $('sheet-attune').textContent = item.attunement;
            $('sheet-desc').textContent = item.desc || 'No rules summary in this build \u2014 prices hold; open on 5e.tools for full text.';
            var link = $('sheet-link');
            if (item.url) {{
                link.href = item.url;
                link.style.display = '';
            }} else {{
                link.style.display = 'none';
            }}
            var sheet = $('sheet');
            sheet.hidden = false;
            requestAnimationFrame(function() {{
                sheet.classList.add('open');
                $('sheet-backdrop').classList.add('open');
            }});
            $('sheet-title').focus(); /* D2: initial focus to sheet title, not Close */
        }}
        function closeSheet() {{
            var sheet = $('sheet');
            sheet.classList.remove('open');
            $('sheet-backdrop').classList.remove('open');
            document.querySelectorAll('tr.plate.stepped').forEach(function(r) {{ r.classList.remove('stepped'); }});
            setTimeout(function() {{ sheet.hidden = true; }}, 200);
            if (lastFocus && lastFocus.focus) lastFocus.focus();
        }}

        function syncDropdownAria() {{
            document.querySelectorAll('.dropdown').forEach(function(d) {{
                d.querySelector('.dropdown-btn').setAttribute('aria-expanded', d.classList.contains('open') ? 'true' : 'false');
            }});
        }}

        function updateFilterCount() {{
            var typeN = state.type.length >= ALL_TYPES.length ? 0 : (state.type.length === 0 ? 1 : state.type.length);
            var srcN = state.source.length >= ALL_SOURCES.length ? 0 : (state.source.length === 0 ? 1 : state.source.length);
            var n = state.rarity.length + typeN + srcN + (state.attune ? 1 : 0) +
                ((state.min !== PRICE_MIN || state.max !== PRICE_MAX) ? 1 : 0);
            var badge = $('filters-count');
            if (badge) {{
                badge.textContent = n;
                badge.classList.toggle('quiet', n === 0);
            }}
            var t = $('filters-toggle');
            var isOpen = $('filter-groups').classList.contains('open');
            if (t) t.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
            var lbl = $('filters-toggle-label');
            if (lbl) lbl.textContent = isOpen ? 'Hide filters' : 'Show filters';
        }}

        function updateDropdown(filterName) {{
            var btn = $(filterName + '-btn');
            var all = filterName === 'source' ? ALL_SOURCES : ALL_TYPES;
            var sel = state[filterName];
            var count = sel.length;
            var isAll = count >= all.length;
            var isEmpty = count === 0;
            var label = isAll ? 'All' : isEmpty ? 'None' :
                (count <= 3 ? esc(sel.slice(0, 3).join(', ')) : count + ' selected');
            var badge = isAll ? 0 : isEmpty ? 'None' : '(' + count + ')';
            btn.innerHTML = label +
                ' <span class="filter-count' + (isAll ? ' quiet' : '') + '">' + badge + '</span>';
            var toggle = document.querySelector('.dropdown-select-all[data-target="' + filterName + '"]');
            if (toggle) toggle.textContent = isEmpty ? 'Select all' : 'Clear';
        }}

        function syncControlsFromState() {{
            $('search').value = state.q;
            document.querySelectorAll('.chip[data-rarity]').forEach(function(chip) {{
                chip.setAttribute('aria-pressed', state.rarity.indexOf(chip.dataset.rarity) !== -1 ? 'true' : 'false');
            }});
            document.querySelectorAll('.chip[data-attune]').forEach(function(chip) {{
                chip.setAttribute('aria-pressed', chip.dataset.attune === state.attune ? 'true' : 'false');
            }});
            document.querySelectorAll('.checkbox-item input').forEach(function(cb) {{
                var arr = state[cb.dataset.filter] || [];
                cb.checked = arr.indexOf(cb.value) !== -1;
            }});
            ['source', 'type'].forEach(updateDropdown);
            $('price-min-r').value = valToPos(state.min);
            $('price-max-r').value = valToPos(state.max);
            syncDualFill();
            syncDualZ();
            $('price-min-n').value = state.min;
            $('price-max-n').value = state.max;
            $('price-readout').textContent = fmtPrice(state.min) + ' to ' + fmtPrice(state.max);
            var sel = $('sort');
            if (state.sort === 'name' || state.sort === 'price' || state.sort === 'rarity') sel.value = state.sort;
            if (SORTABLE.indexOf(state.sort) === -1) {{ state.sort = 'name'; sel.value = 'name'; }}
        }}

        /* Single-track dual-handle helpers: position the ember fill between the
           two handles; raise the interacted handle so overlapping thumbs grab. */
        function syncDualFill() {{
            var fill = $('price-fill');
            if (!fill) return;
            var lo = valToPos(state.min) / 10, hi = valToPos(state.max) / 10;
            fill.style.left = lo + '%';
            fill.style.right = (100 - hi) + '%';
        }}
        function syncDualZ(active) {{
            var lo = $('price-min-r'), hi = $('price-max-r');
            if (!lo || !hi) return;
            if (active === 'min') {{ lo.style.zIndex = 5; hi.style.zIndex = 4; }}
            else if (active === 'max') {{ lo.style.zIndex = 3; hi.style.zIndex = 4; }}
            else {{ lo.style.zIndex = 3; hi.style.zIndex = 4; }}
        }}

        /* D4: one-step Undo restores the exact pre-Reset filter state. Note: the
           Back button cannot substitute — writeURL() uses history.replaceState,
           which leaves no history entries to go back to. */
        function snapshotState() {{
            return {{ q: state.q, rarity: state.rarity.slice(), type: state.type.slice(),
                source: state.source.slice(), attune: state.attune,
                min: state.min, max: state.max, sort: state.sort, dir: state.dir, page: state.page }};
        }}
        function resetFilters() {{
            preResetState = snapshotState();
            state = {{ q: '', rarity: [], type: ALL_TYPES.slice(), source: ALL_SOURCES.slice(), attune: '', min: PRICE_MIN, max: PRICE_MAX, sort: 'name', dir: 'asc', page: 1 }};
            syncControlsFromState();
            renderTable();
            var u = $('reset-undo');
            if (u) u.hidden = false;
        }}
        function undoReset() {{
            if (!preResetState) return;
            state = preResetState;
            preResetState = null;
            var u = $('reset-undo');
            if (u) u.hidden = true;
            syncControlsFromState();
            renderTable();
        }}
        function invalidateUndo() {{
            preResetState = null;
            var u = $('reset-undo');
            if (u) u.hidden = true;
        }}

        function init() {{
            items = window.MISTYSTEP_ITEMS || items || []; /* load-path re-sync: deferred items-data.js executes after this inline script parses */
            readURL();
            /* Collapsed-by-default spine: auto-expand when the URL carries
               active non-default filters so shareable links reveal state. */
            (function() {{
                var hasActive = state.q || state.rarity.length || state.attune ||
                    state.type.length < ALL_TYPES.length || state.source.length < ALL_SOURCES.length ||
                    state.min !== PRICE_MIN || state.max !== PRICE_MAX ||
                    state.sort !== 'name' || state.dir !== 'asc';
                if (hasActive) $('filter-groups').classList.add('open');
            }})();
            syncControlsFromState();

            /* Debounced full-text search over name + type + source + rules */
            $('search').addEventListener('input', debounce(function(e) {{
                state.q = e.target.value;
                state.page = 1;
                renderTable();
            }}, 200));

            /* Rarity chips (multi) */
            document.querySelectorAll('.chip[data-rarity]').forEach(function(chip) {{
                chip.addEventListener('click', function() {{
                    var r = chip.dataset.rarity;
                    var idx = state.rarity.indexOf(r);
                    if (idx > -1) state.rarity.splice(idx, 1);
                    else state.rarity.push(r);
                    chip.setAttribute('aria-pressed', idx > -1 ? 'false' : 'true');
                    state.page = 1;
                    renderTable();
                }});
            }});

            /* Attunement toggle (single) */
            document.querySelectorAll('.chip[data-attune]').forEach(function(chip) {{
                chip.addEventListener('click', function() {{
                    state.attune = chip.dataset.attune;
                    document.querySelectorAll('.chip[data-attune]').forEach(function(c) {{
                        c.setAttribute('aria-pressed', c === chip ? 'true' : 'false');
                    }});
                    state.page = 1;
                    renderTable();
                }});
            }});

            /* Source / type checkbox dropdowns */
            document.querySelectorAll('.checkbox-item input').forEach(function(checkbox) {{
                checkbox.addEventListener('change', function() {{
                    var arr = state[this.dataset.filter];
                    if (this.checked) arr.push(this.value);
                    else {{
                        var idx = arr.indexOf(this.value);
                        if (idx > -1) arr.splice(idx, 1);
                    }}
                    updateDropdown(this.dataset.filter);
                    state.page = 1;
                    renderTable();
                }});
            }});

            /* Source / type Select-all / Clear toggle: label flips on state;
               empty selection means none (zero rows), not all. */
            document.querySelectorAll('.dropdown-select-all').forEach(function(btn) {{
                btn.addEventListener('click', function(e) {{
                    e.stopPropagation();
                    var name = btn.dataset.target;
                    var all = name === 'source' ? ALL_SOURCES : ALL_TYPES;
                    var toAll = state[name].length === 0;
                    state[name] = toAll ? all.slice() : [];
                    document.querySelectorAll('.checkbox-item input[data-filter="' + name + '"]').forEach(function(cb) {{
                        cb.checked = toAll;
                    }});
                    updateDropdown(name);
                    state.page = 1;
                    renderTable();
                }});
            }});
            /* Dropdown open/close + inner search */
            document.querySelectorAll('.dropdown').forEach(function(dropdown) {{
                dropdown.querySelector('.dropdown-btn').addEventListener('click', function(e) {{
                    e.stopPropagation();
                    var wasOpen = dropdown.classList.contains('open');
                    document.querySelectorAll('.dropdown').forEach(function(d) {{ d.classList.remove('open'); }});
                    if (!wasOpen) dropdown.classList.add('open');
                    syncDropdownAria();
                }});
                dropdown.querySelector('.dropdown-content').addEventListener('click', function(e) {{ e.stopPropagation(); }});
            }});
            document.addEventListener('click', function() {{
                document.querySelectorAll('.dropdown').forEach(function(d) {{ d.classList.remove('open'); }});
                syncDropdownAria();
            }});
            document.querySelectorAll('.dropdown-search').forEach(function(input) {{
                input.addEventListener('input', function() {{
                    var query = this.value.toLowerCase();
                    this.parentElement.querySelectorAll('.checkbox-item').forEach(function(item) {{
                        var text = item.querySelector('span').textContent.toLowerCase();
                        item.style.display = text.indexOf(query) !== -1 ? '' : 'none';
                    }});
                }});
                input.addEventListener('click', function(e) {{ e.stopPropagation(); }});
            }});

            /* D3: handles cannot cross (clamp + write handle back); typed inputs snap
            to the slider step; one aria-live announcement on release only
            (change), never per-move (input). */
            function snapToStep(v) {{
                return posToVal(valToPos(v));
            }}
            function announcePrice() {{
                var live = $('price-status');
                if (live) live.textContent = 'Price range ' + fmtPrice(state.min) + ' to ' + fmtPrice(state.max);
            }}
            /* Price range: sliders + numbers, synced */
            $('price-min-r').addEventListener('input', function(e) {{
                state.min = Math.min(posToVal(parseInt(e.target.value, 10)), state.max);
                e.target.value = valToPos(state.min);
                $('price-min-n').value = state.min;
                $('price-readout').textContent = fmtPrice(state.min) + ' to ' + fmtPrice(state.max);
                syncDualFill();
                syncDualZ('min');
                state.page = 1;
                renderTable();
            }});
            $('price-max-r').addEventListener('input', function(e) {{
                state.max = Math.max(posToVal(parseInt(e.target.value, 10)), state.min);
                e.target.value = valToPos(state.max);
                $('price-max-n').value = state.max;
                $('price-readout').textContent = fmtPrice(state.min) + ' to ' + fmtPrice(state.max);
                syncDualFill();
                syncDualZ('max');
                state.page = 1;
                renderTable();
            }});
            $('price-min-n').addEventListener('change', function(e) {{
                var v = parseFloat(e.target.value);
                if (isNaN(v)) return;
                state.min = Math.max(PRICE_MIN, Math.min(snapToStep(v), state.max));
                e.target.value = state.min;
                $('price-min-r').value = valToPos(state.min);
                $('price-readout').textContent = fmtPrice(state.min) + ' to ' + fmtPrice(state.max);
                syncDualFill();
                syncDualZ();
                announcePrice();
                state.page = 1;
                renderTable();
            }});
            $('price-max-n').addEventListener('change', function(e) {{
                var v = parseFloat(e.target.value);
                if (isNaN(v)) return;
                state.max = Math.min(PRICE_MAX, Math.max(snapToStep(v), state.min));
                e.target.value = state.max;
                $('price-max-r').value = valToPos(state.max);
                $('price-readout').textContent = fmtPrice(state.min) + ' to ' + fmtPrice(state.max);
                syncDualFill();
                syncDualZ();
                announcePrice();
                state.page = 1;
                renderTable();
            }});
            $('price-min-r').addEventListener('change', announcePrice);
            $('price-max-r').addEventListener('change', announcePrice);
            $('price-min-r').addEventListener('focus', function() {{ syncDualZ('min'); }});
            $('price-max-r').addEventListener('focus', function() {{ syncDualZ('max'); }});

            /* Sort: select mirrors sortable column headers */
            $('sort').addEventListener('change', function(e) {{
                state.sort = e.target.value;
                state.dir = 'asc';
                state.page = 1;
                renderTable();
            }});
            document.querySelectorAll('.sort-th').forEach(function(btn) {{
                btn.addEventListener('click', function() {{ setSort(btn.dataset.sort); }});
            }});

            /* Pagination (event delegation) */
            $('pagination').addEventListener('click', function(e) {{
                var btn = e.target.closest('button[data-page]');
                if (btn && !btn.disabled) goToPage(parseInt(btn.dataset.page, 10));
            }});

            /* Tap-row detail sheet (click + keyboard) */
            $('results-body').addEventListener('click', function(e) {{
                if (e.target.closest('#empty-reset')) {{ resetFilters(); return; }}
                if (e.target.closest('#empty-clear-price')) {{
                    state.min = PRICE_MIN; state.max = PRICE_MAX; state.page = 1;
                    syncControlsFromState();
                    renderTable();
                    return;
                }}
                var row = e.target.closest('tr.plate');
                if (row) openSheet(pageItems[parseInt(row.dataset.i, 10)], row);
            }});
            $('results-body').addEventListener('keydown', function(e) {{
                var row = e.target.closest('tr.plate');
                if (row && (e.key === 'Enter' || e.key === ' ')) {{
                    e.preventDefault();
                    openSheet(pageItems[parseInt(row.dataset.i, 10)], row);
                }}
            }});
            $('sheet-close').addEventListener('click', closeSheet);
            $('sheet-backdrop').addEventListener('click', closeSheet);
            document.addEventListener('keydown', function(e) {{
                if (e.key === 'Escape') {{
                    if ($('sheet').classList.contains('open')) closeSheet();
                    document.querySelectorAll('.dropdown').forEach(function(d) {{ d.classList.remove('open'); }});
                    syncDropdownAria();
                }}
            }});

            $('filters-toggle').addEventListener('click', function(e) {{
                e.stopPropagation();
                $('filter-groups').classList.toggle('open');
                updateFilterCount();
            }});

            $('reset-btn').addEventListener('click', resetFilters);
            $('reset-undo').addEventListener('click', undoReset);

            /* D2: sheet focus trap — Tab cycles inside the open sheet (Esc + backdrop close preserved) */
            $('sheet').addEventListener('keydown', function(e) {{
                if (e.key !== 'Tab') return;
                var focusables = Array.prototype.slice.call(
                    document.querySelectorAll('#sheet-title, #sheet a[href], #sheet button')
                ).filter(function(el) {{ return el.id === 'sheet-title' || el.style.display !== 'none'; }});
                if (!focusables.length) return;
                var first = focusables[0], last = focusables[focusables.length - 1];
                if (e.shiftKey && document.activeElement === first) {{ e.preventDefault(); last.focus(); }}
                else if (!e.shiftKey && document.activeElement === last) {{ e.preventDefault(); first.focus(); }}
            }});

            /* D4: any fresh filter edit after a Reset invalidates the one-step undo */
            (function() {{
                var spine = document.querySelector('.spine');
                if (!spine) return;
                ['input', 'change'].forEach(function(evt) {{
                    spine.addEventListener(evt, function(e) {{
                        if (e.target.closest && e.target.closest('#reset-btn, #reset-undo')) return;
                        invalidateUndo();
                    }});
                }});
                spine.addEventListener('click', function(e) {{
                    if (e.target.closest && e.target.closest('#reset-btn, #reset-undo')) return;
                    invalidateUndo();
                }});
            }})();

            renderTable();
        }}

        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', init);
        }} else {{
            init();
        }}
    </script>
</body>
</html>'''

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Saved HTML interface to {OUTPUT_HTML}")

    # Externalize the item payload: classic script, relative path, works on
    # Pages and file:// alike (no fetch/CORS involved).
    with open(ITEMS_JS, "w", encoding="utf-8") as f:
        f.write("window.MISTYSTEP_ITEMS = ")
        json.dump(items_data, f, ensure_ascii=False)
        f.write(";")

    print(f"Saved item payload ({len(items_data)} rows) to {ITEMS_JS}")


if __name__ == '__main__':
    main()
