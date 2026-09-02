# Price Creep Guardrail

Baseline CSV: `output/pricing_guide.csv`
Candidate CSV: `output/pricing_guide_candidate.csv`

## Input row matching

- Common rows: 11940
- New candidate rows: 1
- Missing candidate rows: 1

## Aggregate final-price drift

- Median % drift: 0.00%
- Mean % drift: 2.27%
- Median gp drift: 0 gp
- Mean gp drift: -633 gp
- Rows >5% drift: 2652
- Rows >10% drift: 1917
- Rows >25% drift: 1008

## Reference anchored vs formula/ML-only

| Split | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| formula/ML-only | 9407 | 0.00% | 2.82% | 0 gp | -805 gp |
| reference-anchored | 2533 | 0.00% | 0.24% | 0 gp | 3 gp |

## Drift by rarity

| Rarity | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Rare | 3679 | 0.00% | -3.77% | 0 gp | -569 gp |
| Uncommon | 2635 | 0.00% | 1.37% | 0 gp | -71 gp |
| Very Rare | 2267 | 0.00% | -3.28% | 0 gp | -1,181 gp |
| Legendary | 1465 | 0.00% | 0.18% | 0 gp | -669 gp |
| Common | 939 | 0.00% | 8.00% | 0 gp | -7 gp |
| Mundane | 806 | 0.00% | 37.10% | 0 gp | -6 gp |
| Artifact | 102 | 0.00% | -4.20% | 0 gp | -15,548 gp |
| Unknown Magic | 31 | 0.43% | 258.69% | 1 gp | 759 gp |
| Varies | 12 | -25.00% | -38.68% | -375 gp | -4,321 gp |
| Unknown | 4 | 0.00% | 0.00% | 0 gp | 0 gp |

## Drift by type

| Type | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Melee Weapon | 5792 | 0.00% | -0.61% | 0 gp | -406 gp |
| Ranged Weapon | 1775 | 0.00% | -3.05% | 0 gp | -401 gp |
| Wondrous Item | 1591 | -0.79% | 13.52% | -1 gp | -1,475 gp |
| Medium Armor | 353 | 0.00% | -5.39% | 0 gp | -1,468 gp |
| Potion | 338 | -0.46% | 9.70% | -4 gp | -37 gp |
| Ammunition | 285 | 0.00% | 0.03% | 0 gp | 1 gp |
| Heavy Armor | 256 | 0.00% | -5.42% | 0 gp | -1,239 gp |
| Adventuring Gear | 227 | 0.00% | 43.74% | 0 gp | -21 gp |
| Light Armor | 176 | 0.00% | -7.22% | 0 gp | -1,882 gp |
| Spellcasting Focus | 146 | 0.00% | -2.66% | 0 gp | -1,704 gp |
| Ring | 136 | 0.82% | -3.34% | 8 gp | -697 gp |
| Ingred | 135 | -1.02% | -0.15% | -1 gp | -1 gp |
| Shield | 81 | -1.31% | 7.17% | -5 gp | -1,365 gp |
| Wand | 75 | -3.39% | -20.01% | -239 gp | -3,741 gp |
| Artisan's Tools | 72 | 0.00% | -0.13% | 0 gp | 2 gp |
| Rod | 54 | -0.65% | -7.04% | -46 gp | -4,249 gp |
| $A | 53 | 0.00% | 0.00% | 0 gp | 0 gp |
| $G | 52 | 0.00% | 0.00% | 0 gp | 0 gp |
| Musical Instrument | 49 | 0.00% | 2.65% | 0 gp | -445 gp |
| Scroll | 41 | 0.00% | -2.69% | 0 gp | -317 gp |

## Drift by source

