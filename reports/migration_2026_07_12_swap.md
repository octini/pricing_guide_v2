# Migration 2026-07-12 Swap — Hop B (Execution Dispatch)

**Date:** 2026-09-01
**Canonical swap:** `trimmed_5etools_list.json/.md` now contain 12,241 curated 2026_07_12 items, byte-identical to `data/canonical_2026_07_12_curated.*`.

## 1. Decisions Record (User Approvals)

| Approval date | Decision | Detail | Source |
|---|---|---|---|
| 2026-09-01 | 26 new-only sources IN | All 26 sources unique to curated 2026 set approved scope: 24GriffonsSaddlebag1 (897), GriffonsSaddlebag2 (647), ObojimaTallGrass (616), HelianasGuidetoMonsterHunting (547), CallfromtheDeep (483), IllriggerRevised (437), GrimHollowCG24 (322), GrimHollowPG24 (119), GrimHollowLairsEtharis (118), CrookedMoon24 (104), BookOfEbonTides (106), HumblewoodTales (62), TalDoreiCampaignSettingReborn (133), Pugilist2024 (41), HumblewoodCampaignSetting (13), OneShotWondersHolidayPack (14), FleeMortals (19), ValdaGunslinger (8), ValdaPlayerPack (5), WSC (2), RHW (2), ToB1-2023 (3), CthulhuTorchlight (7), TalesFromTheShadows (18), GrimHollowPlayerPack (12), plus aggregated expansions (XDMG +1084, FTD +264, etc.). Total curated sources 88 vs canonical 66. | `reports/curation_preflight_2026_07_12.md` § Top source expansions / New-only sources |
| 2026-09-01 | 40 fantasy explosives/alchemical ordnance IN | 40 items (Blasting Powder, Bomb, Dynamite, Explosive Seed, Fire Bomb, Gluebomb, Smoke Bomb, Smoke Grenade, etc.) kept pending human confirmation — now confirmed IN. | Same § Potential scope review items |
| 2026-09-01 | 761 Renaissance firearms/source-specific firearms IN | 761 items requiring source-specific handling kept source-specific (e.g. Blunderbuss ×3 — GrimHollowPG24 / HelianasGuidetoMonsterHunting / ValdaGunslinger; Musket ×3; Pistol ×3; Blackpowder Pistol/Rifle, Dragon Pistol/Rifle). Classification: 12 groups `review/keep-separate — source-specific firearms`. | Same § Source-specific firearms |
| 2026-09-01 | 131 collisions keep-separate + SR1 UI grouping | 131 same-name cross-source collisions remain as distinct rows (source-qualified); UI collapses them under SR1 grouping rather than deleting/merging. | Same § Duplicate/name collision summary (131 review groups) |
| Prior | QftIS grenades OUT | Exactly 2 hard exclusions applied by `src.list_curation.curate_items()` via `EXCLUDED_SOURCE_NAME_PAIRS`: QftIS Concussion Grenade, QftIS Sleep Grenade. | Same § Hard exclusions |
| Prior | Airships/skyships IN | 3 fantasy vehicles kept in scope: Airship (XPHB), Skyship (EGW), Skyship (TalDoreiCampaignSettingReborn). | Same § Airships/skyships |

Sensitive keep-separate examples re-affirmed: Crystal (XPHB vs MonstersOfDrakkenheim), Zeal ×3 (TalDoreiCampaignSettingReborn / GrimHollowCG24 / GrimHollowPlayerPack), plus Obojima ingredient vs PHB/DMG gem-style names.

## 2. Swap Details

| Field | Value | Verification |
|---|---|---|
| Raw 2026 item count | 12,243 (`2026_07_12_item_list.json`, untracked) | `python -c "len(json.load(open('2026_07_12_item_list.json')))"` → 12243 |
| Curated count after hard exclusions | 12,241 (12243 − 2 excluded QftIS grenades) | `len(data/canonical_2026_07_12_curated.json)` → 12241; `len(trimmed_5etools_list.json)` → 12241 |
| Swap delta | 12243 → 12241 (raw→curated); canonical replacement 4837 → 12241 (previous trimmed → new trimmed) | HEAD `trimmed_5etools_list.json` = 4837; curated = 12241 |
| Byte-identical swap | `trimmed_5etools_list.json` ≡ `data/canonical_2026_07_12_curated.json` (12,680,003 bytes each); `.md` identical (17,033,557 bytes each) | `cmp data/canonical_2026_07_12_curated.json trimmed_5etools_list.json` → identical; same for `.md` |
| Alignment | 0/25 mismatches after 5etools-tag normalization | `src/criteria_extractor._strip_5etools_tags` (`{@tag ...}` → inner text) normalizes prose before comparison; `items_master ↔ items_criteria` name/source sets: 12241/12241, diff 0/0 |
| Duplicate structure aligned | 168 same-name groups in both trimmed and canonical; Counter identical | `Counter(name).groups>1` → 168 trimmed, 168 canonical, `Counter` equality true |
| Hard exclusions | 2 (QftIS grenades) — only curation delta | `src/list_curation.EXCLUDED_SOURCE_NAME_PAIRS` |

