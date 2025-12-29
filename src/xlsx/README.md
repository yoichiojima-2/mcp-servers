# xlsx

MCP server for Excel spreadsheet (.xlsx) creation, editing, and analysis.

## Features

- **Read/Write**: Read Excel data as markdown, write cells with values or formulas
- **Create**: Create new Excel files from CSV data
- **Formulas**: Recalculate formulas and check for errors using LibreOffice
- **Sheets**: List, add, and manage multiple sheets
- **Convert**: Convert Excel to CSV format

## Tools

| Tool | Description |
|------|-------------|
| `read_excel` | Read Excel file as markdown table |
| `create_excel` | Create Excel file from CSV data |
| `write_cell` | Write value or formula to a cell |
| `recalculate` | Recalculate formulas (requires LibreOffice) |
| `get_sheet_names` | List all sheets in a file |
| `add_sheet` | Add a new sheet |
| `convert_to_csv` | Convert sheet to CSV |

## Requirements

- Python 3.12+
- LibreOffice (optional, for formula recalculation)

### Installing LibreOffice

```bash
# macOS
brew install --cask libreoffice

# Ubuntu/Debian
sudo apt-get install libreoffice
```

## Installation

```bash
# From the repository root
uv sync --package xlsx
```

## Usage

```bash
uv run python -m xlsx
```

See [server guide](../../docs/server-guide.md) for common CLI options.

## Testing

```bash
cd src/xlsx
uv run pytest -v
```
