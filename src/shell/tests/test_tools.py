import pytest
from fastmcp import Client

from shell.tools import mcp


@pytest.mark.asyncio
async def test_shell():
    async with Client(mcp) as client:
        msg = "test"
        res = await client.call_tool("shell", {"command": f"echo {msg}"})
        text = res.content[0].text
        assert "exit code**: 0" in text
        assert msg in text


@pytest.mark.asyncio
async def test_shell_with_stderr():
    async with Client(mcp) as client:
        res = await client.call_tool("shell", {"command": "ls /nonexistent_dir_12345"})
        text = res.content[0].text
        assert "stderr" in text.lower()
        assert "exit code" in text.lower()


@pytest.mark.asyncio
async def test_shell_multiline():
    async with Client(mcp) as client:
        res = await client.call_tool("shell", {"command": "echo 'line1'; echo 'line2'"})
        text = res.content[0].text
        assert "line1" in text
        assert "line2" in text


@pytest.mark.asyncio
async def test_shell_exit_code_failure():
    async with Client(mcp) as client:
        res = await client.call_tool("shell", {"command": "exit 1"})
        text = res.content[0].text
        assert "exit code**: 1" in text


@pytest.mark.asyncio
async def test_shell_exit_code_success():
    async with Client(mcp) as client:
        res = await client.call_tool("shell", {"command": "exit 0"})
        text = res.content[0].text
        assert "exit code**: 0" in text
