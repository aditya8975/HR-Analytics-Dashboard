-- =============================================================================
-- HR ANALYTICS - SQL INTERVIEW-LEVEL QUERY BANK (30 QUERIES)
-- =============================================================================
-- Run after 01_schema.sql and 02_data_import.py have populated the database.
-- Organized by category. Each query has a comment explaining its purpose.
-- =============================================================================

USE hr_analytics;

-- =============================================================================
-- CATEGORY 1: EMPLOYEE COUNT
-- =============================================================================

-- Q1. Total number of employees currently in the company
SELECT COUNT(*) AS total_employees
FROM employees;

-- Q2. Employee count per department
SELECT d.department_name, COUNT(*) AS employee_count
FROM employees e
JOIN departments d ON e.department_id = d.department_id
GROUP BY d.department_name
ORDER BY employee_count DESC;

-- Q3. Employee count by gender within each department (pivot-style)
SELECT d.department_name,
       SUM(CASE WHEN e.gender = 'Male' THEN 1 ELSE 0 END)   AS male_count,
       SUM(CASE WHEN e.gender = 'Female' THEN 1 ELSE 0 END) AS female_count
FROM employees e
JOIN departments d ON e.department_id = d.department_id
GROUP BY d.department_name;

-- Q4. Number of active employees (not attrited) vs employees who left
SELECT attrition, COUNT(*) AS emp_count
FROM employees
GROUP BY attrition;

-- =============================================================================
-- CATEGORY 2: AVERAGE SALARY
-- =============================================================================

-- Q5. Overall average salary
SELECT ROUND(AVG(salary), 2) AS avg_salary
FROM employees;

-- Q6. Average salary per department, sorted highest to lowest
SELECT d.department_name, ROUND(AVG(e.salary), 2) AS avg_salary
FROM employees e
JOIN departments d ON e.department_id = d.department_id
GROUP BY d.department_name
ORDER BY avg_salary DESC;

-- Q7. Average salary by job role within a specific department (parameterized example: Engineering)
SELECT jr.job_role_name, ROUND(AVG(e.salary), 2) AS avg_salary
FROM employees e
JOIN job_roles jr ON e.job_role_id = jr.job_role_id
JOIN departments d ON e.department_id = d.department_id
WHERE d.department_name = 'Engineering'
GROUP BY jr.job_role_name
ORDER BY avg_salary DESC;

-- Q8. Average salary by education level
SELECT el.education_name, ROUND(AVG(e.salary), 2) AS avg_salary
FROM employees e
JOIN education_levels el ON e.education_id = el.education_id
GROUP BY el.education_name
ORDER BY avg_salary DESC;

-- Q9. Employees earning above the company-wide average salary (subquery)
SELECT employee_id, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees)
ORDER BY salary DESC;

-- Q10. Top 5 highest paid employees with department and job role
SELECT e.employee_id, d.department_name, jr.job_role_name, e.salary
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN job_roles jr ON e.job_role_id = jr.job_role_id
ORDER BY e.salary DESC
LIMIT 5;

-- =============================================================================
-- CATEGORY 3: DEPARTMENT PERFORMANCE
-- =============================================================================

-- Q11. Average performance rating per department
SELECT d.department_name, ROUND(AVG(p.performance_rating), 2) AS avg_rating
FROM performance p
JOIN employees e ON p.employee_id = e.employee_id
JOIN departments d ON e.department_id = d.department_id
GROUP BY d.department_name
ORDER BY avg_rating DESC;

-- Q12. Department combining headcount, average salary, and average performance in one view
SELECT
    d.department_name,
    COUNT(e.employee_id)              AS headcount,
    ROUND(AVG(e.salary), 2)           AS avg_salary,
    ROUND(AVG(p.performance_rating),2) AS avg_performance
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN performance p ON e.employee_id = p.employee_id
GROUP BY d.department_name
ORDER BY avg_performance DESC;

