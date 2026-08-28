# Price Creep Guardrail

Baseline CSV: `output/pricing_guide.csv`
Candidate CSV: `output/pricing_guide_candidate.csv`

## Input row matching

- Common rows: 4748
- New candidate rows: 1
- Missing candidate rows: 1

## Aggregate final-price drift

- Median % drift: 0.00%
- Mean % drift: 7.08%
- Median gp drift: 0 gp
- Mean gp drift: -27 gp
- Rows >5% drift: 446
- Rows >10% drift: 322
- Rows >25% drift: 180

## Reference anchored vs formula/ML-only

| Split | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| formula/ML-only | 3708 | 0.00% | 8.78% | 0 gp | -37 gp |
| reference-anchored | 1040 | -0.03% | 1.02% | -0 gp | 7 gp |

## Drift by rarity

| Rarity | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Rare | 1411 | 0.00% | 20.10% | 0 gp | -117 gp |
| Uncommon | 946 | 0.00% | 5.60% | 0 gp | 37 gp |
| Very Rare | 853 | 0.00% | 0.07% | 0 gp | 7 gp |
| Legendary | 639 | 0.00% | 0.19% | 0 gp | -7 gp |
| Mundane | 461 | 0.00% | -0.43% | 0 gp | -0 gp |
| Common | 350 | 0.00% | 0.01% | 0 gp | 0 gp |
| Artifact | 71 | 0.00% | 0.00% | 0 gp | 0 gp |
| Unknown Magic | 9 | -0.21% | -2.96% | -1 gp | -150 gp |
| Varies | 8 | 0.00% | 0.00% | 0 gp | 0 gp |

## Drift by type

| Type | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Melee Weapon | 1863 | 0.00% | 13.70% | 0 gp | -192 gp |
| Wondrous Item | 770 | -0.15% | 1.51% | -0 gp | 200 gp |
| Ranged Weapon | 536 | 0.00% | 12.56% | 0 gp | 10 gp |
| Medium Armor | 279 | 0.00% | 0.31% | 0 gp | 220 gp |
| Heavy Armor | 217 | 0.00% | 0.01% | 0 gp | 7 gp |
| Adventuring Gear | 196 | 0.00% | -0.51% | 0 gp | -0 gp |
| Light Armor | 142 | 0.00% | 0.19% | 0 gp | 69 gp |
| Spellcasting Focus | 135 | 0.00% | 4.11% | 0 gp | 62 gp |
| Artisan's Tools | 71 | 0.00% | 0.01% | 0 gp | 2 gp |
| Ring | 69 | -0.58% | -1.05% | -29 gp | -62 gp |
| Potion | 66 | -0.20% | -0.32% | -3 gp | -23 gp |
| Ammunition | 64 | 0.00% | -1.51% | 0 gp | -0 gp |
| Wand | 48 | 0.92% | 1.73% | 3 gp | 186 gp |
| Musical Instrument | 45 | 0.00% | -1.57% | 0 gp | -859 gp |
| Scroll | 35 | -1.11% | -2.65% | -3 gp | -828 gp |
| Other | 34 | -0.10% | -7.30% | -0 gp | -78 gp |
| Shield | 31 | -0.33% | 1.11% | -6 gp | 706 gp |
| Trade Goods | 24 | 0.00% | 0.00% | 0 gp | 0 gp |
| Tack & Harness | 22 | 0.00% | 0.00% | 0 gp | 0 gp |
| Rod | 21 | 1.40% | 5.53% | 154 gp | 1,587 gp |

## Drift by source

