# Price Creep Guardrail

Baseline CSV: `output/pricing_guide.csv`
Candidate CSV: `output/pricing_guide_candidate.csv`

## Input row matching

- Common rows: 4748
- New candidate rows: 1
- Missing candidate rows: 1

## Aggregate final-price drift

- Median % drift: 0.00%
- Mean % drift: 7.04%
- Median gp drift: 0 gp
- Mean gp drift: -7 gp
- Rows >5% drift: 473
- Rows >10% drift: 318
- Rows >25% drift: 174

## Reference anchored vs formula/ML-only

| Split | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| reference-anchored | 3285 | 0.00% | 9.83% | 0 gp | -59 gp |
| formula/ML-only | 1463 | 0.00% | 0.79% | 0 gp | 111 gp |

## Drift by rarity

| Rarity | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Rare | 1411 | 0.00% | 20.17% | 0 gp | -116 gp |
| Uncommon | 946 | 0.00% | 5.14% | 0 gp | 34 gp |
| Very Rare | 853 | 0.00% | -0.02% | 0 gp | -6 gp |
| Legendary | 639 | 0.00% | 0.51% | 0 gp | 162 gp |
| Mundane | 461 | 0.00% | -0.43% | 0 gp | -0 gp |
| Common | 350 | 0.00% | 0.10% | 0 gp | 0 gp |
| Artifact | 71 | 0.00% | 0.00% | 0 gp | 0 gp |
| Unknown Magic | 9 | 0.33% | -2.57% | 1 gp | -149 gp |
| Varies | 8 | 0.00% | 0.00% | 0 gp | 0 gp |

## Drift by type

| Type | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Melee Weapon | 1863 | 0.00% | 13.78% | 0 gp | -148 gp |
| Wondrous Item | 770 | 0.02% | 0.82% | 0 gp | 209 gp |
| Ranged Weapon | 536 | 0.00% | 12.57% | 0 gp | 11 gp |
| Medium Armor | 279 | 0.00% | 0.39% | 0 gp | 252 gp |
| Heavy Armor | 217 | 0.00% | 0.11% | 0 gp | 13 gp |
| Adventuring Gear | 196 | 0.00% | -0.51% | 0 gp | 0 gp |
| Light Armor | 142 | 0.00% | 0.43% | 0 gp | 105 gp |
| Spellcasting Focus | 135 | 0.00% | 4.34% | 0 gp | 124 gp |
| Artisan's Tools | 71 | 0.00% | 0.04% | 0 gp | 4 gp |
| Ring | 69 | -0.05% | -0.15% | -3 gp | -5 gp |
| Potion | 66 | 0.23% | -0.22% | 2 gp | -20 gp |
| Ammunition | 64 | 0.00% | -1.61% | 0 gp | -3 gp |
| Wand | 48 | 0.60% | 0.04% | 1 gp | -50 gp |
| Musical Instrument | 45 | 0.00% | -1.43% | 0 gp | -926 gp |
| Scroll | 35 | -0.65% | -2.82% | -2 gp | -980 gp |
| Other | 34 | 0.00% | -1.20% | 0 gp | -47 gp |
| Shield | 31 | -0.07% | -1.30% | -1 gp | 757 gp |
| Trade Goods | 24 | 0.00% | 0.00% | 0 gp | 0 gp |
| Tack & Harness | 22 | 0.00% | 0.00% | 0 gp | 0 gp |
| Rod | 21 | 1.42% | 4.28% | 76 gp | 1,390 gp |

## Drift by source

