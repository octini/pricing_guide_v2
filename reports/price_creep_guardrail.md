# Price Creep Guardrail

Baseline CSV: `output/pricing_guide.csv`
Candidate CSV: `output/pricing_guide_candidate.csv`

## Input row matching

- Common rows: 4749
- New candidate rows: 0
- Missing candidate rows: 0

## Aggregate final-price drift

- Median % drift: 0.00%
- Mean % drift: 0.01%
- Median gp drift: 0 gp
- Mean gp drift: -2 gp
- Rows >5% drift: 67
- Rows >10% drift: 14
- Rows >25% drift: 0

## Reference anchored vs formula/ML-only

| Split | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| formula/ML-only | 3709 | 0.00% | 0.00% | 0 gp | -3 gp |
| reference-anchored | 1040 | 0.00% | 0.01% | 0 gp | 3 gp |

## Drift by rarity

| Rarity | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Rare | 1412 | 0.00% | 0.19% | 0 gp | 14 gp |
| Uncommon | 946 | 0.00% | -0.03% | 0 gp | -1 gp |
| Very Rare | 853 | 0.00% | 0.07% | 0 gp | 9 gp |
| Legendary | 639 | 0.00% | -0.12% | 0 gp | -54 gp |
| Mundane | 461 | 0.00% | 0.00% | 0 gp | 0 gp |
| Common | 350 | 0.00% | -0.58% | 0 gp | -1 gp |
| Artifact | 71 | 0.00% | 0.00% | 0 gp | 0 gp |
| Unknown Magic | 9 | -0.22% | -0.03% | -1 gp | 3 gp |
| Varies | 8 | 0.00% | 0.00% | 0 gp | 0 gp |

## Drift by type

| Type | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Melee Weapon | 1863 | 0.00% | 0.04% | 0 gp | 9 gp |
| Wondrous Item | 771 | 0.00% | -0.28% | 0 gp | -58 gp |
| Ranged Weapon | 536 | 0.00% | 0.03% | 0 gp | 4 gp |
| Medium Armor | 279 | 0.00% | 0.13% | 0 gp | 22 gp |
| Heavy Armor | 217 | 0.00% | 0.29% | 0 gp | 5 gp |
| Adventuring Gear | 196 | 0.00% | -0.00% | 0 gp | -0 gp |
| Light Armor | 142 | 0.00% | -0.01% | 0 gp | 53 gp |
| Spellcasting Focus | 135 | 0.00% | -0.05% | 0 gp | -45 gp |
| Artisan's Tools | 71 | 0.00% | -0.01% | 0 gp | -3 gp |
| Ring | 69 | 0.11% | -0.97% | 1 gp | 6 gp |
| Potion | 66 | 0.21% | 0.07% | 1 gp | -1 gp |
| Ammunition | 64 | 0.00% | -0.07% | 0 gp | -8 gp |
| Wand | 48 | 0.10% | 1.70% | 1 gp | 256 gp |
| Musical Instrument | 45 | 0.00% | 0.38% | 0 gp | 161 gp |
| Scroll | 35 | 0.00% | -0.17% | 0 gp | -173 gp |
| Other | 34 | 0.00% | 0.60% | 0 gp | -2 gp |
| Shield | 31 | 0.40% | 0.63% | 12 gp | -138 gp |
| Trade Goods | 24 | 0.00% | 0.00% | 0 gp | 0 gp |
| Tack & Harness | 22 | 0.00% | 0.00% | 0 gp | 0 gp |
| Rod | 21 | -0.36% | -0.26% | -8 gp | 23 gp |

## Drift by source

