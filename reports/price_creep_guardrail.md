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
