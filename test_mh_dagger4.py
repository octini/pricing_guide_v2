import pandas as pd
from pathlib import Path
from src.criteria_extractor import extract_structured_criteria, extract_prose_criteria, extract_entries_criteria
from src.prose_loader import load_prose_descriptions
import json

prose_map = load_prose_descriptions(Path('items-sublist.md'))
df = pd.read_csv('data/processed/items_master.csv')
row = df[df['name'] == "Monster Hunter's Dagger +1"].iloc[0]

item_name_lower = row["name"].lower()
prose_text = prose_map.get(item_name_lower, "")
print("Prose:", prose_text)

prose = extract_prose_criteria(prose_text)
print("Wish effect:", prose['wish_effect'])
