# pricing_guide_v2-7xw — Manual Review Sample (Wave 1)

## Objective
Build user's manual-review sample (7xw wave 1) — 400 items stratified + targeted classes (seed 42) for human review; verify pricing logic across floor tripwires, battery parity, family-min, final-gate, ml-variance, and reskin alias classes.

## Touch set
- `scripts/reports/build_manual_review_sample.py` — selector script (inputs: `output/pricing_guide.csv` 11941 rows + metadata JSON `items-sublist-data.json`/`trimmed_5etools_list.json`/`items-sublist.md` via `src/prose_loader.py` + `src/source_names.py`; bounded read of `scripts/11_generate_html.py` first 200 lines; seed 42; dedupe targeted first then stratified random fill; outputs `reports/manual_review_sample.html` self-contained + `reports/manual_review_sample.csv`)
- `reports/manual_review_sample.html` — self-contained HTML, sticky header, sortable-by-click, filter dropdowns for Review flag + Rarity, counts in header, no CDN deps
- `reports/manual_review_sample.csv` — same 400 rows, columns: Name, Source, Type, Rarity, Attunement, Price, Price band (low/mid/high), Price Source, Review flag(s), Prose (full, fallback "—"), Criteria highlights (top ~6 non-zero by abs, humanized), 5e.tools link

## Decisions
- Floor-tripwire: exact price in {50,200,1000,8000,50000} → 108 rows flagged floor-tripwire
- Battery-parity: exact scroll price {25,75,150,300,1500,3000,8500,20000,45000,100000} with `spell_battery_max_level`>0 via `data/processed/items_criteria.csv` → 6 rows (Cottage Chest, Jade Serpent Staff, Mudslick Tower, Spell Gem (Diamond), Spell Gem (Ruby), Unknown Elixir)
- Family-min: non-Amalgamated weapons with `weapon_bonus`>0, `is_generic_variant`!=True, cap 20 by largest price → 20 rows (Wand of Orcus 985k … Silverwind 418k)
- Final-gate: +3 Adamantine Vertebrae Sword, +3 True Name Dart → 2 rows
- ML-variance: top 30 by pct from `reports/tail_attribution_sej913.csv` bucket ml-variance → 30 rows (Book of Secrets 10000% … Volcanic Boots 102%)
- Reskin: Piwafwi (Cloak of Elvenkind) + 4 alias sorted alphabetically (Cannith's Marvelous Miniatures, Cloak of Passage, Cloak of Shadows, Crusader's Shortsword) → 5 rows
- Dedupe targeted → 170 distinct (raw per-class 108+6+20+2+30+5=171, 1 overlap final-gate floor)
- Random fill to 400: stratified across price-source class (Amalgamated/Algorithm/other) × rarity, minimum 8 per rarity present (10 rarities → 76 allocated), remaining 154 via round-robin across price-class×rarity groups, seed 42 → 230 random (76 mins +154 stratified) → total 400
- Prose: hybrid loader — `src/prose_loader.load_prose_descriptions(items-sublist.md)` 9394 + JSON loader pattern from 11 (`items-sublist-data.json` 9422) + `trimmed_5etools_list.json` 12241; merged with priority MD>trimmed>alt>json; url via CSV URL or `build_5etools_url`; criteria highlights top 6 numeric by abs
- Price band: `Price Low / Price Formatted / Price High` from CSV
- HTML: sticky header (position:sticky top:0), sortable via JS `sortTable(col)` (numeric for Price), filters for Review flag and Rarity, live visible count

## Blockers
- None

## Status
- **Sample generated** 2026-09-02 seed 42: `reports/manual_review_sample.html` (710832 bytes) + `reports/manual_review_sample.csv` (400 rows) — **awaiting user review**
- Per-flag final counts: floor-tripwire 108, battery-parity 6, family-min 20, final-gate 2, ml-variance 30, reskin 5, random 230
- Per-rarity: Artifact 37, Common 43, Legendary 39, Mundane 106, Rare 39, Uncommon 58, Unknown 4, Unknown Magic 19, Varies 12, Very Rare 43
- Per-price-class: Algorithm 208 (52.0%), Amalgamated 53 (13.25%), other 139 (34.75%)
- Total 400 rows
- Sanity checks (run output):
  - every row has price: true (0 missing)
  - floor-flagged includes Needler family: true (10: +1 Black Ice Repeater Needler, +1 True Name Repeater Needler, +2 True Name Repeater Needler, +3 Adamantine Repeater Needler, +3 True Name Repeater Needler, Drow +1/+2/+3 Repeater Needler, Monster Hunter +3)
  - battery includes Spell Gem (Diamond): true (Spell Gem (Diamond) 100,000 gp, Legendary)
  - prose non-empty 370/400 =92.5% >=80%: true (hybrid MD+trimmed; MD alone 60.5%, trimmed alone 73.5%, union 92.5%)
- Run: `python3 scripts/reports/build_manual_review_sample.py` (seed 42) — logged above
- Next: user manual review of 400 items via `reports/manual_review_sample.html`

