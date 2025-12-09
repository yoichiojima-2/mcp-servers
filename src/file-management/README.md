# File Management MCP Server

MCP server for file read/write operations. Useful when shell input limits prevent writing large content (e.g., HTML exports from EDA tools).

## Features

- Read/write text files of any size
- Read/write binary files (base64 encoded)
- Append content to existing files
- List directory contents with glob patterns
- Automatic parent directory creation
- Security validation (prevents writes to system directories)

## Tools

### read_file

Read text content from a file.

**Parameters:**
- `file_path` (required): Path to the file (supports `~` expansion)
- `encoding` (optional): Character encoding (default: utf-8)

### read_binary

Read binary content from a file, returned as base64.

**Parameters:**
- `file_path` (required): Path to the file (supports `~` expansion)

### write_file

Write text content to a file.

**Parameters:**
- `file_path` (required): Path to the file (supports `~` expansion)
- `content` (required): Text content to write
- `encoding` (optional): Character encoding (default: utf-8)

### write_binary

Write binary content (base64 encoded) to a file.

**Parameters:**
- `file_path` (required): Path to the file (supports `~` expansion)
- `content_base64` (required): Base64-encoded binary content

### append_file

Append text content to a file. Creates the file if it doesn't exist.

**Parameters:**
- `file_path` (required): Path to the file (supports `~` expansion)
- `content` (required): Text content to append
- `encoding` (optional): Character encoding (default: utf-8)

### list_directory

List files in a directory with optional glob pattern.

**Parameters:**
- `dir_path` (required): Path to the directory (supports `~` expansion)
- `pattern` (optional): Glob pattern to filter files (default: *)

## Installation

```bash
cd src/file-management
uv sync
```

## Running

```bash
# stdio mode (default)
uv run fastmcp run file_management

# SSE mode
TRANSPORT=sse PORT=8010 uv run fastmcp run file_management
```

## Testing

```bash
cd src/file-management
uv run pytest -v
```
