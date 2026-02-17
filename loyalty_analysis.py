"""
CUSTOMER LOYALTY FRAMEWORK ANALYSIS SCRIPT

Purpose: Identify loyal customers based on tenure, consistency, and revenue criteria.
         Generates output file for PowerBI integration and quarterly monitoring.

Version: 1.0
Created: November 9, 2024
Author: Kent Schneider
Last Updated: November 9, 2024

Usage:
    python loyalty_analysis.py

Requirements:
    - Python 3.7+
    - pandas library
    - Input file: customer_annual_revenue.csv (in same directory)
    - Config file: loyalty_config.py (in same directory)

Output:
    - loyalty_analysis_YYYYMMDD_HHMMSS.csv in current directory
    - Console summary statistics
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Import configuration
try:
    from loyalty_config import LOYALTY_CONFIG, EVALUATION_YEARS, NUM_EVALUATION_YEARS
except ImportError:
    print("ERROR: loyalty_config.py not found in current directory.")
    print("Please ensure loyalty_config.py is in the same folder as this script.")
    sys.exit(1)

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

INPUT_FILE = "customer_annual_revenue.csv"
CURRENT_YEAR = LOYALTY_CONFIG["current_year"]

# Extract thresholds from config
MIN_TENURE = LOYALTY_CONFIG["min_tenure_years"]
MIN_CONSISTENCY = LOYALTY_CONFIG["min_consistency_rate"]
MIN_REVENUE_5YR = LOYALTY_CONFIG["min_revenue_5yr"]
MIN_REVENUE_PER_YEAR = LOYALTY_CONFIG["min_revenue_per_active_year"]

print("="*80)
print("CUSTOMER LOYALTY FRAMEWORK ANALYSIS")
print("="*80)
print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Framework Version: 1.0")
print(f"\nConfiguration:")
print(f"  • Minimum Tenure: {MIN_TENURE} years")
print(f"  • Minimum Consistency: {MIN_CONSISTENCY:.0%} ({int(MIN_CONSISTENCY * NUM_EVALUATION_YEARS)} of {NUM_EVALUATION_YEARS} years)")
print(f"  • Minimum 5-Year Revenue: ${MIN_REVENUE_5YR:,}")
print(f"  • Min Revenue Per Active Year: ${MIN_REVENUE_PER_YEAR:,} {'(DISABLED)' if MIN_REVENUE_PER_YEAR == 0 else '(ENABLED)'}")
print(f"  • Evaluation Window: {LOYALTY_CONFIG['evaluation_start_year']}-{LOYALTY_CONFIG['evaluation_end_year']}")
print("="*80)

# ============================================================================
# DATA CLEANING FUNCTIONS
# ============================================================================

def clean_currency(val):
    """
    Clean currency values from various formats to float.
    
    Handles:
    - Blank/null values → 0.0
    - Dollar signs, commas → removed
    - Parentheses (accounting format) → negative numbers
    - Both numeric and string inputs
    
    Examples:
        "$1,234.56" → 1234.56
        "($500.00)" → -500.00
        "" → 0.0
        1234.56 → 1234.56
    
    Args:
        val: Input value (string, numeric, or null)
        
    Returns:
        float: Cleaned numeric value
    """
    # Handle null/blank
    if pd.isna(val) or val == '' or val == ' ':
        return 0.0
    
    # Already numeric
    if isinstance(val, (int, float)):
        return float(val)
    
    # String processing
    val = str(val).strip()
    
    # Handle parentheses (negative in accounting format)
    is_negative = False
    if val.startswith('(') and val.endswith(')'):
        is_negative = True
        val = val[1:-1]  # Remove parentheses
    
    # Remove currency symbols, commas, spaces
    val = val.replace('$', '').replace(',', '').replace(' ', '')
    
    # Convert to float
    try:
        result = float(val)
        if is_negative:
            result = -abs(result)
        return result
    except ValueError:
        return 0.0

def infer_first_order_year(row, year_columns):
    """
    Infer first order year from revenue data if First Order Date is blank.
    
    Finds the earliest year with positive revenue.
    
    Args:
        row: DataFrame row
        year_columns: List of revenue column names to check
        
    Returns:
        int or None: Year of first order, or None if no revenue found
    """
    for col in year_columns:
        if row[col] > 0:  # First year with positive revenue
            # Extract year from column name (e.g., "revenue_2020" → 2020)
            return int(col.split('_')[1])
    return None

# ============================================================================
# DATA LOADING & VALIDATION
# ============================================================================

print("\n" + "-"*80)
print("STEP 1: LOADING DATA")
print("-"*80)

# Check if input file exists
if not os.path.exists(INPUT_FILE):
    print(f"ERROR: Input file '{INPUT_FILE}' not found.")
    print(f"Please ensure {INPUT_FILE} is in the same directory as this script.")
    sys.exit(1)

# Load data
try:
    df = pd.read_csv(INPUT_FILE, encoding='utf-8-sig')
    print(f"✓ Successfully loaded {len(df):,} customer records")
except Exception as e:
    print(f"ERROR: Failed to load {INPUT_FILE}")
    print(f"Error message: {str(e)}")
    sys.exit(1)

# Validate required columns exist
required_columns = ['Account_ID', 'Name', 'Sub Segment', 'First Order Date']
revenue_columns_raw = [f'TY Net Product Revenue {year}' for year in EVALUATION_YEARS]
required_columns.extend(revenue_columns_raw)

missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    print(f"ERROR: Missing required columns: {missing_columns}")
    print(f"\nExpected columns: {required_columns}")
    print(f"Found columns: {list(df.columns)}")
    sys.exit(1)

print(f"✓ All required columns present")

# Check for duplicate Account_IDs
duplicates = df['Account_ID'].duplicated().sum()
if duplicates > 0:
    print(f"WARNING: {duplicates} duplicate Account_IDs found")
    print(f"Keeping first occurrence of each duplicate")
    df = df.drop_duplicates(subset=['Account_ID'], keep='first')

# ============================================================================
# DATA CLEANING & TRANSFORMATION
# ============================================================================

print("\n" + "-"*80)
print("STEP 2: CLEANING DATA")
print("-"*80)

# Clean revenue columns
print("Cleaning revenue columns...")
for year in EVALUATION_YEARS:
    col_raw = f'TY Net Product Revenue {year}'
    col_clean = f'revenue_{year}'
    df[col_clean] = df[col_raw].apply(clean_currency)
    
    # Track statistics
    negative_count = (df[col_clean] < 0).sum()
    if negative_count > 0:
        print(f"  • {year}: {negative_count:,} negative values (returns/credits)")

print(f"✓ Revenue columns cleaned for {len(EVALUATION_YEARS)} years")

# Parse First Order Date
print("\nParsing First Order Date...")
df['first_order_date_parsed'] = pd.to_datetime(df['First Order Date'], errors='coerce')

# Infer missing dates from revenue
blank_dates = df['first_order_date_parsed'].isna().sum()
if blank_dates > 0:
    print(f"  • {blank_dates:,} blank/invalid dates found")
    print(f"  • Inferring from first year with revenue...")
    
    revenue_cols = [f'revenue_{year}' for year in EVALUATION_YEARS]
    df['inferred_year'] = df.apply(lambda row: infer_first_order_year(row, revenue_cols), axis=1)
    
    # Use parsed year if available, otherwise use inferred
    df['first_order_year'] = df['first_order_date_parsed'].dt.year
    df.loc[df['first_order_year'].isna(), 'first_order_year'] = df.loc[df['first_order_year'].isna(), 'inferred_year']
    
    inferred_count = df['inferred_year'].notna().sum()
    print(f"  • Successfully inferred {inferred_count:,} dates from revenue data")
else:
    df['first_order_year'] = df['first_order_date_parsed'].dt.year

# Handle customers with no date and no revenue
no_data = df['first_order_year'].isna().sum()
if no_data > 0:
    print(f"  • WARNING: {no_data:,} customers have no date and no revenue")
    print(f"  • These will be excluded from analysis")

print(f"✓ First Order Date processed")

# ============================================================================
# METRIC CALCULATIONS
# ============================================================================

print("\n" + "-"*80)
print("STEP 3: CALCULATING LOYALTY METRICS")
print("-"*80)

# Calculate tenure
df['tenure_years'] = CURRENT_YEAR - df['first_order_year']
print(f"✓ Tenure calculated (range: {df['tenure_years'].min():.0f} to {df['tenure_years'].max():.0f} years)")

# Calculate active years (considering per-year minimum if enabled)
print(f"\nCalculating consistency...")
if MIN_REVENUE_PER_YEAR > 0:
    print(f"  • Per-year minimum ENABLED: ${MIN_REVENUE_PER_YEAR:,}")
    print(f"  • Years with revenue >= ${MIN_REVENUE_PER_YEAR:,} count as active")
    for year in EVALUATION_YEARS:
        df[f'active_{year}'] = df[f'revenue_{year}'] >= MIN_REVENUE_PER_YEAR
else:
    print(f"  • Per-year minimum DISABLED")
    print(f"  • Any positive revenue counts as active")
    for year in EVALUATION_YEARS:
        df[f'active_{year}'] = df[f'revenue_{year}'] > 0

# Count years active
active_cols = [f'active_{year}' for year in EVALUATION_YEARS]
df['years_active'] = df[active_cols].sum(axis=1)

# Calculate consistency rate
df['consistency_rate'] = df['years_active'] / NUM_EVALUATION_YEARS

print(f"✓ Consistency calculated")
print(f"  • Distribution of years active:")
for i in range(NUM_EVALUATION_YEARS + 1):
    count = (df['years_active'] == i).sum()
    pct = count / len(df) * 100
    print(f"    {i}/{NUM_EVALUATION_YEARS} years: {count:>6,} customers ({pct:>5.1f}%)")

# Calculate 5-year revenue
revenue_cols = [f'revenue_{year}' for year in EVALUATION_YEARS]
df['revenue_5yr'] = df[revenue_cols].sum(axis=1)
print(f"\n✓ 5-Year Revenue calculated")
print(f"  • Total revenue: ${df['revenue_5yr'].sum():,.2f}")
print(f"  • Average per customer: ${df['revenue_5yr'].mean():,.2f}")
print(f"  • Median per customer: ${df['revenue_5yr'].median():,.2f}")

# ============================================================================
# LOYALTY STATUS DETERMINATION
# ============================================================================

print("\n" + "-"*80)
print("STEP 4: DETERMINING LOYALTY STATUS")
print("-"*80)

# Initialize status column
df['loyalty_status'] = 'Not Qualified'
df['ineligibility_reason'] = None

# Ineligible: Insufficient tenure
ineligible_mask = (df['tenure_years'] < MIN_TENURE) | df['tenure_years'].isna()
df.loc[ineligible_mask, 'loyalty_status'] = 'Ineligible'
df.loc[ineligible_mask, 'ineligibility_reason'] = 'Insufficient Tenure'

# For eligible customers, check consistency and revenue
eligible_mask = ~ineligible_mask

# Loyal: Meets all criteria
loyal_mask = (
    eligible_mask &
    (df['consistency_rate'] >= MIN_CONSISTENCY) &
    (df['revenue_5yr'] >= MIN_REVENUE_5YR)
)
df.loc[loyal_mask, 'loyalty_status'] = 'Loyal'

# Track reasons for not qualifying (for eligible customers who don't qualify)
not_qualified_mask = eligible_mask & ~loyal_mask
fails_consistency = (df['consistency_rate'] < MIN_CONSISTENCY)
fails_revenue = (df['revenue_5yr'] < MIN_REVENUE_5YR)

# Set ineligibility reasons
df.loc[not_qualified_mask & fails_consistency & fails_revenue, 'ineligibility_reason'] = 'Below Consistency & Revenue Thresholds'
df.loc[not_qualified_mask & fails_consistency & ~fails_revenue, 'ineligibility_reason'] = 'Below Consistency Threshold'
df.loc[not_qualified_mask & ~fails_consistency & fails_revenue, 'ineligibility_reason'] = 'Below Revenue Threshold'

# Results summary
print(f"\nLoyalty Status Results:")
print(f"  ✓ Loyal: {loyal_mask.sum():,} customers ({loyal_mask.sum()/len(df)*100:.2f}%)")
print(f"  ✗ Not Qualified: {not_qualified_mask.sum():,} customers ({not_qualified_mask.sum()/len(df)*100:.2f}%)")
print(f"  ⊘ Ineligible: {ineligible_mask.sum():,} customers ({ineligible_mask.sum()/len(df)*100:.2f}%)")

# Economic impact
total_revenue = df['revenue_5yr'].sum()
loyal_revenue = df.loc[loyal_mask, 'revenue_5yr'].sum()
print(f"\nEconomic Impact:")
print(f"  • Total 5-year revenue: ${total_revenue:,.2f}")
print(f"  • Revenue from loyal customers: ${loyal_revenue:,.2f}")
print(f"  • Revenue concentration: {loyal_revenue/total_revenue*100:.1f}%")
print(f"  • Avg revenue (loyal): ${df.loc[loyal_mask, 'revenue_5yr'].mean():,.2f}")
print(f"  • Avg revenue (non-loyal): ${df.loc[~loyal_mask, 'revenue_5yr'].mean():,.2f}")

# ============================================================================
# OUTPUT FILE PREPARATION
# ============================================================================

print("\n" + "-"*80)
print("STEP 5: PREPARING OUTPUT FILE")
print("-"*80)

# Create output DataFrame with required columns
output_df = pd.DataFrame({
    'customer_id': df['Account_ID'],
    'customer_name': df['Name'],
    'sub_segment': df['Sub Segment'].fillna('UNKNOWN'),
    'loyalty_status': df['loyalty_status'],
    'tenure_years': df['tenure_years'].fillna(-1).astype(int),
    'years_active_in_window': df['years_active'].astype(int),
    'consistency_rate': df['consistency_rate'].round(4),
    'revenue_5yr': df['revenue_5yr'].round(2),
})

# Add individual year revenues
for year in EVALUATION_YEARS:
    output_df[f'revenue_{year}'] = df[f'revenue_{year}'].round(2)

# Add metadata
output_df['ineligibility_reason'] = df['ineligibility_reason']
output_df['analysis_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Sort by loyalty status, then by revenue (descending)
status_order = {'Loyal': 0, 'Not Qualified': 1, 'Ineligible': 2}
output_df['status_sort'] = output_df['loyalty_status'].map(status_order)
output_df = output_df.sort_values(['status_sort', 'revenue_5yr'], ascending=[True, False])
output_df = output_df.drop('status_sort', axis=1)

print(f"✓ Output DataFrame prepared with {len(output_df)} rows")

# ============================================================================
# DATA QUALITY VALIDATION
# ============================================================================

print("\n" + "-"*80)
print("STEP 6: QUALITY VALIDATION")
print("-"*80)

validation_passed = True

# Check 1: Record count matches
if len(output_df) != len(df):
    print(f"✗ FAIL: Record count mismatch (input: {len(df)}, output: {len(output_df)})")
    validation_passed = False
else:
    print(f"✓ Record count validated: {len(output_df):,} records")

# Check 2: No null loyalty status
null_status = output_df['loyalty_status'].isna().sum()
if null_status > 0:
    print(f"✗ FAIL: {null_status} records have null loyalty_status")
    validation_passed = False
else:
    print(f"✓ All records have loyalty_status assigned")

# Check 3: Revenue totals match
input_total = df['revenue_5yr'].sum()
output_total = output_df['revenue_5yr'].sum()
if abs(input_total - output_total) > 1:  # Allow for rounding
    print(f"✗ FAIL: Revenue mismatch (input: ${input_total:,.2f}, output: ${output_total:,.2f})")
    validation_passed = False
else:
    print(f"✓ Revenue totals validated: ${output_total:,.2f}")

# Check 4: Loyalty status distribution
status_counts = output_df['loyalty_status'].value_counts()
print(f"\n✓ Loyalty status distribution:")
for status, count in status_counts.items():
    print(f"  • {status}: {count:,}")

if validation_passed:
    print(f"\n✓ All quality checks passed")
else:
    print(f"\n✗ Quality validation failed - review errors above")

# ============================================================================
# SAVE OUTPUT FILE
# ============================================================================

print("\n" + "-"*80)
print("STEP 7: SAVING OUTPUT")
print("-"*80)

# Generate output filename with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_filename = f'loyalty_analysis_{timestamp}.csv'

try:
    output_df.to_csv(output_filename, index=False)
    print(f"✓ Output file saved: {output_filename}")
    print(f"  • Location: {os.path.abspath(output_filename)}")
    print(f"  • Rows: {len(output_df):,}")
    print(f"  • Columns: {len(output_df.columns)}")
except Exception as e:
    print(f"✗ ERROR: Failed to save output file")
    print(f"  • Error: {str(e)}")
    sys.exit(1)

# ============================================================================
# SUMMARY REPORT
# ============================================================================

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)

print(f"\nFramework Summary:")
print(f"  • {loyal_mask.sum():,} loyal customers identified")
print(f"  • Representing ${loyal_revenue:,.2f} ({loyal_revenue/total_revenue*100:.1f}% of total revenue)")
print(f"  • Loyal customers are {df.loc[loyal_mask, 'revenue_5yr'].mean() / df.loc[~loyal_mask, 'revenue_5yr'].mean():.1f}x more valuable on average")

print(f"\nOutput File: {output_filename}")
print(f"Ready for PowerBI import or further analysis.")

print("\n" + "="*80)
print(f"Script completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
