from core import parse_args, run_server

from . import mcp

DEFAULT_PORT = 8014


def serve() -> None:
    """Start MCP server."""
    args = parse_args("vectorstore", DEFAULT_PORT)
    run_server(mcp, args)
