import os

from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(os.getenv("NAME", "xlsx"))

from . import prompts, server, tools  # noqa: F401, E402

__all__ = ["mcp"]
