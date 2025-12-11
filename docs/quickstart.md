# Quick Start

Get started with MCP Servers using the composite server - a single endpoint that combines multiple MCP servers into one.

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

## Setup

### 1. Install dependencies

```bash
git clone <repository-url>
cd mcp-servers
uv sync --dev
```

### 2. Configure which servers to enable

Edit `src/composite/composite-config.yaml`:

```yaml
servers:
  data-analysis:
    enabled: true      # Enable this server
    prefix: data
    module: data_analysis

  xlsx:
    enabled: false     # Disable this server
    prefix: xlsx
    module: xlsx
```

### 3. Set environment variables (if needed)

Some servers require API keys. Add them to your Claude Desktop config (see below) or export in terminal.

| Server | Required Variable |
|--------|-------------------|
| nano-banana | `GEMINI_API_KEY` |
| o3-search | `OPENAI_API_KEY` |
| vectorstore | `OPENAI_API_KEY` |
| dify | `DIFY_API_KEY` |

**No API keys needed:** data-analysis, xlsx, pdf, docx, pptx, file-management, shell, frontend-design, browser

### 4. Run the server

```bash
cd src/composite
uv run python -m composite
```

Default is stdio mode (for Claude Desktop). For SSE transport:

```bash
uv run python -m composite --transport sse --port 8000
```

## Claude Desktop Integration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-servers": {
      "command": "uv",
      "args": ["run", "python", "-m", "composite"],
      "cwd": "/path/to/mcp-servers/src/composite",
      "env": {
        "GEMINI_API_KEY": "your-key",
        "OPENAI_API_KEY": "your-key"
      }
    }
  }
}
```

## Docker (Alternative)

```bash
cd src/composite
docker compose up -d
```

The server will be available at `http://localhost:8000/sse`.

## Tool Prefixes

Each server's tools are namespaced with a prefix:

| Server | Prefix | Example |
|--------|--------|---------|
| data-analysis | `data_` | `data_query` |
| xlsx | `xlsx_` | `xlsx_read` |
| pdf | `pdf_` | `pdf_extract` |
| pptx | `pptx_` | `pptx_create` |
| file-management | `file_` | `file_read` |
| shell | `sh_` | `sh_execute` |
| nano-banana | `img_` | `img_generate` |
| o3-search | `o3_` | `o3_search` |
