# Dify MCP Configuration Example

Example configuration for using MCP servers with [Dify](https://dify.ai/).

## Setup

1. Start the servers with SSE transport. The simplest option is the composite server via Docker:
   ```bash
   cd /path/to/mcp-servers/src/composite
   docker compose up -d
   ```
   Or run any server directly:
   ```bash
   uv run python -m shell --transport sse
   ```

2. In Dify, navigate to **Tools** > **MCP**

3. Add servers using the SSE endpoints from `dify-mcp-settings.json`

## Configuration

`dify-mcp-settings.json` contains SSE endpoints for:

| Server | Port | Description |
|--------|------|-------------|
| composite | 8000 | Enabled servers aggregated behind one endpoint |
| shell | 8013 | Shell command execution |

Each server has a fixed default port (see the Server Reference in [docs/server-guide.md](../../../docs/server-guide.md)), so you can add more entries following the same pattern.

## Note

When Dify runs in Docker, use `host.docker.internal` to reach servers on the host machine (as shown in the config file).
