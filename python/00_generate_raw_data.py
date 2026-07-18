"""
00_generate_raw_data.py
------------------------
Generates a synthetic, intentionally messy raw HR dataset (hr_data_raw.csv).

Why generate data instead of using a "real" dataset?
This makes the project fully reproducible for a GitHub portfolio - anyone
cloning the repo can regenerate the exact same messy raw file and run the
cleaning pipeline on it from scratch. The messiness (nulls, duplicates,
inconsistent casing, mixed date formats, stray whitespace) is injected on
purpose so the Data Cleaning script (01_data_cleaning.py) has real work to do
and the README can document real before/after cleaning decisions.

Run:
    python 00_generate_raw_data.py
Output:
    ../data/raw/hr_data_raw.csv
"""

import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

N = 1500  # number of employee records

departments = ["Sales", "Human Resources", "Engineering", "Finance",
               "Marketing", "Customer Support", "IT", "Operations"]

job_roles_by_dept = {
    "Sales": ["Sales Executive", "Sales Manager", "Account Manager"],
    "Human Resources": ["HR Executive", "HR Manager", "Recruiter"],
    "Engineering": ["Software Engineer", "Senior Engineer", "Engineering Manager", "QA Engineer"],
    "Finance": ["Financial Analyst", "Accountant", "Finance Manager"],
    "Marketing": ["Marketing Executive", "Marketing Manager", "Content Strategist"],
    "Customer Support": ["Support Executive", "Support Team Lead"],
    "IT": ["IT Support", "System Administrator", "IT Manager"],
    "Operations": ["Operations Executive", "Operations Manager"],
}

education_levels = ["High School", "Bachelor's", "Master's", "PhD"]
marital_status_opts = ["Single", "Married", "Divorced"]
genders = ["Male", "Female"]

rows = []
for emp_id in range(1001, 1001 + N):
    dept = random.choice(departments)
    role = random.choice(job_roles_by_dept[dept])
    gender = random.choices(genders, weights=[0.56, 0.44])[0]
    age = int(np.clip(np.random.normal(35, 9), 20, 60))
    years_at_company = int(np.clip(np.random.exponential(5), 0, age - 18))
    education = random.choices(education_levels, weights=[0.1, 0.45, 0.35, 0.1])[0]

    # base salary influenced by department, role seniority, education, experience
    base = {"Sales": 55000, "Human Resources": 50000, "Engineering": 85000,
            "Finance": 65000, "Marketing": 58000, "Customer Support": 42000,
            "IT": 68000, "Operations": 52000}[dept]
    seniority_bonus = 1.4 if any(k in role for k in ["Manager", "Senior", "Lead"]) else 1.0
    edu_bonus = {"High School": 0.9, "Bachelor's": 1.0, "Master's": 1.15, "PhD": 1.3}[education]
    salary = round(base * seniority_bonus * edu_bonus * (1 + years_at_company * 0.015)
                    * np.random.uniform(0.9, 1.1), -2)

    performance_rating = random.choices([1, 2, 3, 4, 5], weights=[0.03, 0.12, 0.4, 0.32, 0.13])[0]
    training_hours = int(np.clip(np.random.normal(40, 15), 0, 100))
    marital_status = random.choice(marital_status_opts)
    distance_from_home = int(np.clip(np.random.exponential(8), 1, 45))
    overtime = random.choices(["Yes", "No"], weights=[0.28, 0.72])[0]
    project_tasks = int(np.clip(np.random.normal(12, 4), 1, 30))

    # attrition more likely with low performance, high distance, overtime, low salary
    attr_score = (0.15 if overtime == "Yes" else 0) + (0.15 if distance_from_home > 20 else 0) \
        + (0.2 if performance_rating <= 2 else 0) + (0.1 if years_at_company < 2 else 0) \
        + (0.1 if salary < base * 0.8 else 0)
    attrition = "Yes" if random.random() < min(attr_score + 0.05, 0.85) else "No"

    # promotion more likely with high performance & tenure
    promo_score = (0.25 if performance_rating >= 4 else 0.05) + (0.1 if years_at_company >= 3 else 0)
    promotion = "Yes" if random.random() < promo_score else "No"

    hire_date = datetime(2024, 1, 1) - timedelta(days=years_at_company * 365 + random.randint(0, 300))

    rows.append({
        "EmployeeID": emp_id,
        "Department": dept,
        "JobRole": role,
        "Gender": gender,
        "Age": age,
        "MaritalStatus": marital_status,
        "Education": education,
        "Salary": salary,
        "YearsAtCompany": years_at_company,
        "PerformanceRating": performance_rating,
        "TrainingHours": training_hours,
        "DistanceFromHome": distance_from_home,
        "OverTime": overtime,
        "ProjectTasks": project_tasks,
        "Promotion": promotion,
        "Attrition": attrition,
        "HireDate": hire_date.strftime("%Y-%m-%d"),
    })

df = pd.DataFrame(rows)

# ---------------------------------------------------------------------------
# Inject realistic messiness so the cleaning script has genuine work to do
# ---------------------------------------------------------------------------

# 1) Inconsistent casing / whitespace in categorical text fields
messy_idx = df.sample(frac=0.08, random_state=1).index
df.loc[messy_idx, "Department"] = df.loc[messy_idx, "Department"].str.upper()
messy_idx2 = df.sample(frac=0.06, random_state=2).index
df.loc[messy_idx2, "Gender"] = df.loc[messy_idx2, "Gender"].str.lower()
messy_idx3 = df.sample(frac=0.05, random_state=3).index
df.loc[messy_idx3, "JobRole"] = " " + df.loc[messy_idx3, "JobRole"] + "  "

# 2) Random missing values across several columns
for col, frac in [("Salary", 0.02), ("PerformanceRating", 0.015), ("Education", 0.02),
                   ("TrainingHours", 0.015), ("MaritalStatus", 0.01), ("Age", 0.01)]:
    null_idx = df.sample(frac=frac, random_state=hash(col) % 1000).index
    df.loc[null_idx, col] = np.nan

# 3) Duplicate rows (simulate accidental double export)
dupes = df.sample(n=20, random_state=4)
df = pd.concat([df, dupes], ignore_index=True)

# 4) A few impossible / outlier values to be caught by validation
outlier_idx = df.sample(n=5, random_state=5).index
df.loc[outlier_idx, "Age"] = [150, -5, 200, 0, 999]
outlier_idx2 = df.sample(n=5, random_state=6).index
df.loc[outlier_idx2, "Salary"] = [-1000, 0, 5, 9999999, -50]

# 5) Inconsistent Yes/No formatting
messy_idx4 = df.sample(frac=0.04, random_state=7).index
df.loc[messy_idx4, "Attrition"] = df.loc[messy_idx4, "Attrition"].map({"Yes": "Y", "No": "N"})

# 6) Mixed date formats in HireDate
messy_idx5 = df.sample(frac=0.05, random_state=8).index
def to_alt_format(d):
    try:
        dt = datetime.strptime(d, "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return d
df.loc[messy_idx5, "HireDate"] = df.loc[messy_idx5, "HireDate"].apply(to_alt_format)

# shuffle rows so duplicates aren't neatly at the bottom
df = df.sample(frac=1, random_state=9).reset_index(drop=True)

df.to_csv("../data/raw/hr_data_raw.csv", index=False)
print(f"Raw dataset generated: {df.shape[0]} rows, {df.shape[1]} columns")
print("Saved to ../data/raw/hr_data_raw.csv")
