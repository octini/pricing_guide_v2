#!/usr/bin/env python3
"""Phase 3: Ingest DSA, MSRP, DMPG price guides → data/raw/ CSVs

Sources:
  - DSA: DSA.csv in project root (Item Name, Cost (gp))
  - MSRP: MSRP.csv in project root (Item, MSRP (common), MSRP (rare)) — averages the two columns
  - DMPG: DMPG.pdf in project root (table extraction)
"""

import re
import sys
import pandas as pd
import pdfplumber
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils import normalize_item_name

PROJECT_ROOT = Path(__file__).parent.parent

DSA_CSV = PROJECT_ROOT / "DSA.csv"
MSRP_CSV = PROJECT_ROOT / "MSRP.csv"
DMPG_PDF = PROJECT_ROOT / "DMPG.pdf"

OUT_DIR = PROJECT_ROOT / "data" / "raw"

# Rarity/attunement words that appear contaminating DMPG item names
RARITY_WORDS = {
    "common", "uncommon", "rare", "legendary", "artifact",
    "yes", "no",
}


def _parse_gp(val):
    """Parse a price string like '1,234 gp' or '1234' to a float."""
    if val is None:
        return None
    s = str(val).strip().lower()
    s = re.sub(r'[,gp\s]', '', s)
    try:
        f = float(s)
        return f if f > 0 else None
    except ValueError:
        return None


def clean_dmpg_name(raw_name: str) -> str:
    """Strip attunement (Yes/No) and rarity suffix from DMPG item names.

    DMPG PDF rows look like: 'Absorbing Tattoo Yes Very Rare'
    We want:                  'Absorbing Tattoo'
    """
    tokens = raw_name.strip().split()
    result = []
    i = 0
    while i < len(tokens):
        token = tokens[i].lower()
        # Check for "Very Rare" two-word rarity
        if token == "very" and i + 1 < len(tokens) and tokens[i + 1].lower() == "rare":
            break
        if token in RARITY_WORDS:
            break
        result.append(tokens[i])
        i += 1
    cleaned = " ".join(result).strip()
    return cleaned if cleaned else raw_name.strip()


def load_dsa() -> pd.DataFrame:
    """Load DSA price guide from DSA.csv in project root.

    DSA.csv columns: Item Name, Rarity, Attunement, Cost (gp), ...
    """
    print(f"Loading DSA from {DSA_CSV}...")
    if not DSA_CSV.exists():
        print(f"  ERROR: DSA.csv not found at {DSA_CSV}")
        return pd.DataFrame(columns=["item_name", "price_gp", "normalized_name", "source"])

    df = pd.read_csv(DSA_CSV)
    # Normalise column names (strip whitespace)
    df.columns = df.columns.str.strip()

    if "Item Name" not in df.columns or "Cost (gp)" not in df.columns:
        print(f"  ERROR: Expected 'Item Name' and 'Cost (gp)' columns. Got: {list(df.columns)}")
        return pd.DataFrame(columns=["item_name", "price_gp", "normalized_name", "source"])

    df = df[["Item Name", "Cost (gp)"]].copy()
    df.columns = ["item_name", "price_gp"]
    df["price_gp"] = df["price_gp"].apply(_parse_gp)
    df = df.dropna(subset=["price_gp"])
    df = df[df["price_gp"] > 0]
    df["normalized_name"] = df["item_name"].apply(normalize_item_name)
    df["source"] = "DSA"
    df = df[["item_name", "price_gp", "normalized_name", "source"]]
    print(f"  DSA: {len(df)} items, price range: {df['price_gp'].min():.0f} - {df['price_gp'].max():.0f} gp")
    return df


