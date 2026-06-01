"""
import_data.py
-------------
Converts the raw pharmacy and lab text files into Excel format
so they can be reviewed in spreadsheet tools and shared with
non-technical stakeholders.

Usage:
    python scripts/import_data.py
"""

import pandas as pd
from pathlib import Path

RAW       = Path("data/raw")
PROCESSED = Path("data/processed")
PROCESSED.mkdir(parents=True, exist_ok=True)


def convert(filename: str, label: str) -> pd.DataFrame:
    df = pd.read_csv(RAW / filename)
    out = PROCESSED / filename.replace(".txt", ".xlsx")
    df.to_excel(out, index=False)
    print(f"✓ {label}")
    print(f"  {df.shape[0]} rows × {df.shape[1]} columns  →  {out}")
    print(df.head(5).to_string(index=False))
    print()
    return df


if __name__ == "__main__":
    print("\n=== Data Import ===\n")
    convert("Pharmacy_Claims.txt", "Pharmacy Claims")
    convert("Lab_Results.txt",     "Lab Results")
    print("Done. Files saved to data/processed/")
