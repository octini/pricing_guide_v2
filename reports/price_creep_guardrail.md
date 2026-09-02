# Price Creep Guardrail

Baseline CSV: `output/pricing_guide.csv`
Candidate CSV: `output/pricing_guide_candidate.csv`

## Input row matching

- Common rows: 11940
- New candidate rows: 1
- Missing candidate rows: 1

## Aggregate final-price drift

- Median % drift: 0.00%
- Mean % drift: 250.84%
- Median gp drift: 0 gp
- Mean gp drift: -622 gp
- Rows >5% drift: 2806
- Rows >10% drift: 2242
- Rows >25% drift: 1083

## Reference anchored vs formula/ML-only

| Split | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| formula/ML-only | 9407 | 0.00% | 318.36% | 0 gp | -782 gp |
| reference-anchored | 2533 | 0.00% | 0.05% | 0 gp | -26 gp |

## Drift by rarity

| Rarity | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Rare | 3679 | 0.00% | 501.84% | 0 gp | -541 gp |
| Uncommon | 2635 | 0.00% | 7.65% | 0 gp | -67 gp |
| Very Rare | 2267 | 0.00% | 76.45% | 0 gp | -1,260 gp |
| Legendary | 1465 | 0.00% | 619.83% | 0 gp | -533 gp |
| Common | 939 | 0.00% | 10.16% | 0 gp | -4 gp |
| Mundane | 806 | 0.00% | 37.10% | 0 gp | -6 gp |
| Artifact | 102 | 0.00% | -4.20% | 0 gp | -15,548 gp |
| Unknown Magic | 31 | -0.93% | 278.69% | -3 gp | 813 gp |
| Varies | 12 | -25.00% | -38.68% | -375 gp | -4,321 gp |
| Unknown | 4 | 0.00% | 0.00% | 0 gp | 0 gp |

## Drift by type

| Type | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Melee Weapon | 5792 | 0.00% | -1.42% | 0 gp | -487 gp |
| Ranged Weapon | 1775 | 0.00% | 39.86% | 0 gp | -411 gp |
| Wondrous Item | 1591 | 0.00% | 1831.85% | 0 gp | -1,156 gp |
| Medium Armor | 353 | 0.00% | -5.28% | 0 gp | -1,410 gp |
| Potion | 338 | -0.54% | 15.31% | -3 gp | -37 gp |
| Ammunition | 285 | 0.00% | -0.01% | 0 gp | -1 gp |
| Heavy Armor | 256 | 0.00% | -5.39% | 0 gp | -1,207 gp |
| Adventuring Gear | 227 | 0.00% | 43.68% | 0 gp | -26 gp |
| Light Armor | 176 | 0.00% | -7.04% | 0 gp | -1,730 gp |
| Spellcasting Focus | 146 | 0.00% | -3.32% | 0 gp | -1,770 gp |
| Ring | 136 | 0.92% | -3.02% | 15 gp | -738 gp |
| Ingred | 135 | 2.85% | 1.78% | 3 gp | 3 gp |
| Shield | 81 | 2.02% | 10.73% | 56 gp | -1,077 gp |
| Wand | 75 | -2.76% | -17.37% | -244 gp | -3,615 gp |
| Artisan's Tools | 72 | 0.00% | -0.11% | 0 gp | 2 gp |
| Rod | 54 | 0.00% | -1.38% | 0 gp | -3,254 gp |
| $A | 53 | 0.00% | 0.00% | 0 gp | 0 gp |
| $G | 52 | 0.00% | 0.00% | 0 gp | 0 gp |
| Musical Instrument | 49 | 0.00% | 2.00% | 0 gp | -435 gp |
| Scroll | 41 | 0.00% | -2.88% | 0 gp | -277 gp |

## Drift by source

