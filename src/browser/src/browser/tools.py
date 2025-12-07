import base64
import os
from contextlib import asynccontextmanager
from typing import Optional

from playwright.async_api import Browser, Page, async_playwright

from . import mcp

# Global browser state
_browser: Optional[Browser] = None
_page: Optional[Page] = None
_playwright = None


@asynccontextmanager
async def get_browser():
    """Get or create browser instance."""
    global _browser, _playwright
    if _browser is None:
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(
            headless=os.getenv("HEADLESS", "true").lower() == "true"
        )
    yield _browser


async def get_page() -> Page:
    """Get or create page instance."""
    global _page
    async with get_browser() as browser:
        if _page is None or _page.is_closed():
            _page = await browser.new_page()
        return _page


# ======================================================
# Navigation
# ======================================================


@mcp.tool()
async def navigate(url: str) -> str:
    """Navigate to a URL and return the page title."""
    page = await get_page()
    await page.goto(url)
    return f"Navigated to {url}. Title: {await page.title()}"


@mcp.tool()
async def go_back() -> str:
    """Go back to the previous page."""
    page = await get_page()
    await page.go_back()
    return f"Went back. Current URL: {page.url}"


@mcp.tool()
async def go_forward() -> str:
    """Go forward to the next page."""
    page = await get_page()
    await page.go_forward()
    return f"Went forward. Current URL: {page.url}"


@mcp.tool()
async def reload() -> str:
    """Reload the current page."""
    page = await get_page()
    await page.reload()
    return f"Reloaded. Current URL: {page.url}"


# ======================================================
# Content
# ======================================================


@mcp.tool()
async def get_content() -> str:
    """Get the text content of the current page."""
    page = await get_page()
    content = await page.content()
    # Return a truncated version to avoid overwhelming the model
    text = await page.evaluate("() => document.body.innerText")
    if len(text) > 10000:
        text = text[:10000] + "\n... (truncated)"
    return text


@mcp.tool()
async def get_url() -> str:
    """Get the current page URL."""
    page = await get_page()
    return page.url


@mcp.tool()
async def get_title() -> str:
    """Get the current page title."""
    page = await get_page()
    return await page.title()


# ======================================================
# Interaction
# ======================================================


@mcp.tool()
async def click(selector: str) -> str:
    """Click an element on the page by CSS selector."""
    page = await get_page()
    await page.click(selector)
    return f"Clicked element: {selector}"


@mcp.tool()
async def fill(selector: str, value: str) -> str:
    """Fill a form field with a value."""
    page = await get_page()
    await page.fill(selector, value)
    return f"Filled {selector} with value"


@mcp.tool()
async def type_text(selector: str, text: str) -> str:
    """Type text into an element (simulates real typing)."""
    page = await get_page()
    await page.type(selector, text)
    return f"Typed text into {selector}"


@mcp.tool()
async def press_key(key: str) -> str:
    """Press a keyboard key (e.g., 'Enter', 'Tab', 'Escape')."""
    page = await get_page()
    await page.keyboard.press(key)
    return f"Pressed key: {key}"


@mcp.tool()
async def select_option(selector: str, value: str) -> str:
    """Select an option from a dropdown by value."""
    page = await get_page()
    await page.select_option(selector, value)
    return f"Selected option {value} in {selector}"


@mcp.tool()
async def hover(selector: str) -> str:
    """Hover over an element."""
    page = await get_page()
    await page.hover(selector)
    return f"Hovered over: {selector}"


# ======================================================
# Screenshots
# ======================================================


@mcp.tool()
async def screenshot(filename: str = "screenshot.png", full_page: bool = False) -> str:
    """Take a screenshot of the current page."""
    page = await get_page()
    workspace = os.getenv("WORKSPACE", "workspace")
    filepath = os.path.join(workspace, filename)
    await page.screenshot(path=filepath, full_page=full_page)
    return f"Screenshot saved to {filepath}"


@mcp.tool()
async def screenshot_base64(full_page: bool = False) -> str:
    """Take a screenshot and return it as base64."""
    page = await get_page()
    screenshot_bytes = await page.screenshot(full_page=full_page)
    return base64.b64encode(screenshot_bytes).decode("utf-8")


# ======================================================
# JavaScript
# ======================================================


@mcp.tool()
async def evaluate(script: str) -> str:
    """Execute JavaScript in the browser and return the result."""
    page = await get_page()
    result = await page.evaluate(script)
    return str(result)


# ======================================================
# Wait
# ======================================================


@mcp.tool()
async def wait_for_selector(selector: str, timeout: int = 30000) -> str:
    """Wait for an element to appear on the page."""
    page = await get_page()
    await page.wait_for_selector(selector, timeout=timeout)
    return f"Element {selector} is now visible"


@mcp.tool()
async def wait_for_navigation(timeout: int = 30000) -> str:
    """Wait for navigation to complete."""
    page = await get_page()
    await page.wait_for_load_state("networkidle", timeout=timeout)
    return f"Navigation complete. URL: {page.url}"


# ======================================================
# Browser management
# ======================================================


@mcp.tool()
async def close_browser() -> str:
    """Close the browser and clean up resources."""
    global _browser, _page, _playwright
    if _page:
        await _page.close()
        _page = None
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None
    return "Browser closed"
