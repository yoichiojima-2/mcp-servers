# docx

An MCP server for Word document (.docx) creation, editing, and analysis. Built with [FastMCP](https://github.com/jlowin/fastmcp).

## Features

- **Unpack/Pack**: Extract .docx files to XML for editing and repack them
- **Convert to Markdown**: Extract text content with tracked changes support
- **Convert to PDF**: Convert .docx to PDF using LibreOffice
- **Validation**: Optional LibreOffice validation when packing documents

## Installation

```bash
uv sync
```

## Usage

### Run the server

```bash
uv run python -m docx
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NAME` | `docx` | Server name |
| `TRANSPORT` | `stdio` | Transport protocol (`sse` or `stdio`) |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `ALLOW_ORIGIN` | `*` | CORS allowed origins |

### Docker

```bash
docker compose up
```

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
