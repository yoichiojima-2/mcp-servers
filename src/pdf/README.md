# pdf

MCP server for PDF extraction and manipulation.

## Features

- **Text Extraction**: Extract text content from PDF files with page selection
- **Table Extraction**: Extract tables in markdown, CSV, or JSON format
- **Metadata**: Get PDF metadata (title, author, page count, etc.)
- **Split**: Split PDFs into individual pages
- **Merge**: Combine multiple PDFs into one
- **Rotate**: Rotate pages by 90, 180, or 270 degrees
- **Extract Pages**: Extract specific pages to a new file

## Tools

| Tool | Description |
|------|-------------|
| `extract_text` | Extract text content from PDF with optional page range |
| `extract_tables` | Extract tables as markdown, CSV, or JSON |
| `get_metadata` | Get PDF metadata (title, author, page count, etc.) |
| `get_page_count` | Get number of pages |
| `split_pdf` | Split into individual pages |
| `merge_pdfs` | Combine multiple PDFs into one |
| `rotate_pages` | Rotate pages by 90, 180, or 270 degrees |
| `extract_pages` | Extract specific pages to a new file |

## Requirements

- Python 3.12+
- Optional: `uv sync --extra ocr` for OCR support
- Optional: `uv sync --extra create` for PDF creation

## Page Range Syntax

- `1-3`: Pages 1 through 3
- `1,3,5`: Pages 1, 3, and 5
- `2-`: Page 2 to the end
- `-3`: Pages 1 through 3

## Usage

```bash
uv run python -m pdf
```

See [server guide](../../docs/server-guide.md) for common CLI options.
