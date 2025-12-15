"""MCP tools for the preview server."""

import json
import webbrowser
from pathlib import Path

from core import WORKSPACE, get_workspace, get_workspace_file

from . import mcp
from .http_server import broadcast_reload, ensure_server_running, get_base_url
from .page_store import get_store
from .templates import render_dashboard, render_report


@mcp.tool()
def get_workspace_path() -> str:
    """Get the workspace directory path for saving files.

    Returns:
        Path to ~/.mcp-servers/workspace/ where screenshots, PDFs, and other files are saved.
    """
    return str(get_workspace(WORKSPACE))


@mcp.tool()
def serve_html(
    content: str,
    name: str | None = None,
    title: str | None = None,
    open_browser: bool = False,
) -> str:
    """Serve HTML content at a URL.

    Warning:
        Content is served without sanitization. Only serve trusted HTML content
        to avoid XSS vulnerabilities.

    Args:
        content: HTML content to serve (not sanitized - must be trusted)
        name: Page name for URL (default: auto-generated)
        title: Page title (default: extracted from content or name)
        open_browser: Open the page in default browser

    Returns:
        URL where the page is served
    """
    store = get_store()

    # Generate name if not provided
    if not name:
        name = f"page-{store.page_count() + 1}"

    # Extract title from HTML if not provided
    if not title:
        import re

        match = re.search(r"<title>([^<]+)</title>", content, re.IGNORECASE)
        title = match.group(1) if match else name

    # Ensure HTTP server is running
    base_url = ensure_server_running()

    # Store the page
    store.add_page(name, content, title, content_type="html")

    url = f"{base_url}/pages/{name}"

    if open_browser:
        webbrowser.open(url)

    return f"Page '{name}' served at {url}"


@mcp.tool()
def serve_file(
    path: str,
    name: str | None = None,
    open_browser: bool = False,
) -> str:
    """Serve a file from disk.

    Security note:
        - Absolute paths are allowed (e.g., /path/to/file.html)
        - Relative paths must resolve within the current working directory
        - Path traversal via ../ in relative paths is blocked

    Args:
        path: Path to the HTML file (absolute or relative to cwd)
        name: Page name for URL (default: filename without extension)
        open_browser: Open the page in default browser

    Returns:
        URL where the page is served
    """
    file_path = Path(path).expanduser().resolve()

    # Path traversal protection for relative paths only
    # Absolute paths are allowed since users explicitly specify them
    if not Path(path).is_absolute():
        try:
            file_path.relative_to(Path.cwd())
        except ValueError:
            return f"Error: Path traversal detected: {path}"

    if not file_path.exists():
        return f"Error: File not found: {path}"

    if not file_path.is_file():
        return f"Error: Not a file: {path}"

    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"Error: File encoding not supported (expected UTF-8): {path}"
    except OSError as e:
        return f"Error: Cannot read file '{path}': {e}"

    if not name:
        name = file_path.stem

    # Determine content type from extension
    content_type = "html"
    if file_path.suffix.lower() in (".md", ".markdown"):
        content_type = "markdown"

    store = get_store()
    base_url = ensure_server_running()

    store.add_page(name, content, name, content_type=content_type)

    url = f"{base_url}/pages/{name}"

    if open_browser:
        webbrowser.open(url)

    return f"File '{file_path.name}' served at {url}"


@mcp.tool()
def serve_markdown(
    content: str,
    name: str | None = None,
    title: str | None = None,
    open_browser: bool = False,
) -> str:
    """Serve markdown content rendered as HTML.

    Args:
        content: Markdown content to render and serve
        name: Page name for URL (default: auto-generated)
        title: Page title (default: first heading or name)
        open_browser: Open the page in default browser

    Returns:
        URL where the page is served
    """
    store = get_store()

    # Generate name if not provided
    if not name:
        name = f"md-{store.page_count() + 1}"

    # Extract title from first heading if not provided
    if not title:
        import re

        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = match.group(1) if match else name

    base_url = ensure_server_running()

    # Store as markdown (will be rendered on serve)
    store.add_page(name, content, title, content_type="markdown")

    url = f"{base_url}/pages/{name}"

    if open_browser:
        webbrowser.open(url)

    return f"Markdown page '{name}' served at {url}"


