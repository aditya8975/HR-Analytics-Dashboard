# Power BI - HR Analytics Dashboard: Build Guide

This guide documents exactly how the `.pbix` file was (or should be) built,
page by page, so the design is fully reproducible and explainable in an
interview. Since a `.pbix` is a binary file, this markdown + the DAX
measures file together are the source of truth for rebuilding it.

## 0. Data Source Setup

1. Get Data > Text/CSV > select `data/processed/hr_data_cleaned.csv`
   **OR** Get Data > MySQL Database > server `127.0.0.1`, database
   `hr_analytics` > select tables `employees`, `departments`, `job_roles`,
   `education_levels`, `performance`, `training_records`.
2. If using MySQL, build relationships in Model view:
   - `employees[department_id]` → `departments[department_id]` (many-to-one)
   - `employees[job_role_id]` → `job_roles[job_role_id]` (many-to-one)
   - `employees[education_id]` → `education_levels[education_id]` (many-to-one)
   - `employees[employee_id]` → `performance[employee_id]` (one-to-many)
   - `employees[employee_id]` → `training_records[employee_id]` (one-to-many)
3. If using the single flat CSV, no relationships are needed - just load
   `hr_data_cleaned.csv` as table `HR`.
4. Add the `Calendar` date table from `DAX_Measures.md` Section 7 and mark
   it as a Date Table, related to `HR[HireDate]`.
5. Create the blank `_Measures` table and paste in all DAX from
   `DAX_Measures.md`.
6. Create a **Field Parameter** named `KPI Selector` (Modeling > New
   Parameter > Fields) containing: Total Employees, Attrition Rate,
   Average Salary, Promotion Rate, Average Experience, Average Performance.
   This powers the Dynamic Card on the Executive page.

---

## Page 1: Executive Dashboard

**Purpose:** One-glance summary for leadership.

**Layout:**
- Top KPI strip (6 cards): Total Employees, Attrition Rate, Average Salary,
  Promotion Rate, Average Experience, Average Performance Rating - each
  using the measures from Section 1 of `DAX_Measures.md`.
- **Dynamic Card** (large, top-right): bound to `Selected KPI Value` /
  `Selected KPI Label` measures, driven by the `KPI Selector` field
  parameter slicer placed directly above it - lets executives flip between
  metrics without leaving the page.
- Donut chart: Attrition (Yes/No).
- Column chart: Headcount by Department.
- Line chart: Hiring trend over time (`Calendar[Year]` on axis, Total
  Employees measure on values, using the HireDate relationship).
- Slicers (top bar, applied to all visuals on the page): Department,
  Gender, Age Group.

**Conditional formatting:** Attrition Rate KPI card background bound to
`Attrition Rate Color` measure (red/amber/green).

**Bookmark:** "Reset View" bookmark capturing default slicer state, exposed
as a button top-right, so users can undo any filtering with one click.

---

## Page 2: Employee Overview

**Purpose:** Demographic and workforce composition.

**Visuals:**
- Pie chart: Gender Ratio.
- Histogram (Power BI histogram custom visual or binned bar chart): Age
  Distribution.
- Stacked bar: Marital Status by Department.
- Table/matrix: Education level counts with % of workforce.
- Card: Average Distance From Home.
- Slicers: Department, Education, Marital Status.

**Drillthrough:** Right-click any department bar > Drillthrough to
"Department Analysis" page (see Page 3), automatically filtering it to
the selected department. Configured via Format pane > Drillthrough field
= `Department`, with a "Back" button auto-added.

---

## Page 3: Department Analysis

**Purpose:** Compare departments across every core metric side by side.

**Visuals:**
- Matrix/table: Department x (Headcount, Avg Salary, Avg Performance,
  Attrition Rate, Promotion Rate) - the multi-metric department summary
  table, with conditional formatting (data bars) on every numeric column.
- Clustered bar: Average Salary by Department.
- Clustered column: Average Performance Rating by Department.
- **Tooltip page**: a small hidden page (`Tooltip - Department Details`,
  set as a Tooltip page in Page Information) showing Headcount, Avg Salary,
  Attrition Rate, and Avg Performance for the hovered department; assigned
  as the Report Page Tooltip on all department-level visuals across the
  report.
- This page is also the **Drillthrough target** from Page 2 and Page 1.

---

## Page 4: Attrition Dashboard

**Purpose:** Diagnose *why* employees leave and *where* the risk is
concentrated.

**Visuals:**
- KPI cards: Attrition Rate, Attrition Rate - Overtime, Attrition Rate -
  No Overtime, Attrition Gap (OT vs No-OT).
- Bar chart: Attrition Rate by Department (sorted descending, using
  `Department Rank by Attrition` to highlight the #1 worst department in
  a distinct color via conditional formatting).
- Clustered column: Attrition count by OverTime status.
- Line/area chart: Attrition Rate by Tenure Group (0-1, 2-3, 4-7, 8+ yrs) -
  exposes early-tenure flight risk.
- Bar chart: Attrition Rate by Age Group.
- Slicers: Department, OverTime, Tenure Group.

**Bookmark group:** Two bookmarks - "By Department" and "By Tenure" -
toggling which secondary chart is visible via the Selection Pane
(hide/show objects), with buttons to switch between them, simulating tabs
within the page without needing separate pages.

---

## Page 5: Salary Dashboard

**Purpose:** Compensation analysis and pay-equity check.

**Visuals:**
- Card: Average Salary, Total Salary Cost.
- Box-and-whisker or column chart: Salary Distribution by Salary Band.
- Bar chart: Average Salary by Department (descending).
- Matrix: Average Salary by Department x Gender - pay-gap view, with
  conditional formatting icons flagging any gap greater than 10%.
- Scatter chart: Salary (Y) vs Years at Company (X), colored by
  Department, sized by Performance Rating - visualizes pay-for-tenure and
  pay-for-performance alignment.
- Slicers: Department, Job Role, Education.

---

## Page 6: Performance Dashboard

**Purpose:** Performance ratings, promotions, and training effectiveness.

**Visuals:**
- KPI cards: Average Performance Rating, High Performer %, Promotion Rate,
  Average Training Hours.
- Column chart: Performance Rating Distribution (1-5).
- Bar chart: Promotion Rate by Performance Rating (shows meritocracy
  trend).
- Bar chart: Average Training Hours - Attrition Yes vs No.
- Matrix: Department x Average Performance Rating, conditional formatting
  bound to `Performance Rating Color`.
- Slicers: Department, Performance Rating, Job Role.

---

## Cross-Page Features Checklist

| Feature | Where used |
|---|---|
| **Bookmarks** | Executive "Reset View"; Attrition "By Department"/"By Tenure" toggle |
| **Drillthrough** | Employee Overview → Department Analysis (filtered) |
| **Tooltips** | Custom Report Page Tooltip on all department-level visuals |
| **Dynamic Cards** | Executive Dashboard KPI Selector (Field Parameter) |
| **Conditional Formatting** | Attrition Rate cards, Performance matrix, Salary pay-gap matrix |
| **Slicers** | Department, Gender, Age Group, OverTime, Tenure Group, Education, Job Role (synced where relevant via Sync Slicers pane) |

## Theme / Styling

Use a custom JSON theme (View > Themes > Browse for themes) with a
consistent palette: primary `#2E5EAA` (headers/KPIs), accent `#3FA796`
(positive), `#F2A340` (warning), `#D64550` (negative/attrition), neutral
grays for backgrounds - matching the Matplotlib `viridis`/`rocket`
palettes used in the Python EDA so the whole project has a consistent
visual identity across Python and Power BI deliverables.
