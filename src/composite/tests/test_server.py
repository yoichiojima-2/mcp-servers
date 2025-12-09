"""Tests for composite server using FastMCP mount."""

import pytest
from fastmcp import Client

from composite.server import load_config, mcp


def test_mcp_server_exists():
    """Test that the MCP server is properly initialized."""
    assert mcp is not None
    assert mcp.name == "composite"


@pytest.mark.anyio
async def test_list_tools():
    """Test that mounted tools are available with prefixes based on config."""
    config = load_config()
    enabled_servers = [
        (name, settings) for name, settings in config.get("servers", {}).items() if settings.get("enabled", True)
    ]

    async with Client(mcp) as client:
        tools = await client.list_tools()
        tool_names = [t.name for t in tools]

        # Verify each enabled server has at least one tool with its prefix
        for name, settings in enabled_servers:
            prefix = settings.get("prefix", name)
            assert any(t.startswith(f"{prefix}_") for t in tool_names), (
                f"No tools found with prefix '{prefix}_' for server '{name}'"
            )


@pytest.mark.anyio
async def test_call_mounted_tool():
    """Test calling a tool from the mounted server."""
    async with Client(mcp) as client:
        result = await client.call_tool("lang_add", {"a": 5, "b": 3})
        assert len(result.content) == 1
        assert result.content[0].text == "8"
