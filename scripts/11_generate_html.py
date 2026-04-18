#!/usr/bin/env python3
"""Generate HTML interface for the pricing guide"""

import json
import csv
import pandas as pd
from pathlib import Path

INPUT_CSV = Path('output/pricing_guide.csv')
OUTPUT_HTML = Path('index.html')

# Sourcebook mapping: acronym -> full name (from 5e.tools)
SOURCEBOOK_NAMES = {
    # Core Books
    "PHB": "Player's Handbook",
    "XPHB": "Player's Handbook (2024)",
    "DMG": "Dungeon Master's Guide",
    "XDMG": "Dungeon Master's Guide (2024)",
    "MM": "Monster Manual",
    "XMM": "Monster Manual (2024)",
    
    # Expansion Books
    "XGE": "Xanathar's Guide to Everything",
    "VGM": "Volo's Guide to Monsters",
    "VRGR": "Van Richten's Guide to Ravenloft",
    "TCE": "Tasha's Cauldron of Everything",
    "MTF": "Mordenkainen's Tome of Foes",
    "SCAG": "Sword Coast Adventurer's Guide",
    "GGR": "Guildmasters' Guide to Ravnica",
    "ERLW": "Eberron: Rising from the Last War",
    "EGW": "Explorer's Guide to Wildemount",
    "MOT": "Mythic Odysseys of Theros",
    "FTD": "Fizban's Treasury of Dragons",
    "SCC": "Strixhaven: A Curriculum of Chaos",
    "CRCotN": "Critical Role: Call of the Netherdeep",
    
    # Adventures
    "SKT": "Storm King's Thunder",
    "CoS": "Curse of Strahd",
    "ToA": "Tomb of Annihilation",
    "HotDQ": "Hoard of the Dragon Queen",
    "LMoP": "Lost Mine of Phandelver",
    "WDH": "Waterdeep: Dragon Heist",
    "WDMM": "Waterdeep: Dungeon of the Mad Mage",
    "BGDIA": "Baldur's Gate: Descent Into Avernus",
    "OotA": "Out of the Abyss",
    "PotA": "Princes of the Apocalypse",
    "IDRotF": "Icewind Dale: Rime of the Frostmaiden",
    "GoS": "Ghosts of Saltmarsh",
    "TftYP": "Tales from the Yawning Portal",
    "KftGV": "Keys from the Golden Vault",
    "JttRC": "Journeys through the Radiant Citadel",
    "DSotDQ": "Dragonlance: Shadow of the Dragon Queen",
    "DitLCoT": "Descent into the Lost Caverns of Tsojcanth",
    "LoX": "Light of Xaryxis",
    "PaBTSO": "Phandelver and Below: The Shattered Obelisk",
    "VEoR": "Vecna: Eve of Ruin",
    "WBtW": "The Wild Beyond the Witchlight",
    "QftIS": "Quests from the Infinite Staircase",
    
    # Other Supplements
    "BAM": "Boo's Astral Menagerie",
    "AI": "Acquisitions Incorporated",
    "BGG": "Bigby Presents: Glory of the Giants",
    "BMT": "The Book of Many Things",
    "CM": "Candlekeep Mysteries",
    "AAG": "Astral Adventurer's Guide",
    "SAT": "Sigil and the Outlands",
    "SDW": "Sleeping Dragon's Wake",
    "HotB": "Heroes of the Borderlands",
    "LFL": "Lorwyn: First Light",
    "RoT": "The Rise of Tiamat",
    "RoTOS": "The Rise of Tiamat Online Supplement",
    "RMBRE": "The Lost Dungeon of Rickedness",
    "WttHC": "Stranger Things: Welcome to the Hellfire Club",
    
    # Eberron
    "EET": "Elemental Evil: Trinkets",
    "EFA": "Eberron: Forge of the Artificer",
    "FRAiF": "Forgotten Realms: Adventures in Faerûn",
    "FRHoF": "Forgotten Realms: Heroes of Faerûn",
    "NF": "Netheril's Fall",
    "ExploringEberron24": "Exploring Eberron (2024)",
    "ChroniclesOfEberron": "Chronicles of Eberron",
    
    # Third Party / Other
    "DC": "Divine Contention",
    "FoEQuickstone": "Frontiers of Eberron: Quickstone",
    "HftT": "Hunt for the Thessalhydra",
    "MonstersOfDrakkenheim": "Monsters of Drakkenheim",
    "DungeonsDrakkenheim": "Dungeons of Drakkenheim",
}

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
    "SPC": "Species Item",  # From Astral Adventurer's Guide
    "Dele": "Delerium",  # From Monsters of Drakkenheim
    "EM": "Eldritch Machine",  # From Exploring Eberron
    "TAH": "Tack & Harness",
}


