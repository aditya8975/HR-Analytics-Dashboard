# Power BI - DAX Measures Library

This file contains every DAX measure used across the HR Analytics dashboard.
Import `hr_data_cleaned.csv` (or connect directly to the `hr_analytics` MySQL
database) as the single data table, name it **HR** in Power BI, then create a
dedicated **Measures Table** (a blank table with no rows, used only to hold
measures - best practice for keeping the model clean) and paste these in.

> Tip: Home > Enter Data > name it `_Measures` > OK. Then right-click `_Measures`
> in the Fields pane > New Measure for each one below.

---

## 1. Core KPI Measures

```dax
Total Employees =
COUNTROWS(HR)
```

```dax
Active Employees =
CALCULATE(COUNTROWS(HR), HR[Attrition] = "No")
```

```dax
Employees Left =
CALCULATE(COUNTROWS(HR), HR[Attrition] = "Yes")
```

```dax
Attrition Rate =
DIVIDE([Employees Left], [Total Employees], 0)
```

```dax
Average Salary =
AVERAGE(HR[Salary])
```

```dax
Total Salary Cost =
SUM(HR[Salary])
```

```dax
Promotion Rate =
DIVIDE(
    CALCULATE(COUNTROWS(HR), HR[Promotion] = "Yes"),
    [Total Employees],
    0
)
```

```dax
Average Experience (Years) =
AVERAGE(HR[YearsAtCompany])
```

```dax
Average Performance Rating =
AVERAGE(HR[PerformanceRating])
```

```dax
Average Training Hours =
AVERAGE(HR[TrainingHours])
```

```dax
High Performer Count =
CALCULATE(COUNTROWS(HR), HR[PerformanceRating] >= 4)
```

```dax
High Performer % =
DIVIDE([High Performer Count], [Total Employees], 0)
```

---

## 2. Attrition Deep-Dive Measures

```dax
Attrition Rate - Overtime =
CALCULATE(
    [Attrition Rate],
    HR[OverTime] = "Yes"
)
```

```dax
Attrition Rate - No Overtime =
CALCULATE(
    [Attrition Rate],
    HR[OverTime] = "No"
)
```

```dax
Attrition Gap (OT vs No-OT) =
[Attrition Rate - Overtime] - [Attrition Rate - No Overtime]
```

```dax
Attrition Rate by Department (Highest) =
VAR DeptTable =
    ADDCOLUMNS(
        VALUES(HR[Department]),
        "AttrRate", CALCULATE([Attrition Rate])
    )
RETURN
    MAXX(DeptTable, [AttrRate])
```

```dax
YoY Attrition Change =
VAR CurrentYearAttr = [Attrition Rate]
VAR PriorYearAttr =
    CALCULATE(
        [Attrition Rate],
        DATEADD('Calendar'[Date], -1, YEAR)
    )
RETURN
    CurrentYearAttr - PriorYearAttr
```
*(Requires a Calendar/date dimension table marked as a Date Table, related to HireDate — see Section 5.)*

---

## 3. Ranking & Comparative Measures

```dax
Department Rank by Attrition =
RANKX(
    ALL(HR[Department]),
    CALCULATE([Attrition Rate]),
    ,
    DESC
)
```

```dax
Salary Rank Within Department =
RANKX(
    FILTER(ALL(HR), HR[Department] = EARLIER(HR[Department])),
    HR[Salary],
    ,
    DESC
)
```
*(Better implemented as a calculated column, or with `RANKX` + `ALLEXCEPT` as a measure:)*

```dax
Salary Rank Within Department (Measure) =
RANKX(
    ALLEXCEPT(HR, HR[Department]),
    CALCULATE(AVERAGE(HR[Salary]))
)
```

```dax
Salary vs Department Average =
DIVIDE(
    AVERAGE(HR[Salary]),
    CALCULATE(AVERAGE(HR[Salary]), ALLEXCEPT(HR, HR[Department])),
    0
) - 1
```

---

## 4. Dynamic / Conditional Card Measures (for Executive Dashboard)

Used to power a "dynamic card" that swaps its displayed KPI based on a
Field Parameter or slicer selection (see Dashboard_Design_Guide.md for setup).

```dax
Selected KPI Value =
VAR SelectedMetric = SELECTEDVALUE('KPI Selector'[KPI])
RETURN
    SWITCH(
        TRUE(),
        SelectedMetric = "Total Employees", [Total Employees],
        SelectedMetric = "Attrition Rate", [Attrition Rate],
        SelectedMetric = "Average Salary", [Average Salary],
        SelectedMetric = "Promotion Rate", [Promotion Rate],
        SelectedMetric = "Average Experience", [Average Experience (Years)],
        SelectedMetric = "Average Performance", [Average Performance Rating],
        BLANK()
    )
```

```dax
Selected KPI Label =
SELECTEDVALUE('KPI Selector'[KPI], "Total Employees")
```

---

## 5. Conditional Formatting Helper Measures

```dax
Attrition Rate Color =
VAR R = [Attrition Rate]
RETURN
    SWITCH(
        TRUE(),
        R >= 0.25, "#D64550",   -- red: high risk
        R >= 0.15, "#F2A340",   -- amber: moderate risk
        "#3FA796"               -- green: healthy
    )
```

```dax
Performance Rating Color =
VAR AvgR = [Average Performance Rating]
RETURN
    SWITCH(
        TRUE(),
        AvgR >= 4, "#3FA796",
        AvgR >= 3, "#F2A340",
        "#D64550"
    )
```

Apply these via *Conditional Formatting > Font/Background Color > Format by:
Field value* on the relevant KPI cards and matrix cells.

---

## 6. Tooltip Page Measures (Department Hover Tooltip)

```dax
Tooltip Headcount = [Total Employees]
Tooltip Avg Salary = [Average Salary]
Tooltip Attrition Rate = [Attrition Rate]
Tooltip Avg Performance = [Average Performance Rating]
```
These four feed a small **Tooltip Page** (see Dashboard_Design_Guide.md) that
appears when hovering over any department bar/column across the report.

---

## 7. Date Table (required for time intelligence measures like YoY)

```dax
Calendar =
ADDCOLUMNS(
    CALENDAR(DATE(2015,1,1), DATE(2024,12,31)),
    "Year", YEAR([Date]),
    "Month", FORMAT([Date], "MMM"),
    "MonthNumber", MONTH([Date]),
    "Quarter", "Q" & FORMAT([Date], "Q")
)
```
Mark this table as a **Date Table** (Table tools > Mark as Date Table) and
relate `Calendar[Date]` (1) to `HR[HireDate]` (*) as a one-to-many, single
-direction relationship.

---

## Summary Table of All Measures

| Measure | Purpose | Used On |
|---|---|---|
| Total Employees | Headcount KPI | Executive, Overview |
| Attrition Rate | % who left | Executive, Attrition |
| Average Salary | Compensation KPI | Executive, Salary |
| Promotion Rate | % promoted | Executive, Performance |
| Average Experience (Years) | Tenure KPI | Executive, Overview |
| Average Performance Rating | Quality KPI | Executive, Performance |
| Attrition Gap (OT vs No-OT) | Root-cause driver | Attrition Dashboard |
| Department Rank by Attrition | Highlights worst dept | Attrition Dashboard |
| Salary Rank Within Department | Pay equity check | Salary Dashboard |
| Selected KPI Value/Label | Dynamic card | Executive Dashboard |
| *Color measures | Conditional formatting | All pages |
| Tooltip * measures | Custom hover tooltip | All chart pages |