| Source | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Dungeon Master's Guide (2024) | 3065 | 0.00% | -0.87% | 0 gp | -156 gp |
| The Griffon's Saddlebag: Book One | 897 | 0.00% | 660.39% | 0 gp | -763 gp |
| The Griffon's Saddlebag: Book Two | 633 | 0.00% | 232.97% | 0 gp | -1,033 gp |
| Obojima: Tales from the Tall Grass | 616 | 0.00% | -5.26% | 0 gp | -2,112 gp |
| Monsters of Drakkenheim | 526 | -4.64% | -6.26% | -774 gp | -810 gp |
| Heliana's Guide to Monster Hunting | 501 | 0.00% | 4189.28% | 0 gp | -434 gp |
| Call from the Deep | 483 | 0.00% | 160.21% | 0 gp | 98 gp |
| Fizban's Treasury of Dragons | 470 | 0.25% | -1.20% | 89 gp | 6 gp |
| The Illrigger Revised | 437 | 0.00% | 0.83% | 0 gp | 17 gp |
| Exploring Eberron (2024) | 411 | 0.00% | 6.69% | 0 gp | 266 gp |
| Monster Manual | 368 | -0.11% | 0.62% | -16 gp | -8 gp |
| Explorer's Guide to Wildemount | 322 | -3.35% | -8.36% | -155 gp | -913 gp |
| Grim Hollow: Campaign Guide (2024/Transformed) | 300 | 0.00% | -0.71% | 0 gp | -1,920 gp |
| The Book of Many Things | 292 | -43.53% | -28.34% | -2,998 gp | -6,775 gp |
| Player's Handbook (2024) | 217 | 0.00% | 0.00% | 0 gp | 0 gp |
| Frontiers of Eberron: Quickstone | 184 | 0.00% | 38.74% | 0 gp | 506 gp |
| Where Evil Lives: The MCDM Book of Boss Battles | 151 | -21.65% | 184.56% | -298 gp | -458 gp |
| Acquisitions Incorporated | 141 | 0.68% | -2.70% | 4 gp | -286 gp |
| Eberron: Rising from the Last War | 139 | 0.00% | -7.45% | 0 gp | -78 gp |
| Critical Role: Call of the Netherdeep | 132 | 0.27% | -0.25% | 90 gp | -127 gp |

## Known-good anchors

