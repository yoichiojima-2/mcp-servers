import os

from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(os.getenv("NAME", "file-management"))

from . import server, tools  # noqa: F401, E402

__all__ = ["mcp"]
