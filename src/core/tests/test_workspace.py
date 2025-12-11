"""Tests for workspace module."""

from pathlib import Path

import pytest

from core import MCP_SERVERS_BASE, get_workspace, get_workspace_file


class TestGetWorkspace:
    """Tests for get_workspace function."""

    def test_default_workspace(self, tmp_path, monkeypatch):
        """Test workspace uses ~/.mcp-servers/{server}."""
        monkeypatch.setenv("HOME", str(tmp_path))

        import importlib

        import core.workspace

        importlib.reload(core.workspace)

        workspace = core.workspace.get_workspace("test-server")

        assert workspace == tmp_path / ".mcp-servers" / "test-server"
        assert workspace.exists()
        assert workspace.is_dir()

    def test_creates_nested_directory(self, tmp_path, monkeypatch):
        """Test workspace directory is created if it doesn't exist."""
        monkeypatch.setenv("HOME", str(tmp_path))

        import importlib

        import core.workspace

        importlib.reload(core.workspace)

        workspace = core.workspace.get_workspace("nested-server")

        assert workspace.exists()
        assert workspace.is_dir()

    def test_secure_permissions(self, tmp_path, monkeypatch):
        """Test workspace is created with secure permissions."""
        monkeypatch.setenv("HOME", str(tmp_path))

        import importlib

        import core.workspace

        importlib.reload(core.workspace)

        workspace = core.workspace.get_workspace("secure-server")

        mode = workspace.stat().st_mode & 0o777
        assert mode == 0o700

    def test_path_traversal_blocked(self):
        """Test path traversal attempts are blocked."""
        with pytest.raises(ValueError, match="Invalid server name"):
            get_workspace("../evil")

        with pytest.raises(ValueError, match="Invalid server name"):
            get_workspace("foo/bar")

        with pytest.raises(ValueError, match="Invalid server name"):
            get_workspace("foo\\bar")


class TestGetWorkspaceFile:
    """Tests for get_workspace_file function."""

    def test_returns_file_path(self, tmp_path, monkeypatch):
        """Test get_workspace_file returns path to file in workspace."""
        monkeypatch.setenv("HOME", str(tmp_path))

        import importlib

        import core.workspace

        importlib.reload(core.workspace)

        filepath = core.workspace.get_workspace_file("file-server", "data.db")

        assert filepath == tmp_path / ".mcp-servers" / "file-server" / "data.db"
        assert filepath.parent.exists()

    def test_subdirectories_allowed(self, tmp_path, monkeypatch):
        """Test subdirectories are allowed in filename."""
        monkeypatch.setenv("HOME", str(tmp_path))

        import importlib

        import core.workspace

        importlib.reload(core.workspace)

        filepath = core.workspace.get_workspace_file("test-server", "datasets/data.csv")

        assert filepath == tmp_path / ".mcp-servers" / "test-server" / "datasets" / "data.csv"

    def test_path_traversal_blocked(self):
        """Test path traversal attempts are blocked in filename."""
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            get_workspace_file("test-server", "../evil.txt")

        with pytest.raises(ValueError, match="Path traversal not allowed"):
            get_workspace_file("test-server", "foo/../../../evil.txt")

    def test_double_dots_in_filename_allowed(self, tmp_path, monkeypatch):
        """Test that double dots in filename (not path component) are allowed."""
        monkeypatch.setenv("HOME", str(tmp_path))

        import importlib

        import core.workspace

        importlib.reload(core.workspace)

        # "file..txt" should be allowed - ".." is not a path component
        filepath = core.workspace.get_workspace_file("test-server", "file..txt")
        assert filepath.name == "file..txt"

        # "a..b/file.txt" should also be allowed
        filepath = core.workspace.get_workspace_file("test-server", "a..b/file.txt")
        assert "a..b" in str(filepath)


class TestMCPServersBase:
    """Tests for MCP_SERVERS_BASE constant."""

    def test_base_is_in_home(self):
        """Test MCP_SERVERS_BASE is in home directory."""
        assert MCP_SERVERS_BASE == Path.home() / ".mcp-servers"
