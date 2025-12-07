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


# Lifecycle hook to initialize Dify client
@mcp.lifespan
async def lifespan(request_context):
    """Initialize Dify client for the session."""
    client = DifyClient()
    request_context.state.client = client
    yield

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

# Register Dify prompts with prefixed names
# We define these inline to avoid circular import issues with dify.prompts module


@mcp.prompt(name="dify_create_rag_chatbot")
def create_rag_chatbot() -> str:
    """Guide for creating a RAG (Retrieval-Augmented Generation) chatbot in Dify."""
    return """# Creating a RAG Chatbot in Dify

This guide will help you create a chatbot that retrieves information from your knowledge base.

## Step 1: Create a Knowledge Base

Use the `dify_create_dataset` tool to create a new knowledge base:

```
dify_create_dataset(
    name="My Knowledge Base",
    description="Documentation for my product",
    indexing_technique="high_quality"
)
```

## Step 2: Upload Documents

Add documents to your knowledge base using `dify_upload_document_by_text`:

```
dify_upload_document_by_text(
    dataset_id="<dataset-id-from-step-1>",
    name="Product Guide",
    text="<your document content>"
)
```

## Step 3: Generate a RAG Workflow DSL

Create a workflow that uses knowledge retrieval:

```
dify_generate_workflow_dsl(
    description="Answer customer questions about our product using the knowledge base",
    app_type="chatbot",
    enable_knowledge_base=True
)
```

## Step 4: Customize and Import

Take the generated DSL, customize it (update the knowledge base ID in the
knowledge retrieval node), and import it:

```
dify_import_dsl_workflow(
    dsl_content="<customized-yaml-content>",
    name="Product Support Chatbot"
)
```

## Step 5: Test Your Chatbot

Use `dify_chat_message` to test:

```
dify_chat_message(
    query="How do I install the product?",
    user="test-user"
)
```

That's it! You now have a RAG chatbot that can answer questions based on your documents.
"""


@mcp.prompt(name="dify_create_workflow")
def create_workflow() -> str:
    """Guide for creating a data processing workflow in Dify."""
    return """# Creating a Data Processing Workflow in Dify

Build automated workflows for data transformation, analysis, and batch processing.

## Use Cases

- **Translation**: Batch translate documents
- **Summarization**: Generate summaries from multiple sources
- **Data Extraction**: Extract structured data from unstructured text

## Quick Start

1. Generate a basic workflow:
   ```
   dify_generate_workflow_dsl(
       description="Translate text to multiple languages",
       app_type="workflow"
   )
   ```

2. Customize the DSL with your specific logic

3. Import and test:
   ```
   dify_import_dsl_workflow(dsl_content="<your-yaml>")
   ```

4. Execute:
   ```
   dify_run_workflow(
       inputs={"text": "Hello", "target_lang": "es"},
       response_mode="blocking"
   )
   ```

## Best Practices

- Keep workflows focused on single tasks
- Use meaningful variable names
- Test with edge cases
- Document expected input/output formats
"""


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
