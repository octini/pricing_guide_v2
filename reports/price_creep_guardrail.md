# Price Creep Guardrail

Baseline CSV: `output/pricing_guide.csv`
Candidate CSV: `output/pricing_guide_candidate.csv`

## Input row matching

- Common rows: 11940
- New candidate rows: 1
- Missing candidate rows: 1

## Aggregate final-price drift

- Median % drift: 0.00%
- Mean % drift: 262.49%
- Median gp drift: 0 gp
- Mean gp drift: 432 gp
- Rows >5% drift: 3882
- Rows >10% drift: 3110
- Rows >25% drift: 1999

## Reference anchored vs formula/ML-only

| Split | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| formula/ML-only | 9407 | 0.00% | 319.58% | 0 gp | -727 gp |
| reference-anchored | 2533 | 2.21% | 50.48% | 64 gp | 4,737 gp |

## Drift by rarity

| Rarity | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Rare | 3679 | 0.00% | 498.12% | 0 gp | -522 gp |
| Uncommon | 2635 | 0.00% | 7.89% | 0 gp | -66 gp |
| Very Rare | 2267 | 0.00% | 103.31% | 0 gp | 788 gp |
| Legendary | 1465 | 0.00% | 683.52% | 0 gp | 4,841 gp |
| Common | 939 | 0.00% | 8.00% | 0 gp | -7 gp |
| Mundane | 806 | 0.00% | 37.10% | 0 gp | -6 gp |
| Artifact | 102 | 0.00% | -4.20% | 0 gp | -15,548 gp |
| Unknown Magic | 31 | 0.43% | 279.92% | 1 gp | 821 gp |
| Varies | 12 | -25.00% | -38.68% | -375 gp | -4,321 gp |
| Unknown | 4 | 0.00% | 0.00% | 0 gp | 0 gp |

## Drift by type

| Type | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Melee Weapon | 5792 | 0.00% | 16.01% | 0 gp | 1,267 gp |
| Ranged Weapon | 1775 | 0.00% | 58.52% | 0 gp | 988 gp |
| Wondrous Item | 1591 | -0.79% | 1836.03% | -1 gp | -1,122 gp |
| Medium Armor | 353 | 0.00% | -5.39% | 0 gp | -1,468 gp |
| Potion | 338 | -0.46% | 13.31% | -4 gp | -21 gp |
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
| Dungeon Master's Guide (2024) | 3065 | 0.00% | 6.03% | 0 gp | 639 gp |
| The Griffon's Saddlebag: Book One | 897 | 0.00% | 659.89% | 0 gp | 964 gp |
| The Griffon's Saddlebag: Book Two | 633 | 0.00% | 237.13% | 0 gp | -850 gp |
| Obojima: Tales from the Tall Grass | 616 | 0.00% | -6.77% | 0 gp | -2,114 gp |
| Monsters of Drakkenheim | 526 | -4.63% | -6.01% | -774 gp | -695 gp |
| Heliana's Guide to Monster Hunting | 501 | 0.00% | 4256.01% | 0 gp | -382 gp |
| Call from the Deep | 483 | 0.00% | 200.99% | 0 gp | 3,793 gp |
| Fizban's Treasury of Dragons | 470 | 0.25% | -1.18% | 89 gp | 22 gp |
| The Illrigger Revised | 437 | 33.21% | 69.26% | 450 gp | 6,068 gp |
| Exploring Eberron (2024) | 411 | 0.00% | 6.44% | 0 gp | 250 gp |
| Monster Manual | 368 | 99.07% | 102.13% | 3,384 gp | 10,054 gp |
| Explorer's Guide to Wildemount | 322 | -3.34% | -8.26% | -155 gp | -902 gp |
| Grim Hollow: Campaign Guide (2024/Transformed) | 300 | 0.00% | -0.73% | 0 gp | -1,901 gp |
| The Book of Many Things | 292 | 0.00% | -21.79% | 0 gp | -6,194 gp |
| Player's Handbook (2024) | 217 | 0.00% | 0.00% | 0 gp | 0 gp |
| Frontiers of Eberron: Quickstone | 184 | 0.00% | 38.50% | 0 gp | 517 gp |
| Where Evil Lives: The MCDM Book of Boss Battles | 151 | 0.00% | 199.83% | 0 gp | -233 gp |
| Acquisitions Incorporated | 141 | 0.57% | -1.34% | 4 gp | -286 gp |
| Eberron: Rising from the Last War | 139 | -0.96% | -7.55% | -1 gp | -66 gp |
| Critical Role: Call of the Netherdeep | 132 | 0.27% | -0.42% | 90 gp | -137 gp |

