"""
analyze_claims_and_labs.py
--------------------------
Analyzes pharmacy billing data and lab diagnostic results
to surface operational and clinical insights.

Usage:
    python scripts/analyze_claims_and_labs.py
"""

import pandas as pd
from pathlib import Path

RAW = Path("data/raw")


def pharmacy_analysis(df: pd.DataFrame):
    print("=== Pharmacy Claims Analysis ===\n")

    # Claims where the paid amount exceeded $250
    high_paid = df[df["PaidAmount"] > 250]
    print(f"Claims with PaidAmount > $250:  {len(high_paid)}")

    # Total reimbursed per payer
    by_payer = df.groupby("Payer")["PaidAmount"].sum().sort_values(ascending=False)
    print("\nTotal reimbursed by payer:")
    for payer, total in by_payer.items():
        print(f"  {payer:<12}  ${total:>9,.2f}")

    top = by_payer.idxmax()
    print(f"\nHighest payer:  {top}  (${by_payer[top]:,.2f})")

    return {"high_paid_count": len(high_paid),
            "top_payer": top,
            "top_payer_total": round(by_payer[top], 2)}


def lab_analysis(df: pd.DataFrame):
    print("\n=== LDL Cholesterol Analysis ===\n")

    ldl = df[df["TestName"] == "LDL Cholesterol"]

    max_val = ldl["TestResultValue"].max()
    avg_val = ldl["TestResultValue"].mean()
    high_risk = ldl[ldl["TestResultValue"] > 160]["PatientID"].nunique()

    print(f"Highest result:     {max_val} mg/dL")
    print(f"Average result:     {avg_val:.2f} mg/dL")
    print(f"Patients > 160:     {high_risk}")
    print("\nHigh-risk patients (LDL > 160 mg/dL):")
    print(
        ldl[ldl["TestResultValue"] > 160]
        [["PatientID", "TestResultValue", "CollectionDate"]]
        .sort_values("TestResultValue", ascending=False)
        .to_string(index=False)
    )

    return {"ldl_max": max_val, "ldl_avg": round(avg_val, 2),
            "ldl_high_risk_patients": high_risk}


if __name__ == "__main__":
    pc = pd.read_csv(RAW / "Pharmacy_Claims.txt")
    lr = pd.read_csv(RAW / "Lab_Results.txt")

    p = pharmacy_analysis(pc)
    l = lab_analysis(lr)

    print("\n=== Summary ===")
    all_results = {**p, **l}
    for k, v in all_results.items():
        print(f"  {k}: {v}")
