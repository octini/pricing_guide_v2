# Session Handoff — 2026-09-02 (wave-1.5 adopted, public outputs regenerated)

Wave-1.5 candidate adopted as canonical at **f598b97** (2026-09-01 user sign-off, pushed to origin/master). Public outputs regenerated on 2026-09-02 at 11,941 rows (12,241 curated input → 167 generic-variant exclusions → 133 Name/Price/Type dedupes preferring DMG2024/PHB2024 → 11942 CSV lines). CSV/XLSX/HTML internally consistent. Display names live (dfcefc9); WSC raw-code fallback retained per constraint.

## Wave-1.5 adoption (f598b97) — what shipped

- **Reader fixes:** extractor broadening — conditions→control-spell mapping (slow/hold monster grenades), short-rest healing (2× rests), multi-ability advantage, seal damage, moonbow fire, spell_battery_max_level 0-9 via _SPELL_GEM_NAME_LEVEL_MAP + name fallback.
- **Battery parity (q7b):** reusable spell batteries priced ≥ scroll price of stored spell (SPELL_SCROLL_PRICES 0:25…9:100000), parity not premium, material cost unpriceable. Currently 82 battery-parity rows in tail; zero amalgamated battery rows today (theoretical binding for future waves). Verified: Diamond 100000 (L9), Ruby 45000 (L8), shards 69421.
- **Gated family-min (913):** magic-weapon family minimum premium (WEAPON_BONUS_VALUES {1:725,2:3400,3:14950}, capped multiplier 1.0 — benchmark already tier-priced) gated to non-amalgamated items only (reference authority restored); rejected anchors (price_authority=formula) not protected — e.g. +3 Adamantine Vertebrae 12647→14950 lifted correctly. Ammo-excluded from variant stats (Adamantine Weapon min 0.02→1.0, Needler adj 0).
- **Tripwire floors (sej):** absolute rarity floors as tripwire backstop (exempt official prices + consumable-modifier types ammunition/potion/scroll/poison); 13 floor-lifts (8000/1000/200) + 2 final-gate lifts (Vertebrae 14950, True Name Dart 8000). Drow premium-exempt floor-clamped (2502→8000) per approved scope.

**Key numbers:** guardrail median **0.00%** (reference-anchored mean 0.69% at rrd adoption; wave-1.5 median 0.00% retained despite 1083 tail rows >25%); **373 tests** pass at adoption; R² 0.9700 fingerprint 169a391 PASS; anchors 0 FAILs at rrd → 6/1768 known-good >5% honest at wave-1.5 (5 reference + 1 rejected Vertebrae); Horowitz-reviewed with **R1–R3 remediated** (R1 rejected-anchor gate, R3a 6 honest known-good + ≥8 floor-lifts + 47/59 Adamantine collateral, R3b battery 82 exact-scroll, R3c Drow premium-exempt + battery binds anchored zero — all disclosed in sej_913_q7b_ritual.md).

**Artifacts regenerated at adoption:** `output/pricing_guide.csv` (cp candidate→canonical, identical 11942 lines), `output/pricing_guide.xlsx` (2163018), `output/anomaly_report.md`, `output/variant_consistency_report.csv` (8 families, 2 flagged CV 0.6308 gleaming), `output/official_price_anchor_audit.csv` (999 rows, 724 near_agreement, 155 exact_commodity, 117 high_disagreement), `data/processed/items_validated.csv` (12241, final gate re-applied).

## Current baseline (authoritative)

- **Input:** `2026_07_12_item_list.json` (12,241 rows after QftIS grenade exclusions, user-approved 2026-09-01) → `data/processed/items_criteria.csv` 12241×122 cols.
- **Output:** 11,941 rows (11942 lines CSV) — `output/pricing_guide.csv` / `.xlsx` (4 sheets) / `index.html` (11941 embedded JSON items, 7641 linked to 5e.tools JSON, 11,941 "Showing" header).
- **Pipeline:** 01→02→03→04→05→05b→06→07→07b→09→10→11 all re-ran; canonical preserved through adoption.
- **Display names:** centralized `src/source_names.py` from `docs/reference/ttrpg-convert-cli-sourceMap.md` + 24 verified supplements in `LOCAL_SOURCE_NAME_SUPPLEMENTS` (The Griffon's Saddlebag 897+633, Heliana's 501, etc., websearch-verified). WSC intentionally raw: Scroll of Speak with Animals 75, Wand of True Polymorph 18105.22.
- **Beads:** `bd ready` is authoritative; board reflects wave-1.5 closed (913,q7b,sej), rrd open for triage queue, acc+2b3 closing via this dispatch.

## Honest open items (triage queue — rrd stays OPEN)

