"""Tests for Slack MCP tools.

Note: These tests require SLACK_BOT_TOKEN to be set for full functionality.
Without tokens, they verify the tools are registered but skip actual API calls.
"""

import os

import pytest
from fastmcp import Client

from slack import mcp


@pytest.fixture
def has_slack_token():
    """Check if Slack token is available."""
    return bool(os.getenv("SLACK_BOT_TOKEN"))


@pytest.fixture
def has_npx():
    """Check if npx is available."""
    import shutil

    return shutil.which("npx") is not None


@pytest.mark.asyncio
async def test_tools_registered():
    """Verify all expected tools are registered."""
    async with Client(mcp) as client:
        tools = await client.list_tools()
        tool_names = {t.name for t in tools}

        expected = {
            "get_workspace_path",
            "slack_list_channels",
            "slack_post_message",
            "slack_reply_to_thread",
            "slack_add_reaction",
            "slack_get_channel_history",
            "slack_get_thread_replies",
            "slack_get_users",
            "slack_get_user_profiles",
            "slack_search_messages",
        }

        assert expected.issubset(tool_names), f"Missing tools: {expected - tool_names}"


@pytest.mark.asyncio
async def test_list_channels_requires_npm_package(has_npx, has_slack_token):
    """Test list_channels requires npm package and token."""
    if not has_npx:
        pytest.skip("npx not available")
    if not has_slack_token:
        pytest.skip("SLACK_BOT_TOKEN not set")

    async with Client(mcp) as client:
        # With token set, should be able to call the tool
        result = await client.call_tool("slack_list_channels", {"limit": 1})
        assert result.content is not None
