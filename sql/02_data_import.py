"""
02_data_import.py
------------------
Loads the cleaned HR dataset (hr_data_cleaned.csv) into the normalized
MySQL schema created by 01_schema.sql.

Populates, in order (to satisfy foreign key dependencies):
    1. departments
    2. job_roles
    3. education_levels
    4. employees
    5. performance      (one current-period row per employee)
    6. training_records (one aggregated training row per employee)
    7. attrition_log    (one row per employee where Attrition = 'Yes')

Requirements:
    pip install mysql-connector-python pandas

Configure your MySQL credentials via environment variables before running:
    export MYSQL_HOST=localhost
    export MYSQL_USER=root
    export MYSQL_PASSWORD=yourpassword

Run:
    python 02_data_import.py
"""

import os
import pandas as pd
import mysql.connector
from mysql.connector import Error

CSV_PATH = "../data/processed/hr_data_cleaned.csv"

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "user": os.getenv("MYSQL_USER", "hr_user"),
    "password": os.getenv("MYSQL_PASSWORD", "hr_password123"),
    "database": "hr_analytics",
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def main():
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} cleaned employee records from CSV.")

    try:
        conn = get_connection()
    except Error as e:
        print(f"Could not connect to MySQL: {e}")
        print("Make sure MySQL is running and 01_schema.sql has been executed first.")
        return

    cursor = conn.cursor()

    # -------------------------------------------------------------------
    # 1. departments
    # -------------------------------------------------------------------
    dept_map = {}
    for dept in sorted(df["Department"].unique()):
        cursor.execute(
            "INSERT INTO departments (department_name) VALUES (%s)", (dept,)
        )
        dept_map[dept] = cursor.lastrowid
    conn.commit()
    print(f"Inserted {len(dept_map)} departments.")

    # -------------------------------------------------------------------
    # 2. job_roles
    # -------------------------------------------------------------------
    role_map = {}
    role_dept_pairs = df[["JobRole", "Department"]].drop_duplicates()
    for _, row in role_dept_pairs.iterrows():
        cursor.execute(
            "INSERT INTO job_roles (job_role_name, department_id) VALUES (%s, %s)",
            (row["JobRole"], dept_map[row["Department"]]),
        )
        role_map[(row["JobRole"], row["Department"])] = cursor.lastrowid
    conn.commit()
    print(f"Inserted {len(role_map)} job roles.")

    # -------------------------------------------------------------------
    # 3. education_levels
    # -------------------------------------------------------------------
    edu_map = {}
    for edu in sorted(df["Education"].unique()):
        cursor.execute(
            "INSERT INTO education_levels (education_name) VALUES (%s)", (edu,)
        )
        edu_map[edu] = cursor.lastrowid
    conn.commit()
    print(f"Inserted {len(edu_map)} education levels.")

    # -------------------------------------------------------------------
    # 4. employees
    # -------------------------------------------------------------------
    emp_insert = """
        INSERT INTO employees
        (employee_id, department_id, job_role_id, education_id, gender, age,
         marital_status, salary, years_at_company, distance_from_home,
         overtime, project_tasks, promotion, attrition, hire_date)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    emp_rows = []
    for _, r in df.iterrows():
        emp_rows.append((
            int(r["EmployeeID"]),
            dept_map[r["Department"]],
            role_map[(r["JobRole"], r["Department"])],
            edu_map[r["Education"]],
            r["Gender"],
            int(r["Age"]),
            r["MaritalStatus"],
            float(r["Salary"]),
            int(r["YearsAtCompany"]),
            int(r["DistanceFromHome"]),
            r["OverTime"],
            int(r["ProjectTasks"]),
            r["Promotion"],
            r["Attrition"],
            r["HireDate"],
        ))
    cursor.executemany(emp_insert, emp_rows)
    conn.commit()
    print(f"Inserted {len(emp_rows)} employees.")

    # -------------------------------------------------------------------
    # 5. performance (current period snapshot)
    # -------------------------------------------------------------------
    perf_insert = """
        INSERT INTO performance (employee_id, review_period, performance_rating, review_date)
        VALUES (%s, '2024-Q4', %s, '2024-12-31')
    """
    perf_rows = [(int(r["EmployeeID"]), int(r["PerformanceRating"])) for _, r in df.iterrows()]
    cursor.executemany(perf_insert, perf_rows)
    conn.commit()
    print(f"Inserted {len(perf_rows)} performance records.")

    # -------------------------------------------------------------------
    # 6. training_records (aggregated total as a single record)
    # -------------------------------------------------------------------
    train_insert = """
        INSERT INTO training_records (employee_id, training_name, training_hours, training_date)
        VALUES (%s, 'Annual Training Program 2024', %s, '2024-06-30')
    """
    train_rows = [(int(r["EmployeeID"]), float(r["TrainingHours"])) for _, r in df.iterrows()]
    cursor.executemany(train_insert, train_rows)
    conn.commit()
    print(f"Inserted {len(train_rows)} training records.")

    # -------------------------------------------------------------------
    # 7. attrition_log (only employees who left)
    # -------------------------------------------------------------------
    left_df = df[df["Attrition"] == "Yes"]
    attr_insert = """
        INSERT INTO attrition_log (employee_id, exit_date, exit_reason)
        VALUES (%s, '2024-12-31', 'Not specified')
    """
    attr_rows = [(int(r["EmployeeID"]),) for _, r in left_df.iterrows()]
    cursor.executemany(attr_insert, attr_rows)
    conn.commit()
    print(f"Inserted {len(attr_rows)} attrition log records.")

    cursor.close()
    conn.close()
    print("\nData import complete. Database 'hr_analytics' is ready for querying.")


if __name__ == "__main__":
    main()
