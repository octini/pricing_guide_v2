# Save Advantage Impact Report for 2026-07-12 List

## Scope and method

- Raw input: `2026_07_12_item_list.json` (left untracked).
- Old behavior: `src.criteria_extractor.extract_prose_criteria` from `c6722796b7bb1a2ec1d78306d6b487dae76e4d62` extracted in a temporary `git archive` copy under `/tmp`; the main worktree was not checked out or mutated.
- New behavior: current worktree extractor after the minion/non-wearer bridge guard and policy acceptance.
- Prose flattening: same deterministic `_entry_text` helper used by `scripts/criteria_preflight_2026_07_12.py`.
- Direct valuation estimate: `400 gp * (len(new_save_advantage) - len(old_save_advantage))`, matching `src/pricing_engine.py` lines 1040-1044.
- Approximate rule-price estimate: current `src.pricing_engine.calculate_price` with identical current criteria except `save_advantage` swapped between old/new extraction. Exact current processed `(name, source)` matches include current amalgamation fields; 2026-only or source-renamed rows use raw item criteria only. This does not run the pipeline.

## Accepted policy decisions

- Accept the 9 removals of old false-positive `save_advantage` rows.
- Keep generic `saving throws` at 400 gp for now; do not price it higher than one save-advantage entry.
- Defer any discounting for conditional/narrow save advantage until later; no pricing change now.
- Keep aura/ally save-advantage rows out of price-bearing `save_advantage` for now; revisit if/when a party-benefit criterion is added.
- Full pricing is allowed to proceed after this gate, subject to existing broader curation and canonical migration steps.

## Summary

| Metric | Count / value |
|---|---:|
| Items scanned | 12243 |
| Items with old `save_advantage` | 29 |
| Items with new `save_advantage` | 70 |
| Items with old generic `saving throws` | 0 |
| Items with new generic `saving throws` | 30 |
| Items whose `save_advantage` changed | 60 |
| Rows adding any save_advantage value | 51 |
| Rows removing only old save_advantage values | 9 |
| Rows adding generic `saving throws` | 30 |
| Rows adding ability-specific save advantage | 22 |
| Clean added rows | 31 |
| Conditional/narrow added rows | 20 |
| Aura/ally price-bearing added rows | 0 |
| Target/non-wearer price-bearing added rows | 0 |
| Current extractor false-positive added rows | 0 |
| Old false-positive rows removed by fix | 9 |
| Legitimate old rows still removed | 0 |
| Artifact affected rows | 3 |
| Legendary affected rows | 7 |
| Current-list overlap (exact or name-only) | 14 |
| Current processed/reference overlap | 14 |
| Net direct save_advantage additive delta | 18,000 gp |
| Gross direct delta for added rows | 22,400 gp |
| Direct delta removed by removal-only rows | -4,400 gp |
| Approx. rule-price delta where computable | 224,914 gp |
| Approx. rule-price changed rows | 54 |
| Rows where early return/floor masks direct delta | 6 |
| Approx. pricing errors | 0 |

### Review class counts

| Class | Rows |
|---|---:|
| CLEAN HIT | 31 |
| REVIEW: conditional/narrow generic save advantage | 20 |
| FIXED: old disadvantage false positive removed | 9 |

### Affected rarities

| Rarity | Changed rows |
|---|---:|
| uncommon | 17 |
| rare | 15 |
| very rare | 14 |
| legendary | 7 |
| artifact | 3 |
| unknown (magic) | 3 |
| varies | 1 |

### Top affected sources

| Source | Changed rows |
|---|---:|
| 24GriffonsSaddlebag1 | 12 |
| GrimHollowCG24 | 9 |
| HelianasGuidetoMonsterHunting | 7 |
| GriffonsSaddlebag2 | 5 |
| CrookedMoon24 | 4 |
| XDMG | 3 |
| HumblewoodTales | 3 |
| CthulhuTorchlight | 2 |
| PaBTSO | 1 |
| ToA | 1 |

## Required named items

