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


## Hop C4 — capped family-min + reskin uncommon-or-higher (2026-09-02)

### Objective
Cap family-min rarity multiplier at 1.0 (benchmark already tier-priced; double-count inflated 881 anchored weapons) + reskin inner-rarity >= uncommon (22 -> 1 embedded copy, Piwafwi only; Spell Gem Amber freed) + guardrail header scope fix (counts + separate reference line). Tests 367 green, candidate mechanism rows verified, commit pending Horowitz sign-off.

### Touch set
- `src/pricing_engine.py` — rarity_mults capped `{common:0.25,mundane:0.25,uncommon:0.5,rare:1.0,very_rare:1.0,legendary:1.0,artifact:1.0}` in _family_min_for_criteria, calculate_price simple/anchor/formula paths
- `scripts/09_enforce_floors.py:297` — same cap in _family_min_for_row
- `scripts/10_generate_output.py` — embedded reskin requires `inner_rarity_norm in (uncommon,rare,very_rare,legendary,artifact)`; common/mundane excluded; 22 -> 1 (Piwafwi only)
- `scripts/reports/price_creep_guardrail.py` — header scope fix: counts `known_good_counts` + `reference_anchored_counts`, separate Reference-anchored status line, scope note; stale variable / wrong population bug fixed
- `tests/test_engine_floor_rules.py`, `tests/test_floor_enforcement.py`, `tests/test_pricing_engine.py`, `tests/test_reskin_rarity_fixes.py` — updated for capped expectations (Drow 14950, Silver Sword 5980, Amber 9518 etc)
- `reports/price_creep_guardrail.md` — regenerated: Known-good FAIL (495/1768 >5%), Reference-anchored FAIL (663/2533), Median 0.00%
- `reports/sej_913_q7b_ritual.md` — added Hop C4 section with capped rationale, reskin 22->1, final anchor verdict, 13-row mechanism table verbatim
- `data/processed/*.csv` — 09+10 re-ran, 11,941 rows candidate

### Decisions
- Capped multiplier rationale: WEAPON_BONUS_VALUES already tier-priced at rare; Very Rare 2.0× and Legendary 3.0× double-counted. Cap at 1.0 ensures family-min only discounts sub-norm rarity (common 0.25, uncommon 0.5) else benchmark intact. Repeater Needler Drow 14950×1.0×1.0=14950 (was 44850). Remaining 495 FAILs are correctly low-baseline lifts (Repeater 1000->14950 1395% etc) not double-count; 881 double-count eliminated.
- Reskin: common ingredient Amber (common 114.4) previously inherited as magic (mundane exclusion only). Now requires uncommon+ so Amber very_rare 9518 freed; only Piwafwi (Uncommon) remains among 22 pattern matches.
- Guardrail: bug was header counted reference-anchored or stale variable while table showed known-good honestly. Fix adds explicit counts and separate reference line so verdict reflects table honestly; thresholds unchanged.

### Blockers
- None. Awaiting Horowitz + user sign-off before adopt.

### Status
Complete — hop C4 edits landed uncommitted, 09+10 re-ran, guardrail regenerated with corrected header, candidate verified 13 rows correct, 367 tests pass. Commit next.


## Hop C5 — family-min gated to non-amalgamated (reference authority restored) + needle-weight root fix (2026-09-02)

### Objective
Gate family-min to non-amalgamated items only (reference authority) + fix Adamantine Weapon ammo contamination (needle-weight). Collapse known-good >5% from 495 → 5, reference-anchored 663 → 74, median 0.00% retained. Verify Drow +3 Repeater Needler remains low (authority-correct). 372 tests green, candidate 11942, commit pushed.

### Touch set
- `src/pricing_engine.py` — `_is_amalgamated_reference()` + gated family-min in `calculate_price` (simple amalgam, non-amalgam, anchor) and `_family_min_for_criteria` retained capped 1.0; solo-outlier still clamps
- `src/variant_system.py` — `extract_generic_variant_mapping` records `is_ammunition` (type_base A or ammo flag); `compute_generic_group_stats` excludes ammo for weapon groups (`'weapon' in name.lower()`), filtered median/min/count (Adamantine Weapon min 1.0 not 0.02, count 3, Needler adj 0); Drow/+N groups already clean
- `scripts/09_enforce_floors.py` — `_is_amalgamated_row()` (Price Source Amalgamated or amalgamated_price+multi/solo) + gated final gate `not _is_amalgamated_row` (official + amalgamated exemptions); `math` import
- `tests/test_engine_floor_rules.py` — amalgamated weapon stays <362.5 not lifted, non-amalgamated lifted
- `tests/test_variant_stat_freeze.py` — `test_hop_c5_weapon_stats_exclude_ammunition` (Adamantine Weapon, Needler adj 0)
- `tests/test_pricing_engine.py`, `tests/test_floor_enforcement.py` — gated expectations
- `reports/price_creep_guardrail.md` — regenerated: Known-good FAIL (5/1768 >5%, 54/1768 >1%; PASS ≤1%), Reference-anchored FAIL (74/2533 >5%, 551/2533 >1%; median 0.00%), common 11940, median 0.00% mean 250.84% >5%2806 >25%1083, split formula 9407 mean 318% vs reference 2533 mean 0.05%
- `reports/tail_attribution_sej913.csv` — refreshed 1083 rows (>25%): intended-913/q7b 78, floor-tripwire 7, ml-variance 998; Drow 2502→8000 219% floor-tripwire (amalgamated authority)
- `reports/sej_913_q7b_ritual.md` — added Hop C5 section (gate summary, root-fix Adamantine 0.02→1.0, guardrail verbatim, needler outcome: remained low 8000 not 14950)
- `data/processed/*.csv` — 05→05b→06→07→07b→09→10 re-ran (12241 rows, 11941 output rows)
- `output/pricing_guide_candidate.csv` — 11942 lines, candidate untracked (Drow 8000, Mule 11296, Moonbow 12560, Snuggle Dragon 5918, Grenade Silver 44859, Diamond 100000, Piwafwi 4072, etc.)

