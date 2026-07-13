# 2026-07-12 Curation Preflight

Raw file: `2026_07_12_item_list.json` (raw 2026 files remain untracked; no canonical replacement or pricing pipeline run).
Canonical reference: `trimmed_5etools_list.json`.
Raw 2026 items: 12243
Current canonical items: 4837
Curated items after hard exclusions: 12241
Hard exclusions applied: 2
New exact `(name, source)` rows after curation: 7437
Canonical exact `(name, source)` rows absent from curated 2026 list: 33

## Source count delta summary

Curated 2026 sources: 88; canonical sources: 66; new-only sources: 26.
Spelljammer scope check: AAG present=False; BAM present=False (expected absent unless explicitly approved).

### Top source expansions
| Source | 2026 curated | Current canonical | Delta |
|---|---:|---:|---:|
| XDMG | 3089 | 2005 | +1084 |
| 24GriffonsSaddlebag1 | 897 | 0 | +897 |
| GriffonsSaddlebag2 | 647 | 0 | +647 |
| ObojimaTallGrass | 616 | 0 | +616 |
| HelianasGuidetoMonsterHunting | 547 | 0 | +547 |
| CallfromtheDeep | 483 | 0 | +483 |
| IllriggerRevised | 437 | 0 | +437 |
| GrimHollowCG24 | 322 | 0 | +322 |
| FTD | 473 | 209 | +264 |
| MonstersOfDrakkenheim | 527 | 281 | +246 |
| MM | 368 | 170 | +198 |
| WhereEvilLives | 151 | 0 | +151 |
| ExploringEberron24 | 417 | 276 | +141 |
| TalDoreiCampaignSettingReborn | 133 | 0 | +133 |
| EGW | 337 | 205 | +132 |

### New-only sources (first 25)
- 24GriffonsSaddlebag1 (897)
- BookOfEbonTides (106)
- CallfromtheDeep (483)
- CrookedMoon24 (104)
- CthulhuTorchlight (7)
- FleeMortals (19)
- GriffonsSaddlebag2 (647)
- GrimHollowCG24 (322)
- GrimHollowLairsEtharis (118)
- GrimHollowPG24 (119)
- GrimHollowPlayerPack (12)
- HelianasGuidetoMonsterHunting (547)
- HumblewoodCampaignSetting (13)
- HumblewoodTales (62)
- IllriggerRevised (437)
- ObojimaTallGrass (616)
- OneShotWondersHolidayPack (14)
- Pugilist2024 (41)
- RHW (2)
- TalDoreiCampaignSettingReborn (133)
- TalesFromTheShadows (18)
- ToB1-2023 (3)
- ValdaGunslinger (8)
- ValdaPlayerPack (5)
- WSC (2)

## Hard exclusions

Exact QftIS grenade exclusions applied by `src.list_curation.curate_items()`:
- QftIS — Concussion Grenade
- QftIS — Sleep Grenade

## Potential scope review items

### Fantasy explosives/alchemical ordnance (keep pending final human confirmation)
Count: 40
- Blasting Powder (EGW)
- Bomb (XDMG)
- Dynamite (TalDoreiCampaignSettingReborn)
- Explosive Seed (EGW)
- Fire Bomb (GrimHollowPG24)
- Gluebomb (TalDoreiCampaignSettingReborn)
- Smoke Bomb (GrimHollowPG24)
- Smoke Grenade (XDMG)

### Airships/skyships/fantasy vehicles (currently in scope)
Count: 3
- Airship (XPHB)
- Skyship (EGW)
- Skyship (TalDoreiCampaignSettingReborn)

### Source-specific firearms/Renaissance-tech review
Count: 761
- Blackpowder Pistol (GrimHollowPG24)
- Blackpowder Rifle (GrimHollowPG24)
- Blunderbuss (GrimHollowPG24)
- Blunderbuss (HelianasGuidetoMonsterHunting)
- Blunderbuss (ValdaGunslinger)
- Blunderbuss, Hand (GrimHollowPG24)
- Dragon Pistol (GrimHollowPG24)
- Dragon Rifle (GrimHollowPG24)

