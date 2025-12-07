# docx MCP Server

MCP server for Word document (.docx) creation, editing, and analysis.

## Features

- **Unpack/Pack**: Extract .docx files to XML for editing and repack them
- **Convert to Markdown**: Extract text content with tracked changes support
- **Convert to PDF**: Convert .docx to PDF using LibreOffice
- **Validation**: Optional LibreOffice validation when packing documents

## Tools

### `unpack`
Unpack a .docx, .pptx, or .xlsx file and format XML contents.

**Parameters:**
- `input_file` (str): Path to Office file
- `output_dir` (str): Path to output directory

### `pack`
Pack a directory into a .docx, .pptx, or .xlsx file.

**Parameters:**
- `input_dir` (str): Path to unpacked directory
- `output_file` (str): Path to output Office file
- `validate` (bool, optional): Validate with LibreOffice (default: False)

### `convert_to_markdown`
Convert .docx to markdown using pandoc.

**Parameters:**
- `docx_file` (str): Path to .docx file
- `output_file` (str): Path to output markdown file
- `track_changes` (str, optional): How to handle tracked changes: 'accept', 'reject', or 'all' (default: 'all')

### `convert_to_pdf`
Convert .docx to PDF using LibreOffice.

**Parameters:**
- `docx_file` (str): Path to .docx file
- `output_file` (str, optional): Path to output PDF (default: same name as input with .pdf extension)

## Requirements

- Python 3.12+
- pandoc (for markdown conversion)
- LibreOffice (for PDF conversion and validation)

## Installation

### Install Python Dependencies

```bash
pip install -e .
```

### Install External Dependencies

#### Pandoc (for Markdown conversion)

**macOS:**
```bash
brew install pandoc
```

**Ubuntu/Debian:**
```bash
sudo apt-get install pandoc
```

**Windows:**
Download from https://pandoc.org/installing.html

#### LibreOffice (for PDF conversion and validation)

**macOS:**
```bash
brew install --cask libreoffice
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libreoffice
```

**Windows:**
Download from https://www.libreoffice.org/download/download/

## Error Handling

The tools provide descriptive error messages for common scenarios:
- **File not found**: Returns error if input file doesn't exist
- **Invalid file path**: Returns error if path is not a valid file
- **External tool not found**: Returns error with installation instructions if pandoc or LibreOffice is not installed
- **Conversion timeout**: Operations timeout after 60-120 seconds with appropriate error message
- **Validation failed**: Pack operation with `validate=True` will fail if document is invalid

## Usage

### stdio
```bash
python -m docx
```

### HTTP
```bash
TRANSPORT=sse HOST=0.0.0.0 PORT=8000 python -m docx
```

## Testing

```bash
pytest
```
