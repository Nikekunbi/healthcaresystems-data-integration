"""
clean_ehr.py
------------
Audits and fixes data quality issues in the EHR patient dataset.

Issues addressed:
  - Missing values (DateOfBirth, ZipCode)
  - Exact duplicate rows
  - Inconsistent Gender encoding (M/male/F)
  - Mixed AdmissionDate formats including Excel serial numbers

Usage:
    python scripts/clean_ehr.py
"""

import re
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

RAW       = Path("data/raw")
PROCESSED = Path("data/processed")
PROCESSED.mkdir(parents=True, exist_ok=True)


# ── Load ──────────────────────────────────────────────────────────
def load() -> pd.DataFrame:
    df = pd.read_csv(RAW / "Patients_EHR_raw_data.csv", encoding="utf-8-sig")
    print(f"Loaded: {df.shape[0]} rows × {df.shape[1]} columns\n")
    return df


# ── Audit ─────────────────────────────────────────────────────────
def audit(df: pd.DataFrame):
    print("=== Audit ===\n")

    print("Missing values:")
    print(df.isnull().sum().to_string())
    print(f"  Total: {df.isnull().sum().sum()}\n")

    print(f"Duplicate rows: {df.duplicated().sum()}\n")

    print("Gender distribution:")
    print(df["Gender"].value_counts().to_string())
    non_std = df[~df["Gender"].isin(["Male","Female"])]["Gender"].unique()
    print(f"  Non-standard: {list(non_std)}\n")

    def fmt(v):
        v = str(v).strip()
        if re.match(r"^\d{2}-\d{2}-\d{4}$", v): return "DD-MM-YYYY"
        if re.match(r"^\d{4}-\d{2}-\d{2}$", v): return "YYYY-MM-DD"
        try: float(v); return "Excel serial"
        except: return "Unknown"

    fmts = df["AdmissionDate"].apply(fmt).value_counts()
    print("AdmissionDate formats:")
    print(fmts.to_string())
    bad = df[df["AdmissionDate"].apply(fmt) != "DD-MM-YYYY"]
    if not bad.empty:
        print("\n  Non-standard rows:")
        print(bad[["PatientID","AdmissionDate"]].to_string(index=False))


# ── Fix ───────────────────────────────────────────────────────────
def fix_missing(df: pd.DataFrame) -> pd.DataFrame:
    df["DateOfBirth"] = df["DateOfBirth"].fillna("Unknown")
    df["ZipCode"]     = df["ZipCode"].fillna("Unknown")
    print(f"\n✓ Missing values filled")
    return df


def fix_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(keep="first")
    print(f"✓ Duplicates removed: {before - len(df)}  ({len(df)} rows remain)")
    return df


def fix_gender(df: pd.DataFrame) -> pd.DataFrame:
    df["Gender"] = df["Gender"].replace({
        "M": "Male", "m": "Male", "male": "Male",
        "F": "Female", "f": "Female"
    })
    print(f"✓ Gender standardized: {df['Gender'].value_counts().to_dict()}")
    return df


def fix_dates(df: pd.DataFrame) -> pd.DataFrame:
    def parse(val):
        v = str(val).strip()
        for fmt in ["%d-%m-%Y", "%Y-%m-%d"]:
            try: return datetime.strptime(v, fmt).strftime("%Y-%m-%d")
            except: pass
        try: return (datetime(1899,12,30) + timedelta(days=int(float(v)))).strftime("%Y-%m-%d")
        except: return v

    df["AdmissionDate"] = df["AdmissionDate"].apply(parse)
    df["AdmissionDate"] = pd.to_datetime(
        df["AdmissionDate"], infer_datetime_format=True, errors="coerce"
    ).dt.strftime("%Y-%m-%d")
    all_ok = df["AdmissionDate"].str.match(r"^\d{4}-\d{2}-\d{2}$").all()
    print(f"✓ Dates standardized (all YYYY-MM-DD: {all_ok})")
    return df


def save(df: pd.DataFrame):
    out = PROCESSED / "Patients_EHR_cleaned.csv"
    df.to_csv(out, index=False)
    print(f"\n✓ Saved: {out}  ({df.shape[0]} rows × {df.shape[1]} columns)")


# ── Main ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    df = load()
    audit(df)
    print("\n=== Fixes ===")
    df = fix_missing(df)
    df = fix_duplicates(df)
    df = fix_gender(df)
    df = fix_dates(df)
    save(df)
