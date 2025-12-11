from core import parse_args, run_server

from . import mcp

DEFAULT_PORT = 8012


def serve() -> None:
    """Start MCP server."""
    args = parse_args("shell", DEFAULT_PORT)
    run_server(mcp, args)
