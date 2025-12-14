# MCP Server Guide

This guide covers common operations for all MCP servers in this monorepo.

## Installation

All servers share the same installation process using `uv`:

```bash
# Install all dependencies
uv sync --dev

# Or install a specific server
uv sync --package <server-name>
```

## Running Servers

### Using uv (Recommended)

```bash
# Run a server with default settings (stdio transport)
uv run python -m <module_name>

# Run with SSE transport
uv run python -m <module_name> --transport sse --port 8000

# Run with environment variables
TRANSPORT=sse PORT=8000 uv run python -m <module_name>
```

### Using Docker (Optional)

```bash
# Build and run with docker-compose
cd src/<server-name>
docker compose up
```

## CLI Arguments

All servers support the following command-line arguments:

| Argument | Default | Description |
|----------|---------|-------------|
| `--transport` | `stdio` | Transport protocol: `stdio`, `sse`, or `streamable-http` |
| `--host` | `0.0.0.0` | Host to bind to |
| `--port` | varies | Port to listen on (server-specific default) |
| `--allow-origin` | `*` | CORS allowed origin |

## Environment Variables

Environment variables can be used instead of CLI arguments:

| Variable | Description |
|----------|-------------|
| `NAME` | Server name (for identification) |
| `TRANSPORT` | Transport protocol |
| `HOST` | Host to bind to |
| `PORT` | Port to listen on |
| `ALLOW_ORIGIN` | CORS allowed origins |

## Workspace Directory

> ⚠️ **Breaking Change**: The workspace location changed from `./workspace/` to `~/.mcp-servers/{server}/`. If you have scripts or applications that reference the old location, update them to use the `get_workspace_path()` tool or directly reference `~/.mcp-servers/{server}/`.

MCP servers store runtime data (databases, caches, screenshots, etc.) in `~/.mcp-servers/`:

```
~/.mcp-servers/
├── browser/           # Browser screenshots
├── data-analysis/     # Query history database, datasets
├── nano-banana/       # Generated images
├── preview/           # Screenshots and PDFs
└── ...
```

Each server has its own subdirectory, created automatically on first use with secure permissions (owner-only access, 0700).

### Discovering the Workspace Path

Each server provides a `get_workspace_path()` tool that returns the workspace directory path. Agents can use this to know where to save files.

### Security Notes

- Workspace directories may contain sensitive data (query history, screenshots, etc.)
- Data persists indefinitely - no automatic cleanup
- Backup `~/.mcp-servers/` if you want to preserve data
- To clean up: `rm -rf ~/.mcp-servers/<server>/`

### Docker Data Persistence

When running servers in Docker, workspace data is stored in named volumes:

```bash
# List workspace volumes
docker volume ls | grep workspace

# Backup a volume
docker run --rm -v browser-workspace:/data -v $(pwd):/backup alpine tar czf /backup/browser-backup.tar.gz -C /data .

# Restore a volume
docker run --rm -v browser-workspace:/data -v $(pwd):/backup alpine tar xzf /backup/browser-backup.tar.gz -C /data

# Remove a volume (deletes all data)
docker volume rm browser-workspace
```

Named volumes persist across container restarts and removals. Data is only deleted when the volume itself is removed.

## Testing

```bash
# Run tests for a specific server
cd src/<server-name>
uv run pytest -v

# Run all tests
uv run pytest
```

## Claude Desktop Configuration

