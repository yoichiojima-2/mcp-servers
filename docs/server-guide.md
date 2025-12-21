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

> ⚠️ **Breaking Change**: The workspace location changed to a shared directory at `~/.mcp-servers/workspace/`. If you have scripts or applications that reference old per-server locations, update them to use the `get_workspace_path()` tool or directly reference `~/.mcp-servers/workspace/`.

All MCP servers share a single workspace directory at `~/.mcp-servers/workspace/`:

```
~/.mcp-servers/
└── workspace/                      # Shared workspace for all servers
    ├── data_analysis_history.db    # Query history database
    ├── browser_screenshot.png      # Browser screenshots
    ├── datasets/                   # Downloaded datasets
    │   └── titanic.csv
    └── ...
```

The shared workspace enables inter-server file sharing and is created automatically on first use with secure permissions (owner-only access, 0700).

### Discovering the Workspace Path

Each server provides a `get_workspace_path()` tool that returns the workspace directory path. Agents can use this to know where to save files.

### Security Notes

- Workspace directories may contain sensitive data (query history, screenshots, etc.)
- Data persists indefinitely - no automatic cleanup
- Backup `~/.mcp-servers/` if you want to preserve data
- To clean up: `rm -rf ~/.mcp-servers/<server>/`

### Docker Data Persistence

When running servers in Docker, workspace data is stored in named volumes.

> ⚠️ **Docker Volume Limitation**: The shared workspace only works when running via the composite server. Running individual servers creates separate volumes that do NOT share data:

```bash
# Composite mode (recommended) - all servers share one volume
cd src/composite && docker compose up
# Creates: composite_mcp-workspace (shared by all servers)

# Individual mode - each server gets its own volume (NOT shared)
cd src/browser && docker compose up   # Creates: browser_mcp-workspace
cd src/preview && docker compose up   # Creates: preview_mcp-workspace (separate!)
```

To share data between individually-run servers, use an external volume:

```bash
# Create a shared external volume
docker volume create mcp-workspace

# Then update docker-compose.yml to use external volume:
# volumes:
#   mcp-workspace:
#     external: true
```

Volume management commands:

```bash
# List workspace volumes
docker volume ls | grep workspace

# Backup a volume
docker run --rm -v mcp-workspace:/data -v $(pwd):/backup alpine tar czf /backup/workspace-backup.tar.gz -C /data .

# Restore a volume
docker run --rm -v mcp-workspace:/data -v $(pwd):/backup alpine tar xzf /backup/workspace-backup.tar.gz -C /data

# Remove a volume (deletes all data)
docker volume rm mcp-workspace
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
| frontend-design | `frontend_design` | 8006 | Design themes and palettes |
| img2pptx | `img2pptx` | 8007 | Image to PPTX conversion (GPT-5.2) |
| nano-banana | `nano_banana` | 8008 | AI image generation (Gemini) |
| o3 | `o3_search` | 8009 | OpenAI o3 web search |
| pdf | `pdf` | 8010 | PDF extraction and manipulation |
| pptx | `pptx_mcp` | 8011 | PowerPoint operations |
| preview | `preview` | 8012 | HTML preview with live reload |
| shell | `shell` | 8013 | Shell command execution |
| skills | `skills` | 8005 | Claude skills discovery and loading |
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
   for dir in browser data-analysis preview nano-banana; do
       if [ -d ~/.mcp-servers/$dir ]; then
           echo "Checking ~/.mcp-servers/$dir..."
           count=0
           skipped=0
           for file in ~/.mcp-servers/$dir/*; do
               [ -e "$file" ] || continue
               base=$(basename "$file")
               if [ -e ~/.mcp-servers/workspace/"$base" ]; then
                   echo "  Skipped: $base (already exists)"
                   skipped=$((skipped + 1))
               else
                   mv "$file" ~/.mcp-servers/workspace/
                   echo "  Migrated: $base"
                   count=$((count + 1))
               fi
           done
           echo "  Summary: $count migrated, $skipped skipped"
       fi
   done
   ```

   **Important**: The `data-analysis` server stores query history in `data_analysis_history.db`. If you have existing query history you want to preserve:
   ```bash
   # Migrate data-analysis history database (check for conflicts first)
   if [ -f ~/.mcp-servers/data-analysis/history.db ]; then
       if [ -f ~/.mcp-servers/workspace/data_analysis_history.db ]; then
           echo "Warning: data_analysis_history.db already exists, skipping migration"
       else
           mv ~/.mcp-servers/data-analysis/history.db ~/.mcp-servers/workspace/data_analysis_history.db
           echo "Migrated history.db to data_analysis_history.db"
       fi
   fi
   ```

2. Remove old environment variables from your Claude Desktop config or docker-compose files:
   - Remove `WORKSPACE`
   - Remove `DATA_ANALYSIS_WORKSPACE`
   - Remove `BROWSER_WORKSPACE`
   - Remove `PREVIEW_WORKSPACE`

3. (Optional) Download sample datasets for testing:
   ```bash
   ./scripts/download-sample-data.sh
   ```

**File naming best practices**: With all servers sharing a workspace, use descriptive filenames to avoid conflicts:
- Use server prefixes: `browser_screenshot.png`, `preview_export.pdf`
- Use timestamps: `screenshot_20240101_120000.png`
- Avoid generic names like `output.png` or `data.csv`

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