@mcp.tool()
def serve_report(
    data: str,
    title: str = "Report",
    name: str | None = None,
    open_browser: bool = False,
) -> str:
    """Generate and serve an HTML report from data.

    Args:
        data: JSON string of data (dict for metrics, list for table)
        title: Report title
        name: Page name for URL (default: auto-generated)
        open_browser: Open the page in default browser

    Returns:
        URL where the report is served

    Example data formats:
        Metrics: '{"Revenue": "$1.2M", "Users": "5,432", "Growth": "+12%"}'
        Table: '[{"name": "Alice", "score": 95}, {"name": "Bob", "score": 87}]'
    """
    try:
        parsed_data = json.loads(data)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON data - {e}"

    store = get_store()

    if not name:
        name = f"report-{store.page_count() + 1}"

    # Render the report
    html_content = render_report(parsed_data, title=title)

    base_url = ensure_server_running()
    store.add_page(name, html_content, title, content_type="html")

    url = f"{base_url}/pages/{name}"

    if open_browser:
        webbrowser.open(url)

    return f"Report '{name}' served at {url}"


@mcp.tool()
def serve_dashboard(
    widgets: str,
    title: str = "Dashboard",
    name: str | None = None,
    open_browser: bool = False,
) -> str:
    """Generate and serve a dashboard with widgets.

    Args:
        widgets: JSON array of widget definitions
        title: Dashboard title
        name: Page name for URL (default: auto-generated)
        open_browser: Open the page in default browser

    Returns:
        URL where the dashboard is served

    Widget format:
        [
            {"title": "Users", "value": "1,234", "color": "blue"},
            {"title": "Revenue", "value": "$5.6M", "color": "green"},
            {"title": "Growth", "value": "+15%", "subtitle": "vs last month", "color": "yellow"},
            {"title": "Recent Activity", "type": "table", "full": true, "data": [...]}
        ]

    Colors: blue, green, red, yellow
    """
    try:
        widget_list = json.loads(widgets)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON widgets - {e}"

    if not isinstance(widget_list, list):
        return "Error: widgets must be a JSON array"

    store = get_store()

    if not name:
        name = f"dashboard-{store.page_count() + 1}"

    # Render the dashboard
    html_content = render_dashboard(widget_list, title=title)

    base_url = ensure_server_running()
    store.add_page(name, html_content, title, content_type="html")

    url = f"{base_url}/pages/{name}"

    if open_browser:
        webbrowser.open(url)

    return f"Dashboard '{name}' served at {url}"


@mcp.tool()
def list_pages() -> str:
    """List all served pages.

    Returns:
        Formatted list of pages with URLs
    """
    store = get_store()
    pages = store.list_pages()

    if not pages:
        return "No pages currently served."

    base_url = get_base_url()
    result = [f"# Served Pages ({len(pages)})\n"]

    for page in pages:
        url = f"{base_url}/pages/{page.name}"
        updated = page.updated_at.strftime("%H:%M:%S")
        result.append(f"- **{page.title}** (`{page.name}`)")
        result.append(f"  - URL: {url}")
        result.append(f"  - Type: {page.content_type}")
        result.append(f"  - Updated: {updated}")
        result.append("")

    return "\n".join(result)


@mcp.tool()
def get_page_url(name: str) -> str:
    """Get the URL for a specific page.

    Args:
        name: Page name

    Returns:
        Full URL to the page
    """
    store = get_store()
    page = store.get_page(name)

    if not page:
        available = [p.name for p in store.list_pages()]
        if available:
            return f"Error: Page '{name}' not found. Available: {', '.join(available)}"
        return f"Error: Page '{name}' not found. No pages served."

    base_url = get_base_url()
    return f"{base_url}/pages/{name}"


@mcp.tool()
async def update_page(name: str, content: str) -> str:
    """Update a page's content and trigger live reload.

    Warning:
        Content is served without sanitization. Only serve trusted content
        to avoid XSS vulnerabilities.

    Args:
        name: Page name to update
        content: New content (not sanitized - must be trusted)

    Returns:
        Confirmation message
    """
    store = get_store()
    page = store.update_page(name, content)

    if not page:
        return f"Error: Page '{name}' not found."

    # Broadcast reload to connected clients
    notified = await broadcast_reload(name)

    return f"Page '{name}' updated. {notified} client(s) notified to reload."


