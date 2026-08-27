# Extra Damage Sign-Off Pack — 2026-07-12 Candidate

> Source: `reports/price_creep_guardrail.md` (Price Creep Guardrail, Baseline `output/pricing_guide.csv` vs Candidate `output/pricing_guide_candidate.csv`) and `reports/extra_damage_impact_2026_07_12.md` (extra_damage_avg Current Canonical Impact, 4,837 rows analyzed, 331 changed). Both reports are current in-tree. No pipeline re-run was performed to build this pack; all numbers are taken verbatim from those two reports. Candidate CSV `output/pricing_guide_candidate.csv` is confirmed current (postdates last `src` edit).

---

## SIGN-OFF QUESTION

**You must decide: accept `output/pricing_guide_candidate.csv` into canonical or hold for further investigation.**

- If you accept, 4,748 common rows move at median 0.00% / mean 7.04% (guardrail current), with the Rare tier (+20.17% mean, 1,411 rows) driven disproportionately by the Quickstone Demonglass cluster (+~673% each) and a handful of formula/ML-only legendaries.
- If you hold, the blocking question is Section A: the Demonglass drift is **not** caused by the extra-damage fix that this candidate was built to validate. The true driver (suspected ML/variant handling or `save_advantage` extraction changes) must be investigated before the 25-row Demonglass cluster can be accepted.
- Guardrail verdict is **REVIEW** (PASS ≤1%, REVIEW >1%, FAIL >5%) — no FAIL, but above PASS. The known-good anchors in Section C are within FAIL threshold but above PASS for several items.
- Recommendation in this pack: **do not accept the Demonglass cluster without a targeted driver investigation** (see Section A). Other sections may be acceptable on their own but are entangled in the same candidate; decide cluster-by-cluster or reject the candidate and regenerate after the driver is found.

---

## Section A — Quickstone "Demonglass" Cluster (CRITICAL: NOT extra-damage)

**Guardrail facts:**

- Source `Frontiers of Eberron: Quickstone` is the dominant outlier: 111 rows, median drift **175.00%**, mean drift **311.53%**, median gp drift **1,331 gp**, mean gp drift **2,101 gp** (guardrail Drift by source table).
- Largest percent movers table is entirely Demonglass items — 25 rows listed, all Rare, all reference-anchored, each ~+672–675%:

| Name | Baseline | Candidate | Delta gp | Delta % |
|---|---|---:|---:|---:|
| Demonglass Dart | 615 gp | 4,765 gp | 4,150 gp | 675.23% |
| Demonglass Dagger | 631 gp | 4,882 gp | 4,251 gp | 674.12% |
| Demonglass Club | 639 gp | 4,940 gp | 4,302 gp | 673.58% |
| Demonglass Handaxe | 639 gp | 4,940 gp | 4,302 gp | 673.58% |
| Demonglass Hooked Shortspear | 639 gp | 4,940 gp | 4,302 gp | 673.58% |
| Demonglass Hoopak | 639 gp | 4,940 gp | 4,302 gp | 673.58% |
| Demonglass Javelin | 639 gp | 4,940 gp | 4,302 gp | 673.58% |
| Demonglass Light Hammer | 639 gp | 4,940 gp | 4,302 gp | 673.58% |
| Demonglass Shortbow | 639 gp | 4,940 gp | 4,302 gp | 673.58% |
| Demonglass Shortsword | 639 gp | 4,940 gp | 4,302 gp | 673.58% |
| Demonglass Sickle | 639 gp | 4,940 gp | 4,302 gp | 673.58% |
| Demonglass Blowgun | 643 gp | 4,972 gp | 4,329 gp | 673.29% |
| Demonglass Hand Crossbow | 643 gp | 4,975 gp | 4,331 gp | 673.27% |
| Demonglass Scimitar | 643 gp | 4,975 gp | 4,331 gp | 673.27% |
| Demonglass Sling | 643 gp | 4,975 gp | 4,331 gp | 673.27% |
| Demonglass Spear | 643 gp | 4,975 gp | 4,331 gp | 673.27% |
| Demonglass Whip | 643 gp | 4,975 gp | 4,331 gp | 673.27% |
| Demonglass Mace | 647 gp | 4,999 gp | 4,352 gp | 673.06% |
| Demonglass Quarterstaff | 647 gp | 4,999 gp | 4,352 gp | 673.06% |
| Demonglass Flail | 663 gp | 5,121 gp | 4,458 gp | 672.02% |
| Demonglass Longbow | 663 gp | 5,121 gp | 4,458 gp | 672.02% |
| Demonglass Rapier | 663 gp | 5,121 gp | 4,458 gp | 672.02% |
| Demonglass War Pick | 663 gp | 5,121 gp | 4,458 gp | 672.02% |
| Demonglass Longsword | 668 gp | 5,156 gp | 4,487 gp | 671.73% |
| Demonglass Yklwa | 668 gp | 5,156 gp | 4,487 gp | 671.73% |

