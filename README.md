# D&D 5e Magic Item Pricing Guide

A plain-language price list for nearly twelve thousand D&D 5e magic items — one fair price per item, with a clear record of where that price came from and how you can check it.

This README is written for D&D players and DMs, not data engineers. Jargon is explained the first time it appears.

---

## 1. What this is

This guide prices **11,941 magic items** from D&D 5e. The current canonical file is `output/pricing_guide.csv` — 11,941 rows (plus a header), adopted **2026-09-01** at commit **93cd09e**, after your sign-off. The previous baseline was 4,749 rows; the expansion more than doubled coverage.

**What it covers.** A curated list of 12,241 items drawn from 5e.tools exports — official books (Player's Handbook, Dungeon Master's Guide 2024, Xanathar's, Tasha's, and others) plus a carefully chosen set of community and third-party sources (Grim Hollow, Explorer's Guide to Wildemount, Call from the Deep, Humblewood, The Griffon's Saddlebag, and about twenty more). Two items were hard-excluded as out of scope (the QftIS concussion and sleep grenades); 167 generic-variant templates and 133 duplicate prints were collapsed so each distinct item appears once.

**One price per item, with provenance.** Every row has a single price in gold pieces and a note that says how that price was decided — a printed book price, an average of published reference guides, or a model estimate built from the item's abilities. Nothing is hidden: you can trace any price back to its source.

---

## 2. How a price is made

Think of it as a five-stage assembly line. An item moves through each stage and picks up a price that gets more refined along the way. Plain-language summary here; file paths in parentheses point to where the work actually happens.

### Stage 1 — Gather the items

A curation script (`src/list_curation.py`) starts from the raw 5e.tools export (12,243 entries) and produces the curated working list of **12,241 items**. This is the inventory the rest of the pipeline prices. It decides which sources to include, which generic templates to keep as templates versus priced variants, and which items to exclude.

Each item is then parsed into a row with its name, source, rarity, type, attunement, and the full text of its rules.

*Script: `scripts/01_extract_items.py` → `data/processed/items_master.csv` (999 of those rows carry an official book price straight from the printed books).*

### Stage 2 — Read the rules and pull out price-relevant features

A criteria extractor reads every item's prose and pulls out the things that make an item more or less valuable — **about 121 features** in the current build. Examples: a +1 to +3 bonus on attacks or AC; resistance or immunity to a damage type; storing or casting spells; flight, darkvision, or blindsight; curses; temporary hit points; bonuses to saving throws or ability checks; extra damage Dice, and about a hundred more.

The extractor is rule-based: it looks for specific phrasing ("you gain a +2 bonus to AC," "you can cast *fireball* once per day") rather than guessing. Coverage grows over time as new phrasing is found and added — tracked in `reports/criteria_discovery_findings.md`.

*Script: `scripts/02_extract_criteria.py` (`src/criteria_extractor.py`) → `data/processed/items_criteria.csv` (12,241 rows × ~121 columns).*

### Stage 3 — Collect what other price guides say

Separately, the pipeline ingests published pricing references — community guides that already price many items — and averages them per item. The averages are "amalgamated": outliers are trimmed and the remaining guides are averaged, so no single guide dominates.

*Scripts: `scripts/03_ingest_external.py` and `scripts/04_amalgamate.py` → the amalgamated reference.*

In the current output, about **2,700 items** have a reference-guide average (look for Price Source values like "Amalgamated (DSA,MSRP,DMPG)" — those letters name the guides that contributed). The rest have no external anchor yet.

### Stage 4 — A rules-based formula prices the features

A formula in `src/pricing_engine.py` turns the extracted features into a gold-piece estimate. It works the way a DM might: a +1 weapon adds a known amount, fire resistance adds another amount, a daily *misty step* adds another, and so on. Some effects interact — extra damage priced differently when it only works against a creature type or only on a critical hit, for example.

Variant items (families like "+1/+2/+3 Longsword") get a careful adjustment so the spacing between family members reflects real cost differences, not noise.

*Scripts: `scripts/05_rule_formula.py` and `scripts/05b_variant_adjust.py`.*

### Stage 5 — A machine-learning layer refines the estimate

The formula alone is good but not perfect. A machine-learning model (a regression — a model that predicts a number) is trained on items that **do** have reference-guide averages. It learns how much each feature actually moves prices in practice and nudges the formula toward what the published guides suggest. Think of it as a proofreader that has read thousands of already-priced items.