| Item | Source | Rarity | Type | Old | New | Direct delta | Approx. rule old → new | Review class | Evidence |
|---|---|---|---|---|---|---:|---:|---|---|
| Ascendant Scaled Ornament | FTD | legendary |  | `[]` | `[]` | 0 gp | — | EXCLUDED: not wearer save_advantage | Not present in price-bearing save_advantage after current extractor guards.<br><br>Excerpt: to be fashioned from a dragon's scale, tooth, or claw, or it incorporates images in those shapes. You gain a +1 bonus to AC, and you can't be charmed or frightened. Moreover, each creature of your choice within 30 feet of you has advantage on saving throws it makes to avoid being charmed or frightened or to end those conditions on itself. When you would take damage of the type dealt by the breath of the dragon in whose hoard the ornament became Wakened, you can use your reaction to take no damage instead, and you regain hit points equal to the damage you would have taken. Once this property is used, it can't be used again until the next dawn. While you are wearing the ornament, you gain a fl |
| Crown of the Barrow King (Legendary) | CrookedMoon24 | legendary |  | `[]` | `[]` | 0 gp | — | EXCLUDED: not wearer save_advantage | Not present in price-bearing save_advantage after current extractor guards.<br><br>Excerpt: e malice and corruption that the Barrow King imbued into it. While you wear the crown, you gain a +3 bonus determined by the crown's rarity to spell attack rolls and to your spell save DC for Necromancy spells and spells that deal Necrotic damage, and you can use the following properties. Demand of the Dead (Rare+) You can cast Speak with Dead from the crown. Grave Grasp (Rare+) You know the Chill Touch cantrip. Your spell attack bonus with it is +9 (Rare), +10 (Very Rare), or +11 (Legendary). Necromancer's Call (Rare+) You can cast Animate Dead from the crown. It can be used to cast this spell three times, regaining all expended uses daily at dusk. Master of Undeath (Very Rare+) Undead that |
| Crown of the Barrow King (Very Rare) | CrookedMoon24 | very rare |  | `[]` | `[]` | 0 gp | — | EXCLUDED: not wearer save_advantage | Not present in price-bearing save_advantage after current extractor guards.<br><br>Excerpt: e malice and corruption that the Barrow King imbued into it. While you wear the crown, you gain a +2 bonus determined by the crown's rarity to spell attack rolls and to your spell save DC for Necromancy spells and spells that deal Necrotic damage, and you can use the following properties. Demand of the Dead (Rare+) You can cast Speak with Dead from the crown. Grave Grasp (Rare+) You know the Chill Touch cantrip. Your spell attack bonus with it is +9 (Rare), +10 (Very Rare), or +11 (Legendary). Necromancer's Call (Rare+) You can cast Animate Dead from the crown. It can be used to cast this spell three times, regaining all expended uses daily at dusk. Master of Undeath (Very Rare+) Undead that |
| Indorius's Crown (Adept) | GrimHollowCG24 | artifact |  | `[]` | `['charisma']` | 400 gp | 339,758 gp → 340,271 gp | CLEAN HIT | No obvious heuristic concern.<br><br>Excerpt: resist. The crown does not, however, provide its wearer with wisdom. Aspirant At this tier of Attunement, you have the following benefits while wearing Indorius's Crown: You have Advantage on Charisma ability checks and saving throws. The crown has 12 charges. You can expend 1 or more charges to cast one of the following spells (save 18) from it: Compulsion (4 charges), Dominate Person (5 charges), Hellish Rebuke (1 charge), Hold Person (2 charges), or Suggestion (2 charges). The crown regains 2d4 + 4 expended charges at dawn. You also gain the following curse: Your sense of authority means you tend to pay less attention to the needs of others. While attuned to the crown, you have Disadvant |

## Artifact and legendary affected rows

| Item | Source | Rarity | Old | New | Direct delta | Approx. rule delta | Review class | Current/reference overlap |
|---|---|---|---|---|---:|---:|---|---|
| Indorius's Crown (Adept) | GrimHollowCG24 | artifact | `[]` | `['charisma']` | 400 gp | 513 gp | CLEAN HIT | no; — |
| Indorius's Crown (Aspirant) | GrimHollowCG24 | artifact | `[]` | `['charisma']` | 400 gp | 513 gp | CLEAN HIT | no; — |
| Indorius's Crown (Master) | GrimHollowCG24 | artifact | `[]` | `['charisma']` | 400 gp | 513 gp | CLEAN HIT | no; — |
| Obsidian Flint Dragon Plate | BGDIA | legendary | `[]` | `['saving throws']` | 400 gp | 0 gp | REVIEW: conditional/narrow generic save advantage | exact current processed overlap; amalgamated_price=28687.5; price_confidence=multi; price_source=rule; has_reference_source=True |
| Purity Spear | 24GriffonsSaddlebag1 | legendary | `[]` | `['constitution', 'wisdom']` | 800 gp | 101,607 gp | CLEAN HIT | no; — |
| Red Claw's Regalia | 24GriffonsSaddlebag1 | legendary | `[]` | `['constitution']` | 400 gp | 360 gp | CLEAN HIT | no; — |
| Runestone of the Wild Titan (Legendary) | CrookedMoon24 | legendary | `[]` | `['strength', 'constitution']` | 800 gp | 720 gp | CLEAN HIT | no; — |
| Stonebreaker's Breastplate | BGG | legendary | `[]` | `['saving throws']` | 400 gp | 30,712 gp | REVIEW: conditional/narrow generic save advantage | exact current processed overlap; price_confidence=none; price_source=rule; has_reference_source=False |
| The Sword out of the Stone | HelianasGuidetoMonsterHunting | legendary | `[]` | `['charisma']` | 400 gp | 35,340 gp | CLEAN HIT | no; — |
| Whistle of the Vagrant (Legendary) | CrookedMoon24 | legendary | `[]` | `['saving throws']` | 400 gp | 32,580 gp | CLEAN HIT | no; — |

## Known-good/current-list overlap

Definitions: exact current-list overlap matches `(name, source)` in `items-sublist-data.json`; name-only overlap matches an existing canonical item name with a different/missing source. Reference overlap uses exact/name match in `data/processed/items_priced.csv` and reports official/amalgamated/reference fields when present.

