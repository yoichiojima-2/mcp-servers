"""Server configuration and startup for preview."""

from core import parse_args, run_server

from . import mcp

DEFAULT_PORT = 8012


def serve() -> None:
    """Start the preview MCP server."""
    args = parse_args("preview", DEFAULT_PORT)
    run_server(mcp, args)
