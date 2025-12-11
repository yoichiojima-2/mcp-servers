"""HTTP server with live reload for serving pages."""

import asyncio
import os
import threading
from html import escape

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, PlainTextResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket

from .page_store import get_store

# Default HTTP port (separate from MCP port)
DEFAULT_HTTP_PORT = 3000

# Live reload script to inject into HTML
LIVE_RELOAD_SCRIPT = """
<script>
(function() {
  const pageName = window.location.pathname.split('/').pop();
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const ws = new WebSocket(protocol + '//' + window.location.host + '/livereload');
  ws.onmessage = function(e) {
    if (e.data === pageName || e.data === '*') {
      window.location.reload();
    }
  };
  ws.onclose = function() {
    console.log('[preview] Live reload disconnected. Reconnecting in 3s...');
    setTimeout(function() { window.location.reload(); }, 3000);
  };
})();
</script>
"""


def inject_live_reload(html: str) -> str:
    """Inject live reload script into HTML content."""
    # Try to inject before </body>
    if "</body>" in html.lower():
        idx = html.lower().rfind("</body>")
        return html[:idx] + LIVE_RELOAD_SCRIPT + html[idx:]
    # Try to inject before </html>
    if "</html>" in html.lower():
        idx = html.lower().rfind("</html>")
        return html[:idx] + LIVE_RELOAD_SCRIPT + html[idx:]
    # Append at the end
    return html + LIVE_RELOAD_SCRIPT


async def serve_page(request: Request) -> HTMLResponse:
    """Serve a stored page."""
    name = request.path_params["name"]
    store = get_store()
    page = store.get_page(name)

    if page is None:
        return HTMLResponse(
            content=f"<h1>404 - Page Not Found</h1><p>Page '{escape(name)}' does not exist.</p>",
            status_code=404,
        )

    content = page.content

    # Render markdown if needed
    if page.content_type == "markdown":
        from .templates import render_markdown

        content = render_markdown(content, page.title)

    # Inject live reload script
    content = inject_live_reload(content)

    return HTMLResponse(content=content)


async def index(request: Request) -> HTMLResponse:
    """List all available pages."""
    store = get_store()
    pages = store.list_pages()

    if not pages:
        html = """
        <html>
        <head><title>Preview Server</title></head>
        <body>
            <h1>Preview Server</h1>
            <p>No pages available. Use the MCP tools to serve content.</p>
        </body>
        </html>
        """
    else:
        page_list = "\n".join(
            f'<li><a href="/pages/{p.name}">{p.title}</a> '
            f"<small>({p.content_type}, updated {p.updated_at.strftime('%H:%M:%S')})</small></li>"
            for p in pages
        )
        html = f"""
        <html>
        <head><title>Preview Server</title></head>
        <body>
            <h1>Preview Server</h1>
            <h2>Available Pages ({len(pages)})</h2>
            <ul>{page_list}</ul>
        </body>
        </html>
        """

    return HTMLResponse(content=inject_live_reload(html))


async def health(request: Request) -> PlainTextResponse:
    """Health check endpoint."""
    store = get_store()
    return PlainTextResponse(f"ok - {store.page_count()} pages")


async def livereload_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for live reload."""
    await websocket.accept()
    store = get_store()
    store.register_client(websocket)

    try:
        while True:
            # Keep connection alive, wait for messages (ping/pong)
            await websocket.receive_text()
    except Exception:
        # Expected when client disconnects
        pass
    finally:
        store.unregister_client(websocket)


# Create Starlette app with routes
routes = [
    Route("/", index),
    Route("/health", health),
    Route("/pages/{name}", serve_page),
    WebSocketRoute("/livereload", livereload_websocket),
]

app = Starlette(routes=routes)

# Server state
_server_thread: threading.Thread | None = None
_server_started = threading.Event()
_server_start_lock = threading.Lock()
_server_port: int = DEFAULT_HTTP_PORT


def get_http_port() -> int:
    """Get the configured HTTP port."""
    return int(os.getenv("HTTP_PORT", str(DEFAULT_HTTP_PORT)))


def get_base_url() -> str:
    """Get the base URL for the HTTP server."""
    host = os.getenv("HTTP_HOST", "localhost")
    port = get_http_port()
    return f"http://{host}:{port}"


def is_server_running() -> bool:
    """Check if the HTTP server is running."""
    return _server_started.is_set()


def _run_server(port: int) -> None:
    """Run the uvicorn server in a thread."""
    global _server_port
    _server_port = port

    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level="warning",
    )
    server = uvicorn.Server(config)

    # Signal that server is starting
    _server_started.set()

    # Run the server (blocking)
    asyncio.run(server.serve())


def ensure_server_running() -> str:
    """Ensure the HTTP server is running. Returns the base URL."""
    global _server_thread

    if _server_started.is_set():
        return get_base_url()

    with _server_start_lock:
        # Double-check after acquiring lock
        if _server_started.is_set():
            return get_base_url()

        port = get_http_port()

        _server_thread = threading.Thread(
            target=_run_server,
            args=(port,),
            daemon=True,
            name="preview-http-server",
        )
        _server_thread.start()

        # Wait for server to start (with timeout)
        _server_started.wait(timeout=5.0)

    return get_base_url()


async def broadcast_reload(page_name: str) -> int:
    """Broadcast a reload message to all connected clients."""
    store = get_store()
    return await store.broadcast_reload(page_name)
