# Composite MCP Server

A composite MCP server that combines multiple MCP servers into a single unified server. This example combines the **Dify** and **Browser** servers.

## Features

This composite server provides all tools from:

- **Dify MCP Server**: AI agent building, workflow management, and knowledge base operations
  - Tools prefixed with `dify_*` (e.g., `dify_chat_message`, `dify_import_dsl_workflow`)

- **Browser MCP Server**: Browser automation using Playwright
  - Tools prefixed with `browser_*` (e.g., `browser_navigate`, `browser_click`)

## Architecture

The composite server uses a clean architecture:

1. **Individual servers remain independent**: Each server (`dify`, `browser`) can still be deployed standalone
2. **Tool namespacing**: All tools are prefixed to avoid naming conflicts
3. **Lifespan management**: Properly handles initialization and cleanup from both servers
4. **Shared transport**: All tools available through a single MCP connection

## Installation

```bash
cd src/composite
uv sync
```

## Usage

### stdio transport (default)

```bash
uv run python -m composite
```

### SSE transport

```bash
TRANSPORT=sse HOST=0.0.0.0 PORT=8000 uv run python -m composite
```

## Configuration

Environment variables:

- `TRANSPORT`: Transport type (`stdio` or `sse`, default: `stdio`)
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)
- `ALLOW_ORIGIN`: CORS allowed origins (default: `*`)

### Dify Configuration

- `DIFY_API_KEY`: Service API key for app interactions
- `DIFY_BASE_URL`: Base URL for service API (default: `https://api.dify.ai/v1`)
- `DIFY_CONSOLE_API_KEY`: Console API key for workspace operations
- `DIFY_CONSOLE_BASE_URL`: Base URL for console API (default: `https://api.dify.ai`)

### Browser Configuration

- `BROWSER_TIMEOUT`: Default timeout for browser operations (default: `30000` ms)
- `NAVIGATION_TIMEOUT`: Timeout for page navigation (default: `60000` ms)

## Available Tools

### Dify Tools

- `dify_chat_message`: Send chat messages to Dify agents
- `dify_run_workflow`: Execute Dify workflows
- `dify_get_conversation_messages`: Retrieve conversation history
- `dify_create_dataset`: Create knowledge bases
- `dify_upload_document_by_text`: Upload documents to knowledge bases
- `dify_list_documents`: List documents in a knowledge base
- `dify_import_dsl_workflow`: Import workflow from DSL
- `dify_export_dsl_workflow`: Export workflow as DSL
- `dify_generate_workflow_dsl`: Generate DSL from description

### Browser Tools

- `browser_navigate`: Navigate to a URL
- `browser_click`: Click elements on a page
- `browser_screenshot`: Take screenshots
- `browser_execute`: Execute JavaScript in the browser
- And more browser automation tools...

## Example: Claude Desktop Configuration

```json
{
  "mcpServers": {
    "composite": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-servers/src/composite",
        "run",
        "python",
        "-m",
        "composite"
      ]
    }
  }
}
```

## Extending the Composite Server

To add more servers to the composite:

1. Import the additional MCP server in `server.py`:
   ```python
   from another_server import mcp as another_mcp
   ```

2. Register its tools and prompts with a prefix:
   ```python
   _register_tools_with_prefix(another_mcp, "another", mcp)
   _register_prompts_with_prefix(another_mcp, "another", mcp)
   ```

3. If the server has lifespan hooks, add them to the `lifespan()` function

4. Update the dependencies in `pyproject.toml` if needed

## Architecture Benefits

1. **Single Connection**: Clients only need one MCP connection for multiple capabilities
2. **Independent Development**: Each server can be developed, tested, and deployed independently
3. **Clear Namespacing**: Tool prefixes make it clear which server provides which functionality
4. **Easy Maintenance**: Updates to individual servers don't affect the composite structure
5. **Flexible Deployment**: Deploy as composite or individual servers based on needs
