# Customer Loyalty Framework Analysis

## Overview

This toolkit identifies loyal customers based on tenure, consistency, and revenue criteria. It generates quarterly reports for PowerBI integration and loyalty program management.

**Framework Version:** 1.0  
**Created:** November 9, 2025
**Last Updated:** November 9, 2025

---

## Quick Start

### Prerequisites

1. **Python 3.7 or higher** installed
2. **pandas library** installed
   ```bash
   pip install pandas --break-system-packages
   ```

### Running the Analysis

1. **Prepare your input file:**
   - File name: `customer_annual_revenue.csv`
   - Place in same directory as `loyalty_analysis.py`

2. **Run the script:**
   ```bash
   python3 loyalty_analysis.py
   ```

3. **Output file created:**
   - Format: `loyalty_analysis_YYYYMMDD_HHMMSS.csv`
   - Location: Same directory as script
   - Ready for PowerBI import

**That's it!** The script handles all data cleaning, calculations, and validation automatically.

---

## File Structure

```
loyalty-framework/
├── loyalty_analysis.py          # Main analysis script
├── loyalty_config.py             # Configuration file (thresholds)
├── customer_annual_revenue.csv   # Input data (you provide)
├── loyalty_analysis_*.csv        # Output files (timestamped)
├── README.md                     # This file
└── DATA_DICTIONARY.md            # Output field definitions
```

---

## Input File Requirements

### File Name
`customer_annual_revenue.csv`

### Required Columns

| Column Name | Type | Description | Example |
|-------------|------|-------------|---------|
| `Account_ID` | Integer | Unique customer identifier | 1006014 |
| `Name` | String | Customer business name | "Smith Design Studio" |
| `Sub Segment` | String | Business classification | "DESIGN_FIRM" |
| `First Order Date` | Date | Date of first order | "2018-05-10 00:00:00" |
| `TY Net Product Revenue 2020` | Currency | Total 2020 revenue | "$8,648.00" or 8648.0 |
| `TY Net Product Revenue 2021` | Currency | Total 2021 revenue | "$17,445.00" or 17445.0 |
| `TY Net Product Revenue 2022` | Currency | Total 2022 revenue | "$6,651.00" or 6651.0 |
| `TY Net Product Revenue 2023` | Currency | Total 2023 revenue | "$11,842.00" or 11842.0 |
| `TY Net Product Revenue 2024` | Currency | Total 2024 revenue | "$12,289.00" or 12289.0 |

### Data Format Notes

✅ **Supported formats:**
- Currency with symbols: `$1,234.56`
- Currency with parentheses (negative): `($500.00)`
- Plain numbers: `1234.56` or `-500.00`
- Blank cells (treated as $0)

✅ **The script automatically handles:**
- Dollar signs, commas, spaces
- Negative values (returns/credits)
- Blank/missing dates (infers from revenue)
- Various date formats

---

## Adjusting Thresholds

All loyalty criteria are defined in `loyalty_config.py`. **No code changes needed** to adjust thresholds.

### Current Thresholds (v1.0)

```python
"min_tenure_years": 4           # Customer since 2020 or earlier
"min_consistency_rate": 0.60    # 3 out of 5 years (allows 2 weak years)
"min_revenue_5yr": 35000        # $35,000 total (2020-2024)
"min_revenue_per_active_year": 0  # DISABLED (set to > 0 to enable)
```

### How to Change Thresholds

**Example 1: Increase revenue requirement to $40K**
```python
# In loyalty_config.py, change:
"min_revenue_5yr": 40000,  # Was 35000
```

**Example 2: Require 4 of 5 years (stricter consistency)**
```python
# In loyalty_config.py, change:
"min_consistency_rate": 0.80,  # Was 0.60 (80% = 4 of 5 years)
```

**Example 3: Enable per-year minimum ($5K/year)**
```python
# In loyalty_config.py, change:
"min_revenue_per_active_year": 5000,  # Was 0
```

**After changing thresholds:**
1. Save `loyalty_config.py`
2. Re-run `python3 loyalty_analysis.py`
3. Review new results

---

## Annual Updates (Year-End Process)

At the end of each year, update the evaluation window to shift forward:

### 1. Update Configuration File

**In `loyalty_config.py`, change:**
```python
# For 2025 year-end analysis:
"evaluation_start_year": 2021,  # Was 2020
"evaluation_end_year": 2025,    # Was 2024
"current_year": 2025,           # Was 2024
```

### 2. Update Input Data File

**Export new `customer_annual_revenue.csv` with:**
- New column: `TY Net Product Revenue 2025`
- Keep all previous years (2020-2024)

### 3. Run Analysis

```bash
python3 loyalty_analysis.py
```

That's it! The script automatically uses the new 5-year window (2021-2025).

---

## Output File

### File Naming
`loyalty_analysis_YYYYMMDD_HHMMSS.csv`

Examples:
- `loyalty_analysis_20241109_143022.csv`
- `loyalty_analysis_20250331_091534.csv`

### Contents
One row per customer with loyalty status and supporting metrics.

