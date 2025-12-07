from . import mcp


@mcp.prompt()
def xlsx_workflow() -> str:
    """Provides guidance on working with Excel spreadsheets."""
    return """# Working with Excel Spreadsheets (.xlsx)

## Quick Reference

### Reading Data
- `read_excel` - Read Excel file as markdown table
- `get_sheet_names` - List all sheets in a file

### Creating/Editing
- `create_excel` - Create new Excel file from CSV data
- `write_cell` - Write value or formula to specific cell
- `add_sheet` - Add new sheet to existing file

### Formulas
- `recalculate` - Recalculate all formulas and check for errors

### Converting
- `convert_to_csv` - Convert Excel sheet to CSV

## Typical Workflows

### 1. Read Excel Data
```
read_excel(file_path="data.xlsx", sheet_name="Sheet1")
```

### 2. Create New Excel with Formulas
```
# Create file
create_excel(file_path="report.xlsx", data="Name,Value\\nItem1,100\\nItem2,200", sheet_name="Data")

# Add formula
write_cell(file_path="report.xlsx", sheet_name="Data", cell="C1", value="Total")
write_cell(file_path="report.xlsx", sheet_name="Data", cell="C2", value="=SUM(B2:B3)")

# Recalculate
recalculate(file_path="report.xlsx")
```

### 3. Check Formulas for Errors
```
recalculate(file_path="model.xlsx", timeout=30)
```

## Notes
- Requires LibreOffice for formula recalculation
- Always use Excel formulas instead of hardcoding calculated values
- Use recalculate after writing formulas to compute values
"""