Known-good status: **FAIL** (5/1768 rows >5%, 54/1768 rows >1%; PASS ≤1% drift; REVIEW >1%; FAIL >5%).
Reference-anchored status: **FAIL** (74/2533 rows >5%, 551/2533 rows >1%; median 0.00%).
Configured anchors include Holy Avenger, Defender, Vorpal Sword, +1/+2/+3 Weapon/Armor, Dragon Slayer, Giant Slayer, and Vicious Weapon families when present.
Scope note: known-good status reflects the known-good anchor table honestly; reference-anchored is reported separately so a FAIL there does not mislabel the anchor table.

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| +3 True Name Repeater Needler | The Illrigger Revised | Legendary | Ranged Weapon | 2,437 gp | 8,000 gp | 5,563 gp | 228.29% | reference-anchored |
| Vicious Vertebrae Sword | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,231 gp | 17,642 gp | 3,411 gp | 23.97% | formula/ML-only |
| Vorpal Glaive | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 53,561 gp | 51,400 gp | -2,161 gp | -4.03% | reference-anchored |
| Vorpal Greatsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 53,561 gp | 51,400 gp | -2,161 gp | -4.03% | reference-anchored |
| Vorpal Longsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 53,561 gp | 51,400 gp | -2,161 gp | -4.03% | reference-anchored |
| Vorpal Scimitar | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 53,561 gp | 51,400 gp | -2,161 gp | -4.03% | reference-anchored |
| +3 Moon Sickle | Tasha's Cauldron of Everything | Very Rare | Melee Weapon | 31,905 gp | 32,467 gp | 561 gp | 1.76% | reference-anchored |
| +2 True Name Repeater Needler | The Illrigger Revised | Very Rare | Ranged Weapon | 581 gp | 1,000 gp | 419 gp | 72.02% | reference-anchored |
| Werydd Giantsbane's Giant Slayer Greataxe | Call from the Deep | Rare | Melee Weapon | 8,104 gp | 8,491 gp | 388 gp | 4.78% | formula/ML-only |
| +3 Leather Armor | Dungeon Master's Guide (2024) | Legendary | Light Armor | 29,744 gp | 29,534 gp | -209 gp | -0.70% | reference-anchored |
| +3 Padded Armor | Dungeon Master's Guide (2024) | Legendary | Light Armor | 29,744 gp | 29,534 gp | -209 gp | -0.70% | reference-anchored |
| +3 Studded Leather Armor | Dungeon Master's Guide (2024) | Legendary | Light Armor | 29,744 gp | 29,534 gp | -209 gp | -0.70% | reference-anchored |
| +2 Moon Sickle | Tasha's Cauldron of Everything | Rare | Melee Weapon | 12,111 gp | 12,292 gp | 181 gp | 1.49% | reference-anchored |
| +3 True Name Cavalry Flail | The Illrigger Revised | Legendary | Melee Weapon | 14,398 gp | 14,551 gp | 153 gp | 1.06% | reference-anchored |
| +3 True Name Cavalry Hammer | The Illrigger Revised | Legendary | Melee Weapon | 14,398 gp | 14,551 gp | 153 gp | 1.06% | reference-anchored |
| +3 True Name Cavalry Pick | The Illrigger Revised | Legendary | Melee Weapon | 14,398 gp | 14,551 gp | 153 gp | 1.06% | reference-anchored |
| +3 True Name Knightly Sword | The Illrigger Revised | Legendary | Melee Weapon | 14,398 gp | 14,551 gp | 153 gp | 1.06% | reference-anchored |
| +3 True Name Longsword | The Illrigger Revised | Legendary | Melee Weapon | 14,398 gp | 14,551 gp | 153 gp | 1.06% | reference-anchored |
| +3 True Name Yklwa | The Illrigger Revised | Legendary | Melee Weapon | 14,398 gp | 14,551 gp | 153 gp | 1.06% | reference-anchored |
| +2 Breastplate | Dungeon Master's Guide (2024) | Very Rare | Medium Armor | 8,448 gp | 8,564 gp | 116 gp | 1.37% | reference-anchored |

