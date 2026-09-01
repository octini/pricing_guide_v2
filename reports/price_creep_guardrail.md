# Price Creep Guardrail

Baseline CSV: `output/pricing_guide.csv`
Candidate CSV: `output/pricing_guide_candidate.csv`

## Input row matching

- Common rows: 4717
- New candidate rows: 7224
- Missing candidate rows: 32

## Aggregate final-price drift

- Median % drift: 0.00%
- Mean % drift: 9.32%
- Median gp drift: 0 gp
- Mean gp drift: -218 gp
- Rows >5% drift: 1113
- Rows >10% drift: 802
- Rows >25% drift: 331

## Reference anchored vs formula/ML-only

| Split | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| formula/ML-only | 3677 | 0.00% | 11.77% | 0 gp | -280 gp |
| reference-anchored | 1040 | 0.00% | 0.69% | 0 gp | 1 gp |

## Drift by rarity

| Rarity | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Rare | 1408 | 0.00% | 20.41% | 0 gp | -38 gp |
| Uncommon | 940 | 0.29% | 8.28% | 2 gp | 58 gp |
| Very Rare | 852 | 0.00% | -1.13% | 0 gp | -146 gp |
| Legendary | 638 | 0.00% | -1.78% | 0 gp | -1,437 gp |
| Mundane | 442 | 0.00% | 0.00% | 0 gp | 0 gp |
| Common | 349 | 4.34% | 27.71% | 4 gp | 32 gp |
| Artifact | 71 | 0.00% | 0.00% | 0 gp | 0 gp |
| Unknown Magic | 9 | -8.74% | -13.08% | -28 gp | -13 gp |
| Varies | 8 | 0.00% | 0.00% | 0 gp | 0 gp |

## Drift by type

| Type | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Melee Weapon | 1862 | 0.00% | 18.99% | 0 gp | -81 gp |
| Wondrous Item | 760 | 1.48% | 2.48% | 16 gp | -1,170 gp |
| Ranged Weapon | 536 | 0.00% | 10.60% | 0 gp | -44 gp |
| Medium Armor | 279 | 0.00% | 0.06% | 0 gp | 41 gp |
| Heavy Armor | 217 | 0.00% | 0.28% | 0 gp | 45 gp |
| Adventuring Gear | 195 | 0.00% | 0.01% | 0 gp | 1 gp |
| Light Armor | 142 | 0.00% | 0.07% | 0 gp | 25 gp |
| Spellcasting Focus | 135 | 0.00% | 4.12% | 0 gp | 80 gp |
| Artisan's Tools | 71 | 0.00% | -0.21% | 0 gp | -21 gp |
| Ring | 69 | 1.45% | 2.59% | 49 gp | -167 gp |
| Potion | 66 | 0.46% | 0.07% | 1 gp | 3 gp |
| Ammunition | 64 | 0.00% | -0.10% | 0 gp | -1 gp |
| Wand | 48 | 5.53% | 4.96% | 59 gp | 277 gp |
| Musical Instrument | 45 | 0.00% | 0.73% | 0 gp | -95 gp |
| Scroll | 35 | 3.87% | 3.46% | 11 gp | 467 gp |
| Other | 34 | 0.00% | -9.54% | 0 gp | -97 gp |
| Shield | 30 | -0.76% | 0.05% | -27 gp | -159 gp |
| Trade Goods | 24 | 0.00% | 0.00% | 0 gp | 0 gp |
| Tack & Harness | 22 | 0.00% | 0.00% | 0 gp | 0 gp |
| Rod | 21 | 0.87% | 8.54% | 97 gp | -248 gp |

## Drift by source

| Source | Rows | Median % | Mean % | Median gp | Mean gp |
|---|---:|---:|---:|---:|---:|
| Dungeon Master's Guide (2024) | 1981 | 0.00% | 2.55% | 0 gp | 27 gp |
| Monsters of Drakkenheim | 280 | 0.02% | 2.56% | 3 gp | 73 gp |
| Exploring Eberron (2024) | 270 | 0.00% | 0.50% | 0 gp | -405 gp |
| The Book of Many Things | 219 | 0.00% | 1.46% | 0 gp | -290 gp |
| Player's Handbook (2024) | 217 | 0.00% | 0.00% | 0 gp | 0 gp |
| Fizban's Treasury of Dragons | 206 | 0.02% | 0.90% | 1 gp | 0 gp |
| Explorer's Guide to Wildemount | 190 | 0.00% | 17.22% | 0 gp | -2,337 gp |
| Monster Manual | 170 | -0.49% | -0.90% | -11 gp | -16 gp |
| Frontiers of Eberron: Quickstone | 111 | 131.78% | 241.65% | 982 gp | 1,590 gp |
| Eberron: Rising from the Last War | 107 | 0.00% | 59.98% | 0 gp | 52 gp |
| Tasha's Cauldron of Everything | 80 | -0.04% | 1.37% | -2 gp | -7 gp |
| Acquisitions Incorporated | 75 | 0.24% | 1.93% | 1 gp | 26 gp |
| Eberron: Forge of the Artificer | 72 | 1.11% | 2.11% | 65 gp | 75 gp |
| Critical Role: Call of the Netherdeep | 66 | 0.01% | 3.79% | 2 gp | 365 gp |
| Baldur's Gate: Descent Into Avernus | 56 | 17.53% | 13.64% | 132 gp | 103 gp |
| Player's Handbook | 47 | 0.00% | 0.00% | 0 gp | 0 gp |
| Bigby Presents: Glory of the Giants | 44 | 0.00% | 1.83% | 0 gp | -484 gp |
| Dungeons of Drakkenheim | 43 | 0.00% | 4.55% | 0 gp | 842 gp |
| Guildmasters' Guide to Ravnica | 42 | 0.00% | 1.78% | 0 gp | -430 gp |
| Tomb of Annihilation | 27 | 0.00% | 0.04% | 0 gp | -754 gp |

## Known-good anchors

