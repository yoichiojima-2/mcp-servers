# Shell MCP Server

MCP server for shell command execution with allowlist-based security.

## Features

- Execute shell commands via MCP
- Allowlist-based security (only permitted commands can run)
- Configurable timeout
- Shared workspace directory for file output

## Security

This server uses an **allowlist** to restrict which commands can be executed. Set the `ALLOWED_COMMANDS` environment variable to a comma-separated list of permitted base commands.

```bash
# Only allow specific commands
export ALLOWED_COMMANDS="ls,cat,grep,find,git,python,uv"
```

If `ALLOWED_COMMANDS` is not set or empty, **all commands are allowed** (use with caution in production).

## Tools

| Tool | Description |
|------|-------------|
| `get_workspace_path` | Get the workspace directory path for saving files |
| `shell` | Execute a shell command and return output |

## Requirements

- Python 3.12+
- uv

## Running

### Using uv (stdio transport)

```bash
cd src/shell
uv run python -m shell
```

### Using uv (SSE transport)

```bash
cd src/shell
uv run python -m shell --transport sse --port 8015
```

### Using Docker

```bash
cd src/shell
docker compose up
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ALLOWED_COMMANDS` | Comma-separated list of allowed commands | (empty = all allowed) |
| `TRANSPORT` | Transport protocol: `stdio`, `sse` | `stdio` |
| `PORT` | Port for SSE transport | `8015` |

## Claude Desktop Configuration

```json
{
  "mcpServers": {
    "shell": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-servers/src/shell", "run", "python", "-m", "shell"],
      "env": {
        "ALLOWED_COMMANDS": "ls,cat,grep,find,git,python,uv"
      }
    }
  }
}
```

## Testing

```bash
cd src/shell
uv run pytest -v
```