(Table verbatim from `reports/price_creep_guardrail.md` ## Largest percent movers.)

**CRITICAL finding from prior analysis:**

Their `extra_damage_avg` is **0.0 in BOTH old and new extraction**. The prior extra_damage impact report (`reports/extra_damage_impact_2026_07_12.md`) compares 4,837 canonical rows (331 changed, total extra_damage_avg 3,680.53 → 5,641, weighted 3,680.53 → 4,321.65, direct exposure 870,562 gp) and its 331 changed rows are exclusively Vicious, Dragon Wing / Dragon Slayer, Bane, Giant Slayer, Corpse Slayer, and Dragon's Wrath families — no Demonglass rows appear. The extra-damage fix correctly adds unconditional `2d6` (Vicious, avg 7, mult 1.0) and conditional `vs_creature_type` / `on_crit` with multipliers 0.25 / 0.05 for the other families. Because Demonglass has no extra-damage prose in either extraction, this candidate's ~+673% drift on that cluster is **not** explained by the extra-damage work.

**Suspected drivers (honest open question):**

- ML/variant handling (Demonglass items are weapon variants; variant-group pricing or ML feature changes could re-price the entire family together).
- `save_advantage` extraction changes (separate Phase 1 hardening touched advantage/disadvantage and generic saving-throw extraction; if Demonglass prose carries advantage or save text, a mis-attributed criterion could leak into price).
- Other criterion drift introduced between baseline and candidate that was not isolated to extra_damage.

No evidence in the two source reports isolates the exact cause; the reports themselves note anchor-tier / ML R² checks require pipeline metadata not present in final CSV snapshots.

**Recommendation:**

Investigate the true driver before accepting this cluster. Suggested targeted checks (without a full pipeline re-run until a hypothesis is ready):
1. Diff `items_criteria.csv` (or criteria preflight) between baseline and candidate for the 25 Demonglass rows — compare every price-bearing criterion, not just `extra_damage_avg`.
2. Re-run the guardrail after temporarily excluding the Demonglass family to see Rare-tier residual drift.
3. Audit variant-group and ML feature handling for the Quickstone source across the two code states.

Do not accept the Demonglass prices (631→4,882 gp example) into canonical until step 1 explains the ~+4,250 gp jump.

---

## Section B — Rare-Tier Drift and Top Drivers

**Rare-tier aggregate:**

- 1,411 Rare rows: median % drift **0.00%**, mean % drift **20.17%**, median gp drift **0 gp**, mean gp drift **-116 gp** (guardrail ## Drift by rarity).

The gap between median 0.00% and mean 20.17% is driven by a long right tail; the Rare mean is the highest of any rarity tier (next is Uncommon 5.14%).

**Top drivers (from guardrail's largest-movers and largest-percent-movers tables):**

1. **Demonglass cluster (Rare, reference-anchored)** — 25 rows listed above, each +~673%, +4,150 to +4,487 gp. This cluster alone explains a large share of Rare's mean. The broader Quickstone source (+311% mean across 111 rows) implies additional Quickstone Rare rows beyond the 25 also moved materially.
2. **Breastplate of Kamvuul Norek** — Exploring Eberron (2024), Legendary, Medium Armor, formula/ML-only: **103,206 gp → 151,841 gp, +48,635 gp, +47.12%**. Appears as #1 in both Largest movers and Artifact/legendary movers; not Rare but shows formula/ML-only volatility in the same candidate.
3. Other large movers that intersect Rare or contrast the Rare signal (for context on candidate-wide volatility):
   - Blast Scepter (Very Rare, Rod, formula/ML-only): 34,122 gp → 48,454 gp (+14,332 gp, +42.00%)
   - Stonebreaker's Breastplate (Legendary, Medium Armor): 58,762 gp → 77,083 gp (+31.18%)
   - Euryale's Aegis (Legendary, Shield): 68,121 gp → 86,103 gp (+26.40%)
   - Harp of Gilded Plenty (Legendary, Musical Instrument): 89,148 gp → 49,539 gp (-44.43%) — opposite direction, same candidate
   - Dragonlance Pike/Lance (Legendary, Melee Weapon, reference-anchored): ~-24% each

**What the guardrail lists for Rare specifically:** the only Rare rows named in the largest-tables are the Demonglass items. No other Rare names appear in the top absolute or percent movers, which reinforces that the Rare mean is Demonglass-dominated. The remaining ~1,386 Rare rows are not individually tabulated but collectively include the Vicious / Dragon Slayer / Bane / Giant Slayer families that did receive extra_damage changes (see extra_damage report: each Vicious row gains weighted delta 7 at 1,500 gp/pt = 10,500 gp direct exposure; each Dragon Slayer gains 2.625 pts = 3,938 gp).

Guardrail by-type confirms the Rare signal is weapon-heavy: Melee Weapon mean +13.78% (1,863 rows), Ranged Weapon +12.57% (536 rows).

---

## Section C — Known-Good Anchors

Guardrail Known-good anchors status: **REVIEW** (PASS ≤1% drift; REVIEW >1%; FAIL >5%). All listed anchors are below the 5% FAIL threshold, but several exceed the 1% PASS line — hence REVIEW, not PASS.

Configured anchor families when present: Holy Avenger, Defender, Vorpal Sword, +1/+2/+3 Weapon/Armor, Dragon Slayer, Giant Slayer, Vicious Weapon families. Listed rows:

| Name | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---:|---:|---:|---|
| Vorpal Glaive | 54,605 gp | 54,004 gp | -600 gp | -1.10% | reference-anchored |
| Vorpal Greatsword | 54,605 gp | 54,004 gp | -600 gp | -1.10% | reference-anchored |
| Vorpal Longsword | 54,605 gp | 54,004 gp | -600 gp | -1.10% | reference-anchored |
| Vorpal Scimitar | 54,605 gp | 54,004 gp | -600 gp | -1.10% | reference-anchored |
| +3 Leather Armor | 29,832 gp | 29,508 gp | -324 gp | -1.09% | reference-anchored |
| +3 Padded Armor | 29,832 gp | 29,508 gp | -324 gp | -1.09% | reference-anchored |
| +3 Studded Leather Armor | 29,832 gp | 29,508 gp | -324 gp | -1.09% | reference-anchored |
| +2 Moon Sickle | 12,022 gp | 12,299 gp | 277 gp | 2.31% | reference-anchored |
| +2 Chain Mail | 8,454 gp | 8,594 gp | 140 gp | 1.66% | reference-anchored |
| +2 Plate Armor | 8,454 gp | 8,594 gp | 140 gp | 1.66% | reference-anchored |
| +2 Ring Mail | 8,454 gp | 8,594 gp | 140 gp | 1.66% | reference-anchored |
| +2 Splint Armor | 8,454 gp | 8,594 gp | 140 gp | 1.66% | reference-anchored |
| +2 Leather Armor | 8,426 gp | 8,332 gp | -94 gp | -1.11% | reference-anchored |
| +2 Padded Armor | 8,426 gp | 8,332 gp | -94 gp | -1.11% | reference-anchored |
| +2 Studded Leather Armor | 8,426 gp | 8,332 gp | -94 gp | -1.11% | reference-anchored |
| +3 Moon Sickle | 32,952 gp | 32,876 gp | -75 gp | -0.23% | reference-anchored |
| +3 Chain Mail | 29,656 gp | 29,582 gp | -74 gp | -0.25% | reference-anchored |
| +3 Ring Mail | 29,656 gp | 29,582 gp | -74 gp | -0.25% | reference-anchored |
| +3 Splint Armor | 29,656 gp | 29,582 gp | -74 gp | -0.25% | reference-anchored |
| +1 Moon Sickle | 3,925 gp | 3,858 gp | -67 gp | -1.70% | reference-anchored |

Requested highlights:
- **Vorpal family: -1.10%** (all four weapons, 54,605→54,004 gp). The guardrail's PASS line is ≤1%; Vorpal is **borderline-pass** (just over 1%, so REVIEW, not FAIL). Given these are high-value legendary reference-anchored rows, a -600 gp move is small in absolute terms but crosses the review threshold by 0.10 points — warrants noting, not blocking.
- **+2 Plate (and +2 Chain/Splint/Ring Mail): +1.66%** (8,454→8,594 gp, +140 gp). Same comment applies to all +2 heavy armor at that price point.
- **+1 Moon Sickle: -1.70%** (3,925→3,858 gp, -67 gp).
- +2 Moon Sickle 2.31% and +2 leather variants -1.11% / +3 variants -1.09% to -0.25% complete the picture.

**Interpretation:** no anchor fails (>5%), so the candidate does not break the known-good FAIL gate, but it is not clean PASS. Plate/armor moves at +1.66% / -1.11% tie to the AC-bonus scaling review — small additive or ML shifts to armor pricing could produce these symmetric moves. Track armor calibration separately if further AC-bonus tuning is planned. Vorpal at -1.10% should be treated as borderline; if a stricter 1% PASS is meaningful for legendaries, document the allowance.

---

## Section D — Summary Stats and Split

**Aggregate drift (4,748 common rows):**

- Common rows: **4,748** (1 new candidate row, 1 missing candidate row)
- Median % drift: **0.00%**
- Mean % drift: **7.04%** (guardrail current); the issue tracker notes field earlier recorded 10.88% on an interim candidate snapshot — the current guardrail report is authoritative at 7.04%; the range **+7–11%** brackets interim vs final in this candidate cycle.
- Median gp drift: **0 gp**
- Mean gp drift: **-7 gp** (percent mean up while gp mean slightly negative implies many small-dollar items drifting up by large percent while a few expensive items drifted down)
- Rows >5% drift: **473**
- Rows >10% drift: **318**
- Rows >25% drift: **174**

**Reference-anchored vs formula/ML-only:**

| Split | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| reference-anchored | 3,285 | 0.00% | 9.83% | 0 gp | -59 gp |
| formula/ML-only | 1,463 | 0.00% | 0.79% | 0 gp | 111 gp |

Explicit note: **reference-anchored rows (3,285) drive the mean while formula/ML-only rows (1,463) moved only +0.79%**. This is counter-intuitive — reference anchoring was expected to dampen drift, but here the anchoring does not prevent the Demonglass and other reference-anchored shifts. Formula/ML-only Legendary drift (+0.51% mean across 639 rows) and Artifact 0.00% are comparatively flat.

**Distribution by rarity / type / source (abbrev):**

- By rarity: Rare +20.17% mean is the outlier (see Section B); Uncommon +5.14%; Very Rare -0.02%; Legendary +0.51%; others near 0% (guardrail table verbatim).
- By type: Melee Weapon +13.78% and Ranged Weapon +12.57% confirm weapon-concentrated drift.
- By source: Quickstone 311.53% mean dwarfs all other sources; next largest by magnitude is Bigby Presents 6.07%, then Monster Manual 3.09%; most sources are within ±1%.

**What remains unknown from these CSV snapshots:**

- Anchor-tier transitions and ML R² / double-count audit require pipeline metadata not present in final CSVs (guardrail ## Anchor-tier transitions note).
- Extra_damage impact is direct criterion exposure (870,562 gp total, 641.125 weighted points), not final-price; final-price deltas are in the guardrail.

---

## Inputs and Limitations

- Candidate generated in a temporary worktree from current canonical inputs with current extraction code, then copied to `output/pricing_guide_candidate.csv`; compared against `output/pricing_guide.csv` (guardrail header).
- Extra_damage impact uses markdown prose input shape and rarity-specific coefficients (1,500 gp/pt below legendary, 3,000 gp/pt for legendary/artifact) after condition multipliers (1.0 unconditional, 0.25 vs_creature_type, 0.05 on_crit).
- This pack does not re-run the pipeline, regenerate data, or add new numbers beyond the two source reports. Untouched snapshot files and patch files remain untracked per repo rules.

## Recommendation Summary

1. **Hold** on accepting the Demonglass cluster — investigate ML/variant or save_advantage driver (Section A).
2. **Conditional** on other tiers: the Rare mean excluding Demonglass needs recalculation; known-good anchors are REVIEW (not FAIL) and could be accepted with a recorded allowance for Vorpal -1.10% and armor +1.66% if the Demonglass driver is isolated.
3. **Gate remains** user sign-off on this evidence pack before canonical migration (pricing_guide_v2-r1o).