Raw `2026_07_12_item_list.json/.md` remain untracked under Option A (no canonical replacement beyond trimmed swap).

## 3. Per-Stage Counts (This Run — 2026-09-01)

### Stage 01 — `01_extract_items.py`

```
Loaded 12241 items from trimmed_5etools_list.json
Wrote 12241 rows to data/processed/items_master.csv

Rarity distribution:
  rare: 3793
  uncommon: 2657
  very_rare: 2274
  legendary: 1494
  common: 944
  mundane: 824
  artifact: 116
  varies: 103
  unknown_magic: 32
  unknown: 4

Items with official prices: 999
```

Sanity (independent CSV read, `csv.field_size_limit(10M)`): `items_master rows: 12241` ✓ expect ~12241.

Columns: 10 (`name, source, page, rarity, type, official_price_gp, req_attune, url, alias, raw_json`). Top sources: XDMG 3089, 24GriffonsSaddlebag1 897, GriffonsSaddlebag2 647, ObojimaTallGrass 616, HelianasGuidetoMonsterHunting 547, MonstersOfDrakkenheim 527, CallfromtheDeep 483, FTD 473, IllriggerRevised 437, ExploringEberron24 417.

### Stage 02 — `02_extract_criteria.py`

```
Loaded 9394 prose descriptions from items-sublist.md
Loaded 12241 items from data/processed/items_master.csv
Building generic parent lookup...
Found 41 generic parent items from items_master.csv
Added 172 generic parents from items-sublist-data.json
Total generic parent items: 213
Wrote 12241 rows with 121 columns to data/processed/items_criteria.csv
Variants enriched with parent entries: 5514

Items with weapon_bonus: 4268
Items with ac_bonus: 367
Items with spell_scroll_level: 938
Items with attached_spells (non-empty): 1483

Items with flight_full: 28
Items with flight_limited: 51
Items with teleportation: 44
Items with swim_speed: 146
Items with save_advantage (non-empty): 101
Items with condition_immunity_prose (non-empty): 15
Items with curse_effects (non-empty): 10

Items with extra_damage_avg > 0: 2090
Items with minor_beneficial > 0: 38
Items with major_beneficial > 0: 28
Items with minor_detrimental > 0: 34
Items with major_detrimental > 0: 18
Items with has_fixed_beneficial: 1
Items with has_fixed_detrimental: 0
```

Sanity: `items_criteria rows: 12241 / cols: 121` ✓. Rarity distribution identical to master (mundane 824, common 944, uncommon 2657, rare 3793, very_rare 2274, legendary 1494, artifact 116, varies 103, unknown_magic 32, unknown 4). `is_generic_variant=True` rows: 167.

### Stages 03 / 04 — `03_ingest_external.py` / `04_amalgamate.py`

**SKIPPED** — pricing/amalgamation/ML-stage. Spec: "If they are pricing/amalgamation/ML-stage, SKIP them (those belong to rrd with the full ritual)".

Probe:
- `03_ingest_external.py` — `Phase 3: Ingest DSA, MSRP, DMPG price guides → data/raw/ CSVs` (DSA.xlsx / MSRP.csv / DMPG.pdf). Missing `pdfplumber` on probe, pricing-stage → SKIP.
- `04_amalgamate.py` — `Phase 4: Amalgamate external price guides → amalgamated_prices.csv` — on `--help` probe it auto-executed (no argparse guard) and would regenerate `amalgamated_prices.csv` to 12,241 rows; **reverted to HEAD** to honor SKIP gate. Current `data/processed/amalgamated_prices.csv` remains stale at 4,837 rows (HEAD) pending rrd full ritual.

`ls scripts/` — 12 numbered pipeline scripts identified: 01_extract_items, 02_extract_criteria, 03_ingest_external, 04_amalgamate, 05_rule_formula, 05b_variant_adjust, 06_ml_refine, 07_validate, 07b_variant_consistency, 09_enforce_floors, 10_generate_output, 11_generate_html.

