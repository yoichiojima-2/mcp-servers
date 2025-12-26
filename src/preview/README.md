# Preview Server

MCP server for serving HTML content with live reload capabilities. Ideal for reporting, demonstrations, and previewing generated content.

## Features

- **Serve HTML content** - Display HTML pages via URL
- **Live reload** - Auto-refresh browser when content updates
- **Markdown support** - Render markdown with syntax highlighting
- **Report templates** - Generate reports from data
- **Dashboard templates** - Create metric dashboards
- **Screenshot/PDF export** - Capture pages as images or PDFs

## Tools

### Core Tools

| Tool | Description |
|------|-------------|
| `serve_html` | Serve HTML content at a URL |
| `serve_file` | Serve an HTML/markdown file from disk |
| `serve_markdown` | Render and serve markdown content |
| `list_pages` | List all served pages |
| `get_page_url` | Get URL for a specific page |
| `update_page` | Update page content (triggers live reload) |
| `clear_page` | Remove a served page |
| `clear_all_pages` | Remove all pages |
| `open_page` | Open a page in the browser |
| `get_server_status` | Check server status |

### Template Tools

| Tool | Description |
|------|-------------|
| `serve_report` | Generate HTML report from JSON data |
| `serve_dashboard` | Generate dashboard with metric widgets |

### Export Tools (requires playwright)

| Tool | Description |
|------|-------------|
| `screenshot_page` | Take screenshot of a served page |
| `export_pdf` | Export page as PDF |

## Requirements

- Python 3.12+
- Dependencies: starlette, websockets, jinja2, markdown, pygments
- Optional: playwright (for screenshot/PDF export)

## Installation

```bash
# From the repository root
uv sync --package preview

# For screenshot/PDF support
pip install playwright
playwright install chromium
```

## Usage

### Running the Server

```bash
# With stdio transport (default)
uv run python -m preview

# With SSE transport
uv run python -m preview --transport sse --port 8012
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8012 | MCP server port |
| `TRANSPORT` | stdio | Transport protocol |
| `HTTP_PORT` | 3000 | HTTP server port for serving pages |
| `HTTP_HOST` | localhost | HTTP server host |

Screenshots and PDFs are saved to `~/.mcp-servers/workspace/`. Use the `get_workspace_path()` tool to get the path.

### Example Usage

```python
# Serve HTML content
serve_html(
    content="<html><body><h1>Hello World</h1></body></html>",
    name="hello",
    open_browser=True
)
# Returns: "Page 'hello' served at http://localhost:3000/pages/hello"

# Serve markdown
serve_markdown(
    content="# Report\n\n## Summary\n\nThis is a test.",
    name="report"
)

# Generate a report from data
serve_report(
    data='{"Revenue": "$1.2M", "Users": "5,432", "Growth": "+12%"}',
    title="Q4 Metrics",
    name="q4-report",
    open_browser=True
)

# Generate a dashboard
serve_dashboard(
    widgets='[
        {"title": "Active Users", "value": "1,234", "color": "blue"},
        {"title": "Revenue", "value": "$5.6M", "color": "green", "subtitle": "This month"},
        {"title": "Growth", "value": "+15%", "color": "yellow"}
    ]',
    title="Live Dashboard"
)

# Update content (connected browsers auto-refresh)
update_page("hello", "<html><body><h1>Updated!</h1></body></html>")

# Take a screenshot
screenshot_page("q4-report", "q4-report.png")

# Export as PDF
export_pdf("q4-report", "q4-report.pdf")
```

## Live Reload

The server automatically injects a WebSocket client into served HTML. When you call `update_page()`, all browsers viewing that page will automatically refresh.

This is useful for:
- Iterating on reports
- Real-time dashboards
- Demonstration flows

## Claude Desktop Configuration

```json
{
  "mcpServers": {
    "preview": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-servers/src/preview",
        "run",
        "python",
        "-m",
        "preview"
      ]
    }
  }
}
```

## Testing

```bash
cd src/preview
uv run pytest -v
```

## Security Considerations

This server is designed for local development and trusted environments:

- **No HTML sanitization**: Content is served as-is without XSS protection
- **Only serve trusted content**: Do not serve user-generated or untrusted HTML
- **Local use only**: Do not expose the HTTP server to untrusted networks
- **Authentication**: No built-in authentication - consider a reverse proxy for multi-user environments
- **File access via serve_file**:
  - Absolute paths (e.g., `/path/to/file.html`) are allowed without restriction
  - Relative paths are restricted to the current working directory
  - Path traversal via `../` in relative paths is blocked

## Architecture

The server runs two components:

1. **MCP Server** (port 8012) - Handles tool calls via stdio/SSE
2. **HTTP Server** (port 3000) - Serves pages and handles WebSocket connections

The HTTP server starts automatically when the first page is served.
