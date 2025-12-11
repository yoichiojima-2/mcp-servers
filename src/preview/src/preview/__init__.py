"""Preview server for serving HTML content with live reload."""

import os

from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(os.getenv("NAME", "preview"))

from . import server, tools  # noqa: E402, F401

__all__ = ["mcp"]