| Source | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Dungeon Master's Guide (2024) | 3065 | 0.00% | -0.82% | 0 gp | -133 gp |
| The Griffon's Saddlebag: Book One | 897 | 0.00% | 0.57% | 0 gp | -741 gp |
| The Griffon's Saddlebag: Book Two | 633 | 0.00% | 8.39% | 0 gp | -997 gp |
| Obojima: Tales from the Tall Grass | 616 | 0.00% | -8.75% | 0 gp | -2,123 gp |
| Monsters of Drakkenheim | 526 | -4.63% | -6.06% | -774 gp | -702 gp |
| Heliana's Guide to Monster Hunting | 501 | 0.00% | -2.00% | 0 gp | -517 gp |
| Call from the Deep | 483 | 0.00% | 0.87% | 0 gp | 51 gp |
| Fizban's Treasury of Dragons | 470 | 0.25% | -1.18% | 89 gp | 22 gp |
| The Illrigger Revised | 437 | 0.00% | 0.83% | 0 gp | 16 gp |
| Exploring Eberron (2024) | 411 | 0.00% | 6.35% | 0 gp | 249 gp |
| Monster Manual | 368 | 0.31% | 1.26% | 10 gp | 10 gp |
| Explorer's Guide to Wildemount | 322 | -3.34% | -8.26% | -155 gp | -902 gp |
| Grim Hollow: Campaign Guide (2024/Transformed) | 300 | 0.00% | -0.97% | 0 gp | -1,909 gp |
| The Book of Many Things | 292 | 0.00% | -22.02% | 0 gp | -6,199 gp |
| Player's Handbook (2024) | 217 | 0.00% | 0.00% | 0 gp | 0 gp |
| Frontiers of Eberron: Quickstone | 184 | 0.00% | 38.50% | 0 gp | 517 gp |
| Where Evil Lives: The MCDM Book of Boss Battles | 151 | 0.00% | 199.82% | 0 gp | -233 gp |
| Acquisitions Incorporated | 141 | 0.57% | -2.88% | 4 gp | -287 gp |
| Eberron: Rising from the Last War | 139 | -0.96% | -7.55% | -1 gp | -66 gp |
| Critical Role: Call of the Netherdeep | 132 | 0.27% | -0.42% | 90 gp | -137 gp |

## Known-good anchors

Known-good status: **FAIL** (PASS ≤1% drift; REVIEW >1%; FAIL >5%).
Configured anchors include Holy Avenger, Defender, Vorpal Sword, +1/+2/+3 Weapon/Armor, Dragon Slayer, Giant Slayer, and Vicious Weapon families when present.

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Defender Cavalry Hammer | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 31,500 gp | 44,850 gp | 13,350 gp | 42.38% | reference-anchored |
| Defender Cavalry Pick | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 31,500 gp | 44,850 gp | 13,350 gp | 42.38% | reference-anchored |
| Defender Knightly Sword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 31,500 gp | 44,850 gp | 13,350 gp | 42.38% | reference-anchored |
| Defender Longsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 31,500 gp | 44,850 gp | 13,350 gp | 42.38% | reference-anchored |
| +3 True Name Repeater Needler | The Illrigger Revised | Legendary | Ranged Weapon | 2,437 gp | 8,000 gp | 5,563 gp | 228.29% | reference-anchored |
| Vicious Vertebrae Sword | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,231 gp | 17,642 gp | 3,411 gp | 23.97% | formula/ML-only |
| +3 Adamantine Repeater Needler | Call from the Deep | Very Rare | Ranged Weapon | 1,000 gp | 2,401 gp | 1,401 gp | 140.10% | reference-anchored |
| Vorpal Glaive | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 53,561 gp | 52,401 gp | -1,160 gp | -2.17% | reference-anchored |
| Vorpal Greatsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 53,561 gp | 52,401 gp | -1,160 gp | -2.17% | reference-anchored |
| Vorpal Longsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 53,561 gp | 52,401 gp | -1,160 gp | -2.17% | reference-anchored |
| Vorpal Scimitar | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 53,561 gp | 52,401 gp | -1,160 gp | -2.17% | reference-anchored |
| +3 Moon Sickle | Tasha's Cauldron of Everything | Very Rare | Melee Weapon | 31,905 gp | 32,674 gp | 769 gp | 2.41% | reference-anchored |
| +2 True Name Repeater Needler | The Illrigger Revised | Very Rare | Ranged Weapon | 581 gp | 1,000 gp | 419 gp | 72.02% | reference-anchored |
| +3 Cavalry Flail | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 14,579 gp | 14,222 gp | -357 gp | -2.45% | reference-anchored |
| Werydd Giantsbane's Giant Slayer Greataxe | Call from the Deep | Rare | Melee Weapon | 8,104 gp | 8,302 gp | 198 gp | 2.44% | formula/ML-only |
| +2 Moon Sickle | Tasha's Cauldron of Everything | Rare | Melee Weapon | 12,111 gp | 12,265 gp | 153 gp | 1.27% | reference-anchored |
| +3 Breastplate | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,680 gp | 29,529 gp | -151 gp | -0.51% | reference-anchored |
| +3 Chain Shirt | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,680 gp | 29,529 gp | -151 gp | -0.51% | reference-anchored |
| +3 Half Plate Armor | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,680 gp | 29,529 gp | -151 gp | -0.51% | reference-anchored |
| +3 Hide Armor | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,680 gp | 29,529 gp | -151 gp | -0.51% | reference-anchored |

