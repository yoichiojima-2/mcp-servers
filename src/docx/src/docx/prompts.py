from . import mcp


@mcp.prompt()
def docx_workflow() -> str:
    """Provides guidance on working with Word documents."""
    return """# Working with Word Documents (.docx)

## Quick Reference

### Reading Documents
- `convert_to_markdown` - Extract text as markdown (preserves tracked changes)

### Creating/Editing Documents
- `unpack` - Extract .docx to XML for editing
- `pack` - Repack edited XML back to .docx

### Converting Documents
- `convert_to_pdf` - Convert .docx to PDF
- `convert_to_markdown` - Convert to markdown

## Typical Workflows

### 1. Read Document Content
```
convert_to_markdown(docx_file="document.docx", output_file="output.md", track_changes="all")
```

### 2. Edit Document (Advanced)
```
# Step 1: Unpack
unpack(input_file="document.docx", output_dir="unpacked")

# Step 2: Edit XML files in unpacked/word/document.xml
# Use grep/sed or custom scripts to modify XML

# Step 3: Repack
pack(input_dir="unpacked", output_file="edited.docx", validate=True)
```

### 3. Convert to PDF
```
convert_to_pdf(docx_file="document.docx")
```

## Notes
- Requires pandoc for markdown conversion
- Requires LibreOffice (soffice) for PDF conversion and validation
- XML editing requires understanding of OOXML format
"""