| Item | Source | Rarity | Old | New | Direct delta | Review class | Overlap / anchor summary |
|---|---|---|---|---|---:|---|---|
| Belt of Dwarvenkind | XDMG | rare | `[]` | `['saving throws']` | 400 gp | CLEAN HIT | exact current processed overlap; amalgamated_price=5792.0; price_confidence=multi; price_source=rule; has_reference_source=True |
| Bracers of Celerity | PaBTSO | rare | `[]` | `['saving throws']` | 400 gp | CLEAN HIT | exact current processed overlap; price_confidence=none; price_source=rule; has_reference_source=False |
| Dancing Monkey Fruit | ToA | unknown (magic) | `['dexterity']` | `[]` | -400 gp | FIXED: old disadvantage false positive removed | exact current processed overlap; official_price_gp=5.0; price_confidence=none; price_source=rule; has_reference_source=False |
| Deck of Wonder | BMT | uncommon | `['intelligence']` | `[]` | -400 gp | FIXED: old disadvantage false positive removed | exact current processed overlap; price_confidence=none; price_source=rule; has_reference_source=False |
| Dust of Deliciousness | EGW | uncommon | `['wisdom']` | `[]` | -400 gp | FIXED: old disadvantage false positive removed | exact current processed overlap; amalgamated_price=168.75; price_confidence=multi; price_source=rule; has_reference_source=True |
| Mind Lash | VGM | rare | `['intelligence', 'wisdom', 'charisma']` | `[]` | -1,200 gp | FIXED: old disadvantage false positive removed | exact current processed overlap; price_confidence=none; price_source=rule; has_reference_source=False |
| Necklace of Adaptation | XDMG | uncommon | `[]` | `['saving throws']` | 400 gp | REVIEW: conditional/narrow generic save advantage | exact current processed overlap; amalgamated_price=693.75; price_confidence=multi; price_source=rule; has_reference_source=True |
| Obsidian Flint Dragon Plate | BGDIA | legendary | `[]` | `['saving throws']` | 400 gp | REVIEW: conditional/narrow generic save advantage | exact current processed overlap; amalgamated_price=28687.5; price_confidence=multi; price_source=rule; has_reference_source=True |
| Orb of the Stein Rune | SKT | rare | `[]` | `['saving throws', 'strength']` | 800 gp | REVIEW: conditional/narrow generic save advantage | exact current processed overlap; amalgamated_price=2700.0; price_confidence=solo; price_source=rule; has_reference_source=True |
| Periapt of Health | XDMG | uncommon | `[]` | `['saving throws']` | 400 gp | REVIEW: conditional/narrow generic save advantage | exact current processed overlap; amalgamated_price=2488.0; price_confidence=multi; price_source=rule; has_reference_source=True |
| Potion of Advantage | WBtW | uncommon | `[]` | `['saving throws']` | 400 gp | CLEAN HIT | exact current processed overlap; price_confidence=none; price_source=rule; has_reference_source=False |
| Slumbering Scaled Ornament | FTD | uncommon | `[]` | `['saving throws']` | 400 gp | CLEAN HIT | exact current processed overlap; price_confidence=none; price_source=rule; has_reference_source=False |
| Stonebreaker's Breastplate | BGG | legendary | `[]` | `['saving throws']` | 400 gp | REVIEW: conditional/narrow generic save advantage | exact current processed overlap; price_confidence=none; price_source=rule; has_reference_source=False |
| Vampire Blood Potion | MonstersOfDrakkenheim | very rare | `[]` | `['strength', 'dexterity', 'charisma']` | 1,200 gp | CLEAN HIT | exact current processed overlap; price_confidence=none; price_source=rule; has_reference_source=False |

## Rows needing review before pricing sign-off

