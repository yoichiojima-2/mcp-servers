"""MCP server for Claude skills discovery and loading."""

import os

from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(os.getenv("NAME", "skills"))

# Module-level registry (initialized lazily)
_registry = None


def get_registry():
    """Get or create the skill registry."""
    global _registry
    if _registry is None:
        from .config import get_skill_paths
        from .core import SkillRegistry

        _registry = SkillRegistry(get_skill_paths())
        _registry.discover()
    return _registry


from . import prompts, server, tools  # noqa: F401, E402

__all__ = ["mcp", "get_registry"]
