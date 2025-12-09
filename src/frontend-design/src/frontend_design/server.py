import os

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from . import mcp


def serve():
    """Start MCP server."""
    cors_middleware = Middleware(
        CORSMiddleware,
        allow_origins=[os.getenv("ALLOW_ORIGIN", "*")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    transport = os.getenv("TRANSPORT", "stdio")

    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(
            transport=transport,
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", 8010)),
            middleware=[cors_middleware],
        )
