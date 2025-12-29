# File Management MCP Server

MCP server for file read/write operations.

## Requirements

- Python 3.12+

## Features

- Read/write text files
- Read/write binary files (base64 encoded)
- Append to files
- Delete files
- List directory contents
- Path validation to prevent writing to system directories
- File size limits (100MB max for read operations)
- Cross-platform support (Unix and Windows)

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
| `delete_file` | Delete a file |

## Installation

```bash
# From the repository root
uv sync --package file-management
```

## Usage

```bash
uv run python -m file_management
```

See [server guide](../../docs/server-guide.md) for common CLI options.

## Testing

```bash
cd src/file-management
uv run pytest -v
```
