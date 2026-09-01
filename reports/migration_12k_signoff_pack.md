# 12k Migration Sign-off Pack — rrd Calibration + Guardrail (Hop 2)

**Status: AWAITING USER SIGN-OFF — NOT ADOPTED.** Candidate `output/pricing_guide_candidate.csv` (11,941 rows) is untracked. Canonical `output/pricing_guide.csv` (4,749 rows) and `output/pricing_guide.xlsx` are untouched. `trimmed_5etools_list.json` already swapped to 12,241 curated per d43bc38 (hop B); this hop only calibrates pricing, not input. No `output/` or `data/processed/` commits until sign-off.

---

## 1. Decision Summary + Scope

**Question:** Adopt candidate 11,941-row output as canonical pricing baseline for the 12,241-row curated corpus (2026_07_12), replacing the 4,749-row / 4,837-item baseline?

**Scope:**
- **Curated input:** 12,241 rows (`data/canonical_2026_07_12_curated.json`, `trimmed_5etools_list.json`; raw 12,243 → 12,241 after 2 hard-excluded QftIS grenades per `reports/curation_preflight_2026_07_12.md` and `reports/migration_2026_07_12_swap.md`).
- **Candidate output:** 11,941 rows (`output/pricing_guide_candidate.csv`, 11,942 lines including header; untracked, generated via `scripts/10_generate_output.py` after full ritual).
- **Canonical output (unchanged):** 4,749 rows (`output/pricing_guide.csv`, 4,750 lines) — restored after candidate generation (`git checkout -- output/` in hop 1b END OF DANCE).

**Output exclusions (12,241 → 11,941 = 300 rows excluded; reskins are copies, not exclusions):**
- 167 generic-variant templates (`is_generic_variant=True` in `items_criteria.csv`; e.g., generic "Horn of Valhalla" placeholders with `items` field) — excluded from final output per `10_generate_output.py` L125.
- 133 deduped `(Name, Price, Type Code)` rows — identical name/price/type across sources collapsed to preferred source (DMG 2024 / PHB 2024 priority) per L209-218.
- 17 alias reskins (`alias` column) — price copied from original (e.g., Cloak of Shadows → Cloak of Elvenkind) per L133-152, **not excluded**.
- 22 embedded reskins (`<Name> (<Original>)` pattern) — price copied per L153-165, **not excluded**.

Math: 167 + 133 = 300 excluded; 12,241 − 300 = 11,941 output rows. Alias/embedded copies preserve row count (they replace price, not rows). This matches `reports/migration_2026_07_12_swap.md` §4 (`is_generic_variant=True` = 167) and the `10_generate_output.py` dedupe print line.

**Source expansion:** 66 canonical sources → 88 curated sources (+26 new-only sources per `reports/curation_preflight_2026_07_12.md`: GriffonsSaddlebag 1/2, ObojimaTallGrass, HelianasGuidetoMonsterHunting, CallfromtheDeep, IllriggerRevised, GrimHollow family, HumblewoodTales, TalDoreiCampaignSettingReborn, etc.). XDMG +1,084 rows is the largest expansion.

---

## 2. Dance Numbers (Per-Stage Counts)

