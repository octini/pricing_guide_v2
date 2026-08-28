# Criteria Discovery Findings (pricing_guide_v2-z0z)

Date: 2026-08-28. Method: three parallel prose-mining passes over `trimmed_5etools_list.md`
(4,837 items, canonical pipeline input), sliced by line ranges (1–33,200 / 33,201–66,400 /
66,401–99,613), seed-keyword frequency scans + targeted reads, reconciled against
`src/criteria_extractor.py` (extract_structured_criteria L126-263, extract_prose_criteria
L549-1033 — verified directly, not from miner claims).

**Prevalence numbers are estimates (±30%)** — miners counted via filtered grep line
reviews, not exact `uniq -c`. Each implementation ticket must re-count precisely and ship
through the standard ritual (impact report → price-creep guardrail → anchor-drift review →
user sign-off) per the pricing authority policy.

## Already extracted (do not re-propose)

Structured JSON: attunement, weapon/attack/damage/AC/save/check/proficiency/spell bonuses,
concentration-save bonus, damage resist/immune/vulnerable, condition immunities, spell
scroll/attached spells, charges/recharge, speed mods, grants language/proficiency, sentient,
cursed, tattoo, wondrous, focus, poison, firearm, reload, armor AC/strength, vehicle stats,
ammunition/shield flags, stealth penalty, strength req, crit threshold, item tier, ability
score mods, weapon properties, generic-variant, material (mithral/adamantine/silvered).

Prose: flight (full/limited), darkvision (feet), truesight/blindsight/tremorsense,
teleportation (boolean), invisibility at-will, healing (daily/consumable/permanent), tome/
manual boost, concentration-free, crit immunity, wish effect, spell absorption, stealth
advantage, legendary resistance, swim/climb/burrow speeds, save advantage (tiered
BROAD/CATEGORY/SITUATIONAL), conditional save advantage, condition immunity (prose),
language known, unarmed strike bonus/dice, spell casting (cast *X* once/at-will/per day),
curse effects (limited patterns), check advantage/disadvantage (skill-mapped), save
disadvantage, environmental/water breathing, disease immunity, death-save advantage,
spell-save DC, extra damage (context-classified: unconditional / vs creature type / on crit).

## New candidate criteria — ranked

### Priority 1 (prevalent + strong price impact + feasible)

1. **temporary_hit_points** (~45-50 items) — "gain 2d6 temporary hit points" (L13039,
   L18106, L61758, L74297). Explicitly EXCLUDED from healing extraction
   (is_safe_healing_context L706-707) so currently unpriced. Weapons/wondrous/shields/
   potions. Moderate-strong positive (+300-1500 gp). Feasibility: easy-medium (dice parse +
   frequency context: on-kill vs per-action vs daily differ ~3x).
2. **hp_maximum_increase** (~20-25) — "hit point maximum increases by 1 for each level"
   (L17525), "+10 + level" (L20048), "+20 flat" (L33164). Armor/wondrous/potions. Strong
   positive, scaling. Easy regex.
3. **initiative_bonus** (~25-30) — "+2 bonus to initiative" (L15946), "advantage on
   initiative rolls" (L20865, L83076). Wondrous/shields/weapons. Moderate positive
   (+400-2000 gp; advantage > flat +2 > conditional +d8). NOT captured by check_advantage
   (initiative is not a skill/ability check target). Easy.
4. **extradimensional_storage** (~30) — Bag of Holding / Haversack / Portable Hole /
   gloves / scarves (L21806, L26820, L53416, L57112). Currently priced only via
   is_wondrous + spell value, not capacity. Strong positive; capacity variance (6 vs 64 cu
   ft) drives 2-5x within-tier spread. Medium (capacity parse needed or keyword overvalues).
5. **summon_conjure_companion** (~35-40) — Horn of Valhalla berserkers (L58952), giant
   octopus bracers (L26122), turret (L31078), deck summons (L85060). Strong positive,
   action economy, rare-legendary (+2k-15k). Keyword easy; correct valuation needs
   CR/duration (hard) — ship keyword-tier first.
