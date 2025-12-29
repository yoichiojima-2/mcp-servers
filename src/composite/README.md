# composite

Bundled MCP server that aggregates multiple MCP servers into a single endpoint using FastMCP's `mount()` feature.

## Features

- **Simple Composition**: Use FastMCP's built-in `mount()` to combine servers
- **Tool Namespacing**: Prefixes prevent naming conflicts (e.g., `data_query`)
- **No Proxy Overhead**: Direct in-process communication
- **Single Endpoint**: Clients see one URL with all tools available

## Mounted Servers

| Server | Prefix | Description |
|--------|--------|-------------|
| data-analysis | `data_` | DuckDB SQL data analysis |
| xlsx | `xlsx_` | Excel spreadsheet operations |
| pdf | `pdf_` | PDF document operations |
| docx | `docx_` | Word document operations |
| pptx | `pptx_` | PowerPoint operations |
| vectorstore | `vec_` | Vector database operations |
| browser | `browser_` | Browser automation |
| frontend-design | `design_` | Design themes and palettes |
| dify | `dify_` | Dify AI workflows |
| o3 | `o3_` | OpenAI o3 web search |

## Configuration

Servers are configured via `composite-config.yaml`:

```yaml
servers:
  data-analysis:
    enabled: true
    prefix: data
    module: data_analysis
    description: DuckDB SQL data analysis

  xlsx:
    enabled: false  # disabled
    prefix: xlsx
    module: xlsx
```

| Field | Description |
|-------|-------------|
| `enabled` | Whether to mount the server (default: true) |
| `prefix` | Tool name prefix (e.g., `data_` for data-analysis tools) |
| `module` | Python module name to import |
| `description` | Server description |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `COMPOSITE_CONFIG` | `composite-config.yaml` | Path to config file |

## Usage

```bash
uv run python -m composite
```

### Connect to Dify

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

See [server guide](../../docs/server-guide.md) for common CLI options.

## Requirements

- Python 3.12+
- Dependencies from mounted servers

## Installation

```bash
# From the repository root
uv sync --package composite
```

## Testing

```bash
cd src/composite
uv run pytest -v
```
