# Ritual sej·913·q7b — Retrain 122-col matrix, guardrail, anchors, mechanism verification, tail attribution

**Date:** 2026-09-02
**Baseline:** output/pricing_guide.csv @ 93cd09e (adopted 11,941 rows) — canonical preserved
**Candidate:** output/pricing_guide_candidate.csv (generated 2026-09-02 02:42, 11,942 lines incl header)
**Extractor:** f38356f (122 criteria cols — conditions→control-spell mapping, short-rest healing, multi-ability advantage, seal damage, moonbow fire, spell_battery_max_level)
**Engine:** 82540c0 (family-min + battery-parity) + cda8a73 (absolute rarity floors as tripwire)
**Suite:** 358 tests green (pre-ritual)

---

## 1. Pipeline tails (03→10)

```
# 03 ingest
Saved 637 DMPG items to data/raw/dmpg_prices.csv
Total external prices: DSA=531, MSRP=557, DMPG=637

# 04 amalgamate
unknown_magic: 0/32 (0.0%)
varies: 11/103 (10.7%)
very_rare: 714/2274 (31.4%)

# 05 rule_formula
very_rare: 14,320 gp (n=2274)  [median]
unknown_magic: 750 gp (n=32)

# 05b variant_adjust
Paper Cartridge Bullet of Slaying: 773 gp (base=790.46, adj=-0.088)
Needle of Slaying: 773 gp (base=790.46, adj=-0.437)

# 06 ml_refine
Wrote 12241 rows to data/processed/items_ml_priced.csv
Wrote coefficients with fingerprint 169a3914358c0f7a... to data/processed/coefficients.json
Median final prices by rarity: artifact 327,500 gp (116), legendary 46,396 gp (1494), very_rare 13,764 gp (2274)
Confidence: Low 8904 (72.7%), High 3068 (25.1%), Medium 269 (2.2%)

# check_r2 (scripts/reports/check_r2.py)
Current R2: 0.9700  Baseline R2: 0.8463  Improved +0.1237
Criteria fingerprint matches (169a3914358c0f7a...) — PASS

# 07 validate
Validated data written to data/processed/items_validated.csv
Variant consistency: 8 families, 2 flagged (CV > 0.60)

# 07b variant_consistency
Variant consistency: 8 families, 2 flagged (CV > 0.60)

# 09 enforce_floors (tripwire fires here — clamp log)
Loaded 12241 items
Found 803 unique mundane item prices
=== ABSOLUTE RARITY FLOOR (TRIPWIRE) ===
Total absolute adjustments: 1
  +3 True Name Dart | legendary | 7950.10 -> 8000.00 gp (floor 8000)
=== OFFICIAL PRICE FLOOR FIXES === (5 items, e.g. +1 Adamantine Chakram 435 -> 1000)
=== VARIANT SPACING ADJUSTMENTS === (6 items, dampened)
=== FLOOR PRICE ADJUSTMENTS === (mundane-relative weapons/armor)
  — second run after regenerate showed 0 remaining before final 10; first pipeline run showed 36:
    Musket: Silvered 253->750, Repeating 348->1000, Foresight 1472->2500, etc.
    Plate Armor: Dorrin 114->2250, Gleaming 330->1650 [flavor], Vulnerability 3319->4500, etc.
No remaining violations found.

# 10 generate_output
Saved CSV to output/pricing_guide.csv
Saved Excel with 4 sheets
Total items: 11941  Hyperlinked items: 11941
wc -l pricing_guide_candidate.csv => 11942 (header + 11941 rows) — expect ~11,942 ✓
```

---

## 2. R² / fingerprint

- **R² current:** 0.9700  / **baseline:** 0.8463  / **delta:** +0.1237 — **PASS** (≥0.80)
- **Criteria fingerprint:** `169a3914358c0f7a...` — **PASS** (matches coefficients.json)
- **Retrain command (if FAIL):** `python3 scripts/06_ml_refine.py` then re-check — not needed (PASS)

---

## 3. Guardrail (reports/price_creep_guardrail.md)

- **Baseline:** output/pricing_guide.csv (canonical 93cd09e/HEAD)
- **Candidate:** output/pricing_guide_candidate.csv
- **Common rows:** 11940  (1 new / 1 missing due to dedup edge)
- **Median % drift:** **0.00%** ✓ (expect 0.00%)
- **Mean % drift:** 2.27% (mean gp -633)
- **Rows >5%:** **2652**
- **Rows >10%:** 1917
- **Rows >25%:** **1008**
- **Split:** formula/ML-only 9407 median 0.00% mean 2.82%; reference-anchored 2533 median 0.00% mean 0.24%
- **Known-good anchor verdict:** **FAIL** — 1 FAIL (>5%):
  - `Defender Cavalry Hammer | D&D 2024 | Legendary | Melee Weapon | 31,500 → 44,850 gp | +42.38% | reference-anchored` (family-min intentional)

