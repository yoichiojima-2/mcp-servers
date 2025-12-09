import os

from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(os.getenv("NAME", "pptx"))

from . import analysis, marp, prompts, server  # noqa: F401, E402

__all__ = ["mcp"]
