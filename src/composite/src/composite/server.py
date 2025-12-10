"""MCP Composite Server - Aggregates multiple backend MCP servers into a single endpoint."""

import importlib
import logging
import os
from pathlib import Path

import yaml
from core import parse_args, run_server
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_PORT = 8000

mcp = FastMCP(os.getenv("NAME", "composite"))


def load_config() -> dict:
    """Load server configuration from YAML file."""
    config_path = os.getenv(
        "COMPOSITE_CONFIG",
        Path(__file__).parent.parent.parent / "composite-config.yaml",
    )
    config_path = Path(config_path)

    if not config_path.exists():
        logger.warning("Config file not found at %s, starting with no mounted servers", config_path)
        return {"servers": {}}

    with open(config_path) as f:
        return yaml.safe_load(f) or {"servers": {}}


def mount_servers():
    """Mount enabled servers from configuration."""
    config = load_config()
    servers = config.get("servers", {})

    for name, settings in servers.items():
        if not settings.get("enabled", True):
            continue

        module_name = settings.get("module", name)
        prefix = settings.get("prefix", name)

        try:
            module = importlib.import_module(module_name)
            server_mcp = getattr(module, "mcp", None)
            if server_mcp:
                mcp.mount(server_mcp, prefix=prefix)
        except ImportError as e:
            logger.warning("Could not import %s: %s", module_name, e)


mount_servers()


def serve() -> None:
    """Start MCP server."""
    args = parse_args("composite", DEFAULT_PORT)
    run_server(mcp, args)
