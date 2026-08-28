# Resistance-Armor Pricing Consistency Analysis

Date: 2026-08-27. Trigger: user spot-check on the 50-item sample
(pricing_guide_v2-zda). Scope: analysis only — no prices changed.

## Executive summary

The Demon Skin armor family (poison resistance AND removal of heavy-armor
stealth disadvantage) prices 708-2,928 gp BELOW the equivalent
"Armor of Poison Resistance" items (poison resistance only, stealth penalty
retained). The premium for being strictly better is negative. Root cause:
the engine prices damage resistance (300 gp additive) but never prices
stealth-disadvantage removal — `stealth_penalty` is extracted from prose but
consumed nowhere in `calculate_price` (only `stealth_advantage` is priced,
+400 gp).

## Table 1 — Demon Skin family (all Rare, Heavy Armor, Algorithm-priced)

| Item | Price (gp) | Resistance | Stealth penalty |
|---|---:|---|---|
| Demon Skin Chain Mail | 4,026.64 | poison | removed |
| Demon Skin Ring Mail | 3,685.68 | poison | removed |
| Demon Skin Splint Armor | 4,050.00 | poison | removed |
| Demon Skin Plate Armor | 5,220.00 | poison | removed |

## Table 2 — Armor of Poison Resistance equivalents (sampled)

| Armor type | Price (gp) | Stealth penalty | Source |
|---|---:|---|---|
| Chain Mail | 4,734.70 | kept | Algorithm |
| Ring Mail | 4,496.08 | kept | Algorithm |
| Splint | 4,900.13 | kept | Algorithm |
| Plate | 8,147.98 | kept | Single source (DSA) |
| Hide | 4,268.72 | kept | Algorithm |
| Breastplate | 4,662.58 | kept | Algorithm |
| Half Plate | 4,929.27 | kept | Algorithm |
| Scale | 4,505.08 | kept | Algorithm |

## Table 3 — Inversion deltas (Demon Skin minus equivalent)

| Armor type | Delta gp | Delta % |
|---|---:|---:|
| Splint | -850 | -17.3% |
| Chain Mail | -708 | -15.0% |
| Ring Mail | -810 | -18.0% |
| Plate | -2,928 | -35.9% |

## Table 4 — Full sweep (all damage types)

NOT ENUMERATED HERE. The full sweep (all resistance-granting armors across
fire/cold/acid/lightning/thunder/necrotic/radiant/psychic/force vs their
Armor of [X] Resistance equivalents, ~170 resistance rows in criteria) is
deferred into the adjustment ritual's impact report, where every affected
item must be enumerated regardless. The Demon Skin/Poison inversion
demonstrates the mechanism; the ritual will quantify the full blast radius.

## Analysis

- Damage resistance: +300 gp per type (pricing_engine additive).
- Stealth-disadvantage removal: 0 gp — extracted (`stealth_penalty`) but
  never priced. Parity with `stealth_advantage` (+400 gp) suggests ~400 gp
  value.
- Variant adjustments amplify the gap (Demon Skin generic-parent adjustments
  -0.625 to +0.375; Armor of Poison Resistance 0 to +0.571).
- The Plate inversion (-35.9%) is exaggerated by a single-source DSA anchor
  (12,000 gp) on the Armor of Poison Resistance Plate.

## Recommendation options

a) Adjust Demon Skin family up (+400-800 gp each; 4 items; ~+1.6-3.2k gp exposure).
b) Adjust Armor of [X] Resistance down toward Demon Skin baseline (~70 Algorithm rows; ~-30-50k gp exposure).
c) Accept as anchor/variant noise; document and monitor.
d) RECOMMENDED: price stealth-disadvantage removal at 400 gp (parity with
   stealth_advantage) in the engine, then let the ritual quantify and apply —
   fixes the root cause for the whole population instead of patching one
   family, and the 12k run inherits correct semantics.

Any adjustment ships through the standard ritual: impact report -> guardrail ->
anchor-drift review -> user sign-off.
