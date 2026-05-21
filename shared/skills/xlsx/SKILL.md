---
name: xlsx
description: Create and edit Excel spreadsheets (.xlsx) with formulas, formatting, charts, and financial modeling best practices. Use when asked to generate Excel files, build budgets, create data analysis workbooks, or produce financial models.
---

# Excel Spreadsheet Creator

> Adapted from [Anthropic's Claude Skills](https://github.com/anthropics/skills) under Apache 2.0 license. Original skill: `xlsx`

## Onboarding

This skill provides guidance for creating Excel spreadsheets. Install dependencies as needed:

```bash
# Python (recommended for most tasks)
pip install openpyxl pandas xlsxwriter

# For data analysis
pip install numpy
```

## When to Load Reference Files

Load `references/financial-modeling.md` when the user needs to:
- Build financial models or projections
- Create investment analysis spreadsheets
- Work with accounting or budgeting templates
- Implement financial best practices

## Instructions

### Critical Requirement: Formula Integrity

**Every Excel model MUST be delivered with ZERO formula errors.**

Check for and eliminate:
- `#REF!` — Invalid cell references
- `#DIV/0!` — Division by zero
- `#VALUE!` — Wrong value type
- `#N/A` — Value not available
- `#NAME?` — Unrecognized formula name

### Core Principle: Use Formulas, Not Hardcoded Values

**Critical**: Always use Excel formulas instead of calculating values in Python and hardcoding them.

```python
# WRONG - Hardcoded calculation
ws['C1'] = 150  # Sum calculated in Python

# CORRECT - Excel formula
ws['C1'] = '=A1+B1'  # Excel calculates this
```

### Creating Spreadsheets with Python

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, PatternFill
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active
ws.title = "Data"

# Add headers
headers = ['Date', 'Description', 'Amount', 'Category']
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal='center')

# Add data with formulas
ws['A2'] = '2024-01-15'
ws['B2'] = 'Sales Revenue'
ws['C2'] = 10000
ws['D2'] = 'Income'

# Add a sum formula
ws['C10'] = '=SUM(C2:C9)'

wb.save('output.xlsx')
```

### Template Preservation

When modifying existing files, **maintain established formatting patterns** rather than imposing standardized styles. Respect the original design intent.

### Formatting Standards

#### Number Formatting

| Type | Format | Example |
|------|--------|---------|
| Currency | `$#,##0` | $1,234 |
| Percentage | `0.0%` | 12.5% |
| Years | Text string | "2024" |
| Zero values | Display as "-" | - |
| Negative numbers | Parentheses | (1,234) |

#### Color Coding Convention (Financial Models)

| Color | Meaning |
|-------|---------|
| **Blue text** | User-changeable inputs |
| **Black text** | Calculations and formulas |
| **Green text** | Internal worksheet links |
| **Red text** | External file references |
| **Yellow background** | Key assumptions requiring updates |

### Formula Best Practices

1. **Separate assumptions**: All assumptions in dedicated cells
2. **Reference cells**: Formulas reference cells, never hardcode values
3. **Document sources**: Cite data sources (e.g., "Company 10-K, FY2024, Page 45")
4. **Named ranges**: Use named ranges for key inputs
5. **Error handling**: Use IFERROR() for graceful error handling

### Common Formulas

```excel
=SUM(A1:A10)
=SUMIF(A:A, "Category", B:B)
=VLOOKUP(A1, Sheet2!A:B, 2, FALSE)
=INDEX(B:B, MATCH(A1, A:A, 0))
=EOMONTH(A1, 0)
=NETWORKDAYS(A1, B1)
=NPV(rate, values)
=IRR(values)
=PMT(rate, nper, pv)
=IFERROR(A1/B1, 0)
```

### Chart Creation

```python
from openpyxl.chart import BarChart, Reference

chart = BarChart()
chart.title = "Monthly Revenue"
chart.y_axis.title = "Amount ($)"
chart.x_axis.title = "Month"

data = Reference(ws, min_col=2, min_row=1, max_col=2, max_row=13)
categories = Reference(ws, min_col=1, min_row=2, max_row=13)

chart.add_data(data, titles_from_data=True)
chart.set_categories(categories)
ws.add_chart(chart, "E2")
```

### Data Validation

```python
from openpyxl.worksheet.datavalidation import DataValidation

dv = DataValidation(
    type="list",
    formula1='"Option1,Option2,Option3"',
    allow_blank=True
)
dv.add('A1:A100')
ws.add_data_validation(dv)
```

### Workbook Organization

**Sheet naming conventions**:
- `Inputs` — User-editable assumptions
- `Calculations` — Working calculations
- `Summary` — Key outputs and dashboards
- `Data` — Raw data imports
- `Charts` — Visualizations

### Validation Checklist

Before delivering any spreadsheet:

- [ ] All formulas calculate correctly
- [ ] No error values (#REF!, #DIV/0!, etc.)
- [ ] Inputs clearly identified
- [ ] Formatting is consistent
- [ ] Column widths accommodate content
- [ ] Headers freeze for scrolling

### Programmatic Validation

```python
from openpyxl import load_workbook

def validate_xlsx(filepath):
    """Check spreadsheet for common issues."""
    errors = []
    wb = load_workbook(filepath, data_only=False)
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        for row in ws.iter_rows():
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    if cell.value.startswith('#'):
                        errors.append(f"{sheet_name}!{cell.coordinate}: {cell.value}")
                    if cell.value.startswith('=') and '#REF!' in cell.value:
                        errors.append(f"{sheet_name}!{cell.coordinate}: Broken reference")
    wb.close()
    return errors
```

### Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `#REF!` error | Deleted cell reference | Check formula references exist |
| `#DIV/0!` error | Division by zero | Add `IFERROR()` wrapper |
| `#VALUE!` error | Wrong data type | Ensure cells contain expected types |
| Formulas show as text | Cell formatted as text | Format cell as General |
| Numbers stored as text | Import/paste issue | Use VALUE() |
| Styles not applied | Style object reused | Create new style objects per cell |

### Recommended Dependencies

```bash
openpyxl>=3.1.0
pandas>=2.0.0
xlsxwriter>=3.1.0
numpy>=1.24.0
```
