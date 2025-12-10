import pytest
from fastmcp import Client

from data_analysis.prompts import mcp


@pytest.mark.asyncio
async def test_data_analysis():
    async with Client(mcp) as client:
        res = await client.get_prompt(
            "data_analysis",
            {
                "input": "test",
                "scratchpad": "",
                "tools": "",
            },
        )
        assert res.messages[0].content.text


@pytest.mark.asyncio
async def test_get_data_analysis_prompt():
    async with Client(mcp) as client:
        res = await client.call_tool(
            "get_data_analysis_prompt",
            {
                "input": "test",
                "scratchpad": "",
                "tools": "",
            },
        )
        assert res.content[0].text
