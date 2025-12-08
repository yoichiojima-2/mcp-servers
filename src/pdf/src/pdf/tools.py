from pathlib import Path

import pdfplumber
from pypdf import PdfReader, PdfWriter

from . import mcp

# ======================================================
# Text Extraction
# ======================================================


@mcp.tool()
def extract_text(file_path: str, pages: str | None = None) -> str:
    """
    Extract text content from a PDF file.

    Args:
        file_path: Path to the PDF file
        pages: Optional page range (e.g., "1-3", "1,3,5", "2-"). If None, extracts all pages.

    Returns:
        Extracted text content
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    page_indices = _parse_page_range(pages, path) if pages else None

    results = []
    with pdfplumber.open(path) as pdf:
        total_pages = len(pdf.pages)
        target_pages = page_indices if page_indices else range(total_pages)

        for i in target_pages:
            if 0 <= i < total_pages:
                page = pdf.pages[i]
                text = page.extract_text() or ""
                results.append(f"--- Page {i + 1} ---\n{text}")

    return "\n\n".join(results) if results else "No text extracted."


@mcp.tool()
def extract_tables(
    file_path: str, pages: str | None = None, format: str = "markdown"
) -> str:
    """
    Extract tables from a PDF file.

    Args:
        file_path: Path to the PDF file
        pages: Optional page range (e.g., "1-3", "1,3,5"). If None, extracts from all pages.
        format: Output format - "markdown", "csv", or "json"

    Returns:
        Extracted tables in the specified format
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    page_indices = _parse_page_range(pages, path) if pages else None

    results = []
    with pdfplumber.open(path) as pdf:
        total_pages = len(pdf.pages)
        target_pages = page_indices if page_indices else range(total_pages)

        for i in target_pages:
            if 0 <= i < total_pages:
                page = pdf.pages[i]
                tables = page.extract_tables()

                for table_idx, table in enumerate(tables):
                    if table:
                        formatted = _format_table(table, format)
                        results.append(
                            f"--- Page {i + 1}, Table {table_idx + 1} ---\n{formatted}"
                        )

    return "\n\n".join(results) if results else "No tables found."


# ======================================================
# Metadata
# ======================================================


@mcp.tool()
def get_metadata(file_path: str) -> str:
    """
    Get metadata from a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        PDF metadata (title, author, subject, creator, page count, etc.)
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    reader = PdfReader(str(path))
    meta = reader.metadata or {}

    info = {
        "Title": meta.get("/Title", "N/A"),
        "Author": meta.get("/Author", "N/A"),
        "Subject": meta.get("/Subject", "N/A"),
        "Creator": meta.get("/Creator", "N/A"),
        "Producer": meta.get("/Producer", "N/A"),
        "Creation Date": meta.get("/CreationDate", "N/A"),
        "Modification Date": meta.get("/ModDate", "N/A"),
        "Page Count": len(reader.pages),
    }

    return "\n".join(f"{k}: {v}" for k, v in info.items())


@mcp.tool()
def get_page_count(file_path: str) -> int:
    """
    Get the number of pages in a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Number of pages
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    reader = PdfReader(str(path))
    return len(reader.pages)


# ======================================================
# PDF Manipulation
# ======================================================


@mcp.tool()
def split_pdf(file_path: str, output_dir: str, pages: str | None = None) -> str:
    """
    Split a PDF into individual pages or a subset of pages.

    Args:
        file_path: Path to the PDF file
        output_dir: Directory to save the split pages
        pages: Optional page range to extract (e.g., "1-3", "1,3,5"). If None, splits all pages.

    Returns:
        List of created files
    """
    path = Path(file_path).expanduser().resolve()
    out_dir = Path(output_dir).expanduser().resolve()

    if not path.exists():
        return f"Error: File not found: {path}"

    out_dir.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(path))
    page_indices = _parse_page_range(pages, path) if pages else range(len(reader.pages))

    created_files = []
    base_name = path.stem

    for i in page_indices:
        if 0 <= i < len(reader.pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[i])

            output_path = out_dir / f"{base_name}_page_{i + 1}.pdf"
            with open(output_path, "wb") as f:
                writer.write(f)
            created_files.append(str(output_path))

    return f"Created {len(created_files)} files:\n" + "\n".join(created_files)


