# Methodology

## Why This Project

Healthcare organizations routinely store patient data across multiple disconnected systems. Combining EHR demographics, pharmacy claims, and lab results into a single clean dataset is one of the most common and impactful challenges in health data analytics. This project walks through the full pipeline — from raw text files to SQL-ready, cleaned data.

---

## Data Sources

### Patients EHR (`Patients_EHR_raw_data.csv`)
Demographics and primary diagnoses for 74 patients. This was the messiest dataset, with missing values, duplicate rows, inconsistent gender encoding, and date formats that had been corrupted by spreadsheet software.

### Pharmacy Claims (`Pharmacy_Claims.txt`)
100 medication dispensing records including drug name, dosage, fill date, payer type, and amounts charged vs reimbursed. Some dosage fields were recorded as `?` — a known limitation of the source system.

### Lab Results (`Lab_Results.txt`)
201 diagnostic test results covering three test types: HbA1c (diabetes monitoring), Creatinine (kidney function), and LDL Cholesterol (cardiovascular risk). Each record includes reference ranges and an abnormal flag.

---

## Step 1 — Importing the Data

The pharmacy and lab files arrived as plain text (comma-separated). I loaded these with pandas and exported to `.xlsx` so they could be shared and reviewed in Excel by non-technical stakeholders.

```python
import pandas as pd

pc = pd.read_csv("Pharmacy_Claims.txt")
pc.to_excel("Pharmacy_Claims.xlsx", index=False)

lr = pd.read_csv("Lab_Results.txt")
lr.to_excel("Lab_Results.xlsx", index=False)
```

---

## Step 2 — Claims and Lab Analysis

### Pharmacy Claims
I used filtering and groupby aggregation (equivalent to Excel's FILTER, SORT, and SUMIF) to answer operational questions about billing and payer performance.

```python
# Claims with PaidAmount > $250
(pc["PaidAmount"] > 250).sum()  # → 21

# Payer with highest total reimbursement
pc.groupby("Payer")["PaidAmount"].sum().sort_values(ascending=False)
# → Private: $7,313.09
```

### Lab Results — LDL Cholesterol Focus
Filtered to LDL Cholesterol tests only, then computed summary statistics and flagged high-risk patients.

```python
ldl = lr[lr["TestName"] == "LDL Cholesterol"]

ldl["TestResultValue"].max()   # → 187.1
ldl["TestResultValue"].mean()  # → 134.64

# Patients with LDL > 160 mg/dL (high cardiovascular risk)
ldl[ldl["TestResultValue"] > 160]["PatientID"].nunique()  # → 12
```

---

## Step 3 — EHR Data Quality Audit

Before using the EHR data for any joins or analysis, I ran a systematic quality check across all columns.

### Issues Found

**Missing Values**
```python
df.isnull().sum()
# DateOfBirth    3
# ZipCode        4
```

**Duplicate Rows**
```python
df.duplicated().sum()  # → 2 exact duplicates
```

**Inconsistent Gender Encoding**
```python
df["Gender"].value_counts()
# Female    34
# Male      34
# F          4
# M          1
# male       1
```

**Date Format Issues**
Two `AdmissionDate` values were stored as Excel serial integers (`45258`, `45439`) — a known artifact of copying data through Excel without proper date formatting. These map to real dates via:

```
date = datetime(1899, 12, 30) + timedelta(days=serial_number)
```

### Fixes Applied

```python
# Missing values
df["DateOfBirth"] = df["DateOfBirth"].fillna("Unknown")
df["ZipCode"]     = df["ZipCode"].fillna("Unknown")

# Duplicates
df.drop_duplicates(keep="first", inplace=True)

# Gender standardization
df["Gender"] = df["Gender"].replace({
    "M": "Male", "m": "Male", "male": "Male",
    "F": "Female", "f": "Female"
})

# Date standardization
df["AdmissionDate"] = pd.to_datetime(
    df["AdmissionDate"], infer_datetime_format=True, errors="coerce"
).dt.strftime("%Y-%m-%d")
```

**Result:** 74 rows → 72 rows (2 duplicates removed), 0 remaining issues.

---

## Step 4 — SQL Analysis

All three cleaned datasets were loaded into a SQLite database. I then wrote JOIN queries to connect patient demographics with clinical and pharmacy data.

### Database Schema

```
patients (PatientID, DateOfBirth, Gender, ZipCode, PrimaryCondition, AdmissionDate)
pharmacy_claims (ClaimID, PatientID, Medication, Dosage, FillDate, Payer, ...)
lab_results (PatientID, LabTestID, CollectionDate, TestName, TestResultValue, ...)
```

### Queries

**Patients born before 1980**
```sql
SELECT PatientID, Gender, DateOfBirth
FROM   patients
WHERE  DateOfBirth < '1980-01-01'
ORDER  BY DateOfBirth;
-- 52 rows
```

**Female patients with Type 2 Diabetes**
```sql
SELECT PatientID, Gender, DateOfBirth, PrimaryCondition
FROM   patients
WHERE  Gender = 'Female'
  AND  PrimaryCondition LIKE '%Type 2 Diabetes%';
-- 10 rows
```

**Lab results joined with patient demographics**
```sql
SELECT p.PatientID, p.Gender, p.DateOfBirth,
       l.TestName, l.TestResultValue, l.AbnormalFlag
FROM   patients p
JOIN   lab_results l ON p.PatientID = l.PatientID
ORDER  BY p.PatientID, l.TestName;
-- 180 rows
```

**Patients with their insurance payer**
```sql
SELECT DISTINCT p.PatientID, p.Gender, p.DateOfBirth, pc.Payer
FROM   patients p
JOIN   pharmacy_claims pc ON p.PatientID = pc.PatientID
ORDER  BY p.PatientID;
-- 54 rows
```

---

## Findings Summary

| Metric | Value |
|---|---|
| Claims exceeding $250 reimbursement | 21 |
| Top payer by total reimbursement | Private ($7,313.09) |
| Highest recorded LDL Cholesterol | 187.1 mg/dL |
| Average LDL Cholesterol | 134.64 mg/dL |
| High-risk patients (LDL > 160) | 12 |
| EHR quality issues resolved | 15 |
| Patients pre-1980 | 52 |
| Female patients with Type 2 Diabetes | 10 |