**See `DATA_DICTIONARY.md` for detailed field definitions.**

### Key Columns
- `loyalty_status`: "Loyal", "Not Qualified", or "Ineligible"
- `tenure_years`: Years as customer
- `consistency_rate`: % of years with purchases (0.0 to 1.0)
- `revenue_5yr`: Total revenue across evaluation window
- `revenue_2020` through `revenue_2024`: Year-by-year breakdown

---

## Troubleshooting

### Error: "Input file not found"
**Problem:** `customer_annual_revenue.csv` not in same directory as script

**Solution:**
```bash
# Make sure files are together:
ls -la
# Should show:
#   loyalty_analysis.py
#   loyalty_config.py
#   customer_annual_revenue.csv
```

### Error: "Missing required columns"
**Problem:** Input file column names don't match expected format

**Solution:** Check column names exactly match:
- `Account_ID` (not `AccountID` or `Account ID`)
- `TY Net Product Revenue 2020` (exact spacing and year)
- Run script to see which columns are missing

### Error: "pandas not found"
**Problem:** pandas library not installed

**Solution:**
```bash
pip install pandas --break-system-packages
```

### Warning: "Duplicate Account_IDs"
**Problem:** Input file has duplicate customer records

**Action:** Script automatically keeps first occurrence. Review input data for duplicates.

### Output has unexpected counts
**Problem:** Thresholds may need adjustment

**Action:**
1. Check `loyalty_config.py` values
2. Review Phase 1 analysis report for threshold recommendations
3. Adjust thresholds and re-run

---

## Data Quality Checks

The script automatically validates:

✅ Input file exists and is readable  
✅ All required columns present  
✅ No duplicate Account_IDs  
✅ Record count matches (input = output)  
✅ Revenue totals match (no data loss)  
✅ All customers have loyalty_status assigned  
✅ Negative values handled correctly

**If any check fails, the script will print an error message and stop.**

---

## Understanding the Output

### Loyalty Status Categories

**Loyal**
- ✅ Tenure ≥ 4 years
- ✅ Consistency ≥ 60% (3 of 5 years)
- ✅ Revenue ≥ $35,000
- **Action:** Protect these customers' pricing tiers

**Not Qualified**
- ✅ Tenure ≥ 4 years (eligible)
- ❌ Fails consistency OR revenue threshold
- **Action:** Standard tier rules apply

**Ineligible**
- ❌ Tenure < 4 years
- **Action:** Too new to evaluate; may qualify in future

### Example Interpretation

```csv
customer_id,customer_name,loyalty_status,tenure_years,consistency_rate,revenue_5yr
1001234,ABC Design,Loyal,5,0.80,125000.00
```

**Translation:**
- Customer for 5 years
- Purchased in 4 of last 5 years (80% = allows 1 weak year)
- $125K total revenue
- **Qualifies for loyalty protection**

---

## Integration with PowerBI

### Import Steps

1. Open PowerBI Desktop
2. **Get Data** → **Text/CSV**
3. Select `loyalty_analysis_*.csv`
4. Click **Load**

### Key Metrics to Visualize

**Coverage:**
- Count of "Loyal" customers
- % of total customer base

**Economic Impact:**
- Sum of `revenue_5yr` for "Loyal" status
- % of total revenue from loyal customers

**Distribution:**
- Loyalty status by `sub_segment`
- Average `revenue_5yr` by status

**Trends (over time with multiple runs):**
- Loyalty status changes quarter-over-quarter
- Use `analysis_timestamp` to track

---

## Support & Maintenance

### Quarterly Execution

**Schedule:** End of Q1, Q2, Q3, Q4
1. Export latest `customer_annual_revenue.csv` from PowerBI
2. Run `python3 loyalty_analysis.py`
3. Import output to PowerBI
4. Review loyalty status changes

### Annual Updates

**Schedule:** Year-end (December/January)
1. Add new revenue year column to input file
2. Update `loyalty_config.py` evaluation window
3. Run analysis with new 5-year window
4. Document threshold changes in version history

### Threshold Adjustments

**When to consider:**
- Loyalty rate too high/low (target: 10-20%)
- Business strategy changes
- Market conditions shift
- Customer feedback

**Process:**
1. Test new thresholds with sensitivity analysis
2. Review impact on coverage and revenue concentration
3. Get stakeholder approval (Rico, Asha)
4. Update `loyalty_config.py`
5. Document in version history

---

## Version History

### v1.0 - November 9, 2024
- Initial framework release
- Thresholds: 4yr tenure, 60% consistency, $35K revenue
- Coverage: 9.9% of customers, 61.7% revenue concentration
- Based on Phase 1 exploratory analysis
- Approved by: Kent, Rico, Asha

---

## Contact

**Project Owner:** Kent Schneider  
**Stakeholders:** Rico (VP Sales), Asha (CEO)

For questions about:
- **Thresholds:** Review Phase 1 analysis report
- **Technical issues:** Check Troubleshooting section
- **Business logic:** See `loyalty_config.py` comments

---

**Last Updated:** November 9, 2024  
**Framework Version:** 1.0
