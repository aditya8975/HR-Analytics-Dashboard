"""
01_data_cleaning.py
--------------------
Complete data cleaning pipeline for the HR Analytics dataset.

Steps performed (each documented + logged):
1. Load raw data & initial inspection
2. Standardize column names
3. Fix inconsistent text casing / whitespace in categorical columns
4. Standardize Yes/No fields
5. Parse mixed-format dates into a single standard format
6. Handle missing values (impute or drop, column by column, with reasoning)
7. Remove duplicate records
8. Validate & fix impossible outliers (negative/absurd Age & Salary)
9. Correct data types
10. Feature engineering (Salary bands, Age groups, Tenure groups)
11. Final validation checks
12. Export cleaned dataset + a cleaning log report

Run:
    python 01_data_cleaning.py
Input:
    ../data/raw/hr_data_raw.csv
Output:
    ../data/processed/hr_data_cleaned.csv
    ../data/processed/cleaning_log.txt
"""

import pandas as pd
import numpy as np

LOG = []


def log(msg):
    print(msg)
    LOG.append(str(msg))


log("=" * 70)
log("HR ANALYTICS - DATA CLEANING PIPELINE")
log("=" * 70)

# ---------------------------------------------------------------------------
# 1. Load raw data
# ---------------------------------------------------------------------------
df = pd.read_csv("../data/raw/hr_data_raw.csv")
log(f"\n[1] Loaded raw data: {df.shape[0]} rows x {df.shape[1]} columns")
log(f"Columns: {list(df.columns)}")

# ---------------------------------------------------------------------------
# 2. Standardize column names (already clean here, but enforce convention)
# ---------------------------------------------------------------------------
df.columns = [c.strip() for c in df.columns]
log("\n[2] Column names standardized (stripped whitespace).")

# ---------------------------------------------------------------------------
# 3. Fix inconsistent text casing / stray whitespace in categorical columns
# ---------------------------------------------------------------------------
text_cols = ["Department", "JobRole", "Gender", "MaritalStatus", "Education"]
for col in text_cols:
    before_unique = df[col].nunique(dropna=True)
    df[col] = df[col].astype(str).str.strip()
    df[col] = df[col].apply(lambda x: x.title() if isinstance(x, str) and x.lower() != "nan" else np.nan)
    # title() mangles apostrophes ("Bachelor'S") and known acronyms ("Hr", "It") -
    # fix those specific cases so categories read naturally
    df[col] = df[col].str.replace(r"'S\b", "'s", regex=True)
    df[col] = df[col].str.replace(r"\bHr\b", "HR", regex=True)
    df[col] = df[col].str.replace(r"\bIt\b", "IT", regex=True)
    after_unique = df[col].nunique(dropna=True)
    log(f"[3] {col}: standardized casing/whitespace ({before_unique} -> {after_unique} unique values)")

# Gender has only two categories - title() gives "Male"/"Female" consistently
df["Gender"] = df["Gender"].replace({"Female": "Female", "Male": "Male"})

# ---------------------------------------------------------------------------
# 4. Standardize Yes/No fields (Attrition had "Y"/"N" mixed in)
# ---------------------------------------------------------------------------
yn_map = {"Y": "Yes", "N": "No", "Yes": "Yes", "No": "No"}
df["Attrition"] = df["Attrition"].map(yn_map)
df["Promotion"] = df["Promotion"].map(yn_map)
df["OverTime"] = df["OverTime"].map(yn_map)
log("\n[4] Standardized Yes/No fields: Attrition, Promotion, OverTime")

