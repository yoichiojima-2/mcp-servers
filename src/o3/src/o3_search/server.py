from core import parse_args, run_server

from . import mcp

DEFAULT_PORT = 8008


def serve() -> None:
    """Start MCP server."""
    args = parse_args("o3", DEFAULT_PORT)
    run_server(mcp, args)
