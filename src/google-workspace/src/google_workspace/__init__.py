"""Google Workspace MCP server for Gmail, Drive, Sheets, Docs, Slides, and Calendar."""

import os

from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(os.getenv("NAME", "google-workspace"))

from . import server, tools  # noqa: F401, E402

__all__ = ["mcp"]