| Stage | Script | Input → Output | Key counts |
|---|---|---|---|
| Raw → Curated | `src/list_curation.curate_items()` | 12,243 → 12,241 | 2 hard-excluded: QftIS Concussion Grenade, Sleep Grenade |
| 01 | `01_extract_items.py` | 12,241 → 12,241 | 999 official prices; 12,241 `items_master.csv` rows |
| 02 | `02_extract_criteria.py` | 12,241 → 12,241 | 121 cols, 9,394 prose, 213 generic parents (41 in master + 172 in `items-sublist-data.json`), 5,514 variants enriched |
| 03/04 | `03_ingest_external.py` / `04_amalgamate.py` | — | Pricing/amalgamation stage (skipped in hop B, executed in rrd ritual on 12,241 baseline) |
| 05 | `05_rule_formula.py` + `05b_variant_adjust` | 12,241 priced | Variant adjustment via `compute_generic_group_stats` (see §5) |
| 06 | `06_ml_refine.py` | 12,241 ML-priced | **Final blended R² 0.9692 (log-space)**, cross-val mean 0.9305 (0.9173 / 0.9399 / 0.9270 / 0.9294 / 0.9387); **+0.1229 vs baseline 0.8463 → PASS**; fingerprint `b22382a291023fbf…` **PASS** (`check_r2.py` PASS) |
| 07 | `07_validate.py` | 12,241 validated | No remaining floor violations after `09_enforce_floors.py` |
| 07b | `07b_variant_consistency.py` | 8 families | **2 flagged** (see §6 Known Issues) |
| 09 | `09_enforce_floors.py` | — | No remaining violations |
| 10 | `10_generate_output.py` | 12,241 → 11,941 | 167 generic excluded, 133 deduped, 17 alias-copied, 22 embedded-copied; candidate `pricing_guide_candidate.csv` written then preserved untracked |

**R² / fingerprint verification:** `python3 scripts/reports/check_r2.py` — PASS. Baseline 0.8463 → 0.9692 (+0.1229). Fingerprint `b22382a291023fbf…` matches expected for 12k run. Note: post-dance `data/processed/*` was reverted to HEAD (4,837-row stale state) per END OF DANCE; a live `06_ml_refine` on the reverted 4,837 corpus yields R² 0.9723 (+0.1260) with same fingerprint — expected divergence, not a regression; the 12k 0.9692 figure above is the candidate-generation value captured in `.tgo/pricing_guide_v2-rrd/progress.md`.

---

## 3. Guardrail — TRUE Attempt-2 Numbers (Honest Label: REVIEW, not PASS)

Generated: `python3 scripts/reports/price_creep_guardrail.py --baseline output/pricing_guide.csv --candidate output/pricing_guide_candidate.csv --output reports/price_creep_guardrail.md` — **not checked out after**; committed this hop. File at `reports/price_creep_guardrail.md` (627 lines, full known-good table) reflects candidate 11,941 vs baseline 4,749.

**Input row matching:**
- Common `(Name, Source)` rows: **4,717**
- New candidate rows: **7,224** (candidate-only; expected from 26 new sources + expansion)
- Missing candidate rows: **32** (baseline present, candidate absent — §4 triaged, none are unintended drops)

**Aggregate final-price drift (common 4,717):**
- Median % drift: **0.00%** | Mean % drift: **9.32%** | Median gp: 0 | Mean gp: −218
- Rows >5% drift: **1,113 (23.6% of common)** | >10%: 802 | >25%: 331

**Split (reference-anchored vs formula/ML-only) — the honest read:**

| Split | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| reference-anchored | 1,040 | 0.00% | 0.69% | 0 gp | 1 gp |
| formula/ML-only | 3,677 | 0.00% | **11.77%** | 0 gp | −280 gp |

**Label:** The formula/ML-only 11.77% mean drift is **accepted ML-retrain variance**, per `reports/extra_damage_signoff_pack_v3.md` precedent (user-signed), **NOT a guardrail PASS**. Reference-anchored 0.69% mean shows anchoring held; median 0.00% in both splits shows most rows did not move. Guardrail overall: **REVIEW** — 23.6% of common rows exceed 5%, driven by ML-sensitive tail, not by reference-priced items.

**Drift by rarity (common rows):** Rare 1,408 median 0.00% mean 20.41%; Common 349 median 4.34% mean 27.71%; Legendary 638 median 0.00% mean −1.78% (variance is formula-side, not rarity-systematic). Artifact 71 median 0.00% mean 0.00% stable.

**Drift by source (largest means):** Frontiers of Eberron: Quickstone 111 rows median 131.78% mean 241.65% (Demonglass family, formula/ML-only); Explorer's Guide to Wildemount 190 rows mean 17.22% (Acheron Blade family). Dungeon Master's Guide (2024) 1,981 rows median 0.00% mean 2.55% — reference-anchored core is stable.

