import pandas as pd

# Load the validated items
df = pd.read_csv('data/processed/items_validated.csv')

# Filter for standard items
has_amalg = df[
    df['amalgamated_price'].notna() & 
    df['variant_price'].isna() & 
    (df['price_confidence'] != 'solo-outlier') &
    (~df['rarity'].isin(['non-magic', 'varies', 'mundane', 'Unknown'])) &
    (~df['name'].str.contains('Spell Scroll', na=False, case=False))
].copy()

# Calculate what the old price would have been (roughly 70% amalg, 30% ML)
has_amalg['old_hypothetical_price'] = (0.7 * has_amalg['amalgamated_price'] + 0.3 * has_amalg['ml_price']).round(2)
has_amalg['new_final_price'] = has_amalg['final_price'].round(2)

# Calculate the difference
has_amalg['diff'] = abs(has_amalg['new_final_price'] - has_amalg['old_hypothetical_price'])
has_amalg['diff_pct'] = (has_amalg['diff'] / has_amalg['old_hypothetical_price']) * 100

# Sort by largest percentage difference
top_diffs = has_amalg.sort_values('diff_pct', ascending=False).head(10)

print("Standard Magic Items most impacted by 100% Amalgamated weight (vs 70/30 blend):")
print("-" * 80)
for _, row in top_diffs.iterrows():
    print(f"Item: {row['name']} ({row['rarity']})")
    print(f"  Amalgamated Price: {row['amalgamated_price']:,.2f}")
    print(f"  ML Price:          {row['ml_price']:,.2f}")
    print(f"  Old 70/30 Blend:   {row['old_hypothetical_price']:,.2f}")
    print(f"  New Final Price:   {row['new_final_price']:,.2f}")
    print(f"  Difference:        {row['diff_pct']:.1f}%")
    print("-" * 80)
