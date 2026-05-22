-- Expense Variance & Budget Analysis Project
-- Author: Shrey Aggrawal
-- SQL Analysis Queries


-- CREATE DATABASE expense_analysis;
USE expense_analysis;
-- RENAME TABLE expense_data_cleaned_final TO expense_data;

-- 1.Check exact table name

SHOW TABLES;
SELECT * 
FROM expense_data
LIMIT 5;

-- 2.Budget Variance Classification Per Department Per Month

SELECT
    department,
    year,
    month_name,
    quarter,
    COUNT(*) AS total_transactions,
    ROUND(SUM(budget_amount), 2) AS total_budget,
    ROUND(SUM(actual_amount), 2) AS total_actual,
    ROUND(SUM(variance_amount), 2) AS total_variance,
    ROUND(
        (SUM(variance_amount) / SUM(budget_amount)) * 100, 2
    ) AS variance_pct,
    CASE
        WHEN (SUM(variance_amount) / SUM(budget_amount)) * 100 > 5  
            THEN 'Overspend'
        WHEN (SUM(variance_amount) / SUM(budget_amount)) * 100 < -5 
            THEN 'Underspend'
        ELSE 'On-Track'
    END AS dept_status
FROM expense_data
GROUP BY department, year, month, month_name, quarter
ORDER BY year, month, total_variance DESC;

-- 3.Top 10 Overspend Categories

WITH category_variance AS (
    SELECT
        department,
        expense_category,
        ROUND(SUM(budget_amount), 2) AS total_budget,
        ROUND(SUM(actual_amount), 2) AS total_actual,
        ROUND(SUM(variance_amount), 2) AS total_variance,
        ROUND(
            (SUM(variance_amount) / SUM(budget_amount)) * 100, 2
        ) AS variance_pct
    FROM expense_data
    WHERE variance_status = 'Overspend'
    GROUP BY department, expense_category
),
ranked AS (
    SELECT *,
        RANK() OVER (ORDER BY total_variance DESC) AS rank_by_amount,
        RANK() OVER (ORDER BY variance_pct DESC) AS rank_by_pct
    FROM category_variance
)
SELECT
    department,
    expense_category,
    total_budget,
    total_actual,
    total_variance,
    variance_pct,
    rank_by_amount,
    rank_by_pct
FROM ranked
WHERE rank_by_amount <= 10 OR rank_by_pct <= 10
ORDER BY rank_by_amount;

-- 4.Month Over Month Variance Trend

WITH monthly_variance AS (
    SELECT
        department,
        year,
        month,
        month_name,
        ROUND(SUM(variance_amount), 2) AS total_variance,
        ROUND(
            (SUM(variance_amount) / SUM(budget_amount)) * 100, 2
        ) AS variance_pct
    FROM expense_data
    GROUP BY department, year, month, month_name
),
with_lag AS (
    SELECT *,
        LAG(total_variance) OVER (
            PARTITION BY department
            ORDER BY year, month
        ) AS prev_month_variance
    FROM monthly_variance
)
SELECT
    department,
    year,
    month_name,
    total_variance,
    variance_pct,
    prev_month_variance,
    ROUND(total_variance - prev_month_variance, 2) AS variance_change,
    CASE
        WHEN total_variance > prev_month_variance THEN 'Getting Worse'
        WHEN total_variance < prev_month_variance THEN 'Improving'
        ELSE 'Stable'
    END AS trend
FROM with_lag
ORDER BY department, year, month;

-- 5. Forecasting Accuracy Score

WITH dept_accuracy AS (
    SELECT
        department,
        year,
        ROUND(SUM(budget_amount), 2) AS annual_budget,
        ROUND(SUM(actual_amount), 2) AS annual_actual,
        ROUND(
            (1 - ABS(
                SUM(variance_amount) / SUM(budget_amount)
            )) * 100, 2
        ) AS forecast_accuracy_pct
    FROM expense_data
    GROUP BY department, year
)
SELECT
    department,
    year,
    annual_budget,
    annual_actual,
    forecast_accuracy_pct,
    CASE
        WHEN forecast_accuracy_pct >= 90 THEN 'Excellent'
        WHEN forecast_accuracy_pct >= 80 THEN 'Good'
        WHEN forecast_accuracy_pct >= 70 THEN 'Acceptable'
        ELSE 'Poor — Accountability Issue'
    END AS forecast_rating,
    CASE
        WHEN forecast_accuracy_pct < 70 THEN 'Flag For Review'
        ELSE 'No Action Needed'
    END AS action_required