## Duplicate/name collision summary

Same-name groups after hard exclusions: 168

### Collision classification counts
| Classification | Groups |
|---|---:|
| review — same-name cross-source collision | 131 |
| likely collapsible — ammunition variants | 14 |
| review/keep-separate — source-specific firearms | 12 |
| likely collapsible — vehicle/source variants | 8 |
| keep-separate — sensitive gem/ingredient/source collision | 2 |
| keep-separate — Drakkenheim/source-specific collision | 1 |

### Collision examples
- Trinket: 4 rows; AI, CoS, EET, XPHB; review — same-name cross-source collision
- Blunderbuss: 3 rows; GrimHollowPG24, HelianasGuidetoMonsterHunting, ValdaGunslinger; review/keep-separate — source-specific firearms
- Musket: 3 rows; HelianasGuidetoMonsterHunting, ValdaGunslinger, XPHB; review/keep-separate — source-specific firearms
- Pistol: 3 rows; HelianasGuidetoMonsterHunting, ValdaGunslinger, XPHB; review/keep-separate — source-specific firearms
- Zeal: 3 rows; GrimHollowCG24, GrimHollowPlayerPack, TalDoreiCampaignSettingReborn; keep-separate — sensitive gem/ingredient/source collision
- Adamantine Arrow: 2 rows; XDMG, XGE; likely collapsible — ammunition variants
- Adamantine Bellows Cannister: 2 rows; XDMG, XGE; likely collapsible — ammunition variants
- Adamantine Bolt: 2 rows; XDMG, XGE; likely collapsible — ammunition variants

### Sensitive collision checks
- Crystal rows present: 2 — Crystal (XPHB), Crystal (MonstersOfDrakkenheim); classification: keep-separate.
- Zeal rows present: 3 — Zeal (TalDoreiCampaignSettingReborn), Zeal (GrimHollowCG24), Zeal (GrimHollowPlayerPack); classification: keep-separate.
- Obojima ingredient vs DMG/PHB gem-style name collisions should remain source-specific unless manually collapsed.
- Source-specific firearms should remain source-specific pending source/tech review.

## Variant family and UI grouping candidates

Specific variants with `genericVariant`: 8001
Nested generic/template phrase parents: 13

### Top generic variant families
| Generic parent / family | Specific variants |
|---|---:|
| Lycan Weapon | 218 |
| Lunar Weapon | 112 |
| Weapon of the Sun And Moon | 112 |
| +1 Adamantine Weapon | 109 |
| +1 Black Ice Weapon | 109 |
| +1 True Name | 109 |
| +1 Weapon | 109 |
| +2 True Name | 109 |
| +2 Weapon | 109 |
| +3 Adamantine Weapon | 109 |
| +3 True Name | 109 |
| +3 Weapon | 109 |
| Ascendant Dragon's Wrath Weapon | 109 |
| Black Ice Weapon | 109 |
| Corpse Slayer | 109 |

### UI grouping candidates
- Large generic variant families above should be grouped/collapsed in UI review rather than manually deleted.
- Same-name ammunition and vehicle/source variants are likely collapsible display groups after source review.
- Keep source-specific named collisions such as Crystal/Zeal separate until a human approves any merge.

## Readiness matrix

| Bucket | Status | Examples / next action |
|---|---|---|
| Safe to migrate | Hard exclusions only | 12241 curated rows after excluding QftIS Concussion/Sleep Grenade; raw 2026 files remain untracked. |
| Needs user decision | Scope/curation | Fantasy explosives/alchemical ordnance; new-only source scope; source-specific firearm handling. |
| Needs extractor/pricing work | Criteria/pricing follow-up | Variant family/UI grouping, duplicate collision review, party-benefit/conditional-save follow-ups already tracked separately. |
| Deferred | Out of scope for this preflight | Full pricing run, canonical replacement, data/processed or published output generation. |

## Pipeline safety

- Did not edit `trimmed_5etools_list.*`.
- Did not run full pricing or generate `data/processed`/published outputs.
- Raw `2026_07_12_item_list.json/.md` remain untracked under Option A.
