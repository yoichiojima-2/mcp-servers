"""Dify MCP Server."""

import argparse
import os
import sys
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from .tools import (
    DifyClient,
    chat_message,
    create_dataset,
    export_dsl_workflow,
    generate_workflow_dsl,
    get_conversation_messages,
    import_dsl_workflow,
    list_documents,
    run_workflow,
    upload_document_by_text,
)

DEFAULT_PORT = 8001


# Lifecycle hook to initialize client
@asynccontextmanager
async def app_lifespan():
    """Initialize Dify client for the session."""
    client = DifyClient()
    yield {"client": client}
    await client.close()


# Initialize FastMCP server with lifespan
mcp = FastMCP("Dify AI Agent Builder", lifespan=app_lifespan)


# Register tools
mcp.add_tool(chat_message)
mcp.add_tool(run_workflow)
mcp.add_tool(get_conversation_messages)
mcp.add_tool(create_dataset)
mcp.add_tool(upload_document_by_text)
mcp.add_tool(list_documents)
mcp.add_tool(import_dsl_workflow)
mcp.add_tool(export_dsl_workflow)
mcp.add_tool(generate_workflow_dsl)


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
    parser = argparse.ArgumentParser(description="dify MCP Server")
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
