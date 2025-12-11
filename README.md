# MCP Servers

A collection of Model Context Protocol (MCP) servers for document processing, data operations, and AI integrations.

## Overview

This monorepo contains multiple MCP servers built with [FastMCP](https://github.com/jlowin/fastmcp), each specialized for different tasks. All servers follow consistent patterns and can be deployed individually or as a composite server.

## Available Servers

| Server | Port | Description |
|--------|------|-------------|
| [composite](src/composite) | 8000 | Combines multiple MCP servers into one |
| [browser](src/browser) | 8001 | Browser automation using Playwright |
| [data-analysis](src/data-analysis) | 8002 | SQL data analysis with DuckDB |
| [dify](src/dify) | 8003 | Dify AI workflow integration |
| [docx](src/docx) | 8004 | Word document operations |
| [file-management](src/file-management) | 8005 | File read/write operations |
| [frontend-design](src/frontend-design) | 8006 | Design themes and color palettes |
| [nano-banana](src/nano-banana) | 8007 | AI image generation with Google Gemini |
| [o3-search](src/o3-search) | 8008 | Deep research with OpenAI o3 |
| [pdf](src/pdf) | 8009 | PDF extraction and manipulation |
| [pptx](src/pptx) | 8010 | PowerPoint operations |
| [preview](src/preview) | 8011 | HTML preview with live reload |
| [shell](src/shell) | 8012 | Shell command execution |
| [vectorstore](src/vectorstore) | 8013 | ChromaDB vector operations |
| [xlsx](src/xlsx) | 8014 | Excel spreadsheet operations |

## Quick Start

### Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for package management

### Installation

```bash
# Install all dependencies
uv sync --dev
```

### Running a Server

```bash
# Using uv (recommended)
uv run python -m <module_name>

# Examples
uv run python -m xlsx                    # Run xlsx server (stdio)
uv run python -m xlsx --transport sse    # Run with SSE transport
```

### Docker (Optional)

```bash
cd src/<server>
docker compose up
```

## CLI Options

All servers support these command-line arguments:

```bash
uv run python -m <module> --help

Options:
  --transport {stdio,sse,streamable-http}  Transport protocol (default: stdio)
  --host HOST                               Host to bind to (default: 0.0.0.0)
  --port PORT                               Port to listen on (server-specific default)
  --allow-origin ORIGIN                     CORS allowed origin (default: *)
```

Environment variables (`TRANSPORT`, `HOST`, `PORT`, `ALLOW_ORIGIN`) can be used instead of CLI arguments.

## Project Structure

```
mcp-servers/
├── src/
│   ├── core/           # Shared CLI utilities
│   ├── browser/        # Individual server packages
│   ├── data-analysis/
│   ├── ...
│   └── composite/      # Aggregates all servers
├── docs/               # Shared documentation
├── pyproject.toml      # Root workspace config
└── uv.lock             # Unified lock file
```

This repository uses a **Google-style monorepo** with `uv` workspaces:

- **Root `pyproject.toml`**: Global dependencies (fastmcp, python-dotenv, pytest, ruff)
- **Server `pyproject.toml`**: Server-specific dependencies
- **Single `uv.lock`**: Consistent versions across all servers

## Testing

```bash
# Run tests for a specific server
cd src/<server>
uv run pytest -v

# Run all tests from root
uv run pytest
```

## Development

See [CLAUDE.md](CLAUDE.md) for development guidelines and [docs/server-guide.md](docs/server-guide.md) for detailed server documentation.

### Adding a New Server

1. Create directory structure under `src/<server-name>/`
2. Add to workspace members in root `pyproject.toml`
3. Add to `.github/workflows/test.yml` if needed
4. Optionally add to `src/composite/composite-config.yaml`

### Linting

```bash
uv run ruff check --fix
uv run ruff format
```

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [uv Package Manager](https://github.com/astral-sh/uv)

## License

MIT License - see [LICENSE](LICENSE) for details.