How well does it track? **R² 0.9692** in log-space — R² is a standard goodness-of-fit score where 1.0 means perfect agreement and 0.0 means no relationship. 0.9692 means the model's predictions track the reference prices very closely. Cross-validation (testing on items the model did not train on) averages about 0.93. A fingerprint check makes sure the model is always retrained when the feature list changes; if the fingerprint does not match, the quality gate fails rather than shipping stale coefficients.

*Script: `scripts/06_ml_refine.py` → `data/processed/coefficients.json` and `data/.r2_baseline` (baseline 0.8463; current 0.9692, well above the gate).*

### The trust order — which price wins

Not every price is made the same way. When more than one method could apply, the pipeline follows a clear priority, highest trust first:

1. **Official book price — exact.** 999 items have a price printed in an official D&D book (mostly mundane adventuring gear plus a handful of magic items). When that exists, it is used exactly. In the final CSV about 702 rows show as `Price Source = Official` after duplicate prints are collapsed — the count differs from 999 because the same item can appear in multiple source books and is collapsed to one row.
2. **Averaged reference-guide anchors — averaged.** When no official price exists but one or more reference guides price the item, their trimmed average anchors the price. These rows show as `Amalgamated (...)` or `Single source (...)`.
3. **Formula + ML estimate — modeled.** When neither of the above exists, the price is the formula's estimate refined by the ML layer. These rows show as `Algorithm`. They are honest estimates, not book prices, and they carry lower confidence on average.

Confidence (`High` / `Medium` / `Low` in the CSV) reflects this ladder plus how far the estimate sits from rarity norms and reference anchors.

---

## 3. Safety rails — what keeps prices honest

Four checks run every time the guide is rebuilt. You do not need to understand their internals to trust them, but here is what they do in plain language.

**Rarity floors — "no item below its minimum."** Every rarity has a floor: Common 10 gp, Uncommon 50 gp, Rare 200 gp, Very Rare 1,000 gp, Legendary 8,000 gp, Artifact 50,000 gp (`src/pricing_engine.py`). A later stage enforces those floors (`scripts/09_enforce_floors.py`). Today floors are enforced for weapons, armor, and shields; extending the floor to every item type (like wondrous items that have no mundane counterpart) is tracked as issue `sej` and is the next fix.

**Price-creep guardrail — "did the whole market drift?"** When a new candidate guide is built, it is compared row-for-row against the adopted baseline. The guard reports the median drift (middle value) and the mean drift (average). In the 12k adoption the **median drift was 0.00%** across 4,717 items present in both the old and new guides — meaning half the shared items did not move at all. Reference-anchored items (those with a guide average) moved only **0.69% on average**, which is why the guard treats the adoption as anchored-stable even though formula-only items shifted more (more on that in Limitations).

*Script: `scripts/reports/price_creep_guardrail.py` → `reports/price_creep_guardrail.md`.*

**Known-good anchors — "437 favorites that must stay steady."** A curated set of **437 well-known items** (Holy Avenger, Vorpal Sword, Defender, +1/+2/+3 weapons and armor, Dragon Slayer, and similar benchmarks) is re-checked every run. Status bands: PASS within 1%, REVIEW 1–5%, FAIL above 5%. The adopted run had **zero FAILs** and a maximum drift of **1.47%** (Holy Avenger on a dart), well inside REVIEW. If any anchor moved more than 5%, the adoption would be blocked pending your review.

**User-signed baselines — "nothing ships without your approval."** Every baseline adoption is user-signed. The pipeline can build a candidate, but promotion to `output/pricing_guide.csv` only happens after you approve the sign-off pack. The adopted candidate is archived under `output/baselines/` so any prior release can be restored.

A bonus rail: the **R² quality gate** (`scripts/reports/check_r2.py`) and **criteria fingerprint** block commits built on stale ML coefficients — if the feature list changed but the model was not retrained, the gate prints `ML coefficients stale — retrain before trusting ML-blended prices` and exits non-zero.

---

## 4. How to read the guide

Open `output/pricing_guide.csv` in any spreadsheet. One row per item; fifteen columns. Data types are shown in brackets.

