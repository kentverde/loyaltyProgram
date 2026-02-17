"""
LOYALTY ANALYSIS - EXECUTIVE SUMMARY REPORT

Purpose: Generate high-level summary statistics from a loyalty analysis output CSV.
         Produces counts, revenue breakdowns, top accounts, segment analysis,
         and disqualification reasons suitable for executive reporting.

Usage:
    python loyalty_summary_report.py

Requirements:
    - Python 3.7+
    - pandas library
    - A loyalty analysis output file (loyalty_analysis_*.csv) in the same directory.
      Uses the most recent file by timestamp if multiple exist.

Output:
    - Console summary of loyalty program results
"""

import pandas as pd
import glob
import sys
import os

# ============================================================================
# FIND MOST RECENT ANALYSIS FILE
# ============================================================================

analysis_files = sorted(glob.glob("loyalty_analysis_*.csv"))
if not analysis_files:
    print("ERROR: No loyalty_analysis_*.csv files found in current directory.")
    print("Run loyalty_analysis.py first to generate the analysis output.")
    sys.exit(1)

input_file = analysis_files[-1]  # Most recent by filename timestamp
print(f"Reading: {input_file}")
print()

df = pd.read_csv(input_file)
total_customers = len(df)
total_revenue = df["revenue_5yr"].sum()

# ============================================================================
# STATUS BREAKDOWN
# ============================================================================

print("=" * 70)
print("LOYALTY ANALYSIS — EXECUTIVE SUMMARY")
print("=" * 70)
print(f"Source File: {input_file}")
print(f"Total Customers Evaluated: {total_customers:,}")
print(f"Total 5-Year Revenue: ${total_revenue:,.0f}")
print()

print("-" * 70)
print("STATUS BREAKDOWN")
print("-" * 70)
print(f"{'Status':<20} {'Count':>8} {'% Base':>8} {'5yr Revenue':>16} {'% Revenue':>10} {'Avg Revenue':>14}")
print("-" * 70)

for status in ["Loyal", "Not Qualified", "Ineligible"]:
    subset = df[df["loyalty_status"] == status]
    count = len(subset)
    pct = count / total_customers * 100
    rev = subset["revenue_5yr"].sum()
    rev_pct = rev / total_revenue * 100
    avg_rev = subset["revenue_5yr"].mean()
    print(f"{status:<20} {count:>8,} {pct:>7.1f}% ${rev:>14,.0f} {rev_pct:>9.1f}% ${avg_rev:>12,.0f}")

# ============================================================================
# LOYAL CUSTOMER DETAILS
# ============================================================================

loyal = df[df["loyalty_status"] == "Loyal"]

print()
print("-" * 70)
print("LOYAL CUSTOMER PROFILE")
print("-" * 70)
print(f"  Count:            {len(loyal):,}")
print(f"  Total 5yr Revenue: ${loyal['revenue_5yr'].sum():,.0f}")
print(f"  Average Revenue:   ${loyal['revenue_5yr'].mean():,.0f}")
print(f"  Median Revenue:    ${loyal['revenue_5yr'].median():,.0f}")

# ============================================================================
# TOP LOYAL ACCOUNTS
# ============================================================================

print()
print("-" * 70)
print("TOP 10 LOYAL ACCOUNTS (by 5-year revenue)")
print("-" * 70)

top10 = loyal.nlargest(10, "revenue_5yr")
for i, (_, r) in enumerate(top10.iterrows(), 1):
    print(f"  {i:>2}. {r['customer_name']:40s} {r['sub_segment']:20s} "
          f"Tenure: {r['tenure_years']}yr  Active: {int(r['years_active_in_window'])}/5yr  "
          f"Rev: ${r['revenue_5yr']:,.0f}")

# ============================================================================
# SAMPLE MID-RANGE LOYAL ACCOUNTS
# ============================================================================

print()
print("-" * 70)
print("SAMPLE MID-RANGE LOYAL ACCOUNTS (near median revenue)")
print("-" * 70)

median_rev = loyal["revenue_5yr"].median()
mid = loyal.iloc[(loyal["revenue_5yr"] - median_rev).abs().argsort()[:5]]
for _, r in mid.iterrows():
    print(f"  {r['customer_name']:40s} {r['sub_segment']:20s} "
          f"Tenure: {r['tenure_years']}yr  Active: {int(r['years_active_in_window'])}/5yr  "
          f"Rev: ${r['revenue_5yr']:,.0f}")

# ============================================================================
# NOT QUALIFIED REASONS
# ============================================================================

print()
print("-" * 70)
print("WHY CUSTOMERS DON'T QUALIFY")
print("-" * 70)

nq = df[df["loyalty_status"] == "Not Qualified"]
reasons = nq["ineligibility_reason"].value_counts()
for reason, count in reasons.items():
    pct = count / len(nq) * 100
    print(f"  {reason:50s} {count:>6,} ({pct:.1f}%)")

# ============================================================================
# SEGMENT BREAKDOWN (LOYAL)
# ============================================================================

print()
print("-" * 70)
print("LOYAL CUSTOMERS BY SEGMENT")
print("-" * 70)
print(f"{'Segment':<30} {'Count':>6} {'Total Revenue':>16} {'Avg Revenue':>14}")
print("-" * 70)

seg = (loyal.groupby("sub_segment")
       .agg(count=("customer_id", "count"),
            total_rev=("revenue_5yr", "sum"),
            avg_rev=("revenue_5yr", "mean"))
       .sort_values("total_rev", ascending=False))

for s, r in seg.iterrows():
    print(f"  {s:<28} {r['count']:>6,.0f} ${r['total_rev']:>14,.0f} ${r['avg_rev']:>12,.0f}")

print()
print("=" * 70)
print("END OF REPORT")
print("=" * 70)
