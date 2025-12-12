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
├── file-management/   # Files created by file-management server
├── nano-banana/       # Generated images
├── preview/           # Screenshots and PDFs
├── shell/             # Files created by shell commands
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
| file-management | `file_management` | 8005 | File read/write operations |
| frontend-design | `frontend_design` | 8006 | Design themes and palettes |
| google-workspace | `google_workspace` | 8015 | Google Workspace (Gmail, Drive, Sheets, Docs, Slides, Calendar) |
| nano-banana | `nano_banana` | 8007 | AI image generation (Gemini) |
| o3 | `o3_search` | 8008 | OpenAI o3 web search |
| pdf | `pdf` | 8009 | PDF extraction and manipulation |
| pptx | `pptx_mcp` | 8010 | PowerPoint operations |
| preview | `preview` | 8011 | HTML preview with live reload |
| shell | `shell` | 8012 | Shell command execution |
| slack | `slack` | 8013 | Slack workspace integration |
| vectorstore | `vectorstore` | 8014 | ChromaDB vector operations |
| xlsx | `xlsx` | 8015 | Excel spreadsheet operations |

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

### Port Renumbering (Slack Integration)

**Breaking change**: Port assignments have been updated to follow alphabetical ordering after adding the `slack` server:

| Server | Old Port | New Port |
|--------|----------|----------|
| slack | (new) | 8013 |
| vectorstore | 8013 | 8014 |
| xlsx | 8014 | 8015 |

If you have existing configurations referencing ports 8013 or 8014, update them to use the new port numbers.

### Workspace Location Change

**Breaking change**: Workspace directories have moved from local `./workspace/` to centralized `~/.mcp-servers/{server}/`.

Old environment variables (`WORKSPACE`, `DATA_ANALYSIS_WORKSPACE`, `BROWSER_WORKSPACE`, `PREVIEW_WORKSPACE`) are no longer supported.

**Migration steps**:

1. Move existing data to the new location:
   ```bash
   # data-analysis
   mkdir -p ~/.mcp-servers/data-analysis
   mv ./workspace/data_analysis_history.db ~/.mcp-servers/data-analysis/history.db

   # browser
   mkdir -p ~/.mcp-servers/browser
   mv ./workspace/*.png ~/.mcp-servers/browser/

   # preview
   mkdir -p ~/.mcp-servers/preview
   mv ./workspace/*.png ~/.mcp-servers/preview/
   mv ./workspace/*.pdf ~/.mcp-servers/preview/
   ```

2. Remove old environment variables from your Claude Desktop config or docker-compose files:
   - Remove `WORKSPACE`
   - Remove `DATA_ANALYSIS_WORKSPACE`
   - Remove `BROWSER_WORKSPACE`
   - Remove `PREVIEW_WORKSPACE`

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
