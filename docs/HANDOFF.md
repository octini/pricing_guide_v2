# Session Handoff — 2026-08-27

Written at end of the "expansion prep" session so a fresh session can resume
without context loss. The beads board is authoritative; this file is the map.

## Campaign: 4,837 -> 12,243 item expansion (plan confirmed by user)

Phases 0-2 COMPLETE. Migration gate (pricing_guide_v2-kxc) IN PROGRESS -
user has NOT said go yet. Remaining pre-flight work, all wired as gate
blockers:

1. pricing_guide_v2-6sw — Option D ritual: price stealth-disadvantage
   removal at 400gp (user-approved; root cause of Demon Skin inversion,
   see reports/resistance_armor_consistency.md).
2. pricing_guide_v2-z0z — Criteria deep-dive: discover untapped extractable
   pricing criteria (user's explicit pre-migration request; deliverable is a
   ranked findings report, user picks what to implement).
3. pricing_guide_v2-rsk + pricing_guide_v2-izk — fix 2 pre-existing red
   tests (amalgamator trim_outliers, spell_value charges_format) +
   test_hospitality.py SyntaxError.

After all blockers clear: present go/no-go -> migration (9xv) -> 12k run
(rrd) -> finish line (2b3) -> README (1tm) -> UI revamp (sr1, user will use
the "Impeccable" web-design skill suite).

## Decisions locked this session (all user-signed)

- Pack v3 ACCEPTED: post-extraction-fix candidate is the pricing baseline.
- Option D approved (stealth removal = 400gp, via ritual).
- Big-bang migration; price everything curation keeps (~12k rows);
  tiered triage (auto-accept high-confidence, human-review reference-anchored
  + extreme movers); consolidation library-level only; docs rewritten.
- Sane Magic Item Prices stays EXCLUDED from amalgamation (user decision).
- Publish updated web guide ONCE at the finish line, not before.

## Where the numbers live

- reports/extra_damage_signoff_pack_v3.md — current baseline sign-off
  (ML retrain variance story: 28 extra / 49 save / 369 variance of 446
  >5% movers; anchors held, zero FAILs).
- reports/drift_attribution_post_extraction_fixes.md — attribution method.
- reports/resistance_armor_consistency.md — Demon Skin inversion analysis.
- reports/demonglass_driver_investigation.md — the +673% artifact hunt.
- reports/extra_damage_signoff_pack_v2.md — prior baseline sign-off.
- docs/QUALITY_GATES.md — R2 gate + fingerprint guard + guardrail usage.

## Hard-won facts (also in project memory)

- Real pipeline input: trimmed_5etools_list.json (4,837). items-sublist-data
  .json (9,422) is legacy, unused. Output: 4,749 rows (generic-variant
  exclusion + Name/Price/Type dedupe preferring 2024 core books).
- Candidate list: 2026_07_12_item_list.json (12,243 items), audit done
  (1mv), curation decisions recorded on that issue.
- Pricing authority: anchors win by default; formula wins when criteria-rich
  (>=3) + guide-divergent (>0.60) + multi/solo. ML coefficients carry a
  criteria fingerprint; check_r2 fails on mismatch. ML retrain variance on
  legendary formula-only items is expected and governed by triage.
- Save-advantage tiers: BROAD 400 / CATEGORY 200 / SITUATIONAL 100.
- Extra damage: raw avg preserved; priced avg applies per-source multipliers
  (unconditional 1.0 / vs creature type 0.25 / on crit 0.05).
- Guardrail split classifies by Price Source (fixed in 39e564a - was using
  stale Has-Reference flag, mislabeling 2,245 rows).

## Operational notes for the next session

- Dispatch pattern that works for Dylan on this repo: fully pre-specified
  design + verbatim commands + capped reads. Sessions die in open-ended
  recon (watchdog kills read-loops). Small hops, verify after each.
- The SAFE dance (02 -> 05 -> 05b -> 06 -> 07 -> 09 -> 10 -> mv candidate ->
  git checkout -- output/ data/processed/) is the standard regeneration;
  NEVER leave canonical output/pricing_guide.csv modified.
- Test suite: 272 passed / 2 known failures (rsk) / test_hospitality.py has
  a pre-existing SyntaxError (ignore flag).
- Everything through commit 1550144 is pushed. Beads synced via dolt.