### Stages 05+

**NOT RUN** — per dispatch: "DO NOT run 05+ pricing scripts. DO NOT commit. DO NOT touch output/pricing_guide.csv."

`output/pricing_guide.csv` untouched: 4,749 rows, previous canonical pricing (verified `git status` shows no modification). Next pricing run deferred to rrd.

## 4. Notable Observations for Post-Migration Waves

- **168 duplicate-name groups** — stable across trimmed ↔ canonical (Counter-identical). Breakdown per preflight: 131 review same-name cross-source, 14 collapsible ammunition variants, 12 source-specific firearms, 8 vehicle/source variants, 2 sensitive gem/ingredient, 1 Drakkenheim/source-specific. Standard policy: keep distinct `(name, source)` rows; UI groups; manual collapse only for the 14+8 ammo/vehicle groups after source review. Do not merge Crystal/Zeal/Obojima-ingredient collisions without human approval.
- **8,001 specific variants with `genericVariant` pointers** — `items_master` raw_json `genericVariant` count = 8001 (matches preflight). `items_criteria.is_generic_variant=True` = 167 (parent templates themselves). Variant enrichment: 5,514 variants enriched with parent prose. Generic parent lookup: 41 found in `items_master.csv` + 172 from `items-sublist-data.json` = 213 total parents. Top families: Lycan Weapon (218), Lunar Weapon (112), Weapon of the Sun And Moon (112), +1/+2/+3 Adamantine/True Name/Weapon families (~109 each).
- **13 nested generic parents** — items whose entry contains `"Multiple variations of this item exist"` (per `src/list_curation.NESTED_GENERIC_VARIATION_PHRASE`). All 13 from GriffonsSaddlebag2: Bloody Marilith, Celestial Sunrise, Djinn and Tonic, Dusk Dagger, Hoarder's Haul, Magentan Sun-Saw, Masks of the Sacred Beasts, Orostead Iced Tea, Rejuvenating Draft, Reliquary of Holy Memories, Scroll of Mapping, Shifter's Shine, Wispy Sour. These are both specific variants and generic templates — keep as-is; UI should surface as variation hubs.
- **`items_master` row-size pressure** — raw `items_master.csv` exceeds default `csv.field_size_limit(131072)` on stock Python due to large `raw_json` payloads; consumers must set `csv.field_size_limit(10_000_000)` (as pipeline does). Hop B verified with raised limit.
- **Preflight staleness warning:** `reports/criteria_preflight_2026_07_12.md` and `reports/curation_preflight_2026_07_12.md` are pre-swap dry-runs (no canonical replacement, no processed writes) — still valid for decision record but counts should be cross-checked against this report's live extraction (all counts align: 12243→12241, 168 groups, 8001 variants, 13 nested).
- **Stale pricing artifacts pending rrd:** `data/processed/amalgamated_prices.csv` (4837 rows) and downstream `items_ml_priced.csv` / `items_priced.csv` / `output/pricing_guide.csv` (4749 rows) are still on the old 4837-item baseline. Full ritual must re-run 03→11 after this gate. No floors/validation drift observed in 01/02.
- **88-source expansion** — ensure variant grouping and display filters handle long source tail (26 new sources, several <20 items: FleeMortals 19, TalesFromTheShadows 18, OneShotWondersHolidayPack 14, HumblewoodCampaignSetting 13, Pugilist2024 41, etc.) without truncation in UI facets.

## 5. Verification Summary

| Check | Result |
|---|---|
| `01_extract_items.py` | ✓ 12241 in / 12241 out, 999 official prices |
| `02_extract_criteria.py` | ✓ 12241 rows × 121 cols, 9394 prose, 213 generic parents, 5514 enriched variants |
| `03_ingest_external.py` | ⊘ skipped (pricing-stage) |
| `04_amalgamate.py` | ⊘ skipped (pricing-stage; auto-run reverted) |
| `items_master.csv` rows | ✓ 12241 |
| `items_criteria.csv` rows | ✓ 12241 |
| `output/pricing_guide.csv` | ✓ untouched (4749 rows) |
| No commit | ✓ `git status` shows only `data/processed/items_master.csv`, `items_criteria.csv`, `trimmed_5etools_list.*` modified (no commit performed) |

Generated by hop B execution dispatch on 2026-09-01. Raw 2026 files verified untracked; swap verified byte-identical; extraction pipeline verified end-to-end for stages 01–02 only.
