"""Tests for file-management tools."""

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
