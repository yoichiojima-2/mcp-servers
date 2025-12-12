"""Google Workspace MCP Server."""

from core import parse_args, run_server

from . import mcp

DEFAULT_PORT = 8015


def serve() -> None:
    """Start MCP server."""
    args = parse_args("google-workspace", DEFAULT_PORT)
    run_server(mcp, args)