| Source | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Dungeon Master's Guide (2024) | 1981 | 0.00% | -0.17% | 0 gp | -24 gp |
| Monsters of Drakkenheim | 280 | 0.00% | 0.47% | 0 gp | 54 gp |
| Exploring Eberron (2024) | 270 | 0.00% | -4.41% | 0 gp | -520 gp |
| The Book of Many Things | 219 | 0.00% | 2.81% | 0 gp | 477 gp |
| Player's Handbook (2024) | 217 | 0.00% | -0.46% | 0 gp | -0 gp |
| Fizban's Treasury of Dragons | 206 | 0.00% | 0.07% | 0 gp | -247 gp |
| Explorer's Guide to Wildemount | 190 | 0.00% | -7.62% | 0 gp | -669 gp |
| Monster Manual | 170 | 0.64% | 3.09% | 22 gp | 2 gp |
| Frontiers of Eberron: Quickstone | 111 | 175.00% | 311.53% | 1,331 gp | 2,101 gp |
| Eberron: Rising from the Last War | 107 | 0.00% | 0.14% | 0 gp | 6 gp |
| Tasha's Cauldron of Everything | 80 | 0.01% | 0.28% | 0 gp | 26 gp |
| Acquisitions Incorporated | 75 | 0.96% | 2.39% | 6 gp | 19 gp |
| Eberron: Forge of the Artificer | 72 | 0.00% | -0.02% | 0 gp | 1 gp |
| Critical Role: Call of the Netherdeep | 66 | 0.00% | 0.12% | 0 gp | -2 gp |
| Baldur's Gate: Descent Into Avernus | 56 | 0.00% | 0.16% | 0 gp | 105 gp |
| Player's Handbook | 47 | 0.00% | -2.13% | 0 gp | -0 gp |
| Bigby Presents: Glory of the Giants | 44 | 0.00% | 6.07% | 0 gp | -113 gp |
| Dungeons of Drakkenheim | 43 | 0.00% | -1.40% | 0 gp | -1,028 gp |
| Guildmasters' Guide to Ravnica | 42 | 1.90% | 2.25% | 27 gp | -81 gp |
| Tomb of Annihilation | 27 | 0.00% | -0.61% | 0 gp | -18 gp |

## Known-good anchors

Known-good status: **REVIEW** (PASS ≤1% drift; REVIEW >1%; FAIL >5%).
Configured anchors include Holy Avenger, Defender, Vorpal Sword, +1/+2/+3 Weapon/Armor, Dragon Slayer, Giant Slayer, and Vicious Weapon families when present.

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Vorpal Glaive | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 54,605 gp | 54,004 gp | -600 gp | -1.10% | reference-anchored |
| Vorpal Greatsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 54,605 gp | 54,004 gp | -600 gp | -1.10% | reference-anchored |
| Vorpal Longsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 54,605 gp | 54,004 gp | -600 gp | -1.10% | reference-anchored |
| Vorpal Scimitar | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 54,605 gp | 54,004 gp | -600 gp | -1.10% | reference-anchored |
| +3 Leather Armor | Dungeon Master's Guide (2024) | Legendary | Light Armor | 29,832 gp | 29,508 gp | -324 gp | -1.09% | reference-anchored |
| +3 Padded Armor | Dungeon Master's Guide (2024) | Legendary | Light Armor | 29,832 gp | 29,508 gp | -324 gp | -1.09% | reference-anchored |
| +3 Studded Leather Armor | Dungeon Master's Guide (2024) | Legendary | Light Armor | 29,832 gp | 29,508 gp | -324 gp | -1.09% | reference-anchored |
| +2 Moon Sickle | Tasha's Cauldron of Everything | Rare | Melee Weapon | 12,022 gp | 12,299 gp | 277 gp | 2.31% | reference-anchored |
| +2 Chain Mail | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,454 gp | 8,594 gp | 140 gp | 1.66% | reference-anchored |
| +2 Plate Armor | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,454 gp | 8,594 gp | 140 gp | 1.66% | reference-anchored |
| +2 Ring Mail | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,454 gp | 8,594 gp | 140 gp | 1.66% | reference-anchored |
| +2 Splint Armor | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,454 gp | 8,594 gp | 140 gp | 1.66% | reference-anchored |
| +2 Leather Armor | Dungeon Master's Guide (2024) | Very Rare | Light Armor | 8,426 gp | 8,332 gp | -94 gp | -1.11% | reference-anchored |
| +2 Padded Armor | Dungeon Master's Guide (2024) | Very Rare | Light Armor | 8,426 gp | 8,332 gp | -94 gp | -1.11% | reference-anchored |
| +2 Studded Leather Armor | Dungeon Master's Guide (2024) | Very Rare | Light Armor | 8,426 gp | 8,332 gp | -94 gp | -1.11% | reference-anchored |
| +3 Moon Sickle | Tasha's Cauldron of Everything | Very Rare | Melee Weapon | 32,952 gp | 32,876 gp | -75 gp | -0.23% | reference-anchored |
| +3 Chain Mail | Dungeon Master's Guide (2024) | Legendary | Heavy Armor | 29,656 gp | 29,582 gp | -74 gp | -0.25% | reference-anchored |
| +3 Ring Mail | Dungeon Master's Guide (2024) | Legendary | Heavy Armor | 29,656 gp | 29,582 gp | -74 gp | -0.25% | reference-anchored |
| +3 Splint Armor | Dungeon Master's Guide (2024) | Legendary | Heavy Armor | 29,656 gp | 29,582 gp | -74 gp | -0.25% | reference-anchored |
| +1 Moon Sickle | Tasha's Cauldron of Everything | Uncommon | Melee Weapon | 3,925 gp | 3,858 gp | -67 gp | -1.70% | reference-anchored |

