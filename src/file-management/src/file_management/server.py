from core import parse_args, run_server

from . import mcp

DEFAULT_PORT = 8005


def serve() -> None:
    """Start MCP server."""
    args = parse_args("file-management", DEFAULT_PORT)
    run_server(mcp, args)
