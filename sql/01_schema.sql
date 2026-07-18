-- =============================================================================
-- HR ANALYTICS - MYSQL DATABASE SCHEMA
-- =============================================================================
-- Normalized to 3NF:
--   departments      -> lookup table for department names
--   job_roles        -> lookup table for job roles, linked to a department
--   education_levels -> lookup table for education levels
--   employees        -> core fact/dimension table, one row per employee,
--                        referencing departments, job_roles, education_levels
--   performance      -> one row per employee per review period (supports
--                        historical performance tracking, not just latest rating)
--   training_records -> one row per training event per employee (supports
--                        multiple training sessions, not just a total)
--   attrition_log    -> one row per employee who has left, with exit details
-- =============================================================================

DROP DATABASE IF EXISTS hr_analytics;
CREATE DATABASE hr_analytics;
USE hr_analytics;

-- -----------------------------------------------------------------------------
-- Lookup: departments
-- -----------------------------------------------------------------------------
CREATE TABLE departments (
    department_id   INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(50) NOT NULL UNIQUE
);

-- -----------------------------------------------------------------------------
-- Lookup: job_roles (each role belongs to one department)
-- -----------------------------------------------------------------------------
CREATE TABLE job_roles (
    job_role_id     INT AUTO_INCREMENT PRIMARY KEY,
    job_role_name   VARCHAR(50) NOT NULL,
    department_id   INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    UNIQUE KEY uq_role_dept (job_role_name, department_id)
);

-- -----------------------------------------------------------------------------
-- Lookup: education_levels
-- -----------------------------------------------------------------------------
CREATE TABLE education_levels (
    education_id    INT AUTO_INCREMENT PRIMARY KEY,
    education_name  VARCHAR(30) NOT NULL UNIQUE
);

-- -----------------------------------------------------------------------------
-- Core table: employees
-- -----------------------------------------------------------------------------
CREATE TABLE employees (
    employee_id        INT PRIMARY KEY,
    department_id       INT NOT NULL,
    job_role_id          INT NOT NULL,
    education_id         INT NOT NULL,
    gender               ENUM('Male', 'Female') NOT NULL,
    age                  TINYINT UNSIGNED NOT NULL CHECK (age BETWEEN 18 AND 65),
    marital_status       ENUM('Single', 'Married', 'Divorced') NOT NULL,
    salary               DECIMAL(10,2) NOT NULL CHECK (salary > 0),
    years_at_company     TINYINT UNSIGNED NOT NULL,
    distance_from_home   TINYINT UNSIGNED NOT NULL,
    overtime             ENUM('Yes', 'No') NOT NULL DEFAULT 'No',
    project_tasks        TINYINT UNSIGNED NOT NULL DEFAULT 0,
    promotion            ENUM('Yes', 'No') NOT NULL DEFAULT 'No',
    attrition            ENUM('Yes', 'No') NOT NULL DEFAULT 'No',
    hire_date            DATE NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (job_role_id) REFERENCES job_roles(job_role_id),
    FOREIGN KEY (education_id) REFERENCES education_levels(education_id)
);

CREATE INDEX idx_emp_department ON employees(department_id);
CREATE INDEX idx_emp_attrition  ON employees(attrition);
CREATE INDEX idx_emp_hire_date  ON employees(hire_date);

-- -----------------------------------------------------------------------------
-- performance: supports multiple review periods per employee
-- -----------------------------------------------------------------------------
CREATE TABLE performance (
    performance_id      INT AUTO_INCREMENT PRIMARY KEY,
    employee_id          INT NOT NULL,
    review_period         VARCHAR(10) NOT NULL,     -- e.g. '2024-Q4'
    performance_rating    TINYINT UNSIGNED NOT NULL CHECK (performance_rating BETWEEN 1 AND 5),
    review_date            DATE NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

CREATE INDEX idx_perf_employee ON performance(employee_id);

-- -----------------------------------------------------------------------------
-- training_records: supports multiple training sessions per employee
-- -----------------------------------------------------------------------------
CREATE TABLE training_records (
    training_id       INT AUTO_INCREMENT PRIMARY KEY,
    employee_id         INT NOT NULL,
    training_name         VARCHAR(100) NOT NULL,
    training_hours         DECIMAL(5,2) NOT NULL CHECK (training_hours >= 0),
    training_date           DATE NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

CREATE INDEX idx_train_employee ON training_records(employee_id);

-- -----------------------------------------------------------------------------
-- attrition_log: exit details for employees who left (optional enrichment)
-- -----------------------------------------------------------------------------
CREATE TABLE attrition_log (
    attrition_id        INT AUTO_INCREMENT PRIMARY KEY,
    employee_id           INT NOT NULL,
    exit_date               DATE NOT NULL,
    exit_reason              VARCHAR(100),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

CREATE INDEX idx_attr_employee ON attrition_log(employee_id);