## Known-good anchors

Known-good status: **FAIL** (PASS ≤1% drift; REVIEW >1%; FAIL >5%).
Configured anchors include Holy Avenger, Defender, Vorpal Sword, +1/+2/+3 Weapon/Armor, Dragon Slayer, Giant Slayer, and Vicious Weapon families when present.

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| +3 True Name Repeater Needler | The Illrigger Revised | Legendary | Ranged Weapon | 2,437 gp | 35,880 gp | 33,443 gp | 1372.39% | reference-anchored |
| +3 Adamantine Repeater Needler | Call from the Deep | Very Rare | Ranged Weapon | 1,000 gp | 29,900 gp | 28,900 gp | 2890.00% | reference-anchored |
| +3 True Name Dart | The Illrigger Revised | Legendary | Ranged Weapon | 7,950 gp | 35,880 gp | 27,930 gp | 351.32% | reference-anchored |
| +3 Dragonkin Brass Knuckles | The Griffon's Saddlebag: Book One | Legendary | Melee Weapon | 8,097 gp | 35,880 gp | 27,783 gp | 343.13% | reference-anchored |
| +3 Dragonkin Chakram | The Griffon's Saddlebag: Book One | Legendary | Melee Weapon | 8,097 gp | 35,880 gp | 27,783 gp | 343.13% | reference-anchored |
| +3 Dragonkin Dagger | The Griffon's Saddlebag: Book One | Legendary | Melee Weapon | 8,097 gp | 35,880 gp | 27,783 gp | 343.13% | reference-anchored |
| +3 Dragonkin Parrying Dagger | The Griffon's Saddlebag: Book One | Legendary | Melee Weapon | 8,097 gp | 35,880 gp | 27,783 gp | 343.13% | reference-anchored |
| +3 Dragonkin Punching Dagger | The Griffon's Saddlebag: Book One | Legendary | Melee Weapon | 8,097 gp | 35,880 gp | 27,783 gp | 343.13% | reference-anchored |
| +3 Repeater Needler | Dungeon Master's Guide (2024) | Very Rare | Ranged Weapon | 2,412 gp | 29,900 gp | 27,488 gp | 1139.54% | reference-anchored |
| +3 Dragonkin Club | The Griffon's Saddlebag: Book One | Legendary | Melee Weapon | 9,831 gp | 35,880 gp | 26,049 gp | 264.98% | reference-anchored |
| +3 Dragonkin Hand Claws | The Griffon's Saddlebag: Book One | Legendary | Melee Weapon | 9,831 gp | 35,880 gp | 26,049 gp | 264.98% | reference-anchored |
| +3 Dragonkin Handaxe | The Griffon's Saddlebag: Book One | Legendary | Melee Weapon | 9,831 gp | 35,880 gp | 26,049 gp | 264.98% | reference-anchored |
| +3 Dragonkin Javelin | The Griffon's Saddlebag: Book One | Legendary | Melee Weapon | 9,831 gp | 35,880 gp | 26,049 gp | 264.98% | reference-anchored |
| +3 Dragonkin Light Hammer | The Griffon's Saddlebag: Book One | Legendary | Melee Weapon | 9,831 gp | 35,880 gp | 26,049 gp | 264.98% | reference-anchored |
| +3 Dragonkin Returning Club | The Griffon's Saddlebag: Book One | Legendary | Melee Weapon | 9,831 gp | 35,880 gp | 26,049 gp | 264.98% | reference-anchored |
| +3 Dragonkin Shortsword | The Griffon's Saddlebag: Book One | Legendary | Melee Weapon | 9,831 gp | 35,880 gp | 26,049 gp | 264.98% | reference-anchored |
| +3 Dragonkin Sickle | The Griffon's Saddlebag: Book One | Legendary | Melee Weapon | 9,831 gp | 35,880 gp | 26,049 gp | 264.98% | reference-anchored |
| +3 Dragonkin Side-handle Baton | The Griffon's Saddlebag: Book One | Legendary | Melee Weapon | 9,831 gp | 35,880 gp | 26,049 gp | 264.98% | reference-anchored |
| +3 True Name Bellow Flute | The Illrigger Revised | Legendary | Melee Weapon | 10,237 gp | 35,880 gp | 25,643 gp | 250.48% | reference-anchored |
| +3 True Name Boomerang | The Illrigger Revised | Legendary | Melee Weapon | 10,237 gp | 35,880 gp | 25,643 gp | 250.48% | reference-anchored |

