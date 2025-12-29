# docx

MCP server for Word document (.docx) creation, editing, and analysis.

## Features

- **Unpack/Pack**: Extract .docx files to XML for editing and repack them
- **Convert to Markdown**: Extract text content with tracked changes support
- **Convert to PDF**: Convert .docx to PDF using LibreOffice
- **Validation**: Optional LibreOffice validation when packing documents

## Tools

| Tool | Description |
|------|-------------|
| `unpack` | Unpack a .docx, .pptx, or .xlsx file and format XML contents |
| `pack` | Pack a directory into a .docx, .pptx, or .xlsx file |
| `convert_to_markdown` | Convert .docx to markdown using pandoc |
| `convert_to_pdf` | Convert .docx to PDF using LibreOffice |

## Requirements

- Python 3.12+
- pandoc (for markdown conversion)
- LibreOffice (for PDF conversion and validation)

## Installation

```bash
# From the repository root
uv sync --package docx
```

## Usage

```bash
uv run python -m docx
```

See [server guide](../../docs/server-guide.md) for common CLI options.

## Testing

```bash
cd src/docx
uv run pytest -v
```