@mcp.tool()
def clear_page(name: str) -> str:
    """Remove a served page.

    Args:
        name: Page name to remove

    Returns:
        Confirmation message
    """
    store = get_store()

    if store.remove_page(name):
        return f"Page '{name}' removed."
    else:
        return f"Error: Page '{name}' not found."


@mcp.tool()
def clear_all_pages() -> str:
    """Remove all served pages.

    Returns:
        Confirmation message
    """
    store = get_store()
    count = store.clear_all()
    return f"Removed {count} page(s)."


@mcp.tool()
def open_page(name: str) -> str:
    """Open a served page in the default browser.

    Args:
        name: Page name to open

    Returns:
        Confirmation message
    """
    store = get_store()
    page = store.get_page(name)

    if not page:
        return f"Error: Page '{name}' not found."

    base_url = get_base_url()
    url = f"{base_url}/pages/{name}"
    webbrowser.open(url)

    return f"Opened {url} in browser."


@mcp.tool()
def get_server_status() -> str:
    """Get the status of the preview HTTP server.

    Returns:
        Server status information
    """
    from .http_server import is_server_running, get_http_port

    store = get_store()
    pages = store.list_pages()
    clients = len(store.get_clients())

    status = "running" if is_server_running() else "stopped"
    base_url = get_base_url()
    port = get_http_port()

    return f"""# Preview Server Status

- **Status**: {status}
- **URL**: {base_url}
- **Port**: {port}
- **Pages**: {len(pages)}
- **Connected clients**: {clients}
"""


# Browser integration tools (optional, require playwright)


# Default timeout for playwright operations (30 seconds)
PLAYWRIGHT_TIMEOUT = 30000


@mcp.tool()
async def screenshot_page(
    name: str,
    filename: str | None = None,
    full_page: bool = True,
    timeout: int = PLAYWRIGHT_TIMEOUT,
) -> str:
    """Take a screenshot of a served page.

    Requires playwright to be installed: pip install playwright && playwright install chromium

    Args:
        name: Page name to screenshot
        filename: Output filename (default: {name}.png)
        full_page: Capture full scrollable page
        timeout: Timeout in milliseconds (default: 30000)

    Returns:
        Path to saved screenshot
    """
    store = get_store()
    page = store.get_page(name)

    if not page:
        return f"Error: Page '{name}' not found."

    try:
        from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
    except ImportError:
        return "Error: playwright not installed. Run: pip install playwright && playwright install chromium"

    base_url = get_base_url()
    url = f"{base_url}/pages/{name}"

    if not filename:
        filename = f"preview_{name}.png"

    filepath = get_workspace_file(WORKSPACE, filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            browser_page = await browser.new_page()
            browser_page.set_default_timeout(timeout)
            await browser_page.goto(url, wait_until="networkidle")
            await browser_page.screenshot(path=str(filepath), full_page=full_page)
            await browser.close()
    except PlaywrightTimeout:
        return f"Error: Timeout after {timeout}ms while capturing screenshot"
    except Exception as e:
        return f"Error: Failed to capture screenshot: {e}"

    return f"Screenshot saved to {filepath}"


@mcp.tool()
async def export_pdf(
    name: str,
    filename: str | None = None,
    timeout: int = PLAYWRIGHT_TIMEOUT,
) -> str:
    """Export a served page as PDF.

    Requires playwright to be installed: pip install playwright && playwright install chromium

    Args:
        name: Page name to export
        filename: Output filename (default: {name}.pdf)
        timeout: Timeout in milliseconds (default: 30000)

    Returns:
        Path to saved PDF
    """
    store = get_store()
    page = store.get_page(name)

    if not page:
        return f"Error: Page '{name}' not found."

    try:
        from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
    except ImportError:
        return "Error: playwright not installed. Run: pip install playwright && playwright install chromium"

    base_url = get_base_url()
    url = f"{base_url}/pages/{name}"

    if not filename:
        filename = f"preview_{name}.pdf"

    filepath = get_workspace_file(WORKSPACE, filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            browser_page = await browser.new_page()
            browser_page.set_default_timeout(timeout)
            await browser_page.goto(url, wait_until="networkidle")
            await browser_page.pdf(path=str(filepath))
            await browser.close()
    except PlaywrightTimeout:
        return f"Error: Timeout after {timeout}ms while exporting PDF"
    except Exception as e:
        return f"Error: Failed to export PDF: {e}"

    return f"PDF saved to {filepath}"
