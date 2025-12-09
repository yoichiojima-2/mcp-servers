# Shell MCP Server

MCP server for executing shell commands.

## Security Warning

This tool executes arbitrary shell commands with full shell capabilities including pipes, redirects, and variable expansion. **Only use with trusted input.**

For untrusted environments, consider implementing additional sandboxing or command whitelisting.

## Features

- Execute shell commands
- Capture stdout and stderr
- Return exit code for programmatic success/failure detection

## Tools

### shell

Execute a shell command and return the output.

**Parameters:**
- `command` (required): Shell command to execute

**Returns:**
- Exit code, stdout, and stderr

## Installation

```bash
cd src/shell
uv sync
```

## Running

```bash
# stdio mode (default)
uv run fastmcp run shell

# SSE mode
TRANSPORT=sse PORT=8011 uv run fastmcp run shell
```

## Testing

```bash
cd src/shell
uv run pytest -v
```
