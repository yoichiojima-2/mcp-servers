import os

from . import mcp


def serve():
    """start mcp server"""
    mcp.run(
        transport=os.getenv("TRANSPORT", "stdio"),
    )
