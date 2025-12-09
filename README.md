# MCP Servers

A collection of Model Context Protocol (MCP) servers for document processing, data operations, and browser automation.

## Overview

This monorepo contains multiple MCP servers built with [FastMCP](https://github.com/jlowin/fastmcp), each specialized for different tasks. All servers follow consistent patterns and can be deployed individually or as a composite server.

**[Live Demo](https://yoichiojima-2.github.io/mcp-servers/)** - See the servers in action

## Available Servers

| Server | Description |
|--------|-------------|
| [browser](src/browser) | Browser automation using Playwright with automatic error handling |
| [composite](src/composite) | Combines multiple MCP servers into a single unified server |
| [dify](src/dify) | AI agent building, workflow management, and knowledge base operations |
| [docx](src/docx) | Word document (.docx) creation, editing, and analysis |
| [langquery](src/langquery) | Natural language querying and processing with LangChain |
| [pdf](src/pdf) | PDF document creation, manipulation, and extraction |
| [pptx](src/pptx) | PowerPoint presentation (.pptx) creation and editing |
| [vectorstore](src/vectorstore) | Vector database operations for semantic search |
| [xlsx](src/xlsx) | Excel spreadsheet (.xlsx) creation, editing, and analysis |

## Project Structure

This repository uses a **Google-style monorepo** with `uv` workspaces:

- **Root `pyproject.toml`**: Contains global dependencies shared across all servers (fastmcp, python-dotenv, uvicorn, pytest, ruff)
- **Server-specific `pyproject.toml`**: Each server in `src/<server>/` declares only its specific dependencies
- **Single `uv.lock`**: Manages all dependencies across the workspace consistently

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for package management

## Installation

Install all dependencies for the entire workspace:

```bash
uv sync --dev
```

For specific servers with additional requirements (like browser automation), see the individual server READMEs.

## Usage

Each server can be run independently:

```bash
cd src/<server>
uv run python -m <server>
```

For example:

```bash
cd src/xlsx
uv run python -m xlsx
```

### Configuration

Most servers support these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `NAME` | Server name | MCP server name |
| `TRANSPORT` | `stdio` | Transport protocol (`stdio` or `sse`) |
| `HOST` | `0.0.0.0` | Server host (for SSE transport) |
| `PORT` | `8000` | Server port (for SSE transport) |
| `ALLOW_ORIGIN` | `*` | CORS allowed origins |

Individual servers may have additional configuration options. See the server-specific READMEs for details.

## Testing

Run tests for a specific server:

```bash
cd src/<server>
uv run pytest -v
```

Or run all tests via GitHub Actions workflow locally:

```bash
# Install GitHub CLI if needed
gh act -j test
```

## Dependency Management

### Adding Dependencies

**Global dependency (shared across all servers):**

```bash
# Edit root pyproject.toml
uv lock
```

**Server-specific dependency:**

```bash
# Edit src/<server>/pyproject.toml
uv lock
```

### Common Commands

```bash
# Install all dependencies
uv sync --dev

# Update dependencies
uv lock --upgrade

# Run a server
cd src/<server> && uv run python -m <server>

# Run tests
cd src/<server> && uv run pytest -v
```

## Development Guidelines

See [CLAUDE.md](CLAUDE.md) for detailed development guidelines including:

- Git workflow with worktrees
- Code principles (minimum, clean, consistent)
- Testing standards
- Documentation requirements
- Commit message conventions

## Architecture

### Individual Servers

Each server is self-contained with:

- `server.py`: Main server implementation
- `tests/`: Test suite
- `pyproject.toml`: Server-specific dependencies
- `README.md`: Documentation with features, tools, and usage

### Composite Server

The [composite server](src/composite) demonstrates how to combine multiple MCP servers into a single unified server with:

- Tool namespacing to avoid conflicts
- Unified lifespan management
- Single MCP connection for multiple capabilities

## Contributing

Contributions are welcome! Please:

1. Follow the development guidelines in [CLAUDE.md](CLAUDE.md)
2. Write tests for new features
3. Update documentation
4. Use conventional commit messages

## License

MIT License - see [LICENSE](LICENSE) for details.

## Resources

- [Live Demo](https://yoichiojima-2.github.io/mcp-servers/)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [uv Package Manager](https://github.com/astral-sh/uv)