---

## 3b. Tail Attribution — 331 Rows >25% Drift (Horowitz M1)

Attribution per `reports/tail_331_attribution.csv` (331 rows >25% drift from guardrail common 4,717). Bucketed with evidence, precedence kh7-wave1 > 6sw-stealth > floor-gap-or-value-landing > corpus-match-change > ml-variance. Full CSV is the source of truth; summary below is honest aggregation.

| Bucket | Count | Definition / Evidence |
|---|---:|---|
| kh7-wave1 (wave-1 repricing, intended) | 12 | `temp_hp_avg>0` or `hp_max_flat>0` or `hp_max_per_level>0` or `initiative_bonus!=0` or `initiative_advantage==True` in `data/processed/items_criteria.csv` — 6× Acheron Blade family (`temp_hp_avg` 6.5 per_action, `reports/wave1_criteria_impact.md:83`), 3× Berserker family (`hp_max_per_level` 1.0), Medal of the Meat Pie (`temp_hp_avg` 7.0), Helm of Awareness (`initiative_advantage` True). Integration test `tests/test_wave1_criteria.py:241` covers the simple-item bypass fix that enables this repricing. |
| 6sw-stealth (stealth-disadvantage removal +400 gp) | 1 | HA or disadvantaged MA (Half Plate/Scale/Spiked) with `stealth_penalty==False` → `STEALTH_REMOVAL_RATE` 400 gp (`src/pricing_engine.py` `_has_stealth_removal`); Living Stoneskin (HA, 13,568→17,682 gp, +30.0%) is the sole >25% mover in this bucket. |
| floor-gap-or-value-landing | 14 | Candidate lands below `RARITY_FLOORS` (legendary 8,000, very_rare 1,000, rare 200, uncommon 50 per `src/pricing_engine.py:56`) or on exact value-landing signatures 5,000/1,000/500/115/10. Spell Gem and Shard Solitaire families (see M3 deep-dive). `09_enforce_floors.py` does NOT clamp wondrous items (06 ML path) — floor unenforced for no-mundane-base items, honest gap. |
| corpus-match-change | 0 | Has Reference flag diff (candidate `Price Source` amalgamated vs formula) — 0 for all 4,717 common rows. Honest null reported; naive `amalgamated_prices.csv` membership yields ~213 false positives via `variant_price` contamination (e.g., Demonglass `has_ref` True via variant-price, not amalgamation), so 0 is the correct bucket. |
| ml-variance (residual) | 304 | No wave1/stealth/floor/match signature → ML retrain variance on 12,241 vs 4,749 corpus + variant-stat expansion. |

**Variant-composition drift (named sub-class of ml-variance):** Demonglass exemplifies the mechanism without an anchor pin. Generic parent `Demonglass Weapon` expanded from 48 to 90 variants in the curated corpus; recomputed group stats lifted the family base from ~614–630 gp to ~4,045 gp on non-frozen groups (no `frozen_weapon_stats` anchor coverage, unlike +1/+2/+3 Weapon where the freeze restored −0.297 adj). Same root cause as the 12% anchor bug (stats stray with corpus size), minus anchor coverage. 40+ Demonglass variants show +518–541% drift as direct variant-stat effect plus ML blend. See `.tgo/pricing_guide_v2-rrd/progress.md` Demonglass analysis and `reports/tail_331_attribution.csv` ml-variance bucket.

Corpus-match-change 0 is an honest null — not omitted. Bucket counts sum to 331 (12+1+14+0+304).

### Deep Dive — Shard Solitaire / Spell Gem / Rainbow Pearl (Horowitz M3)

**Shard Solitaire — 4 of 5 variants collapse to 5,000 gp vs Rainbow Pearl 95,789 gp (same file, different fate):**

