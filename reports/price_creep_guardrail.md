# Price Creep Guardrail

Baseline CSV: `output/pricing_guide.csv`
Candidate CSV: `output/pricing_guide_candidate.csv`

## Input row matching

- Common rows: 4748
- New candidate rows: 1
- Missing candidate rows: 1

## Aggregate final-price drift

- Median % drift: 0.00%
- Mean % drift: 0.05%
- Median gp drift: 0 gp
- Mean gp drift: 33 gp
- Rows >5% drift: 222
- Rows >10% drift: 85
- Rows >25% drift: 5

## Reference anchored vs formula/ML-only

| Split | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| reference-anchored | 3285 | 0.00% | -0.03% | 0 gp | 11 gp |
| formula/ML-only | 1463 | 0.00% | 0.21% | 0 gp | 82 gp |

## Drift by rarity

| Rarity | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Rare | 1411 | 0.00% | -0.04% | 0 gp | -4 gp |
| Uncommon | 946 | 0.00% | 0.16% | 0 gp | 2 gp |
| Very Rare | 853 | 0.00% | -0.21% | 0 gp | -42 gp |
| Legendary | 639 | 0.00% | 0.69% | 0 gp | 306 gp |
| Mundane | 461 | 0.00% | -0.43% | 0 gp | -0 gp |
| Common | 350 | 0.00% | 0.25% | 0 gp | 1 gp |
| Artifact | 71 | 0.00% | 0.00% | 0 gp | 0 gp |
| Unknown Magic | 9 | 0.92% | -2.12% | 3 gp | -150 gp |
| Varies | 8 | 0.00% | 0.00% | 0 gp | 0 gp |

## Drift by type

| Type | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Melee Weapon | 1863 | 0.00% | 0.02% | 0 gp | -27 gp |
| Wondrous Item | 770 | 0.04% | 0.53% | 0 gp | 274 gp |
| Ranged Weapon | 536 | 0.00% | 0.05% | 0 gp | 1 gp |
| Medium Armor | 279 | 0.00% | 0.12% | 0 gp | 93 gp |
| Heavy Armor | 217 | 0.00% | 0.02% | 0 gp | 1 gp |
| Adventuring Gear | 196 | 0.00% | -0.51% | 0 gp | 0 gp |
| Light Armor | 142 | 0.00% | 0.04% | 0 gp | 16 gp |
| Spellcasting Focus | 135 | 0.00% | 0.16% | 0 gp | 46 gp |
| Artisan's Tools | 71 | 0.00% | 0.09% | 0 gp | 13 gp |
| Ring | 69 | 0.01% | 1.04% | 1 gp | -52 gp |
| Potion | 66 | -0.80% | -1.39% | -14 gp | -34 gp |
| Ammunition | 64 | 0.00% | -1.37% | 0 gp | 4 gp |
| Wand | 48 | 0.41% | 0.14% | 7 gp | -16 gp |
| Musical Instrument | 45 | 0.00% | -1.19% | 0 gp | -815 gp |
| Scroll | 35 | -0.80% | -2.86% | -10 gp | -893 gp |
| Other | 34 | 0.00% | -1.05% | 0 gp | -39 gp |
| Shield | 31 | 0.10% | 1.03% | 1 gp | 640 gp |
| Trade Goods | 24 | 0.00% | 0.00% | 0 gp | 0 gp |
| Tack & Harness | 22 | 0.00% | 0.00% | 0 gp | 0 gp |
| Rod | 21 | 0.87% | 1.89% | 51 gp | 625 gp |

## Drift by source

