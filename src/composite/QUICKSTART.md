# Composite Server - Quickstart Guide

Get the composite MCP server running in minutes. This guide is for users who want to quickly start using the server without diving into details.

## Installation

1. **Install dependencies**

   ```bash
   uv sync --dev
   ```

   This installs all required dependencies using the workspace lock file.

2. **Navigate to composite directory**

   ```bash
   cd src/composite
   ```

## Configuration

### 1. Enable/Disable Servers

Edit `composite-config.yaml` to enable the servers you need:

```yaml
servers:
  data-analysis:
    enabled: true    # Set to false to disable
    prefix: data
    module: data_analysis
    description: data querying with DuckDB SQL
```

By default, several servers are enabled. You can enable/disable any server by changing the `enabled` field.

### 2. Set Environment Variables

Some servers require API keys or configuration. Copy the example environment file:

```bash
cp .env.example .env
```

Then edit `.env` and add your credentials:

```bash
# Required if dify server is enabled
DIFY_API_KEY=your_dify_api_key_here
DIFY_BASE_URL=https://api.dify.ai/v1

# Required if vectorstore server is enabled
OPENAI_API_KEY=your_openai_api_key_here

# Optional browser configuration
BROWSER_TIMEOUT=30000
```

**Note**: Only configure environment variables for servers you've enabled in `composite-config.yaml`.

## Running the Server

### Standard Mode (stdio)

For local MCP client integration:

```bash
uv run python -m composite
```

### SSE Transport (HTTP)

For HTTP-based clients or remote connections:

```bash
uv run fastmcp run composite.server:mcp --transport sse --port 8000
```

The server will be available at `http://localhost:8000/sse`.

#### Connect from Dify

Use this configuration in Dify's MCP server settings:

```json
{
  "server_name": {
    "url": "http://host.docker.internal:8000/sse",
    "headers": {},
    "timeout": 50,
    "sse_read_timeout": 50
  }
}
```

#### Connect from other HTTP clients

Send requests to `http://localhost:8000/sse` with proper MCP protocol formatting.

## Verify Installation

Once the server is running, you should see output indicating which servers are mounted:

```
Mounting data-analysis with prefix 'data_'
Mounting pptx with prefix 'pptx_'
...
```

## Common Issues

- **Missing API keys**: If a server fails to start, check that you've added required environment variables in `.env`
- **Port already in use**: Change the port with `--port 8001`
- **Module not found**: Run `uv sync --dev` from the repository root

## Next Steps

- See [README.md](README.md) for detailed server configuration
- Check individual server documentation in `src/<server>/` for specific features
- Review [server guide](../../docs/server-guide.md) for advanced CLI options
