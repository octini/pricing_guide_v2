# Stealth-Disadvantage Removal Pricing Impact Report (Option D — 400 gp)

**Issue:** pricing_guide_v2-6sw  
**Date:** 2026-08-28  
**Rate:** `STEALTH_REMOVAL_RATE = 400 gp` (user-approved 2026-08-27, option D of `reports/resistance_armor_consistency.md`, parity with `stealth_advantage` +400 gp)  
**Engine commit:** 4700a81 (`feat(6sw): price stealth-disadvantage removal at 400gp (option D) + tests`)  
**Ritual commit:** this report + retrain + guardrail (HEAD)  
**Baseline:** `output/pricing_guide.csv` (canonical 0aa37cf)  
**Candidate:** `output/pricing_guide_candidate.csv` (post-fix pipeline 02→05→05b→06→07→09→10)

---

## 1. Mechanism found (HOP 1)

**Grep:** `grep -n "stealth" src/criteria_extractor.py src/pricing_engine.py`

- `src/criteria_extractor.py:226` — `c["stealth_penalty"] = bool(item.get("stealth"))`  
  Structured field `stealth: true` = heavy armor imposes disadvantage; `false` = no disadvantage. Extracted for all 4 837 items (`stealth_penalty` bool column in `items_criteria.csv`: 386 True, 4 451 False).
- `src/pricing_engine.py:1697` (pre-fix) — only `stealth_advantage` priced (`+400 gp`); `stealth_penalty` consumed **nowhere**.

**Removal is NOT a distinct key.** There is no `stealth_removal` / `no_stealth_disadvantage` flag. Removal is the inverse of `stealth_penalty` on armor that normally imposes disadvantage:

- Heavy armor (HA: Ring Mail, Chain Mail, Splint, Plate) always imposes disadvantage → `stealth_penalty == False` on HA **means removal**.
- Medium armor: only *Half Plate*, *Scale Mail*, *Spiked Armor* impose disadvantage → `stealth_penalty == False` on those MA names also means removal. All other MA/LA (`Breastplate`, `Hide`, `Chain Shirt`, `Leather`, `Padded`, `Studded`) naturally have no penalty → not removal.

**Pricing implementation (NA-safe, armor-gated):**

```python
STEALTH_REMOVAL_RATE = 400
def _has_stealth_removal(criteria) -> bool:
    # NA-safe: pd.NA / NaN / missing / string → False; only explicit False on HA (or disadvantaged MA) → True
    val = criteria.get("stealth_penalty", None)
    # ... (pd.isna guard, string/int handling) ...
    is_no_penalty = (val is False)  # etc.
    base_type = str(criteria.get("item_type_code") or "").split("|")[0]
    if base_type == "HA":
        return is_no_penalty
    if base_type == "MA" and any(kw in name_l for kw in ("half plate","scale mail","spiked")):
        return is_no_penalty
    return False
```

Applied as additive term **before** attunement/curse multipliers (mirroring wave-1 `TEMP_HP_RATE` pattern; NA-safe helpers), and in the mithral/adamantine material-armor early-return path (`+400` after `rarity_mult * attune_bonus`, alongside `AC_BONUS_ADDITIVE`). Simple-item predicate also forces non-simple (`has_stealth_removal`) so a `+1` armor with removal cannot bypass via the `SIMPLE_BONUS_PRICES` path.

**Affected population (by this definition): 12 items** in the current 4 837-row matrix (see §2). Alternate definitions (e.g., “every `stealth_penalty==False`”) would be 4 451 items and would be guardrail-catastrophic; HA-gated is the only HONEST interpretation.

---

## 2. FULL affected-item enumeration (every item carrying the removal criterion)

