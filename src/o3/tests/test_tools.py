import os
from unittest.mock import Mock, patch

import pytest
from fastmcp import Client

from o3_search import mcp
from o3_search.tools import get_client


@pytest.mark.asyncio
async def test_o3_search_mock():
    """Test o3_search tool with mocked API."""
    with patch("o3_search.tools.get_client") as mock_get_client:
        mock_response = Mock()
        mock_response.output_text = "Mocked response"
        mock_client = Mock()
        mock_client.responses.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        async with Client(mcp) as client:
            result = await client.call_tool("o3", {"query": "test query"})
            assert result.content
            assert "Mocked response" in result.content[0].text


@pytest.mark.asyncio
async def test_o3_search_api_error():
    """Test o3_search tool handles API errors properly."""
    from fastmcp.exceptions import ToolError

    with patch("o3_search.tools.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.responses.create.side_effect = Exception("API connection failed")
        mock_get_client.return_value = mock_client

        async with Client(mcp) as client:
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool("o3", {"query": "test query"})
            assert "OpenAI API error" in str(exc_info.value)


def test_get_client_missing_api_key():
    """Test get_client raises error when API key is missing."""
    from fastmcp.exceptions import ToolError

    get_client.cache_clear()
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ToolError) as exc_info:
            get_client()
        assert "OPENAI_API_KEY" in str(exc_info.value)
    get_client.cache_clear()


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="Requires OPENAI_API_KEY")
@pytest.mark.asyncio
async def test_o3_search_integration():
    """Test o3_search tool with real API call."""
    from fastmcp.exceptions import ToolError

    async with Client(mcp) as client:
        try:
            result = await client.call_tool("o3", {"query": "What is 2 + 2?"})
            assert result.content
            assert len(result.content) > 0
            assert result.content[0].text
            assert len(result.content[0].text) > 0
        except ToolError as e:
            if "429" in str(e) or "quota" in str(e).lower():
                pytest.skip("OpenAI API quota exceeded - skipping integration test")
            raise
