"""Dify MCP Server."""

import os
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
            port=int(os.getenv("PORT", 8006)),
            middleware=[cors_middleware],
        )
