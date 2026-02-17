# Data Dictionary - Loyalty Analysis Output

## Overview

This document defines all fields in the loyalty analysis output file (`loyalty_analysis_YYYYMMDD_HHMMSS.csv`).

**Output Structure:** One row per customer  
**Sort Order:** Loyal customers first, then Not Qualified, then Ineligible (within each status, sorted by revenue descending)

---

## Field Definitions

### Core Identification Fields

#### `customer_id`
- **Type:** Integer
- **Description:** Unique customer identifier from source system
- **Source:** `Account_ID` from input file
- **Example:** `1006014`
- **Notes:** Primary key; used for joining with other systems
- **Null Values:** Never null

#### `customer_name`
- **Type:** String
- **Description:** Customer business name
- **Source:** `Name` from input file
- **Example:** `"Smith Design Studio"`, `"ABC Design Firm"`
- **Notes:** May contain special characters, punctuation
- **Null Values:** Never null (populated from source)

#### `sub_segment`
- **Type:** String (Categorical)
- **Description:** Business classification category
- **Source:** `Sub Segment` from input file
- **Possible Values:**
  - `DESIGN_FIRM`
  - `DESIGNER_INDEPENDENT`
  - `SINGLE_LOCATION`
  - `MULTIPLE_LOCATIONS`
  - `ARCHITECT_BUILDER`
  - `SPECIALTY`
  - `HOSPITALITY`
  - `MASS`
  - `SALES_REP`
  - `EMPLOYEEFRIENDFAMILY`
  - `DESIGNER_NO_SHOWROOM`
  - `DESIGNER_SHOWROOM`
  - `DESIGN_SHOP`
  - `STORE_FLOORING`
  - `STORE_FURNITURE`
  - `STORE_GIFT`
  - `NICHE`
  - `UNKNOWN` (if source value was blank)
- **Example:** `"DESIGN_FIRM"`
- **Notes:** Use for segment analysis and filtering
- **Null Values:** Replaced with "UNKNOWN" if blank in source

---

### Loyalty Status Fields

#### `loyalty_status`
- **Type:** String (Categorical)
- **Description:** Primary loyalty classification
- **Possible Values:**
  - `"Loyal"` - Meets all loyalty criteria
  - `"Not Qualified"` - Has sufficient tenure but fails other criteria
  - `"Ineligible"` - Insufficient tenure to be evaluated
- **Business Logic:**
  ```
  IF tenure_years >= 4 
     AND consistency_rate >= 0.60 
     AND revenue_5yr >= 35000
  THEN "Loyal"
  
  ELSE IF tenure_years >= 4
  THEN "Not Qualified"
  
  ELSE "Ineligible"
  ```
- **Example:** `"Loyal"`
- **Usage:** Primary filter for identifying customers to protect
- **Null Values:** Never null

#### `ineligibility_reason`
- **Type:** String (Categorical) or Null
- **Description:** Explains why customer didn't qualify (if applicable)
- **Possible Values:**
  - `"Insufficient Tenure"` - Customer too new (<4 years)
  - `"Below Revenue Threshold"` - Fails revenue requirement only
  - `"Below Consistency Threshold"` - Fails consistency requirement only
  - `"Below Consistency & Revenue Thresholds"` - Fails both
  - `null` (blank) - Customer is "Loyal"
- **Example:** `"Below Revenue Threshold"`
- **Usage:** Diagnostic; helps understand why customers don't qualify
- **Null Values:** Null for all "Loyal" customers

---

### Tenure Metrics

#### `tenure_years`
- **Type:** Integer
- **Description:** Number of years customer has been with company
- **Calculation:** `2024 - first_order_year`
- **Range:** -1 to 6 (based on current data)
  - `-1` = Customer first ordered in 2025 (future-dated)
  - `0` = Customer first ordered in 2024 (current year)
  - `4+` = Eligible for loyalty consideration
  - `6` = Maximum in current dataset (first order 2018)
- **Example:** `5` (customer since 2019)
- **Notes:** 
  - Calculated from `First Order Date` in source
  - If `First Order Date` was blank, inferred from first year with revenue
  - Will increase by 1 each year (automatic aging)
- **Null Values:** Never null; set to -1 if cannot determine

---

### Consistency Metrics

#### `years_active_in_window`
- **Type:** Integer
- **Description:** Count of years with purchases in the 5-year evaluation window (2020-2024)
- **Calculation:** Count of years where `revenue_YYYY > 0` (or `>= min_per_year` if enabled)
- **Range:** 0 to 5
  - `0` = No purchases in any year
  - `3` = Meets 60% consistency threshold (minimum for loyalty)
  - `5` = Purchased every year (perfect consistency)