| Source | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Dungeon Master's Guide (2024) | 1981 | 0.00% | -0.09% | 0 gp | -15 gp |
| Monsters of Drakkenheim | 280 | 0.00% | -0.01% | 0 gp | 10 gp |
| Exploring Eberron (2024) | 270 | 0.00% | 0.28% | 0 gp | 68 gp |
| The Book of Many Things | 219 | 0.00% | 1.00% | 0 gp | 617 gp |
| Player's Handbook (2024) | 217 | 0.00% | -0.46% | 0 gp | -0 gp |
| Fizban's Treasury of Dragons | 206 | 0.00% | 0.11% | 0 gp | 50 gp |
| Explorer's Guide to Wildemount | 190 | 0.00% | 0.65% | 0 gp | 196 gp |
| Monster Manual | 170 | 0.29% | 0.33% | 10 gp | -10 gp |
| Frontiers of Eberron: Quickstone | 111 | 0.00% | 0.37% | 0 gp | 12 gp |
| Eberron: Rising from the Last War | 107 | 0.00% | 0.26% | 0 gp | 12 gp |
| Tasha's Cauldron of Everything | 80 | -0.23% | -0.20% | -5 gp | -14 gp |
| Acquisitions Incorporated | 75 | 0.27% | 0.16% | 2 gp | -7 gp |
| Eberron: Forge of the Artificer | 72 | 0.00% | 0.17% | 0 gp | 3 gp |
| Critical Role: Call of the Netherdeep | 66 | 0.00% | 0.32% | 0 gp | 26 gp |
| Baldur's Gate: Descent Into Avernus | 56 | 0.00% | 0.10% | 0 gp | 54 gp |
| Player's Handbook | 47 | 0.00% | -2.13% | 0 gp | -0 gp |
| Bigby Presents: Glory of the Giants | 44 | 0.00% | -0.53% | 0 gp | -467 gp |
| Dungeons of Drakkenheim | 43 | 0.00% | -0.75% | 0 gp | -953 gp |
| Guildmasters' Guide to Ravnica | 42 | 0.00% | 2.57% | 0 gp | 196 gp |
| Tomb of Annihilation | 27 | 0.00% | 0.09% | 0 gp | -25 gp |

## Known-good anchors

Known-good status: **REVIEW** (PASS ≤1% drift; REVIEW >1%; FAIL >5%).
Configured anchors include Holy Avenger, Defender, Vorpal Sword, +1/+2/+3 Weapon/Armor, Dragon Slayer, Giant Slayer, and Vicious Weapon families when present.

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Vorpal Glaive | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 54,605 gp | 53,758 gp | -847 gp | -1.55% | reference-anchored |
| Vorpal Greatsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 54,605 gp | 53,758 gp | -847 gp | -1.55% | reference-anchored |
| Vorpal Longsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 54,605 gp | 53,758 gp | -847 gp | -1.55% | reference-anchored |
| Vorpal Scimitar | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 54,605 gp | 53,758 gp | -847 gp | -1.55% | reference-anchored |
| +3 Moon Sickle | Tasha's Cauldron of Everything | Very Rare | Melee Weapon | 32,952 gp | 33,504 gp | 552 gp | 1.68% | reference-anchored |
| +3 Leather Armor | Dungeon Master's Guide (2024) | Legendary | Light Armor | 29,832 gp | 29,503 gp | -328 gp | -1.10% | reference-anchored |
| +3 Padded Armor | Dungeon Master's Guide (2024) | Legendary | Light Armor | 29,832 gp | 29,503 gp | -328 gp | -1.10% | reference-anchored |
| +3 Studded Leather Armor | Dungeon Master's Guide (2024) | Legendary | Light Armor | 29,832 gp | 29,503 gp | -328 gp | -1.10% | reference-anchored |
| +3 Breastplate | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,780 gp | 29,604 gp | -176 gp | -0.59% | reference-anchored |
| +3 Chain Shirt | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,780 gp | 29,604 gp | -176 gp | -0.59% | reference-anchored |
| +3 Half Plate Armor | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,780 gp | 29,604 gp | -176 gp | -0.59% | reference-anchored |
| +3 Hide Armor | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,780 gp | 29,604 gp | -176 gp | -0.59% | reference-anchored |
| +3 Scale Mail | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,780 gp | 29,604 gp | -176 gp | -0.59% | reference-anchored |
| +3 Plate Armor | Dungeon Master's Guide (2024) | Legendary | Heavy Armor | 29,781 gp | 29,610 gp | -171 gp | -0.57% | reference-anchored |
| +2 Chain Mail | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,454 gp | 8,614 gp | 160 gp | 1.89% | reference-anchored |
| +2 Plate Armor | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,454 gp | 8,614 gp | 160 gp | 1.89% | reference-anchored |
| +2 Ring Mail | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,454 gp | 8,614 gp | 160 gp | 1.89% | reference-anchored |
| +2 Splint Armor | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,454 gp | 8,614 gp | 160 gp | 1.89% | reference-anchored |
| +1 Moon Sickle | Tasha's Cauldron of Everything | Uncommon | Melee Weapon | 3,925 gp | 3,876 gp | -49 gp | -1.25% | reference-anchored |
| +3 Chain Mail | Dungeon Master's Guide (2024) | Legendary | Heavy Armor | 29,656 gp | 29,610 gp | -47 gp | -0.16% | reference-anchored |