| Source | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Dungeon Master's Guide (2024) | 1981 | 0.00% | -0.16% | 0 gp | -21 gp |
| Monsters of Drakkenheim | 280 | 0.00% | 0.38% | 0 gp | 39 gp |
| Exploring Eberron (2024) | 270 | 0.00% | -4.10% | 0 gp | -529 gp |
| The Book of Many Things | 219 | 0.00% | 2.74% | 0 gp | 437 gp |
| Player's Handbook (2024) | 217 | 0.00% | -0.46% | 0 gp | -0 gp |
| Fizban's Treasury of Dragons | 206 | 0.00% | -0.03% | 0 gp | -260 gp |
| Explorer's Guide to Wildemount | 190 | 0.00% | -7.82% | 0 gp | -595 gp |
| Monster Manual | 170 | 1.41% | 3.07% | 48 gp | -3 gp |
| Frontiers of Eberron: Quickstone | 111 | 175.00% | 311.43% | 1,331 gp | 2,090 gp |
| Eberron: Rising from the Last War | 107 | 0.00% | 0.10% | 0 gp | 4 gp |
| Tasha's Cauldron of Everything | 80 | -0.09% | -0.02% | -3 gp | 1 gp |
| Acquisitions Incorporated | 75 | 0.55% | 2.30% | 3 gp | 21 gp |
| Eberron: Forge of the Artificer | 72 | 0.00% | -0.07% | 0 gp | -0 gp |
| Critical Role: Call of the Netherdeep | 66 | 0.00% | -0.18% | 0 gp | -117 gp |
| Baldur's Gate: Descent Into Avernus | 56 | 0.00% | -0.02% | 0 gp | -17 gp |
| Player's Handbook | 47 | 0.00% | -2.13% | 0 gp | -0 gp |
| Bigby Presents: Glory of the Giants | 44 | 0.00% | 5.93% | 0 gp | -55 gp |
| Dungeons of Drakkenheim | 43 | 0.00% | -1.25% | 0 gp | -1,353 gp |
| Guildmasters' Guide to Ravnica | 42 | -0.10% | 0.52% | -0 gp | -85 gp |
| Tomb of Annihilation | 27 | 0.00% | -0.51% | 0 gp | -103 gp |

## Known-good anchors

Known-good status: **REVIEW** (PASS ≤1% drift; REVIEW >1%; FAIL >5%).
Configured anchors include Holy Avenger, Defender, Vorpal Sword, +1/+2/+3 Weapon/Armor, Dragon Slayer, Giant Slayer, and Vicious Weapon families when present.

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Vorpal Glaive | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 54,605 gp | 54,087 gp | -518 gp | -0.95% | reference-anchored |
| Vorpal Greatsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 54,605 gp | 54,087 gp | -518 gp | -0.95% | reference-anchored |
| Vorpal Longsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 54,605 gp | 54,087 gp | -518 gp | -0.95% | reference-anchored |
| Vorpal Scimitar | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 54,605 gp | 54,087 gp | -518 gp | -0.95% | reference-anchored |
| +3 Breastplate | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,780 gp | 29,517 gp | -263 gp | -0.88% | reference-anchored |
| +3 Chain Shirt | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,780 gp | 29,517 gp | -263 gp | -0.88% | reference-anchored |
| +3 Half Plate Armor | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,780 gp | 29,517 gp | -263 gp | -0.88% | reference-anchored |
| +3 Hide Armor | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,780 gp | 29,517 gp | -263 gp | -0.88% | reference-anchored |
| +3 Scale Mail | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,780 gp | 29,517 gp | -263 gp | -0.88% | reference-anchored |
| +3 Plate Armor | Dungeon Master's Guide (2024) | Legendary | Heavy Armor | 29,781 gp | 29,518 gp | -263 gp | -0.88% | reference-anchored |
| +3 Leather Armor | Dungeon Master's Guide (2024) | Legendary | Light Armor | 29,832 gp | 29,586 gp | -245 gp | -0.82% | reference-anchored |
| +3 Padded Armor | Dungeon Master's Guide (2024) | Legendary | Light Armor | 29,832 gp | 29,586 gp | -245 gp | -0.82% | reference-anchored |
| +3 Studded Leather Armor | Dungeon Master's Guide (2024) | Legendary | Light Armor | 29,832 gp | 29,586 gp | -245 gp | -0.82% | reference-anchored |
| +3 Chain Mail | Dungeon Master's Guide (2024) | Legendary | Heavy Armor | 29,656 gp | 29,481 gp | -175 gp | -0.59% | reference-anchored |
| +3 Ring Mail | Dungeon Master's Guide (2024) | Legendary | Heavy Armor | 29,656 gp | 29,481 gp | -175 gp | -0.59% | reference-anchored |
| +3 Splint Armor | Dungeon Master's Guide (2024) | Legendary | Heavy Armor | 29,656 gp | 29,481 gp | -175 gp | -0.59% | reference-anchored |
| +2 Moon Sickle | Tasha's Cauldron of Everything | Rare | Melee Weapon | 12,022 gp | 12,194 gp | 172 gp | 1.43% | reference-anchored |
| +2 Chain Mail | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,454 gp | 8,604 gp | 151 gp | 1.78% | reference-anchored |
| +2 Plate Armor | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,454 gp | 8,604 gp | 151 gp | 1.78% | reference-anchored |
| +2 Ring Mail | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,454 gp | 8,604 gp | 151 gp | 1.78% | reference-anchored |