| Column | What it means | Example |
|---|---|---|
| **Name** [text] | Item name as printed. Embedded reskins like "Cloak of Shadows (Cloak of Elvenkind)" are priced copies of their parent. | Cloak of Protection |
| **Source** [text] | Short code for the book or source. Codes use 5e.tools abbreviations; human names are mapped in `src/source_names.py` and `docs/reference/ttrpg-convert-cli-sourceMap.md`. | XPHB = Player's Handbook 2024; EGW = Explorer's Guide to Wildemount; GrimHollow = Grim Hollow; Call from the Deep = Call from the Deep |
| **Type Code** [text] | Compact internal type code (may combine categories). | M = Melee Weapon, R = Ranged Weapon, G = Adventuring Gear, etc. |
| **Type** [text] | Human-readable item type. | Melee Weapon, Wondrous Item, Potion |
| **Rarity** [text] | Official rarity. Mundane means non-magical gear; Unknown Magic / Varies mean the source did not assign a standard rarity. | Uncommon, Rare, Legendary |
| **Attunement** [text] | Whether the item requires attunement. | Yes / No |
| **Price (gp)** [number] | Machine-readable price in gold pieces (decimals allowed). This is the price to use for calculations. | 850.63 |
| **Price Formatted** [text] | Same price rounded for display. | 850 gp |
| **Price Low** [text] | Lower end of the band (roughly 20% below the price). Use when you want a bargain or used price. | 680 gp |
| **Price High** [text] | Upper end of the band (roughly 20% above). Use for pristine, inflated, or high-demand markets. | 1,020 gp |
| **Confidence** [text] | How much to trust the price: **High** (official or multi-guide anchor), **Medium**, **Low** (formula/ML-only with no anchor). | High |
| **Price Source** [text] | Where the price came from (the trust order above). `Official` = printed book; `Amalgamated (DSA,MSRP,DMPG)` = average of those guides; `Single source (...)` = one guide; `Algorithm` = formula+ML estimate. | Amalgamated (DSA,MSRP,DMPG) |
| **URL** [text] | 5e.tools link to the item. | https://5e.tools/items.html#... |
| **Notes** [text] | Disclosures for reskins and special handling. | |
| **Has Reference** [text] | Whether any reference guide priced this item, regardless of whether that price was used as the final anchor. `True` means at least one guide had a number. | True |

**Quick filters that help:**

- Count: 11,941 total rows. About 702 show as Official, about 2,700 as Amalgamated/single-source, and about 8,500 as Algorithm (formula+ML-only). About 7,997 rows have `Has Reference = True`.
- Rarity split: Rare is the largest group (~3,700), followed by Uncommon (~2,600) and Very Rare (~2,300).

---

## 5. Known limitations — honest gaps

No pricing guide is perfect. These are the known gaps today, with where to track them.

**14 items sit below their rarity floor, pending a fix.** Wondrous items and spell gems with no mundane counterpart — Shard Solitaire variants at 5,000 gp (Legendary floor is 8,000 gp) and several Spell Gem variants at 10–5,000 gp — land below `RARITY_FLOORS` because `09_enforce_floors.py` currently clamps only weapons, armor, and shields to mundane-relative floors. Absolute rarity floors for every item type are the next fix, tracked as **issue `sej`**. See `reports/tail_331_attribution.csv` — the 14 floor-gap movers.

**About 300 items moved noticeably on the expanded corpus.** Expanding from 4,749 to 11,941 rows and retraining the ML model shifts some formula/ML-only prices. Of the 331 items that moved more than 25% versus the prior baseline, 13 moves were intentional (new criteria from wave 1 and the stealth-removal reprice), 14 are the floor-gap items above, and **304 are accepted ML-retrain variance** — the model saw new books and new features and adjusted. They are triaged and attributed in `reports/tail_331_attribution.csv`; most are not reference-anchored, so they do not indicate a pricing error, but they merit spot-checks on your next review.

**Criteria coverage grows in waves.** The extractor captures about 121 features today, but D&D prose is varied. Additional price-relevant features (identified in `reports/criteria_discovery_findings.md`) are queued as future waves. Items whose value hinges on an un-captured rule may be underpriced until that wave lands. Community/homebrew sources fall in this category more often — their prices carry less confidence than official-book items, and the Confidence column reflects that.

**Bookkeeping notes.** Source abbreviations can surprise (XPHB, EGW, GrimHollowPG24, etc.) — the display-name map in `src/source_names.py` resolves them. Variant families (like Demonglass weapons) can stretch prices when new variants are added, because shared base stats shift; the variant-freeze hardening in `src/variant_system.py` pins anchor families but a longer-term config-driven pin is tracked as **issue `4om`**.

---

## 6. Reproducing and maintaining the guide

### Pipeline scripts in run order

Run these from the repo root, in order, to rebuild the guide from the curated list. Files named `11_...` and scripts under `scripts/reports/` are reporting helpers, not required for a pricing rebuild.