## Artifact/legendary movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Breastplate of Kamvuul Norek | Exploring Eberron (2024) | Legendary | Medium Armor | 103,206 gp | 151,841 gp | 48,635 gp | 47.12% | formula/ML-only |
| Harp of Gilded Plenty | Bigby Presents: Glory of the Giants | Legendary | Musical Instrument | 89,148 gp | 49,539 gp | -39,608 gp | -44.43% | formula/ML-only |
| Dragonlance Pike | Fizban's Treasury of Dragons | Legendary | Melee Weapon | 136,656 gp | 103,879 gp | -32,777 gp | -23.98% | reference-anchored |
| Dragonlance Lance | Fizban's Treasury of Dragons | Legendary | Melee Weapon | 126,683 gp | 96,298 gp | -30,385 gp | -23.98% | reference-anchored |
| Staff of Contaminated Power | Dungeons of Drakkenheim | Legendary | Melee Weapon | 90,325 gp | 64,172 gp | -26,154 gp | -28.96% | formula/ML-only |
| Inscrutable Staff | Dungeons of Drakkenheim | Legendary | Melee Weapon | 105,750 gp | 86,408 gp | -19,342 gp | -18.29% | formula/ML-only |
| Stonebreaker's Breastplate | Bigby Presents: Glory of the Giants | Legendary | Medium Armor | 58,762 gp | 77,083 gp | 18,321 gp | 31.18% | formula/ML-only |
| Euryale's Aegis | The Book of Many Things | Legendary | Shield | 68,121 gp | 86,103 gp | 17,982 gp | 26.40% | formula/ML-only |
| Verminshroud (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 80,207 gp | 95,260 gp | 15,053 gp | 18.77% | formula/ML-only |
| Jester's Mask | The Book of Many Things | Legendary | Wondrous Item | 56,830 gp | 71,636 gp | 14,806 gp | 26.05% | formula/ML-only |
| Nepenthe | Van Richten's Guide to Ravenloft | Legendary | Melee Weapon | 204,366 gp | 189,891 gp | -14,474 gp | -7.08% | formula/ML-only |
| Azuredge | Waterdeep: Dragon Heist | Legendary | Melee Weapon | 123,008 gp | 110,884 gp | -12,124 gp | -9.86% | formula/ML-only |
| Hazirawn | Hoard of the Dragon Queen | Legendary | Melee Weapon | 104,204 gp | 93,118 gp | -11,086 gp | -10.64% | formula/ML-only |
| Grimoire Infinitus (Dormant) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 31,614 gp | 42,474 gp | 10,860 gp | 34.35% | formula/ML-only |
| Grimoire Infinitus (Awakened) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 46,398 gp | 57,258 gp | 10,860 gp | 23.41% | formula/ML-only |
| Grimoire Infinitus (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 46,398 gp | 57,258 gp | 10,860 gp | 23.41% | formula/ML-only |
| Deck of Many More Things | The Book of Many Things | Legendary | Wondrous Item | 163,975 gp | 174,513 gp | 10,538 gp | 6.43% | reference-anchored |
| Gloves of Soul Catching | Candlekeep Mysteries | Legendary | Wondrous Item | 96,975 gp | 107,114 gp | 10,139 gp | 10.46% | formula/ML-only |
| Witchlight Vane | The Wild Beyond the Witchlight | Legendary | Wondrous Item | 61,366 gp | 70,859 gp | 9,493 gp | 15.47% | formula/ML-only |
| Infiltrator's Key (Awakened) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 82,499 gp | 73,234 gp | -9,265 gp | -11.23% | formula/ML-only |

## Largest movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Breastplate of Kamvuul Norek | Exploring Eberron (2024) | Legendary | Medium Armor | 103,206 gp | 151,841 gp | 48,635 gp | 47.12% | formula/ML-only |
| Harp of Gilded Plenty | Bigby Presents: Glory of the Giants | Legendary | Musical Instrument | 89,148 gp | 49,539 gp | -39,608 gp | -44.43% | formula/ML-only |
| Dragonlance Pike | Fizban's Treasury of Dragons | Legendary | Melee Weapon | 136,656 gp | 103,879 gp | -32,777 gp | -23.98% | reference-anchored |
| Dragonlance Lance | Fizban's Treasury of Dragons | Legendary | Melee Weapon | 126,683 gp | 96,298 gp | -30,385 gp | -23.98% | reference-anchored |
| Staff of Contaminated Power | Dungeons of Drakkenheim | Legendary | Melee Weapon | 90,325 gp | 64,172 gp | -26,154 gp | -28.96% | formula/ML-only |
| Inscrutable Staff | Dungeons of Drakkenheim | Legendary | Melee Weapon | 105,750 gp | 86,408 gp | -19,342 gp | -18.29% | formula/ML-only |
| Stonebreaker's Breastplate | Bigby Presents: Glory of the Giants | Legendary | Medium Armor | 58,762 gp | 77,083 gp | 18,321 gp | 31.18% | formula/ML-only |
| Euryale's Aegis | The Book of Many Things | Legendary | Shield | 68,121 gp | 86,103 gp | 17,982 gp | 26.40% | formula/ML-only |
| Verminshroud (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 80,207 gp | 95,260 gp | 15,053 gp | 18.77% | formula/ML-only |
| Jester's Mask | The Book of Many Things | Legendary | Wondrous Item | 56,830 gp | 71,636 gp | 14,806 gp | 26.05% | formula/ML-only |
| Nepenthe | Van Richten's Guide to Ravenloft | Legendary | Melee Weapon | 204,366 gp | 189,891 gp | -14,474 gp | -7.08% | formula/ML-only |
| Blast Scepter | Waterdeep: Dungeon of the Mad Mage | Very Rare | Rod | 34,122 gp | 48,454 gp | 14,332 gp | 42.00% | formula/ML-only |
| Azuredge | Waterdeep: Dragon Heist | Legendary | Melee Weapon | 123,008 gp | 110,884 gp | -12,124 gp | -9.86% | formula/ML-only |
| Hazirawn | Hoard of the Dragon Queen | Legendary | Melee Weapon | 104,204 gp | 93,118 gp | -11,086 gp | -10.64% | formula/ML-only |
| Grimoire Infinitus (Dormant) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 31,614 gp | 42,474 gp | 10,860 gp | 34.35% | formula/ML-only |
| Grimoire Infinitus (Awakened) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 46,398 gp | 57,258 gp | 10,860 gp | 23.41% | formula/ML-only |
| Grimoire Infinitus (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 46,398 gp | 57,258 gp | 10,860 gp | 23.41% | formula/ML-only |
| Deck of Many More Things | The Book of Many Things | Legendary | Wondrous Item | 163,975 gp | 174,513 gp | 10,538 gp | 6.43% | reference-anchored |
| Gloves of Soul Catching | Candlekeep Mysteries | Legendary | Wondrous Item | 96,975 gp | 107,114 gp | 10,139 gp | 10.46% | formula/ML-only |
| Witchlight Vane | The Wild Beyond the Witchlight | Legendary | Wondrous Item | 61,366 gp | 70,859 gp | 9,493 gp | 15.47% | formula/ML-only |
| Infiltrator's Key (Awakened) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 82,499 gp | 73,234 gp | -9,265 gp | -11.23% | formula/ML-only |
| Platinum Scarf | Fizban's Treasury of Dragons | Legendary | Wondrous Item | 56,479 gp | 47,451 gp | -9,028 gp | -15.98% | formula/ML-only |
| Sunsword | Curse of Strahd | Legendary | Melee Weapon | 63,558 gp | 72,436 gp | 8,878 gp | 13.97% | formula/ML-only |
| Tinderstrike | Princes of the Apocalypse | Legendary | Melee Weapon | 123,540 gp | 114,986 gp | -8,553 gp | -6.92% | formula/ML-only |
| Telescopic Transporter | The Book of Many Things | Legendary | Wondrous Item | 34,081 gp | 42,602 gp | 8,521 gp | 25.00% | formula/ML-only |

## Largest percent movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Demonglass Dart | Frontiers of Eberron: Quickstone | Rare | Ranged Weapon | 615 gp | 4,765 gp | 4,150 gp | 675.23% | reference-anchored |
| Demonglass Dagger | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 631 gp | 4,882 gp | 4,251 gp | 674.12% | reference-anchored |
| Demonglass Club | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,940 gp | 4,302 gp | 673.58% | reference-anchored |
| Demonglass Handaxe | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,940 gp | 4,302 gp | 673.58% | reference-anchored |
| Demonglass Hooked Shortspear | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,940 gp | 4,302 gp | 673.58% | reference-anchored |
| Demonglass Hoopak | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,940 gp | 4,302 gp | 673.58% | reference-anchored |
| Demonglass Javelin | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,940 gp | 4,302 gp | 673.58% | reference-anchored |
| Demonglass Light Hammer | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,940 gp | 4,302 gp | 673.58% | reference-anchored |
| Demonglass Shortbow | Frontiers of Eberron: Quickstone | Rare | Ranged Weapon | 639 gp | 4,940 gp | 4,302 gp | 673.58% | reference-anchored |
| Demonglass Shortsword | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,940 gp | 4,302 gp | 673.58% | reference-anchored |
| Demonglass Sickle | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,940 gp | 4,302 gp | 673.58% | reference-anchored |
| Demonglass Blowgun | Frontiers of Eberron: Quickstone | Rare | Ranged Weapon | 643 gp | 4,972 gp | 4,329 gp | 673.29% | reference-anchored |
| Demonglass Hand Crossbow | Frontiers of Eberron: Quickstone | Rare | Ranged Weapon | 643 gp | 4,975 gp | 4,331 gp | 673.27% | reference-anchored |
| Demonglass Scimitar | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 643 gp | 4,975 gp | 4,331 gp | 673.27% | reference-anchored |
| Demonglass Sling | Frontiers of Eberron: Quickstone | Rare | Ranged Weapon | 643 gp | 4,975 gp | 4,331 gp | 673.27% | reference-anchored |
| Demonglass Spear | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 643 gp | 4,975 gp | 4,331 gp | 673.27% | reference-anchored |
| Demonglass Whip | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 643 gp | 4,975 gp | 4,331 gp | 673.27% | reference-anchored |
| Demonglass Mace | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 647 gp | 4,999 gp | 4,352 gp | 673.06% | reference-anchored |
| Demonglass Quarterstaff | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 647 gp | 4,999 gp | 4,352 gp | 673.06% | reference-anchored |
| Demonglass Flail | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 663 gp | 5,121 gp | 4,458 gp | 672.02% | reference-anchored |
| Demonglass Longbow | Frontiers of Eberron: Quickstone | Rare | Ranged Weapon | 663 gp | 5,121 gp | 4,458 gp | 672.02% | reference-anchored |
| Demonglass Rapier | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 663 gp | 5,121 gp | 4,458 gp | 672.02% | reference-anchored |
| Demonglass War Pick | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 663 gp | 5,121 gp | 4,458 gp | 672.02% | reference-anchored |
| Demonglass Longsword | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 668 gp | 5,156 gp | 4,487 gp | 671.73% | reference-anchored |
| Demonglass Yklwa | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 668 gp | 5,156 gp | 4,487 gp | 671.73% | reference-anchored |

## Anchor-tier transitions / ML R² / double-count audit

- Anchor-tier transition and ML R² checks require pipeline metadata not present in final CSV snapshots; add those columns to future candidate snapshots if needed.
- Use the known-good and reference-anchored sections above as the first-pass double-count audit for extraction-driven price creep.
- Formula exposure reports (for example, extra_damage impact) are not final-price deltas.
