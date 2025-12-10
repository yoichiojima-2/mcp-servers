# shell

MCP server for executing shell commands.

## Security Warning

This tool executes arbitrary shell commands with full shell capabilities including pipes, redirects, and variable expansion. **Only use with trusted input.**

## Features

- Execute shell commands
- Capture stdout and stderr
- Return exit code for programmatic success/failure detection

## Tools

| Tool | Description |
|------|-------------|
| `shell` | Execute a shell command and return exit code, stdout, stderr |

## Usage

```bash
uv run python -m shell
```

See [server guide](../../docs/server-guide.md) for common CLI options.
