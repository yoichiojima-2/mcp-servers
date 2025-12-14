"""Workspace directory management for MCP servers.

Provides a shared workspace at ~/.mcp-servers/workspace/ for all servers,
enabling inter-server file sharing. All servers can read/write files in this
common location.

Directory structure:
    ~/.mcp-servers/
    └── workspace/       # Shared workspace for all servers
        ├── data_analysis_history.db  # data-analysis query history
        ├── browser_screenshot.png    # browser screenshots
        └── ...

Usage:
    from core import SHARED_WORKSPACE, get_workspace
    workspace = get_workspace(SHARED_WORKSPACE)  # ~/.mcp-servers/workspace/
"""

import os
from pathlib import Path


# Base directory for all MCP server workspaces
MCP_SERVERS_BASE = Path.home() / ".mcp-servers"

# Shared workspace name for all servers to enable inter-server file sharing
SHARED_WORKSPACE = "workspace"


def get_workspace(server_name: str) -> Path:
    """Get the workspace directory for an MCP server.

    Creates the directory if it doesn't exist.

    Args:
        server_name: Name of the server (e.g., "data-analysis", "browser")

    Returns:
        Path to the workspace directory (created with 0o700 permissions)

    Raises:
        ValueError: If server_name contains path traversal characters
        OSError: If directory cannot be created
    """
    # Validate server_name to prevent path traversal
    if ".." in server_name or "/" in server_name or "\\" in server_name:
        raise ValueError(f"Invalid server name: {server_name}")

    workspace = MCP_SERVERS_BASE / server_name

    # Create with secure permissions (owner-only access)
    # Set umask to ensure no race condition where directory is briefly accessible
    old_umask = os.umask(0o077)
    try:
        workspace.mkdir(parents=True, exist_ok=True, mode=0o700)
        # Ensure permissions even if directory already existed with different mode
        workspace.chmod(0o700)
    except OSError as e:
        raise OSError(f"Failed to create workspace directory at {workspace}: {e}") from e
    finally:
        os.umask(old_umask)

    return workspace


def get_workspace_file(server_name: str, filename: str) -> Path:
    """Get a file path within a server's workspace.

    Subdirectories are allowed (e.g., "datasets/data.csv"), but path traversal
    attempts (e.g., "../evil.txt") are blocked.

    Args:
        server_name: Name of the server
        filename: Name of the file (may include subdirectories)

    Returns:
        Path to the file within the workspace directory

    Raises:
        ValueError: If filename attempts path traversal
    """
    # Block path traversal attempts - check for ".." as a path component
    parts = Path(filename).parts
    if any(part == ".." for part in parts):
        raise ValueError(f"Path traversal not allowed: {filename}")

    workspace = get_workspace(server_name)
    filepath = (workspace / filename).resolve()

    # Ensure resolved path is still within workspace
    try:
        filepath.relative_to(workspace.resolve())
    except ValueError:
        raise ValueError("Path escapes workspace directory")

    return filepath
