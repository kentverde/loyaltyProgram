"""
CUSTOMER LOYALTY FRAMEWORK - CONFIGURATION FILE

This file contains all business rules and thresholds for identifying loyal customers.
Update these values to adjust the loyalty criteria without modifying the main script.

Last Updated: November 9, 2024
Framework Version: 1.0
Approved by: Kent, Rico, Asha
"""

LOYALTY_CONFIG = {
    # ========================================
    # TENURE THRESHOLD
    # ========================================
    "min_tenure_years": 4,
    # Business rationale: 
    #   - Aligns with 5-year evaluation window (2020-2024)
    #   - Captures customers from 2020 cohort when reliable data began
    #   - 4 years demonstrates meaningful loyalty while being realistic given data availability
    #   - Original proposal was 5 years, but only 7.8% of customers had 5+ years tenure
    # 
    # Impact: ~43.7% of customers (6,842) have 4+ years tenure
    # Last updated: November 2024
    
    # ========================================
    # EVALUATION WINDOW
    # ========================================
    "evaluation_start_year": 2020,
    "evaluation_end_year": 2024,
    # Business rationale:
    #   - 5-year window is B2B industry best practice
    #   - Long enough to see patterns and weather "one bad year"
    #   - Recent enough to reflect current relationship health
    #   - Aligns with year-end tier adjustment process
    #
    # ANNUAL UPDATE REQUIRED:
    #   - At end of 2025, change to: start=2021, end=2025
    #   - At end of 2026, change to: start=2022, end=2026
    #   - Always maintain 5-year rolling window
    #
    # Last updated: November 2024
    
    # ========================================
    # CONSISTENCY THRESHOLD
    # ========================================
    "min_consistency_rate": 0.60,
    # Business rationale:
    #   - 60% = 3 out of 5 years with purchases
    #   - Allows up to 2 weak years (including $0 years)
    #   - Protects loyal customers through temporary disruptions
    #   - Addresses customer feedback about "one bad year" penalty
    #
    # Format: Decimal (0.60 = 60%, 0.80 = 80%)
    # 
    # Alternative thresholds to consider:
    #   - 0.80 (4 of 5 years) = stricter, allows only 1 weak year
    #   - 0.40 (2 of 5 years) = more lenient, allows 3 weak years
    #
    # Current: 84% of 4+ year customers meet this threshold
    # Last updated: November 2024
    
    # ========================================
    # REVENUE THRESHOLD (Total 5-Year)
    # ========================================
    "min_revenue_5yr": 35000,
    # Business rationale:
    #   - $35K over 5 years = ~$7K/year average
    #   - Below Gold tier threshold ($15K/year) but still meaningful
    #   - Filters out low-impact sporadic customers
    #   - Approximately 92nd percentile of all customers
    #
    # Value in dollars (no commas, no decimal point for whole numbers)
    #
    # Alternative thresholds tested:
    #   - $50K = only 7.1% qualify (too strict)
    #   - $40K = 8.9% qualify (reasonable)
    #   - $30K = 11.5% qualify (too loose)
    #
    # Current: With $35K, 9.9% qualify representing 61.7% of revenue
    # Last updated: November 2024
    
    # ========================================
    # REVENUE THRESHOLD (Per Active Year) - OPTIONAL
    # ========================================
    "min_revenue_per_active_year": 0,
    # Business rationale:
    #   - Currently DISABLED (set to 0)
    #   - If enabled: Each year must meet minimum to count as "active"
    #   - Prevents edge cases where customers have many years of tiny purchases
    #
    # How it works when enabled (example: 5000):
    #   - Year with $6,000 revenue ✓ counts as active
    #   - Year with $3,000 revenue ✗ doesn't count as active
    #   - Year with $0 revenue ✗ doesn't count as active
    #
    # Use case for enabling:
    #   - If you find customers gaming system with many low-value years
    #   - Adds quality filter on top of total revenue threshold
    #
    # Recommended starting value if enabled: 5000 (below Insider tier)
    # Current status: DISABLED
    # Last updated: November 2024
    
    # ========================================
    # ANALYSIS METADATA
    # ========================================
    "current_year": 2024,
    # Business rationale:
    #   - Used for tenure calculation (current_year - first_order_year)
    #   - Update annually when running year-end analysis
    #
    # Last updated: November 2024
}

# ========================================
# DERIVED CONSTANTS (Don't modify these)
# ========================================
EVALUATION_YEARS = list(range(
    LOYALTY_CONFIG["evaluation_start_year"], 
    LOYALTY_CONFIG["evaluation_end_year"] + 1
))
# Creates list: [2020, 2021, 2022, 2023, 2024]

NUM_EVALUATION_YEARS = len(EVALUATION_YEARS)
# Number of years in evaluation window: 5

# ========================================
# VERSION HISTORY
# ========================================
"""
v1.0 - November 9, 2024
- Initial framework with data-driven thresholds
- Tenure: 4 years (adjusted from 5 due to data availability)
- Consistency: 60% (allows 2 weak years)
- Revenue: $35,000 (achieves 9.9% coverage, 61.7% revenue concentration)
- Per-year minimum: Disabled (available for future use)
"""