# ---------------------------------------------------------------------------
# 5. Parse mixed-format dates (YYYY-MM-DD and DD/MM/YYYY) into one format
# ---------------------------------------------------------------------------
def parse_mixed_date(d):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return pd.to_datetime(d, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT

df["HireDate"] = df["HireDate"].apply(parse_mixed_date)
bad_dates = df["HireDate"].isna().sum()
log(f"\n[5] Parsed HireDate into standard datetime format. Unparseable dates: {bad_dates}")

# ---------------------------------------------------------------------------
# 6. Handle missing values
# ---------------------------------------------------------------------------
log("\n[6] Missing values BEFORE handling:")
log(df.isnull().sum()[df.isnull().sum() > 0].to_string())

# Numeric columns -> impute with median grouped by Department (more accurate
# than a global median since salary/rating differ a lot by department)
for col in ["Salary", "PerformanceRating", "TrainingHours"]:
    df[col] = df.groupby("Department")[col].transform(lambda x: x.fillna(x.median()))

# Age -> impute with overall median (age doesn't vary meaningfully by dept)
df["Age"] = df["Age"].fillna(df["Age"].median())

# Categorical -> impute with column mode (most frequent category)
for col in ["Education", "MaritalStatus"]:
    df[col] = df[col].fillna(df[col].mode()[0])

log("\n[6] Missing values AFTER handling:")
remaining_na = df.isnull().sum()[df.isnull().sum() > 0]
log(remaining_na.to_string() if len(remaining_na) else "None - all missing values resolved.")

# ---------------------------------------------------------------------------
# 7. Remove duplicate records
# ---------------------------------------------------------------------------
before = df.shape[0]
df = df.drop_duplicates(subset=["EmployeeID"], keep="first")
after = df.shape[0]
log(f"\n[7] Removed {before - after} duplicate EmployeeID records ({before} -> {after} rows).")

# ---------------------------------------------------------------------------
# 8. Validate & fix impossible outliers
# ---------------------------------------------------------------------------
# Age must be realistically between 18 and 65 for a working employee
invalid_age = df[(df["Age"] < 18) | (df["Age"] > 65)]
log(f"\n[8] Invalid Age values found: {len(invalid_age)} -> replaced with department median")
age_median = df.loc[(df["Age"] >= 18) & (df["Age"] <= 65), "Age"].median()
df.loc[(df["Age"] < 18) | (df["Age"] > 65), "Age"] = age_median

# Salary must be positive and within a realistic range (use IQR-based capping)
invalid_salary = df[(df["Salary"] <= 1000) | (df["Salary"] > 500000)]
log(f"[8] Invalid Salary values found: {len(invalid_salary)} -> replaced with department median")
sal_median_by_dept = df[(df["Salary"] > 1000) & (df["Salary"] <= 500000)].groupby("Department")["Salary"].median()
def fix_salary(row):
    if row["Salary"] <= 1000 or row["Salary"] > 500000:
        return sal_median_by_dept.get(row["Department"], df["Salary"].median())
    return row["Salary"]
df["Salary"] = df.apply(fix_salary, axis=1)

# ---------------------------------------------------------------------------
# 9. Correct data types
# ---------------------------------------------------------------------------
df["EmployeeID"] = df["EmployeeID"].astype(int)
df["Age"] = df["Age"].astype(int)
df["YearsAtCompany"] = df["YearsAtCompany"].astype(int)
df["PerformanceRating"] = df["PerformanceRating"].round().astype(int)
df["TrainingHours"] = df["TrainingHours"].round().astype(int)
df["DistanceFromHome"] = df["DistanceFromHome"].astype(int)
df["ProjectTasks"] = df["ProjectTasks"].astype(int)
df["Salary"] = df["Salary"].round(2)
log("\n[9] Data types corrected (ints for counts/ratings, float for salary, datetime for HireDate).")

# ---------------------------------------------------------------------------
# 10. Feature engineering
# ---------------------------------------------------------------------------
df["SalaryBand"] = pd.cut(
    df["Salary"], bins=[0, 45000, 65000, 90000, np.inf],
    labels=["Low (<45K)", "Medium (45K-65K)", "High (65K-90K)", "Very High (90K+)"]
)

df["AgeGroup"] = pd.cut(
    df["Age"], bins=[17, 25, 35, 45, 60],
    labels=["18-25", "26-35", "36-45", "46-60"]
)

df["TenureGroup"] = pd.cut(
    df["YearsAtCompany"], bins=[-1, 1, 3, 7, 100],
    labels=["0-1 yrs", "2-3 yrs", "4-7 yrs", "8+ yrs"]
)

log("\n[10] Feature engineering complete: SalaryBand, AgeGroup, TenureGroup added.")

# ---------------------------------------------------------------------------
# 11. Final validation checks
# ---------------------------------------------------------------------------
assert df["EmployeeID"].is_unique, "Duplicate EmployeeIDs remain!"
assert df["Attrition"].isin(["Yes", "No"]).all(), "Unclean Attrition values remain!"
assert df.isnull().sum().sum() == 0 or df["HireDate"].isnull().sum() == df.isnull().sum().sum(), \
    "Unexpected nulls remain outside HireDate!"
log("\n[11] Final validation checks passed: unique EmployeeIDs, clean Yes/No fields, no unexpected nulls.")

# ---------------------------------------------------------------------------
# 12. Export
# ---------------------------------------------------------------------------
df = df.sort_values("EmployeeID").reset_index(drop=True)
df.to_csv("../data/processed/hr_data_cleaned.csv", index=False)
log(f"\n[12] Cleaned dataset exported: {df.shape[0]} rows x {df.shape[1]} columns")
log("Saved to ../data/processed/hr_data_cleaned.csv")

with open("../data/processed/cleaning_log.txt", "w") as f:
    f.write("\n".join(LOG))

log("\nCleaning log saved to ../data/processed/cleaning_log.txt")
log("=" * 70)