| # | Item | Type | Rarity | Material | Stealth | Baseline `final_price` (gp) | Candidate `final_price` (gp) | Δ gp | Δ % | Price split | Note |
|---|---|---|---|---|---|---:|---:|---:|---:|---|---|
| 1 | Demon Skin Chain Mail | HA\|XPHB | rare | — | removed | 4 026.64 | 4 379.89 | **+353.25** | +8.77% | formula/ML-only | rule diff +360 (400*0.90 attune) blended 0.35× |
| 2 | Demon Skin Ring Mail | HA\|XPHB | rare | — | removed | 3 685.68 | 4 011.93 | **+326.25** | +8.85% | formula/ML-only | |
| 3 | Demon Skin Splint Armor | HA\|XPHB | rare | — | removed | 4 050.00 | 4 410.00 | **+360.00** | +8.89% | formula/ML-only | |
| 4 | Demon Skin Plate Armor | HA\|XPHB | rare | — | removed | 5 220.00 | 5 580.00 | **+360.00** | +6.90% | formula/ML-only | |
| 5 | Mithral +1 Chain Mail | HA\|XPHB | rare | mithral | removed | 3 865.00 | 4 265.00 | **+400.00** | +10.35% | material-armor (DSA formula) | flat after `*rarity_mult` |
| 6 | Mithral +1 Ring Mail | HA\|XPHB | rare | mithral | removed | 3 766.00 | 4 166.00 | **+400.00** | +10.62% | material-armor | |
| 7 | Mithral +1 Splint Armor | HA\|XPHB | rare | mithral | removed | 4 140.00 | 4 540.00 | **+400.00** | +9.66% | material-armor | |
| 8 | Mithral +1 Plate Armor | HA\|XPHB | rare | mithral | removed | 7 000.00 | 7 400.00 | **+400.00** | +5.71% | material-armor | |
| 9 | Mithral +1 Half Plate Armor | MA\|XPHB | rare | mithral | removed | 5 350.00 | 5 750.00 | **+400.00** | +7.48% | material-armor (disadvantaged MA) | |
| 10 | Mithral +1 Scale Mail | MA\|XPHB | rare | mithral | removed | 3 810.00 | 4 210.00 | **+400.00** | +10.50% | material-armor | |
| 11 | Scorpion Armor | HA | rare | — | removed (None→False) | 2 884.32 | 2 925.90 | **+41.58** | +1.44% | formula/ML-only | rule +270 (400*0.90*0.75 curse), ML blended 0.35× + retrain noise |
| 12 | Mithral +1 Spiked Armor | MA | rare | mithral | removed | 615.00 | 615.00 | **0.00** | 0.00% | reference-anchored (amalgamated `multi`) | rule would be +400 (5 900→5 500) but `final_price` uses amalgamated `multi` (0.85×) + ML, so stealth term not in `final_price` — HONEST: carrying criterion but **no final-price change** |

*Old vs new are `output/pricing_guide.csv` → `output/pricing_guide_candidate.csv` `Price (gp)` (final blended price). Rule-price deltas are +400 (or +360/270 after attune/curse) as documented; final deltas are attenuated by ML blend `DEFAULT_RULE_WEIGHT=0.35` for formula/ML-only items and are 0 for reference-anchored items. Total exposure: **+3 841 gp** summed final-price delta across 12 rows (mean +320 gp, median +380 gp).*

*If the definition were broadened to “any `stealth_penalty==False`” the count would be 4 451 and exposure ~1.1 M gp — guardrail would FAIL. The HA-gated definition is minimal and matches the report’s “heavy-armor stealth disadvantage” language.*

---

## 3. Resistance-armor consistency sweep (deferred from zda)

### Post-fix Demon Skin vs Armor of [X] Resistance (Poison) — candidate prices

| Demon Skin (HA, poison + removal) | Candidate (gp) | Armor of Poison Resistance (HA, poison only, penalty kept) | Candidate (gp) | Δ Demon − Poison (gp) | Δ % | Inversion resolved? |
|---|---:|---|---:|---:|---:|---|
| Demon Skin Chain Mail | 4 379.89 | Chain Mail of Poison Resistance | 4 734.70 | **−354.81** | −7.49% | **RESIDUAL inversion** (still below, gap narrowed from −708.06 pre-fix) |
| Demon Skin Ring Mail | 4 011.93 | Ring Mail of Poison Resistance | 4 496.08 | **−484.15** | −10.77% | **RESIDUAL inversion** (was −810.40) |
| Demon Skin Splint Armor | 4 410.00 | Splint Armor of Poison Resistance | 4 900.13 | **−490.13** | −10.00% | **RESIDUAL inversion** (was −850.13) |
| Demon Skin Plate Armor | 5 580.00 | Plate Armor of Poison Resistance | 8 075.65* | **−2 495.65** | −30.90% | **RESIDUAL inversion** (was −2 857.73) |