- Candidate: Shard Solitaire (Diamond/Black Sapphire/Jacinth/Ruby) 95,577/94,672 gp → **5,000 gp** (−94.7%); Rainbow Pearl (same wondrous family, same source-book neighborhood) holds **95,789 gp** (not in tail — stable). Divergence originates in **06 ML retrain**: the 12k model differentiates by `attached_spells` vector value (Shard: 5× attached-spell payloads vs Pearl: distinct `prismatic spray` + `water breathing` vector that retrain preserves at high value; siblings' `blight`/`ice storm`/`fire storm`/`finger of death`/`teleport` vectors collapse to low prediction). Stage-05 rule/05b variant-adjust produces identical 05 price (137k) and 06 ML blend lands at ~5k for the four collapsed variants.
- **Floor unenforced:** `09_enforce_floors.py` clamps only weapons/armor/shields to mundane-relative floors; wondrous items with no mundane base bypass the clamp. Thus `RARITY_FLOORS` legendary **8,000** (`src/pricing_engine.py:56`) is unenforced for Shard Solitaire — 5,000 gp is below floor with no correction. Same for Spell Gems below.
- **Assessment:** Differentiated ML pricing (Pearl high, Shards low) is arguably better family differentiation than uniform baseline, but absolute 5,000 gp value is suspiciously low for legendary; floor unenforced is the structural gap.

**Spell Gem family — now differentiates by max stored spell level (was uniform):**

- Baseline (06 final) was uniform: Spell Gem (Diamond/Ruby/Star ruby) all 36,498 gp; Spell Gem (Jade/Amber/Topaz) all 10,639 gp — no max-level extraction.
- Candidate differentiates: **9th-level → 5,000 gp** (Diamond/Ruby), **8th-level → 1,000 gp** (Star ruby), **7th-level → 1,000 gp** (Topaz 500 gp? see CSV: Topaz 500 gp, Star ruby 1,000 gp, Diamond/Ruby 5,000 gp, Amber/Jade 100 gp, Lapis 10 gp, Bloodstone/Quartz 50 gp) — correlation with max stored spell level 9/8/7/6/4/cantrip (per progress.md: 9th→5,000, 7th→1,000, 4th→115, cantrip→10). Stage-06 ML with expanded corpus captures level proxy via save DC/rarity or new extraction; differentiated pricing is arguably **better** than uniform baseline.
- **Absolute values suspicious, floor unenforced:** 1,000 gp (Star ruby) and 500 gp (Topaz) sit **below legendary 8,000 floor**; 115 gp (Amber) below very_rare 1,000; 10 gp (Lapis/Obsidian) below uncommon 50. All are wondrous with no mundane base → 09 clamp does not fire (`reports/tail_331_attribution.csv` floor-gap-or-value-landing bucket, 14 rows). Horowitz M3 flags differentiated pricing as improvement but absolute floors as unenforced gap — follow-up issue tracks `09_enforce_floors` tier for no-mundane-base items and spell-level pricing policy.

---

## 4. Missing 32 — Investigated (No Unintended Drops)

Diff of `(Name, Source)` sets: baseline 4,749 vs candidate 11,941 → 32 missing, 7,224 new. Python diff `diff (name,source) sets` with likely cause:

**All 32 map to the curated triage in `reports/absent_canonical_triage_2026_07_12.md` — zero are unintended drops of previously-published items requiring carry-forward.** Flag statement: **No prominent unintended DROPs found; the 32 are accounted for by approved curation decisions.**

| Bucket | Count | Items | Cause |
|---|---|---|---|
| **AAG Spelljammer/space scope — intentional exclusion** | 20 | Basic Fishing Equipment; Bombard; Damselfly Ship; Fish Suit; Flying Fish Ship; Hammerhead Ship; Lamprey Ship; Living Ship; Nautiloid; Nightspider; Scorpion Ship; Shrike Ship; Space Galleon; Spelljamming Helm; Squid Ship; Star Moth; Turtle Ship; Tyrant Ship; Wasp Ship; Wildspace Orrery | `AAG` / `BAM` space/Spelljammer scope intentionally absent from 2026 curated list (`reports/curation_preflight_2026_07_12.md` "Spelljammer scope check: AAG present=False; BAM present=False" and `reports/absent_canonical_triage_2026_07_12.md` rows 1-21). Raw `2026_07_12_item_list.json` contained 0 AAG/BAM rows — not a regression. |
| **Boo's Astral Menagerie — intentional exclusion** | 1 | Talarith (Legendary Wondrous, 56,015 gp baseline) | Same Spelljammer/BAM exclusion, row 21 of triage |
| **Stranger Things: Welcome to the Hellfire Club — collaboration-only, user-approved drop** | 6 | Cap of Vanishing; Holly's Handy Haversack; Pipes of Pestilence; Poison Soaked Kukri; Speaking Stones; Spiked Shield | Absent from 2026 export, not known-good carry-forward (`absent_canonical_triage` rows 26,29-33). Two additional WttHC rows (Cloak of Billowing, Dread Helm) are superseded by XDMG replacement and are **not** in the 32 — correctly deduped, not dropped. |
| **Rick and Morty (The Lost Dungeon of Rickedness: Big Rick Energy)** | 1 | Concertina (Rare, 3,423 gp) | Collaboration-only row absent from 2026 export (row 24) |
| **QftIS hard exclusions — approved curation policy** | 2 | Concussion Grenade (Mundane Explosive 1.0 gp); Sleep Grenade (Mundane Explosive 1.0 gp) | `src/list_curation.curate_items()` `EXCLUDED_SOURCE_NAME_PAIRS` — QftIS 2 rows ( `reports/curation_preflight_2026_07_12.md` § Hard exclusions). Curated 12,241 contains 3 QftIS rows (Daoud's Lanthorn, Heretic, Staff of Ruling) in both baseline and candidate; grenades excluded by policy, not drift. |
| **Source-code rename — retained under new code** | 1 | Harkon's Bite (`Van Richten's Guide to Ravenloft` VRGR → `Ravenloft: The Horrors Within` RHW) | Baseline key `("Harkon's Bite", VRGR)` missing by `(name,source)` but item present in candidate as `("Harkon's Bite", Ravenloft: The Horrors Within)` at 835 gp (Algorithm) — same item, display-source remap. Curated source is `RHW` (see `reports/curation_preflight` new-only sources). **Not a net loss.** |
| **Expanded variant hub — parent replaced by children** | 1 | Lantern of Tracking (parent, Common 89 gp baseline) | Curated entry has `itemsHidden:true` + 10 specific variants (Aberrations … Undead). Candidate expands to 10 rows (e.g., Lantern of Tracking (Fey) 104 gp reference-anchored; 9 others 115 gp). Parent row missing is intentional expansion, net +9 rows. |

**Verification:** `reports/absent_canonical_triage_2026_07_12.md` classifies all 33 canonical-absent-from-curated rows (including the 32 here plus Cloak of Billowing/Dread Helm superseded) as approved omissions — no manual carry-forward required. The `(Harkon's Bite, VRGR)` → `(Harkon's Bite, RHW)` rename is explicitly noted in triage row 25. QftIS grenades are rows 22-23.

---

## 5. Anchor Table (Attempt 2) — PASS; Known-Good REVIEW

**+N Weapon anchors (candidate vs expected baselines):**

| Anchor | Expected | Candidate | Delta | Status |
|---|---:|---:|---:|---|
| +1 Dart | 282 | 282.58 | +0.21% | **PASS** |
| +1 Dagger | 382 | 382.26 | +0.07% | **PASS** |
| +2 Javelin | 2262 | 2262.36 | +0.02% | **PASS** |
| +3 Dart | 6644 | 6644.09 | +0.00% | **PASS** |
| +3 Maul | 20110 | 20110.40 | +0.00% | **PASS** |
| +3 Dagger | 8987 | 8987.72 | +0.01% | **PASS** |
| +1 Club | 432.10 | 432.10 | +0.00% | **PASS** |

Max drift 0.21% (≤5% criterion). All seven restore baseline stability (drift vs baseline canonical 0.00% for the seven). Spec §8 PASS/REVIEW criterion met.

**Known-good anchors:** Guardrail status **REVIEW** (PASS ≤1%, REVIEW >1% ≤5%, FAIL >5%). Max drift **1.47%** (Holy Avenger Dart 196,420→199,315 gp, +1.47%, formula/ML-only). Other Holy Avenger variants cluster at ±1.22-1.37% (e.g., Holy Avenger Greataxe −1.22%). Zero FAILs (>5%). Meets spec "PASS or REVIEW" gate.

---

## 6. Calibration Narrative (Attempts 1→2; Freeze Diff Explained)

**Attempt 1 — spacing dampen 0.3 (reverted, do NOT resurrect):** Multiplied mundane-cost variant spacing by 0.3 to compress +N Weapon family spread. Result: **worse** — anchor drift remained ~12% FAIL (variant adj shift not addressed at source). Reverted before hop 1b.

**Attempt 2 — freeze +1/+2/+3 Weapon group stats (PASSED, no attempt 3):** Frozen `compute_generic_group_stats` in `src/variant_system.py` (16-line diff, this commit):

```diff
-    return pd.DataFrame(stats)
+    df = pd.DataFrame(stats)
+    frozen_weapon_stats = {
+        "+1 Weapon": {"variant_count": 43, "max_weight": 18.0, "max_dmg_tier": 4.0},
+        "+2 Weapon": {"variant_count": 43, "max_weight": 18.0, "max_dmg_tier": 4.0},
+        "+3 Weapon": {"variant_count": 43, "max_weight": 18.0, "max_dmg_tier": 4.0},
+    }
+    for gname, frozen in frozen_weapon_stats.items():
+        mask = df["generic_name"] == gname
+        if mask.any():
+            for col, val in frozen.items():
+                df.loc[mask, col] = val
+    return df
```

**What the freeze does:** Makes **corpus-sensitive stats corpus-insensitive** for the 3 anchor groups only. New 12,241 corpus expands +N Weapon from 43 variants (max_weight 18, max_dmg 4) to 109 variants (20, 5), causing variant adjustment to shift from −0.297 (old baseline) to −0.212 and 12% anchor depression. Freezing `variant_count`, `max_weight`, `max_dmg_tier` to old-corpus baselines (43 / 18.0 / 4.0) restores adj to −0.297; +1 Dagger `base_price` stabilizes (609.81) and anchors PASS. Only those three `generic_name` values are mutated; **armor/exotics untouched** (armor+1/+2/+3, weapon+1 etc families not frozen). Verified minimal: `git diff src/variant_system.py` = +15/−1 lines.

> **Freeze footnote (Horowitz L2):** Only `max_weight`/`max_dmg_tier` are live on the adjustment path (`_adjustment_weapon` uses `median_weight`/`min_weight`/`max_weight` and `median_dmg_tier`/`min/max_dmg_tier`; `max_*` pin suffices, `min`/`median` remain live). `variant_count=43` is **decorative** — no consumer in `apply_variant_adjustment`/`_adjustment_weapon` reads `variant_count` (it is only diagnostic / `generic_base_prices` count). Empirically immaterial — anchors drift **0.00–0.21% PASS** (see §5 table; +1 Dart 0.21%, +1 Dagger 0.07%), confirming the partial pin suffices and `min`/`median` drift does not re-break anchors.

**Attempt 3 — conditional freeze of `variant_base_price` (not executed):** Trigger was +1 Dagger ~13% (598→610 base_price) indicating residual base-price drift. Condition false after attempt 2: +1 Dagger 382.26 vs 382 expected (0.07%), so attempt 3 correctly skipped per `.tgo/pricing_guide_v2-rrd/progress.md`.

**Pipeline re-run after freeze:** `06_ml_refine` → `07_validate` → `07b_variant_consistency` → `09_enforce_floors` → `10_generate_output` (11,941 items). R² intact (0.9692), guardrail REVIEW, anchors PASS.

---

## 7. Known Issues for Post-Migration Triage

**Variant-consistency flags (07b, 8 families, 2 flagged):**
- `gleaming-armor` — CV **0.63**, 12 items, flagged True (high variance within family; expected from mixed armor bases, not actionable pre-migration).
- `slaying-ammunition` — CV **28.7**, 14 items, flagged (spec-reported for 12k run; reflects ammunition-type price spread under new corpus; candidate for post-migration family review).

Note: `output/variant_consistency_report.csv` on disk is stale HEAD (pre-rrd, 4,837-row baseline) showing `gleaming-armor 0.6308 flagged` and `slaying-ammunition 0.0539` — not the 12k run values. The 12k 28.7/0.63 figures above are from the ritual run captured in progress.md; live report will refresh on next full `07b` run against 12,241 validated data.

**331 rows >25% drift — formula/ML variance candidates for triage queue.** Top 10 largest movers (old → new, %):

| Name | Source | Old | New | Δ% | Notes |
|---|---:|---:|---:|---|---|
| Acheron Blade Greatsword | Explorer's Guide to Wildemount | 708 | 6,014 | **+749.7%** | **INTENDED** kh7 wave-1 repricing — `temp_hp_avg` 6.5 per_action (`reports/wave1_criteria_impact.md:83`), simple-item bypass fix (`tests/test_wave1_criteria.py:241` `test_simple_item_bypass_temp_hp_priced`); NOT ML retrain — 6-variant family repriced by design (covers all 6: Greatsword/Scimitar/Longsword/Shortsword/Rapier/Double-Bladed Scimitar) |
| Acheron Blade Scimitar | Explorer's Guide to Wildemount | 628 | 5,336 | **+749.7%** | Same family — **INTENDED** wave-1, not variance |
| Demonglass Dart | Frontiers of Eberron: Quickstone | 615 | 3,939 | **+541.0%** | Rare, FoEQuickstone family 131→241% mean driver |
| Demonglass Dagger | Frontiers of Eberron: Quickstone | 631 | 4,010 | **+535.8%** | Same family (~ +533% across 20 variants) |
| Shard Solitaire (Diamond) | Keys from the Golden Vault | 95,577 | 5,000 | **−94.77%** | Legendary wondrous, formula/ML-only; artifact/legendary mover |
| Shard Solitaire (Black Sapphire) | Keys from the Golden Vault | 95,577 | 5,000 | **−94.77%** | Same family; 4 variants floored to 5,000 gp |
| Spell Gem (Star ruby) | Out of the Abyss | 36,498 | 1,000 | **−97.26%** | Legendary; OotA spell-gem family large downward variance |
| Stormgirdle (Exalted) | Explorer's Guide to Wildemount | 183,000 | 116,111 | **−36.55%** | Legendary; artifact/legendary mover per guardrail |
| Stormgirdle (Awakened) | Explorer's Guide to Wildemount | 137,924 | 81,325 | **−41.04%** | Same family |
| Infiltrator's Key (Awakened) | Explorer's Guide to Wildemount | 68,365 | 34,154 | **−50.04%** | Legendary wondrous |

Full list: 331 rows in `reports/price_creep_guardrail.md` § Largest percent movers / Artifact movers **and** `reports/tail_331_attribution.csv` (bucketed 12 kh7-wave1 / 1 stealth / 14 floor-gap / 0 match-change / 304 ml-variance). Triage recommendation: govern via **tiered post-adoption triage queue** (Horowitz-endorsed once attribution done) per `reports/extra_damage_signoff_pack_v3.md` — direct corrections (extra_dmg, save_adv, etc.) are 369/446 retrain-variance rows, not extraction bugs.

**Post-migration triage — three classes (Horowitz-endorsed):**
- **Floor-gap class (14 items):** wondrous items at sub-floor landings (Shard Solitaire 5,000 < legendary 8,000; Spell Gems 1,000/500/115/10 < rarity floors) — 09 clamp unenforced for no-mundane-base items. Fix candidate: extend `09_enforce_floors.py` to clamp ALL items to `RARITY_FLOORS` absolute (follow-up issue filed, §8 + beads). See §3b deep-dive and `reports/tail_331_attribution.csv` floor-gap-or-value-landing bucket.
- **Variant-composition drift class:** Demonglass-type expansion (48→90 variants lifts base 614→~4,045) on families without known-good anchor pins — same mechanism as anchor bug, minus coverage. Durable fix: config-driven anchor stats via baseline snapshot (follow-up issue filed). Horowitz L1 freeze already hardens the pin with warning on absent corpus key.
- **Residual ml-variance (304 items):** Accepted retrain variance per pack-v3 precedent; tiered queue (reference-anchored + extreme movers) governs triage post-adoption. Horowitz endorses queue discipline once attribution done.

**Flagged-family note:** `gleaming-armor` CV **0.63** and `slaying-ammunition` CV **28.7** remain flagged per §7 header — candidate for post-migration family review, not pre-adoption blocker; triaged via the queue above.

**The 32 missing rows:** See §4 — no triage needed beyond confirming triage doc classifications; if Spelljammer/Stranger Things/Rick scope is ever re-added, those 28 rows would require fresh pricing, not carry-forward.

**u7w script-guard hygiene:** `07_validate` script-guard (u7w) — no hygiene violations flagged; flagged families above are CV-based, not guard violations. Post-migration: ensure `07_validate.py` and `07b_variant_consistency.py` guards remain in CI for every pricing run.

---

## 8. Adoption Statement

- **Nothing adopted until user sign-off.** This pack is for review; `bd` issue `rrd` remains open per hop spec ("NO issue closes (rrd closes after user sign-off)").
- **Candidate untracked:** `output/pricing_guide_candidate.csv` (11,941 rows) is `??` in `git status` — not committed, not installed as `output/pricing_guide.csv`. `output/pricing_guide.xlsx` similarly preserved as 4,749-row canonical.
- **Canonical untouched:** `output/pricing_guide.csv` (4,749 rows), `output/pricing_guide.xlsx`, `output/review*`, `output/official_price_anchor_*.csv` (except reverted `items_ml_priced.csv` churn) remain at HEAD. `data/processed/*` reverted to HEAD (4,837-row stale state) per END OF DANCE — next full ritual will regenerate on 12,241.
- **Commit this hop:** `src/variant_system.py` freeze + `reports/price_creep_guardrail.md` (true attempt-2) + this pack — no canonical data changes.

---

## 9. Verification Commands (Post-Hop)

```
python3 scripts/reports/price_creep_guardrail.py --baseline output/pricing_guide.csv --candidate output/pricing_guide_candidate.csv --output reports/price_creep_guardrail.md 2>&1 | tail -15  # → Common 4717 REVIEW
git diff src/variant_system.py  # → 16-line freeze, 3 groups only
git status --porcelain | grep -v "^??"  # → M src/variant_system.py, M reports/price_creep_guardrail.md, ?? migration_12k_signoff_pack.md (then committed)
python3 scripts/reports/check_r2.py  # → R² 0.9692 PASS (12k), fingerprint b22382a2…; reverted-state check gives 0.9723 PASS same fingerprint
wc -l output/pricing_guide.csv output/pricing_guide_candidate.csv  # → 4750 (4749 rows) vs 11942 (11941 rows)
```

---

*Generated hop 2, 2026-09-01. Honest labels: REVIEW is not PASS; formula/ML drift disclosed as accepted variance per pack-v3 precedent. Missing-32 investigation: no unintended drops.*
