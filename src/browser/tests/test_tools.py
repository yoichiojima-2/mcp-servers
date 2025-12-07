import pytest
from fastmcp import Client

from browser import mcp


@pytest.mark.asyncio
async def test_navigate():
    """Test navigation to a URL."""
    async with Client(mcp) as client:
        res = await client.call_tool("navigate", {"url": "https://example.com"})
        assert "Navigated to" in res.content[0].text
        assert "Example Domain" in res.content[0].text


@pytest.mark.asyncio
async def test_get_content():
    """Test getting page content."""
    async with Client(mcp) as client:
        await client.call_tool("navigate", {"url": "https://example.com"})
        res = await client.call_tool("get_content", {})
        assert "Example Domain" in res.content[0].text


@pytest.mark.asyncio
async def test_get_url():
    """Test getting current URL."""
    async with Client(mcp) as client:
        await client.call_tool("navigate", {"url": "https://example.com"})
        res = await client.call_tool("get_url", {})
        assert "example.com" in res.content[0].text


@pytest.mark.asyncio
async def test_get_title():
    """Test getting page title."""
    async with Client(mcp) as client:
        await client.call_tool("navigate", {"url": "https://example.com"})
        res = await client.call_tool("get_title", {})
        assert "Example Domain" in res.content[0].text


@pytest.mark.asyncio
async def test_evaluate():
    """Test JavaScript evaluation."""
    async with Client(mcp) as client:
        await client.call_tool("navigate", {"url": "https://example.com"})
        res = await client.call_tool("evaluate", {"script": "1 + 1"})
        assert res.content[0].text == "2"


@pytest.mark.asyncio
async def test_close_browser():
    """Test closing the browser."""
    async with Client(mcp) as client:
        await client.call_tool("navigate", {"url": "https://example.com"})
        res = await client.call_tool("close_browser", {})
        assert "Browser closed" in res.content[0].text