| Source | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Dungeon Master's Guide (2024) | 1981 | 0.00% | 0.00% | 0 gp | -3 gp |
| Monsters of Drakkenheim | 280 | 0.00% | 0.00% | 0 gp | -5 gp |
| Exploring Eberron (2024) | 270 | 0.00% | 0.10% | 0 gp | 115 gp |
| The Book of Many Things | 219 | 0.00% | -0.11% | 0 gp | -112 gp |
| Player's Handbook (2024) | 217 | 0.00% | 0.00% | 0 gp | 0 gp |
| Fizban's Treasury of Dragons | 206 | 0.00% | 0.04% | 0 gp | 2 gp |
| Explorer's Guide to Wildemount | 190 | 0.00% | 0.01% | 0 gp | 84 gp |
| Monster Manual | 170 | 0.19% | 0.11% | 10 gp | 2 gp |
| Frontiers of Eberron: Quickstone | 111 | 0.00% | -0.19% | 0 gp | -9 gp |
| Eberron: Rising from the Last War | 107 | 0.00% | -0.21% | 0 gp | -1 gp |
| Tasha's Cauldron of Everything | 80 | 0.22% | 0.15% | 8 gp | 15 gp |
| Acquisitions Incorporated | 75 | -0.13% | 0.67% | -1 gp | 40 gp |
| Eberron: Forge of the Artificer | 72 | 0.00% | -0.01% | 0 gp | -1 gp |
| Critical Role: Call of the Netherdeep | 66 | 0.00% | -0.59% | 0 gp | -208 gp |
| Baldur's Gate: Descent Into Avernus | 56 | 0.00% | -0.09% | 0 gp | -68 gp |
| Player's Handbook | 47 | 0.00% | 0.00% | 0 gp | 0 gp |
| Bigby Presents: Glory of the Giants | 44 | 0.00% | 1.02% | 0 gp | 349 gp |
| Dungeons of Drakkenheim | 43 | 0.00% | 0.42% | 0 gp | 28 gp |
| Guildmasters' Guide to Ravnica | 42 | 0.00% | -1.66% | 0 gp | 17 gp |
| Tomb of Annihilation | 27 | 0.00% | 0.18% | 0 gp | 18 gp |

## Known-good anchors

Known-good status: **REVIEW** (PASS ≤1% drift; REVIEW >1%; FAIL >5%).
Configured anchors include Holy Avenger, Defender, Vorpal Sword, +1/+2/+3 Weapon/Armor, Dragon Slayer, Giant Slayer, and Vicious Weapon families when present.

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Vorpal Glaive | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 53,758 gp | 54,130 gp | 372 gp | 0.69% | reference-anchored |
| Vorpal Greatsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 53,758 gp | 54,130 gp | 372 gp | 0.69% | reference-anchored |
| Vorpal Longsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 53,758 gp | 54,130 gp | 372 gp | 0.69% | reference-anchored |
| Vorpal Scimitar | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 53,758 gp | 54,130 gp | 372 gp | 0.69% | reference-anchored |
| +3 Moon Sickle | Tasha's Cauldron of Everything | Very Rare | Melee Weapon | 33,504 gp | 33,292 gp | -212 gp | -0.63% | reference-anchored |
| +3 Chain Mail | Dungeon Master's Guide (2024) | Legendary | Heavy Armor | 29,610 gp | 29,494 gp | -115 gp | -0.39% | reference-anchored |
| +3 Ring Mail | Dungeon Master's Guide (2024) | Legendary | Heavy Armor | 29,610 gp | 29,494 gp | -115 gp | -0.39% | reference-anchored |
| +3 Splint Armor | Dungeon Master's Guide (2024) | Legendary | Heavy Armor | 29,610 gp | 29,494 gp | -115 gp | -0.39% | reference-anchored |
| +2 Chain Mail | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,614 gp | 8,504 gp | -110 gp | -1.27% | reference-anchored |
| +2 Plate Armor | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,614 gp | 8,504 gp | -110 gp | -1.27% | reference-anchored |
| +2 Ring Mail | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,614 gp | 8,504 gp | -110 gp | -1.27% | reference-anchored |
| +2 Splint Armor | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,614 gp | 8,504 gp | -110 gp | -1.27% | reference-anchored |
| +3 Pistol | Dungeon Master's Guide (2024) | Very Rare | Ranged Weapon | 14,178 gp | 14,126 gp | -51 gp | -0.36% | reference-anchored |
| +2 Moon Sickle | Tasha's Cauldron of Everything | Rare | Melee Weapon | 12,061 gp | 12,106 gp | 45 gp | 0.38% | reference-anchored |
| +3 Longsword | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 14,203 gp | 14,168 gp | -35 gp | -0.25% | reference-anchored |
| +3 Yklwa | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 14,203 gp | 14,168 gp | -35 gp | -0.25% | reference-anchored |
| +2 Leather Armor | Dungeon Master's Guide (2024) | Very Rare | Light Armor | 8,428 gp | 8,395 gp | -33 gp | -0.39% | reference-anchored |
| +2 Padded Armor | Dungeon Master's Guide (2024) | Very Rare | Light Armor | 8,428 gp | 8,395 gp | -33 gp | -0.39% | reference-anchored |
| +2 Studded Leather Armor | Dungeon Master's Guide (2024) | Very Rare | Light Armor | 8,428 gp | 8,395 gp | -33 gp | -0.39% | reference-anchored |
| +1 Chain Mail | Dungeon Master's Guide (2024) | Rare | Heavy Armor | 1,784 gp | 1,806 gp | 22 gp | 1.24% | reference-anchored |

