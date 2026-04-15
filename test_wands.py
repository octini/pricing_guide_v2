import pandas as pd
df = pd.read_csv('data/processed/items_validated.csv')

wands = df[df['name'].str.startswith("Channeling Wand")]
print("Channeling Wands rule prices:")
for _, row in wands.iterrows():
    print(f"{row['name']}: {row['rule_price']:,.0f} gp")

