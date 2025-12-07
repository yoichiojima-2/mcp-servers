"""Composite MCP Server that combines dify and browser servers."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Get paths to individual servers and add them to Python path
repo_root = Path(__file__).parent.parent.parent.parent
browser_src = repo_root / "browser" / "src"
dify_src = repo_root / "dify" / "src"

# Add to path if not already there
for path in [str(browser_src), str(dify_src)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import tool modules with error handling
try:
    import dify.tools as dify_tools  # noqa: E402
    from dify.tools import DifyClient  # noqa: E402
except ImportError as e:
    raise ImportError(
        f"Failed to import dify server. Ensure dify server is available at {dify_src}. "
        f"Error: {e}"
    ) from e

# Initialize composite FastMCP server
mcp = FastMCP("Composite: Dify + Browser")

# Note: We cannot use @mcp.lifespan() as it's not available in FastMCP 2.13.3
# Dify tools expect ctx.request_context.state.client to be initialized
# Users must ensure DIFY_API_KEY and DIFY_CONSOLE_API_KEY are set in environment
# The client will be initialized on first tool call (lazy initialization in tools)

# Register Dify tools with prefixed names
mcp.tool(name="dify_chat_message")(dify_tools.chat_message)
mcp.tool(name="dify_run_workflow")(dify_tools.run_workflow)
mcp.tool(name="dify_get_conversation_messages")(dify_tools.get_conversation_messages)
mcp.tool(name="dify_create_dataset")(dify_tools.create_dataset)
mcp.tool(name="dify_upload_document_by_text")(dify_tools.upload_document_by_text)
mcp.tool(name="dify_list_documents")(dify_tools.list_documents)
mcp.tool(name="dify_import_dsl_workflow")(dify_tools.import_dsl_workflow)
mcp.tool(name="dify_export_dsl_workflow")(dify_tools.export_dsl_workflow)
mcp.tool(name="dify_generate_workflow_dsl")(dify_tools.generate_workflow_dsl)

# Now import and register browser tools with error handling
try:
    from browser import mcp as browser_mcp  # noqa: E402
except ImportError as e:
    raise ImportError(
        f"Failed to import browser server. Ensure browser server is available at {browser_src}. "
        f"Error: {e}"
    ) from e

# Copy tools from browser MCP instance using the tool manager
# NOTE: This uses private FastMCP APIs (_tool_manager, _tools, _prompt_manager, _prompts)
# This is necessary because FastMCP does not currently provide a public API for
# registering tools from another MCP instance with custom names.
# This may break if FastMCP's internal structure changes.
# TODO: Propose a public API to FastMCP for tool composition
try:
    browser_tool_manager = browser_mcp._tool_manager
    for tool_key, tool_obj in browser_tool_manager._tools.items():
        # Validate tool name before prefixing to avoid double-prefixing
        tool_name = getattr(tool_obj, 'name', tool_key)
        if not tool_name.startswith('browser_'):
            prefixed_name = f"browser_{tool_name}"
        else:
            prefixed_name = tool_name
        # Re-register with prefixed name
        mcp._tool_manager._tools[prefixed_name] = tool_obj
except AttributeError as e:
    raise RuntimeError(
        f"Failed to access browser tools. FastMCP internal structure may have changed. "
        f"Error: {e}"
    ) from e

# Copy prompts from browser MCP instance (if any)
try:
    browser_prompt_manager = browser_mcp._prompt_manager
    if hasattr(browser_prompt_manager, '_prompts'):
        for prompt_key, prompt_obj in browser_prompt_manager._prompts.items():
            prompt_name = getattr(prompt_obj, 'name', prompt_key)
            if not prompt_name.startswith('browser_'):
                prefixed_name = f"browser_{prompt_name}"
            else:
                prefixed_name = prompt_name
            mcp._prompt_manager._prompts[prefixed_name] = prompt_obj
except AttributeError:
    # Browser may not have prompts, which is fine
    pass

# Note: Dify prompts are not registered to avoid circular import issues
# when importing dify.prompts -> dify.server -> mcp.lifespan()
# Users can access dify prompts by running the dify server directly if needed


def serve() -> None:
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
