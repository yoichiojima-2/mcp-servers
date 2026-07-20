# Quick Start

Get started with MCP Servers using the composite server - a single endpoint that combines multiple MCP servers into one.

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

## Setup

### 1. Install dependencies

```bash
git clone https://github.com/yoichiojima-2/mcp-servers.git
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
| img2pptx | `OPENAI_API_KEY` |
| nano-banana | `GEMINI_API_KEY` |
| o3 | `OPENAI_API_KEY` |
| vectorstore | `OPENAI_API_KEY` |
| dify | `DIFY_API_KEY` |

**No API keys needed:** data-analysis, xlsx, pdf, docx, pptx, file-management, frontend-design, browser, preview, shell, skills

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
      "args": ["run", "--directory", "/absolute/path/to/mcp-servers/src/composite", "python", "-m", "composite"],
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
| browser | `browser_` | `browser_navigate` |
| data-analysis | `data_` | `data_query` |
| dify | `dify_` | `dify_chat_message` |
| docx | `docx_` | `docx_unpack` |
| file-management | `file_` | `file_read_file` |
| frontend-design | `design_` | `design_design_list_themes` |
| img2pptx | `img2pptx_` | `img2pptx_image_to_pptx` |
| nano-banana | `img_` | `img_generate_image` |
| o3 | `o3_` | `o3_o3` |
| pdf | `pdf_` | `pdf_extract_text` |
| pptx | `pptx_` | `pptx_extract_text` |
| preview | `preview_` | `preview_serve_html` |
| shell | `shell_` | `shell_shell` |
| skills | `skills_` | `skills_list_skills` |
| vectorstore | `vec_` | `vec_query` |
| xlsx | `xlsx_` | `xlsx_read_excel` |