6. **regeneration_continuous** (~10-15) — "regain 1d6 hit points every 10 minutes" /
   "regain 15 hit points at the end of each hour" (Ring of Regeneration archetype,
   Trollgut Rope L93543). Very strong positive (per-10-min >> daily; +5k-20k at legendary).
   Medium (rate parse; distinct from healing_daily_hp which requires dawn/day anchors).

### Priority 2

7. **reroll_mechanic** (~10-15) — "reroll one failed D20 Test" (L64183), "reroll the
   weapon's damage dice" (L19393), forced enemy save rerolls (L61637). Strong positive;
   reroll-save > reroll-damage. Easy regex, target-type nuance medium.
8. **attack_roll_advantage** (~30) — "you have advantage on attack rolls" / ally-granted
   (L64034). NOT extracted (code handles check/save advantage only). Strong positive
   (+1000-3000 gp). Medium: actor filter required (Heavy/Mastery boilerplate false
   positives; enemy-debuff exclusion like effect_clauses L636-654).
9. **attacks_against_you_disadvantage** (~10) — "attack rolls against you have
   disadvantage" (L3706, L68441). Strong defensive. Easy.
10. **telepathy_range** (~25) — "telepathy with a range of 30 feet" (L56962) vs 1-mile
    scout (L21460) vs unlimited sentient (L23540). Low-moderate positive. Easy + range
    parse; filter attached-spell noise (Rary's Telepathic Bond already priced).
11. **charm_fright_protection_gap** (~25) — "you can't be charmed or frightened" (L53757),
    "advantage on saves vs being charmed" (L64079), ally auras (L15972). Partially covered
    (condition_immunity_prose regex `immune to the X condition` misses "can't be charmed";
    conditional_save_advantage L844 catches some). Medium.
12. **size_change_prose** (~15-20) — "grow larger as if affected by enlarge/reduce"
    (L30865), height growth (L33164). attachedSpells captures tagged enlarge/reduce but
    misses prose forms; dedupe rule needed to avoid double-count. Moderate.
13. **ethereal_gaseous_phase** (~15) — "gaseous form", "ethereal", "pass through tiny
    openings" (L9677). Infiltration/escape utility. Medium.
14. **maximum_damage_vs_type** (~5-10) — "deals maximum damage when attacking a Plant"
    (Hew, L57100). Same shape as extra-damage vs-creature-type (0.25 multiplier analog).
    Easy-medium.

### Priority 3 (niche / hard)

15. **exhaustion_immunity_mitigation** (~8-12) — "immune to exhaustion" (L18686),
    "exhaustion level reduced by 2" (L9665). Easy. Niche; conditionImmune JSON rarely
    lists exhaustion.
16. **wealth_creation** (~5-10) — food/water/gem/coin creation per day (L58722, L59919).
    Hard: needs economy model + daily caps; gem/coin loops are price-breaking if uncapped.
17. **item_destruction_downside** (~5) — "destroyed" drawbacks (negative pricing signal).
    Medium; pairs with curse_effects.
18. **random_property_tables** (~10) — "roll on table" mechanics beyond artifact
    minor/major. Hard: table parsing.

## Refinements to existing criteria (not new criteria)

- `teleportation` is a bare boolean — no distance/action-type/frequency nuance
  (60-ft reaction escape vs at-will vs 1/day plane shift price very differently).
- `invisibility_atwill` detection (L749-751) is fragile (prefix spell-filter via
  find-index arithmetic); worth a robustness pass.
- `flight_limited` keyword list includes "up to" (L726) — likely misclassifies some
  unlimited flight as limited.

## Recommended next step

User picks criteria from this catalog; each pick becomes an implementation ticket shipping
through the standard ritual (impact report → price-creep guardrail → anchor-drift review →
user sign-off; ML retrain after every criteria change per pricing authority policy).
Suggested first wave: 1, 2, 3 (easy, prevalent, isolated from anchors).
