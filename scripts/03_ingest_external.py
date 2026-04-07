#!/usr/bin/env python3
"""Phase 3: Ingest DSA, MSRP, DMPG price guides → data/raw/ CSVs"""

import re
import sys
import requests
import pandas as pd
import pdfplumber
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils import normalize_item_name

# Source files
COMPREHENSIVE_XLSX = Path.home() / "Downloads" / "Magic Item Pricing Guide (Comprehensive).xlsx"
DMPG_PDF = Path.home() / "Downloads" / "DMPG.pdf"

OUT_DIR = Path("data/raw")


def fetch_dsa() -> pd.DataFrame:
    """Extract DSA guide from comprehensive Excel. Uses 'Cost (gp)' column."""
    print("Extracting DSA from comprehensive guide...")
    
    if not COMPREHENSIVE_XLSX.exists():
        print(f"  WARNING: Comprehensive guide not found at {COMPREHENSIVE_XLSX}")
        return pd.DataFrame(columns=["item_name", "price_gp", "normalized_name", "source"])
    
    df = pd.read_excel(COMPREHENSIVE_XLSX, sheet_name="Master")
    print(f"  DSA raw columns: {list(df.columns)[:10]}")
    print(f"  DSA shape: {df.shape}")
    
    # Use 'Item Name' and 'Cost (gp)' columns
    name_col = "Item Name"
    price_col = "Cost (gp)"
    
    df = df[[name_col, price_col]].copy()
    df = df.rename(columns={name_col: "item_name", price_col: "price_gp"})
    df = df.dropna(subset=["item_name"])
    df["item_name"] = df["item_name"].astype(str)
    df["price_gp"] = pd.to_numeric(df["price_gp"], errors="coerce")
    df = df.dropna(subset=["price_gp"])
    df["normalized_name"] = df["item_name"].apply(normalize_item_name)
    df["source"] = "DSA"
    return df


def fetch_msrp() -> pd.DataFrame:
    """Extract MSRP guide from comprehensive Excel. Same data, different source label."""
    print("Extracting MSRP from comprehensive guide...")
    
    if not COMPREHENSIVE_XLSX.exists():
        print(f"  WARNING: Comprehensive guide not found at {COMPREHENSIVE_XLSX}")
        return pd.DataFrame(columns=["item_name", "price_gp", "normalized_name", "source"])
    
    df = pd.read_excel(COMPREHENSIVE_XLSX, sheet_name="Master")
    print(f"  MSRP raw columns: {list(df.columns)[:10]}")
    print(f"  MSRP shape: {df.shape}")
    
    # Use 'Item Name' and 'Cost (gp)' columns
    name_col = "Item Name"
    price_col = "Cost (gp)"
    
    df = df[[name_col, price_col]].copy()
    df = df.rename(columns={name_col: "item_name", price_col: "price_gp"})
    df = df.dropna(subset=["item_name"])
    df["item_name"] = df["item_name"].astype(str)
    df["price_gp"] = pd.to_numeric(df["price_gp"], errors="coerce")
    df = df.dropna(subset=["price_gp"])
    df["normalized_name"] = df["item_name"].apply(normalize_item_name)
    df["source"] = "MSRP"
    return df


def parse_dmpg() -> pd.DataFrame:
    """Parse DMPG PDF to extract item name and price."""
    print(f"Parsing DMPG from {DMPG_PDF}...")
    if not DMPG_PDF.exists():
        print(f"  WARNING: DMPG.pdf not found at {DMPG_PDF}")
        return pd.DataFrame(columns=["item_name", "price_gp", "normalized_name", "source"])

    rows = []
    with pdfplumber.open(DMPG_PDF) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if row and len(row) >= 2:
                        name = str(row[0] or "").strip()
                        price_str = str(row[1] or "").strip()
                        price_str = re.sub(r'[,gG pP\s]', '', price_str)
                        try:
                            price = float(price_str)
                            if price > 0 and name:
                                rows.append({"item_name": name, "price_gp": price})
                        except ValueError:
                            pass

    if not rows:
        # Fallback: extract text-based price patterns
        with pdfplumber.open(DMPG_PDF) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                for line in text.split('\n'):
                    m = re.match(r'^(.+?)\s+(\d[\d,]+)\s*gp?', line, re.IGNORECASE)
                    if m:
                        name = m.group(1).strip()
                        price = float(m.group(2).replace(',', ''))
                        rows.append({"item_name": name, "price_gp": price})

    df = pd.DataFrame(rows)
    if len(df) > 0:
        df["normalized_name"] = df["item_name"].apply(normalize_item_name)
        df["source"] = "DMPG"
    print(f"  DMPG: extracted {len(df)} items")
    return df


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    dsa = fetch_dsa()
    dsa.to_csv(OUT_DIR / "dsa_prices.csv", index=False)
    print(f"  Saved {len(dsa)} DSA items to data/raw/dsa_prices.csv")

    msrp = fetch_msrp()
    msrp.to_csv(OUT_DIR / "msrp_prices.csv", index=False)
    print(f"  Saved {len(msrp)} MSRP items to data/raw/msrp_prices.csv")

    dmpg = parse_dmpg()
    dmpg.to_csv(OUT_DIR / "dmpg_prices.csv", index=False)
    print(f"  Saved {len(dmpg)} DMPG items to data/raw/dmpg_prices.csv")

    print(f"\nTotal external prices: DSA={len(dsa)}, MSRP={len(msrp)}, DMPG={len(dmpg)}")


if __name__ == "__main__":
    main()
