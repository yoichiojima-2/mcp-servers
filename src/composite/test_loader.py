from pathlib import Path
from unittest.mock import MagicMock

import pytest

from composite.config import ServerConfig
from composite.loader import ServerLoader


@pytest.fixture
def repo_root():
    return Path(__file__).parent.parent


@pytest.fixture
def loader(repo_root):
    return ServerLoader(repo_root)


def test_load_browser_server(loader):
    config = ServerConfig(
        name="browser",
        module="browser",
        prefix="browser",
        enabled=True,
        has_lifespan=False,
    )
    mcp = loader.load_server_module(config)
    assert mcp is not None
    assert hasattr(mcp, "_tool_manager")


def test_load_nonexistent_server(loader):
    config = ServerConfig(
        name="nonexistent",
        module="nonexistent",
        prefix="ne",
        enabled=True,
    )
    with pytest.raises(ModuleNotFoundError):
        loader.load_server_module(config)


def test_register_tools(loader):
    config = ServerConfig(
        name="browser", module="browser", prefix="browser", enabled=True
    )
    source_mcp = loader.load_server_module(config)

    target_mcp = MagicMock()
    target_mcp._tool_manager._tools = {}

    count = loader.register_tools(source_mcp, target_mcp, "test")
    assert count > 0
    assert len(target_mcp._tool_manager._tools) == count


def test_validate_server_module(loader):
    config = ServerConfig(
        name="browser", module="browser", prefix="browser", enabled=True
    )
    mcp = loader.load_server_module(config)
    assert loader.validate_server_module(mcp) is True

    invalid_mcp = MagicMock(spec=[])
    assert loader.validate_server_module(invalid_mcp) is False