FROM dept_accuracy
ORDER BY forecast_accuracy_pct ASC;

-- 6. Expense Per Employee

SELECT
    department,
    year,
    MAX(headcount) AS headcount,
    ROUND(SUM(budget_amount), 2) AS total_budget,
    ROUND(SUM(actual_amount), 2) AS total_actual,
    ROUND(SUM(variance_amount), 2) AS total_variance,
    ROUND(SUM(budget_amount) / MAX(headcount), 2) AS budget_per_employee,
    ROUND(SUM(actual_amount) / MAX(headcount), 2) AS actual_per_employee,
    ROUND(SUM(variance_amount) / MAX(headcount), 2) AS variance_per_employee,
    RANK() OVER (
        PARTITION BY year
        ORDER BY SUM(actual_amount) / MAX(headcount) DESC
    ) AS cost_rank
FROM expense_data
GROUP BY department, year
ORDER BY year, actual_per_employee DESC;

-- 7.Annual Summary

SELECT
    year,
    ROUND(SUM(budget_amount), 2) AS total_budget,
    ROUND(SUM(actual_amount), 2) AS total_actual,
    ROUND(SUM(variance_amount), 2) AS total_variance,
    ROUND(
        (SUM(variance_amount) / SUM(budget_amount)) * 100, 2
    ) AS overall_variance_pct,
    COUNT(DISTINCT department) AS departments,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN variance_status = 'Overspend' 
        THEN 1 ELSE 0 END) AS overspend_records,
    SUM(CASE WHEN variance_status = 'Underspend' 
        THEN 1 ELSE 0 END) AS underspend_records,
    SUM(CASE WHEN variance_status = 'On-Track' 
        THEN 1 ELSE 0 END) AS ontrack_records
FROM expense_data
GROUP BY year
ORDER BY year;

-- 8.Quarterly Variance Trend

SELECT
    department,
    year,
    quarter,
    ROUND(SUM(budget_amount), 2) AS quarterly_budget,
    ROUND(SUM(actual_amount), 2) AS quarterly_actual,
    ROUND(SUM(variance_amount), 2) AS quarterly_variance,
    ROUND(
        (SUM(variance_amount) / SUM(budget_amount)) * 100, 2
    ) AS quarterly_variance_pct,
    RANK() OVER (
        PARTITION BY year, quarter
        ORDER BY SUM(variance_amount) DESC
    ) AS overspend_rank
FROM expense_data
GROUP BY department, year, quarter
ORDER BY year, quarter, quarterly_variance DESC;

-- 9. Approver Level Spend Analysis 

SELECT
    approver,
    department,
    COUNT(*) AS total_transactions,
    ROUND(SUM(budget_amount), 2) AS total_budget,
    ROUND(SUM(actual_amount), 2) AS total_actual,
    ROUND(SUM(variance_amount), 2) AS total_variance,
    ROUND(
        (SUM(variance_amount) / SUM(budget_amount)) * 100, 2
    ) AS variance_pct,
    ROUND(AVG(actual_amount), 2) AS avg_transaction_value
FROM expense_data
GROUP BY approver, department
ORDER BY
    FIELD(approver, 'CFO', 'VP', 'Director', 'Manager'),
    total_variance DESC;

-- 10.Variance Severity Distribution

SELECT
    department,
    year,
    variance_severity,
    COUNT(*) AS transaction_count,
    ROUND(SUM(actual_amount), 2) AS total_spend,
    ROUND(SUM(variance_amount), 2) AS total_variance,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (
            PARTITION BY department, year
        ), 2
    ) AS pct_of_dept_transactions
FROM expense_data
GROUP BY department, year, variance_severity
ORDER BY department, year, total_variance DESC;

-- 11. High Risk Expense Flagging

SELECT
    expense_id,
    employee_name,
    department,
    expense_category,
    fiscal_period,
    approver,
    ROUND(budget_amount, 2) AS budget_amount,
    ROUND(actual_amount, 2) AS actual_amount,
    ROUND(variance_amount, 2) AS variance_amount,
    ROUND(variance_pct, 2) AS variance_pct,
    variance_severity,
    utilization_category
FROM expense_data
WHERE variance_severity = 'Critical Overspend'
   OR (variance_severity = 'Moderate Overspend'
       AND actual_amount > 10000)
ORDER BY variance_amount DESC
LIMIT 50;


SELECT AVG(variance_amount) FROM expense_data;