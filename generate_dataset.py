# ============================================================
# EXPENSE VARIANCE DATASET GENERATOR
# Target: 50,000+ rows
# Company: 500-person Tech Company
# Period: January 2023 - December 2024 (2 years)
# ============================================================

import pandas as pd
import numpy as np
from faker import Faker
import random
import os
from datetime import datetime

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)
fake = Faker()
Faker.seed(42)

# ============================================================
# STEP 1 - DEFINE MASTER REFERENCE DATA
# ============================================================

departments = {
    'Engineering':  {'headcount': 180, 'annual_budget': 1_400_000, 'type': 'chronic_overspender',  'expenses_per_month': 5},
    'Sales':        {'headcount': 80,  'annual_budget': 820_000,  'type': 'chronic_overspender',  'expenses_per_month': 6},
    'Marketing':    {'headcount': 50,  'annual_budget': 640_000,  'type': 'seasonal_overspender', 'expenses_per_month': 5},
    'Operations':   {'headcount': 60,  'annual_budget': 480_000,  'type': 'seasonal_overspender', 'expenses_per_month': 4},
    'Product':      {'headcount': 40,  'annual_budget': 360_000,  'type': 'well_managed',         'expenses_per_month': 4},
    'HR':           {'headcount': 30,  'annual_budget': 280_000,  'type': 'well_managed',         'expenses_per_month': 3},
    'Finance':      {'headcount': 30,  'annual_budget': 160_000,  'type': 'well_managed',         'expenses_per_month': 3},
    'Legal':        {'headcount': 30,  'annual_budget': 260_000,  'type': 'chronic_overspender',  'expenses_per_month': 4},
}

dept_categories = {
    'Engineering':  ['Cloud Infrastructure', 'SaaS Subscriptions', 'Training',
                     'Salaries', 'Hardware', 'Software Licenses'],
    'Sales':        ['Travel', 'Client Entertainment', 'SaaS Subscriptions',
                     'Training', 'Commission Tools', 'Office Supplies'],
    'Marketing':    ['Marketing Campaigns', 'SaaS Subscriptions', 'Events',
                     'Travel', 'Design Tools', 'Content Production'],
    'Operations':   ['Office Supplies', 'Facilities', 'Software',
                     'Travel', 'Maintenance', 'Utilities'],
    'HR':           ['Recruitment', 'Training', 'Office Supplies',
                     'SaaS Subscriptions', 'Employee Benefits', 'Events'],
    'Finance':      ['SaaS Subscriptions', 'Audit Fees', 'Office Supplies',
                     'Training', 'Compliance Tools', 'Legal Consultation'],
    'Legal':        ['Legal Fees', 'SaaS Subscriptions', 'Travel',
                     'Compliance', 'Research Tools', 'Consulting'],
    'Product':      ['SaaS Subscriptions', 'Training', 'Travel',
                     'Research', 'Design Tools', 'Prototyping'],
}

# Realistic budget range per category per employee per month
category_budget_range = {
    'Cloud Infrastructure':  (3000, 8000),
    'SaaS Subscriptions':    (200,  1500),
    'Training':              (300,  2000),
    'Salaries':              (5000, 15000),
    'Hardware':              (500,  4000),
    'Software Licenses':     (200,  2000),
    'Travel':                (500,  5000),
    'Client Entertainment':  (200,  2000),
    'Commission Tools':      (100,  1000),
    'Office Supplies':       (50,   500),
    'Marketing Campaigns':   (2000, 10000),
    'Events':                (1000, 8000),
    'Design Tools':          (100,  800),
    'Content Production':    (500,  4000),
    'Facilities':            (1000, 5000),
    'Software':              (200,  2000),
    'Maintenance':           (500,  3000),
    'Utilities':             (300,  2000),
    'Recruitment':           (1000, 6000),
    'Employee Benefits':     (500,  3000),
    'Audit Fees':            (2000, 10000),
    'Compliance Tools':      (200,  1500),
    'Legal Consultation':    (500,  3000),
    'Legal Fees':            (2000, 12000),
    'Compliance':            (500,  3000),
    'Research Tools':        (200,  1500),
    'Consulting':            (1000, 8000),
    'Research':              (300,  2000),
    'Prototyping':           (200,  2000),
}

monthly_weights = {
    1: 0.055, 2: 0.065, 3: 0.080,
    4: 0.085, 5: 0.090, 6: 0.095,
    7: 0.080, 8: 0.075, 9: 0.085,
    10: 0.090, 11: 0.095, 12: 0.105,
}

seasonal_peaks = {
    'Marketing':  [5, 6, 11, 12],
    'Operations': [3, 6, 9, 12],
}

# ============================================================
# STEP 2 - GENERATE EMPLOYEES PER DEPARTMENT
# Each employee gets a unique ID and name
# ============================================================

employees = []
emp_counter = 1

for dept_name, dept_info in departments.items():
    for _ in range(dept_info['headcount']):
        employees.append({
            'employee_id':   f'EMP-{emp_counter:04d}',
            'employee_name': fake.name(),
            'department':    dept_name,
        })
        emp_counter += 1

employees_df = pd.DataFrame(employees)

# ============================================================
# STEP 3 - VARIANCE MULTIPLIER LOGIC
# ============================================================

