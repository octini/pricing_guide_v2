# pricing_guide_v2-913 — extractor broadening + q7b spell battery + engine floors (hop B)

## Objective
Hop A (landed f38356f): broaden extractor for 16 below-floor items (grenades, Mule, Snuggle Dragon, Moonbows, True Name seals) + q7b spell_battery_max_level 0-9 (333 tests green, 122 cols). Hop B: engine family minimum (magic-weapon benchmark) + scroll-parity battery floor, blast-gate, tests, commit/push.

## Touch set
- `src/criteria_extractor.py` — _SPELL_GEM_NAME_LEVEL_MAP + _GRENADE_SPELL_MAP + _parse_spell_battery_max_level; spell_battery_max_level structured init + name fallback; entries extra_damage seal/Moonbow/True Name + healing short-rest 2×rests + check_advantage multi-ability + grenade slow/hold monster
- `src/pricing_engine.py` — WEAPON_BONUS_VALUES table {1:725,2:3400,3:14950} helpers `_family_min_for_criteria` + `_battery_min_for_criteria`; family minimum applied after amalgam/variant selection before attunement (amalgam raw no-attune, non-amalgam with attune via helper, property after, exclusions: is_ammunition True or type not M/R); battery floor parity via SPELL_SCROLL_PRICES (0:25…9:100000) for (a) spell_battery_max_level>=0 or (b) charges>0+attached non-empty; applied in simple, anchor, and formula paths before floor; SP parity not premium; enspelled verified no battery parse ("Bound into this weapon is a cantrip" without level bound -> None, charges 6 but attached_spells [] => no floor)
- `tests/test_extractor_broadening.py` — 17 tests
- `tests/test_engine_floor_rules.py` — 11 tests: needler +1 rare >=725*attune, +1 dagger, rarity scaling, ammo excluded (acid test: +1 Needle amalgam 32.88 stays <362 vs weapon lifted), Diamond >=100k, Silver shard >=20k, Obsidian mundane ->25 exact parity, charges+hold monster ->3000, parity-not-premium Topaz 13500 untouched, enspelled not firing, precedence
- `data/processed/items_criteria.csv` — 12242 rows, 122 cols (via 02)
- `/tmp/hopB_blast.py` — blast counts from criteria.csv + engine code paths

## Decisions
- Family minimum: WEAPON_BONUS_VALUES calibrated at rare; rarity mult uncommon 0.5 rare1.0 very_rare2.0 legendary3.0 fallback1.0; attune open0.90 class0.80 none1.0; applied max(current, family) after selection before attune (equivalent to post-attune max due to monotonic). Amalgam branch uses raw no-attune compare to avoid double-discounting guide prices. Ammo excluded via is_ammunition + type M/R gate.
- Battery floor: condition (a) parsed level 0-9 else (b) charges>0 + attached non-empty -> max level via get_spell_level -> scroll price; charges parsing handles string dice via regex; attached parsing NA-safe via ast.literal_eval + dict/list; parity not premium = max(price,battery_min) no extra multiplier.
- Blast gate: family binds 3 (Blood Spear uncommon+2 open 1476<1530, Bloodrage Greataxe uncommon+2 1500<1700, Silver Sword uncommon+3 class 3680<5980) — 0 needlers because simple path already at benchmark; battery binds 6 (Unknown Elixir uncommon6, Jade Serpent Staff unknown_magic5, Cottage Chest rare8, Mudslick Tower very_rare8, Diamond9, Ruby8). Both < thresholds 150/50 => pass. Expected rough vs honest: spec expected ~8 Needlers + a few daggers/darts but honest count is 3 due to variant system staleness and simple path already correct; battery expected 10 gems +4-5 shards but honest 6 due to only high-level gems needing lift (only Diamond/Ruby exceed pricing; lower gems already above scroll parity via rarity base).
- Obsidian 25 exact test uses mundane rarity (floor1) to allow parity 25 to stand above base 1; uncommon base 750 already >25 so no lift — test uses mundane to demonstrate parity exactly.
- Enspelled: verified "store one spell" phrasing without level -> _parse returns None, no battery trigger.

## Blockers
- None.

## Status
Complete — hop B engine edits + 11 new tests green; full suite 344 passed (333+11), blast gate pass (family 3, battery 6); commit pending.