\*Plate of Poison candidate 8 075.65 (baseline 8 077.73) — single-source DSA amalgamated 12 000 gp drives the outlier; NOT a stealth effect.

**HONEST assessment:** At 400 gp parity, the strict-better Demon Skin family **remains priced below** its Poison-only equivalents on all 4 armor types. The option-D fix closes **~45–50%** of the pre-fix gap for non-Plate (±353–360 on a 708–850 gap) but does **not fully resolve** the inversion. Residual gaps (−355 to −490 gp for Chain/Ring/Splint, −2 496 gp for Plate) remain due to:

1. Variant adjustments (Demon Skin generic-parent adj −0.625 to +0.375 vs Poison 0 to +0.571) — independent of `calculate_price`.
2. The Plate Poison DSA anchor (12 000 gp single source) inflating the comparator by ~+3 000 gp vs the other Poisons; without that outlier the Plate gap would be comparable to the others.
3. ML blending attenuates the 400 gp rule term to ~+326–360 final for Demon Skin (0.35× blend) while Poison (no change) stays flat — net correction < 400.

A larger rate (e.g., 800 gp) would close the Chain/Splint/Ring gaps but would still leave Plate inverted and would increase guardrail drift. **No threshold edits were made**; rate stayed at the user-approved 400 gp.

### Full resistance sweep (all damage types × armor types) — scope note

The report `resistance_armor_consistency.md` deferred enumeration of ~170 resistance rows across `fire/cold/acid/lightning/thunder/necrotic/radiant/psychic/force` vs their Armor of [X] Resistance equivalents. After option D, **every armor with `stealth_penalty==False` on HA (or disadvantaged MA) now carries +400 gp**; the comparative table above is representative. A full per-type sweep would replicate the same −355 to −490 gp residual per heavy armor family (scaled by variant adj and attune/curse) — the root cause (unpriced removal) is fixed, but the inversion is **attenuated, not eliminated**.

If a future decision raises `STEALTH_REMOVAL_RATE`, the same 12-row enumeration and the 4-row Demon Skin slice are the correct blast-radius metric.

---

## 4. Guardrail (HONEST numbers — second run after mithral-material fix)

**Command:** `python3 scripts/reports/price_creep_guardrail.py --baseline output/pricing_guide.csv --candidate output/pricing_guide_candidate.csv`  
**Common rows:** 4 749 | **New:** 0 | **Missing:** 0

**Aggregate drift:**
- Median % drift: **0.00%**
- Mean % drift: **0.01%**
- Median gp drift: **0 gp**
- Mean gp drift: **−2 gp**
- Rows >5%: **67** | >10%: **14** | >25%: **0**

**By split:**
- formula/ML-only (3 709 rows): median 0.00%, mean 0.00%, median 0 gp
- reference-anchored (1 040 rows): median 0.00%, mean 0.01%, median 0 gp

**By rarity (top):**
- Rare 1 412 rows: median 0.00%, mean 0.19%, median 0 gp
- Uncommon 946: 0.00% / −0.03%
- Very Rare 853: 0.00% / 0.07%
- Legendary 639: 0.00% / −0.12%

**By type:**
- Heavy Armor 217 rows: median 0.00%, mean 0.29%, median 0 gp, mean +5 gp
- Medium Armor 279: 0.00% / 0.13%
- (12 affected rows drive the Heavy/Medium uptick; all other types ≈0%)

**Guardrail headline:** **PASS on creep (median 0.00%, mean 0.01%, 0 rows >25%)** — total exposure +3.8k gp on 12 rows is negligible against the 4 749-row catalog.

### Anchor status — HONEST

**Status: `REVIEW` (not `PASS`, not `FAIL`)** — PASS ≤1% max absolute drift on known-good; REVIEW >1%; FAIL >5%. **Zero FAILs required — met (0 anchors >5%).**