| Item | Source | Rarity | Type | Old | New | Direct delta | Approx. rule old → new | Review class | Excerpt |
|---|---|---|---|---|---|---:|---:|---|---|
| Obsidian Flint Dragon Plate | BGDIA | legendary | HA | `[]` | `['saving throws']` | 400 gp | 28,688 gp → 28,688 gp | REVIEW: conditional/narrow generic save advantage | You gain a +2 bonus to AC and resistance to poison damage while you wear this armor. In addition, you gain advantage on ability checks and saving throws made to avoid or end the grappled condition on yourself. |
| Stonebreaker's Breastplate | BGG | legendary | MA | `[]` | `['saving throws']` | 400 gp | 60,345 gp → 91,058 gp | REVIEW: conditional/narrow generic save advantage | eoning, piercing, and slashing damage and are immune to being knocked prone. Invoking the Rune As an action, you can invoke the breastplate's rune to cast the wall of stone spell (save 14) with it. When you cast the spell in this way, you have advantage on saving throws made to maintain concentration on the spell. Once the rune has been invoked, it can't be invoked again until the next dawn. This armor consists of a fitted metal chest piece worn with supple leather. Although it leaves the legs and arms relatively unprotected, this armor provides good protection for the wearer's vital organs while leaving the wearer relatively unencumbered. |
| Orb of the Stein Rune | SKT | rare |  | `[]` | `['saving throws', 'strength']` | 800 gp | 2,700 gp → 2,700 gp | REVIEW: conditional/narrow generic save advantage | k only while it's on your person. Indomitable Stand As an action, you can channel the orb's magic to hold your ground. For the next minute or until you move any distance, you have advantage on all checks and saving throws to resist effects that force you to move. In addition, any enemy that moves to a space within 10 feet of you must succeed on a 12 Strength saving throw or be unable to move any farther this turn. Stone Soul You can't be petrified. Earthen Step You can cast meld into stone as a bonus action. Once you use this property, you can't use it again until you finish a short or long rest. Gift of Stone You can transfer the orb's magic to a nonmagical item—a shield or a pair of boots— |
| Blessed Reliquary | GrimHollowCG24 | rare |  | `[]` | `['saving throws']` | 400 gp | 3,600 gp → 3,960 gp | REVIEW: conditional/narrow generic save advantage | This small wooden or ivory box holds a piece of a saint. While it is on your person, you gain the following benefits: You have Advantage on saving throws caused by Undead creatures. You can use each of your Channel Divinity class features one additional time. When you use Turn Undead, you may choose for the targets to have Disadvantage on their saving throws. This can be used once. You regain its use after a Long Rest. |
| Couatl Herald's Mantle | 24GriffonsSaddlebag1 | uncommon |  | `[]` | `['saving throws']` | 400 gp | 8,600 gp → 8,920 gp | REVIEW: conditional/narrow generic save advantage | This magic cloak is given to those deemed kindhearted and responsible by a Celestial. While wearing the mantle, you have Advantage on saving throws to avoid or end the Poisoned condition and the effects of magical contagions. In addition, you are immune to any effect that would sense your emotions. Flight of the Couatls While you're attuned to 3 items with this property, you gain a Fly Speed of 30 feet. If you already have a Fly Speed, it increases by 30 feet instead. |
| Frefil's Jolly Oozebean Sugarbombs | 24GriffonsSaddlebag1 | uncommon |  | `[]` | `['saving throws']` | 400 gp | 1,350 gp → 1,750 gp | REVIEW: conditional/narrow generic save advantage | causes the effects of the first sugarbomb to immediately end and be replaced by the new one's. This rapid change is difficult to stomach, forcing you to make a DC 13 Constitution saving throw. On a failed save, you have the Poisoned condition for 1 minute. 1 White You can breathe underwater. 2 Black You have Resistance to Acid damage and can safely eat otherwise inedible and nonpoisonous organic materials. 3 Blue Whenever you successfully grappled a creature or another creature successfully grapples you, that creature takes 1d8 Acid damage. 4 Gray You have Advantage on saving throws to avoid or end the Charmed and Frightened conditions. 5 Gold You gain a Climb Speed equal to your Speed. 6 R |
| Humble Frock | GrimHollowCG24 | uncommon |  | `[]` | `['saving throws']` | 400 gp | 675 gp → 1,035 gp | REVIEW: conditional/narrow generic save advantage | While wearing this frock and not wearing any armor, Opportunity Attack rolls against you have Disadvantage. If you have reached at least Stage 2 of the Seraph, you have Advantage on saving throws to avoid revealing your true nature. |
| Hunter's Zeal | GrimHollowCG24 | rare | P\|XPHB | `[]` | `['saving throws']` | 400 gp | 2,600 gp → 2,800 gp | REVIEW: conditional/narrow generic save advantage | s immune system into a hyperactive state. When you drink this potion, you have Immunity to Poison damage and to the Poisoned condition for 1 hour. While the effect lasts, you have Advantage on saving throws to avoid becoming cursed. When the potion's effect ends, you gain 1 level of Exhaustion. |
| Necklace of Adaptation | XDMG | uncommon |  | `[]` | `['saving throws']` | 400 gp | 694 gp → 694 gp | REVIEW: conditional/narrow generic save advantage | While wearing this necklace, you can breathe normally in any environment, and you have Advantage on saving throws made to avoid or end the Poisoned condition. |
| Night Messenger's Coat | TalesFromTheShadows | uncommon |  | `[]` | `['saving throws']` | 400 gp | 6,750 gp → 7,150 gp | REVIEW: conditional/narrow generic save advantage | d from other sources automatically fail while you wear a night messenger's coat. Witchlight Sight You can see and sense the trails left behind by witchlight. Shadow Sense You have advantage on Wisdom (Survival) checks made to navigate or avoid getting lost in the Shadow Realm. Incorruptible You have advantage on all saving throws made to resist shadow corruption. |
| Overgrown Barkshield | HelianasGuidetoMonsterHunting | varies | S | `[]` | `['saving throws']` | 400 gp | 675 gp → 1,035 gp | REVIEW: conditional/narrow generic save advantage | e unable to hold a shield and you gain the following benefits: You gain 1d8 temporary hit points. You gain the benefits of the barkskin spell (no concentration required). You have advantage on saving throws made to resist being poisoned. When this effect ends, the barkshield falls from its place on your torso, fading to a lifeless shade of grey. This property can't be used again until you finish a long rest when the shield blooms with life once more. Vines and Thorns While attuned to this shield, you can use an action to animate one of the shield's thorny vines and make a melee weapon attack (+5 to hit) against one target within 30 feet of you. On a hit, the target takes 2d8 piercing damage, |
| Overgrown Barkshield (rare) | HelianasGuidetoMonsterHunting | rare | S | `[]` | `['saving throws']` | 400 gp | 3,600 gp → 3,960 gp | REVIEW: conditional/narrow generic save advantage | e unable to hold a shield and you gain the following benefits: You gain 3d8 temporary hit points. You gain the benefits of the barkskin spell (no concentration required). You have advantage on saving throws made to resist being poisoned. When this effect ends, the barkshield falls from its place on your torso, fading to a lifeless shade of grey. This property can't be used again until you finish a long rest when the shield blooms with life once more. Vines and Thorns While attuned to this shield, you can use an action to animate one of the shield's thorny vines and make a melee weapon attack (+8 to hit, reach 30 ft.) against one target. On a hit, the target takes 3d8 piercing damage, and, if |
| Overgrown Barkshield (uncommon) | HelianasGuidetoMonsterHunting | uncommon | S | `[]` | `['saving throws']` | 400 gp | 675 gp → 1,035 gp | REVIEW: conditional/narrow generic save advantage | e unable to hold a shield and you gain the following benefits: You gain 1d8 temporary hit points. You gain the benefits of the barkskin spell (no concentration required). You have advantage on saving throws made to resist being poisoned. When this effect ends, the barkshield falls from its place on your torso, fading to a lifeless shade of grey. This property can't be used again until you finish a long rest when the shield blooms with life once more. Vines and Thorns While attuned to this shield, you can use an action to animate one of the shield's thorny vines and make a melee weapon attack (+5 to hit, reach 30 ft.) against one target. On a hit, the target takes 2d8 piercing damage, and, if |
| Overgrown Barkshield (very rare) | HelianasGuidetoMonsterHunting | very rare | S | `[]` | `['saving throws']` | 400 gp | 675 gp → 1,035 gp | REVIEW: conditional/narrow generic save advantage | e unable to hold a shield and you gain the following benefits: You gain 5d8 temporary hit points. You gain the benefits of the barkskin spell (no concentration required). You have advantage on saving throws made to resist being poisoned. When this effect ends, the barkshield falls from its place on your torso, fading to a lifeless shade of grey. This property can't be used again until you finish a long rest when the shield blooms with life once more. Vines and Thorns While attuned to this shield, you can use an action to animate one of the shield's thorny vines and make a melee weapon attack (+10 to hit, reach 30 ft.) against one target. On a hit, the target takes 4d8 piercing damage, and, i |
| Periapt of Health | XDMG | uncommon |  | `[]` | `['saving throws']` | 400 gp | 2,488 gp → 2,488 gp | REVIEW: conditional/narrow generic save advantage | While wearing this pendant, you can take a Magic action to regain 2d4 + 2 Hit Points. Once used, this property can't be used again until the next dawn. In addition, you have Advantage on saving throws to avoid or end the Poisoned condition while you wear this pendant. |
| Plaguebane Mask | 24GriffonsSaddlebag1 | rare |  | `[]` | `['saving throws']` | 400 gp | 4,866 gp → 5,266 gp | REVIEW: conditional/narrow generic save advantage | to eat or speak more clearly. The mask's beak is lined with magical flowers that react to and purify airborne toxins before they pass through it. While wearing the mask, you have Advantage on saving throws to avoid or end the Poisoned condition as well as the effects of magical contagions if they came from an airborne source, and you have Resistance to any Poison damage that those effects might deal. In addition, the flowers have 3 charges and regain 1d3 expended charges daily at dawn as new flowers bloom. As a Magic action, you can hold the beak's nostrils closed with a free hand and expend 1 charge to exhale a 15-foot Cone [Area of Effect] of thick pollen in front of you. Each creature in |
| Ring of Seething | 24GriffonsSaddlebag1 | uncommon | RG\|XDMG | `[]` | `['saving throws']` | 400 gp | 506 gp → 776 gp | REVIEW: conditional/narrow generic save advantage | he touch and has several cracks throughout its otherwise smooth body. When you attune to the ring, choose a creature type: Aberration, Celestial, Dragon, Elemental, Fey, Fiend, or Undead. While wearing the ring, its normally cool band glows red hot when a creature of the chosen type is within 60 feet of you. In addition, you have Advantage on saving throws to avoid or end the Charmed and Frightened conditions caused by creatures of that type. Though it seemingly radiates heat, the ring feels only faintly warm to you. Small pieces of the metal band hover above the surface of the ring when glowing in this way. Curse This ring is cursed. Attuning to it curses you until you are targeted by a Rem |
| Shaedenstaff | 24GriffonsSaddlebag1 | very rare | M\|XPHB | `[]` | `['saving throws']` | 400 gp | 33,113 gp → 33,433 gp | REVIEW: conditional/narrow generic save advantage | This staff is made from the reclaimed horn of a huge Undead creature. While you're attuned to the staff, you have Advantage on saving throws to resist mental stress effects. The staff can also be wielded as a magic Quarterstaff. The staff has 15 charges for the following properties and regains 2d6 + 3 expended charges daily at dusk. If you expend the last charge, roll 1d20. On a 1, the staff disintegrates in a plume of pitch black smoke and emits a terrifying scream audible out to 300 feet. Annihilating Strike When you hit with a melee attack using this staff, you ca |
| Sirensong Silencer | 24GriffonsSaddlebag1 | uncommon |  | `[]` | `['saving throws']` | 400 gp | 750 gp → 1,150 gp | REVIEW: conditional/narrow generic save advantage | You can place this golden ear cuff over your ear as a Magic action. While wearing the cuff, you have Advantage on saving throws to avoid or end the Charmed condition. Tapping the ear cuff twice (no action required) causes you to have the Deafened condition, although you can still faintly hear the sound of the ocean. Doing so again ends this effect on you. |
| Ventilation Unit D-20 | HelianasGuidetoMonsterHunting | rare |  | `[]` | `['saving throws']` | 400 gp | 4,050 gp → 4,410 gp | REVIEW: conditional/narrow generic save advantage | ygen analogue, allowing its wearer to breathe in otherwise impossible conditions. Breathe Easy While wearing this helmet, you can breathe normally in any environment, and you have advantage on saving throws made against harmful gases and vapours that you inhale (such as the stinking cloud effect, inhaled poisons, and the breath weapons of some dragons, but not contact toxins like cloudkill). Biomantic Overload While wearing this helmet, you can use a bonus action to ingest the chemicals in it before they are combined into a gas, causing your body to go into a mutated state of enhanced adaptability for 1 minute. During this time, immediately after you take damage from any source, you gain res |
| Caltrooze | HelianasGuidetoMonsterHunting | uncommon |  | `['dexterity']` | `[]` | -400 gp | 64,150 gp → 63,750 gp | FIXED: old disadvantage false positive removed | zes cause them to roll and shift. Caltrops As an action, you can spread a single bag of caltroozes to cover a 5-foot square. Any creature that enters the area must succeed on a 15 Dexterity saving throw or stop moving and take 1 piercing damage. Until the creature regains at least 1 hit point, its walking speed is reduced by 10 feet. A creature that moves through the area of the caltroozes at half speed makes the saving throw against them with advantage. Corrosive Chaos If a creature fails the Dexterity saving throw, roll a d4 and consult the table below to determine what additional effects take place: 1 The acid in the caltroozes discharges in a single burst. The creature takes an additiona |
| Dancing Monkey Fruit | ToA | unknown (magic) | OTH | `['dexterity']` | `[]` | -400 gp | 1,150 gp → 750 gp | FIXED: old disadvantage false positive removed | This rare magical fruit produces enough juice to fill a vial. Any humanoid that eats a dancing monkey fruit or drinks its juice must succeed on a 14 Constitution saving throw or begin a comic dance that lasts for 1 minute. Humanoids that can't be poisoned are immune to this magical effect. The dancer must use all its movement to dance without leaving its space and has disadvantage on attack rolls and Dexterity saving throws, and other creatures have advantage on attack rolls against it. Each time it takes damage, the dancer can repeat the saving throw, ending the effect on itself on a success. When the dancing effect ends, the humanoid suffers the poisoned condition for 1 h |
| Deck of Wonder | BMT | uncommon |  | `['intelligence']` | `[]` | -400 gp | 13,431 gp → 13,031 gp | FIXED: old disadvantage false positive removed | k and damage rolls. This bonus lasts for 8 hours. Chancellor Within 8 hours of drawing this card, you can cast Augury once as an action, requiring no material components. Use your Intelligence, Wisdom, or Charisma as the spellcasting ability (your choice). Chaos You gain resistance to one of the following damage types (chosen by the DM): acid, cold, fire, lightning, or thunder. This resistance lasts for 1d12 days. Coin Five pieces of jewelry, each worth 100 gp, or ten gemstones, each worth 50 gp, appear at your feet. Crown You learn the Friends cantrip. Use your Intelligence, Wisdom, or Charisma as the spellcasting ability (your choice). If you already know this cantrip, the card has no effe |
| Dust of Deliciousness | EGW | uncommon |  | `['wisdom']` | `[]` | -400 gp | 169 gp → 169 gp | FIXED: old disadvantage false positive removed | reddish brown dust can be sprinkled over any edible substance to greatly improve the flavor. The dust also dulls the eater's senses: anyone eating food treated with this dust has disadvantage on Wisdom ability checks and Wisdom saving throws for 1 hour. There is enough dust to flavor six servings. |
| Fool's Lamp | GriffonsSaddlebag2 | very rare |  | `['dexterity']` | `[]` | -400 gp | 1,150 gp → 750 gp | FIXED: old disadvantage false positive removed | see as if you were in the lamp's space, but are otherwise incapacitated and deafened. At the end of each of your turns while you're in the demiplane, you can make a DC 20 Charisma saving throw, ending the effect early on a success. At the end of the duration, you return to the nearest unoccupied space within 5 feet of the lamp. 2 A fireball (5th-level version, save DC 16) erupts, centered on you. 3 You're unintelligible for 2d6 hours, during which time you only speak in nonsensical sounds. 4 You're under the effect of the faerie fire spell for 24 hours. 5 A hostile air elemental (40%), earth elemental (20%), fire elemental (20%), or water elemental (20%) elemental appears in an unoccupied sp |
| Lamian Facestealer | GriffonsSaddlebag2 | rare | M | `['wisdom']` | `[]` | -400 gp | 7,900 gp → 7,500 gp | FIXED: old disadvantage false positive removed | egains 1d3 expended charges daily at dusk. When you hit a humanoid with this weapon, you can expend 1 of its charges to immediately recreate the effect of the disguise self spell (save DC 15), taking on the appearance of the target. When you do, the dagger's metal face changes to match the appearance. This version of the spell allows you to seem up to 3 feet shorter or taller when taking on the target's appearance. When you take on a creature's appearance in this way, that creature must make a DC 15 Wisdom saving throw. On a failed save, that creature has disadvantage on Wisdom saving throws and all ability checks as long as it can see you while you share its appearance in this way. |
| Lindwyrm Venom | GrimHollowLairsEtharis | very rare | P | `['strength']` | `[]` | -400 gp | 575 gp → 375 gp | FIXED: old disadvantage false positive removed | terrible venom is extracted and distilled from the deadly lindwyrm. It can be delivered via ingestion or a wound. A creature exposed to the venom must succeed on a 18 Constitution saving throw or take 36 (8d8) poison damage and be poisoned for 1 minute. While poisoned, the creature has disadvantage on Strength and Dexterity skill checks and saving throws. |
| Ring of the Arcane Berserker | GriffonsSaddlebag2 | rare | RG\|DMG | `['constitution']` | `[]` | -400 gp | 4,213 gp → 3,893 gp | FIXED: old disadvantage false positive removed | spell. If you do, your rage does not end at the end of your turn as a result of not attacking a hostile creature. In addition, you can concentrate on spells while raging, but have disadvantage on Constitution saving throws to maintain your concentration on them when you take damage. |
| Mind Lash | VGM | rare | M | `['intelligence', 'wisdom', 'charisma']` | `[]` | -1,200 gp | 16,160 gp → 15,200 gp | FIXED: old disadvantage false positive removed | urvive as it also strips away flesh, dealing an extra 2d4 psychic damage to any target it hits. Any creature that takes psychic damage from the mind lash must also succeed on a 15 Wisdom saving throw or have disadvantage on Intelligence, Wisdom, and Charisma saving throws for 1 minute. The creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success. |

