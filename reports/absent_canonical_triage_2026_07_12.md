# 2026-07-12 Absent Canonical Row Triage

Raw input: `2026_07_12_item_list.json` (left untracked).
Canonical reference: `trimmed_5etools_list.json`.
No canonical migration, full pricing run, or processed/published output generation was performed.

## Summary

- Canonical rows: 4837
- Raw 2026 rows: 12243
- Curated 2026 rows after hard exclusions: 12241
- Canonical rows absent from raw 2026 by exact `(name, source)`: 31
- Canonical rows absent from curated 2026 by exact `(name, source)`: 33
- Additional curated-absent rows caused by hard exclusions: 2
- Unclassified rows: 0
- Recommendation: approve all classified omissions; no manual carry-forward required.

## Classification counts

| Classification | Rows |
|---|---:|
| hard exclusion — QftIS grenade | 2 |
| intentional draft exclusion — Ravnica/RMBRE draft-only | 1 |
| intentional draft exclusion — WttHC draft-only | 6 |
| intentional scope exclusion — Spelljammer/space | 21 |
| source-code rename — VRGR → RHW | 1 |
| superseded draft row — WttHC replaced by XDMG | 2 |

## Sensitive presence checks

- Crystal raw rows: Crystal (MonstersOfDrakkenheim), Crystal (XPHB); classification: keep-separate.
- Crystal curated rows: Crystal (MonstersOfDrakkenheim), Crystal (XPHB); classification: keep-separate.
- Harkon's Bite source-code rename is classified explicitly as VRGR → RHW when present.

## Full absent row triage

| # | Name | Source | Rarity | Type | Raw exact present | Curated exact present | Present by name in raw | Price | Classification | Rationale |
|---:|---|---|---|---|---|---|---|---:|---|---|
| 1 | Basic Fishing Equipment | AAG | none | G | no | no | — | 10 cp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 2 | Bombard | AAG | none | SPC\|AAG | no | no | — | 50,000 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 3 | Damselfly Ship | AAG | none | SPC\|AAG | no | no | — | 20,000 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 4 | Fish Suit | AAG | very rare |  | no | no | — | 18,171 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 5 | Flying Fish Ship | AAG | none | SPC\|AAG | no | no | — | 20,000 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 6 | Hammerhead Ship | AAG | none | SPC\|AAG | no | no | — | 40,000 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 7 | Lamprey Ship | AAG | none | SPC\|AAG | no | no | — | 20,000 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 8 | Living Ship | AAG | none | SPC\|AAG | no | no | — | 25,000 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 9 | Nautiloid | AAG | none | SPC\|AAG | no | no | — | 50,000 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 10 | Nightspider | AAG | none | SPC\|AAG | no | no | — | 50,000 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 11 | Scorpion Ship | AAG | none | SPC\|AAG | no | no | — | 25,000 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 12 | Shrike Ship | AAG | none | SPC\|AAG | no | no | — | 20,000 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 13 | Space Galleon | AAG | none | SPC\|AAG | no | no | — | 30,000 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 14 | Spelljamming Helm | AAG | rare |  | no | no | — | 3,267 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 15 | Squid Ship | AAG | none | SPC\|AAG | no | no | — | 25,000 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 16 | Star Moth | AAG | none | SPC\|AAG | no | no | — | 40,000 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 17 | Turtle Ship | AAG | none | SPC\|AAG | no | no | — | 40,000 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 18 | Tyrant Ship | AAG | none | SPC\|AAG | no | no | — | 1.0 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 19 | Wasp Ship | AAG | none | SPC\|AAG | no | no | — | 20,000 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 20 | Wildspace Orrery | AAG | uncommon |  | no | no | — | 718 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 21 | Talarith | BAM | legendary |  | no | no | — | 47,508 gp (name-only) | intentional scope exclusion — Spelljammer/space | AAG/BAM Spelljammer/space scope intentionally absent from 2026 curation candidate. |
| 22 | Concussion Grenade | QftIS | none | EXP\|DMG | yes | no | Concussion Grenade (QftIS) | 1.0 gp (name-only) | hard exclusion — QftIS grenade | Approved exact hard exclusion from curation policy. |
| 23 | Sleep Grenade | QftIS | none | EXP\|DMG | yes | no | Sleep Grenade (QftIS) | 1.0 gp (name-only) | hard exclusion — QftIS grenade | Approved exact hard exclusion from curation policy. |
| 24 | Concertina | RMBRE | rare |  | no | no | — | 3,355 gp (name-only) | intentional draft exclusion — Ravnica/RMBRE draft-only | Ravnica draft row omitted from the 2026 curation candidate. |
| 25 | Harkon's Bite | VRGR | uncommon |  | no | no | Harkon's Bite (RHW) | 804 gp (name-only) | source-code rename — VRGR → RHW | Same item is present under the updated source code. |
| 26 | Cap of Vanishing | WttHC | uncommon |  | no | no | — | 1,053 gp (name-only) | intentional draft exclusion — WttHC draft-only | Wayfinder/Eberron draft-only row omitted from the 2026 curation candidate. |
| 27 | Cloak of Billowing | WttHC | common |  | no | no | Cloak of Billowing (XDMG) | 147 gp (name-only) | superseded draft row — WttHC replaced by XDMG | Draft Wayfinder/Eberron row is superseded by the 2024 XDMG entry. |
| 28 | Dread Helm | WttHC | common |  | no | no | Dread Helm (XDMG) | 159 gp (name-only) | superseded draft row — WttHC replaced by XDMG | Draft Wayfinder/Eberron row is superseded by the 2024 XDMG entry. |
| 29 | Holly's Handy Haversack | WttHC | rare |  | no | no | — | 3,355 gp (name-only) | intentional draft exclusion — WttHC draft-only | Wayfinder/Eberron draft-only row omitted from the 2026 curation candidate. |
| 30 | Pipes of Pestilence | WttHC | uncommon |  | no | no | — | 745 gp (name-only) | intentional draft exclusion — WttHC draft-only | Wayfinder/Eberron draft-only row omitted from the 2026 curation candidate. |
| 31 | Poison Soaked Kukri | WttHC | uncommon | M\|XPHB | no | no | — | 699 gp (name-only) | intentional draft exclusion — WttHC draft-only | Wayfinder/Eberron draft-only row omitted from the 2026 curation candidate. |
| 32 | Speaking Stones | WttHC | rare |  | no | no | — | 3,804 gp (name-only) | intentional draft exclusion — WttHC draft-only | Wayfinder/Eberron draft-only row omitted from the 2026 curation candidate. |
| 33 | Spiked Shield | WttHC | uncommon | S\|XPHB | no | no | — | 887 gp (name-only) | intentional draft exclusion — WttHC draft-only | Wayfinder/Eberron draft-only row omitted from the 2026 curation candidate. |

## Migration recommendation

Recommendation: approve all classified omissions; no manual carry-forward required.
Proceed only after this report is reviewed; do not manually carry forward these rows unless the recommendation changes.
