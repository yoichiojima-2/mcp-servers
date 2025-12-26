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
| frontend-design | 8006 | Design principles & themes |
| img2pptx | 8007 | Image to PPTX conversion |
| nano-banana | 8008 | AI image generation |
| o3 | 8009 | AI-powered web search |
| pdf | 8010 | PDF operations |
| pptx | 8011 | PowerPoint operations |
| preview | 8012 | HTML preview server |
| shell | 8013 | Shell command execution |
| skills | 8014 | Claude skills discovery |
| vectorstore | 8015 | Vector database |
| xlsx | 8016 | Excel operations |

## Note

When running in Docker, use `host.docker.internal` to connect to the host machine (as shown in the config file).
