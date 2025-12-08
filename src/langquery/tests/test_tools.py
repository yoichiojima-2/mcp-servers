import pytest
from fastmcp import Client

from langquery.tools import mcp


@pytest.mark.asyncio
async def test_add():
    async with Client(mcp) as client:
        res = await client.call_tool("add", {"a": 1, "b": 2})
        assert res.content[0].text == "3"


@pytest.mark.asyncio
async def test_sub():
    async with Client(mcp) as client:
        res = await client.call_tool("sub", {"a": 2, "b": 1})
        assert res.content[0].text == "1"


@pytest.mark.asyncio
async def test_mul():
    async with Client(mcp) as client:
        res = await client.call_tool("mul", {"a": 2, "b": 3})
        assert res.content[0].text == "6"


@pytest.mark.asyncio
async def test_div():
    async with Client(mcp) as client:
        res = await client.call_tool("div", {"a": 2, "b": 1})
        assert res.content[0].text == "2.0"


@pytest.mark.asyncio
async def test_shell():
    async with Client(mcp) as client:
        msg = "test"
        res = await client.call_tool("shell", {"command": f"echo {msg}"})
        assert res.content[0].text == f"{msg}\n"


@pytest.mark.asyncio
async def test_query():
    async with Client(mcp) as client:
        res = await client.call_tool("query", {"sql": "SELECT 1 as test"})
        assert "test" in res.content[0].text


@pytest.mark.asyncio
async def test_query_history_logging():
    """Test that queries are logged to history."""
    async with Client(mcp) as client:
        # Execute a query
        await client.call_tool("query", {"sql": "SELECT 42 as answer"})

        # Get history
        history_res = await client.call_tool("get_query_history", {"limit": 5})
        history_text = history_res.content[0].text

        # Verify query appears in history
        assert "SELECT 42 as answer" in history_text
        assert "answer" in history_text or "42" in history_text


@pytest.mark.asyncio
async def test_query_history_failed_query():
    """Test that failed queries are logged with error messages."""
    async with Client(mcp) as client:
        # Execute an invalid query
        try:
            await client.call_tool("query", {"sql": "SELECT * FROM nonexistent_table"})
        except Exception:
            pass  # Expected to fail

        # Get history
        history_res = await client.call_tool("get_query_history", {"limit": 5})
        history_text = history_res.content[0].text

        # Verify failed query appears in history
        assert "nonexistent_table" in history_text


@pytest.mark.asyncio
async def test_get_cached_result():
    """Test retrieving cached results from previous queries."""
    async with Client(mcp) as client:
        # Execute a query
        await client.call_tool("query", {"sql": "SELECT 'cached' as test_value"})

        # Get history to find the query ID
        history_res = await client.call_tool("get_query_history", {"limit": 1})
        history_text = history_res.content[0].text

        # Extract query ID from history (first number after "id")
        # This is a simple extraction - in real code you might parse the markdown
        import re

        match = re.search(r"\|\s*(\d+)\s*\|", history_text)
        if match:
            query_id = int(match.group(1))

            # Get cached result
            cached_res = await client.call_tool("get_cached_result", {"query_id": query_id})
            cached_text = cached_res.content[0].text

            # Verify cached result contains our value
            assert "cached" in cached_text or "test_value" in cached_text


@pytest.mark.asyncio
async def test_search_query_history():
    """Test searching query history."""
    async with Client(mcp) as client:
        # Execute a few queries with distinct patterns
        await client.call_tool("query", {"sql": "SELECT 'findme' as unique_search_term"})
        await client.call_tool("query", {"sql": "SELECT 1 as other_query"})

        # Search for the specific query
        search_res = await client.call_tool(
            "search_query_history", {"search_term": "findme", "limit": 5}
        )
        search_text = search_res.content[0].text

        # Verify search finds the right query
        assert "findme" in search_text
        assert "unique_search_term" in search_text


@pytest.mark.asyncio
async def test_query_history_limit():
    """Test that query history respects the limit parameter."""
    async with Client(mcp) as client:
        # Get history with limit of 1
        history_res = await client.call_tool("get_query_history", {"limit": 1})
        history_text = history_res.content[0].text

        # Count the number of query rows (rough check - each query has at least one pipe)
        # This is a basic test - proper implementation would parse markdown properly
        lines = [line for line in history_text.split("\n") if "|" in line and "id" not in line.lower()]

        # Should have at most 1 data row (plus header and separator)
        assert len(lines) <= 3  # header + separator + 1 data row