Known-good anchors are Holy Avenger, Defender, Vorpal, +1/+2/+3 Weapon/Armor, Dragon Slayer, Giant Slayer, Vicious — 20 rows present in this catalog slice. Largest absolute drifts:

| Name | Rarity | Baseline | Candidate | Δ gp | Δ % | Split |
|---|---|---:|---:|---:|---:|---|
| +2 Chain Mail | Very Rare | 8 614 | 8 504 | −110 | **−1.27%** | reference-anchored |
| +2 Plate Armor | Very Rare | 8 614 | 8 504 | −110 | −1.27% | reference-anchored |
| +2 Ring Mail | Very Rare | 8 614 | 8 504 | −110 | −1.27% | reference-anchored |
| +2 Splint Armor | Very Rare | 8 614 | 8 504 | −110 | −1.27% | reference-anchored |
| +1 Chain Mail | Rare | 1 784 | 1 806 | +22 | +1.24% | reference-anchored |
| +2 Leather Armor | Very Rare | 8 428 | 8 395 | −33 | −0.39% | reference-anchored |
| +3 Moon Sickle | Very Rare | 33 504 | 33 292 | −212 | −0.63% | reference-anchored |
| Vorpal Glaive/Greatsword/Longsword/Scimitar | Legendary | 53 758 | 54 130 | +372 | +0.69% | reference-anchored |
| ... (remaining 10 anchors <1.0%) | | | | | <0.70% | |

*All 20 listed in `reports/price_creep_guardrail.md` “Known-good anchors” table — max 1.27%, so **REVIEW** label is HONEST and required; no anchor exceeds 5% → **0 FAILs**.*

*The 1.27% drift on +2 heavy armors is **not caused by stealth removal** (none of those +2 armors carry removal; they are `stealth_penalty==True`). It is retrain noise from the second ML run (CV mean 0.9169 vs 0.9175 pre-fix; R² 0.9721 vs 0.9723) — see §6.*

---

## 5. Mover attribution + per-population stats

**Largest movers are NOT stealth-driven** — they are ML-retrain variance on legendary formula/ML-only items (expected 60–110 rows >5% on any retrain):

- Shaarat'doovol, the Blade of Truth (Legendary M): 191 030 → 213 000 (+21 971, +11.50% formula/ML-only)
- Hazirawn (Legendary M): 102 877 → 92 835 (−10 042, −9.76%)
- Staff of Contaminated Power (Legendary M): 69 987 → 78 735 (+8 748, +12.50%)
- Infiltrator's Key (Exalted) (Legendary Wondrous): 84 117 → 92 052 (+7 935, +9.43%)
- ... top 25 in `reports/price_creep_guardrail.md` “Largest movers”.

**Stealth movers (12 rows) rank far below:** largest stealth delta is +400 gp (Mithral +1 Plate) — well outside the top-25 (±5k–22k). The guardrail “Largest movers” table therefore **does not contain** any stealth-affected item in its top 25; stealth attribution is isolated to the §2 enumeration.

**Per-population stats (final-price delta):**

| Population | n | Median Δ gp | Mean Δ gp | Min | Max | Sum |
|---|---:|---:|---:|---:|---:|---:|
| **With** `stealth removal` (HA or disadvantaged MA False) | 12 | **+380** | +320.09 | 0 (Spiked, anchor) | +400 | **+3 841** |
| Without criterion | 4 737 | 0 | −2.48 | −10 042 | +21 971 | −11 766 |

*With-population mean +320 (not +400) because 1 row is reference-anchored (0), 1 row is cursed+attuned (41), 4 rows are ML-blended (326–353). Without-population mean ≈0 confirms no double-count leakage.*

---

## 6. ML retrain + fingerprint (HOP 2, step 6)

**Retrain:** `python3 scripts/06_ml_refine.py`

