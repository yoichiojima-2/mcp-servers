# mcp composite server

a bundled mcp server that aggregates multiple mcp servers into a single endpoint using fastmcp's `mount()` feature.

## features

- **simple composition**: use fastmcp's built-in `mount()` to combine servers
- **tool namespacing**: prefixes prevent naming conflicts (e.g., `lang_query`)
- **no proxy overhead**: direct in-process communication
- **single endpoint**: clients see one url with all tools available

## installation

```bash
cd src/composite
uv sync
```

## usage

### standalone

```bash
# stdio transport (default)
cd src/composite
uv run python -m composite

# sse transport for web clients
TRANSPORT=sse PORT=8000 uv run python -m composite
```

### connect to dify

in dify mcp configuration:
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

## configuration

### environment variables

- `NAME`: server name (default: "composite")
- `TRANSPORT`: "stdio" or "sse" (default: "stdio")
- `HOST`: server host for sse (default: "0.0.0.0")
- `PORT`: server port for sse (default: 8000)
- `ALLOW_ORIGIN`: cors origin (default: "*")
- `COMPOSITE_CONFIG`: path to config file (default: `composite-config.yaml`)

### server configuration

copy the example config to create your own:

```bash
cp composite-config.example.yaml composite-config.yaml
```

servers are configured via `composite-config.yaml`. enable/disable servers by setting `enabled: true/false`:

```yaml
servers:
  langquery:
    enabled: true
    prefix: lang
    module: langquery
    description: data querying and shell commands

  xlsx:
    enabled: false  # disabled
    prefix: xlsx
    module: xlsx
    description: excel spreadsheet operations
```

each server entry supports:
- `enabled`: whether to mount the server (default: true)
- `prefix`: tool name prefix (e.g., `lang_` for langquery tools)
- `module`: python module name to import
- `description`: server description

## mounted servers

currently mounts the following servers with prefixes:

| server | prefix | description |
|--------|--------|-------------|
| langquery | `lang_` | data querying and shell commands |
| xlsx | `xlsx_` | excel spreadsheet operations |
| pdf | `pdf_` | pdf document operations |
| docx | `docx_` | word document operations |
| pptx | `pptx_` | powerpoint operations |
| vectorstore | `vec_` | vector database operations |
| browser | `browser_` | browser automation |

## testing

```bash
cd src/composite
uv run pytest -v
```

## development

key files:
- `src/composite/server.py`: main server with dynamic mount logic
- `composite-config.example.yaml`: example server configuration
- `composite-config.yaml`: your local server configuration (gitignored)
