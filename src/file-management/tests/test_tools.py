"""Tests for file-management tools."""

import base64
import tempfile
from pathlib import Path

import pytest
from fastmcp import Client

from file_management import mcp


@pytest.mark.asyncio
async def test_get_workspace_path():
    """Test get_workspace_path returns correct path."""
    async with Client(mcp) as client:
        res = await client.call_tool("get_workspace_path", {})
        path = res.content[0].text
        assert ".mcp-servers" in path


@pytest.mark.asyncio
async def test_write_and_read_file():
    """Test writing and reading a file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = str(Path(tmpdir) / "test.txt")
        content = "Hello, World!"

        async with Client(mcp) as client:
            # Write file
            res = await client.call_tool("write_file", {"file_path": file_path, "content": content})
            assert "Successfully wrote" in res.content[0].text

            # Read file
            res = await client.call_tool("read_file", {"file_path": file_path})
            assert res.content[0].text == content


@pytest.mark.asyncio
async def test_append_file():
    """Test appending to a file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = str(Path(tmpdir) / "test.txt")

        async with Client(mcp) as client:
            await client.call_tool("write_file", {"file_path": file_path, "content": "Hello"})
            await client.call_tool("append_file", {"file_path": file_path, "content": ", World!"})

            res = await client.call_tool("read_file", {"file_path": file_path})
            assert res.content[0].text == "Hello, World!"


@pytest.mark.asyncio
async def test_list_directory():
    """Test listing directory contents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        (Path(tmpdir) / "file1.txt").write_text("content1")
        (Path(tmpdir) / "file2.txt").write_text("content2")
        (Path(tmpdir) / "subdir").mkdir()

        async with Client(mcp) as client:
            res = await client.call_tool("list_directory", {"dir_path": tmpdir})
            result = res.content[0].text
            assert "file1.txt" in result
            assert "file2.txt" in result
            assert "subdir/" in result


@pytest.mark.asyncio
async def test_read_nonexistent_file():
    """Test reading a file that doesn't exist."""
    async with Client(mcp) as client:
        res = await client.call_tool("read_file", {"file_path": "/nonexistent/path/file.txt"})
        assert "Error: File not found" in res.content[0].text


@pytest.mark.asyncio
async def test_write_to_forbidden_path():
    """Test that writing to system paths is blocked."""
    async with Client(mcp) as client:
        res = await client.call_tool("write_file", {"file_path": "/etc/test.txt", "content": "test"})
        result = res.content[0].text.lower()
        assert "error" in result


@pytest.mark.asyncio
async def test_write_and_read_binary():
    """Test writing and reading binary files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = str(Path(tmpdir) / "test.bin")
        content = b"\x00\x01\x02\x03\xff\xfe"
        content_base64 = base64.b64encode(content).decode("ascii")

        async with Client(mcp) as client:
            # Write binary
            res = await client.call_tool("write_binary", {"file_path": file_path, "content_base64": content_base64})
            assert "Successfully wrote" in res.content[0].text

            # Read binary
            res = await client.call_tool("read_binary", {"file_path": file_path})
            assert res.content[0].text == content_base64


@pytest.mark.asyncio
async def test_write_binary_invalid_base64():
    """Test that invalid base64 content is rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = str(Path(tmpdir) / "test.bin")

        async with Client(mcp) as client:
            res = await client.call_tool(
                "write_binary", {"file_path": file_path, "content_base64": "not-valid-base64!!!"}
            )
            assert "error" in res.content[0].text.lower()


@pytest.mark.asyncio
async def test_path_traversal_blocked():
    """Test that path traversal attempts are blocked."""
    async with Client(mcp) as client:
        res = await client.call_tool("write_file", {"file_path": "/tmp/../etc/test.txt", "content": "test"})
        result = res.content[0].text.lower()
        assert "error" in result


@pytest.mark.asyncio
async def test_symlink_to_forbidden_blocked():
    """Test that symlinks to forbidden paths are blocked."""
    with tempfile.TemporaryDirectory() as tmpdir:
        symlink = Path(tmpdir) / "link_to_etc"
        try:
            symlink.symlink_to("/etc")

            async with Client(mcp) as client:
                res = await client.call_tool("write_file", {"file_path": str(symlink / "test.txt"), "content": "test"})
                assert "error" in res.content[0].text.lower()
        except OSError:
            # Skip if symlinks not supported (e.g., some Windows configs)
            pytest.skip("Symlinks not supported on this system")


@pytest.mark.asyncio
async def test_delete_file():
    """Test deleting a file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = str(Path(tmpdir) / "test.txt")

        async with Client(mcp) as client:
            # Create file
            await client.call_tool("write_file", {"file_path": file_path, "content": "test"})
            assert Path(file_path).exists()

            # Delete file
            res = await client.call_tool("delete_file", {"file_path": file_path})
            assert "Successfully deleted" in res.content[0].text
            assert not Path(file_path).exists()


@pytest.mark.asyncio
async def test_delete_nonexistent_file():
    """Test deleting a file that doesn't exist."""
    async with Client(mcp) as client:
        res = await client.call_tool("delete_file", {"file_path": "/nonexistent/path/file.txt"})
        assert "Error: File not found" in res.content[0].text


@pytest.mark.asyncio
async def test_delete_forbidden_path_blocked():
    """Test that deleting system paths is blocked."""
    async with Client(mcp) as client:
        res = await client.call_tool("delete_file", {"file_path": "/etc/passwd"})
        result = res.content[0].text.lower()
        assert "error" in result
