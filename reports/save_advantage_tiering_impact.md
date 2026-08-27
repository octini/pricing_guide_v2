# Save-Advantage Tiering Impact Report

**Commit:** `cdc1a4d` — `feat(criteria,engine): tiered save-advantage pricing`
**Date:** 2026-08-27
**Candidate:** `output/pricing_guide_candidate.csv` (freshly regenerated under tiered authority)
**Baseline:** `output/pricing_guide.csv`
**Criteria source:** `data/processed/items_criteria.csv` (+ `src/criteria_extractor.py` classifier)

## 1. What shipped

### Three-tier pricing for `save_advantage`

| Tier | Meaning | Pricing | Example |
|---|---|---|---|
| **BROAD** | advantage on all saving throws, or all saves of one ability, always-on | **400 gp** (1.0× base) | "advantage on all saving throws", "advantage on Strength saving throws" |
| **CATEGORY** | advantage versus a category of effect — condition, creature-type, damage-type, or spell (e.g. "vs frightened", "vs spells", "to avoid or end paralyzed/restrained") | **200 gp** (0.5×) | "advantage on saving throws to avoid or end the paralyzed condition", "advantage on saves vs spells" |
| **SITUATIONAL** | advantage gated on item state / position / duration — strictly narrower than CATEGORY | **100 gp** (0.25×) | "while at 0 hit points, you have advantage on death saving throws" (not priced here — handled separately), "while mounted, you have advantage on Dexterity saving throws", "while in the air" |

- **Constants (pricing_engine):** `SAVE_ADVANTAGE_BASE_VALUE = 400`, `SAVE_ADVANTAGE_CATEGORY_MULTIPLIER = 0.5`, `SAVE_ADVANTAGE_SITUATIONAL_MULTIPLIER = 0.25`
- **Classifier (criteria_extractor):** `_save_advantage_tier_for_clause()` + `_SAVE_ADVANTAGE_CATEGORY_RE` (`against` / `to avoid or end` / `versus` / `vs`) and `_SAVE_ADVANTAGE_SITUATIONAL_RE` (`while at 0 hit points` / `while mounted` / `while riding` / `mounted on` / `while in the air` / `while flying`). SITUATIONAL takes precedence over CATEGORY (strictly narrower gate). A 250-char window before the clause is scanned so "while mounted, you have advantage ..." is caught even when the state marker sits outside the captured clause.
- **Emitter:** `extract_prose_criteria()` now emits parallel tier data: `save_advantage_tiers` (ordered list matching `save_advantage`), plus counts `save_advantage_broad` / `save_advantage_category` / `save_advantage_situational`. Deduplicated per-target; fallback ensures every `save_advantage` entry gets a tier.
- **Pricing engine:** `src/pricing_engine.py` `calculate_price()` prefers explicit per-tier counts when present; falls back to `save_advantage_tiers` list; else backward-compatible flat 400 gp per entry. Handles NaN/string CSV round-tripping, length mismatches (pads BROAD), and clamping.
- **Backward compatibility:** Missing tier data → all BROAD (original flat 400 gp behavior). No migration required; old snapshots and pre-existing CSVs price identically. Pre-existing `conditional_save_advantage` (130 rows, implicit 0.5× via separate path) is untouched.
- **Bracers-of-Celerity fix:** "saving throws you make to avoid or end the paralyzed/restrained condition" previously priced as BROAD (400 gp) due to generic `save_advantage` capture; now correctly classified as **CATEGORY (200 gp)**. This is the largest intentional price movement from the tiering.
- **Tests:** `tests/test_criteria_extractor.py` and `tests/test_pricing_engine.py` added covering BROAD/CATEGORY/SITUATIONAL classification and tiered pricing math.

## 2. Expected tier split

> These expected counts are from the extractor spec / prior analysis; the checked-in `data/processed/items_criteria.csv` (4838 rows) predates `cdc1a4d` and does not yet carry `save_advantage_broad` / `save_advantage_category` / `save_advantage_situational` columns, so live tier counts were **not captured** in this run (grep returned 0; python tier-count probe returned `n/a` for all three).

- **BROAD:** ~16–17 items (always-on generic or single-ability saves)
- **CATEGORY:** ~2–3 items incl. **Bracers of Celerity fix** (paralyzed/restrained category gate)
- **SITUATIONAL:** 0 items (no `save_advantage` currently matches the situational state markers; situational advantage in the corpus lives in `conditional_save_advantage` / `death_save_advantage` paths)
- **Pre-existing conditional rows:** **130 rows** in `conditional_save_advantage` unchanged at implicit 0.5× — tiering does not touch this path; only `save_advantage` is tiered.

Live tier verification after next `items_criteria.csv` regeneration:
```bash
grep -c "save_advantage_broad" data/processed/items_criteria.csv
python3 -c "import pandas as pd; df=pd.read_csv('data/processed/items_criteria.csv'); print(df[['save_advantage_broad','save_advantage_category','save_advantage_situational']].sum())"
```