-- Q13. Departments where average performance rating is below the company average (HAVING + subquery)
SELECT d.department_name, ROUND(AVG(p.performance_rating), 2) AS avg_rating
FROM performance p
JOIN employees e ON p.employee_id = e.employee_id
JOIN departments d ON e.department_id = d.department_id
GROUP BY d.department_name
HAVING AVG(p.performance_rating) < (SELECT AVG(performance_rating) FROM performance);

-- Q14. Count of top performers (rating 4 or 5) by department
SELECT d.department_name, COUNT(*) AS top_performers
FROM performance p
JOIN employees e ON p.employee_id = e.employee_id
JOIN departments d ON e.department_id = d.department_id
WHERE p.performance_rating >= 4
GROUP BY d.department_name
ORDER BY top_performers DESC;

-- =============================================================================
-- CATEGORY 4: HIGHEST ATTRITION
-- =============================================================================

-- Q15. Attrition rate (%) by department
SELECT
    d.department_name,
    ROUND(SUM(CASE WHEN e.attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS attrition_rate_pct
FROM employees e
JOIN departments d ON e.department_id = d.department_id
GROUP BY d.department_name
ORDER BY attrition_rate_pct DESC;

-- Q16. Department with the single highest attrition rate (ORDER BY + LIMIT)
SELECT
    d.department_name,
    ROUND(SUM(CASE WHEN e.attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS attrition_rate_pct
FROM employees e
JOIN departments d ON e.department_id = d.department_id
GROUP BY d.department_name
ORDER BY attrition_rate_pct DESC
LIMIT 1;

-- Q17. Attrition rate comparison: overtime vs non-overtime employees
SELECT
    overtime,
    ROUND(SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS attrition_rate_pct
FROM employees
GROUP BY overtime;

-- Q18. Employees who left within their first year (early attrition risk)
SELECT employee_id, years_at_company, salary, overtime
FROM employees
WHERE attrition = 'Yes' AND years_at_company <= 1;

-- Q19. Attrition rate by age group (using CASE for bucketing)
SELECT
    CASE
        WHEN age BETWEEN 18 AND 25 THEN '18-25'
        WHEN age BETWEEN 26 AND 35 THEN '26-35'
        WHEN age BETWEEN 36 AND 45 THEN '36-45'
        ELSE '46-60'
    END AS age_group,
    ROUND(SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS attrition_rate_pct
FROM employees
GROUP BY age_group
ORDER BY age_group;

-- Q20. Monthly exit trend from attrition_log
SELECT DATE_FORMAT(exit_date, '%Y-%m') AS exit_month, COUNT(*) AS exits
FROM attrition_log
GROUP BY exit_month
ORDER BY exit_month;

-- =============================================================================
-- CATEGORY 5: PROMOTION RATE
-- =============================================================================

-- Q21. Overall promotion rate (%)
SELECT ROUND(SUM(CASE WHEN promotion = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS promotion_rate_pct
FROM employees;

-- Q22. Promotion rate by performance rating (shows meritocracy link)
SELECT
    p.performance_rating,
    ROUND(SUM(CASE WHEN e.promotion = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS promotion_rate_pct
FROM employees e
JOIN performance p ON e.employee_id = p.employee_id
GROUP BY p.performance_rating
ORDER BY p.performance_rating;

-- Q23. Promotion rate by department
SELECT d.department_name,
       ROUND(SUM(CASE WHEN e.promotion = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS promotion_rate_pct
FROM employees e
JOIN departments d ON e.department_id = d.department_id
GROUP BY d.department_name
ORDER BY promotion_rate_pct DESC;

-- Q24. Employees promoted despite below-average performance (data quality / exception check)
SELECT e.employee_id, d.department_name, p.performance_rating, e.promotion
FROM employees e
JOIN performance p ON e.employee_id = p.employee_id
JOIN departments d ON e.department_id = d.department_id
WHERE e.promotion = 'Yes' AND p.performance_rating < 3;

-- =============================================================================
-- CATEGORY 6: EXPERIENCE ANALYSIS
-- =============================================================================

-- Q25. Average years at company overall and by department
SELECT d.department_name, ROUND(AVG(e.years_at_company), 2) AS avg_tenure_years
FROM employees e
JOIN departments d ON e.department_id = d.department_id
GROUP BY d.department_name
ORDER BY avg_tenure_years DESC;

-- Q26. Tenure bucket distribution (0-1, 2-3, 4-7, 8+) using CASE
SELECT
    CASE
        WHEN years_at_company <= 1 THEN '0-1 yrs'
        WHEN years_at_company BETWEEN 2 AND 3 THEN '2-3 yrs'
        WHEN years_at_company BETWEEN 4 AND 7 THEN '4-7 yrs'
        ELSE '8+ yrs'
    END AS tenure_bucket,
    COUNT(*) AS employee_count
FROM employees
GROUP BY tenure_bucket
ORDER BY MIN(years_at_company);

-- Q27. Correlation proxy: average salary by tenure bucket (shows experience-pay relationship)
SELECT
    CASE
        WHEN years_at_company <= 1 THEN '0-1 yrs'
        WHEN years_at_company BETWEEN 2 AND 3 THEN '2-3 yrs'
        WHEN years_at_company BETWEEN 4 AND 7 THEN '4-7 yrs'
        ELSE '8+ yrs'
    END AS tenure_bucket,
    ROUND(AVG(salary), 2) AS avg_salary
FROM employees
GROUP BY tenure_bucket
ORDER BY MIN(years_at_company);

-- Q28. Longest-serving employee in each department (window function)
SELECT department_name, employee_id, years_at_company
FROM (
    SELECT d.department_name, e.employee_id, e.years_at_company,
           RANK() OVER (PARTITION BY d.department_name ORDER BY e.years_at_company DESC) AS rnk
    FROM employees e
    JOIN departments d ON e.department_id = d.department_id
) ranked
WHERE rnk = 1;

-- =============================================================================
-- CATEGORY 7: ADVANCED / MISCELLANEOUS INTERVIEW QUERIES
-- =============================================================================

-- Q29. Running total of headcount by hire year (window function)
SELECT hire_year, employees_hired,
       SUM(employees_hired) OVER (ORDER BY hire_year) AS running_total
FROM (
    SELECT YEAR(hire_date) AS hire_year, COUNT(*) AS employees_hired
    FROM employees
    GROUP BY hire_year
) yearly
ORDER BY hire_year;

-- Q30. Rank employees by salary within their department (window function)
SELECT employee_id, department_name, salary,
       RANK() OVER (PARTITION BY department_name ORDER BY salary DESC) AS salary_rank
FROM (
    SELECT e.employee_id, d.department_name, e.salary
    FROM employees e
    JOIN departments d ON e.department_id = d.department_id
) x;

-- Q31. Second highest salary overall (classic interview question, no LIMIT/OFFSET dependency)
SELECT MAX(salary) AS second_highest_salary
FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);

-- Q32. Departments with more than 100 employees (HAVING clause)
SELECT d.department_name, COUNT(*) AS headcount
FROM employees e
JOIN departments d ON e.department_id = d.department_id
GROUP BY d.department_name
HAVING COUNT(*) > 100;

-- Q33. Employees with no promotion in 5+ years of tenure (potential flight risk / stagnation)
SELECT employee_id, years_at_company, promotion
FROM employees
WHERE years_at_company >= 5 AND promotion = 'No';

-- Q34. Gender pay gap check: average salary by gender within each department
SELECT d.department_name, e.gender, ROUND(AVG(e.salary), 2) AS avg_salary
FROM employees e
JOIN departments d ON e.department_id = d.department_id
GROUP BY d.department_name, e.gender
ORDER BY d.department_name, e.gender;

-- Q35. Employees whose training hours are below the department average (correlated subquery)
SELECT e.employee_id, d.department_name, t.training_hours
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN training_records t ON e.employee_id = t.employee_id
WHERE t.training_hours < (
    SELECT AVG(t2.training_hours)
    FROM training_records t2
    JOIN employees e2 ON t2.employee_id = e2.employee_id
    WHERE e2.department_id = e.department_id
);

-- =============================================================================
-- END OF QUERY BANK (35 queries - exceeds the 25 query requirement)
-- =============================================================================
