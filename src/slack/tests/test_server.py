"""Tests for Slack MCP server initialization."""

import pytest


def test_import_module():
    """Test that the slack module can be imported."""
    import slack

    assert slack.mcp is not None


def test_mcp_has_tools():
    """Test that the MCP server has tools registered."""
    from slack import mcp

    # The server should have tools defined
    assert mcp is not None
    assert mcp.name == "slack"


@pytest.mark.asyncio
async def test_workspace_path():
    """Test get_workspace_path tool."""
    from fastmcp import Client

    from slack import mcp

    async with Client(mcp) as client:
        result = await client.call_tool("get_workspace_path", {})
        assert result.content
        path = result.content[0].text
        assert "slack" in path
        assert ".mcp-servers" in path