def translate_source(source_code):
    """Translate sourcebook acronym to full name"""
    if pd.isna(source_code):
        return 'Unknown'
    sources = str(source_code).split('|')
    translated = []
    for s in sources:
        s = s.strip()
        translated.append(SOURCEBOOK_NAMES.get(s, s))
    return ', '.join(translated)


def translate_type(type_code):
    """Translate 5e.tools type code to common name"""
    if pd.isna(type_code):
        return 'Unknown'
    types = str(type_code).split('|')
    translated = []
    for t in types:
        t = t.strip()
        if t in TYPE_NAMES:
            translated.append(TYPE_NAMES[t])
        else:
            base = t.split('|')[0]
            translated.append(TYPE_NAMES.get(base, base))
    return ', '.join(translated)


def format_price(price_gp):
    if price_gp < 1:
        return f"{int(price_gp * 100)} cp"
    elif price_gp < 10:
        return f"{price_gp:.1f} gp"
    else:
        return f"{int(price_gp):,} gp"


def main():
    df = pd.read_csv(INPUT_CSV)
    print(f'Loaded {len(df)} items')
    
    # Translate source and type for the UI
    df['Source Display'] = df['Source'].apply(translate_source)
    df['Type Display'] = df['Type'].apply(translate_type)
    
    # Build unique filter options
    sources = sorted(df['Source Display'].unique())
    types = sorted(df['Type Display'].unique())
    rarities = sorted(df['Rarity'].unique())
    
    # Convert data to JSON
    items_data = []
    for _, row in df.iterrows():
        items_data.append({
            'name': row['Name'],
            'source': row['Source Display'],
            'sourceCode': row['Type'],  # Keep original Type for filtering
            'type': row['Type Display'],
            'typeCode': row['Type'],  # Actually we need this too
            'rarity': row['Rarity'],
            'attunement': row['Attunement'],
            'price': row['Price (gp)'],
            'priceFormatted': row['Price Formatted'],
        })
    
    # Generate HTML with dropdown checkboxes
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>D&D 5e Magic Item Pricing Guide</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            color: #e0e0e0;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ text-align: center; color: #ffd700; margin-bottom: 10px; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }}
        .subtitle {{ text-align: center; color: #888; margin-bottom: 30px; }}
        .filters {{ background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin-bottom: 20px; backdrop-filter: blur(10px); }}
        .search-row {{ display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 15px; align-items: center; }}
        .filter-row {{ display: flex; gap: 20px; flex-wrap: wrap; align-items: flex-start; }}
        .filter-group {{ display: flex; flex-direction: column; gap: 5px; position: relative; }}
        .filter-group label {{ font-size: 0.85em; color: #aaa; font-weight: 500; }}
        
        /* Dropdown button style */
        .dropdown {{ position: relative; display: inline-block; }}
        .dropdown-btn {{
            padding: 10px 15px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 6px;
            background: rgba(0,0,0,0.3);
            color: #fff;
            font-size: 14px;
            min-width: 180px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .dropdown-btn:after {{ content: ' ▼'; font-size: 0.7em; }}
        .dropdown-btn:hover, .dropdown.open .dropdown-btn {{ border-color: #ffd700; }}
        
        /* Dropdown content - always hidden by default, shown when .open class present */
        .dropdown-content {{
            display: none;
            position: absolute;
            background: rgba(30,30,40,0.98);
            min-width: 250px;
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 6px;
            z-index: 1000;
            margin-top: 5px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        }}
        .dropdown.open .dropdown-content {{ display: block; }}
        
        /* Checkbox list */
        .checkbox-list {{
            padding: 10px;
            max-height: 250px;
            overflow-y: auto;
        }}
        .checkbox-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 5px 8px;
            cursor: pointer;
            border-radius: 4px;
        }}
        .checkbox-item:hover {{ background: rgba(255,255,255,0.1); }}
        .checkbox-item input[type="checkbox"] {{ min-width: auto; cursor: pointer; }}
        .checkbox-item span {{ font-size: 0.9em; color: #ccc; cursor: pointer; }}
        
        /* Show count in button */
        .filter-count {{ 
            background: #ffd700; 
            color: #000; 
            padding: 2px 6px; 
            border-radius: 10px; 
            font-size: 0.75em; 
            margin-left: 5px;
        }}
        
        input[type="text"] {{ padding: 10px 15px; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; background: rgba(0,0,0,0.3); color: #fff; font-size: 14px; min-width: 250px; }}
        input[type="number"] {{ padding: 10px 15px; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; background: rgba(0,0,0,0.3); color: #fff; font-size: 14px; width: 100px; }}
        
        .price-range {{ display: flex; align-items: center; gap: 10px; }}
        .price-range span {{ color: #888; }}
        
        .results-info {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding: 10px 15px; background: rgba(255,255,255,0.05); border-radius: 6px; }}
        .results-count {{ color: #ffd700; font-weight: bold; }}
        .results-table {{ width: 100%; border-collapse: collapse; background: rgba(255,255,255,0.05); border-radius: 10px; overflow: hidden; }}
        .results-table th {{ background: #2d4a3e; color: #fff; padding: 12px 15px; text-align: left; font-weight: 600; cursor: pointer; user-select: none; white-space: nowrap; }}
        .results-table th:hover {{ background: #3d5a4e; }}
        .results-table td {{ padding: 10px 15px; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        .results-table tr:hover {{ background: rgba(255,255,255,0.1); }}
        .rarity-common {{ color: #fff; }}
        .rarity-uncommon {{ color: #1eff00; }}
        .rarity-rare {{ color: #0070dd; }}
        .rarity-very rare {{ color: #a335ee; }}
        .rarity-legendary {{ color: #ff8000; }}
        .rarity-artifact {{ color: #e6cc80; }}
        .rarity-mundane {{ color: #999; }}
        
        .price {{ font-family: 'Courier New', monospace; font-weight: bold; }}
        
        a {{ color: #64b5f6; text-decoration: none; }}
        
        .pagination {{ display: flex; justify-content: center; gap: 10px; margin-top: 20px; }}
        .pagination button {{ padding: 8px 16px; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; background: rgba(0,0,0,0.3); color: #fff; cursor: pointer; transition: all 0.2s; }}
        .pagination button:hover {{ background: rgba(255,215,0,0.2); border-color: #ffd700; }}
        .pagination button:disabled {{ opacity: 0.5; cursor: not-allowed; }}
        .pagination button.active {{ background: #ffd700; color: #000; border-color: #ffd700; }}
        
        .reset-btn {{ padding: 10px 20px; background: #dc2626; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }}
        .reset-btn:hover {{ background: #b91c1c; }}
    </style>
</head>
<body>
    <div class="container">
        
        <div class="filters">
            <div class="search-row">
                <input type="text" id="search" placeholder="Search items by name..." autocomplete="off">
                <button class="reset-btn" onclick="resetFilters()">Reset Filters</button>
            </div>
            <div class="filter-row">
                <div class="filter-group">
                    <label>Sourcebook</label>
                    <div class="dropdown" onclick="this.classList.toggle('open'); event.stopPropagation();">
                        <button class="dropdown-btn" id="source-btn" type="button">All <span class="filter-count">0</span></button>
                        <div class="dropdown-content">
                            <div class="checkbox-list" onclick="event.stopPropagation();">
                                {''.join(f'<div class="checkbox-item"><input type="checkbox" id="src_{i}" value="{s}" data-filter="source"><span>{s}</span></div>' for i, s in enumerate(sources))}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="filter-group">
                    <label>Item Type</label>
                    <div class="dropdown" onclick="this.classList.toggle('open'); event.stopPropagation();">
                        <button class="dropdown-btn" id="type-btn" type="button">All <span class="filter-count">0</span></button>
                        <div class="dropdown-content">
                            <div class="checkbox-list" onclick="event.stopPropagation();">
                                {''.join(f'<div class="checkbox-item"><input type="checkbox" id="type_{i}" value="{t}" data-filter="type"><span>{t}</span></div>' for i, t in enumerate(types))}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="filter-group">
                    <label>Rarity</label>
                    <div class="dropdown" onclick="this.classList.toggle('open'); event.stopPropagation();">
                        <button class="dropdown-btn" id="rarity-btn" type="button">All <span class="filter-count">0</span></button>
                        <div class="dropdown-content">
                            <div class="checkbox-list" onclick="event.stopPropagation();">
                                {''.join(f'<div class="checkbox-item"><input type="checkbox" id="rar_{i}" value="{r}" data-filter="rarity"><span>{r}</span></div>' for i, r in enumerate(rarities))}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="filter-group">
                    <label>Attunement</label>
                    <select id="filter-attunement" style="padding: 10px 15px; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; background: rgba(0,0,0,0.3); color: #fff; font-size: 14px; min-width: 150px;">
                        <option value="">Any</option>
                        <option value="No">No Attunement</option>
                        <option value="Yes">Requires Attunement</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Price Range (gp)</label>
                    <div class="price-range">
                        <input type="number" id="price-min" placeholder="Min" min="0">
                        <span>to</span>
                        <input type="number" id="price-max" placeholder="Max" min="0">
                    </div>
                </div>
            </div>
        </div>
        
        <div class="results-info">
            <span class="results-count" id="results-count">Showing {len(df):,} items</span>
        </div>
        
        <table class="results-table">
            <thead>
                <tr>
                    <th onclick="sortTable('name')">Name</th>
                    <th onclick="sortTable('source')">Source</th>
                    <th onclick="sortTable('type')">Type</th>
                    <th onclick="sortTable('rarity')">Rarity</th>
                    <th onclick="sortTable('attunement')">Attune</th>
                    <th onclick="sortTable('price')">Price</th>
                </tr>
            </thead>
            <tbody id="results-body">
            </tbody>
        </table>
        
        <div class="pagination" id="pagination">
        </div>
    </div>
    
    <script>
        const items = {json.dumps(items_data, ensure_ascii=False)};
        const ITEMS_PER_PAGE = 50;
        let currentPage = 1;
        let sortColumn = 'name';
        let sortAsc = true;
        
        // Track selected filters
        let selectedFilters = {{ source: [], type: [], rarity: [] }};
        
        // Update dropdown button text and count
        function updateDropdown(filterName) {{
            const btn = document.getElementById(filterName + '-btn');
            const count = selectedFilters[filterName].length;
            if (count === 0) {{
                btn.innerHTML = 'All';
            }} else if (count <= 3) {{
                btn.innerHTML = selectedFilters[filterName].slice(0,3).join(', ') + (count > 3 ? '...' : '');
            }} else {{
                btn.innerHTML = count + ' selected';
            }}
            btn.innerHTML += ' <span class="filter-count">' + count + '</span>';
        }}
        
        // Add checkbox listeners
        document.querySelectorAll('.checkbox-item input').forEach(checkbox => {{
            checkbox.addEventListener('change', function() {{
                const filterName = this.dataset.filter;
                if (this.checked) {{
                    selectedFilters[filterName].push(this.value);
                }} else {{
                    const idx = selectedFilters[filterName].indexOf(this.value);
                    if (idx > -1) selectedFilters[filterName].splice(idx, 1);
                }}
                updateDropdown(filterName);
                currentPage = 1;
                renderTable();
            }});
        }});
        
        function getFilteredItems() {{
            const search = document.getElementById('search').value.toLowerCase();
            const attunement = document.getElementById('filter-attunement').value;
            const priceMin = parseFloat(document.getElementById('price-min').value) || 0;
            const priceMax = parseFloat(document.getElementById('price-max').value) || Infinity;
            
            return items.filter(item => {{
                if (search && !item.name.toLowerCase().includes(search)) return false;
                if (selectedFilters.source.length > 0 && !selectedFilters.source.includes(item.source)) return false;
                if (selectedFilters.type.length > 0 && !selectedFilters.type.includes(item.type)) return false;
                if (selectedFilters.rarity.length > 0 && !selectedFilters.rarity.includes(item.rarity)) return false;
                if (attunement && item.attunement !== attunement) return false;
                if (item.price < priceMin || item.price > priceMax) return false;
                return true;
            }});
        }}
        
        function sortFilteredItems(filtered) {{
            return filtered.sort((a, b) => {{
                let aVal = a[sortColumn];
                let bVal = b[sortColumn];
                if (typeof aVal === 'string') {{
                    aVal = aVal.toLowerCase();
                    bVal = bVal.toLowerCase();
                }}
                if (aVal < bVal) return sortAsc ? -1 : 1;
                if (aVal > bVal) return sortAsc ? 1 : -1;
                return 0;
            }});
        }}
        
        function renderTable() {{
            const filtered = sortFilteredItems(getFilteredItems());
            const totalPages = Math.ceil(filtered.length / ITEMS_PER_PAGE);
            const start = (currentPage - 1) * ITEMS_PER_PAGE;
            const end = Math.min(start + ITEMS_PER_PAGE, filtered.length);
            const pageItems = filtered.slice(start, end);
            
            document.getElementById('results-count').textContent = 
                `Showing ${{start + 1}}-${{end}} of ${{filtered.length}} items`;
            
            const tbody = document.getElementById('results-body');
            tbody.innerHTML = pageItems.map(item => `
                <tr>
                    <td><strong>${{item.name}}</strong></td>
                    <td>${{item.source}}</td>
                    <td>${{item.type}}</td>
                    <td class="rarity-${{item.rarity.toLowerCase()}}">${{item.rarity}}</td>
                    <td>${{item.attunement}}</td>
                    <td class="price">${{item.priceFormatted}}</td>
                </tr>
            `).join('');
            
            // Render pagination
            const pagination = document.getElementById('pagination');
            let paginationHTML = '';
            paginationHTML += `<button onclick="goToPage(1)" ${{currentPage === 1 ? 'disabled' : ''}}>««</button>`;
            paginationHTML += `<button onclick="goToPage(currentPage - 1)" ${{currentPage === 1 ? 'disabled' : ''}}>«</button>`;
            
            for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {{
                paginationHTML += `<button class="${{i === currentPage ? 'active' : ''}}" onclick="goToPage(${{i}})">${{i}}</button>`;
            }}
            
            paginationHTML += `<button onclick="goToPage(currentPage + 1)" ${{currentPage === totalPages ? 'disabled' : ''}}>»</button>`;
            paginationHTML += `<button onclick="goToPage(${{totalPages}})" ${{currentPage === totalPages ? 'disabled' : ''}}>»»</button>`;
            pagination.innerHTML = paginationHTML;
        }}
        
        function goToPage(page) {{
            currentPage = page;
            renderTable();
        }}
        
        function sortTable(column) {{
            if (sortColumn === column) {{
                sortAsc = !sortAsc;
            }} else {{
                sortColumn = column;
                sortAsc = true;
            }}
            renderTable();
        }}
        
        function resetFilters() {{
            document.getElementById('search').value = '';
            document.querySelectorAll('.checkbox-item input').forEach(cb => cb.checked = false);
            selectedFilters = {{ source: [], type: [], rarity: [] }};
            ['source', 'type', 'rarity'].forEach(updateDropdown);
            document.getElementById('filter-attunement').value = '';
            document.getElementById('price-min').value = '';
            document.getElementById('price-max').value = '';
            currentPage = 1;
            renderTable();
        }}
        
        // Add event listeners
        document.querySelectorAll('input, select').forEach(el => {{
            el.addEventListener('change', () => {{ currentPage = 1; renderTable(); }});
            el.addEventListener('input', () => {{ currentPage = 1; renderTable(); }});
        }});
        
        // Add click handlers for dropdowns to toggle on click
        document.querySelectorAll('.dropdown').forEach(dropdown => {{
            dropdown.addEventListener('click', function(e) {{
                // Toggle the open class
                this.classList.toggle('open');
                e.stopPropagation();
            }});
        }});
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', function(e) {{
            document.querySelectorAll('.dropdown').forEach(dropdown => {{
                if (!dropdown.contains(e.target)) {{
                    dropdown.classList.remove('open');
                }}
            }});
        }});
        
        // Prevent checkbox clicks from closing dropdown
        document.querySelectorAll('.checkbox-item').forEach(item => {{
            item.addEventListener('click', function(e) {{
                e.stopPropagation();
            }});
        }});
        
        // Initial render
        renderTable();
    </script>
</body>
</html>'''
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Saved HTML interface to {OUTPUT_HTML}")


if __name__ == '__main__':
    main()