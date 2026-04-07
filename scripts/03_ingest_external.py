#!/usr/bin/env python3
"""Phase 3: Ingest DSA, MSRP, DMPG price guides → data/raw/ CSVs

Sources:
  - DSA: Pre-cleaned CSV from prior project (pricing_guide_2)
  - MSRP: Pre-cleaned CSV from prior project (pricing_guide_2)
  - DMPG: Re-parsed from DMPG.pdf with name cleaning
"""

import re
import sys
import pandas as pd
import pdfplumber
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils import normalize_item_name

# Prior project pre-cleaned CSVs (columns: item_name, price, source)
PRIOR_PROJECT = Path("/Users/ryan/OpenCode/TTRPG/pricing_guide_2/data/raw")
DSA_SOURCE = PRIOR_PROJECT / "dsa_prices_clean.csv"
MSRP_SOURCE = PRIOR_PROJECT / "msrp_prices_clean.csv"
DMPG_PDF = Path.home() / "Downloads" / "DMPG.pdf"

OUT_DIR = Path("data/raw")

# Rarity words that appear in DMPG name column (to strip out)
RARITY_WORDS = {
    "common", "uncommon", "rare", "very rare", "legendary", "artifact",
    "yes", "no",  # attunement tokens
}


def clean_dmpg_name(raw_name: str) -> str:
    """Strip attunement (Yes/No) and rarity suffix from DMPG item names.

    DMPG PDF rows look like: 'Absorbing Tattoo Yes Very Rare'
    We want:                  'Absorbing Tattoo'
    """
    # Remove trailing rarity + attunement combos in any order
    # Strategy: strip known tokens from the end
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
    # If nothing left after stripping, return original (avoid empty)
    return cleaned if cleaned else raw_name.strip()


def load_dsa() -> pd.DataFrame:
    """Load DSA price guide from prior project clean CSV."""
    print(f"Loading DSA from {DSA_SOURCE}...")
    if not DSA_SOURCE.exists():
        print(f"  WARNING: DSA source not found at {DSA_SOURCE}")
        return pd.DataFrame(columns=["item_name", "price_gp", "normalized_name", "source"])

    df = pd.read_csv(DSA_SOURCE)
    # Prior project columns: item_name, price, source
    df = df.rename(columns={"price": "price_gp"})
    df["price_gp"] = pd.to_numeric(df["price_gp"], errors="coerce")
    df = df.dropna(subset=["price_gp"])
    df = df[df["price_gp"] > 0]
    df["normalized_name"] = df["item_name"].apply(normalize_item_name)
    df["source"] = "DSA"
    df = df[["item_name", "price_gp", "normalized_name", "source"]]
    print(f"  DSA: {len(df)} items, price range: {df['price_gp'].min():.0f} - {df['price_gp'].max():.0f} gp")
    return df


def load_msrp() -> pd.DataFrame:
    """Load MSRP price guide from prior project clean CSV."""
    print(f"Loading MSRP from {MSRP_SOURCE}...")
    if not MSRP_SOURCE.exists():
        print(f"  WARNING: MSRP source not found at {MSRP_SOURCE}")
        return pd.DataFrame(columns=["item_name", "price_gp", "normalized_name", "source"])

    df = pd.read_csv(MSRP_SOURCE)
    # Prior project columns: item_name, price, source
    df = df.rename(columns={"price": "price_gp"})
    df["price_gp"] = pd.to_numeric(df["price_gp"], errors="coerce")
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
        print(f"  WARNING: DMPG.pdf not found at {DMPG_PDF}")
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
                        price_str = re.sub(r'[,gG pP\s]', '', price_str)
                        try:
                            price = float(price_str)
                            if price > 0 and raw_name:
                                name = clean_dmpg_name(raw_name)
                                if name:
                                    rows.append({"item_name": name, "price_gp": price})
                        except ValueError:
                            pass

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
        # Filter out junk rows where the "name" is just rarity/attunement words
        df = df[df["item_name"].str.len() > 5]  # must have at least 6 chars
        df = df[~df["item_name"].str.lower().str.match(r'^(yes|no)\s+(very rare|uncommon|rare|common|legendary|artifact)$')]
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