## Artifact/legendary movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| The Griffon's Saddlebag | The Griffon's Saddlebag: Book One | Artifact | Wondrous Item | 440,423 gp | 250,000 gp | -190,423 gp | -43.24% | formula/ML-only |
| Morath, Scepter of the Soul Vortex | The Griffon's Saddlebag: Book Two | Artifact | Rod | 391,419 gp | 250,000 gp | -141,419 gp | -36.13% | formula/ML-only |
| Nimbus, First Staff of the Thunderbirds | The Griffon's Saddlebag: Book Two | Artifact | Spellcasting Focus | 368,936 gp | 250,000 gp | -118,936 gp | -32.24% | formula/ML-only |
| Guardian's Reliquary | The Griffon's Saddlebag: Book Two | Legendary | Wondrous Item | 203,831 gp | 87,187 gp | -116,644 gp | -57.23% | formula/ML-only |
| Ardor | Grim Hollow: Player Pack | Artifact | Melee Weapon | 440,420 gp | 338,200 gp | -102,220 gp | -23.21% | formula/ML-only |
| Zeal | Grim Hollow: Player Pack | Artifact | Melee Weapon | 440,420 gp | 338,200 gp | -102,220 gp | -23.21% | formula/ML-only |
| Spell Gem (Diamond) | Out of the Abyss | Legendary | Wondrous Item | 5,000 gp | 100,000 gp | 95,000 gp | 1900.00% | formula/ML-only |
| Ardor | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Melee Weapon | 444,771 gp | 349,866 gp | -94,905 gp | -21.34% | formula/ML-only |
| Zeal | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Melee Weapon | 444,771 gp | 349,866 gp | -94,905 gp | -21.34% | formula/ML-only |
| Arista, Wand of the Spire | The Griffon's Saddlebag: Book Two | Artifact | Wand | 353,546 gp | 259,649 gp | -93,896 gp | -26.56% | formula/ML-only |
| Indorius's Crown (Adept) | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Wondrous Item | 339,758 gp | 250,000 gp | -89,758 gp | -26.42% | formula/ML-only |
| Indorius's Crown (Aspirant) | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Wondrous Item | 339,758 gp | 250,000 gp | -89,758 gp | -26.42% | formula/ML-only |
| Indorius's Crown (Master) | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Wondrous Item | 339,758 gp | 250,000 gp | -89,758 gp | -26.42% | formula/ML-only |
| Ascendant Dragon-Touched Focus | Fizban's Treasury of Dragons | Legendary | Spellcasting Focus | 137,308 gp | 58,093 gp | -79,214 gp | -57.69% | formula/ML-only |
| Spire of Conflux (Exalted) | Tal'Dorei Campaign Setting Reborn | Legendary | Melee Weapon | 142,861 gp | 63,848 gp | -79,013 gp | -55.31% | formula/ML-only |
| Graz'tchar, the Decadent End | Tal'Dorei Campaign Setting Reborn | Legendary | Melee Weapon | 137,886 gp | 61,050 gp | -76,835 gp | -55.72% | formula/ML-only |
| Shaarat'doovol, the Blade of Truth | Exploring Eberron (2024) | Legendary | Melee Weapon | 268,190 gp | 197,355 gp | -70,834 gp | -26.41% | formula/ML-only |
| Precipit, the Formless | The Griffon's Saddlebag: Book One | Artifact | Melee Weapon | 404,955 gp | 338,984 gp | -65,972 gp | -16.29% | formula/ML-only |
| Shard Solitaire (Black Sapphire) | Keys from the Golden Vault | Legendary | Wondrous Item | 5,000 gp | 69,422 gp | 64,422 gp | 1288.43% | formula/ML-only |
| Shard Solitaire (Diamond) | Keys from the Golden Vault | Legendary | Wondrous Item | 5,000 gp | 69,422 gp | 64,422 gp | 1288.43% | formula/ML-only |