**Calibration attempts:** 0 via documented constants (docs/QUALITY_GATES.md lists only R² retrain; no guardrail constants documented). No further attempts made — reported as honest gap per spec (≤3 allowed, else STOP). Median passes; anchor FAIL is intentional family-min raise.

---

## 4. Mechanism verification (grep candidate; expected vs actual)

Grep rows pasted verbatim from `output/pricing_guide_candidate.csv`:

| Item | Was | Expected | Candidate actual | Verdict |
|------|-----|----------|------------------|---------|
| **Drow +3 Repeater Needler** | 2,502 | ~11–14k | `8000.0` Legendary | **PARTIAL / GAP** — raised via legendary floor 8000, not family-min 44,850. `is_ammunition` = False (not blocking), but amalgamated anchor (635 gp, multi) + ML (12932) → final 2480 before floor, then 09 clamps to 8000. Family-min 44,850 present in rule_price (44850) but not applied in ML/anchor path. Report as GAP per spec. |
| **Wyrm's Breath Grenade (Silver)** | 5 | 20–40k | `5.0` Legendary | **FAIL / GAP** — remains 5 gp. Val `46699` but out `5` due to embedded-reskin? No, grenade maps to control spell (slow 3rd / hold monster 5th) via `_GRENADE_SPELL_MAP` → rule 47k in validated, but output reverts to 5 (see reskin artefact). |
| **Masks of the Sacred Beasts (Mule)** | 8 | 3–6k | `8.0` Very Rare | **FAIL / GAP** — val `11508.6` (correct: seal/advantage etc, rule 12510) but out `8` due to **embedded reskin bug** in `10_generate_output.py`: `Masks (…) (Mule)` inner `Mule` → copies mundane `Mule` @8 gp. |
| **Snugglebeast (Dragon)** | 1 | 1.5–3.5k | `1.0` Rare | **FAIL / GAP** — val `5717.8` (correct) but out `1` — similar reskin (Dragon). |
| **Moonbow (Shortbow)** | 25 | 3.5–6k | `25.0` Rare | **FAIL / GAP** — val `12560.6` (correct) but out `25` — no reskin; ML/out path retains old. |
| **Spell Gem (Diamond)** | 5,000 | 100,000 | `5000.0` Legendary | **FAIL / GAP** — val `60504` (battery floor 100k, rule 100k) but out `5000` — reskin inner `Diamond` (trade good 5000). |
| **Shard Solitaire (Diamond)** | 5,000 | 85–124k | `5000.0` Legendary | **FAIL / GAP** — val `62309` (correct) but out `5000` — same reskin. |
| **Universal Solvent** | 7,806 | 8,000 | `8800.67` Legendary | **PASS** — val `8800.67` out `8800.67` (floor 8000, now above). |
| **Spell Gem (Obsidian)** | 10 | ~25–750 | `10.0` Uncommon | **FAIL / GAP** — val `764.68` (battery 25 → rule 680 +) but out `10` — reskin `Obsidian` 10. |
| **Silver Sword** | 3,680 | 5,980 | `3107.63` Uncommon | **FAIL / PARTIAL** — val `3107` (family-min 5980 not reached; rule 5980 but ML 3107, below floor 50). |

**Honest labels:** 1 PASS, 9 GAP/FAIL. Is-ammunition flag **not** blocking Needler (False); gaps are anchor/ML/reskin, not flag.

---

## 5. Tripwire clamped list (09 absolute floor)

- **Absolute rarity floor (tripwire) adjustments:** 1
  - `+3 True Name Dart | legendary | 7950.10 → 8000.00 gp (floor 8000)` — correctly exempts official & consumable-modifier (ammo/potion/scroll/poison); grenades/wondrous clamp.
- **Mundane-relative floors (36 in first pipeline run, 0 in final regenerate after variant-spacing undo):**
  - Musket, Pistol, Plate Armor, Half Plate, Breastplate families (e.g., Dorrin Plate 114→2250, Foresight Musket 1472→2500).
- **No remaining violations** after 09.

---

## 6. Attribution of >25% movers

- **Input:** 1008 rows >25% (2652 >5%)
- **Output:** `reports/tail_attribution_sej913.csv` (1008 rows, sorted by pct desc)
- **Columns:** name,source,old,new,pct,bucket,evidence
- **Buckets (mechanical, like tail_331_attribution.csv):**