## Artifact/legendary movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| The Griffon's Saddlebag | The Griffon's Saddlebag: Book One | Artifact | Wondrous Item | 440,423 gp | 250,000 gp | -190,423 gp | -43.24% | formula/ML-only |
| Morath, Scepter of the Soul Vortex | The Griffon's Saddlebag: Book Two | Artifact | Rod | 391,419 gp | 250,000 gp | -141,419 gp | -36.13% | formula/ML-only |
| Guardian's Reliquary | The Griffon's Saddlebag: Book Two | Legendary | Wondrous Item | 203,831 gp | 77,590 gp | -126,241 gp | -61.93% | formula/ML-only |
| Nimbus, First Staff of the Thunderbirds | The Griffon's Saddlebag: Book Two | Artifact | Spellcasting Focus | 368,936 gp | 250,000 gp | -118,936 gp | -32.24% | formula/ML-only |
| Ardor | Grim Hollow: Player Pack | Artifact | Melee Weapon | 440,420 gp | 338,200 gp | -102,220 gp | -23.21% | formula/ML-only |
| Zeal | Grim Hollow: Player Pack | Artifact | Melee Weapon | 440,420 gp | 338,200 gp | -102,220 gp | -23.21% | formula/ML-only |
| Spell Gem (Diamond) | Out of the Abyss | Legendary | Wondrous Item | 5,000 gp | 100,000 gp | 95,000 gp | 1900.00% | formula/ML-only |
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

## Largest movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| The Griffon's Saddlebag | The Griffon's Saddlebag: Book One | Artifact | Wondrous Item | 440,423 gp | 250,000 gp | -190,423 gp | -43.24% | formula/ML-only |
| Morath, Scepter of the Soul Vortex | The Griffon's Saddlebag: Book Two | Artifact | Rod | 391,419 gp | 250,000 gp | -141,419 gp | -36.13% | formula/ML-only |
| Guardian's Reliquary | The Griffon's Saddlebag: Book Two | Legendary | Wondrous Item | 203,831 gp | 77,590 gp | -126,241 gp | -61.93% | formula/ML-only |
| Nimbus, First Staff of the Thunderbirds | The Griffon's Saddlebag: Book Two | Artifact | Spellcasting Focus | 368,936 gp | 250,000 gp | -118,936 gp | -32.24% | formula/ML-only |
| Ardor | Grim Hollow: Player Pack | Artifact | Melee Weapon | 440,420 gp | 338,200 gp | -102,220 gp | -23.21% | formula/ML-only |
| Zeal | Grim Hollow: Player Pack | Artifact | Melee Weapon | 440,420 gp | 338,200 gp | -102,220 gp | -23.21% | formula/ML-only |
| Spell Gem (Diamond) | Out of the Abyss | Legendary | Wondrous Item | 5,000 gp | 100,000 gp | 95,000 gp | 1900.00% | formula/ML-only |
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
| Shard Solitaire (Black Sapphire) | Keys from the Golden Vault | Legendary | Wondrous Item | 5,000 gp | 62,309 gp | 57,309 gp | 1146.19% | formula/ML-only |
| Shard Solitaire (Diamond) | Keys from the Golden Vault | Legendary | Wondrous Item | 5,000 gp | 62,309 gp | 57,309 gp | 1146.19% | formula/ML-only |
| Shard Solitaire (Jacinth) | Keys from the Golden Vault | Legendary | Wondrous Item | 5,000 gp | 62,309 gp | 57,309 gp | 1146.19% | formula/ML-only |
| Shard Solitaire (Ruby) | Keys from the Golden Vault | Legendary | Wondrous Item | 5,000 gp | 62,309 gp | 57,309 gp | 1146.19% | formula/ML-only |
| Luck Glaive | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 220,283 gp | 163,021 gp | -57,262 gp | -25.99% | formula/ML-only |

