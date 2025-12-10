import argparse
import os

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from . import mcp

DEFAULT_PORT = 8003


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="pptx MCP Server")
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
        type=int,
        default=int(os.getenv("PORT", DEFAULT_PORT)),
        help=f"Port to listen on (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--allow-origin",
        default=os.getenv("ALLOW_ORIGIN", "*"),
        help="CORS allowed origin (default: *)",
    )
    return parser.parse_args()


def serve():
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