1. **Needler-class floor-clamped vs references 3× — manual-review candidate.** Example: +3 Repeater Needler (Drow) 2502→8000 floor (family-min 14950 gated away because amalgamated multi/solo anchor wins). Tripwire floor 8000 is backstop, not destination; factor ~3× vs family benchmark signals manual review for next wave (premium-exempt per sej scope, 9 total floor-clamped items including Vertebrae/Dart/Monster Hunter's Needler 6721→8000).
2. **994 unanchored ml-variance rows.** Tail attribution: 82 intended (battery + gated family-min) + 7 floor-tripwire + **994 ml-variance** = 1083 rows >25% drift. Variance is unanchored (no guide price, formula-only legendary items retrained) — expected but requires disposition (sample audits, not auto-accept).
3. **Triage queue = sej-closed, 4om, CV flags, variance disposition.** sej tripwire policy closed; 4om (4 off-median?) + CV flags (2 flagged variant families CV >0.60) + variance disposition remain. rrd holds tiered triage: auto-accept high-confidence formula prices; human-review queue = reference-anchored + extreme movers + 994 variance sample.

## Campaign: 4,837 → 12,241 → 11,941 (complete through adoption)

Phases 0-2 were complete at 2026-08-27 (see prior HANDOFF at f598b97 parent). Expansion plan executed:

- pricing_guide_v2-6sw — Option D ritual: stealth-disadvantage removal 400gp (landed 71e5bf7, Horowitz follow-up 449c8f9).
- pricing_guide_v2-9xv — Migration: canonical 4,837 → 12,241 curated list (Dolt-curated, QftIS grenades excluded, airships/skyships kept, collisions keep-separate, alignment 0/25 mismatches).
- pricing_guide_v2-rrd — Full 12k run: ML retrain 122 cols, R² 0.9692, guardrail median 0.00%, anchors 0 FAILs, tail 331 (13 intended, 14 floor-gap→sej, 304 variance), suite 316, Horowitz APPROVE → adopted 93cd09e.
- pricing_guide_v2-913/q7b/sej — Wave-1.5 broadening + battery + gated floors + tripwire → adopted f598b97 (this handoff).
- pricing_guide_v2-acc — Display names (24 supplements, dfcefc9) → closing via 2b3 gate.
- pricing_guide_v2-2b3 — Finish line: public-ready CSV/XLSX/HTML regenerated, internally consistent, docs synced.
- pricing_guide_v2-1tm — README done (Horowitz-reviewed natural register).

After 2b3: sr1 UI revamp (user will use "Impeccable" web-design skill suite) remains.

## Decisions locked (all user-signed)

- Pack v3 ACCEPTED: post-extraction-fix candidate is pricing baseline.
- Option D approved (stealth removal = 400gp, via ritual).
- Big-bang migration; price everything curation keeps (~12k rows); tiered triage (auto-accept high-confidence, human-review reference-anchored + extreme movers + variance sample); consolidation library-level only; docs rewritten.
- Sane Magic Item Prices stays EXCLUDED from amalgamation.
- Publish updated web guide ONCE at finish line (now).
- Tripwire floors remain backstop (official+consumable exempt; Drow premium-exempt approved scope); battery parity binds anchored rows theoretically (zero today).
- Display names: verified 24 from publisher/DDB pages; WSC raw fallback per constraint; unknown codes fall back to raw code, never invented titles.

## Where the numbers live

- `reports/sej_913_q7b_ritual.md` — wave-1.5 ritual: Hop C3-C6 guardrail/tail/mechanism tables (median 0.00%, 372→373 tests, 6/1768 known-good, 75/2533 reference, 82/7/994 tail).
- `reports/price_creep_guardrail.md` — guardrail after C6: Known-good FAIL 6/1768 >5% (was 5→6 with Vertebrae), Reference FAIL 75/2533, median 0.00% PASS.
- `reports/tail_attribution_sej913.csv` — 1083 rows >25% (82 intended, 7 floor, 994 variance).
- `reports/migration_12k_signoff_pack.md` + `reports/migration_2026_07_12_swap.md` — rrd sign-off + migration swap.
- `docs/QUALITY_GATES.md` — R² gate + fingerprint + guardrail usage.
- `PROJECT_CONTEXT.md` — architecture + current baseline (pointer here for 11,941/12,241 counts).

## Hard-won facts (also in project memory)

- Real pipeline input now: `2026_07_12_item_list.json` (12,241) → `data/processed/items_master.csv` 12,241 → `output/pricing_guide.csv` 11,941 (generic-variant exclusion 167 + Name/Price/Type dedupe preferring 2024 core books, 133 removed). Legacy `trimmed_5etools_list.json` (4,837→4,749) superseded and archived.
- Candidate list: 2026_07_12_item_list.json (12,241) audit done (1mv), curation decisions on 9xv.
- Pricing authority: anchors win by default; formula wins when criteria-rich (≥3) + guide-divergent (>0.60) + multi/solo. ML coefficients carry criteria fingerprint; check_r2 fails on mismatch. ML retrain variance on legendary formula-only items is expected and governed by triage.
- Save-advantage tiers: BROAD 400 / CATEGORY 200 / SITUATIONAL 100.
- Extra damage: raw avg preserved; priced avg applies per-source multipliers (unconditional 1.0 / vs creature type 0.25 / on crit 0.05).
- Guardrail split classifies by Price Source (fixed in f253f46 — was stale Has-Reference flag).
- Source names: `src/source_names.py` loads from `docs/reference/ttrpg-convert-cli-sourceMap.md` + LOCAL_SOURCE_NAME_SUPPLEMENTS (24); WSC raw fallback.

## Operational notes for next session

- Dispatch pattern that works for Dylan: fully pre-specified design + verbatim commands + capped reads. Sessions die in open-ended recon (watchdog kills read-loops). Small hops, verify after each.
- The SAFE dance (02→05→05b→06→07→09→10→ mv candidate → git checkout -- output/ data/processed/) is standard regeneration; NEVER leave canonical output/pricing_guide.csv modified outside adoption.
- Test suite: 373 passed at wave-1.5 adoption (316 at rrd adoption); full suite via `python3 -m pytest tests/ -q` (ignore `test_hospitality.py` SyntaxError for quick sanity).
- Everything through f598b97 is pushed (canonical + baselines). After 2b3 dispatch, expect 2 new commits: HTML regen + HANDOFF/PROJECT_CONTEXT sync, plus output/pricing_guide.xlsx (same 11941 rows, timestamp freshened).