## Artifact/legendary movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Breastplate of Kamvuul Norek | Exploring Eberron (2024) | Legendary | Medium Armor | 103,206 gp | 144,692 gp | 41,486 gp | 40.20% | formula/ML-only |
| Harp of Gilded Plenty | Bigby Presents: Glory of the Giants | Legendary | Musical Instrument | 89,148 gp | 51,946 gp | -37,202 gp | -41.73% | formula/ML-only |
| Dragonlance Pike | Fizban's Treasury of Dragons | Legendary | Melee Weapon | 136,656 gp | 103,879 gp | -32,777 gp | -23.98% | formula/ML-only |
| Staff of Contaminated Power | Dungeons of Drakkenheim | Legendary | Melee Weapon | 90,325 gp | 58,241 gp | -32,084 gp | -35.52% | formula/ML-only |
| Dragonlance Lance | Fizban's Treasury of Dragons | Legendary | Melee Weapon | 126,683 gp | 96,298 gp | -30,385 gp | -23.98% | formula/ML-only |
| Stormgirdle (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 179,134 gp | 204,487 gp | 25,352 gp | 14.15% | formula/ML-only |
| Stormgirdle (Awakened) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 132,828 gp | 157,158 gp | 24,330 gp | 18.32% | formula/ML-only |
| Stonebreaker's Breastplate | Bigby Presents: Glory of the Giants | Legendary | Medium Armor | 58,762 gp | 78,910 gp | 20,149 gp | 34.29% | formula/ML-only |
| Tinderstrike | Princes of the Apocalypse | Legendary | Melee Weapon | 123,540 gp | 104,202 gp | -19,337 gp | -15.65% | formula/ML-only |
| Nepenthe | Van Richten's Guide to Ravenloft | Legendary | Melee Weapon | 204,366 gp | 186,065 gp | -18,301 gp | -8.96% | formula/ML-only |
| Euryale's Aegis | The Book of Many Things | Legendary | Shield | 68,121 gp | 85,177 gp | 17,056 gp | 25.04% | formula/ML-only |
| Inscrutable Staff | Dungeons of Drakkenheim | Legendary | Melee Weapon | 105,750 gp | 92,472 gp | -13,278 gp | -12.56% | formula/ML-only |
| Azuredge | Waterdeep: Dragon Heist | Legendary | Melee Weapon | 123,008 gp | 110,442 gp | -12,566 gp | -10.22% | formula/ML-only |
| Dawnbringer | Out of the Abyss | Legendary | Melee Weapon | 67,203 gp | 55,594 gp | -11,608 gp | -17.27% | formula/ML-only |
| Infiltrator's Key (Dormant) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 34,093 gp | 45,060 gp | 10,967 gp | 32.17% | formula/ML-only |
| Platinum Scarf | Fizban's Treasury of Dragons | Legendary | Wondrous Item | 56,479 gp | 45,779 gp | -10,700 gp | -18.94% | formula/ML-only |
| Sunsword | Curse of Strahd | Legendary | Melee Weapon | 63,558 gp | 74,194 gp | 10,636 gp | 16.73% | formula/ML-only |
| Witchlight Watch | The Wild Beyond the Witchlight | Legendary | Wondrous Item | 57,628 gp | 67,960 gp | 10,332 gp | 17.93% | formula/ML-only |
| Talarith | Boo's Astral Menagerie | Legendary | Wondrous Item | 47,508 gp | 56,904 gp | 9,395 gp | 19.78% | formula/ML-only |
| White Dragon Mask | The Rise of Tiamat Online Supplement | Legendary | Wondrous Item | 95,859 gp | 86,825 gp | -9,034 gp | -9.42% | formula/ML-only |

## Largest movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Breastplate of Kamvuul Norek | Exploring Eberron (2024) | Legendary | Medium Armor | 103,206 gp | 144,692 gp | 41,486 gp | 40.20% | formula/ML-only |
| Harp of Gilded Plenty | Bigby Presents: Glory of the Giants | Legendary | Musical Instrument | 89,148 gp | 51,946 gp | -37,202 gp | -41.73% | formula/ML-only |
| Dragonlance Pike | Fizban's Treasury of Dragons | Legendary | Melee Weapon | 136,656 gp | 103,879 gp | -32,777 gp | -23.98% | formula/ML-only |
| Staff of Contaminated Power | Dungeons of Drakkenheim | Legendary | Melee Weapon | 90,325 gp | 58,241 gp | -32,084 gp | -35.52% | formula/ML-only |
| Dragonlance Lance | Fizban's Treasury of Dragons | Legendary | Melee Weapon | 126,683 gp | 96,298 gp | -30,385 gp | -23.98% | formula/ML-only |
| Stormgirdle (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 179,134 gp | 204,487 gp | 25,352 gp | 14.15% | formula/ML-only |
| Stormgirdle (Awakened) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 132,828 gp | 157,158 gp | 24,330 gp | 18.32% | formula/ML-only |
| Stonebreaker's Breastplate | Bigby Presents: Glory of the Giants | Legendary | Medium Armor | 58,762 gp | 78,910 gp | 20,149 gp | 34.29% | formula/ML-only |
| Tinderstrike | Princes of the Apocalypse | Legendary | Melee Weapon | 123,540 gp | 104,202 gp | -19,337 gp | -15.65% | formula/ML-only |
| Nepenthe | Van Richten's Guide to Ravenloft | Legendary | Melee Weapon | 204,366 gp | 186,065 gp | -18,301 gp | -8.96% | formula/ML-only |
| Euryale's Aegis | The Book of Many Things | Legendary | Shield | 68,121 gp | 85,177 gp | 17,056 gp | 25.04% | formula/ML-only |
| Blast Scepter | Waterdeep: Dungeon of the Mad Mage | Very Rare | Rod | 34,122 gp | 47,525 gp | 13,404 gp | 39.28% | formula/ML-only |
| Inscrutable Staff | Dungeons of Drakkenheim | Legendary | Melee Weapon | 105,750 gp | 92,472 gp | -13,278 gp | -12.56% | formula/ML-only |
| Azuredge | Waterdeep: Dragon Heist | Legendary | Melee Weapon | 123,008 gp | 110,442 gp | -12,566 gp | -10.22% | formula/ML-only |
| Dawnbringer | Out of the Abyss | Legendary | Melee Weapon | 67,203 gp | 55,594 gp | -11,608 gp | -17.27% | formula/ML-only |
| Rod of Hellish Flames | The Book of Many Things | Very Rare | Rod | 23,376 gp | 34,769 gp | 11,392 gp | 48.73% | formula/ML-only |
| Infiltrator's Key (Dormant) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 34,093 gp | 45,060 gp | 10,967 gp | 32.17% | formula/ML-only |
| Platinum Scarf | Fizban's Treasury of Dragons | Legendary | Wondrous Item | 56,479 gp | 45,779 gp | -10,700 gp | -18.94% | formula/ML-only |
| Sunsword | Curse of Strahd | Legendary | Melee Weapon | 63,558 gp | 74,194 gp | 10,636 gp | 16.73% | formula/ML-only |
| Witchlight Watch | The Wild Beyond the Witchlight | Legendary | Wondrous Item | 57,628 gp | 67,960 gp | 10,332 gp | 17.93% | formula/ML-only |
| Talarith | Boo's Astral Menagerie | Legendary | Wondrous Item | 47,508 gp | 56,904 gp | 9,395 gp | 19.78% | formula/ML-only |
| White Dragon Mask | The Rise of Tiamat Online Supplement | Legendary | Wondrous Item | 95,859 gp | 86,825 gp | -9,034 gp | -9.42% | formula/ML-only |
| Hazirawn | Hoard of the Dragon Queen | Legendary | Melee Weapon | 104,204 gp | 95,433 gp | -8,771 gp | -8.42% | formula/ML-only |
| Moon Card | The Book of Many Things | Legendary | Wondrous Item | 53,894 gp | 62,498 gp | 8,605 gp | 15.97% | formula/ML-only |
| Jester's Mask | The Book of Many Things | Legendary | Wondrous Item | 56,830 gp | 65,351 gp | 8,521 gp | 14.99% | formula/ML-only |

## Largest percent movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Piwafwi (Cloak of Elvenkind) | Out of the Abyss | Uncommon | Wondrous Item | 514 gp | 4,067 gp | 3,552 gp | 690.45% | reference-anchored |
| Demonglass Dart | Frontiers of Eberron: Quickstone | Rare | Ranged Weapon | 615 gp | 4,765 gp | 4,150 gp | 675.23% | formula/ML-only |
| Demonglass Dagger | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 631 gp | 4,882 gp | 4,251 gp | 674.12% | formula/ML-only |
| Demonglass Club | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,940 gp | 4,302 gp | 673.58% | formula/ML-only |
| Demonglass Handaxe | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,940 gp | 4,302 gp | 673.58% | formula/ML-only |
| Demonglass Hooked Shortspear | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,940 gp | 4,302 gp | 673.58% | formula/ML-only |
| Demonglass Hoopak | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,940 gp | 4,302 gp | 673.58% | formula/ML-only |
| Demonglass Javelin | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,940 gp | 4,302 gp | 673.58% | formula/ML-only |
| Demonglass Light Hammer | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,940 gp | 4,302 gp | 673.58% | formula/ML-only |
| Demonglass Shortbow | Frontiers of Eberron: Quickstone | Rare | Ranged Weapon | 639 gp | 4,940 gp | 4,302 gp | 673.58% | formula/ML-only |
| Demonglass Shortsword | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,940 gp | 4,302 gp | 673.58% | formula/ML-only |
| Demonglass Sickle | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,940 gp | 4,302 gp | 673.58% | formula/ML-only |
| Demonglass Blowgun | Frontiers of Eberron: Quickstone | Rare | Ranged Weapon | 643 gp | 4,972 gp | 4,329 gp | 673.29% | formula/ML-only |
| Demonglass Hand Crossbow | Frontiers of Eberron: Quickstone | Rare | Ranged Weapon | 643 gp | 4,975 gp | 4,331 gp | 673.27% | formula/ML-only |
| Demonglass Scimitar | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 643 gp | 4,975 gp | 4,331 gp | 673.27% | formula/ML-only |
| Demonglass Sling | Frontiers of Eberron: Quickstone | Rare | Ranged Weapon | 643 gp | 4,975 gp | 4,331 gp | 673.27% | formula/ML-only |
| Demonglass Spear | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 643 gp | 4,975 gp | 4,331 gp | 673.27% | formula/ML-only |
| Demonglass Whip | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 643 gp | 4,975 gp | 4,331 gp | 673.27% | formula/ML-only |
| Demonglass Mace | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 647 gp | 4,999 gp | 4,352 gp | 673.06% | formula/ML-only |
| Demonglass Quarterstaff | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 647 gp | 4,999 gp | 4,352 gp | 673.06% | formula/ML-only |
| Demonglass Flail | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 663 gp | 5,121 gp | 4,458 gp | 672.02% | formula/ML-only |
| Demonglass Longbow | Frontiers of Eberron: Quickstone | Rare | Ranged Weapon | 663 gp | 5,121 gp | 4,458 gp | 672.02% | formula/ML-only |
| Demonglass Rapier | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 663 gp | 5,121 gp | 4,458 gp | 672.02% | formula/ML-only |
| Demonglass War Pick | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 663 gp | 5,121 gp | 4,458 gp | 672.02% | formula/ML-only |
| Demonglass Longsword | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 668 gp | 5,156 gp | 4,487 gp | 671.73% | formula/ML-only |

## Anchor-tier transitions / ML R² / double-count audit

- Anchor-tier transition and ML R² checks require pipeline metadata not present in final CSV snapshots; add those columns to future candidate snapshots if needed.
- Use the known-good and reference-anchored sections above as the first-pass double-count audit for extraction-driven price creep.
- Formula exposure reports (for example, extra_damage impact) are not final-price deltas.