To use a server with Claude Desktop, add it to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "<server-name>": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-servers/src/<server-name>",
        "run",
        "python",
        "-m",
        "<module_name>"
      ],
      "env": {
        "ENV_VAR": "value"
      }
    }
  }
}
```

Replace `<server-name>` and `<module_name>` with the appropriate values from the table below.

## Server Reference

| Server | Module | Port | Description |
|--------|--------|------|-------------|
| browser | `browser` | 8001 | Playwright browser automation |
| composite | `composite` | 8000 | Aggregates multiple MCP servers |
| data-analysis | `data_analysis` | 8002 | DuckDB SQL data analysis |
| dify | `dify` | 8003 | Dify AI workflow integration |
| docx | `docx` | 8004 | Word document operations |
| frontend-design | `frontend_design` | 8005 | Design themes and palettes |
| nano-banana | `nano_banana` | 8006 | AI image generation (Gemini) |
| o3 | `o3_search` | 8007 | OpenAI o3 web search |
| pdf | `pdf` | 8008 | PDF extraction and manipulation |
| pptx | `pptx_mcp` | 8009 | PowerPoint operations |
| preview | `preview` | 8010 | HTML preview with live reload |
| vectorstore | `vectorstore` | 8011 | ChromaDB vector operations |
| xlsx | `xlsx` | 8012 | Excel spreadsheet operations |

## Migration Notes

If upgrading from a previous version, note the following breaking changes:

### Module Renames

| Old Name | New Name | Reason |
|----------|----------|--------|
| `langquery` | `data-analysis` | Name was misleading - uses DuckDB, not LangChain |
| `pptx` (module) | `pptx_mcp` | Avoids circular import with `python-pptx` library |

### Update Claude Desktop Config

If you were using these servers, update your `claude_desktop_config.json`:

**data-analysis** (formerly langquery):
```json
{
  "mcpServers": {
    "data-analysis": {
      "command": "uv",
      "args": ["--directory", "/path/to/src/data-analysis", "run", "python", "-m", "data_analysis"]
    }
  }
}
```

**pptx**:
```json
{
  "mcpServers": {
    "pptx": {
      "command": "uv",
      "args": ["--directory", "/path/to/src/pptx", "run", "python", "-m", "pptx_mcp"]
    }
  }
}
```

### Update docker-compose

If using Docker, update service names and paths accordingly:
- `langquery` service → `data-analysis`
- Environment variables: `LANGQUERY_*` → `DATA_ANALYSIS_*`

### Workspace Location Change

**Breaking change**: All servers now use a shared workspace at `~/.mcp-servers/workspace/`.

Old environment variables (`WORKSPACE`, `DATA_ANALYSIS_WORKSPACE`, `BROWSER_WORKSPACE`, `PREVIEW_WORKSPACE`) are no longer supported.

**Migration steps**:

1. Move existing data to the new shared workspace:
   ```bash
   mkdir -p ~/.mcp-servers/workspace

   # If migrating from local ./workspace directory:
   mv ./workspace/* ~/.mcp-servers/workspace/

   # If migrating from per-server workspaces:
   [ -d ~/.mcp-servers/browser ] && cp -r ~/.mcp-servers/browser/* ~/.mcp-servers/workspace/
   [ -d ~/.mcp-servers/data-analysis ] && cp -r ~/.mcp-servers/data-analysis/* ~/.mcp-servers/workspace/
   [ -d ~/.mcp-servers/preview ] && cp -r ~/.mcp-servers/preview/* ~/.mcp-servers/workspace/
   [ -d ~/.mcp-servers/nano-banana ] && cp -r ~/.mcp-servers/nano-banana/* ~/.mcp-servers/workspace/
   ```

2. Remove old environment variables from your Claude Desktop config or docker-compose files:
   - Remove `WORKSPACE`
   - Remove `DATA_ANALYSIS_WORKSPACE`
   - Remove `BROWSER_WORKSPACE`
   - Remove `PREVIEW_WORKSPACE`

**File naming best practices**: With all servers sharing a workspace, use descriptive filenames to avoid conflicts (e.g., `browser_screenshot.png` instead of `screenshot.png`).

## Troubleshooting

### Port Conflicts

Each server has a unique default port (see Server Reference table above). You can override with:

```bash
# CLI
uv run python -m <module> --port 9000

# Environment variable
PORT=9000 uv run python -m <module>

# docker-compose.yml
services:
  server:
    environment:
      - PORT=9000
    ports:
      - "9000:9000"
```

### Import Errors

If you see circular import errors with pptx, ensure you're using the correct module name:
```bash
# Correct
uv run python -m pptx_mcp

# Wrong (conflicts with python-pptx library)
uv run python -m pptx
```
