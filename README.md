# MCP Servers

A monorepo of 17 [Model Context Protocol](https://modelcontextprotocol.io/) servers built with [FastMCP](https://github.com/jlowin/fastmcp), covering browser automation, document processing, data analysis, and AI service integrations. Each server runs standalone or mounted behind a single composite endpoint.

## Servers

| Server | Module | Port | Description |
|--------|--------|------|-------------|
| [composite](src/composite) | `composite` | 8000 | Aggregates the other servers into one endpoint |
| [browser](src/browser) | `browser` | 8001 | Browser automation using Playwright |
| [data-analysis](src/data-analysis) | `data_analysis` | 8002 | SQL data analysis with DuckDB |
| [dify](src/dify) | `dify` | 8003 | Dify AI workflow integration |
| [docx](src/docx) | `docx` | 8004 | Word document operations |
| [file-management](src/file-management) | `file_management` | 8005 | File read/write operations |
| [frontend-design](src/frontend-design) | `frontend_design` | 8006 | Design themes and color palettes |
| [img2pptx](src/img2pptx) | `img2pptx` | 8007 | Image to PPTX conversion via OpenAI vision |
| [nano-banana](src/nano-banana) | `nano_banana` | 8008 | AI image generation with Google Gemini |
| [o3](src/o3) | `o3_search` | 8009 | Deep research with OpenAI o3 web search |
| [pdf](src/pdf) | `pdf` | 8010 | PDF extraction and manipulation |
| [pptx](src/pptx) | `pptx_mcp` | 8011 | PowerPoint operations |
| [preview](src/preview) | `preview` | 8012 | HTML preview with live reload |
| [shell](src/shell) | `shell` | 8013 | Shell command execution with an allowlist |
| [skills](src/skills) | `skills` | 8014 | Claude skills discovery and loading |
| [vectorstore](src/vectorstore) | `vectorstore` | 8015 | ChromaDB vector operations |
| [xlsx](src/xlsx) | `xlsx` | 8016 | Excel spreadsheet operations |

A shared `core` package (`src/core`) provides the CLI argument parsing and transport startup used by every server.

## Quick Start

Requirements: Python 3.12+ and [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/yoichiojima-2/mcp-servers.git
cd mcp-servers
uv sync --all-packages --dev
```

Run any server by its module name (see table above):

```bash
uv run python -m xlsx                    # stdio transport (default)
uv run python -m xlsx --transport sse    # SSE transport
```

All servers accept the same CLI options — `--transport {stdio,sse,streamable-http}`, `--host`, `--port`, `--allow-origin` — or the equivalent `TRANSPORT`, `HOST`, `PORT`, `ALLOW_ORIGIN` environment variables.

Each server also ships a Dockerfile and `docker-compose.yml`:

```bash
cd src/<server>
docker compose up
```

See [docs/quickstart.md](docs/quickstart.md) for Claude Desktop integration and [.env.example](.env.example) for the API keys some servers require.

## Architecture

This is a `uv` workspace monorepo: one root `pyproject.toml` and a single `uv.lock` pin consistent dependency versions across all packages, while each server declares only its own extra dependencies.

The **composite server** implements an aggregator pattern. Driven by [composite-config.yaml](src/composite/composite-config.yaml), it imports each enabled server's FastMCP instance and mounts it under a tool prefix (`browser_navigate`, `data_query`, ...), so a client like Claude Desktop needs a single MCP connection instead of one per server. Servers can be toggled per deployment by flipping `enabled` in the config.

```
mcp-servers/
├── src/
│   ├── core/           # Shared CLI and transport utilities
│   ├── browser/        # Individual server packages
│   ├── data-analysis/
│   ├── ...
│   └── composite/      # Mounts enabled servers behind one endpoint
├── docs/               # Quickstart and server guide
├── examples/           # Claude Desktop / Dify configs, sample output
├── pyproject.toml      # Workspace root
└── uv.lock             # Single lock file for all packages
```

## Testing and CI

Each server has its own test suite under `src/<server>/tests/`. Run them from the server directory:

```bash
cd src/<server>
uv run pytest -v
```

GitHub Actions runs the full matrix — every server's tests plus a lockfile freshness check — on each push and pull request ([.github/workflows/test.yml](.github/workflows/test.yml)).

Lint and format with ruff:

```bash
uv run ruff check --fix
uv run ruff format
```

## Development

See [CLAUDE.md](CLAUDE.md) for contribution guidelines and [docs/server-guide.md](docs/server-guide.md) for detailed per-server reference.

To add a new server: create `src/<server-name>/`, register it in the root `pyproject.toml` workspace members and the CI matrix, and optionally add it to `src/composite/composite-config.yaml`.

## License

MIT — see [LICENSE](LICENSE).
