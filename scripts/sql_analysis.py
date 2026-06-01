"""
sql_analysis.py
---------------
Builds a local SQLite database from the three healthcare datasets
and runs cross-system queries joining patients, pharmacy claims,
and lab results.

Usage:
    python scripts/sql_analysis.py
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

RAW       = Path("data/raw")
PROCESSED = Path("data/processed")
PROCESSED.mkdir(parents=True, exist_ok=True)
DB        = PROCESSED / "medical_data.db"


def _parse_date(val):
    v = str(val).strip()
    for fmt in ["%d-%m-%Y", "%Y-%m-%d"]:
        try: return datetime.strptime(v, fmt).strftime("%Y-%m-%d")
        except: pass
    try: return (datetime(1899,12,30)+timedelta(days=int(float(v)))).strftime("%Y-%m-%d")
    except: return v


def build_db() -> sqlite3.Connection:
    """Load, clean, and store all three datasets in SQLite."""
    ehr = pd.read_csv(RAW / "Patients_EHR_raw_data.csv", encoding="utf-8-sig")
    ehr["DateOfBirth"]   = ehr["DateOfBirth"].fillna("Unknown")
    ehr["ZipCode"]       = ehr["ZipCode"].fillna("Unknown")
    ehr.drop_duplicates(inplace=True)
    ehr["Gender"]        = ehr["Gender"].replace({"M":"Male","m":"Male","male":"Male","F":"Female","f":"Female"})
    ehr["AdmissionDate"] = ehr["AdmissionDate"].apply(_parse_date)
    ehr["DateOfBirth"]   = ehr["DateOfBirth"].apply(lambda x: _parse_date(x) if x != "Unknown" else x)

    pc = pd.read_csv(RAW / "Pharmacy_Claims.txt")
    lr = pd.read_csv(RAW / "Lab_Results.txt")

    conn = sqlite3.connect(DB)
    ehr.to_sql("patients",        conn, if_exists="replace", index=False)
    pc.to_sql("pharmacy_claims",  conn, if_exists="replace", index=False)
    lr.to_sql("lab_results",      conn, if_exists="replace", index=False)
    conn.commit()

    print(f"Database: {DB}")
    print(f"  patients:        {len(ehr)} rows")
    print(f"  pharmacy_claims: {len(pc)} rows")
    print(f"  lab_results:     {len(lr)} rows\n")
    return conn


def query(conn, title: str, sql: str):
    print(f"{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")
    print(f"\n{sql.strip()}\n")
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))
    print(f"\n  → {len(df)} rows\n")


if __name__ == "__main__":
    conn = build_db()

    query(conn, "Patients born before 1980", """
        SELECT PatientID, Gender, DateOfBirth
        FROM   patients
        WHERE  DateOfBirth < '1980-01-01'
          AND  DateOfBirth != 'Unknown'
        ORDER  BY DateOfBirth;
    """)

    query(conn, "Female patients with Type 2 Diabetes", """
        SELECT PatientID, Gender, DateOfBirth, PrimaryCondition
        FROM   patients
        WHERE  Gender = 'Female'
          AND  PrimaryCondition LIKE '%Type 2 Diabetes%'
        ORDER  BY PatientID;
    """)

    query(conn, "Lab results joined with patient demographics", """
        SELECT p.PatientID, p.Gender, p.DateOfBirth,
               l.TestName, l.TestResultValue, l.Units, l.AbnormalFlag
        FROM   patients    p
        JOIN   lab_results l ON p.PatientID = l.PatientID
        ORDER  BY p.PatientID, l.TestName;
    """)

    query(conn, "Patients and their insurance payer(s)", """
        SELECT DISTINCT p.PatientID, p.Gender, p.DateOfBirth, pc.Payer
        FROM   patients        p
        JOIN   pharmacy_claims pc ON p.PatientID = pc.PatientID
        ORDER  BY p.PatientID;
    """)

    conn.close()