### Decisions
- Gating rationale: amalgamated multi/solo guide prices WIN vs rule premium; solo-outlier/Algorithm (none) still clamp via family-min; prevents double-count and authority drift.
- Variant exclusion narrow: only weapon groups drop ammo members; ammo groups (Adamantine Ammunition) retain members; filtered only if retains ≥1 member.
- Drow outcome: amalgamated reference remains low 8000 (floor 8000, not family 14950) — authority-correct. Variant fix did not raise Needler (adj 0); +N/Drow groups already clean.

### Blockers
- None. Awaiting Horowitz + user sign-off for remaining 5 known-good and 74 reference-anchored FAILs (now honest, non-amalgamated only).

### Status
Complete — hop C5 landed in 1b7ea83 (14 files, 28685 insertions), 372 tests pass, guardrail collapsed 495→5, tail 1083, candidate verified 11942, bd dolt push + git push done, canonical preserved.

## Hop C6 — rejected-anchor gate fix + honest tail re-bucketing (2026-09-02)

### Objective
Gate must not protect REJECTED references (price_authority == formula → forced-formula, rejected anchor not winning) + honest tail re-bucketing (battery-parity 4 rows) + policy disclosures. Re-run 09+10, guardrail, mechanism verify, 373 tests.

### Touch set
- `src/pricing_engine.py:_is_amalgamated_reference` — early-return False when price_authority == 'formula' (rejected anchor) before amalgamated_price/confidence check; 4 family-min sites now lift rejected anchors
- `scripts/09_enforce_floors.py:_is_amalgamated_row` — same (price_authority formula → False) before Price Source Amalgamated check; gate in apply_final_guarantees now lifts rejected
- `tests/test_pricing_engine.py::test_hop_c6_rejected_anchor_not_protected_by_family_min` — bounded read live row +3 Adamantine Vertebrae Sword price_authority==formula (coverage 3 spread 0.674, rule 87750, validated 12647.38), asserts _is_amalgamated false for formula / true for anchor, DataFrame simulate 12647→14950 via apply_final_guarantees, cross-check 09 predicate
- `reports/tail_attribution_sej913.csv` — re-bucketed 4 battery-parity rows ml-variance→intended-q7b (Cottage Chest 45000 L8, Mudslick Tower 45000 L8, Unknown Elixir 8500 L6, Jade Serpent Staff 3000 L5 — exact scroll-table levels; full 1083-row scan for other exact-scroll rows found none additional — Weightlessness/Sagittarian remain ml-variance correctly); counts 78/7/998 → 82/7/994
- `reports/sej_913_q7b_ritual.md` — added Hop C6 (R1 gate fix, R3a honest 5→6 known-good relabel 4 floor +1 drift +1 rejected Vertebrae + ≥8 floor-lifted + Adamantine collateral 47/59, R3b 994/82, R3c two policy notes: Drow premium-exempt floor-clamped 2502→8000, battery parity binds anchored rows too but ZERO amalgamated battery rows currently — theoretical)
- `reports/price_creep_guardrail.md` — regenerated: Known-good FAIL (6/1768 >5%, 55/1768 >1%; was 5/74 before Vertebrae lift), Reference FAIL (75/2533 >5%, 552/2533 >1%; was 74), median 0.00% PASS; mean drift stable
- `data/processed/items_validated.csv` — final gate now 12647.38→14950 for +3 Adamantine Vertebrae (+ True Name Dart 7950→8000); 09+10 re-ran, candidate 11942 preserved, canonical untouched
- `output/pricing_guide_candidate.csv` — 11942 candidate (Vertebrae 14950, Drow 8000, Spell Gem 100000, Masks 11296, +3 Dagger 8987, Piwafwi 4072)

### Decisions
- Rejected-anchor gate: tiered-authority (coverage≥3 AND spread>0.60) forces formula → price_authority=formula; those rows are NOT winning references, so family-min may clamp. Fix checks price_authority before amalgamated. Winning anchors (anchor) remain protected. Battery parity still binds anchored rows via engine :1705-1711, but currently zero amalgamated battery rows — theoretical only.
- Tail re-bucketing honest: battery parity exact scroll values (45000 L8 etc.) are intended-q7b, not variance; scan confirmed no other battery-parity exact-scroll mislabels.
- Floor-lifted ≥8 (7 tail + True Name Dart 7950.1→8000 outside tail at +0.63%; actually 9 with Monster Hunter's Needler 6721→8000 at 19%) — corrects stale “1 item clamped”.
- Adamantine collateral disclosure: 47/59 non-ammo Adamantine weapon adjustments shifted by design (log_range 300×→6×), e.g. Fighting Chain -0.199→-0.130 (740.40→748.44); Drow Crossbow Heavy byte-identical.
- Policy notes added for sign-off: Drow premium-exempt floor-clamped per approved tripwire scope; battery parity binds anchored rows (theoretical zero currently).

### Blockers
- None. R2 (stale xlsx/audit artifacts) deferred to adoption commit after user sign-off — not regenerated in this hop.

### Status
Hop C6 complete — 373 tests pass, candidate 11942 with Vertebrae 14950, guardrail 6/1768 & 75/2533 FAIL honest (median 0.00% PASS), mechanism 6/6 PASS, tail 82/7/994, git commit pending bd dolt push + git push; R2 deferred to adoption commit.

