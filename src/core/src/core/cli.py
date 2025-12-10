"""Shared CLI utilities for MCP servers."""

import argparse
import os
import sys
from typing import Any

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware


def validate_port(value: str) -> int:
    """Validate port is in valid range."""
    try:
        port = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid integer")
    if not (1 <= port <= 65535):
        raise argparse.ArgumentTypeError(f"Port must be between 1 and 65535, got {port}")
    return port


def get_port_default(default_port: int) -> int:
    """Get port from environment variable with validation."""
    port_str = os.getenv("PORT")
    if port_str is None:
        return default_port
    try:
        return int(port_str)
    except ValueError:
        print(f"Error: Invalid PORT environment variable '{port_str}'. Must be an integer.", file=sys.stderr)
        sys.exit(1)


def create_arg_parser(server_name: str, default_port: int) -> argparse.ArgumentParser:
    """Create a standardized argument parser for MCP servers.

    Args:
        server_name: Name of the server (used in help text)
        default_port: Default port number for this server

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(description=f"{server_name} MCP Server")
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
        type=validate_port,
        default=get_port_default(default_port),
        help=f"Port to listen on (default: {default_port})",
    )
    parser.add_argument(
        "--allow-origin",
        default=os.getenv("ALLOW_ORIGIN", "*"),
        help="CORS allowed origin (default: *)",
    )
    return parser


def parse_args(server_name: str, default_port: int) -> argparse.Namespace:
    """Parse command line arguments for an MCP server.

    Args:
        server_name: Name of the server (used in help text)
        default_port: Default port number for this server

    Returns:
        Parsed arguments namespace
    """
    parser = create_arg_parser(server_name, default_port)
    return parser.parse_args()


def run_server(mcp: Any, args: argparse.Namespace) -> None:
    """Run an MCP server with the given configuration.

    Args:
        mcp: FastMCP instance
        args: Parsed command line arguments
    """
    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        cors_middleware = Middleware(
            CORSMiddleware,
            allow_origins=[args.allow_origin],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        mcp.run(
            transport=args.transport,
            host=args.host,
            port=args.port,
            middleware=[cors_middleware],
        )
