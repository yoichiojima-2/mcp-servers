import asyncio
import base64
import os
import threading
from contextlib import asynccontextmanager
from functools import wraps
from typing import Optional

from playwright.async_api import Browser, Page, TimeoutError, async_playwright

from . import mcp

# Global browser state
_browser: Optional[Browser] = None
_page: Optional[Page] = None
_playwright = None
_page_lock: Optional[asyncio.Lock] = None  # Lock to prevent concurrent page access
_browser_lock: Optional[asyncio.Lock] = None  # Lock for browser initialization

# Thread lock to protect lock initialization (prevents race conditions during lock creation)
_lock_init_mutex = threading.Lock()

# Configuration
DEFAULT_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30000"))  # 30 seconds
DEFAULT_NAVIGATION_TIMEOUT = int(os.getenv("NAVIGATION_TIMEOUT", "60000"))  # 60 seconds

# Timeout constants for internal operations (configurable via environment variables)
HEALTH_CHECK_TIMEOUT = float(os.getenv("HEALTH_CHECK_TIMEOUT", "5.0"))  # Timeout for page health checks
CONTENT_EVAL_TIMEOUT = float(os.getenv("CONTENT_EVAL_TIMEOUT", "10.0"))  # Timeout for content evaluation
SCRIPT_EVAL_TIMEOUT = float(os.getenv("SCRIPT_EVAL_TIMEOUT", "30.0"))  # Timeout for JavaScript evaluation


def _ensure_lock(lock_name: str) -> asyncio.Lock:
    """Ensure a lock exists for the current event loop.

    This function is thread-safe and ensures the same lock instance is returned
    for each lock name within the same event loop.

    Args:
        lock_name: Either "_page_lock" or "_browser_lock"

    Returns:
        The lock instance for the current event loop
    """
    global _page_lock, _browser_lock, _lock_init_mutex

    # Use thread lock to prevent race conditions during lock creation
    with _lock_init_mutex:
        # Get the current lock value inside the mutex to avoid race conditions
        current_lock = _page_lock if lock_name == "_page_lock" else _browser_lock

        try:
            loop = asyncio.get_running_loop()
            # Check if we need to create a new lock
            if current_lock is None or (hasattr(current_lock, "_loop") and current_lock._loop is not loop):
                # Create new lock for this event loop
                new_lock = asyncio.Lock()
                # Update the global variable
                if lock_name == "_page_lock":
                    _page_lock = new_lock
                else:
                    _browser_lock = new_lock
                return new_lock
            return current_lock
        except RuntimeError:
            # No event loop running - shouldn't happen in async context
            if current_lock is None:
                new_lock = asyncio.Lock()
                if lock_name == "_page_lock":
                    _page_lock = new_lock
                else:
                    _browser_lock = new_lock
                return new_lock
            return current_lock


def handle_browser_errors(func):
    """Decorator to handle browser errors and auto-recover.

    Acquires _page_lock to ensure thread-safe access to page operations.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        page_lock = _ensure_lock("_page_lock")
        async with page_lock:
            try:
                return await func(*args, **kwargs)
            except TimeoutError as e:
                return f"Error: Operation timed out - {str(e)}"
            except Exception as e:
                error_msg = f"Error: {type(e).__name__} - {str(e)}"
                # Attempt recovery with more aggressive cleanup
                try:
                    await _reset_page_unsafe()
                    return f"{error_msg}\nPage has been reset. Ready for next operation."
                except Exception as reset_error:
                    # If page reset fails, try to close browser entirely
                    try:
                        global _browser, _page, _playwright
                        if _page:
                            try:
                                await _page.close()
                            except Exception:
                                pass
                        _page = None
                        if _browser:
                            try:
                                await _browser.close()
                            except Exception:
                                pass
                        _browser = None
                        if _playwright:
                            try:
                                await _playwright.stop()
                            except Exception:
                                pass
                        _playwright = None
                        return f"{error_msg}\nPage reset failed. Browser has been closed. Will reinitialize on next operation."
                    except Exception as cleanup_error:
                        return f"{error_msg}\nRecovery failed: {str(reset_error)}\nCleanup failed: {str(cleanup_error)}"

    return wrapper


async def _reset_page_unsafe():
    """Reset the page if it's in a bad state. MUST be called with _page_lock held."""
    global _page
    try:
        if _page and not _page.is_closed():
            await _page.close()
    except Exception:
        pass
    finally:
        _page = None


async def _reset_page():
    """Reset the page if it's in a bad state. Thread-safe version."""
    page_lock = _ensure_lock("_page_lock")
    async with page_lock:
        await _reset_page_unsafe()


