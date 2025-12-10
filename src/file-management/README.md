# file-management

MCP server for file read/write operations. Useful when shell input limits prevent writing large content (e.g., HTML exports from EDA tools).

## Features

- Read/write text files of any size
- Read/write binary files (base64 encoded)
- Append content to existing files
- List directory contents with glob patterns
- Automatic parent directory creation
- Security validation (prevents writes to system directories)

## Tools

| Tool | Description |
|------|-------------|
| `read_file` | Read text content from a file |
| `read_binary` | Read binary content as base64 |
| `write_file` | Write text content to a file |
| `write_binary` | Write binary content (base64 encoded) |
| `append_file` | Append text to a file |
| `list_directory` | List files with optional glob pattern |

## Usage

```bash
uv run python -m file_management
```

See [server guide](../../docs/server-guide.md) for common CLI options.
