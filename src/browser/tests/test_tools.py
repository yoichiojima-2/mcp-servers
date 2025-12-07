import asyncio

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


# ======================================================
# Concurrency Tests
# ======================================================


@pytest.mark.asyncio
async def test_concurrent_get_content():
    """Test multiple concurrent get_content calls don't cause race conditions."""
    async with Client(mcp) as client:
        await client.call_tool("navigate", {"url": "https://example.com"})

        # Make 5 concurrent requests
        tasks = [client.call_tool("get_content", {}) for _ in range(5)]
        results = await asyncio.gather(*tasks)

        # All should succeed and return the same content
        for res in results:
            assert "Example Domain" in res.content[0].text


@pytest.mark.asyncio
async def test_concurrent_navigate_and_get_content():
    """Test that navigation and content retrieval work concurrently."""
    async with Client(mcp) as client:
        # First navigate to establish a page
        await client.call_tool("navigate", {"url": "https://example.com"})

        # Then try concurrent operations
        tasks = [
            client.call_tool("get_title", {}),
            client.call_tool("get_url", {}),
            client.call_tool("get_content", {}),
        ]
        results = await asyncio.gather(*tasks)

        # All should succeed
        assert "Example Domain" in results[0].content[0].text  # title
        assert "example.com" in results[1].content[0].text  # url
        assert "Example Domain" in results[2].content[0].text  # content


@pytest.mark.asyncio
async def test_concurrent_evaluations():
    """Test multiple concurrent JavaScript evaluations."""
    async with Client(mcp) as client:
        await client.call_tool("navigate", {"url": "https://example.com"})

        # Make 5 concurrent JavaScript evaluations
        tasks = [
            client.call_tool("evaluate", {"script": f"{i} + {i}"}) for i in range(1, 6)
        ]
        results = await asyncio.gather(*tasks)

        # Check results are correct
        expected = ["2", "4", "6", "8", "10"]
        for i, res in enumerate(results):
            assert res.content[0].text == expected[i]


# ======================================================
# Error Recovery Tests
# ======================================================


@pytest.mark.asyncio
async def test_page_status():
    """Test getting page status."""
    async with Client(mcp) as client:
        await client.call_tool("navigate", {"url": "https://example.com"})
        res = await client.call_tool("get_page_status", {})
        assert "healthy" in res.content[0].text.lower()
        assert "example.com" in res.content[0].text


@pytest.mark.asyncio
async def test_force_reset():
    """Test force resetting the browser page."""
    async with Client(mcp) as client:
        await client.call_tool("navigate", {"url": "https://example.com"})
        res = await client.call_tool("force_reset", {})
        assert "reset successfully" in res.content[0].text.lower()


@pytest.mark.asyncio
async def test_invalid_selector_error_handling():
    """Test that invalid selectors are handled gracefully."""
    async with Client(mcp) as client:
        await client.call_tool("navigate", {"url": "https://example.com"})
        res = await client.call_tool("click", {"selector": "#nonexistent-element-12345"})
        # Should return an error message, not crash
        assert "Error" in res.content[0].text or "Timeout" in res.content[0].text


@pytest.mark.asyncio
async def test_recovery_after_error():
    """Test that the browser recovers after an error."""
    async with Client(mcp) as client:
        await client.call_tool("navigate", {"url": "https://example.com"})

        # Cause an error
        await client.call_tool("click", {"selector": "#nonexistent-element-12345"})

        # Should still be able to use the browser
        res = await client.call_tool("get_title", {})
        assert "Example Domain" in res.content[0].text


@pytest.mark.asyncio
async def test_invalid_javascript_error_handling():
    """Test that invalid JavaScript is handled gracefully."""
    async with Client(mcp) as client:
        await client.call_tool("navigate", {"url": "https://example.com"})
        res = await client.call_tool("evaluate", {"script": "this.is.invalid.javascript"})
        # Should return an error message, not crash
        assert "Error" in res.content[0].text


# ======================================================
# Stress Tests
# ======================================================


@pytest.mark.asyncio
async def test_rapid_sequential_operations():
    """Test rapid sequential operations don't cause issues."""
    async with Client(mcp) as client:
        await client.call_tool("navigate", {"url": "https://example.com"})

        # Perform 10 rapid sequential operations
        for _ in range(10):
            res1 = await client.call_tool("get_title", {})
            assert "Example Domain" in res1.content[0].text

            res2 = await client.call_tool("get_url", {})
            assert "example.com" in res2.content[0].text


@pytest.mark.asyncio
async def test_multiple_navigations():
    """Test multiple navigations in sequence."""
    async with Client(mcp) as client:
        # Navigate to first URL
        res1 = await client.call_tool("navigate", {"url": "https://example.com"})
        assert "Example Domain" in res1.content[0].text

        # Navigate to second URL
        res2 = await client.call_tool("navigate", {"url": "https://httpbin.org/html"})
        assert "Navigated to" in res2.content[0].text

        # Navigate back to first URL
        res3 = await client.call_tool("navigate", {"url": "https://example.com"})
        assert "Example Domain" in res3.content[0].text


@pytest.mark.asyncio
async def test_browser_reopen_after_close():
    """Test that browser can be reopened after closing."""
    async with Client(mcp) as client:
        await client.call_tool("navigate", {"url": "https://example.com"})
        await client.call_tool("close_browser", {})

        # Should be able to navigate again after closing
        res = await client.call_tool("navigate", {"url": "https://example.com"})
        assert "Navigated to" in res.content[0].text


@pytest.mark.asyncio
async def test_page_health_after_multiple_operations():
    """Test page health remains good after multiple operations."""
    async with Client(mcp) as client:
        await client.call_tool("navigate", {"url": "https://example.com"})

        # Perform various operations
        await client.call_tool("get_content", {})
        await client.call_tool("evaluate", {"script": "1 + 1"})
        await client.call_tool("get_title", {})

        # Check page is still healthy
        res = await client.call_tool("get_page_status", {})
        assert "healthy" in res.content[0].text.lower()
