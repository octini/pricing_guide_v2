#!/usr/bin/env python3
"""Phase 8: Generate Excel and CSV output"""

import sys
import csv
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter
from pathlib import Path

INPUT_CSV = Path('data/processed/items_validated.csv')
OUTPUT_XLSX = Path('output/pricing_guide.xlsx')
OUTPUT_CSV = Path('output/pricing_guide.csv')

RARITY_COLORS = {
    'mundane': 'F5F5F5',
    'common': 'FFFFFF',
    'uncommon': '1EFF00',
    'rare': '0070DD',
    'very_rare': 'A335EE',
    'legendary': 'FF8000',
    'artifact': 'E6CC80',
    'unknown_magic': 'DDDDDD',
    'unknown': 'EEEEEE',
    'varies': 'BBBBBB',
}

RARITY_TEXT_COLORS = {
    'uncommon': '000000',
    'rare': 'FFFFFF',
    'very_rare': 'FFFFFF',
    'legendary': '000000',
    'artifact': '000000',
}

def format_price(price_gp):
    if price_gp < 1:
        return f"{int(price_gp * 100)} cp"
    elif price_gp < 10:
        return f"{price_gp:.1f} gp"
    else:
        return f"{int(price_gp):,} gp"

def determine_price_source_label(row):
    if row.get('price_source') == 'official':
        return 'Official'
    elif row.get('price_confidence') == 'multi':
        return f"Amalgamated ({row.get('price_sources', '')})"
    elif row.get('price_confidence') == 'solo':
        return f"Single source ({row.get('price_sources', '')})"
    else:
        return 'Algorithm'

def main():
    df = pd.read_csv(INPUT_CSV)
    print(f'Loaded {len(df)} items')
    
    # Exclude generic variants (items with 'items' field in raw JSON)
    # These are placeholder items like "Horn of Valhalla" that have specific variants
    if 'is_generic_variant' in df.columns:
        before = len(df)
        df = df[~df['is_generic_variant'].fillna(False)]
        print(f'Excluded {before - len(df)} generic variants')

    output_rows = []
    for _, row in df.iterrows():
        price = row.get('final_price', row.get('rule_price', 0))
        output_rows.append({
            'Name': row['name'],
            'Source': row['source'],
            'Type': row.get('type', ''),
            'Rarity': row['rarity'].replace('_', ' ').title(),
            'Attunement': row.get('req_attune', 'none').replace('none', 'No'),
            'Price (gp)': round(float(price), 2) if pd.notna(price) else 0,
            'Price Formatted': format_price(float(price)) if pd.notna(price) else '0 gp',
            'Price Source': determine_price_source_label(row.to_dict()),
            'URL': row.get('url', ''),
            'Is Outlier': row.get('is_outlier', False),
        })

    out_df = pd.DataFrame(output_rows)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    csv_df = out_df.drop(columns=['URL', 'Is Outlier'])
    csv_df.to_csv(OUTPUT_CSV, index=False, quoting=csv.QUOTE_ALL)
    print(f'Saved CSV to {OUTPUT_CSV}')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Pricing Guide'

    headers = ['Name', 'Source', 'Type', 'Rarity', 'Attunement', 'Price (gp)', 'Price Source', 'Notes']
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.fill = PatternFill(start_color='2F4F4F', end_color='2F4F4F', fill_type='solid')
        cell.font = Font(bold=True, color='FFFFFF')
        cell.alignment = Alignment(horizontal='center')

    ws.freeze_panes = 'A2'

    for row_idx, row in enumerate(output_rows, 2):
        rarity_key = row['Rarity'].lower().replace(' ', '_')
        bg_color = RARITY_COLORS.get(rarity_key, 'FFFFFF')
        text_color = RARITY_TEXT_COLORS.get(rarity_key, '000000')

        fill = PatternFill(start_color=bg_color, end_color=bg_color, fill_type='solid')
        font_normal = Font(color=text_color, size=10)
        font_link = Font(color='0563C1', underline='single', size=10)

        name_cell = ws.cell(row=row_idx, column=1, value=row['Name'])
        if row['URL']:
            name_cell.hyperlink = row['URL']
            name_cell.font = font_link
        else:
            name_cell.font = font_normal
        name_cell.fill = fill

        values = [
            row['Source'],
            row['Type'],
            row['Rarity'],
            row['Attunement'],
            row['Price Formatted'],
            row['Price Source'],
            '⚠️' if row['Is Outlier'] else ''
        ]

        for col_offset, val in enumerate(values, 2):
            cell = ws.cell(row=row_idx, column=col_offset, value=val)
            cell.font = font_normal
            cell.fill = fill
            cell.alignment = Alignment(horizontal='left')

    col_widths = [35, 12, 15, 12, 15, 18, 30, 8]
    for col_idx, width in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"

    wb.save(OUTPUT_XLSX)
    print(f'Saved Excel to {OUTPUT_XLSX}')

    print(f'\nTotal items: {len(output_rows)}')
    print(f"Hyperlinked items: {sum(1 for r in output_rows if r['URL'])}")

if __name__ == '__main__':
    main()
