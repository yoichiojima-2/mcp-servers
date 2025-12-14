# File Management MCP Server

MCP server for file read/write operations.

## Features

- Read/write text files
- Read/write binary files (base64 encoded)
- Append to files
- List directory contents
- Path validation to prevent writing to system directories

## Tools

| Tool | Description |
|------|-------------|
| `get_workspace_path` | Get workspace directory path |
| `write_file` | Write text content to a file |
| `write_binary` | Write binary content (base64) to a file |
| `append_file` | Append text content to a file |
| `read_file` | Read text content from a file |
| `read_binary` | Read binary content from a file (base64) |
| `list_directory` | List files in a directory |

## Usage

```bash
# Run standalone
uv run fastmcp run src/file_management/server.py:mcp

# Or enable in composite server
# Set enabled: true in composite-config.yaml
```
