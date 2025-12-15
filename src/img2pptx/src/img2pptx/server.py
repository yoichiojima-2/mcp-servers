from core import parse_args, run_server

from . import mcp

DEFAULT_PORT = 8007


def serve() -> None:
    """Start MCP server."""
    args = parse_args("img2pptx", DEFAULT_PORT)
    run_server(mcp, args)