def get_variance_multiplier(dept_name, dept_type, month):
    if dept_type == 'chronic_overspender':
        base_multiplier = np.random.uniform(1.15, 1.30)

    elif dept_type == 'seasonal_overspender':
        peak_months = seasonal_peaks.get(dept_name, [])
        if month in peak_months:
            base_multiplier = np.random.uniform(1.20, 1.40)
        else:
            base_multiplier = np.random.uniform(0.92, 1.05)

    elif dept_type == 'well_managed':
        base_multiplier = np.random.uniform(0.95, 1.05)

    else:
        base_multiplier = 1.0

    noise = np.random.uniform(-0.03, 0.03)
    final_multiplier = base_multiplier + noise
    final_multiplier = np.clip(final_multiplier, 0.60, 1.60)

    return round(final_multiplier, 4)

# ============================================================
# STEP 4 - APPROVER LOGIC
# ============================================================

def get_approver(actual_amount):
    if actual_amount < 5_000:
        return 'Manager'
    elif actual_amount < 20_000:
        return 'Director'
    elif actual_amount < 50_000:
        return 'VP'
    else:
        return 'CFO'

# ============================================================
# STEP 5 - MAIN GENERATION LOOP
# Employee level — one record per expense submission
# ============================================================

records = []
expense_counter = 1

for year in [2023, 2024]:
    for month in range(1, 13):

        weight = monthly_weights[month]

        for dept_name, dept_info in departments.items():

            dept_type = dept_info['type']
            headcount = dept_info['headcount']
            expenses_per_month = dept_info['expenses_per_month']
            categories = dept_categories[dept_name]

            # Get all employees in this department
            dept_employees = employees_df[
                employees_df['department'] == dept_name
            ]

            for _, emp_row in dept_employees.iterrows():

                # Each employee submits N expense records this month
                # Small random variation — not every employee submits same number
                n_expenses = random.randint(
                    max(1, expenses_per_month - 1),
                    expenses_per_month + 1
                )

                # Pick N random categories for this employee this month
                selected_categories = random.sample(
                    categories,
                    min(n_expenses, len(categories))
                )

                for category in selected_categories:

                    # Get budget range for this category
                    budget_min, budget_max = category_budget_range.get(
                        category, (100, 1000)
                    )

                    # Apply seasonal weight to budget
                    budget_amount = round(
                        np.random.uniform(budget_min, budget_max) * weight * 12,
                        2
                    )

                    if budget_amount < 50:
                        continue

                    # Get variance multiplier
                    multiplier = get_variance_multiplier(
                        dept_name, dept_type, month
                    )

                    actual_amount = round(budget_amount * multiplier, 2)

                    variance_amount = round(actual_amount - budget_amount, 2)
                    variance_pct = round(
                        (variance_amount / budget_amount) * 100, 2
                    )

                    if variance_pct > 5:
                        variance_status = 'Overspend'
                    elif variance_pct < -5:
                        variance_status = 'Underspend'
                    else:
                        variance_status = 'On-Track'

                    record = {
                        'expense_id':       f'EXP-{expense_counter:06d}',
                        'employee_id':      emp_row['employee_id'],
                        'employee_name':    emp_row['employee_name'],
                        'year':             year,
                        'month':            month,
                        'month_name':       datetime(year, month, 1).strftime('%B'),
                        'quarter':          f'Q{(month - 1) // 3 + 1}',
                        'department':       dept_name,
                        'expense_category': category,
                        'headcount':        headcount,
                        'budget_amount':    budget_amount,
                        'actual_amount':    actual_amount,
                        'variance_amount':  variance_amount,
                        'variance_pct':     variance_pct,
                        'variance_status':  variance_status,
                        'approver':         get_approver(actual_amount),
                        'fiscal_period':    f'{year}-{month:02d}',
                    }

                    records.append(record)
                    expense_counter += 1

# ============================================================
# STEP 6 - BUILD DATAFRAME
# ============================================================

df = pd.DataFrame(records)
print(f"Clean dataset rows: {len(df)}")
print(df.head())

# ============================================================
# STEP 7 - INTRODUCE DATA QUALITY ISSUES
# ============================================================

df_messy = df.copy()

null_indices = df_messy.sample(frac=0.02, random_state=42).index
df_messy.loc[null_indices, 'actual_amount'] = np.nan

duplicates = df_messy.sample(n=30, random_state=42)
df_messy = pd.concat([df_messy, duplicates], ignore_index=True)

inconsistent_indices = df_messy.sample(frac=0.05, random_state=42).index
df_messy.loc[inconsistent_indices, 'department'] = (
    df_messy.loc[inconsistent_indices, 'department'].str.upper()
)

zero_indices = df_messy.sample(n=10, random_state=42).index
df_messy.loc[zero_indices, 'actual_amount'] = 0

neg_indices = df_messy.sample(n=5, random_state=42).index
df_messy.loc[neg_indices, 'budget_amount'] = (
    df_messy.loc[neg_indices, 'budget_amount'] * -1
)

print(f"\nMessy dataset rows:     {len(df_messy)}")
print(f"Null actual_amount:      {df_messy['actual_amount'].isnull().sum()}")
print(f"Duplicate rows added:    30")
print(f"Zero actual amounts:     {(df_messy['actual_amount'] == 0).sum()}")

# ============================================================
# STEP 8 - EXPORT
# ============================================================

os.makedirs('data', exist_ok=True)

df.to_csv('data/expense_clean_reference.csv', index=False)
df_messy.to_csv('data/expense_data_raw.csv', index=False)

print(f"\nFinal row count: {len(df_messy)}")
print("Files saved successfully.")
print(df_messy.dtypes)