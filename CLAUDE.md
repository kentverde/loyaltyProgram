# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Customer Loyalty Framework that identifies loyal B2B customers based on tenure, consistency, and revenue criteria. Generates timestamped CSV reports for PowerBI integration. Python/pandas project with no build system or test suite.

## Running the Analysis

```bash
python3 loyalty_analysis.py
```

**Prerequisites:** Python 3.7+, pandas (`pip install pandas --break-system-packages`)

**Input:** `customer_annual_revenue.csv` (must be in repo root)
**Output:** `loyalty_analysis_YYYYMMDD_HHMMSS.csv` (timestamped, in repo root)

## Architecture

Two-file Python system with strict separation of config from logic:

- **`loyalty_config.py`** - All business rule thresholds and the evaluation window. This is the only file that needs editing for threshold changes or annual year-window shifts. Contains `LOYALTY_CONFIG` dict and derived constants `EVALUATION_YEARS` and `NUM_EVALUATION_YEARS`.
- **`loyalty_analysis.py`** - Main script that runs as a sequential 7-step pipeline: load CSV → validate columns → clean currency/dates → calculate metrics (tenure, consistency, revenue) → determine loyalty status → quality checks → write output CSV. Imports thresholds from `loyalty_config.py`.

### Loyalty Status Logic

Three categories determined by layered criteria:
- **Loyal**: tenure >= 4yr AND consistency >= 60% (3/5 years) AND 5yr revenue >= $35K
- **Not Qualified**: tenure >= 4yr but fails consistency or revenue
- **Ineligible**: tenure < 4yr

### Annual Maintenance

Each year-end, update three values in `loyalty_config.py`: `evaluation_start_year`, `evaluation_end_year`, `current_year` (rolling 5-year window). Input CSV must include the new year's revenue column (`TY Net Product Revenue YYYY`).

## Key Conventions

- Revenue columns in input use format `TY Net Product Revenue YYYY`; cleaned columns use `revenue_YYYY`
- Currency cleaning handles `$`, commas, accounting-style parentheses for negatives, and blanks
- Missing `First Order Date` is inferred from first year with positive revenue
- Output is sorted: Loyal first (by revenue desc), then Not Qualified, then Ineligible
- `DATA_DICTIONARY.md` documents all 15 output fields with types, ranges, and null behavior
