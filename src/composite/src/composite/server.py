"""MCP Composite Server - Aggregates multiple backend MCP servers into a single endpoint."""

import argparse
import importlib
import logging
import os
import sys
from pathlib import Path

import yaml
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


def _get_port_default() -> int:
    """Get port from environment variable with validation."""
    port_str = os.getenv("PORT")
    if port_str is None:
        return DEFAULT_PORT
    try:
        return int(port_str)
    except ValueError:
        print(f"Error: Invalid PORT environment variable '{port_str}'. Must be an integer.", file=sys.stderr)
        sys.exit(1)


def _validate_port(value: str) -> int:
    """Validate port is in valid range."""
    try:
        port = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid integer")
    if not (1 <= port <= 65535):
        raise argparse.ArgumentTypeError(f"Port must be between 1 and 65535, got {port}")
    return port


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="composite MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default=os.getenv("TRANSPORT", "stdio"),
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("HOST", "0.0.0.0"),
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=_validate_port,
        default=_get_port_default(),
        help=f"Port to listen on (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--allow-origin",
        default=os.getenv("ALLOW_ORIGIN", "*"),
        help="CORS allowed origin (default: *)",
    )
    return parser.parse_args()


def serve() -> None:
    """Start MCP server."""
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware

    args = parse_args()

    cors_middleware = Middleware(
        CORSMiddleware,
        allow_origins=[args.allow_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(
            transport=args.transport,
            host=args.host,
            port=args.port,
            middleware=[cors_middleware],
        )
