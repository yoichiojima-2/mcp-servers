"""Dify MCP Server."""

from contextlib import asynccontextmanager

from core import parse_args, run_server
from fastmcp import FastMCP

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


@asynccontextmanager
async def app_lifespan():
    """Initialize Dify client for the session."""
    client = DifyClient()
    yield {"client": client}
    await client.close()


mcp = FastMCP("Dify AI Agent Builder", lifespan=app_lifespan)

mcp.add_tool(chat_message)
mcp.add_tool(run_workflow)
mcp.add_tool(get_conversation_messages)
mcp.add_tool(create_dataset)
mcp.add_tool(upload_document_by_text)
mcp.add_tool(list_documents)
mcp.add_tool(import_dsl_workflow)
mcp.add_tool(export_dsl_workflow)
mcp.add_tool(generate_workflow_dsl)


def serve() -> None:
    """Start MCP server."""
    args = parse_args("dify", DEFAULT_PORT)
    run_server(mcp, args)
