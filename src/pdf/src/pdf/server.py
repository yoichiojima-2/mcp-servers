import os

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from . import mcp


def serve():
    """start mcp server"""
    cors_middleware = Middleware(
        CORSMiddleware,
        allow_origins=[os.getenv("ALLOW_ORIGIN", "*")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    mcp.run(
        transport=os.getenv("TRANSPORT", "sse"),
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8001)),
        middleware=[cors_middleware],
    )