- **Example:** `4` (purchased in 4 of 5 years)
- **Notes:**
  - Years with negative revenue (returns only) count as $0, not active
  - If per-year minimum enabled, only years above threshold count
- **Null Values:** Never null

#### `consistency_rate`
- **Type:** Decimal (Float)
- **Description:** Percentage of years active in evaluation window
- **Calculation:** `years_active_in_window / 5`
- **Range:** 0.0 to 1.0
  - `0.0` = 0% (no purchases)
  - `0.60` = 60% (minimum for loyalty = 3 of 5 years)
  - `0.80` = 80% (4 of 5 years)
  - `1.0` = 100% (purchased every year)
- **Format:** 4 decimal places (e.g., `0.6000`)
- **Example:** `0.8000` (80% consistency)
- **Notes:** 
  - Current threshold: ≥ 0.60 required for loyalty
  - Allows up to 2 "weak" years (including $0 years)
- **Null Values:** Never null

---

### Revenue Metrics

#### `revenue_5yr`
- **Type:** Decimal (Float)
- **Description:** Total net revenue across 5-year evaluation window (2020-2024)
- **Calculation:** Sum of `revenue_2020` + `revenue_2021` + `revenue_2022` + `revenue_2023` + `revenue_2024`
- **Format:** 2 decimal places
- **Range:** Can be negative (if returns exceed sales), typically $0 - $1.6M+
- **Example:** `125,450.75`
- **Notes:**
  - Current threshold: ≥ $35,000 required for loyalty
  - Includes all revenue (positive and negative)
  - Approximately 92nd percentile of all customers
- **Null Values:** Never null (defaults to 0.0 if no data)

#### `revenue_2020`
- **Type:** Decimal (Float)
- **Description:** Total net revenue in calendar year 2020
- **Source:** `TY Net Product Revenue 2020` from input file
- **Format:** 2 decimal places
- **Range:** Can be negative (returns exceed sales)
- **Example:** `15,250.00`, `0.00`, `-500.00`
- **Notes:**
  - Negative values indicate net returns/credits for the year
  - Blank cells in source converted to 0.00
  - Currency symbols, commas removed during processing
- **Null Values:** Never null (defaults to 0.00)

#### `revenue_2021`
- **Type:** Decimal (Float)
- **Description:** Total net revenue in calendar year 2021
- **Source:** `TY Net Product Revenue 2021` from input file
- **Format/Range/Notes:** Same as `revenue_2020`

#### `revenue_2022`
- **Type:** Decimal (Float)
- **Description:** Total net revenue in calendar year 2022
- **Source:** `TY Net Product Revenue 2022` from input file
- **Format/Range/Notes:** Same as `revenue_2020`

#### `revenue_2023`
- **Type:** Decimal (Float)
- **Description:** Total net revenue in calendar year 2023
- **Source:** `TY Net Product Revenue 2023` from input file
- **Format/Range/Notes:** Same as `revenue_2020`

#### `revenue_2024`
- **Type:** Decimal (Float)
- **Description:** Total net revenue in calendar year 2024
- **Source:** `TY Net Product Revenue 2024` from input file
- **Format/Range/Notes:** Same as `revenue_2020`

---

### Metadata Fields

#### `analysis_timestamp`
- **Type:** String (Datetime)
- **Description:** Date and time when this analysis was run
- **Format:** `YYYY-MM-DD HH:MM:SS` (24-hour time)
- **Example:** `"2024-11-09 14:30:22"`
- **Usage:**
  - Track when analysis was performed
  - Enable quarter-over-quarter comparison
  - Audit trail for threshold changes
- **Notes:**
  - All rows in same file have same timestamp
  - Matches timestamp in output filename
- **Null Values:** Never null

---

## Data Types Summary

| Field | Type | Format | Can Be Null? |
|-------|------|--------|--------------|
| `customer_id` | Integer | `1234567` | No |
| `customer_name` | String | `"Text"` | No |
| `sub_segment` | String | `"CATEGORY"` | No (uses "UNKNOWN") |
| `loyalty_status` | String | `"Status"` | No |
| `tenure_years` | Integer | `5` | No |
| `years_active_in_window` | Integer | `4` | No |
| `consistency_rate` | Float | `0.8000` | No |
| `revenue_5yr` | Float | `12345.67` | No |
| `revenue_2020` | Float | `12345.67` | No |
| `revenue_2021` | Float | `12345.67` | No |
| `revenue_2022` | Float | `12345.67` | No |
| `revenue_2023` | Float | `12345.67` | No |
| `revenue_2024` | Float | `12345.67` | No |
| `ineligibility_reason` | String | `"Reason"` | Yes (for Loyal) |
| `analysis_timestamp` | String | `"YYYY-MM-DD HH:MM:SS"` | No |