async def _is_page_healthy_unsafe() -> bool:
    """Check if the page is in a healthy state. MUST be called with _page_lock held."""
    global _page
    if _page is None or _page.is_closed():
        return False
    try:
        # Try to evaluate a simple script to check if page is responsive
        # Add a timeout to prevent hanging
        await asyncio.wait_for(_page.evaluate("1 + 1"), timeout=HEALTH_CHECK_TIMEOUT)
        return True
    except (asyncio.TimeoutError, Exception):
        return False


@asynccontextmanager
async def get_browser():
    """Get or create browser instance."""
    global _browser, _playwright
    browser_lock = _ensure_lock("_browser_lock")
    async with browser_lock:
        if _browser is None:
            try:
                _playwright = await async_playwright().start()
                # Build browser args list
                browser_args = [
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-extensions",
                ]
                if os.getenv("NO_SANDBOX", "false").lower() == "true":
                    browser_args.append("--no-sandbox")

                _browser = await _playwright.chromium.launch(
                    headless=os.getenv("HEADLESS", "false").lower() == "true",
                    args=browser_args,
                )
            except Exception as e:
                if _playwright:
                    try:
                        await _playwright.stop()
                    except Exception:
                        pass
                    _playwright = None
                raise Exception(f"Failed to launch browser: {str(e)}")
        yield _browser


async def get_page_unsafe() -> Page:
    """Get or create page instance. MUST be called with _page_lock held."""
    global _page
    async with get_browser() as browser:
        # Check if page is healthy, not just closed
        if not await _is_page_healthy_unsafe():
            await _reset_page_unsafe()
            _page = await browser.new_page()
            # Set default timeouts
            _page.set_default_timeout(DEFAULT_TIMEOUT)
            _page.set_default_navigation_timeout(DEFAULT_NAVIGATION_TIMEOUT)
        return _page


async def get_page() -> Page:
    """Get or create page instance. Thread-safe version."""
    page_lock = _ensure_lock("_page_lock")
    async with page_lock:
        return await get_page_unsafe()


# ======================================================
# Navigation
# ======================================================


@mcp.tool()
@handle_browser_errors
async def navigate(url: str) -> str:
    """Navigate to a URL and return the page title."""
    page = await get_page_unsafe()
    await page.goto(url, wait_until="domcontentloaded")
    title = await page.title()
    return f"Navigated to {url}. Title: {title}"


@mcp.tool()
@handle_browser_errors
async def go_back() -> str:
    """Go back to the previous page."""
    page = await get_page_unsafe()
    await page.go_back(wait_until="domcontentloaded")
    return f"Went back. Current URL: {page.url}"


@mcp.tool()
@handle_browser_errors
async def go_forward() -> str:
    """Go forward to the next page."""
    page = await get_page_unsafe()
    await page.go_forward(wait_until="domcontentloaded")
    return f"Went forward. Current URL: {page.url}"


@mcp.tool()
@handle_browser_errors
async def reload() -> str:
    """Reload the current page."""
    page = await get_page_unsafe()
    await page.reload(wait_until="domcontentloaded")
    return f"Reloaded. Current URL: {page.url}"


# ======================================================
# Content
# ======================================================


@mcp.tool()
@handle_browser_errors
async def get_content(max_length: int = 10000) -> str:
    """Get the text content of the current page."""
    page = await get_page_unsafe()
    # Add timeout to prevent hanging
    text = await asyncio.wait_for(
        page.evaluate("() => document.body.innerText || document.body.textContent || ''"),
        timeout=CONTENT_EVAL_TIMEOUT
    )
    # Return a truncated version to avoid overwhelming the model
    if len(text) > max_length:
        text = text[:max_length] + f"\n... (truncated, total length: {len(text)})"
    return text


@mcp.tool()
@handle_browser_errors
async def get_url() -> str:
    """Get the current page URL."""
    page = await get_page_unsafe()
    return page.url


@mcp.tool()
@handle_browser_errors
async def get_title() -> str:
    """Get the current page title."""
    page = await get_page_unsafe()
    title = await page.title()
    return title


# ======================================================
# Interaction
# ======================================================


@mcp.tool()
@handle_browser_errors
async def click(selector: str) -> str:
    """Click an element on the page by CSS selector."""
    page = await get_page_unsafe()
    await page.click(selector)
    return f"Clicked element: {selector}"


@mcp.tool()
@handle_browser_errors
async def fill(selector: str, value: str) -> str:
    """Fill a form field with a value."""
    page = await get_page_unsafe()
    await page.fill(selector, value)
    return f"Filled {selector} with value"