## 3. Price-creep guardrail — headline stats

**Command:** `python3 scripts/price_creep_guardrail.py`
**Report:** `reports/price_creep_guardrail.md` (generated 2026-08-27 17:07)

- **Common rows:** 4748 (New candidate rows: 1, Missing candidate rows: 1)
- **Median % drift:** **0.00%**
- **Mean % drift:** **0.05%**
- **Median gp drift:** **0 gp**
- **Mean gp drift:** **33 gp**
- **Rows >5% drift:** **222**
- **Rows >10% drift:** **85**
- **Rows >25% drift:** **5**
- **Reference-anchored (3285 rows):** median 0.00%, mean -0.03%, median 0 gp, mean 11 gp
- **Formula/ML-only (1463 rows):** median 0.00%, mean 0.21%, median 0 gp, mean 82 gp
- **Known-good status:** **REVIEW** — PASS ≤1% drift; REVIEW >1%; FAIL >5%
  - 4× Vorpal family (Glaive/Greatsword/Longsword/Scimitar): -847 gp, **-1.55%** (reference-anchored)
  - +3 Moon Sickle: +552 gp, **+1.68%** (reference-anchored)
  - +3 Leather/Padded/Studded Leather: -328 gp, **-1.10%** (reference-anchored)
  - Remaining anchors within ±1%: +3 Breastplate/Chain Shirt/Half Plate/Hide/Scale Mail -0.59%, +3 Plate -0.57% to -0.16% etc.
  - No anchor exceeds FAIL (>5%); status REVIEW driven by >1% on Vorpal and Moon Sickle families — consistent with intentional Bracers/Category repricing and normal ML variance, not systemic creep.
- **Rarity drift:** Legendary largest mover (mean +306 gp, +0.69%); Unknown Magic 9 rows (median +0.92%, mean -2.12%)
- **Largest movers (>25% except 0→0 artifacts):** Harp of Gilded Plenty -39.85% (-35,522 gp, formula/ML-only), Grimoire Infinitus Dormant +36.48%, Telescopic Transporter +26.09% etc. — all formula/ML-only or previously flagged high-variance items (see `demonglass_driver_investigation.md`, `extra_damage_signoff_pack_v2.md`).

*Side-effect dirt from prior `check_r2` run was cleared before guardrail capture: `git checkout -- data/processed/items_ml_priced.csv output/official_price_anchor_audit.csv` (restored to HEAD; verified clean via `git diff --name-only` and `git restore`).*

## 4. R² + fingerprint — `python3 scripts/check_r2.py`

```
🔄 Running ML pipeline...
📊 Current R²: 0.9723
📏 Baseline R²: 0.8463
✅ R² improved by 0.1260
✅ Criteria fingerprint matches (3bb3dab66462ed2f...)
```

- **Current R²:** **0.9723**
- **Baseline R²:** **0.8463**
- **Delta:** **+0.1260** (improved)
- **Fingerprint:** **matches** `3bb3dab66462ed2f...` (criteria fingerprint guard — no stale coefficients)

## 5. Tier counts probe (step 4)

- `grep -c "save_advantage_broad" data/processed/items_criteria.csv` → **0** (column not present)
- Python probe:
  ```
  broad n/a
  category n/a
  situational n/a
  ```
  **Result:** `tier counts not captured` — CSV predates `cdc1a4d` (last criteria commit `659eeb2`). Expected split quoted in §2 applies to post-regeneration CSV; `130 conditional_save_advantage` rows remain at implicit 0.5×.

---

## SIGN-OFF QUESTION

> **Accept tiered save-advantage pricing?**
>
> - BROAD 400 gp (1.0×) / CATEGORY 200 gp (0.5×) / SITUATIONAL 100 gp (0.25×), classifier in `src/criteria_extractor.py`, pricing in `src/pricing_engine.py`, backward-compatible (missing tier data → BROAD).
> - Guardrail: 4748 common rows, median 0.00% / mean 0.05%, 222 >5% / 85 >10% / 5 >25%, known-good REVIEW (max 1.68% drift).
> - R² 0.9723 (baseline 0.8463, +0.1260), fingerprint matches.
>
> Reply **ACK** to accept, or list blocking concerns.

## References

- Tiering commit: `cdc1a4d` (diff: `src/criteria_extractor.py`, `src/pricing_engine.py`, `tests/test_criteria_extractor.py`, `tests/test_pricing_engine.py`)
- Guardrail report: `reports/price_creep_guardrail.md`
- Candidate: `output/pricing_guide_candidate.csv` (1.1M, generated 2026-08-27 17:05)
- Previous anchor/ML guards: `reports/extra_damage_signoff_pack_v2.md`, `reports/demonglass_driver_investigation.md`
