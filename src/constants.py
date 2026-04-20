# src/constants.py
"""Shared constants for the pricing pipeline."""

# Rarity median prices (calibrated from actual data)
# Used for single-source outlier detection
RARITY_MEDIANS = {
    "mundane": 1,
    "common": 132,
    "uncommon": 852,
    "rare": 3890,
    "very_rare": 13450,
    "legendary": 46500,
    "artifact": 150000,
}

# Condition immunity values (gp premium per condition)
CONDITION_IMMUNITY_VALUES = {
    "frightened": 400,
    "charmed": 400,
    "poisoned": 400,
    "exhaustion": 400,
    "petrified": 400,
    "paralyzed": 400,
    "blinded": 400,
    "deafened": 400,
    "stunned": 400,
    "incapacitated": 400,
    "prone": 400,
    "restrained": 400,
}
