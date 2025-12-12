"""Slack MCP Server - Proxies to @ubie-oss/slack-mcp-server."""

from core import parse_args, run_server

from . import mcp

DEFAULT_PORT = 8013


def serve() -> None:
    """Start MCP server."""
    args = parse_args("slack", DEFAULT_PORT)
    run_server(mcp, args)