@mcp.tool()
@handle_browser_errors
async def type_text(selector: str, text: str) -> str:
    """Type text into an element (simulates real typing)."""
    page = await get_page_unsafe()
    await page.type(selector, text)
    return f"Typed text into {selector}"


@mcp.tool()
@handle_browser_errors
async def press_key(key: str) -> str:
    """Press a keyboard key (e.g., 'Enter', 'Tab', 'Escape')."""
    page = await get_page_unsafe()
    await page.keyboard.press(key)
    return f"Pressed key: {key}"


@mcp.tool()
@handle_browser_errors
async def select_option(selector: str, value: str) -> str:
    """Select an option from a dropdown by value."""
    page = await get_page_unsafe()
    await page.select_option(selector, value)
    return f"Selected option {value} in {selector}"


@mcp.tool()
@handle_browser_errors
async def hover(selector: str) -> str:
    """Hover over an element."""
    page = await get_page_unsafe()
    await page.hover(selector)
    return f"Hovered over: {selector}"


# ======================================================
# Screenshots
# ======================================================


@mcp.tool()
@handle_browser_errors
async def screenshot(filename: str = "screenshot.png", full_page: bool = False) -> str:
    """Take a screenshot of the current page."""
    page = await get_page_unsafe()
    workspace = os.getenv("WORKSPACE", "workspace")
    # Create workspace directory if it doesn't exist
    os.makedirs(workspace, exist_ok=True)
    filepath = os.path.join(workspace, filename)
    await page.screenshot(path=filepath, full_page=full_page, timeout=30000)
    return f"Screenshot saved to {filepath}"


@mcp.tool()
@handle_browser_errors
async def screenshot_base64(full_page: bool = False) -> str:
    """Take a screenshot and return it as base64."""
    page = await get_page_unsafe()
    screenshot_bytes = await page.screenshot(full_page=full_page, timeout=30000)
    return base64.b64encode(screenshot_bytes).decode("utf-8")


# ======================================================
# JavaScript
# ======================================================


@mcp.tool()
@handle_browser_errors
async def evaluate(script: str) -> str:
    """Execute JavaScript in the browser and return the result."""
    page = await get_page_unsafe()
    # Add timeout to prevent hanging
    result = await asyncio.wait_for(page.evaluate(script), timeout=SCRIPT_EVAL_TIMEOUT)
    return str(result)


# ======================================================
# Wait
# ======================================================


@mcp.tool()
@handle_browser_errors
async def wait_for_selector(selector: str, timeout: int = 30000) -> str:
    """Wait for an element to appear on the page."""
    page = await get_page_unsafe()
    await page.wait_for_selector(selector, timeout=timeout)
    return f"Element {selector} is now visible"


@mcp.tool()
@handle_browser_errors
async def wait_for_navigation(timeout: int = 30000) -> str:
    """Wait for navigation to complete."""
    page = await get_page_unsafe()
    await page.wait_for_load_state("networkidle", timeout=timeout)
    return f"Navigation complete. URL: {page.url}"


# ======================================================
# Browser management
# ======================================================


@mcp.tool()
async def close_browser() -> str:
    """Close the browser and clean up resources.

    Note: This function manually handles locking in the correct order
    (browser_lock -> page_lock) to avoid deadlocks.
    """
    global _browser, _page, _playwright

    # Acquire locks in consistent order: browser_lock first, then page_lock
    browser_lock = _ensure_lock("_browser_lock")
    page_lock = _ensure_lock("_page_lock")

    async with browser_lock:
        async with page_lock:
            # Close the page first
            try:
                if _page and not _page.is_closed():
                    await _page.close()
            except Exception:
                pass
            finally:
                _page = None

        # Close browser and playwright (still within browser_lock)
        # All global state mutations must happen within appropriate locks
        try:
            if _browser:
                await _browser.close()
        except Exception:
            pass
        finally:
            _browser = None

        try:
            if _playwright:
                await _playwright.stop()
        except Exception:
            pass
        finally:
            _playwright = None

    return "Browser closed"


@mcp.tool()
@handle_browser_errors
async def force_reset() -> str:
    """Force reset the browser page if it's in a bad state."""
    await _reset_page_unsafe()
    # Create a new page to verify it works
    page = await get_page_unsafe()
    return f"Browser reset successfully. New page ready."


@mcp.tool()
@handle_browser_errors
async def get_page_status() -> str:
    """Check if the page is in a healthy state."""
    is_healthy = await _is_page_healthy_unsafe()
    if is_healthy:
        page = await get_page_unsafe()
        return f"Page is healthy. URL: {page.url}"
    else:
        return "Page is not healthy or not initialized"