## Largest movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| The Griffon's Saddlebag | The Griffon's Saddlebag: Book One | Artifact | Wondrous Item | 440,423 gp | 250,000 gp | -190,423 gp | -43.24% | formula/ML-only |
| Morath, Scepter of the Soul Vortex | The Griffon's Saddlebag: Book Two | Artifact | Rod | 391,419 gp | 250,000 gp | -141,419 gp | -36.13% | formula/ML-only |
| Nimbus, First Staff of the Thunderbirds | The Griffon's Saddlebag: Book Two | Artifact | Spellcasting Focus | 368,936 gp | 250,000 gp | -118,936 gp | -32.24% | formula/ML-only |
| Guardian's Reliquary | The Griffon's Saddlebag: Book Two | Legendary | Wondrous Item | 203,831 gp | 87,187 gp | -116,644 gp | -57.23% | formula/ML-only |
| Ardor | Grim Hollow: Player Pack | Artifact | Melee Weapon | 440,420 gp | 338,200 gp | -102,220 gp | -23.21% | formula/ML-only |
| Zeal | Grim Hollow: Player Pack | Artifact | Melee Weapon | 440,420 gp | 338,200 gp | -102,220 gp | -23.21% | formula/ML-only |
| Spell Gem (Diamond) | Out of the Abyss | Legendary | Wondrous Item | 5,000 gp | 100,000 gp | 95,000 gp | 1900.00% | formula/ML-only |
| Ardor | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Melee Weapon | 444,771 gp | 349,866 gp | -94,905 gp | -21.34% | formula/ML-only |
| Zeal | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Melee Weapon | 444,771 gp | 349,866 gp | -94,905 gp | -21.34% | formula/ML-only |
| Arista, Wand of the Spire | The Griffon's Saddlebag: Book Two | Artifact | Wand | 353,546 gp | 259,649 gp | -93,896 gp | -26.56% | formula/ML-only |
| Indorius's Crown (Adept) | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Wondrous Item | 339,758 gp | 250,000 gp | -89,758 gp | -26.42% | formula/ML-only |
| Indorius's Crown (Aspirant) | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Wondrous Item | 339,758 gp | 250,000 gp | -89,758 gp | -26.42% | formula/ML-only |
| Indorius's Crown (Master) | Grim Hollow: Campaign Guide (2024/Transformed) | Artifact | Wondrous Item | 339,758 gp | 250,000 gp | -89,758 gp | -26.42% | formula/ML-only |
| Ascendant Dragon-Touched Focus | Fizban's Treasury of Dragons | Legendary | Spellcasting Focus | 137,308 gp | 58,093 gp | -79,214 gp | -57.69% | formula/ML-only |
| Spire of Conflux (Exalted) | Tal'Dorei Campaign Setting Reborn | Legendary | Melee Weapon | 142,861 gp | 63,848 gp | -79,013 gp | -55.31% | formula/ML-only |
| Graz'tchar, the Decadent End | Tal'Dorei Campaign Setting Reborn | Legendary | Melee Weapon | 137,886 gp | 61,050 gp | -76,835 gp | -55.72% | formula/ML-only |
| Shaarat'doovol, the Blade of Truth | Exploring Eberron (2024) | Legendary | Melee Weapon | 268,190 gp | 197,355 gp | -70,834 gp | -26.41% | formula/ML-only |
| Precipit, the Formless | The Griffon's Saddlebag: Book One | Artifact | Melee Weapon | 404,955 gp | 338,984 gp | -65,972 gp | -16.29% | formula/ML-only |
| Shard Solitaire (Black Sapphire) | Keys from the Golden Vault | Legendary | Wondrous Item | 5,000 gp | 69,422 gp | 64,422 gp | 1288.43% | formula/ML-only |
| Shard Solitaire (Diamond) | Keys from the Golden Vault | Legendary | Wondrous Item | 5,000 gp | 69,422 gp | 64,422 gp | 1288.43% | formula/ML-only |
| Shard Solitaire (Jacinth) | Keys from the Golden Vault | Legendary | Wondrous Item | 5,000 gp | 69,422 gp | 64,422 gp | 1288.43% | formula/ML-only |
| Shard Solitaire (Ruby) | Keys from the Golden Vault | Legendary | Wondrous Item | 5,000 gp | 69,422 gp | 64,422 gp | 1288.43% | formula/ML-only |
| Luck Greatsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 228,170 gp | 168,858 gp | -59,313 gp | -25.99% | formula/ML-only |
| Azuredge | Waterdeep: Dragon Heist | Legendary | Melee Weapon | 84,964 gp | 142,502 gp | 57,538 gp | 67.72% | formula/ML-only |
| Luck Glaive | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 220,283 gp | 163,021 gp | -57,262 gp | -25.99% | formula/ML-only |

