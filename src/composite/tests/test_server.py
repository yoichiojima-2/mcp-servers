"""Tests for composite server using FastMCP mount."""

import pytest
from fastmcp import Client

from composite.server import mcp


def test_mcp_server_exists():
    """Test that the MCP server is properly initialized."""
    assert mcp is not None
    assert mcp.name == "composite"


@pytest.mark.anyio
async def test_list_tools():
    """Test that mounted tools are available with prefixes."""
    async with Client(mcp) as client:
        tools = await client.list_tools()
        tool_names = [t.name for t in tools]

        # Verify langquery tools are mounted with lang_ prefix
        assert "lang_add" in tool_names
        assert "lang_query" in tool_names

        # Verify xlsx tools are mounted with xlsx_ prefix
        assert any(name.startswith("xlsx_") for name in tool_names)

        # Verify pdf tools are mounted with pdf_ prefix
        assert any(name.startswith("pdf_") for name in tool_names)

        # Verify docx tools are mounted with docx_ prefix
        assert any(name.startswith("docx_") for name in tool_names)

        # Verify pptx tools are mounted with pptx_ prefix
        assert any(name.startswith("pptx_") for name in tool_names)

        # Verify vectorstore tools are mounted with vec_ prefix
        assert any(name.startswith("vec_") for name in tool_names)

        # Verify browser tools are mounted with browser_ prefix
        assert any(name.startswith("browser_") for name in tool_names)


@pytest.mark.anyio
async def test_call_mounted_tool():
    """Test calling a tool from the mounted server."""
    async with Client(mcp) as client:
        result = await client.call_tool("lang_add", {"a": 5, "b": 3})
        assert len(result.content) == 1
        assert result.content[0].text == "8"
