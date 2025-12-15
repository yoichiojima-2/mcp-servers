from unittest.mock import patch

import pytest
from fastmcp import Client

from shell import mcp
from shell.tools import _get_allowed_commands, _validate_command


class TestAllowlist:
    def test_get_allowed_commands_empty(self):
        with patch.object(
            __import__("shell.tools", fromlist=["ALLOWED_COMMANDS"]),
            "ALLOWED_COMMANDS",
            "",
        ):
            assert _get_allowed_commands() is None

    def test_get_allowed_commands_set(self):
        with patch.object(
            __import__("shell.tools", fromlist=["ALLOWED_COMMANDS"]),
            "ALLOWED_COMMANDS",
            "ls,cat,grep",
        ):
            result = _get_allowed_commands()
            assert result == {"ls", "cat", "grep"}

    def test_validate_command_allowed(self):
        with patch.object(
            __import__("shell.tools", fromlist=["ALLOWED_COMMANDS"]),
            "ALLOWED_COMMANDS",
            "ls,cat",
        ):
            tokens, error = _validate_command("ls -la")
            assert error is None
            assert tokens == ["ls", "-la"]
            tokens, error = _validate_command("cat /etc/hosts")
            assert error is None
            assert tokens == ["cat", "/etc/hosts"]

    def test_validate_command_not_allowed(self):
        with patch.object(
            __import__("shell.tools", fromlist=["ALLOWED_COMMANDS"]),
            "ALLOWED_COMMANDS",
            "ls,cat",
        ):
            tokens, error = _validate_command("rm -rf /")
            assert error is not None
            assert tokens == []
            assert "rm" in error
            assert "not in the allowlist" in error

    def test_validate_command_no_allowlist(self):
        with patch.object(
            __import__("shell.tools", fromlist=["ALLOWED_COMMANDS"]),
            "ALLOWED_COMMANDS",
            "",
        ):
            tokens, error = _validate_command("rm -rf /")
            assert error is None
            assert tokens == ["rm", "-rf", "/"]


@pytest.mark.asyncio
async def test_shell_echo():
    async with Client(mcp) as client:
        result = await client.call_tool("shell", {"command": "echo hello"})
        assert "hello" in result.content[0].text


@pytest.mark.asyncio
async def test_shell_timeout():
    async with Client(mcp) as client:
        result = await client.call_tool("shell", {"command": "sleep 10", "timeout": 1})
        assert "timed out" in result.content[0].text


@pytest.mark.asyncio
async def test_get_workspace_path():
    async with Client(mcp) as client:
        result = await client.call_tool("get_workspace_path", {})
        path = result.content[0].text
        assert ".mcp-servers" in path
        assert "workspace" in path
