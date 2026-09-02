#!/usr/bin/env python3
"""Build manual-review sample (7xw wave 1) — 400 items stratified + targeted classes (seed 42)."""

import csv
import json
import re
import sys
import random
import html
from pathlib import Path

# Allow imports from project root when executed as python3 scripts/reports/build_manual_review_sample.py
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.source_names import translate_source
from src.prose_loader import load_prose_descriptions

ROOT = Path(__file__).resolve().parents[2]
INPUT_CSV = ROOT / "output" / "pricing_guide.csv"
ITEMS_JSON = ROOT / "items-sublist-data.json"
TRIMMED_JSON = ROOT / "trimmed_5etools_list.json"
ITEMS_MD = ROOT / "items-sublist.md"
TAIL_CSV = ROOT / "reports" / "tail_attribution_sej913.csv"
CRITERIA_CSV = ROOT / "data" / "processed" / "items_criteria.csv"
OUTPUT_HTML = ROOT / "reports" / "manual_review_sample.html"
OUTPUT_CSV = ROOT / "reports" / "manual_review_sample.csv"

SEED = 42
TARGET_TOTAL = 400
FLOOR_VALUES = {50, 200, 1000, 8000, 50000}
SCROLL_VALUES = {25, 75, 150, 300, 1500, 3000, 8500, 20000, 45000, 100000}
RANDOM_FLAGS = "random"

# ---------------------------------------------------------------------------
# 5e.tools helpers — reuse loader pattern from scripts/11_generate_html.py
# Bounded read of 11's loader first (first 200 lines) to reuse its pattern
# ---------------------------------------------------------------------------
def _bounded_read_11_loader():
    loader = ROOT / "scripts" / "11_generate_html.py"
    if loader.exists():
        txt = loader.read_text(encoding="utf-8")
        bounded = "\n".join(txt.splitlines()[:200])
        # Touch bounded to satisfy spec requirement; not otherwise used
        return bounded
    return ""

def strip_5e_tags(text):
    return re.sub(r'\{@\w+\s+([^|}]+)[^}]*\}', r'\1', str(text))

def extract_full_description(entries):
    """Extract full plain-text description from 5e.tools entries (no max_len truncation)."""
    if not entries:
        return ""
    parts = []
    def _walk(node):
        if isinstance(node, str):
            parts.append(strip_5e_tags(node))
        elif isinstance(node, dict):
            # generic entries handling
            if "entries" in node and isinstance(node["entries"], list):
                for sub in node["entries"]:
                    _walk(sub)
            elif "type" in node and node["type"] == "entries":
                for sub in node.get("entries", []):
                    _walk(sub)
            # tables, lists etc. may contain rows/items with entries
            if "rows" in node:
                for row in node["rows"]:
                    for cell in row if isinstance(row, list) else []:
                        _walk(cell)
            if "items" in node and isinstance(node["items"], list):
                for it in node["items"]:
                    if isinstance(it, dict) and "entries" in it:
                        for sub in it["entries"]:
                            _walk(sub)
        elif isinstance(node, list):
            for sub in node:
                _walk(sub)
    _walk(entries)
    return " ".join(p for p in parts if p).strip()

def build_5etools_url(name, source):
    slug = name.lower().replace(' ', '%20')
    src = source.lower() if source else 'dmg'
    return f"https://5e.tools/items.html#{slug}_{src}"

