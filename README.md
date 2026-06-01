# 🏥 Healthcare Data Integration and Analysis

A personal data analytics project where I unified, cleaned, and analyzed patient records from three siloed healthcare systems to surface population health insights.

---

## 🧠 Problem Statement

Healthcare organizations often store patient data across disconnected systems — EHRs, pharmacy platforms, and clinical labs — making it impossible to get a complete picture of patient health without manual effort. In this project, I built a pipeline to **combine these sources**, **fix data quality issues**, and **answer key clinical and operational questions** using Python and SQL.

The analysis focuses on patients with chronic conditions:

| Condition | Clinical Focus |
|---|---|
| Type 2 Diabetes | Blood glucose monitoring via HbA1c |
| Hypertension | Blood pressure management |
| Osteoarthritis | Joint condition tracking |
| Hyperlipidemia | High LDL cholesterol |

---

## 🗂️ Repository Structure

```
healthcare-data-project/
│
├── data/
│   ├── raw/                          # Original source files (unmodified)
│   │   ├── Patients_EHR_raw_data.csv
│   │   ├── Pharmacy_Claims.txt
│   │   └── Lab_Results.txt
│   └── processed/                    # Cleaned and exported outputs
│       ├── Pharmacy_Claims.xlsx
│       ├── Lab_Results.xlsx
│       └── Patients_EHR_cleaned.csv
│
├── notebooks/
│   └── Healthcare_Data_Integration_and_Analysis.ipynb
│
├── scripts/
│   ├── import_data.py                # Convert txt → xlsx
│   ├── analyze_claims_and_labs.py    # Claims & lab analysis
│   ├── clean_ehr.py                  # EHR data quality pipeline
│   └── sql_analysis.py              # SQL cross-system queries
│
├── outputs/
│   └── analysis_summary.txt
│
├── docs/
│   └── methodology.md
│
├── requirements.txt
└── README.md
```

---

## 📦 Data Sources

Three datasets were used, each representing a separate healthcare source system:

| File | System | Records | Key Fields |
|---|---|---|---|
| `Patients_EHR_raw_data.csv` | EHR | 74 patients | PatientID, DateOfBirth, Gender, ZipCode, PrimaryCondition, AdmissionDate |
| `Pharmacy_Claims.txt` | Pharmacy | 100 claims | Medication, Dosage, FillDate, Payer, ChargeAmount, PaidAmount |
| `Lab_Results.txt` | Clinical Lab | 201 results | TestName, TestResultValue, Units, ReferenceRange, AbnormalFlag |

> All patient data is synthetically generated — no real PHI is used.

---

## ⚙️ What I Built

### 1. Data Import Pipeline
Converted raw `.txt` source files from the pharmacy and lab systems into structured `.xlsx` format, making them ready for spreadsheet analysis and sharing with non-technical stakeholders.

### 2. Claims & Lab Analysis
Analyzed pharmacy billing and lab diagnostic data to answer operational questions:

| Question | Answer |
|---|---|
| How many claims had a paid amount over $250? | **21 claims** |
| Which insurance payer reimbursed the most in total? | **Private — $7,313.09** |
| What is the highest recorded LDL Cholesterol? | **187.1 mg/dL** |
| What is the average LDL Cholesterol across patients? | **134.64 mg/dL** |
| How many patients have dangerously high LDL (> 160)? | **12 patients** |

### 3. EHR Data Quality Audit & Cleaning
Before any analysis, I audited the EHR dataset and found multiple quality issues across only 74 records — roughly a 10% problem rate. Every issue was identified and fixed:

| Issue | Column | Count | Fix Applied |
|---|---|---|---|
| Missing values | DateOfBirth | 3 | Filled with `'Unknown'` |
| Missing values | ZipCode | 4 | Filled with `'Unknown'` |
| Exact duplicate rows | All | 2 | Removed, kept first occurrence |
| Inconsistent entries | Gender (`M`, `male`, `F`) | 6 | Standardized → `Male` / `Female` |
| Wrong date format | AdmissionDate (Excel serial #) | 2 | Converted to `YYYY-MM-DD` |

**Before cleaning:** 74 rows, 15 data issues  
**After cleaning:** 72 rows, 0 issues → saved as `Patients_EHR_cleaned.csv`

### 4. SQL Cross-System Analysis
Loaded all three datasets into a SQLite database and wrote JOIN queries to connect patient demographics with clinical and pharmacy data:

- Patients born before 1980 → *52 patients*
- Female patients diagnosed with Type 2 Diabetes → *10 patients*
- Full lab history per patient with demographics → *180 matched records*
- Each patient mapped to their insurance payer → *54 patient-payer combinations*

---

## 💡 Key Insights

- **Private insurance** pays the most in total reimbursements — worth tracking for contract and forecasting decisions.
- **12 patients** have LDL levels above 160 mg/dL, which is clinically significant and should trigger outreach.
- Data quality problems affected nearly **1 in 10 EHR records**, pointing to a need for input validation at point of entry.
- **Excel serial number dates** are a silent and common corruption pattern when data is exported from legacy systems without explicit formatting — easy to miss without a systematic audit.

---

## 🚀 Getting Started

```bash
# Clone the repo
git clone https://github.com/yourusername/healthcare-data-project.git
cd healthcare-data-project

# Install dependencies
pip install -r requirements.txt

# Run the full pipeline
python scripts/import_data.py
python scripts/analyze_claims_and_labs.py
python scripts/clean_ehr.py
python scripts/sql_analysis.py

# Or open the end-to-end notebook
jupyter notebook notebooks/Healthcare_Data_Integration_and_Analysis.ipynb
```

---

## 🛠️ Tech Stack

| Tool | Use |
|---|---|
| Python 3 | Pipeline, cleaning, analysis |
| pandas | Data wrangling and transformation |
| openpyxl | Excel file generation |
| SQLite | Relational database for cross-system queries |
| Jupyter Notebook | Interactive analysis and documentation |

---

## 📁 Where to Start

| Goal | Go to |
|---|---|
| Understand the full methodology | [`docs/methodology.md`](docs/methodology.md) |
| Run the full analysis interactively | [`notebooks/`](notebooks/) |
| Use individual scripts | [`scripts/`](scripts/) |
| See the raw vs cleaned data | [`data/raw/`](data/raw/) vs [`data/processed/`](data/processed/) |
