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


class TestSharedWorkspace:
    """Tests for WORKSPACE constant."""

    def test_shared_workspace_constant(self):
        """Test WORKSPACE constant is defined and exported correctly."""
        from core import WORKSPACE

        assert WORKSPACE == "workspace"

    def test_shared_workspace_creates_shared_directory(self, tmp_path, monkeypatch):
        """Test WORKSPACE creates the shared workspace directory."""
        monkeypatch.setenv("HOME", str(tmp_path))

        import importlib

        import core.workspace

        importlib.reload(core.workspace)

        workspace = core.workspace.get_workspace(core.workspace.WORKSPACE)

        assert workspace == tmp_path / ".mcp-servers" / "workspace"
        assert workspace.exists()
        assert workspace.is_dir()

    def test_cross_server_file_sharing(self, tmp_path, monkeypatch):
        """Test that multiple servers can access the same files via WORKSPACE."""
        monkeypatch.setenv("HOME", str(tmp_path))

        import importlib

        import core.workspace

        importlib.reload(core.workspace)

        # Simulate browser server creating a file
        browser_file = core.workspace.get_workspace_file(core.workspace.WORKSPACE, "browser_screenshot.png")

        # Simulate preview server accessing the same file
        preview_file = core.workspace.get_workspace_file(core.workspace.WORKSPACE, "browser_screenshot.png")

        # Both should point to the exact same path
        assert browser_file == preview_file
        assert browser_file.parent == tmp_path / ".mcp-servers" / "workspace"

    def test_shared_workspace_file_persistence(self, tmp_path, monkeypatch):
        """Test that files created in shared workspace persist across server calls."""
        monkeypatch.setenv("HOME", str(tmp_path))

        import importlib

        import core.workspace

        importlib.reload(core.workspace)

        # Server A creates a file
        file_path = core.workspace.get_workspace_file(core.workspace.WORKSPACE, "shared_data.txt")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("data from server A")

        # Server B reads the same file
        same_file = core.workspace.get_workspace_file(core.workspace.WORKSPACE, "shared_data.txt")
        assert same_file.read_text() == "data from server A"
