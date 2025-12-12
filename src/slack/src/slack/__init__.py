"""Slack MCP Server - Wraps @ubie-oss/slack-mcp-server npm package."""

import logging
import os
import shutil

from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

logger = logging.getLogger(__name__)

# Check for npx at startup and warn if not found
if not shutil.which("npx"):
    logger.warning("npx not found. Slack tools require Node.js. Install from https://nodejs.org/")

mcp = FastMCP(os.getenv("NAME", "slack"))

from . import server, tools  # noqa: F401, E402

__all__ = ["mcp"]
