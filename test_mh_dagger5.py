import pandas as pd
from src.criteria_extractor import extract_entries_criteria
import json

df = pd.read_csv('data/processed/items_master.csv')
row = df[df['name'] == "Monster Hunter's Dagger +1"].iloc[0]
item = json.loads(row["raw_json"])
entries = extract_entries_criteria(item)
print("wish effect in entries:", entries.get('wish_effect', 'NOT FOUND'))