## Full changed row list

| # | Item | Source | Rarity | Type | Old | New | Added | Removed | Direct delta | Approx. rule delta | Review class | Current overlap |
|---:|---|---|---|---|---|---|---|---|---:|---:|---|---|
| 1 | Indorius's Crown (Adept) | GrimHollowCG24 | artifact |  | `[]` | `['charisma']` | `['charisma']` | `[]` | 400 gp | 513 gp | CLEAN HIT | no |
| 2 | Indorius's Crown (Aspirant) | GrimHollowCG24 | artifact |  | `[]` | `['charisma']` | `['charisma']` | `[]` | 400 gp | 513 gp | CLEAN HIT | no |
| 3 | Indorius's Crown (Master) | GrimHollowCG24 | artifact |  | `[]` | `['charisma']` | `['charisma']` | `[]` | 400 gp | 513 gp | CLEAN HIT | no |
| 4 | Purity Spear | 24GriffonsSaddlebag1 | legendary | M\|XPHB | `[]` | `['constitution', 'wisdom']` | `['constitution', 'wisdom']` | `[]` | 800 gp | 101,607 gp | CLEAN HIT | no |
| 5 | Red Claw's Regalia | 24GriffonsSaddlebag1 | legendary |  | `[]` | `['constitution']` | `['constitution']` | `[]` | 400 gp | 360 gp | CLEAN HIT | no |
| 6 | Obsidian Flint Dragon Plate | BGDIA | legendary | HA | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 0 gp | REVIEW: conditional/narrow generic save advantage | exact |
| 7 | Stonebreaker's Breastplate | BGG | legendary | MA | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 30,712 gp | REVIEW: conditional/narrow generic save advantage | exact |
| 8 | Runestone of the Wild Titan (Legendary) | CrookedMoon24 | legendary |  | `[]` | `['strength', 'constitution']` | `['strength', 'constitution']` | `[]` | 800 gp | 720 gp | CLEAN HIT | no |
| 9 | Whistle of the Vagrant (Legendary) | CrookedMoon24 | legendary |  | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 32,580 gp | CLEAN HIT | no |
| 10 | The Sword out of the Stone | HelianasGuidetoMonsterHunting | legendary | M | `[]` | `['charisma']` | `['charisma']` | `[]` | 400 gp | 35,340 gp | CLEAN HIT | no |
| 11 | Plaguebane Mask | 24GriffonsSaddlebag1 | rare |  | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 400 gp | REVIEW: conditional/narrow generic save advantage | no |
| 12 | Wine of the Summer Court | BookOfEbonTides | rare | P | `[]` | `['charisma']` | `['charisma']` | `[]` | 400 gp | 200 gp | CLEAN HIT | no |
| 13 | Whistle of the Vagrant (Rare) | CrookedMoon24 | rare |  | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 360 gp | CLEAN HIT | no |
| 14 | Lamian Facestealer | GriffonsSaddlebag2 | rare | M | `['wisdom']` | `[]` | `[]` | `['wisdom']` | -400 gp | -400 gp | FIXED: old disadvantage false positive removed | no |
| 15 | Ring of the Arcane Berserker | GriffonsSaddlebag2 | rare | RG\|DMG | `['constitution']` | `[]` | `[]` | `['constitution']` | -400 gp | -320 gp | FIXED: old disadvantage false positive removed | no |
| 16 | Blessed Reliquary | GrimHollowCG24 | rare |  | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 360 gp | REVIEW: conditional/narrow generic save advantage | no |
| 17 | Cloak of the Stygian Bat | GrimHollowCG24 | rare |  | `[]` | `['dexterity']` | `['dexterity']` | `[]` | 400 gp | 360 gp | CLEAN HIT | no |
| 18 | Fin Symbiote | GrimHollowCG24 | rare |  | `[]` | `['constitution']` | `['constitution']` | `[]` | 400 gp | 360 gp | CLEAN HIT | no |
| 19 | Hunter's Zeal | GrimHollowCG24 | rare | P\|XPHB | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 200 gp | REVIEW: conditional/narrow generic save advantage | no |
| 20 | Overgrown Barkshield (rare) | HelianasGuidetoMonsterHunting | rare | S | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 360 gp | REVIEW: conditional/narrow generic save advantage | no |
| 21 | Ventilation Unit D-20 | HelianasGuidetoMonsterHunting | rare |  | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 360 gp | REVIEW: conditional/narrow generic save advantage | no |
| 22 | Bracers of Celerity | PaBTSO | rare |  | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 360 gp | CLEAN HIT | exact |
| 23 | Orb of the Stein Rune | SKT | rare |  | `[]` | `['saving throws', 'strength']` | `['saving throws', 'strength']` | `[]` | 800 gp | 0 gp | REVIEW: conditional/narrow generic save advantage | exact |
| 24 | Mind Lash | VGM | rare | M | `['intelligence', 'wisdom', 'charisma']` | `[]` | `[]` | `['intelligence', 'wisdom', 'charisma']` | -1,200 gp | -960 gp | FIXED: old disadvantage false positive removed | exact |
| 25 | Belt of Dwarvenkind | XDMG | rare |  | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 0 gp | CLEAN HIT | exact |
| 26 | Couatl Herald's Mantle | 24GriffonsSaddlebag1 | uncommon |  | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 320 gp | REVIEW: conditional/narrow generic save advantage | no |
| 27 | Frefil's Jolly Oozebean Sugarbombs | 24GriffonsSaddlebag1 | uncommon |  | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 400 gp | REVIEW: conditional/narrow generic save advantage | no |
| 28 | Ring of Seething | 24GriffonsSaddlebag1 | uncommon | RG\|XDMG | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 270 gp | REVIEW: conditional/narrow generic save advantage | no |
| 29 | Sirensong Silencer | 24GriffonsSaddlebag1 | uncommon |  | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 400 gp | REVIEW: conditional/narrow generic save advantage | no |
| 30 | Deck of Wonder | BMT | uncommon |  | `['intelligence']` | `[]` | `[]` | `['intelligence']` | -400 gp | -400 gp | FIXED: old disadvantage false positive removed | exact |
| 31 | Dust of Deliciousness | EGW | uncommon |  | `['wisdom']` | `[]` | `[]` | `['wisdom']` | -400 gp | 0 gp | FIXED: old disadvantage false positive removed | exact |
| 32 | Slumbering Scaled Ornament | FTD | uncommon |  | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 360 gp | CLEAN HIT | exact |
| 33 | Full Moon Extract | GrimHollowCG24 | uncommon | P\|XPHB | `[]` | `['strength']` | `['strength']` | `[]` | 400 gp | 200 gp | CLEAN HIT | no |
| 34 | Humble Frock | GrimHollowCG24 | uncommon |  | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 360 gp | REVIEW: conditional/narrow generic save advantage | no |
| 35 | Caltrooze | HelianasGuidetoMonsterHunting | uncommon |  | `['dexterity']` | `[]` | `[]` | `['dexterity']` | -400 gp | -400 gp | FIXED: old disadvantage false positive removed | no |
| 36 | Overgrown Barkshield (uncommon) | HelianasGuidetoMonsterHunting | uncommon | S | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 360 gp | REVIEW: conditional/narrow generic save advantage | no |
| 37 | Talons of the Squall | HumblewoodTales | uncommon |  | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 360 gp | CLEAN HIT | no |
| 38 | Incredible Luck | ObojimaTallGrass | uncommon | P | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 200 gp | CLEAN HIT | no |
| 39 | Night Messenger's Coat | TalesFromTheShadows | uncommon |  | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 400 gp | REVIEW: conditional/narrow generic save advantage | no |
| 40 | Potion of Advantage | WBtW | uncommon | P | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 200 gp | CLEAN HIT | exact |
| 41 | Necklace of Adaptation | XDMG | uncommon |  | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 0 gp | REVIEW: conditional/narrow generic save advantage | exact |
| 42 | Periapt of Health | XDMG | uncommon |  | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 0 gp | REVIEW: conditional/narrow generic save advantage | exact |
| 43 | Pnakotic Manuscripts | CthulhuTorchlight | unknown (magic) |  | `[]` | `['dexterity']` | `['dexterity']` | `[]` | 400 gp | 320 gp | CLEAN HIT | no |
| 44 | Seven Cryptical Books of Hsan | CthulhuTorchlight | unknown (magic) |  | `[]` | `['wisdom']` | `['wisdom']` | `[]` | 400 gp | 320 gp | CLEAN HIT | no |
| 45 | Dancing Monkey Fruit | ToA | unknown (magic) | OTH | `['dexterity']` | `[]` | `[]` | `['dexterity']` | -400 gp | -400 gp | FIXED: old disadvantage false positive removed | exact |
| 46 | Overgrown Barkshield | HelianasGuidetoMonsterHunting | varies | S | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 360 gp | REVIEW: conditional/narrow generic save advantage | no |
| 47 | Circlet of the Huntsman's Third Eye | 24GriffonsSaddlebag1 | very rare |  | `[]` | `['constitution']` | `['constitution']` | `[]` | 400 gp | 270 gp | CLEAN HIT | no |
| 48 | Mask of Dendallen | 24GriffonsSaddlebag1 | very rare |  | `[]` | `['constitution']` | `['constitution']` | `[]` | 400 gp | 270 gp | CLEAN HIT | no |
| 49 | Shaedenstaff | 24GriffonsSaddlebag1 | very rare | M\|XPHB | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 320 gp | REVIEW: conditional/narrow generic save advantage | no |
| 50 | Tempest Griffon Feather Cape | 24GriffonsSaddlebag1 | very rare |  | `[]` | `['dexterity']` | `['dexterity']` | `[]` | 400 gp | 360 gp | CLEAN HIT | no |
| 51 | Timepiercer | 24GriffonsSaddlebag1 | very rare | M\|XPHB | `[]` | `['constitution']` | `['constitution']` | `[]` | 400 gp | 13,725 gp | CLEAN HIT | no |
| 52 | Whistle of the Vagrant (Very Rare) | CrookedMoon24 | very rare |  | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 360 gp | CLEAN HIT | no |
| 53 | Camilla's Quicksilver Mirror | GriffonsSaddlebag2 | very rare |  | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 360 gp | CLEAN HIT | no |
| 54 | Fool's Lamp | GriffonsSaddlebag2 | very rare |  | `['dexterity']` | `[]` | `[]` | `['dexterity']` | -400 gp | -400 gp | FIXED: old disadvantage false positive removed | no |
| 55 | Masks of the Sacred Beasts (Mule) | GriffonsSaddlebag2 | very rare |  | `['strength']` | `['strength', 'dexterity']` | `['dexterity']` | `[]` | 400 gp | 360 gp | CLEAN HIT | no |
| 56 | Lindwyrm Venom | GrimHollowLairsEtharis | very rare | P | `['strength']` | `[]` | `[]` | `['strength']` | -400 gp | -200 gp | FIXED: old disadvantage false positive removed | no |
| 57 | Overgrown Barkshield (very rare) | HelianasGuidetoMonsterHunting | very rare | S | `[]` | `['saving throws']` | `['saving throws']` | `[]` | 400 gp | 360 gp | REVIEW: conditional/narrow generic save advantage | no |
| 58 | Draught of Feather Shine | HumblewoodTales | very rare | P | `[]` | `['charisma']` | `['charisma']` | `[]` | 400 gp | 200 gp | CLEAN HIT | no |
| 59 | Talon Tincture | HumblewoodTales | very rare | P | `[]` | `['dexterity']` | `['dexterity']` | `[]` | 400 gp | 200 gp | CLEAN HIT | no |
| 60 | Vampire Blood Potion | MonstersOfDrakkenheim | very rare | P\|XPHB | `[]` | `['strength', 'dexterity', 'charisma']` | `['strength', 'dexterity', 'charisma']` | `[]` | 1,200 gp | 600 gp | CLEAN HIT | exact |

## Review recommendation

- The save_advantage validation gate is satisfied under the accepted policy decisions above.
- Do not run full pricing in this task, but full pricing may proceed in a separate controlled curation/migration step.
- If a future party-benefit criterion is added, revisit the excluded aura/ally rows (for example Scaled Ornament variants) outside `save_advantage` pricing.
