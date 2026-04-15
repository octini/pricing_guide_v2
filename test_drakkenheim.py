import pandas as pd

df = pd.read_csv('data/processed/items_validated.csv')

items = ["Sceptre of Saint Vitruvio", "Phylactery of Saint Vitruvio", "Helm of Patron Saints", "Prospector's Wand"]

for item in items:
    match = df[df['name'] == item]
    if len(match):
        print(f"{item}: {match.iloc[0]['final_price']:,.0f} gp (rule_price: {match.iloc[0]['rule_price']:,.0f} gp)")
    else:
        print(f"{item}: NOT FOUND")
