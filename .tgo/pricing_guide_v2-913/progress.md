# pricing_guide_v2-913 — extractor broadening + q7b spell battery

## Objective
Broaden src/criteria_extractor.py to capture 16 below-floor items (grenades, Masks Mule, Snuggle Dragon, Moonbows, True Name seals) and implement q7b spell_battery_max_level for Spell Gems (0-9). Scope src/criteria_extractor.py + tests ONLY, verify via tests and 02 re-extract.

## Touch set
- `src/criteria_extractor.py` — helpers _SPELL_GEM_NAME_LEVEL_MAP (obsidian 0 … diamond 9) + _GRENADE_SPELL_MAP + _parse_spell_battery_max_level; structured init `spell_battery_max_level` (entries+name fallback); entries fallback _ENTRIES_FALLBACK_TEXT/_NAME for merge-preservation; entries extra_damage seal (damage dealt by your seals increases by Nd6) + Moonbow 7.0 always-on + True Name name fallback (+1 3.5/+2 7/+3 10.5) + short-rest healing (entries private); prose extra_damage (plain 2d6 fire unconditional Moonbow while-glowing always-on + seal) + short-rest healing 2×rests (3d6→21, 2d6→14, 1d6→7, 4d6→28) + multi-ability check_advantage fallback (`\badvantage` to avoid disadvantage) + grenade DC-debuff→attached_spells (slow 3rd: copper/gold, hold monster 5th: silver/brass, bronze damage only) + spell_battery 0-9 parsing (store up to Nth level / can only store cantrips) + Moonbow/True Name name fallback via _ENTRIES_FALLBACK_NAME
- `tests/test_extractor_broadening.py` — 17 tests with verbatim corpus snippets: Moonbow 7.0 fire, True Name +1 3.5/+2 7/+3 10.5, Snuggle Dragon 21/ Unicorn 14, Mule strength+dexterity, Copper slow/Gold slow/Silver hold monster/Brass hold monster/Bronze none, Spell Gem 0/1/9 and all 0-9, negatives
- `data/processed/items_criteria.csv` — re-extracted via scripts/02_extract_criteria.py (12241 rows, 122 cols, variants enriched 5514, extra_damage 2139, attached_spells 13)
- `.tgo/pricing_guide_v2-913/progress.md` (this file)

## Decisions
- Grenade mapping reuses daily 1 pricing path: slow 3rd (copper, gold broad-disadvantage+half-speed), hold monster 5th (silver paralysed, brass unconscious). Bronze prone+2d6 already priced via extra_damage, no spell. Documented in comments + tests. DC tag strips to number, so check `saving throw` not literal `dc`.
- Healing: is_safe_healing_context kept, temporary HP excluded, proximity 350/150 window, 2 short rests/day convention documented (3d6 10.5×2=21).
- Check advantage multi-ability fallback uses `\badvantage` to avoid matching inside disadvantage (fixed preflight cross-contamination where check_advantage counted 3 vs 1).
- Merge-preservation: entries stores combined_text+name in globals; prose only augments when desc empty (not just short) to avoid cross-item contamination in batch runs (fixed preflight 3→1).
- Moonbow/True Name name fallbacks guarantee CSV even when JSON entries [] (advanced weapons, Moonbow). Extra damage seal condition “seal” with multiplier 1.0 (spec says conditional avg 3.5/7/10.5).
- Spell battery: primary regex `store(?: up to)?` + alternative `spell of (up to)?Nth level`; cantrip-only →0; fallback name map for empty prose.
- No engine edits; only extractor + tests.

## Blockers
- None.

## Status
Complete — tests 333 passed (17 broadening + 316 existing), 02 re-extract grepped rows verified (grenades attached slow/hold monster, moonbows 7.0, snuggle 21/14, mule check, True Name needlers 3.5/7/10.5, gems 0-9), commit pending pushes.