## Artifact/legendary movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| The Griffon's Saddlebag | The Griffon's Saddlebag: Book One | Artifact | Wondrous Item | 440,423 gp | 250,000 gp | -190,423 gp | -43.24% | formula/ML-only |
| Morath, Scepter of the Soul Vortex | The Griffon's Saddlebag: Book Two | Artifact | Rod | 391,419 gp | 250,000 gp | -141,419 gp | -36.13% | formula/ML-only |
| Guardian's Reliquary | The Griffon's Saddlebag: Book Two | Legendary | Wondrous Item | 203,831 gp | 77,590 gp | -126,241 gp | -61.93% | formula/ML-only |
| Nimbus, First Staff of the Thunderbirds | The Griffon's Saddlebag: Book Two | Artifact | Spellcasting Focus | 368,936 gp | 250,000 gp | -118,936 gp | -32.24% | formula/ML-only |
| Ardor | Grim Hollow: Player Pack | Artifact | Melee Weapon | 440,420 gp | 338,200 gp | -102,220 gp | -23.21% | formula/ML-only |
| Zeal | Grim Hollow: Player Pack | Artifact | Melee Weapon | 440,420 gp | 338,200 gp | -102,220 gp | -23.21% | formula/ML-only |
| Ardor | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Melee Weapon | 444,771 gp | 349,866 gp | -94,905 gp | -21.34% | formula/ML-only |
| Zeal | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Melee Weapon | 444,771 gp | 349,866 gp | -94,905 gp | -21.34% | formula/ML-only |
| Arista, Wand of the Spire | The Griffon's Saddlebag: Book Two | Artifact | Wand | 353,546 gp | 259,649 gp | -93,896 gp | -26.56% | formula/ML-only |
| Indorius's Crown (Adept) | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Wondrous Item | 339,758 gp | 250,000 gp | -89,758 gp | -26.42% | formula/ML-only |
| Indorius's Crown (Aspirant) | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Wondrous Item | 339,758 gp | 250,000 gp | -89,758 gp | -26.42% | formula/ML-only |
| Indorius's Crown (Master) | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Wondrous Item | 339,758 gp | 250,000 gp | -89,758 gp | -26.42% | formula/ML-only |
| Ascendant Dragon-Touched Focus | Fizban's Treasury of Dragons | Legendary | Spellcasting Focus | 137,308 gp | 58,537 gp | -78,770 gp | -57.37% | formula/ML-only |
| Spire of Conflux (Exalted) | Tal'Dorei Campaign Setting Reborn | Legendary | Melee Weapon | 142,861 gp | 67,223 gp | -75,638 gp | -52.94% | formula/ML-only |
| Graz'tchar, the Decadent End | Tal'Dorei Campaign Setting Reborn | Legendary | Melee Weapon | 137,886 gp | 63,042 gp | -74,843 gp | -54.28% | formula/ML-only |
| Precipit, the Formless | The Griffon's Saddlebag: Book One | Artifact | Melee Weapon | 404,955 gp | 338,984 gp | -65,972 gp | -16.29% | formula/ML-only |
| Shaarat'doovol, the Blade of Truth | Exploring Eberron (2024) | Legendary | Melee Weapon | 268,190 gp | 203,373 gp | -64,817 gp | -24.17% | formula/ML-only |
| Luck Greatsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 228,170 gp | 168,858 gp | -59,313 gp | -25.99% | formula/ML-only |
| Azuredge | Waterdeep: Dragon Heist | Legendary | Melee Weapon | 84,964 gp | 142,710 gp | 57,746 gp | 67.96% | formula/ML-only |
| Luck Glaive | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 220,283 gp | 163,021 gp | -57,262 gp | -25.99% | formula/ML-only |