@mcp.tool()
def merge_pdfs(file_paths: list[str], output_path: str) -> str:
    """
    Merge multiple PDF files into a single PDF.

    Args:
        file_paths: List of paths to PDF files to merge
        output_path: Path for the merged output file

    Returns:
        Path to the merged file
    """
    writer = PdfWriter()
    out_path = Path(output_path).expanduser().resolve()

    for fp in file_paths:
        path = Path(fp).expanduser().resolve()
        if not path.exists():
            return f"Error: File not found: {path}"

        reader = PdfReader(str(path))
        for page in reader.pages:
            writer.add_page(page)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        writer.write(f)

    return f"Merged {len(file_paths)} files into: {out_path}"


@mcp.tool()
def rotate_pages(
    file_path: str,
    rotation: int,
    pages: str | None = None,
    output_path: str | None = None,
) -> str:
    """
    Rotate pages in a PDF file.

    Args:
        file_path: Path to the PDF file
        rotation: Rotation angle in degrees (90, 180, or 270)
        pages: Optional page range to rotate. If None, rotates all pages.
        output_path: Optional output path. If None, overwrites the original file.

    Returns:
        Path to the rotated file
    """
    if rotation not in (90, 180, 270):
        return "Error: Rotation must be 90, 180, or 270 degrees"

    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    reader = PdfReader(str(path))
    writer = PdfWriter()
    page_indices = _parse_page_range(pages, path) if pages else None

    for i, page in enumerate(reader.pages):
        if page_indices is None or i in page_indices:
            page.rotate(rotation)
        writer.add_page(page)

    out = Path(output_path).expanduser().resolve() if output_path else path
    with open(out, "wb") as f:
        writer.write(f)

    return f"Rotated pages by {rotation}° and saved to: {out}"


@mcp.tool()
def extract_pages(file_path: str, pages: str, output_path: str) -> str:
    """
    Extract specific pages from a PDF and save to a new file.

    Args:
        file_path: Path to the source PDF file
        pages: Page range to extract (e.g., "1-3", "1,3,5", "5-")
        output_path: Path for the output file

    Returns:
        Path to the extracted file
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    reader = PdfReader(str(path))
    writer = PdfWriter()
    page_indices = _parse_page_range(pages, path)

    for i in page_indices:
        if 0 <= i < len(reader.pages):
            writer.add_page(reader.pages[i])

    out = Path(output_path).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as f:
        writer.write(f)

    return f"Extracted {len(page_indices)} pages to: {out}"


# ======================================================
# Helper Functions
# ======================================================


def _parse_page_range(pages_str: str, path: Path) -> list[int]:
    """
    Parse a page range string into a list of 0-based page indices.

    Supports formats like:
    - "1-3" -> [0, 1, 2]
    - "1,3,5" -> [0, 2, 4]
    - "2-" -> [1, 2, 3, ...] (to end)
    - "-3" -> [0, 1, 2] (from start)
    """
    reader = PdfReader(str(path))
    total_pages = len(reader.pages)
    indices = set()

    for part in pages_str.split(","):
        part = part.strip()
        if "-" in part:
            if part.startswith("-"):
                start, end = 0, int(part[1:])
            elif part.endswith("-"):
                start, end = int(part[:-1]), total_pages
            else:
                start, end = map(int, part.split("-"))
            indices.update(range(start - 1, end))
        else:
            indices.add(int(part) - 1)

    return sorted(i for i in indices if 0 <= i < total_pages)


def _format_table(table: list[list], format: str) -> str:
    """Format a table in the specified format."""
    if format == "csv":
        lines = []
        for row in table:
            cells = [str(cell).replace(",", ";") if cell else "" for cell in row]
            lines.append(",".join(cells))
        return "\n".join(lines)

    elif format == "json":
        import json

        if table and len(table) > 1:
            headers = [str(h) if h else f"col_{i}" for i, h in enumerate(table[0])]
            rows = []
            for row in table[1:]:
                rows.append({headers[i]: cell for i, cell in enumerate(row)})
            return json.dumps(rows, indent=2)
        return json.dumps(table, indent=2)

    else:  # markdown
        if not table:
            return ""
        lines = []
        for i, row in enumerate(table):
            cells = [str(cell) if cell else "" for cell in row]
            lines.append("| " + " | ".join(cells) + " |")
            if i == 0:
                lines.append("| " + " | ".join(["---"] * len(cells)) + " |")
        return "\n".join(lines)
