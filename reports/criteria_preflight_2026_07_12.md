# 2026-07-12 Criteria Preflight (Phase 1)

Raw file: `2026_07_12_item_list.json` (left untracked; no canonical replacement or pricing pipeline run).
Total items analyzed: 12243

## Count summary

| Metric | Count | Top sources |
|---|---:|---|
| `reload` | 415 | XDMG (240), HelianasGuidetoMonsterHunting (80), 24GriffonsSaddlebag1 (25), EFA (15), FoEQuickstone (15) |
| raw `ac` | 894 | XDMG (407), BMT (78), GriffonsSaddlebag2 (60), HelianasGuidetoMonsterHunting (44), MM (39) |
| extracted `armor_ac` | 809 | XDMG (397), BMT (75), GriffonsSaddlebag2 (45), HelianasGuidetoMonsterHunting (39), MM (39) |
| raw `strength` | 214 | XDMG (101), BMT (19), HelianasGuidetoMonsterHunting (12), GriffonsSaddlebag2 (10), AI (9) |
| extracted `armor_strength_req` | 204 | XDMG (101), BMT (19), HelianasGuidetoMonsterHunting (12), GriffonsSaddlebag2 (10), MM (9) |
| raw vehicle stats (any) | 31 | CallfromtheDeep (17), XPHB (7), FRAiF (4), EGW (1), TalDoreiCampaignSettingReborn (1) |
| any `vehicle_*` | 31 | CallfromtheDeep (17), XPHB (7), FRAiF (4), EGW (1), TalDoreiCampaignSettingReborn (1) |
| raw prose `advantage ... checks` | 236 | GriffonsSaddlebag2 (35), EGW (19), XDMG (18), GrimHollowCG24 (14), ExploringEberron24 (13) |
| raw prose `disadvantage ... checks/saves` | 130 | GrimHollowCG24 (21), GriffonsSaddlebag2 (20), 24GriffonsSaddlebag1 (13), HelianasGuidetoMonsterHunting (12), TalDoreiCampaignSettingReborn (10) |
| extracted `check_advantage` | 181 | GriffonsSaddlebag2 (30), EGW (17), GrimHollowCG24 (14), XDMG (14), BookOfEbonTides (12) |
| extracted `check_disadvantage` | 30 | GrimHollowCG24 (10), 24GriffonsSaddlebag1 (7), GriffonsSaddlebag2 (5), HumblewoodTales (3), BookOfEbonTides (1) |
| extracted `save_disadvantage` | 22 | GrimHollowCG24 (13), 24GriffonsSaddlebag1 (3), GriffonsSaddlebag2 (3), BMT (1), BookOfEbonTides (1) |

## Structured field examples

### Reload
- Blunderbuss (HelianasGuidetoMonsterHunting): `reload=1`
- Hand Tommybow (2) (HelianasGuidetoMonsterHunting): `reload=2`
- Hand Tommybow (3) (HelianasGuidetoMonsterHunting): `reload=3`
- Hand Tommybow (4) (HelianasGuidetoMonsterHunting): `reload=4`
- Hand Tommybow (5) (HelianasGuidetoMonsterHunting): `reload=5`

### Raw AC
- Bark Armor (ObojimaTallGrass): `ac=11`
- Breastplate (XPHB): `ac=14`
- Breastplate Barding (PHB): `ac=14`
- Chain Mail (XPHB): `ac=16`
- Chain Mail Barding (PHB): `ac=16`

### Extracted armor_ac
- Bark Armor (ObojimaTallGrass): `armor_ac=11`
- Breastplate (XPHB): `armor_ac=14`
- Breastplate Barding (PHB): `armor_ac=14`
- Chain Mail (XPHB): `armor_ac=16`
- Chain Mail Barding (PHB): `armor_ac=16`

### Raw strength
- Chain Mail (XPHB): `strength=13`
- Chain Mail Barding (PHB): `strength=13`
- Divers Armor (ObojimaTallGrass): `strength=16`
- Hunter's Chain Mail (GrimHollowPG24): `strength=13`
- Hunter's Plate Armor (GrimHollowPG24): `strength=15`

### Extracted armor_strength_req
- Chain Mail (XPHB): `armor_strength_req=13`
- Chain Mail Barding (PHB): `armor_strength_req=13`
- Divers Armor (ObojimaTallGrass): `armor_strength_req=16`
- Hunter's Chain Mail (GrimHollowPG24): `armor_strength_req=13`
- Hunter's Plate Armor (GrimHollowPG24): `armor_strength_req=15`

### Vehicle stats
- Airship (XPHB): `vehicle_speed=8, vehicle_ac=13, vehicle_hp=300, vehicle_crew=10, vehicle_cargo_capacity=1`
- Angel's Bane (CallfromtheDeep): `vehicle_speed=2, vehicle_ac=15, vehicle_hp=200, vehicle_crew=15, vehicle_cargo_capacity=100`
- Bireme (CallfromtheDeep): `vehicle_speed=2, vehicle_ac=15, vehicle_hp=200, vehicle_crew=20, vehicle_cargo_capacity=10`
- Canoe (ToA): `vehicle_speed=2, vehicle_ac=11, vehicle_hp=50, vehicle_crew=1`
- Caravel (CallfromtheDeep): `vehicle_speed=2, vehicle_ac=15, vehicle_hp=200, vehicle_crew=15, vehicle_cargo_capacity=100`

## Advantage/disadvantage prose examples

Examples show normalized extractor targets only, not raw prose snippets.

### check_advantage
- Bark Armor (ObojimaTallGrass): `dexterity (stealth)`
- Costume (XPHB): `ability checks`
- Crowbar (XPHB): `strength`
- Cultist's Robe (HotB): `ability checks`
- Demon Signet Ring (WhereEvilLives): `charisma (intimidation)`

### check_disadvantage
- Aether Blood (GrimHollowCG24): `strength, constitution`
- Alluring Dye (HumblewoodTales): `charisma`
- Barricade Shield (24GriffonsSaddlebag1): `dexterity`
- Boots of Dendallen (24GriffonsSaddlebag1): `dexterity (acrobatics)`
- Dream Mantle (24GriffonsSaddlebag1): `wisdom (perception)`

### save_disadvantage
- Aether Blood (GrimHollowCG24): `strength, constitution`
- Amulet of the Lycanthrope (GriffonsSaddlebag2): `saving throws`
- Barricade Shield (24GriffonsSaddlebag1): `dexterity`
- Boots of Dendallen (24GriffonsSaddlebag1): `dexterity`
- Deck of Wonder (BMT): `intelligence`

## Pipeline safety

- Did not edit `trimmed_5etools_list.*`.
- Did not run full pricing or write `data/processed`/published outputs.
- Report reflects current `src.criteria_extractor` behavior only.
