#!/usr/bin/env python3
"""Unpack and format XML contents of Office files (.docx, .pptx, .xlsx)"""

import secrets
import zipfile
from pathlib import Path

import defusedxml.minidom


def unpack_document(input_file: str | Path, output_dir: str | Path) -> str:
    """Unpack an Office file and format XML contents.

    Args:
        input_file: Path to Office file (.docx/.pptx/.xlsx)
        output_dir: Path to output directory

    Returns:
        str: Suggested RSID for .docx files, empty string otherwise
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Extract with path traversal protection
    with zipfile.ZipFile(input_file) as zf:
        for member in zf.namelist():
            member_path = output_path / member
            # Prevent path traversal attacks
            if not member_path.resolve().is_relative_to(output_path.resolve()):
                raise ValueError(f"Attempted path traversal: {member}")
        zf.extractall(output_path)

    # Protect against resource exhaustion - limit XML file size to 10MB
    MAX_XML_SIZE = 10 * 1024 * 1024
    xml_files = list(output_path.rglob("*.xml")) + list(output_path.rglob("*.rels"))
    for xml_file in xml_files:
        if xml_file.stat().st_size > MAX_XML_SIZE:
            raise ValueError(
                f"XML file too large: {xml_file} ({xml_file.stat().st_size} bytes)"
            )
        content = xml_file.read_text(encoding="utf-8")
        dom = defusedxml.minidom.parseString(content)
        xml_file.write_bytes(dom.toprettyxml(indent="  ", encoding="ascii"))

    if str(input_file).endswith(".docx"):
        suggested_rsid = secrets.token_hex(4).upper()
        return suggested_rsid
    return ""