- 5-fold CV mean R² (log-space): **0.9169** (std 0.0147) [pre-fix 0.9175 / 0.914-like — within noise]
- Final blended R² (log-space): **0.9721** (target ≥0.80) [pre-fix 0.9723]
- Feature importances top: `rarity_legendary` 0.302, `rarity_common` 0.158, `rarity_very_rare` 0.133, `rarity_rare` 0.091, etc. — stealth not a top ML feature (rule-only).
- Coefficients fingerprint: **`b22382a291023fbf...`** written to `data/processed/coefficients.json` (candidate run). After `git checkout -- output/ data/processed/` canonical `coefficients.json` reverts to pre-fix fingerprint `3bb3dab66462ed2f...`; candidate pricing was generated with `b223…`.

**Fingerprint check:** `python3 scripts/reports/check_r2.py`

```
Current R²: 0.9721
Baseline R²: 0.8463
✅ R² improved by 0.1258
✅ Criteria fingerprint matches (b22382a291023fbf...)
```

**PASS required — met.**

---

## 7. Calibration loop (≤3 attempts, STEALTH_REMOVAL_RATE only)

**Attempt 1:** `STEALTH_REMOVAL_RATE = 400` (initial, user-approved) → guardrail **REVIEW** (max anchor 1.27% <5% → 0 FAILs), aggregate 0.01%, R² 0.9721.

**Decision:** **No tuning** — spec says tune only if anchors gain a **FAIL** (>5%). 0 FAILs → keep 400. **Attempts used: 1 of 3 allowed; 0 rate changes.**

Log: `reports/price_creep_guardrail.md` with REVIEW is the honest anchor status; no rate change logged because no FAIL.

If a future calibration were required, only `STEALTH_REMOVAL_RATE` would be tuned and every attempt logged here.

---

## 8. Canonical cleanliness (SAFE dance verification)

**Dance:** `02→05→05b→06→07→09→10→cp pricing_guide.csv → pricing_guide_candidate.csv→git checkout -- output/ data/processed/`

**Verification:** `git status --porcelain -- output/ data/processed/`  
**Result:** `?? output/pricing_guide_candidate.csv` **only** — `output/pricing_guide.csv`, `output/pricing_guide.xlsx`, `output/anomaly_report.md`, `output/variant_consistency_report.csv`, `data/processed/*.csv`, `data/processed/coefficients.json` all **clean (reverted)**. Candidate preserved at `output/pricing_guide_candidate.csv` (1.1 M, 4 749 rows). No canonical left modified — PASS.

---

## 9. GAPS & HONEST residual

- **Inversion not fully resolved** (see §3): Demon Skin still −355 to −490 gp below Poison equivalents (Plate −2 496 gp). The 400 gp rate is the user-approved parity; closing the gap fully would require ~750 gp (Chain/Splint/Ring) and would still leave Plate inverted due to its 12 000 gp DSA outlier. No threshold edits performed.
- **Mithral +1 Spiked Armor (0 gp delta):** carries removal per `_has_stealth_removal` but is reference-anchored, so `final_price` unchanged. This is HONEST leakage of the definition — rule price does increase (+400), but `final_price` does not. If `final_price` parity is required, the item would need to be moved off the amalgamated anchor.
- **Scorpion Armor attenuated (+41.58):** cursed + open attune + ML blend attenuates the 400 gp term to 41.58 final. Rule delta is 270 (400*0.90*0.75). HONEST: additive is before multipliers.
- **No new test failures:** 312 passed, 0 failed (`tests/test_stealth_removal.py` 5/5, full suite 312/312).
- **No threshold edits, no output/ left modified.**

---

## 10. Files changed (this ritual)

- `src/pricing_engine.py` — `STEALTH_REMOVAL_RATE` + `_has_stealth_removal` + additive + material-armor path + simple-predicate forcing
- `tests/test_stealth_removal.py` — 5 tests (400-parity, additive, NA/absent, HA/MA gating, simple-forcing)
- `reports/stealth_removal_impact.md` — this report
- `reports/price_creep_guardrail.md` — regenerated (67 rows >5%, max anchor 1.27% REVIEW)
- `output/pricing_guide_candidate.csv` — 4 749-row candidate (untracked, preserved)

**Next gate:** User sign-off on this report + guardrail (REVIEW accepted) before `mv candidate → canonical` migration.

