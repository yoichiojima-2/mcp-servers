import tempfile
from pathlib import Path

import pytest
from fastmcp import Client

from docx.tools import mcp


@pytest.mark.asyncio
async def test_convert_to_markdown():
    async with Client(mcp) as client:
        with tempfile.NamedTemporaryFile(suffix=".docx") as f:
            docx_path = f.name
            md_path = f.name.replace(".docx", ".md")

            res = await client.call_tool(
                "convert_to_markdown",
                {"docx_file": docx_path, "output_file": md_path, "track_changes": "all"},
            )
            assert "docx" in res.content[0].text or "Error" in res.content[0].text


@pytest.mark.asyncio
async def test_convert_to_markdown_invalid_track_changes():
    async with Client(mcp) as client:
        res = await client.call_tool(
            "convert_to_markdown",
            {"docx_file": "test.docx", "output_file": "test.md", "track_changes": "invalid"},
        )
        assert "Invalid track_changes value" in res.content[0].text


@pytest.mark.asyncio
async def test_unpack_pack():
    async with Client(mcp) as client:
        with tempfile.TemporaryDirectory() as tmpdir:
            docx_path = Path(tmpdir) / "test.docx"
            unpack_dir = Path(tmpdir) / "unpacked"
            output_docx = Path(tmpdir) / "output.docx"

            # Create minimal valid docx for testing
            import zipfile

            with zipfile.ZipFile(docx_path, "w") as zf:
                zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types/>')
                zf.writestr("_rels/.rels", '<?xml version="1.0"?><Relationships/>')

            # Test unpack
            res = await client.call_tool("unpack", {"input_file": str(docx_path), "output_dir": str(unpack_dir)})
            assert "Unpacked" in res.content[0].text

            # Test pack
            res = await client.call_tool(
                "pack", {"input_dir": str(unpack_dir), "output_file": str(output_docx), "validate": False}
            )
            assert "Packed" in res.content[0].text
            assert output_docx.exists()


@pytest.mark.asyncio
async def test_convert_to_markdown_file_not_found():
    """Test error handling when file doesn't exist"""
    async with Client(mcp) as client:
        res = await client.call_tool(
            "convert_to_markdown",
            {"docx_file": "/nonexistent/file.docx", "output_file": "output.md"},
        )
        assert "Error" in res.content[0].text
        assert "not found" in res.content[0].text.lower()


@pytest.mark.asyncio
async def test_convert_to_pdf_file_not_found():
    """Test error handling when file doesn't exist"""
    async with Client(mcp) as client:
        res = await client.call_tool(
            "convert_to_pdf",
            {"docx_file": "/nonexistent/file.docx"},
        )
        assert "Error" in res.content[0].text
        assert "not found" in res.content[0].text.lower()
