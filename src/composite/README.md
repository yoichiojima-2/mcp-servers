# composite mcp server

a configurable composite mcp server that combines multiple mcp servers into a single unified server. developers can select which servers to include via yaml configuration.

## features

- **dynamic configuration**: choose which servers to include via yaml config
- **tool namespacing**: all tools are prefixed to avoid naming conflicts
- **lifespan management**: handles initialization and cleanup for servers that need it
- **single connection**: clients only need one mcp connection for multiple capabilities
- **fail-fast validation**: ensures all configured servers load successfully

## available servers

- **dify**: ai agent building, workflow management, knowledge bases (requires api keys)
- **browser**: browser automation using playwright
- **pdf**: pdf manipulation and extraction
- **xlsx**: spreadsheet operations
- **docx**: word document operations
- **pptx**: powerpoint operations
- **vectorstore**: vector database operations (requires openai api key)
- **langquery**: language query operations

## installation

```bash
cd src/composite
uv sync
```

## configuration

create a `composite-config.yaml` file to define which servers to include:

```yaml
servers:
  - name: browser
    module: browser
    prefix: browser
    enabled: true
    has_lifespan: false

  - name: dify
    module: dify
    prefix: dify
    enabled: true
    has_lifespan: true

  - name: pdf
    module: pdf
    prefix: pdf
    enabled: false
```

### configuration file location

the server searches for configuration in this order:
1. path specified in `COMPOSITE_CONFIG_PATH` environment variable
2. `./composite-config.yaml` in current directory
3. `composite-config.yaml` in the package directory

see `composite-config.yaml` for a complete example with all available servers.

### server configuration fields

- `name`: unique identifier for the server
- `module`: python module name to import
- `prefix`: prefix for tool names (e.g., "browser" → "browser_navigate")
- `enabled`: whether to include this server (true/false)
- `has_lifespan`: whether server needs initialization/cleanup (true/false)
- `description`: human-readable description (optional)

## usage

### stdio transport (default)

```bash
uv run python -m composite
```

### sse transport

```bash
TRANSPORT=sse HOST=0.0.0.0 PORT=8000 uv run python -m composite
```

## environment variables

### composite configuration

- `COMPOSITE_CONFIG_PATH`: path to yaml configuration file

### transport configuration

- `TRANSPORT`: transport type (`stdio` or `sse`, default: `stdio`)
- `HOST`: server host (default: `0.0.0.0`)
- `PORT`: server port (default: `8000`)
- `ALLOW_ORIGIN`: cors allowed origins (default: `*`)

### server-specific configuration

configure these based on which servers you enable:

**dify** (requires `has_lifespan: true`):
- `DIFY_API_KEY`: service api key
- `DIFY_BASE_URL`: service api url (default: `https://api.dify.ai/v1`)
- `DIFY_CONSOLE_API_KEY`: console api key
- `DIFY_CONSOLE_BASE_URL`: console api url (default: `https://api.dify.ai`)

**browser**:
- `BROWSER_TIMEOUT`: operation timeout in ms (default: `30000`)
- `NAVIGATION_TIMEOUT`: navigation timeout in ms (default: `60000`)

**vectorstore**:
- `OPENAI_API_KEY`: openai api key for embeddings

see individual server documentation for complete configuration options.

## example configurations

### browser only

```yaml
servers:
  - name: browser
    module: browser
    prefix: browser
    enabled: true
```

### document processing suite

```yaml
servers:
  - name: pdf
    module: pdf
    prefix: pdf
    enabled: true

  - name: docx
    module: docx
    prefix: doc
    enabled: true

  - name: xlsx
    module: xlsx
    prefix: sheet
    enabled: true
```

### ai workflow suite

```yaml
servers:
  - name: dify
    module: dify
    prefix: ai
    enabled: true
    has_lifespan: true

  - name: browser
    module: browser
    prefix: web
    enabled: true

  - name: vectorstore
    module: vectorstore
    prefix: vec
    enabled: true
```

## claude desktop configuration

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
      ],
      "env": {
        "COMPOSITE_CONFIG_PATH": "/path/to/your/composite-config.yaml"
      }
    }
  }
}
```

## architecture

### how it works

1. **configuration loading**: reads yaml config to determine which servers to include
2. **dynamic server loading**: imports server modules and validates them
3. **tool registration**: copies tools from each server with configured prefix
4. **lifespan management**: initializes servers that need it (e.g., dify client)
5. **unified interface**: exposes all tools through single mcp connection

### benefits

- **flexible composition**: choose exactly which capabilities you need
- **clear namespacing**: prefixes prevent tool name conflicts
- **independent development**: each server can be developed and tested separately
- **easy maintenance**: update individual servers without changing composite structure
- **explicit dependencies**: only install what you actually use

## troubleshooting

### error: no configuration file found

create a `composite-config.yaml` file or set `COMPOSITE_CONFIG_PATH` environment variable.

example:
```bash
export COMPOSITE_CONFIG_PATH=/path/to/composite-config.yaml
```

### error: failed to load server

ensure the server's dependencies are installed:
```bash
uv sync
```

### error: duplicate prefixes

each enabled server must have a unique prefix. update your config:
```yaml
servers:
  - name: browser
    prefix: web  # changed from conflicting prefix
    enabled: true
```

### error: server requires lifespan

some servers need initialization. set `has_lifespan: true`:
```yaml
servers:
  - name: dify
    has_lifespan: true  # required for dify
    enabled: true
```

## testing

run tests:
```bash
uv run pytest
```

test specific modules:
```bash
uv run pytest test_config.py
uv run pytest test_loader.py
```
