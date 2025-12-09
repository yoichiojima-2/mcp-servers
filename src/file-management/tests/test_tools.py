import base64
import tempfile
from pathlib import Path

import pytest
from fastmcp import Client

from file_management.tools import mcp


@pytest.mark.asyncio
async def test_write_file():
    async with Client(mcp) as client:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = str(Path(tmpdir) / "test.txt")
            content = "Hello, World!"

            res = await client.call_tool("write_file", {"file_path": file_path, "content": content})
            assert "Successfully wrote" in res.content[0].text
            assert Path(file_path).exists()
            assert Path(file_path).read_text() == content


@pytest.mark.asyncio
async def test_write_file_large():
    """Test writing a large file that would exceed shell limits"""
    async with Client(mcp) as client:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = str(Path(tmpdir) / "large.txt")
            content = "x" * 100_000  # 100KB of content

            res = await client.call_tool("write_file", {"file_path": file_path, "content": content})
            assert "Successfully wrote" in res.content[0].text
            assert "100,000 bytes" in res.content[0].text
            assert Path(file_path).exists()
            assert len(Path(file_path).read_text()) == 100_000


@pytest.mark.asyncio
async def test_write_file_creates_parent_dirs():
    async with Client(mcp) as client:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = str(Path(tmpdir) / "nested" / "dir" / "test.txt")
            content = "Nested content"

            res = await client.call_tool("write_file", {"file_path": file_path, "content": content})
            assert "Successfully wrote" in res.content[0].text
            assert Path(file_path).exists()


@pytest.mark.asyncio
async def test_write_file_forbidden_path():
    async with Client(mcp) as client:
        res = await client.call_tool("write_file", {"file_path": "/etc/test.txt", "content": "test"})
        assert "Error" in res.content[0].text
        # Either permission denied or system directory validation error
        assert "permission denied" in res.content[0].text.lower() or "system directory" in res.content[0].text.lower()


@pytest.mark.asyncio
async def test_write_binary():
    async with Client(mcp) as client:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = str(Path(tmpdir) / "test.bin")
            content = b"Binary content with \x00 bytes"
            content_base64 = base64.b64encode(content).decode()

            res = await client.call_tool("write_binary", {"file_path": file_path, "content_base64": content_base64})
            assert "Successfully wrote" in res.content[0].text
            assert Path(file_path).exists()
            assert Path(file_path).read_bytes() == content


@pytest.mark.asyncio
async def test_write_binary_invalid_base64():
    async with Client(mcp) as client:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = str(Path(tmpdir) / "test.bin")

            res = await client.call_tool(
                "write_binary", {"file_path": file_path, "content_base64": "not-valid-base64!"}
            )
            assert "Error" in res.content[0].text
            # Base64 decode errors can be "Invalid base64" or "Incorrect padding"
            assert "base64" in res.content[0].text.lower() or "padding" in res.content[0].text.lower()


@pytest.mark.asyncio
async def test_append_file():
    async with Client(mcp) as client:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = str(Path(tmpdir) / "test.txt")

            await client.call_tool("write_file", {"file_path": file_path, "content": "First line\n"})
            res = await client.call_tool("append_file", {"file_path": file_path, "content": "Second line\n"})
            assert "Successfully appended" in res.content[0].text
            assert Path(file_path).read_text() == "First line\nSecond line\n"


@pytest.mark.asyncio
async def test_append_file_creates_new():
    async with Client(mcp) as client:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = str(Path(tmpdir) / "new.txt")

            res = await client.call_tool("append_file", {"file_path": file_path, "content": "Content"})
            assert "Successfully appended" in res.content[0].text
            assert Path(file_path).exists()
            assert Path(file_path).read_text() == "Content"


@pytest.mark.asyncio
async def test_write_file_with_encoding():
    async with Client(mcp) as client:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = str(Path(tmpdir) / "japanese.txt")
            content = "こんにちは世界"

            res = await client.call_tool("write_file", {"file_path": file_path, "content": content})
            assert "Successfully wrote" in res.content[0].text
            assert Path(file_path).read_text(encoding="utf-8") == content


@pytest.mark.asyncio
async def test_read_file():
    async with Client(mcp) as client:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = str(Path(tmpdir) / "test.txt")
            content = "Hello, World!"
            Path(file_path).write_text(content)

            res = await client.call_tool("read_file", {"file_path": file_path})
            assert res.content[0].text == content


@pytest.mark.asyncio
async def test_read_file_not_found():
    async with Client(mcp) as client:
        res = await client.call_tool("read_file", {"file_path": "/nonexistent/file.txt"})
        assert "Error" in res.content[0].text
        assert "not found" in res.content[0].text.lower()


@pytest.mark.asyncio
async def test_read_binary():
    async with Client(mcp) as client:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = str(Path(tmpdir) / "test.bin")
            content = b"Binary \x00 content"
            Path(file_path).write_bytes(content)

            res = await client.call_tool("read_binary", {"file_path": file_path})
            decoded = base64.b64decode(res.content[0].text)
            assert decoded == content


@pytest.mark.asyncio
async def test_list_directory():
    async with Client(mcp) as client:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some files and directories
            (Path(tmpdir) / "file1.txt").write_text("content1")
            (Path(tmpdir) / "file2.txt").write_text("content2")
            (Path(tmpdir) / "subdir").mkdir()

            res = await client.call_tool("list_directory", {"dir_path": tmpdir})
            text = res.content[0].text
            assert "file1.txt" in text
            assert "file2.txt" in text
            assert "subdir/" in text


@pytest.mark.asyncio
async def test_list_directory_with_pattern():
    async with Client(mcp) as client:
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "file1.txt").write_text("content1")
            (Path(tmpdir) / "file2.py").write_text("content2")
            (Path(tmpdir) / "file3.txt").write_text("content3")

            res = await client.call_tool("list_directory", {"dir_path": tmpdir, "pattern": "*.txt"})
            text = res.content[0].text
            assert "file1.txt" in text
            assert "file3.txt" in text
            assert "file2.py" not in text


@pytest.mark.asyncio
async def test_list_directory_not_found():
    async with Client(mcp) as client:
        res = await client.call_tool("list_directory", {"dir_path": "/nonexistent/dir"})
        assert "Error" in res.content[0].text
        assert "not found" in res.content[0].text.lower()


@pytest.mark.asyncio
async def test_write_file_symlink_to_forbidden():
    """Test that symlinks to forbidden directories are blocked"""
    async with Client(mcp) as client:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a symlink pointing to /etc
            symlink_path = Path(tmpdir) / "malicious_link"
            try:
                symlink_path.symlink_to("/etc")
            except OSError:
                pytest.skip("Cannot create symlink (permission denied)")

            res = await client.call_tool(
                "write_file",
                {"file_path": str(symlink_path / "test.txt"), "content": "test"},
            )
            assert "Error" in res.content[0].text
            # Either our validation catches it or OS permission denied - both are acceptable security outcomes
            text_lower = res.content[0].text.lower()
            assert "system directory" in text_lower or "permission denied" in text_lower