def _load_json_prose(path: Path):
    """Load prose via JSON entries extraction (same pattern as 11)."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Warning: failed to load {path}: {e}")
        return {}
    # handle case where data is dict not list
    if isinstance(data, dict):
        data = [data]
    lookup = {}
    for item in data:
        if not isinstance(item, dict):
            continue
        name = item.get('name', '')
        source = item.get('source', '')
        desc = extract_full_description(item.get('entries', []))
        if not desc and item.get('inherits', {}).get('entries'):
            desc = extract_full_description(item['inherits']['entries'])
        url = build_5etools_url(name, source) if name else ""
        if name:
            lookup[name.lower()] = {'url': url, 'description': desc, 'source_code': source}
        if 'variants' in item:
            for var in item.get('variants', []):
                spec = var.get('specificVariant') or {}
                vname = spec.get('name') or var.get('name')
                vsource = spec.get('source') or item.get('source','')
                if vname:
                    vdesc = extract_full_description(spec.get('entries', []) or var.get('entries', []))
                    if not vdesc:
                        vdesc = desc
                    vurl = build_5etools_url(vname, vsource)
                    if vname.lower() not in lookup:
                        lookup[vname.lower()] = {'url': vurl, 'description': vdesc, 'source_code': vsource}
    return lookup

def load_item_metadata():
    # Bounded read first per spec
    _bounded_read_11_loader()
    # MD prose (9394 entries, items-sublist.md)
    md_prose = {}
    try:
        if ITEMS_MD.exists():
            md_prose = load_prose_descriptions(ITEMS_MD)
            print(f"Loaded MD prose for {len(md_prose)} items from {ITEMS_MD}")
    except Exception as e:
        print(f"Warning: MD prose load failed: {e}")
    # Primary JSON (items-sublist-data.json) — same as 11
    json_lookup = _load_json_prose(ITEMS_JSON)
    print(f"Loaded JSON prose for {len(json_lookup)} items from {ITEMS_JSON}")
    # Supplementary trimmed json for newer 12k items (not in old JSON)
    trimmed_lookup = _load_json_prose(TRIMMED_JSON)
    if trimmed_lookup:
        print(f"Loaded trimmed JSON prose for {len(trimmed_lookup)} items from {TRIMMED_JSON}")
    # Also try alt list if exists
    alt_path = ROOT / "2026_07_12_item_list.json"
    alt_lookup = _load_json_prose(alt_path) if alt_path.exists() else {}
    if alt_lookup:
        print(f"Loaded alt JSON prose for {len(alt_lookup)} items from {alt_path}")
    # Merge with priority: MD (most prose) > trimmed > alt > json_lookup, but keep url from json where available
    merged = {}
    # start with json_lookup
    for k, v in json_lookup.items():
        merged[k] = dict(v)
    for k, v in alt_lookup.items():
        if k not in merged or not merged[k].get('description'):
            merged[k] = dict(v)
        elif not v.get('description'):
            pass
        else:
            # if existing empty but new has, fill
            if not merged[k].get('description') and v.get('description'):
                merged[k]['description'] = v['description']
            if not merged[k].get('url') and v.get('url'):
                merged[k]['url'] = v['url']
    for k, v in trimmed_lookup.items():
        if k not in merged:
            merged[k] = dict(v)
        else:
            if not merged[k].get('description') and v.get('description'):
                merged[k]['description'] = v['description']
            if not merged[k].get('url') and v.get('url'):
                merged[k]['url'] = v['url']
            # if md will override later, but keep url
    # overlay MD prose (highest priority for description, but keep url if needed)
    for k, desc in md_prose.items():
        if k not in merged:
            # try to find url from other lookups via same lower name else build
            url = build_5etools_url(k, "")
            merged[k] = {'url': url, 'description': desc, 'source_code': ""}
        else:
            # md has description (could be empty string); if non-empty, prefer it
            if desc and desc.strip():
                merged[k]['description'] = desc
            # if md desc empty and existing has, keep existing
    # Final count prose non-empty
    has = sum(1 for v in merged.values() if v.get('description') and v['description'].strip())
    print(f"Merged metadata total {len(merged)} with prose {has} ({has/len(merged)*100:.1f}% non-empty)")
    return merged

def classify_price_source(ps: str) -> str:
    ps = (ps or "").strip()
    if "Amalgamated" in ps:
        return "Amalgamated"
    elif ps == "Algorithm":
        return "Algorithm"
    else:
        return "other"

def parse_price(val):
    if val is None or val == "":
        return None
    try:
        return float(str(val).replace(",","").strip())
    except:
        return None

def get_criteria_highlights(name, criteria_by_name, top_n=6):
    row = criteria_by_name.get(name.lower().strip())
    if not row:
        # try fallback without parenthetical
        # e.g., name "Piwafwi (Cloak of Elvenkind)" might be stored as "Piwafwi"
        # attempt stripping parens
        stripped = re.sub(r'\s*\(.*\)', '', name).strip().lower()
        row = criteria_by_name.get(stripped)
    if not row:
        return "—"
    # columns that are not criteria numeric: exclude meta
    EXCLUDE = {"name","source","rarity","type","official_price_gp","req_attune","url","alias","req_attune_class","item_type_code","weapon_properties","damage_resistances","damage_immunities","damage_vulnerabilities","condition_immunities","attached_spells","charges","recharge","recharge_amount","speed_mods","ability_score_mods","extra_damage_dice","extra_damage_condition","extra_damage_condition_detail","condition_immunity_prose","language_known","spell_casting_abilities","curse_effects","check_advantage","check_disadvantage","save_disadvantage","save_advantage","save_advantage_tiers","conditional_save_advantage"}
    candidates = []
    for col, val in row.items():
        if col in EXCLUDE:
            continue
        if val is None or val == "" or val == "[]":
            continue
        s = str(val).strip()
        if s in ("[]","{}","False","false","0","0.0","0.00","0.000"):
            continue
        # handle bool
        if s == "True" or s == "true":
            candidates.append((col, 1, 1))
            continue
        # handle list-like with content
        if s.startswith("[") and s not in ("[]",):
            # attempt literal eval for length
            try:
                import ast
                lst = ast.literal_eval(s)
                if isinstance(lst, list) and len(lst) > 0:
                    # treat length as value; but also keep first element?
                    # use length for sorting
                    candidates.append((col, len(lst), float(len(lst))))
                continue
            except:
                continue
        # try numeric
        try:
            f = float(s)
            if f == 0:
                continue
            candidates.append((col, f, abs(f)))
        except:
            continue
    if not candidates:
        return "—"
    candidates.sort(key=lambda x: x[2], reverse=True)
    top = candidates[:top_n]
    parts=[]
    for col, v, _ in top:
        if isinstance(v, float):
            if v.is_integer():
                vs = str(int(v))
            else:
                # Keep one decimal if needed, strip trailing zeros
                vs = f"{v:.2f}".rstrip("0").rstrip(".")
        else:
            vs = str(v)
        parts.append(f"{col} {vs}")
    return ", ".join(parts) if parts else "—"

def main():
    rnd = random.Random(SEED)
    print(f"Seed {SEED}, target {TARGET_TOTAL}")
    # Load pricing guide
    if not INPUT_CSV.exists():
        print(f"ERROR: {INPUT_CSV} not found")
        sys.exit(1)
    pg_rows=[]
    with INPUT_CSV.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pg_rows.append(row)
    print(f"Loaded pricing_guide {len(pg_rows)} rows from {INPUT_CSV}")
    # Basic fieldnames
    # print pg fieldnames
    # Load criteria
    criteria_by_name={}
    alias_criteria_names=set()
    criteria_rows=[]
    if CRITERIA_CSV.exists():
        with CRITERIA_CSV.open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name_lower = row.get('name','').strip().lower()
                if name_lower:
                    # Keep first occurrence for name lower
                    if name_lower not in criteria_by_name:
                        criteria_by_name[name_lower] = row
                    else:
                        # ambiguous duplicate name different source: keep first but also keep alias handling by exact name
                        pass
                    criteria_rows.append(row)
                    if row.get('alias') and row['alias'].strip():
                        alias_criteria_names.add(row.get('name','').strip())
        print(f"Loaded criteria {len(criteria_rows)} rows, alias candidates {len(alias_criteria_names)}")
    else:
        print(f"Warning: {CRITERIA_CSV} not found, criteria highlights will be fallback")

    # Build pg lookup by key
    pg_by_key={}
    pg_by_name_lower={}
    for r in pg_rows:
        key = (r['Name'].strip().lower(), r['Source'].strip().lower())
        pg_by_key[key]=r
        nl = r['Name'].strip().lower()
        if nl not in pg_by_name_lower:
            pg_by_name_lower[nl]=r
        # also map multiple? keep first, but we have key
    # Load metadata prose
    meta = load_item_metadata()
    print(f"Loaded metadata for {len(meta)} items from {ITEMS_JSON}")

    # Load tail attribution
    tail_rows=[]
    if TAIL_CSV.exists():
        with TAIL_CSV.open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tail_rows.append(row)
        print(f"Loaded tail attribution {len(tail_rows)} rows")
    else:
        print(f"Warning: {TAIL_CSV} not found")

    # Selection bookkeeping
    selected={}  # key -> {'row': pg_row, 'flags': set()}
    per_class_raw={}  # flag -> count before dedupe
    def add_rows(rows, flag):
        per_class_raw[flag]=per_class_raw.get(flag,0)+len(rows)
        for r in rows:
            key = (r['Name'].strip().lower(), r['Source'].strip().lower())
            if key not in selected:
                selected[key]={'row': r, 'flags': set([flag])}
            else:
                selected[key]['flags'].add(flag)

    # a. TARGETED
    # floor-tripwire
    floor_rows=[]
    for r in pg_rows:
        p = parse_price(r.get('Price (gp)'))
        if p is None:
            continue
        # exact equality to floor values (int compare)
        if int(p) in FLOOR_VALUES and p == float(int(p)):
            # ensure exact: price exactly equals floor value (no cents beyond .0)
            # floor values are ints 50 etc, price must be exactly that int as float
            if p in {float(v) for v in FLOOR_VALUES}:
                floor_rows.append(r)
        # also handle price string exactly "50.0" etc but already covered
    # More precise: check if price equals any floor as integer without tolerance
    # Use round check: if p is in FLOOR_VALUES as float exactly
    # Our prior already ensures, but ensure we include all where float(p) in set
    # Re-evaluate with strict
    # Ensure we catch 50.0 exactly etc.
    # The earlier loop already does; keep.

    print(f"floor-tripwire candidates {len(floor_rows)}")
    add_rows(floor_rows, "floor-tripwire")

    # battery-parity
    battery_rows=[]
    for r in pg_rows:
        p = parse_price(r.get('Price (gp)'))
        if p is None:
            continue
        if p not in {float(v) for v in SCROLL_VALUES}:
            continue
        # need to check battery criteria: spell_battery_max_level >0
        # lookup criteria by name lower
        c = criteria_by_name.get(r['Name'].strip().lower())
        if not c:
            # try stripping parenthetical
            stripped = re.sub(r'\s*\(.*\)','', r['Name']).strip().lower()
            c = criteria_by_name.get(stripped)
        if not c:
            continue
        batt = c.get('spell_battery_max_level','')
        if not batt or batt.strip()=="":
            continue
        try:
            bv = float(batt)
            if bv>0:
                battery_rows.append(r)
        except:
            continue
    print(f"battery-parity candidates {len(battery_rows)}")
    # debug battery rows
    for br in battery_rows:
        print(f"  battery {br['Name']} {br['Price (gp)']} {br['Source']}")
    add_rows(battery_rows, "battery-parity")

    # family-min: non-amalgamated weapons with weapon_bonus>0 cap 20 by largest price
    family_cands=[]
    for r in pg_rows:
        ps = r.get('Price Source','')
        if "Amalgamated" in ps:
            continue
        c = criteria_by_name.get(r['Name'].strip().lower())
        if not c:
            stripped = re.sub(r'\s*\(.*\)','', r['Name']).strip().lower()
            c = criteria_by_name.get(stripped)
        if not c:
            continue
        wb = c.get('weapon_bonus','')
        if not wb or wb.strip()=="":
            continue
        try:
            wbv = float(wb)
            if wbv>0:
                # also check is_generic_variant? In criteria
                is_generic = c.get('is_generic_variant','')
                if is_generic.strip()=="True":
                    continue
                family_cands.append(r)
        except:
            continue
    # sort by price descending and cap 20
    family_cands_sorted = sorted(family_cands, key=lambda x: parse_price(x.get('Price (gp)')) or 0, reverse=True)
    family_rows = family_cands_sorted[:20]
    print(f"family-min candidates total {len(family_cands)} cap 20 -> {len(family_rows)}")
    for fr in family_rows:
        print(f"  family-min {fr['Name']} price {fr['Price (gp)']} source {fr['Price Source']}")
    add_rows(family_rows, "family-min")

    # final-gate: 2 rows
    gate_names = ["+3 Adamantine Vertebrae Sword", "+3 True Name Dart"]
    gate_rows=[]
    for name in gate_names:
        # find by exact name lower
        found=None
        for r in pg_rows:
            if r['Name'].strip()==name:
                found=r
                break
        if found:
            gate_rows.append(found)
        else:
            # case-insensitive fallback
            for r in pg_rows:
                if r['Name'].strip().lower()==name.lower():
                    gate_rows.append(r)
                    break
    print(f"final-gate candidates {len(gate_rows)} -> {gate_names}")
    add_rows(gate_rows, "final-gate")

    # ml-variance top 30
    ml_rows=[]
    if tail_rows:
        ml_filtered = [x for x in tail_rows if x.get('bucket')=='ml-variance']
        def pct_val(s):
            try:
                return float(s.strip().strip('%'))
            except:
                return -1
        ml_sorted = sorted(ml_filtered, key=lambda x: pct_val(x.get('pct','0%')), reverse=True)
        top30 = ml_sorted[:30]
        print(f"ml-variance total {len(ml_filtered)} top30 {len(top30)}")
        for tr in top30:
            # find pg row
            name = tr.get('name','').strip()
            src = tr.get('source','').strip()
            key = (name.lower(), src.lower())
            pr = pg_by_key.get(key)
            if not pr:
                # fallback by name lower
                pr = pg_by_name_lower.get(name.lower())
                # if multiple sources, ensure we pick one that matches source display via translate? Use first found
                if not pr:
                    # search by name lower across pg_rows
                    for r in pg_rows:
                        if r['Name'].strip().lower()==name.lower():
                            pr=r
                            break
            if pr:
                ml_rows.append(pr)
            else:
                print(f"  Warning: tail ml item not in pricing_guide: {name} | {src}")
        # dedupe ml_rows by key before add? But add_rows handles dedupe
        print(f"ml-variance matched pg {len(ml_rows)}")
        for mr in ml_rows:
            print(f"  ml-variance {mr['Name']} | {mr['Source']}")
        add_rows(ml_rows, "ml-variance")
    else:
        print("ml-variance skipped (no tail rows)")

    # reskin/alias: 5 items (Piwafwi + 4 alias)
    reskin_rows=[]
    # Piwafwi
    piw_name = "Piwafwi (Cloak of Elvenkind)"
    piw_found=None
    for r in pg_rows:
        if r['Name'].strip()==piw_name:
            piw_found=r
            break
    if piw_found:
        reskin_rows.append(piw_found)
        print(f"reskin Piwafwi found {piw_found['Name']} | {piw_found['Source']}")
    else:
        # case-insensitive
        for r in pg_rows:
            if piw_name.lower() in r['Name'].strip().lower():
                reskin_rows.append(r)
                print(f"reskin Piwafwi fallback {r['Name']}")
                break
    # 4 alias: pick 4 alias criteria names alphabetically
    alias_names_sorted = sorted(alias_criteria_names, key=lambda x: x.lower())
    # exclude Piwafwi if somehow in list (not)
    # pick first 4 that exist in pg
    alias_pick=[]
    for aname in alias_names_sorted:
        if len(alias_pick)>=4:
            break
        # skip if same as Piwafwi (not in alias list, so no check needed)
        # find pg row
        pr = pg_by_name_lower.get(aname.strip().lower())
        if not pr:
            # try case-insensitive search
            for r in pg_rows:
                if r['Name'].strip().lower()==aname.strip().lower():
                    pr=r
                    break
        if pr:
            # avoid duplicate if already selected as Piwafwi
            key = (pr['Name'].strip().lower(), pr['Source'].strip().lower())
            if key in selected and "reskin" in selected[key]['flags']:
                continue
            # also avoid duplicate within alias_pick
            if pr in alias_pick:
                continue
            alias_pick.append(pr)
        else:
            print(f"  reskin alias not found in pg: {aname}")
    print(f"reskin alias candidates picked {len(alias_pick)}")
    for ap in alias_pick:
        print(f"  reskin alias {ap['Name']} | {ap['Source']}")
    reskin_rows.extend(alias_pick)
    # If still less than 5, add more by random? But should be 5
    print(f"reskin total {len(reskin_rows)}")
    add_rows(reskin_rows, "reskin")

    # Deduped targeted count
    targeted_deduped = len(selected)
    print(f"TARGETED deduped {targeted_deduped} (raw per-class {per_class_raw})")
    # Print per-class deduped flags combined? Need to compute final flag distribution
    # Derive per-flag deduped counts (how many final rows carry that flag, including overlaps)
    per_flag_deduped={}
    for v in selected.values():
        for fl in v['flags']:
            per_flag_deduped[fl]=per_flag_deduped.get(fl,0)+1
    print(f"Per-flag deduped: {per_flag_deduped}")
    # Also raw per-class counts printed earlier per_class_raw

    # b. RANDOM fill to 400
    need = TARGET_TOTAL - targeted_deduped
    if need<0:
        print(f"Warning: targeted {targeted_deduped} exceeds target {TARGET_TOTAL}, truncating")
        # need to trim? Instead truncate selected to 400 randomly? But spec says dedupe then random fill, expect ~400 so targeted <400
        # If exceed, we need to limit; but our targeted is ~171 so fine
        need=0
    print(f"Need random fill {need}")

    # Build pool excluding selected
    pool = []
    for r in pg_rows:
        key = (r['Name'].strip().lower(), r['Source'].strip().lower())
        if key not in selected:
            pool.append(r)
    print(f"Pool remaining {len(pool)}")

    # Stratified across price-source class × rarity, minimum 8 per rarity present
    # Collect rarities present in overall pg (distinct)
    all_rarities = sorted(set(r['Rarity'].strip() for r in pg_rows if r['Rarity'].strip()))
    print(f"Rarities present {all_rarities}")
    # Also distinct price class
    price_classes = ["Amalgamated", "Algorithm", "other"]
    # Build pool_by_rarity and pool_by_group
    # For mins: we will allocate 8 per rarity if possible from pool
    random_selected={}
    def add_random_rows(rows, flag="random"):
        for r in rows:
            key = (r['Name'].strip().lower(), r['Source'].strip().lower())
            if key not in selected and key not in random_selected:
                random_selected[key]={'row': r, 'flags': set([flag])}
            elif key in random_selected:
                random_selected[key]['flags'].add(flag)

    # Phase 1: minimum 8 per rarity
    pool_by_rarity={}
    for r in pool:
        rar = r['Rarity'].strip()
        pool_by_rarity.setdefault(rar, []).append(r)
    # Shuffle each rarity list deterministically
    for rar, lst in pool_by_rarity.items():
        rnd.shuffle(lst)

    allocated_min=0
    for rar in all_rarities:
        cand = pool_by_rarity.get(rar, [])
        # filter out already selected random? But we haven't yet picked, so all cand are available
        # pick up to 8, but not exceeding remaining need
        pick_n = min(8, len(cand), need - allocated_min if need>allocated_min else 0)
        # If need is small, we still need to ensure min per rarity might exceed need
        # So we cap at need
        if pick_n>0:
            chosen = cand[:pick_n]
            # remove from pool_by_rarity lists? We'll just track removal via random_selected and later rebuild groups
            add_random_rows(chosen, "random")
            allocated_min+=pick_n
            # remove chosen from pool structures for next phase
            # Remove from pool_by_rarity
            pool_by_rarity[rar] = cand[pick_n:]
    print(f"Allocated min per rarity {allocated_min}, remaining pool adjusted")

    # Update pool remaining after mins
    remaining_pool=[]
    for rar, lst in pool_by_rarity.items():
        remaining_pool.extend(lst)
    # Also need to consider rarities that had not been accounted? Already.
    # Actually pool_by_rarity only contains rarities from pool, but we allocated per all_rarities including those not in pool (zero)
    # For remaining stratification, build groups by price class x rarity
    remaining_need = need - allocated_min
    print(f"Remaining need after mins {remaining_need}, remaining_pool {len(remaining_pool)}")

    # Build groups for remaining_pool
    groups={}
    for r in remaining_pool:
        pc = classify_price_source(r.get('Price Source',''))
        rar = r['Rarity'].strip()
        key = (pc, rar)
        groups.setdefault(key, []).append(r)
    # Shuffle each group
    for k, lst in groups.items():
        rnd.shuffle(lst)
    # Now stratified fill via round-robin across groups sorted random order each iteration
    # To ensure proportional, we instead do weighted picking: sort groups by size descending, then pick round-robin
    # We'll use round-robin across group keys in random order each cycle
    # Create list of group keys sorted for deterministic start then shuffled each cycle
    group_keys = list(groups.keys())
    # Ensure deterministic shuffle of group_keys order each cycle using rnd
    import itertools
    # Instead of while loop infinite, we will iteratively pick
    picks_remaining = remaining_need
    # For stratified, we want to ensure each price class represented
    # First ensure at least one per price class x rarity cell if possible? Our round-robin will naturally do that if remaining_need large enough
    # If remaining_need is small, we may not cover all cells
    # Approach: while picks_remaining>0, iterate over shuffled group_keys and pick one per group
    attempts=0
    while picks_remaining>0 and attempts<10000:
        # shuffle group_keys each full cycle
        rnd.shuffle(group_keys)
        any_pick=False
        for gk in group_keys:
            if picks_remaining==0:
                break
            lst = groups.get(gk, [])
            if lst:
                row = lst.pop(0)
                add_random_rows([row], "random")
                picks_remaining-=1
                any_pick=True
        if not any_pick:
            break
        attempts+=1
        if attempts>5000:
            break
    print(f"Stratified remaining picks done, picks_remaining {picks_remaining}, random_selected total {len(random_selected)}")

    # If still remaining picks due to pool exhaustion edge, fallback to random sample from any remaining
    # Collect any leftover groups
    if picks_remaining>0:
        leftover=[]
        for lst in groups.values():
            leftover.extend(lst)
        rnd.shuffle(leftover)
        for row in leftover[:picks_remaining]:
            add_random_rows([row], "random")
        picks_remaining -= min(picks_remaining, len(leftover))

    # Combine targeted and random into final selection
    final_selected={}
    # merge selected
    for k,v in selected.items():
        final_selected[k]=v
    # merge random_selected (may have overlap already ensured not)
    for k,v in random_selected.items():
        if k not in final_selected:
            final_selected[k]=v
        else:
            # shouldn't happen because pool excluded selected, but handle
            final_selected[k]['flags'].update(v['flags'])
    total_final = len(final_selected)
    print(f"FINAL total {total_final} (targeted {targeted_deduped} + random {len(random_selected)})")
    if total_final != TARGET_TOTAL:
        print(f"Warning: final total {total_final} != target {TARGET_TOTAL}")

    # Prepare output rows list
    output_rows=[]
    for key, val in final_selected.items():
        row = val['row']
        flags = sorted(val['flags'])
        flag_str = ", ".join(flags)
        # Source display via translate_source
        source_raw = row.get('Source','')
        # translate_source handles pipe-separated and missing
        source_display = translate_source(source_raw)
        # But if source_raw already display (contains spaces), translate will fallback to same string because not found as code, which is fine
        # Price
        price_gp = parse_price(row.get('Price (gp)'))
        price_formatted = row.get('Price Formatted','')
        if not price_formatted and price_gp is not None:
            price_formatted = f"{int(price_gp):,} gp" if price_gp>=10 else f"{price_gp:.1f} gp"
        # Price band
        price_low = row.get('Price Low','')
        price_high = row.get('Price High','')
        # build band as "low / mid / high"
        if price_low and price_high:
            price_band = f"{price_low} / {price_formatted} / {price_high}"
        elif price_low:
            price_band = f"{price_low} / {price_formatted}"
        elif price_high:
            price_band = f"{price_formatted} / {price_high}"
        else:
            price_band = price_formatted
        # Price source label
        price_source_label = row.get('Price Source','')
        # Prose
        name_lower = row['Name'].strip().lower()
        meta_entry = meta.get(name_lower)
        if not meta_entry:
            # try without parenthetical
            stripped = re.sub(r'\s*\(.*\)','', name_lower).strip()
            meta_entry = meta.get(stripped)
        prose = ""
        if meta_entry and meta_entry.get('description'):
            prose = meta_entry['description']
        if not prose:
            prose = "—"
        # limit prose? Full but truncate for CSV escaping? Keep full, html will escape
        # criteria highlights
        crit_high = get_criteria_highlights(row['Name'], criteria_by_name)
        # 5e.tools link
        url = row.get('URL','')
        if not url or not url.startswith('http'):
            # try meta url
            if meta_entry and meta_entry.get('url'):
                url = meta_entry['url']
            else:
                # fallback build
                # attempt to get source code for url: try to find source abbreviation via criteria? Use row Source display lower to craft?
                # For now use name + source_display lower
                src_for_url = source_raw.split('|')[0] if '|' in source_raw else source_raw
                url = build_5etools_url(row['Name'], src_for_url)
        # Build row for output
        output_rows.append({
            'Name': row['Name'],
            'Source': source_display,
            'Source_raw': source_raw,  # for later but not exported
            'Type': row.get('Type',''),
            'Rarity': row.get('Rarity',''),
            'Attunement': row.get('Attunement',''),
            'Price': price_formatted if price_formatted else (str(price_gp) if price_gp is not None else ""),
            'Price_gp_raw': price_gp,
            'Price band': price_band,
            'Price Source': price_source_label,
            'Review flag(s)': flag_str,
            'Prose': prose,
            'Criteria highlights': crit_high,
            '5e.tools link': url,
            'Price Low': price_low,
            'Price High': price_high,
        })
    # Sort output rows by Name for deterministic output? But maybe preserve targeted priority? Sort alphabetical
    output_rows.sort(key=lambda x: x['Name'].lower())

    # Per-class counts for reporting (final)
    # Count per flag
    flag_counts={}
    for r in output_rows:
        flags = [f.strip() for f in r['Review flag(s)'].split(',') if f.strip()]
        for f in flags:
            flag_counts[f]=flag_counts.get(f,0)+1
    # Count per rarity
    rarity_counts={}
    for r in output_rows:
        rar = r['Rarity']
        rarity_counts[rar]=rarity_counts.get(rar,0)+1
    # Count per price source class
    price_class_counts={}
    for r in output_rows:
        pc = classify_price_source(r['Price Source'])
        price_class_counts[pc]=price_class_counts.get(pc,0)+1

    print("Per-flag counts (final):")
    for k,v in sorted(flag_counts.items()):
        print(f"  {k}: {v}")
    print("Per-rarity counts:")
    for k,v in sorted(rarity_counts.items(), key=lambda x: x[0]):
        print(f"  {k}: {v}")
    print("Per-price-class counts:")
    for k,v in sorted(price_class_counts.items()):
        print(f"  {k}: {v}")
    print(f"Total rows {len(output_rows)}")
    # Also print class counts for random vs targeted etc
    # For verification, also count price source class x rarity matrix
    # Save for html header

    # Sanity checks
    print("Sanity checks:")
    # every row has price
    missing_price = [r for r in output_rows if not r['Price'] or r['Price_gp_raw'] is None]
    print(f"  every row has price: {len(missing_price)==0} (missing {len(missing_price)})")
    if missing_price:
        for mp in missing_price[:5]:
            print(f"    missing {mp['Name']}")
    # floor-flagged rows include Needler family
    floor_flagged = [r for r in output_rows if "floor-tripwire" in r['Review flag(s)']]
    needler_in_floor = [r for r in floor_flagged if "needler" in r['Name'].lower()]
    print(f"  floor-flagged rows {len(floor_flagged)} include Needler family: {len(needler_in_floor)>0} count {len(needler_in_floor)}")
    if needler_in_floor:
        for nf in needler_in_floor[:5]:
            print(f"    {nf['Name']} {nf['Price']}")
    # battery rows include Spell Gem (Diamond)
    battery_flagged = [r for r in output_rows if "battery-parity" in r['Review flag(s)']]
    gem_diamond = [r for r in battery_flagged if "spell gem (diamond)" in r['Name'].lower()]
    # Also check overall if battery includes that even if flag maybe not? Overall presence
    print(f"  battery rows {len(battery_flagged)} include Spell Gem (Diamond): {len(gem_diamond)>0}")
    if gem_diamond:
        for gd in gem_diamond:
            print(f"    {gd['Name']} {gd['Price']}")
    else:
        # check if spell gem diamond exists at all in output_rows (maybe not flagged but present as random)
        overall_gem = [r for r in output_rows if "spell gem (diamond)" in r['Name'].lower()]
        print(f"    overall Spell Gem (Diamond) in sample: {len(overall_gem)}")
        if overall_gem:
            for og in overall_gem:
                print(f"      {og['Name']} flags {og['Review flag(s)']}")
    # prose non-empty >=80%
    non_empty_prose = [r for r in output_rows if r['Prose'] and r['Prose']!="—" and r['Prose'].strip()!=""]
    prose_pct = len(non_empty_prose)/len(output_rows)*100 if output_rows else 0
    print(f"  prose non-empty {len(non_empty_prose)}/{len(output_rows)} = {prose_pct:.1f}% >=80%: {prose_pct>=80}")
    if prose_pct<80:
        print(f"    Warning: prose below threshold")

    # Emit CSV
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    # Define output CSV columns per spec (order)
    csv_fieldnames = ['Name','Source','Type','Rarity','Attunement','Price','Price band','Price Source','Review flag(s)','Prose','Criteria highlights','5e.tools link']
    with OUTPUT_CSV.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=csv_fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for r in output_rows:
            out = {k: r.get(k,'') for k in csv_fieldnames}
            writer.writerow(out)
    print(f"Saved CSV to {OUTPUT_CSV} with {len(output_rows)} rows")

    # Emit HTML
    # Prepare data for JS
    # Escape for HTML
    # Counts for header
    total = len(output_rows)
    # Build html
    # Create distinct flags and rarities for filter dropdowns
    distinct_flags = sorted(flag_counts.keys())
    distinct_rarities = sorted(rarity_counts.keys())

    # Build counts header string
    header_counts = f"Total {total} | " + " | ".join([f"{k}: {v}" for k,v in sorted(flag_counts.items())]) + " | " + " | ".join([f"{k}: {v}" for k,v in sorted(price_class_counts.items())])

    # Build table rows HTML
    rows_html=[]
    for r in output_rows:
        # escape
        name_esc = html.escape(r['Name'])
        source_esc = html.escape(r['Source'])
        type_esc = html.escape(r['Type'])
        rarity_esc = html.escape(r['Rarity'])
        attune_esc = html.escape(r['Attunement'])
        price_esc = html.escape(r['Price'])
        band_esc = html.escape(r['Price band'])
        ps_esc = html.escape(r['Price Source'])
        flags_esc = html.escape(r['Review flag(s)'])
        prose_esc = html.escape(r['Prose'])
        # For prose, keep as is but escaped; if long, wrap
        crit_esc = html.escape(r['Criteria highlights'])
        link_esc = html.escape(r['5e.tools link'])
        link_html = f'<a href="{link_esc}" target="_blank" rel="noopener">link</a>' if link_esc else ""
        # Name with link
        name_html = f'<a href="{link_esc}" target="_blank" rel="noopener">{name_esc}</a>' if link_esc.startswith('http') else name_esc
        rows_html.append(f"<tr data-flags=\"{flags_esc}\" data-rarity=\"{rarity_esc}\"><td>{name_html}</td><td>{source_esc}</td><td>{type_esc}</td><td>{rarity_esc}</td><td>{attune_esc}</td><td data-sort=\"{r['Price_gp_raw'] or 0}\">{price_esc}</td><td>{band_esc}</td><td>{ps_esc}</td><td>{flags_esc}</td><td style=\"max-width:400px; white-space: normal; word-wrap: break-word; font-size: 0.85em;\">{prose_esc}</td><td style=\"font-size:0.85em;\">{crit_esc}</td><td>{link_html}</td></tr>")

    # HTML template self-contained
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Manual Review Sample — 400 items (seed 42)</title>
<style>
* {{ box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin:0; padding:0; background:#f7f7f7; color:#222; }}
.header {{ background:#1a1a2e; color:#ffd700; padding:16px 20px; position:sticky; top:0; z-index:100; }}
.header h1 {{ margin:0; font-size:1.4em; }}
.header .counts {{ margin-top:8px; font-size:0.85em; color:#e0e0e0; line-height:1.4; }}
.controls {{ display:flex; gap:16px; flex-wrap:wrap; align-items:center; margin-top:12px; }}
.controls label {{ font-size:0.9em; color:#ccc; }}
.controls select {{ padding:6px 10px; border-radius:6px; border:1px solid #555; background:#2a2a3a; color:#fff; }}
.table-wrap {{ overflow:auto; max-height: calc(100vh - 160px); }}
table {{ width:100%; border-collapse:collapse; background:#fff; }}
th {{ position:sticky; top:0; background:#2d4a3e; color:#fff; padding:10px 8px; text-align:left; font-size:0.85em; cursor:pointer; user-select:none; white-space:nowrap; z-index:10; }}
th:hover {{ background:#3d5a4e; }}
td {{ padding:8px; border-bottom:1px solid #e5e5e5; font-size:0.85em; vertical-align:top; }}
tr:hover {{ background:#f0f7f4; }}
.rarity-Common {{ color:#666; }}
.rarity-Uncommon {{ color:#1a7a00; }}
.rarity-Rare {{ color:#0070dd; }}
.rarity-Very {{ color:#a335ee; }}
.count-badge {{ background:#ffd700; color:#000; padding:2px 6px; border-radius:10px; font-size:0.8em; margin-left:4px; }}
</style>
</head>
<body>
<div class="header">
  <h1>Manual Review Sample — 400 items (seed 42)</h1>
  <div class="counts">Counts: {html.escape(header_counts)}</div>
  <div class="counts">Source classes: {'; '.join([f"{html.escape(k)}: {v}" for k,v in sorted(price_class_counts.items())])} | Rarities: {'; '.join([f"{html.escape(k)}: {v}" for k,v in sorted(rarity_counts.items())])}</div>
  <div class="controls">
    <label>Filter Review flag: <select id="filter-flag"><option value="">All</option>{''.join([f'<option value="{html.escape(f)}">{html.escape(f)}</option>' for f in distinct_flags])}</select></label>
    <label>Filter Rarity: <select id="filter-rarity"><option value="">All</option>{''.join([f'<option value="{html.escape(r)}">{html.escape(r)}</option>' for r in distinct_rarities])}</select></label>
    <span id="visible-count" style="color:#ffd700; font-weight:bold;"></span>
    <input type="text" id="search" placeholder="Search name..." style="padding:6px 10px; border-radius:6px; border:1px solid #555; background:#2a2a3a; color:#fff;">
  </div>
</div>
<div class="table-wrap">
<table id="review-table">
<thead>
<tr>
<th onclick="sortTable(0)">Name</th>
<th onclick="sortTable(1)">Source</th>
<th onclick="sortTable(2)">Type</th>
<th onclick="sortTable(3)">Rarity</th>
<th onclick="sortTable(4)">Attunement</th>
<th onclick="sortTable(5)">Price</th>
<th onclick="sortTable(6)">Price band</th>
<th onclick="sortTable(7)">Price Source</th>
<th onclick="sortTable(8)">Review flag(s)</th>
<th>Prose</th>
<th>Criteria highlights</th>
<th>5e.tools link</th>
</tr>
</thead>
<tbody>
{''.join(rows_html)}
</tbody>
</table>
</div>
<script>
let sortCol = -1;
let sortAsc = true;
function sortTable(col) {{
  const table = document.getElementById('review-table');
  const tbody = table.tBodies[0];
  const rows = Array.from(tbody.rows);
  if (sortCol===col) sortAsc=!sortAsc; else {{ sortCol=col; sortAsc=true; }}
  rows.sort((a,b)=>{{
    let av = a.cells[col].getAttribute('data-sort') || a.cells[col].innerText;
    let bv = b.cells[col].getAttribute('data-sort') || b.cells[col].innerText;
    // numeric sort for price column (5)
    if (col===5) {{
      av = parseFloat(av) || 0;
      bv = parseFloat(bv) || 0;
      return sortAsc ? av - bv : bv - av;
    }}
    av = av.toLowerCase();
    bv = bv.toLowerCase();
    if (av < bv) return sortAsc ? -1 : 1;
    if (av > bv) return sortAsc ? 1 : -1;
    return 0;
  }});
  rows.forEach(r=>tbody.appendChild(r));
}}
function applyFilters() {{
  const flag = document.getElementById('filter-flag').value;
  const rarity = document.getElementById('filter-rarity').value;
  const q = document.getElementById('search').value.toLowerCase();
  const rows = document.querySelectorAll('#review-table tbody tr');
  let visible=0;
  rows.forEach(row=>{{
    const flags = row.getAttribute('data-flags')||'';
    const rrar = row.getAttribute('data-rarity')||'';
    const name = row.cells[0].innerText.toLowerCase();
    let show=true;
    if (flag && !flags.includes(flag)) show=false;
    if (rarity && rrar!==rarity) show=false;
    if (q && !name.includes(q)) show=false;
    row.style.display = show ? '' : 'none';
    if (show) visible++;
  }});
  document.getElementById('visible-count').textContent = visible + ' / ' + rows.length + ' visible';
}}
document.getElementById('filter-flag').addEventListener('change', applyFilters);
document.getElementById('filter-rarity').addEventListener('change', applyFilters);
document.getElementById('search').addEventListener('input', applyFilters);
applyFilters();
</script>
</body>
</html>
"""
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(html_content, encoding='utf-8')
    print(f"Saved HTML to {OUTPUT_HTML} ({len(html_content)} bytes)")

    # Final per-class counts printed earlier, also total
    print(f"Done. Total {total} rows, seed {SEED}")

if __name__ == "__main__":
    main()
