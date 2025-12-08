#!/usr/bin/env python3
"""Pack a directory into a .docx, .pptx, or .xlsx file with XML formatting undone."""

import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import defusedxml.minidom

# LibreOffice filter names for document validation
FILTER_DOCX = "html:HTML"
FILTER_PPTX = "html:impress_html_Export"
FILTER_XLSX = "html:HTML (StarCalc)"


def pack_document(
    input_dir: str | Path, output_file: str | Path, validate: bool = False
) -> bool:
    """Pack a directory into an Office file (.docx/.pptx/.xlsx).

    Args:
        input_dir: Path to unpacked Office document directory
        output_file: Path to output Office file
        validate: If True, validates with soffice (default: False)

    Returns:
        bool: True if successful, False if validation failed
    """
    input_dir = Path(input_dir)
    output_file = Path(output_file)

    if not input_dir.is_dir():
        raise ValueError(f"{input_dir} is not a directory")
    if output_file.suffix.lower() not in {".docx", ".pptx", ".xlsx"}:
        raise ValueError(f"{output_file} must be a .docx, .pptx, or .xlsx file")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_content_dir = Path(temp_dir) / "content"
        shutil.copytree(input_dir, temp_content_dir)

        for pattern in ["*.xml", "*.rels"]:
            for xml_file in temp_content_dir.rglob(pattern):
                condense_xml(xml_file)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in temp_content_dir.rglob("*"):
                if f.is_file():
                    zf.write(f, f.relative_to(temp_content_dir))

        if validate:
            if not validate_document(output_file):
                output_file.unlink()
                return False

    return True


def validate_document(doc_path: Path) -> bool:
    """Validate document by converting to HTML with soffice.

    Args:
        doc_path: Path to the Office document to validate

    Returns:
        bool: True if validation succeeds, False otherwise
    """
    match doc_path.suffix.lower():
        case ".docx":
            filter_name = FILTER_DOCX
        case ".pptx":
            filter_name = FILTER_PPTX
        case ".xlsx":
            filter_name = FILTER_XLSX
        case _:
            raise ValueError(f"Unsupported file type: {doc_path.suffix}")

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            result = subprocess.run(
                [
                    "soffice",
                    "--headless",
                    "--convert-to",
                    filter_name,
                    "--outdir",
                    temp_dir,
                    str(doc_path),
                ],
                capture_output=True,
                timeout=10,
                text=True,
            )
            if not (Path(temp_dir) / f"{doc_path.stem}.html").exists():
                error_msg = result.stderr.strip() or "Document validation failed"
                print(f"Validation error: {error_msg}", file=sys.stderr)
                return False
            return True
        except FileNotFoundError:
            print("Warning: soffice not found. Skipping validation.", file=sys.stderr)
            return True
        except subprocess.TimeoutExpired:
            print("Validation error: Timeout during conversion", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Validation error: {e}", file=sys.stderr)
            return False


def condense_xml(xml_file: Path) -> None:
    """Strip unnecessary whitespace and remove comments.

    Args:
        xml_file: Path to the XML file to condense
    """
    # Protect against resource exhaustion - limit XML file size to 10MB
    MAX_XML_SIZE = 10 * 1024 * 1024
    if xml_file.stat().st_size > MAX_XML_SIZE:
        raise ValueError(
            f"XML file too large: {xml_file} ({xml_file.stat().st_size} bytes)"
        )

    with open(xml_file, "r", encoding="utf-8") as f:
        dom = defusedxml.minidom.parse(f)

    for element in dom.getElementsByTagName("*"):
        if element.tagName.endswith(":t"):
            continue

        for child in list(element.childNodes):
            if (
                child.nodeType == child.TEXT_NODE
                and child.nodeValue
                and child.nodeValue.strip() == ""
            ) or child.nodeType == child.COMMENT_NODE:
                element.removeChild(child)

    with open(xml_file, "wb") as f:
        f.write(dom.toxml(encoding="UTF-8"))
