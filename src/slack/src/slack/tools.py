"""Slack MCP tools - Proxy to @ubie-oss/slack-mcp-server.

This module creates a proxy to the npm Slack MCP server, exposing all its tools
through the FastMCP interface.

Required environment variables:
- SLACK_BOT_TOKEN: Slack Bot User OAuth Token (xoxb-...)
- SLACK_USER_TOKEN: Slack User OAuth Token (xoxp-...) for search
- SLACK_SAFE_SEARCH: Optional, set to 'true' for safe search mode
"""

import os
import shutil

from core import get_workspace
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

from . import mcp

# Check if npx is available
NPX_PATH = shutil.which("npx")


def _get_slack_client() -> Client:
    """Create a client to the npm Slack MCP server.

    Note: Each tool call creates a new npx process. This is intentional to keep
    the implementation simple and stateless. For high-frequency operations,
    consider running the npm server persistently and connecting via HTTP transport.
    """
    if not NPX_PATH:
        raise RuntimeError("npx not found. Please install Node.js from https://nodejs.org/ to use Slack integration.")

    # Validate PATH exists (required for npx to work)
    path_env = os.environ.get("PATH")
    if not path_env:
        raise RuntimeError("PATH environment variable is not set. Cannot run npx.")

    # Only pass required environment variables (principle of least privilege)
    env = {"PATH": path_env}
    if home := os.environ.get("HOME"):
        env["HOME"] = home
    if node_path := os.environ.get("NODE_PATH"):
        env["NODE_PATH"] = node_path
    # Add Slack-specific tokens
    for key in ["SLACK_BOT_TOKEN", "SLACK_USER_TOKEN", "SLACK_SAFE_SEARCH"]:
        if key in os.environ:
            env[key] = os.environ[key]

    transport = StdioTransport(
        command=NPX_PATH,
        args=["-y", "@ubie-oss/slack-mcp-server"],
        env=env,
    )
    return Client(transport)


async def _call_slack_tool(tool_name: str, params: dict, token_type: str = "SLACK_BOT_TOKEN") -> str:
    """Call a Slack tool with proper error handling.

    Args:
        tool_name: Name of the tool to call on the npm server
        params: Parameters to pass to the tool
        token_type: Which token is required (for error messages)

    Returns:
        The result text from the Slack API
    """
    try:
        async with _get_slack_client() as client:
            result = await client.call_tool(tool_name, params)
            if not result.content:
                return f"No response from Slack API. Check {token_type} is set correctly."
            return result.content[0].text
    except RuntimeError:
        raise  # Re-raise npx/PATH errors as-is
    except Exception as e:
        return f"Slack API error: {e}. Verify {token_type} and permissions."


@mcp.tool()
def get_workspace_path() -> str:
    """Get the workspace directory path for saving Slack-related files."""
    return str(get_workspace("slack"))


@mcp.tool()
async def slack_list_channels(limit: int = 100, cursor: str | None = None) -> str:
    """List public channels in the Slack workspace.

    Args:
        limit: Maximum number of channels to return (default 100)
        cursor: Pagination cursor for next page of results
    """
    params = {"limit": limit}
    if cursor:
        params["cursor"] = cursor
    return await _call_slack_tool("slack_list_channels", params)


@mcp.tool()
async def slack_post_message(channel: str, text: str) -> str:
    """Post a message to a Slack channel.

    Args:
        channel: Channel ID or name to post to
        text: Message text to send
    """
    return await _call_slack_tool("slack_post_message", {"channel": channel, "text": text})


@mcp.tool()
async def slack_reply_to_thread(channel: str, thread_ts: str, text: str) -> str:
    """Reply to a message thread in Slack.

    Args:
        channel: Channel ID where the thread exists
        thread_ts: Timestamp of the parent message
        text: Reply text to send
    """
    return await _call_slack_tool("slack_reply_to_thread", {"channel": channel, "thread_ts": thread_ts, "text": text})


@mcp.tool()
async def slack_add_reaction(channel: str, timestamp: str, reaction: str) -> str:
    """Add a reaction emoji to a message.

    Args:
        channel: Channel ID where the message exists
        timestamp: Timestamp of the message to react to
        reaction: Emoji name without colons (e.g., 'thumbsup')
    """
    return await _call_slack_tool(
        "slack_add_reaction", {"channel": channel, "timestamp": timestamp, "reaction": reaction}
    )


@mcp.tool()
async def slack_get_channel_history(channel: str, limit: int = 10) -> str:
    """Get recent messages from a Slack channel.

    Args:
        channel: Channel ID to get history from
        limit: Number of messages to retrieve (default 10)
    """
    return await _call_slack_tool("slack_get_channel_history", {"channel": channel, "limit": limit})


@mcp.tool()
async def slack_get_thread_replies(channel: str, thread_ts: str) -> str:
    """Get all replies in a message thread.

    Args:
        channel: Channel ID where the thread exists
        thread_ts: Timestamp of the parent message
    """
    return await _call_slack_tool("slack_get_thread_replies", {"channel": channel, "thread_ts": thread_ts})


@mcp.tool()
async def slack_get_users(limit: int = 100, cursor: str | None = None) -> str:
    """Get list of users in the workspace.

    Args:
        limit: Maximum number of users to return (default 100)
        cursor: Pagination cursor for next page
    """
    params = {"limit": limit}
    if cursor:
        params["cursor"] = cursor
    return await _call_slack_tool("slack_get_users", params)


@mcp.tool()
async def slack_get_user_profiles(user_ids: list[str]) -> str:
    """Get profile information for multiple users.

    Args:
        user_ids: List of user IDs to get profiles for
    """
    return await _call_slack_tool("slack_get_user_profiles", {"user_ids": user_ids})


@mcp.tool()
async def slack_search_messages(query: str, count: int = 20, cursor: str | None = None) -> str:
    """Search for messages in Slack (requires SLACK_USER_TOKEN).

    Args:
        query: Search query with Slack search modifiers
        count: Number of results to return (default 20)
        cursor: Pagination cursor
    """
    params = {"query": query, "count": count}
    if cursor:
        params["cursor"] = cursor
    return await _call_slack_tool("slack_search_messages", params, token_type="SLACK_USER_TOKEN")