## Largest percent movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Wyrm's Breath Grenade (Copper) | Heliana's Guide to Monster Hunting | Rare | Wondrous Item | 0 gp | 5,887 gp | 5,886 gp | 1177266.00% | formula/ML-only |
| Wyrm's Breath Grenade (Silver) | Heliana's Guide to Monster Hunting | Legendary | Wondrous Item | 5 gp | 44,860 gp | 44,855 gp | 897096.00% | formula/ML-only |
| Snugglebeast (Dragon) | The Griffon's Saddlebag: Book One | Rare | Wondrous Item | 1 gp | 5,918 gp | 5,917 gp | 591739.00% | formula/ML-only |
| Masks of the Sacred Beasts (Mule) | The Griffon's Saddlebag: Book Two | Very Rare | Wondrous Item | 8 gp | 11,296 gp | 11,288 gp | 141104.50% | formula/ML-only |
| Moonbow (Shortbow) | Call from the Deep | Rare | Ranged Weapon | 25 gp | 12,561 gp | 12,536 gp | 50142.48% | formula/ML-only |
| Moonbow (Longbow) | Call from the Deep | Rare | Ranged Weapon | 50 gp | 13,539 gp | 13,489 gp | 26978.76% | formula/ML-only |
| Wyrm's Breath Grenade (Gold) | Heliana's Guide to Monster Hunting | Very Rare | Wondrous Item | 50 gp | 12,849 gp | 12,799 gp | 25597.12% | formula/ML-only |
| Kiona's Notes | Where Evil Lives: The MCDM Book of Boss Battles | Mundane | Wondrous Item | 1 gp | 201 gp | 200 gp | 20000.00% | formula/ML-only |
| Book of Secrets | Where Evil Lives: The MCDM Book of Boss Battles | Mundane | Adventuring Gear | 1 gp | 101 gp | 100 gp | 10000.00% | formula/ML-only |
| Spell Gem (Jade) | Out of the Abyss | Very Rare | Wondrous Item | 100 gp | 9,519 gp | 9,419 gp | 9418.56% | formula/ML-only |
| Spell Gem (Amber) | Out of the Abyss | Very Rare | Wondrous Item | 116 gp | 9,519 gp | 9,403 gp | 8135.47% | formula/ML-only |
| Spell Gem (Lapis lazuli) | Out of the Abyss | Uncommon | Wondrous Item | 10 gp | 773 gp | 763 gp | 7625.60% | formula/ML-only |
| Spell Gem (Obsidian) | Out of the Abyss | Uncommon | Wondrous Item | 10 gp | 773 gp | 763 gp | 7625.60% | formula/ML-only |
| Spell Gem (Bloodstone) | Out of the Abyss | Rare | Wondrous Item | 50 gp | 3,204 gp | 3,154 gp | 6307.16% | formula/ML-only |
| Spell Gem (Quartz) | Out of the Abyss | Rare | Wondrous Item | 50 gp | 3,204 gp | 3,154 gp | 6307.16% | formula/ML-only |
| Whispergust Mote | The Griffon's Saddlebag: Book Two | Common | Wondrous Item | 121 gp | 7,419 gp | 7,298 gp | 6040.29% | formula/ML-only |
| Spell Gem (Star ruby) | Out of the Abyss | Legendary | Wondrous Item | 1,000 gp | 38,067 gp | 37,067 gp | 3706.74% | formula/ML-only |
| Suude (Blue) | Tal'Dorei Campaign Setting Reborn | Unknown Magic | IDG | 292 gp | 6,852 gp | 6,560 gp | 2248.59% | formula/ML-only |
| Suude (Brown) | Tal'Dorei Campaign Setting Reborn | Unknown Magic | IDG | 292 gp | 6,852 gp | 6,560 gp | 2248.59% | formula/ML-only |
| Suude (Red) | Tal'Dorei Campaign Setting Reborn | Unknown Magic | IDG | 292 gp | 6,852 gp | 6,560 gp | 2248.59% | formula/ML-only |
| Spell Gem (Diamond) | Out of the Abyss | Legendary | Wondrous Item | 5,000 gp | 100,000 gp | 95,000 gp | 1900.00% | formula/ML-only |
| Unknown Elixir | Obojima: Tales from the Tall Grass | Uncommon | Potion | 429 gp | 8,500 gp | 8,071 gp | 1880.61% | formula/ML-only |
| Spell Gem (Topaz) | Out of the Abyss | Very Rare | Wondrous Item | 500 gp | 9,519 gp | 9,019 gp | 1803.71% | formula/ML-only |
| Shard Solitaire (Black Sapphire) | Keys from the Golden Vault | Legendary | Wondrous Item | 5,000 gp | 69,422 gp | 64,422 gp | 1288.43% | formula/ML-only |
| Shard Solitaire (Diamond) | Keys from the Golden Vault | Legendary | Wondrous Item | 5,000 gp | 69,422 gp | 64,422 gp | 1288.43% | formula/ML-only |

## Anchor-tier transitions / ML R² / double-count audit

- Anchor-tier transition and ML R² checks require pipeline metadata not present in final CSV snapshots; add those columns to future candidate snapshots if needed.
- Use the known-good and reference-anchored sections above as the first-pass double-count audit for extraction-driven price creep.
- Formula exposure reports (for example, extra_damage impact) are not final-price deltas.