## Largest movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| The Griffon's Saddlebag | The Griffon's Saddlebag: Book One | Artifact | Wondrous Item | 440,423 gp | 250,000 gp | -190,423 gp | -43.24% | formula/ML-only |
| Morath, Scepter of the Soul Vortex | The Griffon's Saddlebag: Book Two | Artifact | Rod | 391,419 gp | 250,000 gp | -141,419 gp | -36.13% | formula/ML-only |
| Guardian's Reliquary | The Griffon's Saddlebag: Book Two | Legendary | Wondrous Item | 203,831 gp | 77,590 gp | -126,241 gp | -61.93% | formula/ML-only |
| Nimbus, First Staff of the Thunderbirds | The Griffon's Saddlebag: Book Two | Artifact | Spellcasting Focus | 368,936 gp | 250,000 gp | -118,936 gp | -32.24% | formula/ML-only |
| Ardor | Grim Hollow: Player Pack | Artifact | Melee Weapon | 440,420 gp | 338,200 gp | -102,220 gp | -23.21% | formula/ML-only |
| Zeal | Grim Hollow: Player Pack | Artifact | Melee Weapon | 440,420 gp | 338,200 gp | -102,220 gp | -23.21% | formula/ML-only |
| Ardor | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Melee Weapon | 444,771 gp | 349,866 gp | -94,905 gp | -21.34% | formula/ML-only |
| Zeal | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Melee Weapon | 444,771 gp | 349,866 gp | -94,905 gp | -21.34% | formula/ML-only |
| Arista, Wand of the Spire | The Griffon's Saddlebag: Book Two | Artifact | Wand | 353,546 gp | 259,649 gp | -93,896 gp | -26.56% | formula/ML-only |
| Indorius's Crown (Adept) | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Wondrous Item | 339,758 gp | 250,000 gp | -89,758 gp | -26.42% | formula/ML-only |
| Indorius's Crown (Aspirant) | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Wondrous Item | 339,758 gp | 250,000 gp | -89,758 gp | -26.42% | formula/ML-only |
| Indorius's Crown (Master) | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Wondrous Item | 339,758 gp | 250,000 gp | -89,758 gp | -26.42% | formula/ML-only |
| Ascendant Dragon-Touched Focus | Fizban's Treasury of Dragons | Legendary | Spellcasting Focus | 137,308 gp | 58,537 gp | -78,770 gp | -57.37% | formula/ML-only |
| Spire of Conflux (Exalted) | Tal'Dorei Campaign Setting Reborn | Legendary | Melee Weapon | 142,861 gp | 67,223 gp | -75,638 gp | -52.94% | formula/ML-only |
| Graz'tchar, the Decadent End | Tal'Dorei Campaign Setting Reborn | Legendary | Melee Weapon | 137,886 gp | 63,042 gp | -74,843 gp | -54.28% | formula/ML-only |
| Precipit, the Formless | The Griffon's Saddlebag: Book One | Artifact | Melee Weapon | 404,955 gp | 338,984 gp | -65,972 gp | -16.29% | formula/ML-only |
| Shaarat'doovol, the Blade of Truth | Exploring Eberron (2024) | Legendary | Melee Weapon | 268,190 gp | 203,373 gp | -64,817 gp | -24.17% | formula/ML-only |
| Luck Greatsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 228,170 gp | 168,858 gp | -59,313 gp | -25.99% | formula/ML-only |
| Azuredge | Waterdeep: Dragon Heist | Legendary | Melee Weapon | 84,964 gp | 142,710 gp | 57,746 gp | 67.96% | formula/ML-only |
| Luck Glaive | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 220,283 gp | 163,021 gp | -57,262 gp | -25.99% | formula/ML-only |
| Axe of the Galloping Headsman (Legendary) | The Crooked Moon | Legendary | Melee Weapon | 87,530 gp | 143,130 gp | 55,600 gp | 63.52% | formula/ML-only |
| Coldrazor | Grim Hollow: Campaign Guide (2024/Transformed) | Legendary | Melee Weapon | 87,530 gp | 143,083 gp | 55,553 gp | 63.47% | formula/ML-only |
| Luck Longsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 210,330 gp | 155,655 gp | -54,675 gp | -25.99% | formula/ML-only |
| Shroud of Ending | Humblewood Tales | Artifact | Wondrous Item | 330,628 gp | 276,678 gp | -53,950 gp | -16.32% | formula/ML-only |
| Luck Rapier | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 204,508 gp | 151,346 gp | -53,162 gp | -25.99% | formula/ML-only |

