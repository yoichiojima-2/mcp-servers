# Dify MCP Configuration Example

Example configuration for using MCP servers with [Dify](https://dify.ai/).

## Setup

1. Start the MCP servers from the repository root:
   ```bash
   cd /path/to/mcp-servers
   docker compose up -d

   # Or start specific services only:
   docker compose up -d composite data-analysis xlsx
   ```

2. In Dify, navigate to **Tools** > **MCP**

3. Add servers using the SSE endpoints from `dify-mcp-settings.json`

## Configuration

The `dify-mcp-settings.json` file in this directory contains SSE endpoints for all servers:

| Server | Port | Description |
|--------|------|-------------|
| composite | 8000 | All servers aggregated |
| browser | 8001 | Browser automation |
| data-analysis | 8002 | DuckDB SQL queries |
| dify | 8003 | Dify workflow integration |
| docx | 8004 | Word document operations |
| frontend-design | 8005 | Design principles & themes |
| nano-banana | 8006 | AI image generation |
| o3 | 8007 | AI-powered web search |
| pdf | 8008 | PDF operations |
| pptx | 8009 | PowerPoint operations |
| preview | 8010 | HTML preview server |
| vectorstore | 8011 | Vector database |
| xlsx | 8012 | Excel operations |

## Note

When running in Docker, use `host.docker.internal` to connect to the host machine (as shown in the config file).
