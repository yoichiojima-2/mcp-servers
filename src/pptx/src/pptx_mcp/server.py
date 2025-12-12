from core import parse_args, run_server

from . import mcp

DEFAULT_PORT = 8009


def serve() -> None:
    """Start MCP server."""
    args = parse_args("pptx", DEFAULT_PORT)
    run_server(mcp, args)
