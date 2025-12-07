# PDF MCP Server

An MCP server for PDF extraction and manipulation.

## Features

- **Text Extraction**: Extract text content from PDF files with page selection
- **Table Extraction**: Extract tables in markdown, CSV, or JSON format
- **Metadata**: Get PDF metadata (title, author, page count, etc.)
- **Split**: Split PDFs into individual pages
- **Merge**: Combine multiple PDFs into one
- **Rotate**: Rotate pages by 90, 180, or 270 degrees
- **Extract Pages**: Extract specific pages to a new file

## Installation

```bash
cd pdf
uv sync
```

For OCR support (scanned documents):
```bash
uv sync --extra ocr
```

For PDF creation:
```bash
uv sync --extra create
```

## Usage

### Run as MCP Server

```bash
# SSE transport (default)
uv run python -m pdf

# stdio transport
TRANSPORT=stdio uv run python -m pdf
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NAME` | `pdf` | Server name |
| `TRANSPORT` | `sse` | Transport type (`sse` or `stdio`) |
| `HOST` | `0.0.0.0` | Host to bind |
| `PORT` | `8001` | Port to bind |
| `ALLOW_ORIGIN` | `*` | CORS allowed origins |

### Claude Desktop Configuration

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "pdf": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/pdf", "python", "-m", "pdf"],
      "env": {
        "TRANSPORT": "stdio"
      }
    }
  }
}
```

## Tools

### `extract_text`
Extract text content from a PDF file.
- `file_path`: Path to the PDF file
- `pages`: Optional page range (e.g., "1-3", "1,3,5", "2-")

### `extract_tables`
Extract tables from a PDF file.
- `file_path`: Path to the PDF file
- `pages`: Optional page range
- `format`: Output format - "markdown", "csv", or "json"

### `get_metadata`
Get metadata from a PDF file (title, author, page count, etc.)

### `get_page_count`
Get the number of pages in a PDF file.

### `split_pdf`
Split a PDF into individual pages.
- `file_path`: Path to the PDF file
- `output_dir`: Directory to save the split pages
- `pages`: Optional page range to extract

### `merge_pdfs`
Merge multiple PDF files into a single PDF.
- `file_paths`: List of paths to PDF files to merge
- `output_path`: Path for the merged output file

### `rotate_pages`
Rotate pages in a PDF file.
- `file_path`: Path to the PDF file
- `rotation`: Rotation angle (90, 180, or 270)
- `pages`: Optional page range to rotate
- `output_path`: Optional output path (defaults to overwrite)

### `extract_pages`
Extract specific pages from a PDF to a new file.
- `file_path`: Path to the source PDF
- `pages`: Page range to extract
- `output_path`: Path for the output file

## Page Range Syntax

- `1-3`: Pages 1 through 3
- `1,3,5`: Pages 1, 3, and 5
- `2-`: Page 2 to the end
- `-3`: Pages 1 through 3
