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

# Expensive armor base costs (PHB prices)
# Used to prevent magic variants from being cheaper than mundane base
# IMPORTANT: Order matters! More specific names must come before substrings
# e.g., "half plate" must come before "plate armor" to avoid false matches
EXPENSIVE_ARMOR_BASES = {
    "half plate": 750,  # Must come before "plate armor"
    "plate armor": 1500,
    "splint armor": 200,
    "chain mail": 75,
    "breastplate": 400,
    "ring mail": 30,
    "scale mail": 50,
    "chain shirt": 50,
    "hide armor": 10,
    "leather armor": 10,
    "padded armor": 5,
    "studded leather": 45,
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
