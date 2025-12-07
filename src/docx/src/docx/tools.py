from pathlib import Path

from . import mcp
from .scripts import pack_document, unpack_document


@mcp.tool()
def unpack(input_file: str, output_dir: str) -> str:
    """Unpack a .docx, .pptx, or .xlsx file and format XML contents.

    Args:
        input_file: Path to Office file (.docx/.pptx/.xlsx)
        output_dir: Path to output directory for unpacked contents

    Returns:
        Success message with suggested RSID for .docx files
    """
    suggested_rsid = unpack_document(input_file, output_dir)
    msg = f"Unpacked {input_file} to {output_dir}"
    if suggested_rsid:
        msg += f"\nSuggested RSID for edit session: {suggested_rsid}"
    return msg


@mcp.tool()
def pack(input_dir: str, output_file: str, validate: bool = False) -> str:
    """Pack a directory into a .docx, .pptx, or .xlsx file.

    Args:
        input_dir: Path to unpacked Office document directory
        output_file: Path to output Office file (.docx/.pptx/.xlsx)
        validate: If True, validates with LibreOffice (default: False)

    Returns:
        Success or error message
    """
    success = pack_document(input_dir, output_file, validate)
    if not success:
        return f"Failed to pack {input_dir} - validation failed"
    msg = f"Packed {input_dir} to {output_file}"
    if validate:
        msg += " (validated)"
    return msg


@mcp.tool()
def convert_to_markdown(docx_file: str, output_file: str, track_changes: str = "all") -> str:
    """Convert .docx to markdown using pandoc.

    Args:
        docx_file: Path to .docx file
        output_file: Path to output markdown file
        track_changes: How to handle tracked changes: 'accept', 'reject', or 'all' (default: 'all')

    Returns:
        Success message
    """
    import subprocess

    if track_changes not in ["accept", "reject", "all"]:
        return f"Invalid track_changes value: {track_changes}. Must be 'accept', 'reject', or 'all'"

    # Validate and resolve input file path
    docx_path = Path(docx_file).expanduser().resolve()
    if not docx_path.exists():
        return f"Error: File not found: {docx_path}"
    if not docx_path.is_file():
        return f"Error: Path is not a file: {docx_path}"

    # Resolve output file path
    output_path = Path(output_file).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            ["pandoc", f"--track-changes={track_changes}", str(docx_path), "-o", str(output_path)],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            return f"Error converting {docx_path}: {result.stderr}"

        return f"Converted {docx_path} to {output_path} (track-changes={track_changes})"
    except subprocess.TimeoutExpired:
        return f"Error: Conversion timed out after 60 seconds"
    except FileNotFoundError:
        return "Error: pandoc not found. Please install pandoc."
    except Exception as e:
        return f"Error converting file: {str(e)}"


@mcp.tool()
def convert_to_pdf(docx_file: str, output_file: str = "") -> str:
    """Convert .docx to PDF using LibreOffice.

    Args:
        docx_file: Path to .docx file
        output_file: Optional path to output PDF (default: same name as input with .pdf extension)

    Returns:
        Success message with output path
    """
    import subprocess

    # Validate and resolve input file path
    docx_path = Path(docx_file).expanduser().resolve()
    if not docx_path.exists():
        return f"Error: File not found: {docx_path}"
    if not docx_path.is_file():
        return f"Error: Path is not a file: {docx_path}"

    # Resolve output file path
    if not output_file:
        output_path = docx_path.with_suffix(".pdf")
    else:
        output_path = Path(output_file).expanduser().resolve()

    output_dir = str(output_path.parent)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf", "--outdir", output_dir, str(docx_path)],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            return f"Error converting {docx_path}: {result.stderr}"

        return f"Converted {docx_path} to {output_path}"
    except subprocess.TimeoutExpired:
        return f"Error: Conversion timed out after 120 seconds"
    except FileNotFoundError:
        return "Error: soffice (LibreOffice) not found. Please install LibreOffice."
    except Exception as e:
        return f"Error converting file: {str(e)}"