Known-good status: **REVIEW** (PASS ≤1% drift; REVIEW >1%; FAIL >5%).
Configured anchors include Holy Avenger, Defender, Vorpal Sword, +1/+2/+3 Weapon/Armor, Dragon Slayer, Giant Slayer, and Vicious Weapon families when present.

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Holy Avenger Dart | Dungeon Master's Guide (2024) | Legendary | Ranged Weapon | 196,420 gp | 199,315 gp | 2,896 gp | 1.47% | formula/ML-only |
| Holy Avenger Maul | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 226,279 gp | 223,498 gp | -2,780 gp | -1.23% | formula/ML-only |
| Holy Avenger Musket | Dungeon Master's Guide (2024) | Legendary | Ranged Weapon | 226,279 gp | 223,498 gp | -2,780 gp | -1.23% | formula/ML-only |
| Holy Avenger Dagger | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 201,616 gp | 204,387 gp | 2,771 gp | 1.37% | formula/ML-only |
| Holy Avenger Light Bayonet | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 201,616 gp | 204,387 gp | 2,771 gp | 1.37% | formula/ML-only |
| Holy Avenger Greataxe | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 224,942 gp | 222,194 gp | -2,748 gp | -1.22% | formula/ML-only |
| Holy Avenger Greatsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 224,364 gp | 221,630 gp | -2,734 gp | -1.22% | formula/ML-only |
| Holy Avenger Club | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 204,214 gp | 206,923 gp | 2,708 gp | 1.33% | formula/ML-only |
| Holy Avenger Handaxe | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 204,214 gp | 206,923 gp | 2,708 gp | 1.33% | formula/ML-only |
| Holy Avenger Hooked Shortspear | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 204,214 gp | 206,923 gp | 2,708 gp | 1.33% | formula/ML-only |
| Holy Avenger Hoopak | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 204,214 gp | 206,923 gp | 2,708 gp | 1.33% | formula/ML-only |
| Holy Avenger Javelin | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 204,214 gp | 206,923 gp | 2,708 gp | 1.33% | formula/ML-only |
| Holy Avenger Light Hammer | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 204,214 gp | 206,923 gp | 2,708 gp | 1.33% | formula/ML-only |
| Holy Avenger Shortbow | Dungeon Master's Guide (2024) | Legendary | Ranged Weapon | 204,214 gp | 206,923 gp | 2,708 gp | 1.33% | formula/ML-only |
| Holy Avenger Shortsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 204,214 gp | 206,923 gp | 2,708 gp | 1.33% | formula/ML-only |
| Holy Avenger Sickle | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 204,214 gp | 206,923 gp | 2,708 gp | 1.33% | formula/ML-only |
| Holy Avenger Hand Crossbow | Dungeon Master's Guide (2024) | Legendary | Ranged Weapon | 205,734 gp | 208,406 gp | 2,672 gp | 1.30% | formula/ML-only |
| Holy Avenger Hand Sentira Lens | Dungeon Master's Guide (2024) | Legendary | Ranged Weapon | 205,734 gp | 208,406 gp | 2,672 gp | 1.30% | formula/ML-only |
| Holy Avenger Scimitar | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 205,734 gp | 208,406 gp | 2,672 gp | 1.30% | formula/ML-only |
| Holy Avenger Sling | Dungeon Master's Guide (2024) | Legendary | Ranged Weapon | 205,734 gp | 208,406 gp | 2,672 gp | 1.30% | formula/ML-only |
| Holy Avenger Spear | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 205,734 gp | 208,406 gp | 2,672 gp | 1.30% | formula/ML-only |
| Holy Avenger Whip | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 205,734 gp | 208,406 gp | 2,672 gp | 1.30% | formula/ML-only |
| Holy Avenger Mace | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 206,813 gp | 209,459 gp | 2,646 gp | 1.28% | formula/ML-only |
| Holy Avenger Quarterstaff | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 206,813 gp | 209,459 gp | 2,646 gp | 1.28% | formula/ML-only |
| Holy Avenger Light Sentira Lens | Dungeon Master's Guide (2024) | Legendary | Ranged Weapon | 207,649 gp | 210,275 gp | 2,626 gp | 1.26% | formula/ML-only |
| Holy Avenger Heavy Sentira Lens | Dungeon Master's Guide (2024) | Legendary | Ranged Weapon | 212,451 gp | 214,961 gp | 2,510 gp | 1.18% | formula/ML-only |
| +3 Moon Sickle | Tasha's Cauldron of Everything | Very Rare | Melee Weapon | 33,292 gp | 31,905 gp | -1,387 gp | -4.17% | reference-anchored |
| Vorpal Glaive | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 54,130 gp | 53,561 gp | -568 gp | -1.05% | reference-anchored |
| Vorpal Greatsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 54,130 gp | 53,561 gp | -568 gp | -1.05% | reference-anchored |
| Vorpal Longsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 54,130 gp | 53,561 gp | -568 gp | -1.05% | reference-anchored |
| Vorpal Scimitar | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 54,130 gp | 53,561 gp | -568 gp | -1.05% | reference-anchored |
| +3 Leather Armor | Dungeon Master's Guide (2024) | Legendary | Light Armor | 29,485 gp | 29,744 gp | 259 gp | 0.88% | reference-anchored |
| +3 Padded Armor | Dungeon Master's Guide (2024) | Legendary | Light Armor | 29,485 gp | 29,744 gp | 259 gp | 0.88% | reference-anchored |
| +3 Studded Leather Armor | Dungeon Master's Guide (2024) | Legendary | Light Armor | 29,485 gp | 29,744 gp | 259 gp | 0.88% | reference-anchored |
| Defender Dagger | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 27,090 gp | 27,342 gp | 252 gp | 0.93% | reference-anchored |
| Defender Club | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 28,223 gp | 28,475 gp | 252 gp | 0.89% | reference-anchored |
| Defender Handaxe | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 28,223 gp | 28,475 gp | 252 gp | 0.89% | reference-anchored |
| Defender Javelin | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 28,223 gp | 28,475 gp | 252 gp | 0.89% | reference-anchored |
| Defender Light Hammer | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 28,223 gp | 28,475 gp | 252 gp | 0.89% | reference-anchored |
| Defender Shortsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 28,223 gp | 28,475 gp | 252 gp | 0.89% | reference-anchored |
| Defender Sickle | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 28,223 gp | 28,475 gp | 252 gp | 0.89% | reference-anchored |
| Defender Scimitar | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 28,886 gp | 29,138 gp | 252 gp | 0.87% | reference-anchored |
| Defender Spear | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 28,886 gp | 29,138 gp | 252 gp | 0.87% | reference-anchored |
| Defender Whip | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 28,886 gp | 29,138 gp | 252 gp | 0.87% | reference-anchored |
| Defender Flail | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 30,585 gp | 30,837 gp | 252 gp | 0.82% | reference-anchored |
| Defender Rapier | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 30,585 gp | 30,837 gp | 252 gp | 0.82% | reference-anchored |
| Defender War Pick | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 30,585 gp | 30,837 gp | 252 gp | 0.82% | reference-anchored |
| Defender Longsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 31,248 gp | 31,500 gp | 252 gp | 0.81% | reference-anchored |
| Defender Warhammer | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 32,083 gp | 32,335 gp | 252 gp | 0.79% | reference-anchored |
| Defender Greatclub | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 33,216 gp | 33,468 gp | 252 gp | 0.76% | reference-anchored |
| Defender Pike | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 34,177 gp | 34,429 gp | 252 gp | 0.74% | reference-anchored |
| Defender Greataxe | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 34,996 gp | 35,248 gp | 252 gp | 0.72% | reference-anchored |
| Defender Maul | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 35,579 gp | 35,831 gp | 252 gp | 0.71% | reference-anchored |
| Defender Glaive | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 32,381 gp | 32,633 gp | 252 gp | 0.78% | reference-anchored |
| Defender Halberd | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 32,381 gp | 32,633 gp | 252 gp | 0.78% | reference-anchored |
| Defender Lance | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 32,381 gp | 32,633 gp | 252 gp | 0.78% | reference-anchored |
| Defender Mace | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 29,356 gp | 29,608 gp | 252 gp | 0.86% | reference-anchored |
| Defender Quarterstaff | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 29,356 gp | 29,608 gp | 252 gp | 0.86% | reference-anchored |
| Defender Battleaxe | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 31,718 gp | 31,970 gp | 252 gp | 0.79% | reference-anchored |
| Defender Morningstar | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 31,718 gp | 31,970 gp | 252 gp | 0.79% | reference-anchored |
| Defender Trident | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 31,718 gp | 31,970 gp | 252 gp | 0.79% | reference-anchored |
| Defender Greatsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 34,744 gp | 34,996 gp | 252 gp | 0.73% | reference-anchored |
| +3 Chain Mail | Dungeon Master's Guide (2024) | Legendary | Heavy Armor | 29,494 gp | 29,710 gp | 216 gp | 0.73% | reference-anchored |
| +3 Ring Mail | Dungeon Master's Guide (2024) | Legendary | Heavy Armor | 29,494 gp | 29,710 gp | 216 gp | 0.73% | reference-anchored |
| +3 Splint Armor | Dungeon Master's Guide (2024) | Legendary | Heavy Armor | 29,494 gp | 29,710 gp | 216 gp | 0.73% | reference-anchored |
| Vicious Dart | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 13,329 gp | 13,524 gp | 194 gp | 1.46% | formula/ML-only |
| Vicious Maul | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 15,357 gp | 15,165 gp | -192 gp | -1.25% | formula/ML-only |
| Vicious Musket | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 15,357 gp | 15,165 gp | -192 gp | -1.25% | formula/ML-only |
| Vicious Greataxe | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 15,266 gp | 15,076 gp | -189 gp | -1.24% | formula/ML-only |
| Vicious Greatsword | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 15,227 gp | 15,038 gp | -188 gp | -1.24% | formula/ML-only |
| Vicious Dagger | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 13,682 gp | 13,868 gp | 186 gp | 1.36% | formula/ML-only |
| Vicious Light Bayonet | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 13,682 gp | 13,868 gp | 186 gp | 1.36% | formula/ML-only |
| Vicious Club | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 13,859 gp | 14,040 gp | 181 gp | 1.31% | formula/ML-only |
| Vicious Handaxe | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 13,859 gp | 14,040 gp | 181 gp | 1.31% | formula/ML-only |
| Vicious Hooked Shortspear | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 13,859 gp | 14,040 gp | 181 gp | 1.31% | formula/ML-only |
| Vicious Hoopak | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 13,859 gp | 14,040 gp | 181 gp | 1.31% | formula/ML-only |
| Vicious Javelin | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 13,859 gp | 14,040 gp | 181 gp | 1.31% | formula/ML-only |
| Vicious Light Hammer | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 13,859 gp | 14,040 gp | 181 gp | 1.31% | formula/ML-only |
| Vicious Shortbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 13,859 gp | 14,040 gp | 181 gp | 1.31% | formula/ML-only |
| Vicious Shortsword | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 13,859 gp | 14,040 gp | 181 gp | 1.31% | formula/ML-only |
| Vicious Sickle | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 13,859 gp | 14,040 gp | 181 gp | 1.31% | formula/ML-only |
| Vicious Hand Crossbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 13,962 gp | 14,141 gp | 179 gp | 1.28% | formula/ML-only |
| Vicious Hand Sentira Lens | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 13,962 gp | 14,141 gp | 179 gp | 1.28% | formula/ML-only |
| Vicious Scimitar | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 13,962 gp | 14,141 gp | 179 gp | 1.28% | formula/ML-only |
| Vicious Sling | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 13,962 gp | 14,141 gp | 179 gp | 1.28% | formula/ML-only |
| Vicious Spear | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 13,962 gp | 14,141 gp | 179 gp | 1.28% | formula/ML-only |
| Vicious Whip | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 13,962 gp | 14,141 gp | 179 gp | 1.28% | formula/ML-only |
| Vicious Mace | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,035 gp | 14,212 gp | 177 gp | 1.26% | formula/ML-only |
| Vicious Quarterstaff | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,035 gp | 14,212 gp | 177 gp | 1.26% | formula/ML-only |
| Vicious Light Sentira Lens | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 14,092 gp | 14,268 gp | 176 gp | 1.25% | formula/ML-only |
| Vicious Heavy Sentira Lens | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 14,418 gp | 14,586 gp | 168 gp | 1.16% | formula/ML-only |
| Holy Avenger Heavy Crossbow | Dungeon Master's Guide (2024) | Legendary | Ranged Weapon | 220,466 gp | 220,305 gp | -161 gp | -0.07% | formula/ML-only |
| Holy Avenger Pike | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 220,466 gp | 220,305 gp | -161 gp | -0.07% | formula/ML-only |
| Holy Avenger Greatclub | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 218,263 gp | 218,155 gp | -109 gp | -0.05% | formula/ML-only |
| Holy Avenger Blowgun | Dungeon Master's Guide (2024) | Legendary | Ranged Weapon | 209,632 gp | 209,731 gp | 99 gp | 0.05% | formula/ML-only |
| Holy Avenger Heavy Bayonet | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 209,632 gp | 209,731 gp | 99 gp | 0.05% | formula/ML-only |
| Giant Slayer Battleaxe | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Club | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Dagger | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Double-Bladed Scimitar | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Flail | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Glaive | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Greataxe | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Greatclub | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Greatsword | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Halberd | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Handaxe | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Heavy Bayonet | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Hooked Shortspear | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Hoopak | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Javelin | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Lance | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Light Bayonet | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Light Hammer | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Longsword | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Mace | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Maul | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Morningstar | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Pike | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Quarterstaff | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Rapier | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Scimitar | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Shortsword | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Sickle | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Spear | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Trident | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer War Pick | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Warhammer | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Whip | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| Giant Slayer Yklwa | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,035 gp | 3,946 gp | -89 gp | -2.21% | reference-anchored |
| +3 Plate Armor | Dungeon Master's Guide (2024) | Legendary | Heavy Armor | 29,621 gp | 29,710 gp | 89 gp | 0.30% | reference-anchored |
| Giant Slayer Blowgun | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,024 gp | 3,938 gp | -85 gp | -2.12% | reference-anchored |
| Giant Slayer Dart | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,024 gp | 3,938 gp | -85 gp | -2.12% | reference-anchored |
| Giant Slayer Hand Crossbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,024 gp | 3,938 gp | -85 gp | -2.12% | reference-anchored |
| Giant Slayer Hand Sentira Lens | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,024 gp | 3,938 gp | -85 gp | -2.12% | reference-anchored |
| Giant Slayer Heavy Crossbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,024 gp | 3,938 gp | -85 gp | -2.12% | reference-anchored |
| Giant Slayer Heavy Sentira Lens | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,024 gp | 3,938 gp | -85 gp | -2.12% | reference-anchored |
| Giant Slayer Light Crossbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,024 gp | 3,938 gp | -85 gp | -2.12% | reference-anchored |
| Giant Slayer Light Repeating Crossbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,024 gp | 3,938 gp | -85 gp | -2.12% | reference-anchored |
| Giant Slayer Light Sentira Lens | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,024 gp | 3,938 gp | -85 gp | -2.12% | reference-anchored |
| Giant Slayer Longbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,024 gp | 3,938 gp | -85 gp | -2.12% | reference-anchored |
| Giant Slayer Musket | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,024 gp | 3,938 gp | -85 gp | -2.12% | reference-anchored |
| Giant Slayer Pistol | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,024 gp | 3,938 gp | -85 gp | -2.12% | reference-anchored |
| Giant Slayer Shortbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,024 gp | 3,938 gp | -85 gp | -2.12% | reference-anchored |
| Giant Slayer Sling | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,024 gp | 3,938 gp | -85 gp | -2.12% | reference-anchored |
| +2 Longsword | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 3,141 gp | 3,213 gp | 71 gp | 2.27% | reference-anchored |
| +2 Yklwa | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 3,141 gp | 3,213 gp | 71 gp | 2.27% | reference-anchored |
| +1 Moon Sickle | Tasha's Cauldron of Everything | Uncommon | Melee Weapon | 3,895 gp | 3,831 gp | -64 gp | -1.64% | reference-anchored |
| +3 Longsword | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 14,168 gp | 14,231 gp | 64 gp | 0.45% | reference-anchored |
| +3 Yklwa | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 14,168 gp | 14,231 gp | 64 gp | 0.45% | reference-anchored |
| Holy Avenger Double-Bladed Scimitar | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 216,348 gp | 216,286 gp | -62 gp | -0.03% | formula/ML-only |
| Holy Avenger Glaive | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 216,348 gp | 216,286 gp | -62 gp | -0.03% | formula/ML-only |
| Holy Avenger Halberd | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 216,348 gp | 216,286 gp | -62 gp | -0.03% | formula/ML-only |
| Holy Avenger Lance | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 216,348 gp | 216,286 gp | -62 gp | -0.03% | formula/ML-only |
| +3 Breastplate | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,620 gp | 29,680 gp | 59 gp | 0.20% | reference-anchored |
| +3 Chain Shirt | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,620 gp | 29,680 gp | 59 gp | 0.20% | reference-anchored |
| +3 Half Plate Armor | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,620 gp | 29,680 gp | 59 gp | 0.20% | reference-anchored |
| +3 Hide Armor | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,620 gp | 29,680 gp | 59 gp | 0.20% | reference-anchored |
| +3 Scale Mail | Dungeon Master's Guide (2024) | Legendary | Medium Armor | 29,620 gp | 29,680 gp | 59 gp | 0.20% | reference-anchored |
| +2 Pistol | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 3,134 gp | 3,186 gp | 52 gp | 1.67% | reference-anchored |
| Holy Avenger Staff | Dungeon Master's Guide (2024) | Legendary | Spellcasting Focus | 215,907 gp | 215,855 gp | -52 gp | -0.02% | formula/ML-only |
| Holy Avenger Wooden Staff | Dungeon Master's Guide (2024) | Legendary | Spellcasting Focus | 215,907 gp | 215,855 gp | -52 gp | -0.02% | formula/ML-only |
| Holy Avenger Light Crossbow | Dungeon Master's Guide (2024) | Legendary | Ranged Weapon | 215,665 gp | 215,619 gp | -46 gp | -0.02% | formula/ML-only |
| Holy Avenger Light Repeating Crossbow | Dungeon Master's Guide (2024) | Legendary | Ranged Weapon | 215,665 gp | 215,619 gp | -46 gp | -0.02% | formula/ML-only |
| Holy Avenger Warhammer | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 215,665 gp | 215,619 gp | -46 gp | -0.02% | formula/ML-only |
| +2 Chain Mail | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,504 gp | 8,459 gp | -45 gp | -0.53% | reference-anchored |
| +2 Plate Armor | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,504 gp | 8,459 gp | -45 gp | -0.53% | reference-anchored |
| +2 Ring Mail | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,504 gp | 8,459 gp | -45 gp | -0.53% | reference-anchored |
| +2 Splint Armor | Dungeon Master's Guide (2024) | Very Rare | Heavy Armor | 8,504 gp | 8,459 gp | -45 gp | -0.53% | reference-anchored |
| +2 Leather Armor | Dungeon Master's Guide (2024) | Very Rare | Light Armor | 8,395 gp | 8,436 gp | 41 gp | 0.49% | reference-anchored |
| +2 Padded Armor | Dungeon Master's Guide (2024) | Very Rare | Light Armor | 8,395 gp | 8,436 gp | 41 gp | 0.49% | reference-anchored |
| +2 Studded Leather Armor | Dungeon Master's Guide (2024) | Very Rare | Light Armor | 8,395 gp | 8,436 gp | 41 gp | 0.49% | reference-anchored |
| Holy Avenger Flail | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 212,230 gp | 212,267 gp | 37 gp | 0.02% | formula/ML-only |
| Holy Avenger Longbow | Dungeon Master's Guide (2024) | Legendary | Ranged Weapon | 212,230 gp | 212,267 gp | 37 gp | 0.02% | formula/ML-only |
| Holy Avenger Rapier | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 212,230 gp | 212,267 gp | 37 gp | 0.02% | formula/ML-only |
| Holy Avenger War Pick | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 212,230 gp | 212,267 gp | 37 gp | 0.02% | formula/ML-only |
| +3 Pistol | Dungeon Master's Guide (2024) | Very Rare | Ranged Weapon | 14,126 gp | 14,163 gp | 37 gp | 0.26% | reference-anchored |
| +1 Breastplate | Dungeon Master's Guide (2024) | Rare | Medium Armor | 1,757 gp | 1,730 gp | -27 gp | -1.53% | reference-anchored |
| +1 Chain Shirt | Dungeon Master's Guide (2024) | Rare | Medium Armor | 1,757 gp | 1,730 gp | -27 gp | -1.53% | reference-anchored |
| +1 Half Plate Armor | Dungeon Master's Guide (2024) | Rare | Medium Armor | 1,757 gp | 1,730 gp | -27 gp | -1.53% | reference-anchored |
| +1 Hide Armor | Dungeon Master's Guide (2024) | Rare | Medium Armor | 1,757 gp | 1,730 gp | -27 gp | -1.53% | reference-anchored |
| +1 Scale Mail | Dungeon Master's Guide (2024) | Rare | Medium Armor | 1,757 gp | 1,730 gp | -27 gp | -1.53% | reference-anchored |
| Holy Avenger Battleaxe | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 214,828 gp | 214,802 gp | -26 gp | -0.01% | formula/ML-only |
| Holy Avenger Morningstar | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 214,828 gp | 214,802 gp | -26 gp | -0.01% | formula/ML-only |
| Holy Avenger Trident | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 214,828 gp | 214,802 gp | -26 gp | -0.01% | formula/ML-only |
| +2 Breastplate | Dungeon Master's Guide (2024) | Very Rare | Medium Armor | 8,470 gp | 8,448 gp | -23 gp | -0.27% | reference-anchored |
| +2 Chain Shirt | Dungeon Master's Guide (2024) | Very Rare | Medium Armor | 8,470 gp | 8,448 gp | -23 gp | -0.27% | reference-anchored |
| +2 Half Plate Armor | Dungeon Master's Guide (2024) | Very Rare | Medium Armor | 8,470 gp | 8,448 gp | -23 gp | -0.27% | reference-anchored |
| +2 Hide Armor | Dungeon Master's Guide (2024) | Very Rare | Medium Armor | 8,470 gp | 8,448 gp | -23 gp | -0.27% | reference-anchored |
| +2 Scale Mail | Dungeon Master's Guide (2024) | Very Rare | Medium Armor | 8,470 gp | 8,448 gp | -23 gp | -0.27% | reference-anchored |
| +1 Chain Mail | Dungeon Master's Guide (2024) | Rare | Heavy Armor | 1,806 gp | 1,787 gp | -19 gp | -1.06% | reference-anchored |
| +1 Plate Armor | Dungeon Master's Guide (2024) | Rare | Heavy Armor | 1,806 gp | 1,787 gp | -19 gp | -1.06% | reference-anchored |
| +1 Ring Mail | Dungeon Master's Guide (2024) | Rare | Heavy Armor | 1,806 gp | 1,787 gp | -19 gp | -1.06% | reference-anchored |
| +1 Splint Armor | Dungeon Master's Guide (2024) | Rare | Heavy Armor | 1,806 gp | 1,787 gp | -19 gp | -1.06% | reference-anchored |
| Vicious Heavy Crossbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 14,962 gp | 14,948 gp | -14 gp | -0.09% | formula/ML-only |
| Vicious Pike | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,962 gp | 14,948 gp | -14 gp | -0.09% | formula/ML-only |
| Vicious Greatclub | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,812 gp | 14,802 gp | -10 gp | -0.07% | formula/ML-only |
| Dragon Slayer Battleaxe | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Club | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Dagger | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Double-Bladed Scimitar | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Flail | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Glaive | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Greataxe | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Greatclub | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Greatsword | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Halberd | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Handaxe | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Heavy Bayonet | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Hooked Shortspear | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Hoopak | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Javelin | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Lance | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Light Bayonet | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Light Hammer | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Longsword | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Mace | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Maul | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Morningstar | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Pike | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Quarterstaff | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Rapier | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Scimitar | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Shortsword | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Sickle | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Spear | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Trident | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer War Pick | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Warhammer | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Whip | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Dragon Slayer Yklwa | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,265 gp | 4,256 gp | -9 gp | -0.22% | reference-anchored |
| Vicious Double-Bladed Scimitar | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,682 gp | 14,675 gp | -7 gp | -0.05% | formula/ML-only |
| Vicious Glaive | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,682 gp | 14,675 gp | -7 gp | -0.05% | formula/ML-only |
| Vicious Halberd | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,682 gp | 14,675 gp | -7 gp | -0.05% | formula/ML-only |
| Vicious Lance | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,682 gp | 14,675 gp | -7 gp | -0.05% | formula/ML-only |
| Vicious +1 Blowgun | Acquisitions Incorporated | Uncommon | Ranged Weapon | 616 gp | 609 gp | -7 gp | -1.12% | reference-anchored |
| Vicious +1 Dart | Acquisitions Incorporated | Uncommon | Ranged Weapon | 616 gp | 609 gp | -7 gp | -1.12% | reference-anchored |
| Vicious +1 Hand Crossbow | Acquisitions Incorporated | Uncommon | Ranged Weapon | 616 gp | 609 gp | -7 gp | -1.12% | reference-anchored |
| Vicious +1 Heavy Crossbow | Acquisitions Incorporated | Uncommon | Ranged Weapon | 616 gp | 609 gp | -7 gp | -1.12% | reference-anchored |
| Vicious +1 Light Crossbow | Acquisitions Incorporated | Uncommon | Ranged Weapon | 616 gp | 609 gp | -7 gp | -1.12% | reference-anchored |
| Vicious +1 Light Repeating Crossbow | Acquisitions Incorporated | Uncommon | Ranged Weapon | 616 gp | 609 gp | -7 gp | -1.12% | reference-anchored |
| Vicious +1 Longbow | Acquisitions Incorporated | Uncommon | Ranged Weapon | 616 gp | 609 gp | -7 gp | -1.12% | reference-anchored |
| Vicious +1 Musket | Acquisitions Incorporated | Uncommon | Ranged Weapon | 616 gp | 609 gp | -7 gp | -1.12% | reference-anchored |
| Vicious +1 Pistol | Acquisitions Incorporated | Uncommon | Ranged Weapon | 616 gp | 609 gp | -7 gp | -1.12% | reference-anchored |
| Vicious +1 Shortbow | Acquisitions Incorporated | Uncommon | Ranged Weapon | 616 gp | 609 gp | -7 gp | -1.12% | reference-anchored |
| Vicious +1 Sling | Acquisitions Incorporated | Uncommon | Ranged Weapon | 616 gp | 609 gp | -7 gp | -1.12% | reference-anchored |
| Dragon Slayer Blowgun | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,255 gp | 4,248 gp | -7 gp | -0.15% | reference-anchored |
| Dragon Slayer Dart | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,255 gp | 4,248 gp | -7 gp | -0.15% | reference-anchored |
| Dragon Slayer Hand Crossbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,255 gp | 4,248 gp | -7 gp | -0.15% | reference-anchored |
| Dragon Slayer Hand Sentira Lens | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,255 gp | 4,248 gp | -7 gp | -0.15% | reference-anchored |
| Dragon Slayer Heavy Crossbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,255 gp | 4,248 gp | -7 gp | -0.15% | reference-anchored |
| Dragon Slayer Heavy Sentira Lens | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,255 gp | 4,248 gp | -7 gp | -0.15% | reference-anchored |
| Dragon Slayer Light Crossbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,255 gp | 4,248 gp | -7 gp | -0.15% | reference-anchored |
| Dragon Slayer Light Repeating Crossbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,255 gp | 4,248 gp | -7 gp | -0.15% | reference-anchored |
| Dragon Slayer Light Sentira Lens | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,255 gp | 4,248 gp | -7 gp | -0.15% | reference-anchored |
| Dragon Slayer Longbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,255 gp | 4,248 gp | -7 gp | -0.15% | reference-anchored |
| Dragon Slayer Musket | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,255 gp | 4,248 gp | -7 gp | -0.15% | reference-anchored |
| Dragon Slayer Pistol | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,255 gp | 4,248 gp | -7 gp | -0.15% | reference-anchored |
| Dragon Slayer Shortbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,255 gp | 4,248 gp | -7 gp | -0.15% | reference-anchored |
| Dragon Slayer Sling | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,255 gp | 4,248 gp | -7 gp | -0.15% | reference-anchored |
| Vicious Light Crossbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 14,636 gp | 14,630 gp | -6 gp | -0.04% | formula/ML-only |
| Vicious Light Repeating Crossbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 14,636 gp | 14,630 gp | -6 gp | -0.04% | formula/ML-only |
| Vicious Warhammer | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,636 gp | 14,630 gp | -6 gp | -0.04% | formula/ML-only |
| +2 Moon Sickle | Tasha's Cauldron of Everything | Rare | Melee Weapon | 12,106 gp | 12,111 gp | 5 gp | 0.04% | reference-anchored |
| Vicious Battleaxe | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,579 gp | 14,575 gp | -4 gp | -0.03% | formula/ML-only |
| Vicious Morningstar | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,579 gp | 14,575 gp | -4 gp | -0.03% | formula/ML-only |
| Vicious Trident | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,579 gp | 14,575 gp | -4 gp | -0.03% | formula/ML-only |
| +1 Pistol | Dungeon Master's Guide (2024) | Uncommon | Ranged Weapon | 596 gp | 592 gp | -4 gp | -0.71% | reference-anchored |
| Vicious Blowgun | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 14,226 gp | 14,231 gp | 4 gp | 0.03% | formula/ML-only |
| Vicious Heavy Bayonet | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,226 gp | 14,231 gp | 4 gp | 0.03% | formula/ML-only |
| Vicious Longsword | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,506 gp | 14,503 gp | -3 gp | -0.02% | formula/ML-only |
| Vicious Pistol | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 14,506 gp | 14,503 gp | -3 gp | -0.02% | formula/ML-only |
| Vicious Yklwa | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,506 gp | 14,503 gp | -3 gp | -0.02% | formula/ML-only |
| +1 Leather Armor | Dungeon Master's Guide (2024) | Rare | Light Armor | 1,748 gp | 1,750 gp | 2 gp | 0.09% | reference-anchored |
| +1 Padded Armor | Dungeon Master's Guide (2024) | Rare | Light Armor | 1,748 gp | 1,750 gp | 2 gp | 0.09% | reference-anchored |
| +1 Studded Leather Armor | Dungeon Master's Guide (2024) | Rare | Light Armor | 1,748 gp | 1,750 gp | 2 gp | 0.09% | reference-anchored |
| Vicious +1 Battleaxe | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Club | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Dagger | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Double-Bladed Scimitar | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Flail | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Glaive | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Greataxe | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Greatclub | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Greatsword | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Halberd | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Handaxe | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Hooked Shortspear | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Hoopak | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Javelin | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Lance | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Light Hammer | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Longsword | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Mace | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Maul | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Morningstar | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Pike | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Quarterstaff | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Rapier | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Scimitar | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Shortsword | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Sickle | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Spear | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Trident | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 War Pick | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Warhammer | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Whip | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| Vicious +1 Yklwa | Acquisitions Incorporated | Uncommon | Melee Weapon | 617 gp | 618 gp | 1 gp | 0.24% | reference-anchored |
| +1 Longsword | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 599 gp | 600 gp | 1 gp | 0.11% | reference-anchored |
| +1 Yklwa | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 599 gp | 600 gp | 1 gp | 0.11% | reference-anchored |
| Vicious Flail | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,403 gp | 14,403 gp | -0 gp | -0.00% | formula/ML-only |
| Vicious Longbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 14,403 gp | 14,403 gp | -0 gp | -0.00% | formula/ML-only |
| Vicious Rapier | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,403 gp | 14,403 gp | -0 gp | -0.00% | formula/ML-only |
| Vicious War Pick | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 14,403 gp | 14,403 gp | -0 gp | -0.00% | formula/ML-only |
| +1 Battleaxe | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 636 gp | 636 gp | 0 gp | 0.00% | reference-anchored |
| +1 Blowgun | Dungeon Master's Guide (2024) | Uncommon | Ranged Weapon | 536 gp | 536 gp | 0 gp | 0.00% | reference-anchored |
| +1 Club | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 432 gp | 432 gp | 0 gp | 0.00% | reference-anchored |
| +1 Dagger | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 382 gp | 382 gp | 0 gp | 0.00% | reference-anchored |
| +1 Dart | Dungeon Master's Guide (2024) | Uncommon | Ranged Weapon | 283 gp | 283 gp | 0 gp | 0.00% | reference-anchored |
| +1 Double-Bladed Scimitar | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 665 gp | 665 gp | 0 gp | 0.00% | reference-anchored |
| +1 Flail | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 586 gp | 586 gp | 0 gp | 0.00% | reference-anchored |
| +1 Glaive | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 665 gp | 665 gp | 0 gp | 0.00% | reference-anchored |
| +1 Greataxe | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 830 gp | 830 gp | 0 gp | 0.00% | reference-anchored |
| +1 Greatclub | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 702 gp | 702 gp | 0 gp | 0.00% | reference-anchored |
| +1 Greatsword | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 819 gp | 819 gp | 0 gp | 0.00% | reference-anchored |
| +1 Halberd | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 665 gp | 665 gp | 0 gp | 0.00% | reference-anchored |
| +1 Hand Crossbow | Dungeon Master's Guide (2024) | Uncommon | Ranged Weapon | 461 gp | 461 gp | 0 gp | 0.00% | reference-anchored |
| +1 Handaxe | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 432 gp | 432 gp | 0 gp | 0.00% | reference-anchored |
| +1 Heavy Crossbow | Dungeon Master's Guide (2024) | Uncommon | Ranged Weapon | 744 gp | 744 gp | 0 gp | 0.00% | reference-anchored |
| +1 Hooked Shortspear | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 432 gp | 432 gp | 0 gp | 0.00% | reference-anchored |
| +1 Hoopak | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 432 gp | 432 gp | 0 gp | 0.00% | reference-anchored |
| +1 Javelin | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 432 gp | 432 gp | 0 gp | 0.00% | reference-anchored |
| +1 Lance | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 665 gp | 665 gp | 0 gp | 0.00% | reference-anchored |
| +1 Light Crossbow | Dungeon Master's Guide (2024) | Uncommon | Ranged Weapon | 652 gp | 652 gp | 0 gp | 0.00% | reference-anchored |
| +1 Light Hammer | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 432 gp | 432 gp | 0 gp | 0.00% | reference-anchored |
| +1 Light Repeating Crossbow | Dungeon Master's Guide (2024) | Uncommon | Ranged Weapon | 652 gp | 652 gp | 0 gp | 0.00% | reference-anchored |
| +1 Longbow | Dungeon Master's Guide (2024) | Uncommon | Ranged Weapon | 586 gp | 586 gp | 0 gp | 0.00% | reference-anchored |
| +1 Mace | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 482 gp | 482 gp | 0 gp | 0.00% | reference-anchored |
| +1 Maul | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 855 gp | 855 gp | 0 gp | 0.00% | reference-anchored |
| +1 Morningstar | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 636 gp | 636 gp | 0 gp | 0.00% | reference-anchored |
| +1 Musket | Dungeon Master's Guide (2024) | Uncommon | Ranged Weapon | 855 gp | 855 gp | 0 gp | 0.00% | reference-anchored |
| +1 Pike | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 744 gp | 744 gp | 0 gp | 0.00% | reference-anchored |
| +1 Quarterstaff | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 482 gp | 482 gp | 0 gp | 0.00% | reference-anchored |
| +1 Rapier | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 586 gp | 586 gp | 0 gp | 0.00% | reference-anchored |
| +1 Scimitar | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 461 gp | 461 gp | 0 gp | 0.00% | reference-anchored |
| +1 Shortbow | Dungeon Master's Guide (2024) | Uncommon | Ranged Weapon | 432 gp | 432 gp | 0 gp | 0.00% | reference-anchored |
| +1 Shortsword | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 434 gp | 434 gp | 0 gp | 0.00% | reference-anchored |
| +1 Sickle | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 432 gp | 432 gp | 0 gp | 0.00% | reference-anchored |
| +1 Sling | Dungeon Master's Guide (2024) | Uncommon | Ranged Weapon | 461 gp | 461 gp | 0 gp | 0.00% | reference-anchored |
| +1 Spear | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 461 gp | 461 gp | 0 gp | 0.00% | reference-anchored |
| +1 Trident | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 636 gp | 636 gp | 0 gp | 0.00% | reference-anchored |
| +1 War Pick | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 586 gp | 586 gp | 0 gp | 0.00% | reference-anchored |
| +1 Warhammer | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 652 gp | 652 gp | 0 gp | 0.00% | reference-anchored |
| +1 Whip | Dungeon Master's Guide (2024) | Uncommon | Melee Weapon | 461 gp | 461 gp | 0 gp | 0.00% | reference-anchored |
| +2 Battleaxe | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 3,328 gp | 3,328 gp | 0 gp | 0.00% | reference-anchored |
| +2 Blowgun | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 2,806 gp | 2,806 gp | 0 gp | 0.00% | reference-anchored |
| +2 Club | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 2,262 gp | 2,262 gp | 0 gp | 0.00% | reference-anchored |
| +2 Dagger | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 2,001 gp | 2,001 gp | 0 gp | 0.00% | reference-anchored |
| +2 Dart | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 1,480 gp | 1,480 gp | 0 gp | 0.00% | reference-anchored |
| +2 Double-Bladed Scimitar | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 3,481 gp | 3,481 gp | 0 gp | 0.00% | reference-anchored |
| +2 Flail | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 3,067 gp | 3,067 gp | 0 gp | 0.00% | reference-anchored |
| +2 Glaive | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 3,481 gp | 3,481 gp | 0 gp | 0.00% | reference-anchored |
| +2 Greataxe | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,344 gp | 4,344 gp | 0 gp | 0.00% | reference-anchored |
| +2 Greatclub | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 3,673 gp | 3,673 gp | 0 gp | 0.00% | reference-anchored |
| +2 Greatsword | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,286 gp | 4,286 gp | 0 gp | 0.00% | reference-anchored |
| +2 Halberd | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 3,481 gp | 3,481 gp | 0 gp | 0.00% | reference-anchored |
| +2 Hand Crossbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 2,415 gp | 2,415 gp | 0 gp | 0.00% | reference-anchored |
| +2 Handaxe | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 2,262 gp | 2,262 gp | 0 gp | 0.00% | reference-anchored |
| +2 Heavy Crossbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 3,895 gp | 3,895 gp | 0 gp | 0.00% | reference-anchored |
| +2 Hooked Shortspear | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 2,262 gp | 2,262 gp | 0 gp | 0.00% | reference-anchored |
| +2 Hoopak | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 2,262 gp | 2,262 gp | 0 gp | 0.00% | reference-anchored |
| +2 Javelin | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 2,262 gp | 2,262 gp | 0 gp | 0.00% | reference-anchored |
| +2 Lance | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 3,481 gp | 3,481 gp | 0 gp | 0.00% | reference-anchored |
| +2 Light Crossbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 3,412 gp | 3,412 gp | 0 gp | 0.00% | reference-anchored |
| +2 Light Hammer | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 2,262 gp | 2,262 gp | 0 gp | 0.00% | reference-anchored |
| +2 Light Repeating Crossbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 3,412 gp | 3,412 gp | 0 gp | 0.00% | reference-anchored |
| +2 Longbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 3,067 gp | 3,067 gp | 0 gp | 0.00% | reference-anchored |
| +2 Mace | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 2,523 gp | 2,523 gp | 0 gp | 0.00% | reference-anchored |
| +2 Maul | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 4,478 gp | 4,478 gp | 0 gp | 0.00% | reference-anchored |
| +2 Morningstar | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 3,328 gp | 3,328 gp | 0 gp | 0.00% | reference-anchored |
| +2 Musket | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 4,478 gp | 4,478 gp | 0 gp | 0.00% | reference-anchored |
| +2 Pike | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 3,895 gp | 3,895 gp | 0 gp | 0.00% | reference-anchored |
| +2 Quarterstaff | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 2,523 gp | 2,523 gp | 0 gp | 0.00% | reference-anchored |
| +2 Rapier | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 3,067 gp | 3,067 gp | 0 gp | 0.00% | reference-anchored |
| +2 Scimitar | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 2,415 gp | 2,415 gp | 0 gp | 0.00% | reference-anchored |
| +2 Shortbow | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 2,262 gp | 2,262 gp | 0 gp | 0.00% | reference-anchored |
| +2 Shortsword | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 2,262 gp | 2,262 gp | 0 gp | 0.00% | reference-anchored |
| +2 Sickle | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 2,262 gp | 2,262 gp | 0 gp | 0.00% | reference-anchored |
| +2 Sling | Dungeon Master's Guide (2024) | Rare | Ranged Weapon | 2,415 gp | 2,415 gp | 0 gp | 0.00% | reference-anchored |
| +2 Spear | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 2,415 gp | 2,415 gp | 0 gp | 0.00% | reference-anchored |
| +2 Trident | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 3,328 gp | 3,328 gp | 0 gp | 0.00% | reference-anchored |
| +2 War Pick | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 3,067 gp | 3,067 gp | 0 gp | 0.00% | reference-anchored |
| +2 Warhammer | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 3,412 gp | 3,412 gp | 0 gp | 0.00% | reference-anchored |
| +2 Whip | Dungeon Master's Guide (2024) | Rare | Melee Weapon | 2,415 gp | 2,415 gp | 0 gp | 0.00% | reference-anchored |
| +3 Battleaxe | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 14,946 gp | 14,946 gp | 0 gp | 0.00% | reference-anchored |
| +3 Blowgun | Dungeon Master's Guide (2024) | Very Rare | Ranged Weapon | 12,603 gp | 12,603 gp | 0 gp | 0.00% | reference-anchored |
| +3 Club | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 10,160 gp | 10,160 gp | 0 gp | 0.00% | reference-anchored |
| +3 Dagger | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 8,988 gp | 8,988 gp | 0 gp | 0.00% | reference-anchored |
| +3 Dart | Dungeon Master's Guide (2024) | Very Rare | Ranged Weapon | 6,644 gp | 6,644 gp | 0 gp | 0.00% | reference-anchored |
| +3 Double-Bladed Scimitar | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 15,632 gp | 15,632 gp | 0 gp | 0.00% | reference-anchored |
| +3 Flail | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 13,775 gp | 13,775 gp | 0 gp | 0.00% | reference-anchored |
| +3 Glaive | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 15,632 gp | 15,632 gp | 0 gp | 0.00% | reference-anchored |
| +3 Greataxe | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 19,507 gp | 19,507 gp | 0 gp | 0.00% | reference-anchored |
| +3 Greatclub | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 16,495 gp | 16,495 gp | 0 gp | 0.00% | reference-anchored |
| +3 Greatsword | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 19,247 gp | 19,247 gp | 0 gp | 0.00% | reference-anchored |
| +3 Halberd | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 15,632 gp | 15,632 gp | 0 gp | 0.00% | reference-anchored |
| +3 Hand Crossbow | Dungeon Master's Guide (2024) | Very Rare | Ranged Weapon | 10,845 gp | 10,845 gp | 0 gp | 0.00% | reference-anchored |
| +3 Handaxe | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 10,160 gp | 10,160 gp | 0 gp | 0.00% | reference-anchored |
| +3 Heavy Crossbow | Dungeon Master's Guide (2024) | Very Rare | Ranged Weapon | 17,489 gp | 17,489 gp | 0 gp | 0.00% | reference-anchored |
| +3 Hooked Shortspear | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 10,160 gp | 10,160 gp | 0 gp | 0.00% | reference-anchored |
| +3 Hoopak | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 10,160 gp | 10,160 gp | 0 gp | 0.00% | reference-anchored |
| +3 Javelin | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 10,160 gp | 10,160 gp | 0 gp | 0.00% | reference-anchored |
| +3 Lance | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 15,632 gp | 15,632 gp | 0 gp | 0.00% | reference-anchored |
| +3 Light Crossbow | Dungeon Master's Guide (2024) | Very Rare | Ranged Weapon | 15,324 gp | 15,324 gp | 0 gp | 0.00% | reference-anchored |
| +3 Light Hammer | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 10,160 gp | 10,160 gp | 0 gp | 0.00% | reference-anchored |
| +3 Light Repeating Crossbow | Dungeon Master's Guide (2024) | Very Rare | Ranged Weapon | 15,324 gp | 15,324 gp | 0 gp | 0.00% | reference-anchored |
| +3 Longbow | Dungeon Master's Guide (2024) | Very Rare | Ranged Weapon | 13,775 gp | 13,775 gp | 0 gp | 0.00% | reference-anchored |
| +3 Mace | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 11,331 gp | 11,331 gp | 0 gp | 0.00% | reference-anchored |
| +3 Maul | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 20,110 gp | 20,110 gp | 0 gp | 0.00% | reference-anchored |
| +3 Morningstar | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 14,946 gp | 14,946 gp | 0 gp | 0.00% | reference-anchored |
| +3 Musket | Dungeon Master's Guide (2024) | Very Rare | Ranged Weapon | 20,110 gp | 20,110 gp | 0 gp | 0.00% | reference-anchored |
| +3 Pike | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 17,489 gp | 17,489 gp | 0 gp | 0.00% | reference-anchored |
| +3 Quarterstaff | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 11,331 gp | 11,331 gp | 0 gp | 0.00% | reference-anchored |
| +3 Rapier | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 13,775 gp | 13,775 gp | 0 gp | 0.00% | reference-anchored |
| +3 Scimitar | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 10,845 gp | 10,845 gp | 0 gp | 0.00% | reference-anchored |
| +3 Shortbow | Dungeon Master's Guide (2024) | Very Rare | Ranged Weapon | 10,160 gp | 10,160 gp | 0 gp | 0.00% | reference-anchored |
| +3 Shortsword | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 10,160 gp | 10,160 gp | 0 gp | 0.00% | reference-anchored |
| +3 Sickle | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 10,160 gp | 10,160 gp | 0 gp | 0.00% | reference-anchored |
| +3 Sling | Dungeon Master's Guide (2024) | Very Rare | Ranged Weapon | 10,845 gp | 10,845 gp | 0 gp | 0.00% | reference-anchored |
| +3 Spear | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 10,845 gp | 10,845 gp | 0 gp | 0.00% | reference-anchored |
| +3 Trident | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 14,946 gp | 14,946 gp | 0 gp | 0.00% | reference-anchored |
| +3 War Pick | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 13,775 gp | 13,775 gp | 0 gp | 0.00% | reference-anchored |
| +3 Warhammer | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 15,324 gp | 15,324 gp | 0 gp | 0.00% | reference-anchored |
| +3 Whip | Dungeon Master's Guide (2024) | Very Rare | Melee Weapon | 10,845 gp | 10,845 gp | 0 gp | 0.00% | reference-anchored |
| Holy Avenger Longsword | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 213,750 gp | 213,750 gp | 0 gp | 0.00% | formula/ML-only |
| Holy Avenger Pistol | Dungeon Master's Guide (2024) | Legendary | Ranged Weapon | 213,750 gp | 213,750 gp | 0 gp | 0.00% | formula/ML-only |
| Holy Avenger Yklwa | Dungeon Master's Guide (2024) | Legendary | Melee Weapon | 213,750 gp | 213,750 gp | 0 gp | 0.00% | formula/ML-only |

