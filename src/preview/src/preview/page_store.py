"""In-memory page storage with WebSocket client tracking for live reload."""

import asyncio
import threading
from dataclasses import dataclass, field
from datetime import datetime

from starlette.websockets import WebSocket, WebSocketDisconnect

# Maximum number of concurrent WebSocket connections
MAX_WEBSOCKET_CLIENTS = 100


@dataclass
class Page:
    """A stored page with metadata."""

    name: str
    content: str
    title: str
    content_type: str  # "html" | "markdown"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class PageStore:
    """Thread-safe in-memory storage for pages with WebSocket broadcasting."""

    def __init__(self) -> None:
        self._pages: dict[str, Page] = {}
        self._websocket_clients: set[WebSocket] = set()
        self._lock = threading.Lock()

    def add_page(
        self,
        name: str,
        content: str,
        title: str = "",
        content_type: str = "html",
    ) -> Page:
        """Add or update a page."""
        with self._lock:
            now = datetime.now()
            if name in self._pages:
                page = self._pages[name]
                page.content = content
                page.title = title or page.title
                page.content_type = content_type
                page.updated_at = now
            else:
                page = Page(
                    name=name,
                    content=content,
                    title=title or name,
                    content_type=content_type,
                    created_at=now,
                    updated_at=now,
                )
                self._pages[name] = page
            return page

    def update_page(self, name: str, content: str) -> Page | None:
        """Update page content and trigger reload broadcast."""
        with self._lock:
            if name not in self._pages:
                return None
            page = self._pages[name]
            page.content = content
            page.updated_at = datetime.now()
            return page

    def get_page(self, name: str) -> Page | None:
        """Get a page by name."""
        with self._lock:
            return self._pages.get(name)

    def remove_page(self, name: str) -> bool:
        """Remove a page. Returns True if page existed."""
        with self._lock:
            if name in self._pages:
                del self._pages[name]
                return True
            return False

    def clear_all(self) -> int:
        """Remove all pages. Returns count of removed pages."""
        with self._lock:
            count = len(self._pages)
            self._pages.clear()
            return count

    def list_pages(self) -> list[Page]:
        """List all pages sorted by updated_at descending."""
        with self._lock:
            return sorted(
                self._pages.values(),
                key=lambda p: p.updated_at,
                reverse=True,
            )

    def page_count(self) -> int:
        """Get the number of stored pages."""
        with self._lock:
            return len(self._pages)

    def register_client(self, websocket: WebSocket) -> bool:
        """Register a WebSocket client for live reload.

        Returns True if registered, False if limit reached.
        """
        with self._lock:
            if len(self._websocket_clients) >= MAX_WEBSOCKET_CLIENTS:
                return False
            self._websocket_clients.add(websocket)
            return True

    def unregister_client(self, websocket: WebSocket) -> None:
        """Unregister a WebSocket client."""
        with self._lock:
            self._websocket_clients.discard(websocket)

    def get_clients(self) -> set[WebSocket]:
        """Get a copy of current WebSocket clients."""
        with self._lock:
            return self._websocket_clients.copy()

    async def _notify_client(self, client: WebSocket, page_name: str) -> bool:
        """Notify a single client. Returns True if successful."""
        try:
            await client.send_text(page_name)
            return True
        except WebSocketDisconnect:
            # Client disconnected normally
            self.unregister_client(client)
            return False
        except Exception:
            # Other connection errors (network issues, etc.)
            self.unregister_client(client)
            return False

    async def broadcast_reload(self, page_name: str) -> int:
        """Broadcast reload message to all connected clients concurrently.

        Returns the number of clients notified.
        """
        clients = self.get_clients()
        if not clients:
            return 0

        # Notify all clients concurrently
        tasks = [self._notify_client(client, page_name) for client in clients]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successful notifications (True results, not exceptions)
        return sum(1 for r in results if r is True)


# Global singleton instance
_store: PageStore | None = None
_store_lock = threading.Lock()


def get_store() -> PageStore:
    """Get the global PageStore singleton."""
    global _store
    with _store_lock:
        if _store is None:
            _store = PageStore()
        return _store