| Bucket | Count | Definition |
|--------|-------|------------|
| **intended-913/q7b** | **272** | newly-extracted criteria / battery / family-min: `spell_battery_max_level`, `family-min weapon_bonus` (M/R, non-ammo), `grenade-control attached_spells` (hold monster/slow), or name-patterns (Masks, Snugglebeast, Moonbow, Needler, Spell Gem, Solitaire, Wyrm, Silver Sword) |
| **floor-tripwire** | **1** | candidate == RARITY_FLOORS[rarity] |
| **ml-variance** | **735** | rest: `no wave1/stealth/floor/match signature → ML retrain / variant-stat / rule-blend variance` |

- **Named sub-classes within intended:**
  - **battery floor:** ~10 Spell Gems (Diamond 9, Ruby 8, Star Ruby 7, etc. → scroll-parity 100k, etc.; Obsidian 0 → 25 gp) — many still masked by reskin in output (gap)
  - **family-min:** ~180 +1/+2/+3 weapons (Drow Needlers, Defender family, Silver Sword etc.; Drow +3 shows gap)
  - **grenade-control:** ~60 grenades/debuff items mapping to slow (3rd) / hold monster (5th) via `_GRENADE_SPELL_MAP` (e.g., Suude Blue/Brown/Red 291→6855, +2249%)
  - **broadening (f38356f):** Masks, Snugglebeast, Moonbow, seal, healing, advantage — validated correct (Mule 11508, Dragon 5717, Moonbow 12560) but output masked

- **Largest movers (example):**
  - Kiona's Notes 1→201 (+20000% ml-variance)
  - Whispergust Mote 120→7411 (+6033% ml-variance)
  - Suude (Blue/Brown/Red) 291→6855 (+2249% intended/grenade)

---

## 7. Known gaps

1. **Needler (is_ammunition flag) — GAP per spec:** Drow +3 Repeater Needler remains 8000 (floor) vs expected 11–14k / family-min 44,850. Flag is **False** (not blocking), but anchor/ML path prevents family-min from reaching output. Rule shows 44,850, ML 12932, final before floor 2480 → floor 8000. Report as GAP, do not fix here.
2. **Embedded reskin bug in `10_generate_output.py` — GAP:** Any `Name (Inner)` where inner is a generic item (Mule 8, Diamond 5000, Obsidian 10, Dragon, Silver) copies inner price, masking correct validated price (Mule 11508→8, Diamond 60504→5000, etc.). Affects 5/10 mechanism anchors. Requires fix to `embedded_pattern` allowlist (should only match known alias map, not any parenthetical).
3. **Battery floor not reaching output — GAP:** Spell Gems correct in validated (60504) but reskin masks them.
4. **Moonbow / Wyrm etc. not reaching output — GAP:** Validated 12.5k/46k but output retains old (25/5) — ML/anchor path or reskin.
5. **Guardrail anchor FAIL — GAP:** Defender Cavalry Hammer 42% drift (family-min intentional) — 0 FAILs required; documented constants for calibration not present in QUALITY_GATES.md, so no calibration attempt.
6. **Silver Sword (Uncommon +3) 3107 vs 5980 — GAP:** family-min 5980 not applied (ML 3107 < floor 50, but below family-min).

---

## 8. Verification

- **R²:** 0.9700 PASS, fingerprint PASS
- **Guardrail:** median 0.00% PASS, mean 2.27%, >5% 2652, >25% 1008, anchors 1 FAIL (Defender)
- **Candidate row count:** 11942 (11941 rows) ✓ (off by 0, ≤200 gate PASS)
- **Canonical preserved:** `output/pricing_guide.csv` restored to HEAD (93cd09e) — `git diff` null for canonical after `git checkout --`; before restore candidate was copied.
- **Git status after pipeline (before commit):**  M reports/price_creep_guardrail.md (commit will include), candidate untracked `?? output/pricing_guide_candidate.csv` — canonical clean.
- **Tests:** 358 green pre-ritual (tripwire floors).

---

## 9. Files

- `reports/price_creep_guardrail.md` — guardrail report (FAIL as above)
- `reports/tail_attribution_sej913.csv` — 1008 movers, 272 intended / 1 floor / 735 ml-variance
- `output/pricing_guide_candidate.csv` — candidate (preserved, untracked)

**Next:** Fix reskin allowlist in 10, re-train, re-guardrail, re-attest anchors; family-min anchor path needs ML/anchor precedence fix for Drow.
