"""Composite MCP Server that combines dify and browser servers."""

import os
import sys
from pathlib import Path

from fastmcp import FastMCP, Context
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Get paths to individual servers and add them to Python path
repo_root = Path(__file__).parent.parent.parent.parent
browser_src = repo_root / "browser" / "src"
dify_src = repo_root / "dify" / "src"

# Add to path if not already there
for path in [str(browser_src), str(dify_src)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import tool modules
import dify.tools as dify_tools  # noqa: E402
from dify.tools import DifyClient  # noqa: E402

# Initialize composite FastMCP server
mcp = FastMCP("Composite: Dify + Browser")


# Initialize Dify client on startup - FastMCP will manage the context
@mcp.tool()
async def _init_dify(ctx: Context) -> str:
    """Internal tool to initialize Dify client (not meant to be called directly)."""
    if not hasattr(ctx.request_context.state, "client"):
        ctx.request_context.state.client = DifyClient()
    return "Dify client initialized"


# Register Dify tools with prefixed names
# Note: These tools expect ctx.request_context.state.client to exist
# Users should ensure DIFY_API_KEY and DIFY_CONSOLE_API_KEY are set
mcp.tool(name="dify_chat_message")(dify_tools.chat_message)
mcp.tool(name="dify_run_workflow")(dify_tools.run_workflow)
mcp.tool(name="dify_get_conversation_messages")(dify_tools.get_conversation_messages)
mcp.tool(name="dify_create_dataset")(dify_tools.create_dataset)
mcp.tool(name="dify_upload_document_by_text")(dify_tools.upload_document_by_text)
mcp.tool(name="dify_list_documents")(dify_tools.list_documents)
mcp.tool(name="dify_import_dsl_workflow")(dify_tools.import_dsl_workflow)
mcp.tool(name="dify_export_dsl_workflow")(dify_tools.export_dsl_workflow)
mcp.tool(name="dify_generate_workflow_dsl")(dify_tools.generate_workflow_dsl)

# Now import and register browser tools
# Browser tools are registered via decorators, so we need to access the registered MCP instance
from browser import mcp as browser_mcp  # noqa: E402

# Copy tools from browser MCP instance using the tool manager
browser_tool_manager = browser_mcp._tool_manager
for tool_key, tool_obj in browser_tool_manager._tools.items():
    prefixed_name = f"browser_{tool_obj.name}"
    # Re-register with prefixed name
    mcp._tool_manager._tools[prefixed_name] = tool_obj

# Copy prompts from browser MCP instance (if any)
browser_prompt_manager = browser_mcp._prompt_manager
if hasattr(browser_prompt_manager, '_prompts'):
    for prompt_key, prompt_obj in browser_prompt_manager._prompts.items():
        prefixed_name = f"browser_{prompt_obj.name}"
        mcp._prompt_manager._prompts[prefixed_name] = prompt_obj


def serve():
    """Start the composite MCP server."""
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
            port=int(os.getenv("PORT", 8000)),
            middleware=[cors_middleware],
        )