## Largest percent movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Kiona's Notes | Where Evil Lives: The MCDM Book of Boss Battles | Mundane | Wondrous Item | 1 gp | 201 gp | 200 gp | 20000.00% | formula/ML-only |
| Book of Secrets | Where Evil Lives: The MCDM Book of Boss Battles | Mundane | Adventuring Gear | 1 gp | 101 gp | 100 gp | 10000.00% | formula/ML-only |
| Whispergust Mote | The Griffon's Saddlebag: Book Two | Common | Wondrous Item | 121 gp | 7,412 gp | 7,291 gp | 6033.86% | formula/ML-only |
| Suude (Blue) | Tal'Dorei Campaign Setting Reborn | Unknown Magic | IDG | 292 gp | 6,855 gp | 6,564 gp | 2249.94% | formula/ML-only |
| Suude (Brown) | Tal'Dorei Campaign Setting Reborn | Unknown Magic | IDG | 292 gp | 6,855 gp | 6,564 gp | 2249.94% | formula/ML-only |
| Suude (Red) | Tal'Dorei Campaign Setting Reborn | Unknown Magic | IDG | 292 gp | 6,855 gp | 6,564 gp | 2249.94% | formula/ML-only |
| Mind Flayer Skull | Waterdeep: Dungeon of the Mad Mage | Unknown Magic | Other | 292 gp | 3,093 gp | 2,801 gp | 960.22% | formula/ML-only |
| Shield of Swans | Book of Ebon Tides | Common | Shield | 406 gp | 3,939 gp | 3,534 gp | 871.17% | formula/ML-only |
| Secret Path | Obojima: Tales from the Tall Grass | Common | Potion | 78 gp | 674 gp | 596 gp | 767.27% | formula/ML-only |
| Staff of the Dream Shepherd | The Griffon's Saddlebag: Book Two | Uncommon | Wondrous Item | 729 gp | 5,987 gp | 5,257 gp | 720.68% | formula/ML-only |
| Unknown Elixir | Obojima: Tales from the Tall Grass | Uncommon | Potion | 429 gp | 3,267 gp | 2,838 gp | 661.19% | formula/ML-only |
| Orostead Iced Tea (Common) | The Griffon's Saddlebag: Book Two | Common | Potion | 127 gp | 959 gp | 832 gp | 653.24% | formula/ML-only |
| Couatl Herald's Lash | The Griffon's Saddlebag: Book One | Rare | Melee Weapon | 657 gp | 4,804 gp | 4,147 gp | 631.07% | formula/ML-only |
| Snugglebeast (Owlbear) | The Griffon's Saddlebag: Book One | Common | Wondrous Item | 116 gp | 626 gp | 511 gp | 441.74% | formula/ML-only |
| Cottage Chest | The Griffon's Saddlebag: Book Two | Rare | Wondrous Item | 3,533 gp | 17,856 gp | 14,322 gp | 405.33% | formula/ML-only |
| Couatl Herald's Mantle | The Griffon's Saddlebag: Book One | Uncommon | Wondrous Item | 729 gp | 3,520 gp | 2,790 gp | 382.53% | formula/ML-only |
| Indigo Painted Stone | Tales from the Shadows | Uncommon | Wondrous Item | 853 gp | 3,697 gp | 2,845 gp | 333.60% | formula/ML-only |
| Cleaning Cube | The Griffon's Saddlebag: Book Two | Common | Wondrous Item | 121 gp | 522 gp | 401 gp | 332.14% | formula/ML-only |
| Slumbering Dragon's Wrath Vertebrae Sword | Fizban's Treasury of Dragons | Uncommon | Melee Weapon | 894 gp | 3,786 gp | 2,892 gp | 323.46% | formula/ML-only |
| Bird of a Feather (Common) | The Griffon's Saddlebag: Book One | Common | Wondrous Item | 116 gp | 478 gp | 363 gp | 313.66% | formula/ML-only |
| Vanisher Hat | Tome of Beasts 1 (2023 Edition) | Uncommon | Wondrous Item | 958 gp | 3,897 gp | 2,939 gp | 306.77% | formula/ML-only |
| Talons of the Squall | Humblewood Tales | Uncommon | Wondrous Item | 1,053 gp | 4,274 gp | 3,222 gp | 306.06% | formula/ML-only |
| Jade Serpent Staff | Waterdeep: Dungeon of the Mad Mage | Unknown Magic | Other | 292 gp | 1,080 gp | 789 gp | 270.37% | formula/ML-only |
| Sky Swimming | Obojima: Tales from the Tall Grass | Common | Potion | 78 gp | 275 gp | 198 gp | 254.42% | formula/ML-only |
| Wispy Sour (Common) | The Griffon's Saddlebag: Book Two | Common | Potion | 78 gp | 275 gp | 198 gp | 254.42% | formula/ML-only |

## Anchor-tier transitions / ML R² / double-count audit

- Anchor-tier transition and ML R² checks require pipeline metadata not present in final CSV snapshots; add those columns to future candidate snapshots if needed.
- Use the known-good and reference-anchored sections above as the first-pass double-count audit for extraction-driven price creep.
- Formula exposure reports (for example, extra_damage impact) are not final-price deltas.