---

## Field Relationships

### Loyalty Status Logic

```
loyalty_status = 
  IF (tenure_years >= 4 
      AND consistency_rate >= 0.60 
      AND revenue_5yr >= 35000)
  THEN "Loyal"
  
  ELSE IF (tenure_years >= 4)
  THEN "Not Qualified"
  
  ELSE "Ineligible"
```

### Consistency Calculation

```
years_active_in_window = 
  COUNT of years where revenue_YYYY > 0
  (for YYYY in [2020, 2021, 2022, 2023, 2024])

consistency_rate = 
  years_active_in_window / 5
```

### Revenue Aggregation

```
revenue_5yr = 
  revenue_2020 + 
  revenue_2021 + 
  revenue_2022 + 
  revenue_2023 + 
  revenue_2024
```

---

## Common Use Cases

### Find All Loyal Customers
```sql
WHERE loyalty_status = 'Loyal'
```

### Find Customers at Risk (Loyal but No 2024 Revenue)
```sql
WHERE loyalty_status = 'Loyal'
  AND revenue_2024 = 0
```

### Find Customers Close to Qualifying
```sql
WHERE loyalty_status = 'Not Qualified'
  AND tenure_years >= 4
  AND consistency_rate >= 0.60
  AND revenue_5yr >= 30000  -- Within $5K of threshold
```

### Segment Analysis
```sql
SELECT 
  sub_segment,
  COUNT(*) as total_customers,
  SUM(CASE WHEN loyalty_status = 'Loyal' THEN 1 ELSE 0 END) as loyal_count,
  AVG(revenue_5yr) as avg_revenue
GROUP BY sub_segment
ORDER BY loyal_count DESC
```

### Track Status Changes (Between Two Analysis Runs)
```sql
SELECT 
  current.customer_id,
  current.customer_name,
  previous.loyalty_status as old_status,
  current.loyalty_status as new_status
FROM current_analysis as current
JOIN previous_analysis as previous
  ON current.customer_id = previous.customer_id
WHERE current.loyalty_status != previous.loyalty_status
```

---

## Data Quality Notes

### Validated During Processing

✅ All customers have a `loyalty_status` assigned  
✅ No duplicate `customer_id` values  
✅ `revenue_5yr` matches sum of individual years  
✅ `consistency_rate` = `years_active_in_window` / 5  
✅ Record count matches input file  

### Expected Patterns

- Most customers are "Ineligible" (~56% in v1.0 data)
- Loyal customers have higher average revenue
- `years_active_in_window` of 0-2 most common (~62% of customers)
- Negative `revenue_YYYY` values are rare (~0.1% of records)

### Known Edge Cases

**Customers with negative tenure_years:**
- Indicates future-dated `First Order Date` (data quality issue)
- Automatically marked as "Ineligible"

**Customers with negative revenue_5yr:**
- More returns than sales across 5 years
- Automatically fails revenue threshold
- Marked as "Not Qualified" or "Ineligible"

**Customers with blank First Order Date:**
- Date inferred from first year with revenue
- If no revenue in any year, marked "Ineligible" with tenure = -1

---

## Version History

### v1.0 - November 9, 2024
- Initial data structure
- 15 total fields
- Supports evaluation window 2020-2024
- Thresholds: 4yr tenure, 60% consistency, $35K revenue

---

## Notes for Future Updates

### When Adding New Year (e.g., 2025)

**New field to add:**
- `revenue_2025` (Float, 2 decimals)

**Fields to update:**
- `years_active_in_window` - will now count up to 6 years if window shifts
- `consistency_rate` - denominator remains 5 (always 5-year window)
- `revenue_5yr` - will sum new 5-year window (2021-2025)

**Fields unchanged:**
- All identification, status, and metadata fields

### When Changing Thresholds

**No schema changes needed** - thresholds are applied during processing, not stored in output.

**Document in:**
- `loyalty_config.py` version history
- Analysis reports
- Stakeholder communications

---

**Last Updated:** November 9, 2024  
**Framework Version:** 1.0