## Largest percent movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Wyrm's Breath Grenade (Copper) | Heliana's Guide to Monster Hunting | Rare | Wondrous Item | 0 gp | 5,868 gp | 5,868 gp | 1173546.00% | formula/ML-only |
| Wyrm's Breath Grenade (Silver) | Heliana's Guide to Monster Hunting | Legendary | Wondrous Item | 5 gp | 46,699 gp | 46,694 gp | 933880.60% | formula/ML-only |
| Snugglebeast (Dragon) | The Griffon's Saddlebag: Book One | Rare | Wondrous Item | 1 gp | 5,718 gp | 5,717 gp | 571684.00% | formula/ML-only |
| Masks of the Sacred Beasts (Mule) | The Griffon's Saddlebag: Book Two | Very Rare | Wondrous Item | 8 gp | 11,509 gp | 11,501 gp | 143757.50% | formula/ML-only |
| Moonbow (Shortbow) | Call from the Deep | Rare | Ranged Weapon | 25 gp | 12,561 gp | 12,536 gp | 50142.48% | formula/ML-only |
| Moonbow (Longbow) | Call from the Deep | Rare | Ranged Weapon | 50 gp | 13,539 gp | 13,489 gp | 26978.76% | formula/ML-only |
| Wyrm's Breath Grenade (Gold) | Heliana's Guide to Monster Hunting | Very Rare | Wondrous Item | 50 gp | 12,938 gp | 12,888 gp | 25776.86% | formula/ML-only |
| Kiona's Notes | Where Evil Lives: The MCDM Book of Boss Battles | Mundane | Wondrous Item | 1 gp | 201 gp | 200 gp | 20000.00% | formula/ML-only |
| Book of Secrets | Where Evil Lives: The MCDM Book of Boss Battles | Mundane | Adventuring Gear | 1 gp | 101 gp | 100 gp | 10000.00% | formula/ML-only |
| Spell Gem (Jade) | Out of the Abyss | Very Rare | Wondrous Item | 100 gp | 9,584 gp | 9,484 gp | 9484.09% | formula/ML-only |
| Spell Gem (Lapis lazuli) | Out of the Abyss | Uncommon | Wondrous Item | 10 gp | 765 gp | 755 gp | 7546.80% | formula/ML-only |
| Spell Gem (Obsidian) | Out of the Abyss | Uncommon | Wondrous Item | 10 gp | 765 gp | 755 gp | 7546.80% | formula/ML-only |
| Spell Gem (Bloodstone) | Out of the Abyss | Rare | Wondrous Item | 50 gp | 3,177 gp | 3,127 gp | 6254.82% | formula/ML-only |
| Spell Gem (Quartz) | Out of the Abyss | Rare | Wondrous Item | 50 gp | 3,177 gp | 3,127 gp | 6254.82% | formula/ML-only |
| Whispergust Mote | The Griffon's Saddlebag: Book Two | Common | Wondrous Item | 121 gp | 7,412 gp | 7,291 gp | 6033.86% | formula/ML-only |
| Spell Gem (Star ruby) | Out of the Abyss | Legendary | Wondrous Item | 1,000 gp | 38,692 gp | 37,692 gp | 3769.21% | formula/ML-only |
| +3 Adamantine Repeater Needler | Call from the Deep | Very Rare | Ranged Weapon | 1,000 gp | 29,900 gp | 28,900 gp | 2890.00% | reference-anchored |
| Suude (Blue) | Tal'Dorei Campaign Setting Reborn | Unknown Magic | IDG | 292 gp | 6,855 gp | 6,564 gp | 2249.94% | formula/ML-only |
| Suude (Brown) | Tal'Dorei Campaign Setting Reborn | Unknown Magic | IDG | 292 gp | 6,855 gp | 6,564 gp | 2249.94% | formula/ML-only |
| Suude (Red) | Tal'Dorei Campaign Setting Reborn | Unknown Magic | IDG | 292 gp | 6,855 gp | 6,564 gp | 2249.94% | formula/ML-only |
| Spell Gem (Diamond) | Out of the Abyss | Legendary | Wondrous Item | 5,000 gp | 100,000 gp | 95,000 gp | 1900.00% | formula/ML-only |
| Unknown Elixir | Obojima: Tales from the Tall Grass | Uncommon | Potion | 429 gp | 8,500 gp | 8,071 gp | 1880.61% | formula/ML-only |
| Spell Gem (Topaz) | Out of the Abyss | Very Rare | Wondrous Item | 500 gp | 9,584 gp | 9,084 gp | 1816.82% | formula/ML-only |
| Drow +3 Repeater Needler | Monster Manual | Legendary | Ranged Weapon | 2,502 gp | 44,850 gp | 42,348 gp | 1692.49% | reference-anchored |
| +3 True Name Repeater Needler | The Illrigger Revised | Legendary | Ranged Weapon | 2,437 gp | 35,880 gp | 33,443 gp | 1372.39% | reference-anchored |

## Anchor-tier transitions / ML R² / double-count audit

- Anchor-tier transition and ML R² checks require pipeline metadata not present in final CSV snapshots; add those columns to future candidate snapshots if needed.
- Use the known-good and reference-anchored sections above as the first-pass double-count audit for extraction-driven price creep.
- Formula exposure reports (for example, extra_damage impact) are not final-price deltas.