## Artifact/legendary movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Harp of Gilded Plenty | Bigby Presents: Glory of the Giants | Legendary | Musical Instrument | 89,148 gp | 53,626 gp | -35,522 gp | -39.85% | formula/ML-only |
| Deck of Many More Things | The Book of Many Things | Legendary | Wondrous Item | 163,975 gp | 191,370 gp | 27,394 gp | 16.71% | reference-anchored |
| Staff of Contaminated Power | Dungeons of Drakkenheim | Legendary | Melee Weapon | 90,325 gp | 69,987 gp | -20,338 gp | -22.52% | formula/ML-only |
| Breastplate of Kamvuul Norek | Exploring Eberron (2024) | Legendary | Medium Armor | 103,206 gp | 121,209 gp | 18,003 gp | 17.44% | formula/ML-only |
| Nepenthe | Van Richten's Guide to Ravenloft | Legendary | Melee Weapon | 204,366 gp | 188,361 gp | -16,005 gp | -7.83% | formula/ML-only |
| Verminshroud (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 80,207 gp | 95,282 gp | 15,075 gp | 18.80% | formula/ML-only |
| Euryale's Aegis | The Book of Many Things | Legendary | Shield | 68,121 gp | 82,297 gp | 14,176 gp | 20.81% | formula/ML-only |
| Inscrutable Staff | Dungeons of Drakkenheim | Legendary | Melee Weapon | 105,750 gp | 92,161 gp | -13,589 gp | -12.85% | formula/ML-only |
| Infiltrator's Key (Awakened) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 82,499 gp | 70,015 gp | -12,484 gp | -15.13% | formula/ML-only |
| Azuredge | Waterdeep: Dragon Heist | Legendary | Melee Weapon | 123,008 gp | 110,806 gp | -12,202 gp | -9.92% | formula/ML-only |
| Key Card | The Book of Many Things | Legendary | Wondrous Item | 59,474 gp | 71,312 gp | 11,838 gp | 19.90% | formula/ML-only |
| Grimoire Infinitus (Dormant) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 31,614 gp | 43,145 gp | 11,531 gp | 36.48% | formula/ML-only |
| Grimoire Infinitus (Awakened) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 46,398 gp | 57,929 gp | 11,531 gp | 24.85% | formula/ML-only |
| Grimoire Infinitus (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 46,398 gp | 57,929 gp | 11,531 gp | 24.85% | formula/ML-only |
| Tinderstrike | Princes of the Apocalypse | Legendary | Melee Weapon | 123,540 gp | 112,619 gp | -10,920 gp | -8.84% | formula/ML-only |
| Stonebreaker's Breastplate | Bigby Presents: Glory of the Giants | Legendary | Medium Armor | 58,762 gp | 68,579 gp | 9,817 gp | 16.71% | formula/ML-only |
| Sunsword | Curse of Strahd | Legendary | Melee Weapon | 63,558 gp | 73,268 gp | 9,710 gp | 15.28% | formula/ML-only |
| Infiltrator's Key (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 93,812 gp | 84,117 gp | -9,695 gp | -10.33% | formula/ML-only |
| Rakdos Riteknife | Guildmasters' Guide to Ravnica | Legendary | Melee Weapon | 50,725 gp | 60,413 gp | 9,688 gp | 19.10% | formula/ML-only |
| Witchlight Vane | The Wild Beyond the Witchlight | Legendary | Wondrous Item | 61,366 gp | 70,462 gp | 9,096 gp | 14.82% | formula/ML-only |

## Largest movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Harp of Gilded Plenty | Bigby Presents: Glory of the Giants | Legendary | Musical Instrument | 89,148 gp | 53,626 gp | -35,522 gp | -39.85% | formula/ML-only |
| Deck of Many More Things | The Book of Many Things | Legendary | Wondrous Item | 163,975 gp | 191,370 gp | 27,394 gp | 16.71% | reference-anchored |
| Staff of Contaminated Power | Dungeons of Drakkenheim | Legendary | Melee Weapon | 90,325 gp | 69,987 gp | -20,338 gp | -22.52% | formula/ML-only |
| Breastplate of Kamvuul Norek | Exploring Eberron (2024) | Legendary | Medium Armor | 103,206 gp | 121,209 gp | 18,003 gp | 17.44% | formula/ML-only |
| Nepenthe | Van Richten's Guide to Ravenloft | Legendary | Melee Weapon | 204,366 gp | 188,361 gp | -16,005 gp | -7.83% | formula/ML-only |
| Verminshroud (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 80,207 gp | 95,282 gp | 15,075 gp | 18.80% | formula/ML-only |
| Euryale's Aegis | The Book of Many Things | Legendary | Shield | 68,121 gp | 82,297 gp | 14,176 gp | 20.81% | formula/ML-only |
| Inscrutable Staff | Dungeons of Drakkenheim | Legendary | Melee Weapon | 105,750 gp | 92,161 gp | -13,589 gp | -12.85% | formula/ML-only |
| Infiltrator's Key (Awakened) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 82,499 gp | 70,015 gp | -12,484 gp | -15.13% | formula/ML-only |
| Azuredge | Waterdeep: Dragon Heist | Legendary | Melee Weapon | 123,008 gp | 110,806 gp | -12,202 gp | -9.92% | formula/ML-only |
| Key Card | The Book of Many Things | Legendary | Wondrous Item | 59,474 gp | 71,312 gp | 11,838 gp | 19.90% | formula/ML-only |
| Grimoire Infinitus (Dormant) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 31,614 gp | 43,145 gp | 11,531 gp | 36.48% | formula/ML-only |
| Grimoire Infinitus (Awakened) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 46,398 gp | 57,929 gp | 11,531 gp | 24.85% | formula/ML-only |
| Grimoire Infinitus (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 46,398 gp | 57,929 gp | 11,531 gp | 24.85% | formula/ML-only |
| Tinderstrike | Princes of the Apocalypse | Legendary | Melee Weapon | 123,540 gp | 112,619 gp | -10,920 gp | -8.84% | formula/ML-only |
| Stonebreaker's Breastplate | Bigby Presents: Glory of the Giants | Legendary | Medium Armor | 58,762 gp | 68,579 gp | 9,817 gp | 16.71% | formula/ML-only |
| Sunsword | Curse of Strahd | Legendary | Melee Weapon | 63,558 gp | 73,268 gp | 9,710 gp | 15.28% | formula/ML-only |
| Infiltrator's Key (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 93,812 gp | 84,117 gp | -9,695 gp | -10.33% | formula/ML-only |
| Rakdos Riteknife | Guildmasters' Guide to Ravnica | Legendary | Melee Weapon | 50,725 gp | 60,413 gp | 9,688 gp | 19.10% | formula/ML-only |
| Witchlight Vane | The Wild Beyond the Witchlight | Legendary | Wondrous Item | 61,366 gp | 70,462 gp | 9,096 gp | 14.82% | formula/ML-only |
| Witchlight Watch | The Wild Beyond the Witchlight | Legendary | Wondrous Item | 57,628 gp | 66,693 gp | 9,065 gp | 15.73% | formula/ML-only |
| Telescopic Transporter | The Book of Many Things | Legendary | Wondrous Item | 34,081 gp | 42,972 gp | 8,890 gp | 26.09% | formula/ML-only |
| Jester's Mask | The Book of Many Things | Legendary | Wondrous Item | 56,830 gp | 65,407 gp | 8,578 gp | 15.09% | formula/ML-only |
| Shard Solitaire (Jacinth) | Keys from the Golden Vault | Legendary | Wondrous Item | 85,534 gp | 94,004 gp | 8,471 gp | 9.90% | formula/ML-only |
| Shard Solitaire (Ruby) | Keys from the Golden Vault | Legendary | Wondrous Item | 85,534 gp | 94,004 gp | 8,471 gp | 9.90% | formula/ML-only |

## Largest percent movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Ball Bearing | Player's Handbook | Mundane | Adventuring Gear | 0 gp | 0 gp | -0 gp | -100.00% | reference-anchored |
| Sling Bullet | Player's Handbook (2024) | Mundane | Ammunition | 0 gp | 0 gp | -0 gp | -100.00% | reference-anchored |
| Harp of Gilded Plenty | Bigby Presents: Glory of the Giants | Legendary | Musical Instrument | 89,148 gp | 53,626 gp | -35,522 gp | -39.85% | formula/ML-only |
| Grimoire Infinitus (Dormant) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 31,614 gp | 43,145 gp | 11,531 gp | 36.48% | formula/ML-only |
| Telescopic Transporter | The Book of Many Things | Legendary | Wondrous Item | 34,081 gp | 42,972 gp | 8,890 gp | 26.09% | formula/ML-only |
| Talon Gloves | Monsters of Drakkenheim | Rare | Wondrous Item | 8,796 gp | 10,992 gp | 2,196 gp | 24.96% | formula/ML-only |
| Grimoire Infinitus (Awakened) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 46,398 gp | 57,929 gp | 11,531 gp | 24.85% | formula/ML-only |
| Grimoire Infinitus (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 46,398 gp | 57,929 gp | 11,531 gp | 24.85% | formula/ML-only |
| Flame Tongue Shortsword of Greed | Tales from the Yawning Portal | Unknown Magic | Melee Weapon | 5,544 gp | 4,176 gp | -1,368 gp | -24.68% | formula/ML-only |
| Rod of Hellish Flames | The Book of Many Things | Very Rare | Rod | 23,376 gp | 28,767 gp | 5,390 gp | 23.06% | formula/ML-only |
| Staff of Contaminated Power | Dungeons of Drakkenheim | Legendary | Melee Weapon | 90,325 gp | 69,987 gp | -20,338 gp | -22.52% | formula/ML-only |
| Wyllow's Staff of Flowers | Waterdeep: Dungeon of the Mad Mage | Common | Wondrous Item | 177 gp | 139 gp | -38 gp | -21.31% | formula/ML-only |
| Euryale's Aegis | The Book of Many Things | Legendary | Shield | 68,121 gp | 82,297 gp | 14,176 gp | 20.81% | formula/ML-only |
| Potion of Healing | Dungeon Master's Guide (2024) | Common | Potion | 65 gp | 52 gp | -13 gp | -20.60% | reference-anchored |
| Sandstorm Staff | Frontiers of Eberron: Quickstone | Uncommon | Melee Weapon | 1,815 gp | 2,178 gp | 364 gp | 20.04% | formula/ML-only |
| Key Card | The Book of Many Things | Legendary | Wondrous Item | 59,474 gp | 71,312 gp | 11,838 gp | 19.90% | formula/ML-only |
| Rakdos Riteknife | Guildmasters' Guide to Ravnica | Legendary | Melee Weapon | 50,725 gp | 60,413 gp | 9,688 gp | 19.10% | formula/ML-only |
| Verminshroud (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 80,207 gp | 95,282 gp | 15,075 gp | 18.80% | formula/ML-only |
| Mechanical Wonder (Domestic) | Forgotten Realms: Adventures in Faerûn | Uncommon | Wondrous Item | 719 gp | 586 gp | -133 gp | -18.51% | formula/ML-only |
| Mind Sharpener | Eberron: Forge of the Artificer | Uncommon | Ring | 1,065 gp | 1,251 gp | 187 gp | 17.55% | formula/ML-only |
| Breastplate of Kamvuul Norek | Exploring Eberron (2024) | Legendary | Medium Armor | 103,206 gp | 121,209 gp | 18,003 gp | 17.44% | formula/ML-only |
| Infiltrator's Key (Dormant) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 34,093 gp | 39,930 gp | 5,837 gp | 17.12% | formula/ML-only |
| Constantori's Portrait | Keys from the Golden Vault | Very Rare | Wondrous Item | 28,029 gp | 23,329 gp | -4,700 gp | -16.77% | formula/ML-only |
| Stonebreaker's Breastplate | Bigby Presents: Glory of the Giants | Legendary | Medium Armor | 58,762 gp | 68,579 gp | 9,817 gp | 16.71% | formula/ML-only |
| Deck of Many More Things | The Book of Many Things | Legendary | Wondrous Item | 163,975 gp | 191,370 gp | 27,394 gp | 16.71% | reference-anchored |

## Anchor-tier transitions / ML R² / double-count audit

- Anchor-tier transition and ML R² checks require pipeline metadata not present in final CSV snapshots; add those columns to future candidate snapshots if needed.
- Use the known-good and reference-anchored sections above as the first-pass double-count audit for extraction-driven price creep.
- Formula exposure reports (for example, extra_damage impact) are not final-price deltas.
