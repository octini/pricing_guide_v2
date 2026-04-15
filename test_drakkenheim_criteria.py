import pandas as pd
df = pd.read_csv('data/processed/items_criteria.csv')
items = ["Sceptre of Saint Vitruvio", "Helm of Patron Saints", "Prospector's Wand"]

cols = ['name', 'charges', 'attached_spells', 'wish_effect']
for item in items:
    match = df[df['name'] == item]
    if len(match):
        print(match[cols].to_dict('records')[0])