1. `scripts/01_extract_items.py` — parse `trimmed_5etools_list.json` (12,241 curated items) into `data/processed/items_master.csv`.
2. `scripts/02_extract_criteria.py` — extract ~121 price-relevant features from each item's prose.
3. `scripts/03_ingest_external.py` — ingest published reference-guide prices.
4. `scripts/04_amalgamate.py` — trim outliers and average guide prices per item.
5. `scripts/05_rule_formula.py` — apply the rules-based pricing formula (`src/pricing_engine.py`).
6. `scripts/05b_variant_adjust.py` — adjust variant-family spacing.
7. `scripts/06_ml_refine.py` — blend in the ML refinement and write coefficients with a criteria fingerprint.
8. `scripts/07_validate.py` — validate floors, sanity checks, and R² bookkeeping.
9. `scripts/07b_variant_consistency.py` — flag variant families with unexpected spread.
10. `scripts/09_enforce_floors.py` — enforce rarity floors on the priced list.
11. `scripts/10_generate_output.py` — write `output/pricing_guide.csv` (11,941 rows), the spreadsheet, and related artifacts.
12. `scripts/11_generate_html.py` — regenerate the browsable HTML guide (if published).

Validation helpers (run any time):

- `python3 scripts/reports/check_r2.py` — R² gate plus fingerprint check; fails if ML coefficients are stale.
- `python3 scripts/reports/price_creep_guardrail.py --baseline output/pricing_guide.csv --candidate output/pricing_guide_candidate.csv` — price-creep guardrail.
- `python3 -m pytest -q` — test suite; expect **316 tests** passing (3.5 s).

### Session map and baselines

- **Session map:** `docs/HANDOFF.md` is the handoff between work sessions — where numbers live, what was decided, and what is next. The beads board (`bd ready`) is authoritative for open work.
- **Quality gates:** `docs/QUALITY_GATES.md` documents the R² gate and fingerprint discipline.
- **Baselines:** every adopted release is archived under `output/baselines/` (e.g., `output/baselines/pricing_guide_12k_adopted_2026_09_01.csv`). Restore any baseline by copying it back to `output/pricing_guide.csv`.

---

## 7. Changelog of baselines — what changed and when

Every adoption below was user-approved before it became canonical. Commit hashes are the point where `output/pricing_guide.csv` changed.

| Adoption | Commit | What changed |
|---|---|---|
| **Pack v3 baseline** | `1518778` sign-off; prior canonical | Post-extraction-fix baseline: per-source extra-damage multipliers (unconditional 1.0 / vs creature type 0.25 / on crit 0.05), token-aware save-advantage tiering, and the reskin inheritance fix all landed and were reviewed. |
| **Wave-1 criteria** | `0aa37cf` — 2026-08-28 | New criteria wave: temporary hit points, hit-point-maximum effects, and initiative bonuses/advantage entered the feature matrix; ML was retrained; 1,677 rows repriced versus prior baseline. |
| **Stealth-removal reprice** | `71e5bf7` — 2026-08-28 | Option D (400 gp) to price removal of stealth disadvantage on armor — the root cause of the Demon Skin pricing inversion. Impact report at `reports/stealth_removal_impact.md` with a resistance-armor consistency sweep. |
| **12k expansion (current)** | `93cd09e` — **2026-09-01** | Big-bang migration: curated corpus 4,837 → 12,241 items (26 new sources, explosives in, Renaissance firearms in), output **4,749 → 11,941 rows**. Gates at adoption: R² 0.9692 (fingerprint PASS), guardrail median 0.00% / reference-anchored mean 0.69%, anchors 0 FAILs / REVIEW max 1.47%, tail 331 attributed, suite 316 passed. Archived at `output/baselines/pricing_guide_12k_adopted_2026_09_01.csv`. |

Non-adoption notes: `d43bc38` swapped the curated input to the 12,241-item list (no reprice); `8d27941` updated the embedded-reskin test for the new corpus.

---

## Sources and provenance

- Item text and rules: **5e.tools** exports (sourced from official books; community sources listed above). Each row's Source and URL identify the book.
- Reference prices averaged: the DSA / MSRP / DMPG families (see `scripts/03_ingest_external.py` and `scripts/04_amalgamate.py` for the exact import set; Sane Magic Item Prices remains excluded by your decision).
- Pricing logic: `src/pricing_engine.py` (formula), `src/criteria_extractor.py` (feature extraction), `src/variant_system.py` (variant families), `src/source_names.py` (source display names).
- Everything in `output/pricing_guide.csv` is reproducible from `trimmed_5etools_list.json` via the scripts above — no manual price edits.

---

*Questions about a specific price? Filter the CSV by Name and Source, check Price Source and Confidence, and consult the reports folder for the adoption sign-off that produced your copy (`reports/migration_12k_signoff_pack.md` for the current baseline).*
