import os

from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(os.getenv("NAME", "nano-banana"))

from . import server, tools  # noqa: F401, E402

__all__ = ["mcp", "serve"]


def serve():
    """Start the MCP server."""
    from .server import serve as _serve

    _serve()
