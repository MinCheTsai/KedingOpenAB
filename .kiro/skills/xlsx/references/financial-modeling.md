# Financial Modeling Standards

This steering file provides detailed guidance for building professional financial models in Excel.

## When to Use This Guide

- Creating financial projections or forecasts
- Building investment analysis models
- Developing budgets and business plans
- Creating valuation models
- Building accounting templates

## Model Structure

### Standard Tab Organization

1. **Cover** — Model name, version, date, author
2. **Inputs** — All assumptions and user inputs
3. **Revenue** — Revenue build-up and projections
4. **Costs** — Operating expenses and COGS
5. **P&L** — Income statement
6. **Balance Sheet** — Assets, liabilities, equity
7. **Cash Flow** — Cash flow statement
8. **Valuation** — DCF, multiples, or other valuation
9. **Sensitivity** — Scenario analysis
10. **Charts** — Visualizations and dashboards

### Color Coding (Industry Standard)

| Color | Usage | Example |
|-------|-------|---------|
| **Blue text** | Hardcoded inputs that users can change | Revenue growth rate |
| **Black text** | Formulas and calculations | Calculated revenue |
| **Green text** | Links to other worksheets | Reference to Inputs tab |
| **Red text** | Links to external files | Data from another model |
| **Yellow fill** | Key assumptions to review | Critical growth assumptions |

### Number Formatting Standards

```
Currency:        $#,##0 or $#,##0.00
Large Currency:  $#,##0,, "M" (millions)
Percentage:      0.0% or 0.00%
Multiples:       0.0x
Years:           Text format "2024"
Zero values:     "-" (custom format: 0;(0);"-")
Negatives:       (1,234) using accounting format
```

## Formula Best Practices

### Cell Reference Rules

**Never hardcode values in formulas**:
```excel
# WRONG
=B5*0.10

# CORRECT
=B5*$C$2  # Where C2 contains the 10% rate
```

### Documentation Requirements

Every key assumption must cite its source:
- "Company 10-K, FY2024, Page 45"
- "Bloomberg Terminal, Retrieved 8/15/2025"
- "Management guidance, Q3 earnings call"
- "Industry average per IBISWorld report"

### Error Prevention

```excel
# Protect against division by zero
=IFERROR(Revenue/Units, 0)

# Handle missing data
=IF(ISBLANK(A1), 0, A1)

# Validate inputs
=IF(AND(GrowthRate>=0, GrowthRate<=1), Calculation, "Check Input")
```

## Financial Statement Formulas

### Income Statement

```excel
# Revenue
=Units * Price_Per_Unit

# Gross Profit
=Revenue - COGS

# Gross Margin
=Gross_Profit / Revenue

# Operating Income (EBIT)
=Gross_Profit - OpEx

# Net Income
=EBIT - Interest - Taxes
```

### Balance Sheet

```excel
# Total Assets
=Current_Assets + Fixed_Assets + Other_Assets

# Total Liabilities
=Current_Liabilities + LongTerm_Debt

# Shareholders Equity
=Total_Assets - Total_Liabilities

# Balance Check (must equal zero)
=Total_Assets - Total_Liabilities - Shareholders_Equity
```

### Cash Flow Statement

```excel
# Operating Cash Flow
=Net_Income + Depreciation - Change_in_Working_Capital

# Free Cash Flow
=Operating_CF - CapEx

# Ending Cash
=Beginning_Cash + Operating_CF + Investing_CF + Financing_CF
```

## Projection Methods

### Revenue Projection

```excel
# Growth rate method
=Prior_Year_Revenue * (1 + Growth_Rate)

# Driver-based
=Units * Price * (1 + Price_Increase)

# Cohort analysis
=Existing_Customers * Retention + New_Customers
```

### Expense Projection

```excel
# As percentage of revenue
=Revenue * Expense_Percent

# Fixed + Variable
=Fixed_Cost + (Variable_Rate * Revenue)

# Step function
=IF(Revenue > Threshold, Higher_Cost, Lower_Cost)
```

## Valuation Models

### DCF Framework

```excel
# Discount Factor
=1 / (1 + WACC) ^ Period

# Present Value
=FCF * Discount_Factor

# Terminal Value (Gordon Growth)
=FCF_Terminal * (1 + Terminal_Growth) / (WACC - Terminal_Growth)

# Enterprise Value
=SUM(PV_of_FCFs) + PV_of_Terminal_Value

# Equity Value
=Enterprise_Value - Net_Debt
```

### Sensitivity Tables

Use Data Tables for 2-variable sensitivity:
1. Set up row and column inputs
2. Reference output cell in corner
3. Select entire table
4. Data → What-If Analysis → Data Table

## Quality Checklist

Before delivering any financial model:

- [ ] **Formula integrity**: Zero errors (#REF!, #DIV/0!, etc.)
- [ ] **Balance sheet balances**: Assets = Liabilities + Equity
- [ ] **Cash reconciles**: Ending cash ties to balance sheet
- [ ] **Circular references**: None, or intentionally controlled
- [ ] **Color coding**: Consistent throughout
- [ ] **Documentation**: All assumptions sourced
- [ ] **Print setup**: Appropriate for each sheet
- [ ] **Protection**: Input cells unlocked, formulas locked
- [ ] **Version control**: Clear versioning in filename/cover

## Common Pitfalls

1. **Hardcoding values** in formulas instead of referencing input cells
2. **Inconsistent time periods** (mixing monthly/quarterly/annual)
3. **Circular references** without iterative calculation enabled
4. **Missing error handling** for edge cases
5. **Poor labeling** making the model hard to audit
6. **Overcomplicating** with unnecessary complexity
