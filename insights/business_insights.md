# HR Analytics - Business Insights

Auto-generated from `02_eda_analysis.py` based on the cleaned dataset.

### Employee Distribution
Finance is the largest department, holding 13.9% of the total workforce (208 employees). Workforce planning and headcount budgeting should weight this department accordingly.

### Gender Ratio
The workforce is 55.0% Male and 45.0% Female. This is a reasonably balanced split, but HR should track this ratio per department to spot any localized imbalance (e.g. Engineering vs HR).

### Salary Distribution
Median salary is $74,600 with a right-skewed distribution (mean $78,904 > median), driven by a smaller group of senior/management roles earning $90K+. This skew is expected and should be considered when setting compensation benchmarks (median is a better central measure than mean).

### Age Distribution
The average employee age is 34.7 years, with the majority falling in the 26-35 bracket. A workforce concentrated in early-to-mid career ranges suggests strong growth potential but also a need for succession planning as senior staff approach retirement.

### Department Analysis
Engineering has the highest average salary ($115,073), while Customer Support has the lowest ($57,150). Full department-level KPI table saved to insights/department_summary.csv for further review.

### Attrition Analysis
Overall attrition rate is 17.7%. Engineering has the highest departmental attrition at 21.4%. Employees working overtime leave at 32.4% vs 12.6% for those who don't - overtime is a strong attrition risk factor and a priority area for retention initiatives.

### Performance Ratings
43.9% of employees are rated 4 or 5 (high performers). Average performance rating company-wide is 3.37/5. Departments with lower median ratings may need targeted coaching or clearer performance-management processes.

### Promotion Analysis
Overall promotion rate is 18.4%. Promotion rate rises sharply with performance rating (from 8.5% at rating 1 to 31.6% at rating 5), confirming the promotion process is meritocratic and tightly linked to performance outcomes.

### Training Analysis
Average training hours are nearly identical between employees who stayed (39.2h) and those who left (39.2h). Training volume alone is not a strong predictor of attrition in this dataset - retention efforts should instead focus on factors like overtime and department shown above.

### Correlation Insights
Salary correlates most strongly with YearsAtCompany, confirming tenure-based compensation growth. No numeric variable shows a strong (>0.5) correlation with Attrition alone, indicating attrition is a multi-factor outcome best modeled with categorical drivers like OverTime and Department rather than a single numeric metric.