def load_msrp() -> pd.DataFrame:
    """Load MSRP price guide from MSRP.csv in project root.

    MSRP.csv has a lookup block at the top, then a header row with:
      Item, MSRP (common), MSRP (rare), Sane Price, DMPG Price, ...
    We average 'MSRP (common)' and 'MSRP (rare)' to get the representative price.
    """
    print(f"Loading MSRP from {MSRP_CSV}...")
    if not MSRP_CSV.exists():
        print(f"  ERROR: MSRP.csv not found at {MSRP_CSV}")
        return pd.DataFrame(columns=["item_name", "price_gp", "normalized_name", "source"])

    # The CSV has junk rows at the top; find the real header row
    raw = pd.read_csv(MSRP_CSV, header=None, dtype=str)

    header_row = None
    for i, row in raw.iterrows():
        row_vals = [str(v).strip().lower() for v in row if pd.notna(v)]
        if any("msrp" in v and "common" in v for v in row_vals):
            header_row = i
            break

    if header_row is None:
        print("  ERROR: Could not find MSRP header row containing 'MSRP (common)'")
        return pd.DataFrame(columns=["item_name", "price_gp", "normalized_name", "source"])

    df = pd.read_csv(MSRP_CSV, header=header_row, dtype=str)
    df.columns = df.columns.str.strip()

    # Drop any leading unnamed column (the CSV has a blank first column)
    df = df.loc[:, ~df.columns.str.match(r'^Unnamed')]

    # Find item name and price columns
    item_col = next((c for c in df.columns if c.strip().lower() == "item"), None)
    common_col = next((c for c in df.columns if "msrp" in c.lower() and "common" in c.lower()), None)
    rare_col = next((c for c in df.columns if "msrp" in c.lower() and "rare" in c.lower()), None)

    if not item_col or not common_col or not rare_col:
        print(f"  ERROR: Missing expected columns. Found: {list(df.columns)}")
        return pd.DataFrame(columns=["item_name", "price_gp", "normalized_name", "source"])

    df = df[[item_col, common_col, rare_col]].copy()
    df.columns = ["item_name", "price_common", "price_rare"]
    df = df.dropna(subset=["item_name"])
    df = df[df["item_name"].str.strip() != ""]

    df["price_common"] = df["price_common"].apply(_parse_gp)
    df["price_rare"] = df["price_rare"].apply(_parse_gp)

    # Average common and rare; fall back to whichever is present
    def avg_prices(row):
        c, r = row["price_common"], row["price_rare"]
        if c is not None and r is not None:
            return (c + r) / 2.0
        return c or r

    df["price_gp"] = df.apply(avg_prices, axis=1)
    df = df.dropna(subset=["price_gp"])
    df = df[df["price_gp"] > 0]

    df["normalized_name"] = df["item_name"].apply(normalize_item_name)
    df["source"] = "MSRP"
    df = df[["item_name", "price_gp", "normalized_name", "source"]]
    print(f"  MSRP: {len(df)} items, price range: {df['price_gp'].min():.0f} - {df['price_gp'].max():.0f} gp")
    return df


def parse_dmpg() -> pd.DataFrame:
    """Parse DMPG PDF to extract item name and price, cleaning contaminated names."""
    print(f"Parsing DMPG from {DMPG_PDF}...")
    if not DMPG_PDF.exists():
        print(f"  ERROR: DMPG.pdf not found at {DMPG_PDF}")
        return pd.DataFrame(columns=["item_name", "price_gp", "normalized_name", "source"])

    rows = []
    with pdfplumber.open(DMPG_PDF) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if row and len(row) >= 2:
                        raw_name = str(row[0] or "").strip()
                        price_str = str(row[1] or "").strip()
                        price = _parse_gp(price_str)
                        if price and price > 0 and raw_name:
                            name = clean_dmpg_name(raw_name)
                            if name:
                                rows.append({"item_name": name, "price_gp": price})

    if not rows:
        # Fallback: text-based extraction
        with pdfplumber.open(DMPG_PDF) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                for line in text.split('\n'):
                    m = re.match(r'^(.+?)\s+(\d[\d,]+)\s*gp?', line, re.IGNORECASE)
                    if m:
                        raw_name = m.group(1).strip()
                        name = clean_dmpg_name(raw_name)
                        price = float(m.group(2).replace(',', ''))
                        if price > 0 and name:
                            rows.append({"item_name": name, "price_gp": price})

    df = pd.DataFrame(rows)
    if len(df) > 0:
        df["normalized_name"] = df["item_name"].apply(normalize_item_name)
        df["source"] = "DMPG"
        df = df[["item_name", "price_gp", "normalized_name", "source"]]
        # Filter junk rows
        df = df[df["item_name"].str.len() > 5]
        df = df[~df["item_name"].str.lower().str.match(
            r'^(yes|no)\s+(very rare|uncommon|rare|common|legendary|artifact)$'
        )]
    print(f"  DMPG: extracted {len(df)} items")
    if len(df) > 0:
        print(f"  DMPG price range: {df['price_gp'].min():.0f} - {df['price_gp'].max():.0f} gp")
    return df


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    dsa = load_dsa()
    dsa.to_csv(OUT_DIR / "dsa_prices.csv", index=False)
    print(f"  Saved {len(dsa)} DSA items to data/raw/dsa_prices.csv")

    msrp = load_msrp()
    msrp.to_csv(OUT_DIR / "msrp_prices.csv", index=False)
    print(f"  Saved {len(msrp)} MSRP items to data/raw/msrp_prices.csv")

    dmpg = parse_dmpg()
    dmpg.to_csv(OUT_DIR / "dmpg_prices.csv", index=False)
    print(f"  Saved {len(dmpg)} DMPG items to data/raw/dmpg_prices.csv")

    print(f"\nTotal external prices: DSA={len(dsa)}, MSRP={len(msrp)}, DMPG={len(dmpg)}")


if __name__ == "__main__":
    main()
