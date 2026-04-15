import pandas as pd

df = pd.read_csv("data/processed/items_validated.csv")
items = ["Mantle of Spell Resistance", "Ring of Three Wishes", "Broom of Flying"]

for item in items:
    row = df[df['name'].str.lower() == item.lower()]
    if not row.empty:
        r = row.iloc[0]
        print(f"Item: {r['name']}")
        print(f"Rarity: {r['rarity']}")
        print(f"Amalgamated: {r['amalgamated_price']}")
        print(f"Rule Price: {r['rule_price']}")
        print(f"ML Price: {r['ml_price']}")
        print(f"Final Price: {r['final_price']}")
        print(f"Confidence: {r['confidence']}")
        print("-" * 30)