## Artifact/legendary movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Shaarat'doovol, the Blade of Truth | Exploring Eberron (2024) | Legendary | Melee Weapon | 191,030 gp | 213,000 gp | 21,971 gp | 11.50% | formula/ML-only |
| Hazirawn | Hoard of the Dragon Queen | Legendary | Melee Weapon | 102,877 gp | 92,835 gp | -10,042 gp | -9.76% | formula/ML-only |
| Staff of Contaminated Power | Dungeons of Drakkenheim | Legendary | Melee Weapon | 69,987 gp | 78,735 gp | 8,748 gp | 12.50% | formula/ML-only |
| Infiltrator's Key (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 84,117 gp | 92,052 gp | 7,935 gp | 9.43% | formula/ML-only |
| Harp of Gilded Plenty | Bigby Presents: Glory of the Giants | Legendary | Musical Instrument | 53,626 gp | 60,208 gp | 6,582 gp | 12.27% | formula/ML-only |
| Jewel of Three Prayers (Exalted) | Critical Role: Call of the Netherdeep | Legendary | Wondrous Item | 55,039 gp | 48,527 gp | -6,512 gp | -11.83% | formula/ML-only |
| Ascendant Dragon-Touched Focus | Fizban's Treasury of Dragons | Legendary | Spellcasting Focus | 139,557 gp | 134,287 gp | -5,270 gp | -3.78% | formula/ML-only |
| Witchlight Vane | The Wild Beyond the Witchlight | Legendary | Wondrous Item | 70,462 gp | 65,209 gp | -5,253 gp | -7.45% | formula/ML-only |
| Deck of Many More Things | The Book of Many Things | Legendary | Wondrous Item | 191,370 gp | 186,175 gp | -5,195 gp | -2.71% | formula/ML-only |
| Hide of the Feral Guardian (Dormant) | Explorer's Guide to Wildemount | Legendary | Light Armor | 67,339 gp | 71,986 gp | 4,647 gp | 6.90% | formula/ML-only |
| Nepenthe | Van Richten's Guide to Ravenloft | Legendary | Melee Weapon | 188,361 gp | 183,918 gp | -4,443 gp | -2.36% | formula/ML-only |
| Jewel of Three Prayers (Dormant) | Critical Role: Call of the Netherdeep | Legendary | Wondrous Item | 55,497 gp | 51,095 gp | -4,402 gp | -7.93% | formula/ML-only |
| Stormgirdle (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 178,996 gp | 183,000 gp | 4,004 gp | 2.24% | formula/ML-only |
| Stormgirdle (Awakened) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 134,194 gp | 137,924 gp | 3,731 gp | 2.78% | formula/ML-only |
| Gloves of Soul Catching | Candlekeep Mysteries | Legendary | Wondrous Item | 92,199 gp | 95,657 gp | 3,458 gp | 3.75% | formula/ML-only |
| Inscrutable Staff | Dungeons of Drakkenheim | Legendary | Melee Weapon | 92,161 gp | 88,777 gp | -3,384 gp | -3.67% | formula/ML-only |
| Shield of the Hidden Lord | Baldur's Gate: Descent Into Avernus | Legendary | Shield | 79,935 gp | 76,593 gp | -3,342 gp | -4.18% | formula/ML-only |
| Sunsword | Curse of Strahd | Legendary | Melee Weapon | 73,268 gp | 76,548 gp | 3,280 gp | 4.48% | formula/ML-only |
| Stonebreaker's Breastplate | Bigby Presents: Glory of the Giants | Legendary | Medium Armor | 68,579 gp | 71,840 gp | 3,261 gp | 4.75% | formula/ML-only |
| Crown of Westemär | Dungeons of Drakkenheim | Legendary | Wondrous Item | 96,705 gp | 93,604 gp | -3,101 gp | -3.21% | formula/ML-only |

## Largest movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Shaarat'doovol, the Blade of Truth | Exploring Eberron (2024) | Legendary | Melee Weapon | 191,030 gp | 213,000 gp | 21,971 gp | 11.50% | formula/ML-only |
| Hazirawn | Hoard of the Dragon Queen | Legendary | Melee Weapon | 102,877 gp | 92,835 gp | -10,042 gp | -9.76% | formula/ML-only |
| Staff of Contaminated Power | Dungeons of Drakkenheim | Legendary | Melee Weapon | 69,987 gp | 78,735 gp | 8,748 gp | 12.50% | formula/ML-only |
| Infiltrator's Key (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 84,117 gp | 92,052 gp | 7,935 gp | 9.43% | formula/ML-only |
| Harp of Gilded Plenty | Bigby Presents: Glory of the Giants | Legendary | Musical Instrument | 53,626 gp | 60,208 gp | 6,582 gp | 12.27% | formula/ML-only |
| Jewel of Three Prayers (Exalted) | Critical Role: Call of the Netherdeep | Legendary | Wondrous Item | 55,039 gp | 48,527 gp | -6,512 gp | -11.83% | formula/ML-only |
| Ascendant Dragon-Touched Focus | Fizban's Treasury of Dragons | Legendary | Spellcasting Focus | 139,557 gp | 134,287 gp | -5,270 gp | -3.78% | formula/ML-only |
| Witchlight Vane | The Wild Beyond the Witchlight | Legendary | Wondrous Item | 70,462 gp | 65,209 gp | -5,253 gp | -7.45% | formula/ML-only |
| Deck of Many More Things | The Book of Many Things | Legendary | Wondrous Item | 191,370 gp | 186,175 gp | -5,195 gp | -2.71% | formula/ML-only |
| Hide of the Feral Guardian (Dormant) | Explorer's Guide to Wildemount | Legendary | Light Armor | 67,339 gp | 71,986 gp | 4,647 gp | 6.90% | formula/ML-only |
| Nepenthe | Van Richten's Guide to Ravenloft | Legendary | Melee Weapon | 188,361 gp | 183,918 gp | -4,443 gp | -2.36% | formula/ML-only |
| Jewel of Three Prayers (Dormant) | Critical Role: Call of the Netherdeep | Legendary | Wondrous Item | 55,497 gp | 51,095 gp | -4,402 gp | -7.93% | formula/ML-only |
| Stormgirdle (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 178,996 gp | 183,000 gp | 4,004 gp | 2.24% | formula/ML-only |
| Stormgirdle (Awakened) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 134,194 gp | 137,924 gp | 3,731 gp | 2.78% | formula/ML-only |
| Gloves of Soul Catching | Candlekeep Mysteries | Legendary | Wondrous Item | 92,199 gp | 95,657 gp | 3,458 gp | 3.75% | formula/ML-only |
| Inscrutable Staff | Dungeons of Drakkenheim | Legendary | Melee Weapon | 92,161 gp | 88,777 gp | -3,384 gp | -3.67% | formula/ML-only |
| Shield of the Hidden Lord | Baldur's Gate: Descent Into Avernus | Legendary | Shield | 79,935 gp | 76,593 gp | -3,342 gp | -4.18% | formula/ML-only |
| Sunsword | Curse of Strahd | Legendary | Melee Weapon | 73,268 gp | 76,548 gp | 3,280 gp | 4.48% | formula/ML-only |
| Stonebreaker's Breastplate | Bigby Presents: Glory of the Giants | Legendary | Medium Armor | 68,579 gp | 71,840 gp | 3,261 gp | 4.75% | formula/ML-only |
| Crown of Westemär | Dungeons of Drakkenheim | Legendary | Wondrous Item | 96,705 gp | 93,604 gp | -3,101 gp | -3.21% | formula/ML-only |
| Ignacious, the Sword of Burning Truth | Dungeons of Drakkenheim | Legendary | Melee Weapon | 136,572 gp | 133,756 gp | -2,816 gp | -2.06% | formula/ML-only |
| Korolnor Scepter | Storm King's Thunder | Legendary | Melee Weapon | 66,852 gp | 64,158 gp | -2,694 gp | -4.03% | formula/ML-only |
| Gurt's Greataxe | Storm King's Thunder | Legendary | Melee Weapon | 73,176 gp | 70,526 gp | -2,650 gp | -3.62% | formula/ML-only |
| Reaper's Scream | Bigby Presents: Glory of the Giants | Legendary | Melee Weapon | 42,118 gp | 44,695 gp | 2,577 gp | 6.12% | formula/ML-only |
| Platinum Scarf | Fizban's Treasury of Dragons | Legendary | Wondrous Item | 57,253 gp | 59,782 gp | 2,530 gp | 4.42% | formula/ML-only |

## Largest percent movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Falkir's Helm of Pigheadedness | Waterdeep: Dungeon of the Mad Mage | Uncommon | Other | 457 gp | 536 gp | 79 gp | 17.24% | formula/ML-only |
| Sword of the Paruns | Guildmasters' Guide to Ravnica | Very Rare | Melee Weapon | 5,196 gp | 5,965 gp | 768 gp | 14.79% | formula/ML-only |
| Wingwear | Princes of the Apocalypse | Uncommon | Wondrous Item | 673 gp | 768 gp | 95 gp | 14.17% | formula/ML-only |
| Staff of Contaminated Power | Dungeons of Drakkenheim | Legendary | Melee Weapon | 69,987 gp | 78,735 gp | 8,748 gp | 12.50% | formula/ML-only |
| Harp of Gilded Plenty | Bigby Presents: Glory of the Giants | Legendary | Musical Instrument | 53,626 gp | 60,208 gp | 6,582 gp | 12.27% | formula/ML-only |
| Jewel of Three Prayers (Exalted) | Critical Role: Call of the Netherdeep | Legendary | Wondrous Item | 55,039 gp | 48,527 gp | -6,512 gp | -11.83% | formula/ML-only |
| Shaarat'doovol, the Blade of Truth | Exploring Eberron (2024) | Legendary | Melee Weapon | 191,030 gp | 213,000 gp | 21,971 gp | 11.50% | formula/ML-only |
| Staff of Defense | Phandelver and Below: The Shattered Obelisk | Rare | Melee Weapon | 3,722 gp | 4,131 gp | 409 gp | 10.98% | formula/ML-only |
| Baleful Talon | The Book of Many Things | Very Rare | Melee Weapon | 4,221 gp | 4,683 gp | 462 gp | 10.94% | formula/ML-only |
| Mithral +1 Ring Mail | Acquisitions Incorporated | Rare | Heavy Armor | 3,766 gp | 4,166 gp | 400 gp | 10.62% | formula/ML-only |
| Mithral +1 Scale Mail | Acquisitions Incorporated | Rare | Medium Armor | 3,810 gp | 4,210 gp | 400 gp | 10.50% | formula/ML-only |
| Sling Bullets of Althemone | Mythic Odysseys of Theros | Very Rare | Ammunition | 4,836 gp | 4,333 gp | -503 gp | -10.40% | formula/ML-only |
| Scroll of Spell Power | Monsters of Drakkenheim | Uncommon | Scroll | 665 gp | 734 gp | 69 gp | 10.39% | formula/ML-only |
| Mithral +1 Chain Mail | Acquisitions Incorporated | Rare | Heavy Armor | 3,865 gp | 4,265 gp | 400 gp | 10.35% | formula/ML-only |
| Thunderbuss | Bigby Presents: Glory of the Giants | Very Rare | Ranged Weapon | 4,567 gp | 5,019 gp | 452 gp | 9.90% | formula/ML-only |
| Hazirawn | Hoard of the Dragon Queen | Legendary | Melee Weapon | 102,877 gp | 92,835 gp | -10,042 gp | -9.76% | formula/ML-only |
| Final Messenger | Exploring Eberron (2024) | Uncommon | Wondrous Item | 1,835 gp | 2,014 gp | 179 gp | 9.75% | formula/ML-only |
| Mithral +1 Splint Armor | Acquisitions Incorporated | Rare | Heavy Armor | 4,140 gp | 4,540 gp | 400 gp | 9.66% | formula/ML-only |
| Skyblinder Staff | Guildmasters' Guide to Ravnica | Uncommon | Wondrous Item | 656 gp | 593 gp | -63 gp | -9.57% | formula/ML-only |
| Infiltrator's Key (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 84,117 gp | 92,052 gp | 7,935 gp | 9.43% | formula/ML-only |
| Ring of Obscuring | Explorer's Guide to Wildemount | Uncommon | Ring | 279 gp | 253 gp | -26 gp | -9.32% | reference-anchored |
| Demon Skin Splint Armor | Descent into the Lost Caverns of Tsojcanth | Rare | Heavy Armor | 4,050 gp | 4,410 gp | 360 gp | 8.89% | formula/ML-only |
| Demon Skin Ring Mail | Descent into the Lost Caverns of Tsojcanth | Rare | Heavy Armor | 3,686 gp | 4,012 gp | 326 gp | 8.85% | formula/ML-only |
| Demon Skin Chain Mail | Descent into the Lost Caverns of Tsojcanth | Rare | Heavy Armor | 4,027 gp | 4,380 gp | 353 gp | 8.77% | formula/ML-only |
| Duskcrusher | Explorer's Guide to Wildemount | Very Rare | Melee Weapon | 16,414 gp | 17,717 gp | 1,303 gp | 7.94% | formula/ML-only |

## Anchor-tier transitions / ML R² / double-count audit

- Anchor-tier transition and ML R² checks require pipeline metadata not present in final CSV snapshots; add those columns to future candidate snapshots if needed.
- Use the known-good and reference-anchored sections above as the first-pass double-count audit for extraction-driven price creep.
- Formula exposure reports (for example, extra_damage impact) are not final-price deltas.