## Artifact/legendary movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Shard Solitaire (Black Sapphire) | Keys from the Golden Vault | Legendary | Wondrous Item | 95,577 gp | 5,000 gp | -90,577 gp | -94.77% | formula/ML-only |
| Shard Solitaire (Diamond) | Keys from the Golden Vault | Legendary | Wondrous Item | 95,577 gp | 5,000 gp | -90,577 gp | -94.77% | formula/ML-only |
| Shard Solitaire (Jacinth) | Keys from the Golden Vault | Legendary | Wondrous Item | 94,672 gp | 5,000 gp | -89,672 gp | -94.72% | formula/ML-only |
| Shard Solitaire (Ruby) | Keys from the Golden Vault | Legendary | Wondrous Item | 94,672 gp | 5,000 gp | -89,672 gp | -94.72% | formula/ML-only |
| Stormgirdle (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 183,000 gp | 116,111 gp | -66,889 gp | -36.55% | formula/ML-only |
| Stormgirdle (Awakened) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 137,924 gp | 81,325 gp | -56,599 gp | -41.04% | formula/ML-only |
| Shaarat'doovol, the Blade of Truth | Exploring Eberron (2024) | Legendary | Melee Weapon | 213,000 gp | 268,190 gp | 55,190 gp | 25.91% | formula/ML-only |
| Deck of Many More Things | The Book of Many Things | Legendary | Wondrous Item | 186,175 gp | 140,210 gp | -45,965 gp | -24.69% | formula/ML-only |
| Spell Gem (Star ruby) | Out of the Abyss | Legendary | Wondrous Item | 36,498 gp | 1,000 gp | -35,498 gp | -97.26% | formula/ML-only |
| Infiltrator's Key (Awakened) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 68,365 gp | 34,154 gp | -34,211 gp | -50.04% | formula/ML-only |
| Dragonlance Pike | Fizban's Treasury of Dragons | Legendary | Melee Weapon | 136,656 gp | 103,879 gp | -32,777 gp | -23.98% | formula/ML-only |
| Infiltrator's Key (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 92,052 gp | 60,110 gp | -31,942 gp | -34.70% | formula/ML-only |
| Spell Gem (Diamond) | Out of the Abyss | Legendary | Wondrous Item | 36,498 gp | 5,000 gp | -31,498 gp | -86.30% | formula/ML-only |
| Spell Gem (Ruby) | Out of the Abyss | Legendary | Wondrous Item | 36,498 gp | 5,000 gp | -31,498 gp | -86.30% | formula/ML-only |
| Dragonlance Lance | Fizban's Treasury of Dragons | Legendary | Melee Weapon | 126,683 gp | 96,298 gp | -30,385 gp | -23.98% | formula/ML-only |
| Azuredge | Waterdeep: Dragon Heist | Legendary | Melee Weapon | 109,437 gp | 84,964 gp | -24,473 gp | -22.36% | formula/ML-only |
| Flail of Tiamat | Fizban's Treasury of Dragons | Legendary | Melee Weapon | 133,922 gp | 156,110 gp | 22,188 gp | 16.57% | formula/ML-only |
| Bookmark | Tomb of Annihilation | Legendary | Melee Weapon | 63,573 gp | 41,598 gp | -21,975 gp | -34.57% | formula/ML-only |
| Verminshroud (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 93,666 gp | 72,312 gp | -21,354 gp | -22.80% | formula/ML-only |
| Inscrutable Staff | Dungeons of Drakkenheim | Legendary | Melee Weapon | 88,777 gp | 109,729 gp | 20,952 gp | 23.60% | formula/ML-only |

## Largest movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Shard Solitaire (Black Sapphire) | Keys from the Golden Vault | Legendary | Wondrous Item | 95,577 gp | 5,000 gp | -90,577 gp | -94.77% | formula/ML-only |
| Shard Solitaire (Diamond) | Keys from the Golden Vault | Legendary | Wondrous Item | 95,577 gp | 5,000 gp | -90,577 gp | -94.77% | formula/ML-only |
| Shard Solitaire (Jacinth) | Keys from the Golden Vault | Legendary | Wondrous Item | 94,672 gp | 5,000 gp | -89,672 gp | -94.72% | formula/ML-only |
| Shard Solitaire (Ruby) | Keys from the Golden Vault | Legendary | Wondrous Item | 94,672 gp | 5,000 gp | -89,672 gp | -94.72% | formula/ML-only |
| Stormgirdle (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 183,000 gp | 116,111 gp | -66,889 gp | -36.55% | formula/ML-only |
| Stormgirdle (Awakened) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 137,924 gp | 81,325 gp | -56,599 gp | -41.04% | formula/ML-only |
| Shaarat'doovol, the Blade of Truth | Exploring Eberron (2024) | Legendary | Melee Weapon | 213,000 gp | 268,190 gp | 55,190 gp | 25.91% | formula/ML-only |
| Deck of Many More Things | The Book of Many Things | Legendary | Wondrous Item | 186,175 gp | 140,210 gp | -45,965 gp | -24.69% | formula/ML-only |
| Spell Gem (Star ruby) | Out of the Abyss | Legendary | Wondrous Item | 36,498 gp | 1,000 gp | -35,498 gp | -97.26% | formula/ML-only |
| Infiltrator's Key (Awakened) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 68,365 gp | 34,154 gp | -34,211 gp | -50.04% | formula/ML-only |
| Dragonlance Pike | Fizban's Treasury of Dragons | Legendary | Melee Weapon | 136,656 gp | 103,879 gp | -32,777 gp | -23.98% | formula/ML-only |
| Infiltrator's Key (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 92,052 gp | 60,110 gp | -31,942 gp | -34.70% | formula/ML-only |
| Spell Gem (Diamond) | Out of the Abyss | Legendary | Wondrous Item | 36,498 gp | 5,000 gp | -31,498 gp | -86.30% | formula/ML-only |
| Spell Gem (Ruby) | Out of the Abyss | Legendary | Wondrous Item | 36,498 gp | 5,000 gp | -31,498 gp | -86.30% | formula/ML-only |
| Dragonlance Lance | Fizban's Treasury of Dragons | Legendary | Melee Weapon | 126,683 gp | 96,298 gp | -30,385 gp | -23.98% | formula/ML-only |
| Azuredge | Waterdeep: Dragon Heist | Legendary | Melee Weapon | 109,437 gp | 84,964 gp | -24,473 gp | -22.36% | formula/ML-only |
| Flail of Tiamat | Fizban's Treasury of Dragons | Legendary | Melee Weapon | 133,922 gp | 156,110 gp | 22,188 gp | 16.57% | formula/ML-only |
| Bookmark | Tomb of Annihilation | Legendary | Melee Weapon | 63,573 gp | 41,598 gp | -21,975 gp | -34.57% | formula/ML-only |
| Verminshroud (Exalted) | Explorer's Guide to Wildemount | Legendary | Wondrous Item | 93,666 gp | 72,312 gp | -21,354 gp | -22.80% | formula/ML-only |
| Inscrutable Staff | Dungeons of Drakkenheim | Legendary | Melee Weapon | 88,777 gp | 109,729 gp | 20,952 gp | 23.60% | formula/ML-only |
| Holy Symbol of Ravenkind | Curse of Strahd | Legendary | Wondrous Item | 47,695 gp | 65,422 gp | 17,727 gp | 37.17% | formula/ML-only |
| Jewel of Three Prayers (Exalted) | Critical Role: Call of the Netherdeep | Legendary | Wondrous Item | 48,527 gp | 66,044 gp | 17,517 gp | 36.10% | formula/ML-only |
| Ascendant Scaled Ornament | Fizban's Treasury of Dragons | Legendary | Wondrous Item | 45,706 gp | 61,032 gp | 15,326 gp | 33.53% | formula/ML-only |
| Longbow of the Healing Hearth | Bigby Presents: Glory of the Giants | Legendary | Ranged Weapon | 68,729 gp | 54,062 gp | -14,667 gp | -21.34% | formula/ML-only |
| Rakdos Riteknife | Guildmasters' Guide to Ravnica | Legendary | Melee Weapon | 61,291 gp | 46,883 gp | -14,408 gp | -23.51% | formula/ML-only |

## Largest percent movers

| Name | Source | Rarity | Type | Baseline | Candidate | Delta gp | Delta % | Split |
|---|---|---|---|---:|---:|---:|---:|---|
| Acheron Blade Greatsword | Explorer's Guide to Wildemount | Rare | Melee Weapon | 708 gp | 6,014 gp | 5,306 gp | 749.66% | formula/ML-only |
| Acheron Blade Scimitar | Explorer's Guide to Wildemount | Rare | Melee Weapon | 628 gp | 5,336 gp | 4,708 gp | 749.66% | formula/ML-only |
| Acheron Blade Longsword | Explorer's Guide to Wildemount | Rare | Melee Weapon | 652 gp | 5,544 gp | 4,892 gp | 749.66% | formula/ML-only |
| Acheron Blade Shortsword | Explorer's Guide to Wildemount | Rare | Melee Weapon | 610 gp | 5,183 gp | 4,573 gp | 749.65% | formula/ML-only |
| Acheron Blade Rapier | Explorer's Guide to Wildemount | Rare | Melee Weapon | 634 gp | 5,391 gp | 4,756 gp | 749.65% | formula/ML-only |
| Acheron Blade Double-Bladed Scimitar | Explorer's Guide to Wildemount | Rare | Melee Weapon | 683 gp | 5,806 gp | 5,123 gp | 749.65% | formula/ML-only |
| Demonglass Dart | Frontiers of Eberron: Quickstone | Rare | Ranged Weapon | 615 gp | 3,939 gp | 3,325 gp | 540.96% | formula/ML-only |
| Demonglass Dagger | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 631 gp | 4,010 gp | 3,379 gp | 535.85% | formula/ML-only |
| Demonglass Blowgun | Frontiers of Eberron: Quickstone | Rare | Ranged Weapon | 643 gp | 4,084 gp | 3,441 gp | 535.17% | formula/ML-only |
| Demonglass Club | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,045 gp | 3,406 gp | 533.39% | formula/ML-only |
| Demonglass Handaxe | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,045 gp | 3,406 gp | 533.39% | formula/ML-only |
| Demonglass Hooked Shortspear | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,045 gp | 3,406 gp | 533.39% | formula/ML-only |
| Demonglass Hoopak | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,045 gp | 3,406 gp | 533.39% | formula/ML-only |
| Demonglass Javelin | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,045 gp | 3,406 gp | 533.39% | formula/ML-only |
| Demonglass Light Hammer | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,045 gp | 3,406 gp | 533.39% | formula/ML-only |
| Demonglass Shortbow | Frontiers of Eberron: Quickstone | Rare | Ranged Weapon | 639 gp | 4,045 gp | 3,406 gp | 533.39% | formula/ML-only |
| Demonglass Shortsword | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,045 gp | 3,406 gp | 533.39% | formula/ML-only |
| Demonglass Sickle | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 639 gp | 4,045 gp | 3,406 gp | 533.39% | formula/ML-only |
| Demonglass Hand Crossbow | Frontiers of Eberron: Quickstone | Rare | Ranged Weapon | 643 gp | 4,066 gp | 3,422 gp | 531.98% | formula/ML-only |
| Demonglass Scimitar | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 643 gp | 4,066 gp | 3,422 gp | 531.98% | formula/ML-only |
| Demonglass Sling | Frontiers of Eberron: Quickstone | Rare | Ranged Weapon | 643 gp | 4,066 gp | 3,422 gp | 531.98% | formula/ML-only |
| Demonglass Spear | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 643 gp | 4,066 gp | 3,422 gp | 531.98% | formula/ML-only |
| Demonglass Whip | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 643 gp | 4,066 gp | 3,422 gp | 531.98% | formula/ML-only |
| Demonglass Mace | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 647 gp | 4,080 gp | 3,434 gp | 530.99% | formula/ML-only |
| Demonglass Quarterstaff | Frontiers of Eberron: Quickstone | Rare | Melee Weapon | 647 gp | 4,080 gp | 3,434 gp | 530.99% | formula/ML-only |

## Anchor-tier transitions / ML R² / double-count audit

- Anchor-tier transition and ML R² checks require pipeline metadata not present in final CSV snapshots; add those columns to future candidate snapshots if needed.
- Use the known-good and reference-anchored sections above as the first-pass double-count audit for extraction-driven price creep.
- Formula exposure reports (for example, extra_damage impact) are not final-price deltas.
