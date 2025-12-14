import base64
import binascii
import platform
from pathlib import Path

from core import get_workspace

from . import mcp

# Maximum file size for read operations (100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024

# Unix system paths
FORBIDDEN_WRITE_PATHS_UNIX = [
    "/bin",
    "/sbin",
    "/usr/bin",
    "/usr/sbin",
    "/etc",
    "/boot",
    "/dev",
    "/proc",
    "/sys",
    "/root",
    "/System",
    "/Library",
    "/opt",
    "/Applications",
    # /var subdirectories (but not /var/folders or /var/tmp which are safe for temp files)
    "/var/log",
    "/var/db",
    "/var/run",
]

# Windows system paths
FORBIDDEN_WRITE_PATHS_WINDOWS = [
    "C:\\Windows",
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    "C:\\ProgramData",
]

# Select paths based on platform
FORBIDDEN_WRITE_PATHS = FORBIDDEN_WRITE_PATHS_WINDOWS if platform.system() == "Windows" else FORBIDDEN_WRITE_PATHS_UNIX


def _is_path_in_forbidden(resolved: Path, forbidden: str) -> bool:
    """Check if resolved path is inside a forbidden directory."""
    # Use string-based check to avoid race conditions with filesystem state
    resolved_str = str(resolved)
    # Ensure we match directory boundaries (e.g., /etc matches /etc/passwd but not /etcetera)
    if resolved_str == forbidden or resolved_str.startswith(forbidden + "/"):
        return True
    return False


def _validate_write_path(path: Path) -> None:
    """Validate that the path is safe to write to.

    Security: path.resolve() follows all symlinks (both in the path itself and
    any parent directories), so checking the resolved path is sufficient to
    prevent symlink-based attacks targeting forbidden directories.
    """
    resolved = path.resolve()

    # Check if resolved path is in forbidden locations
    # This catches all symlink attacks since resolve() follows symlinks
    for forbidden in FORBIDDEN_WRITE_PATHS:
        if _is_path_in_forbidden(resolved, forbidden):
            raise ValueError(f"Cannot write to system directory: {forbidden}")


@mcp.tool()
def get_workspace_path() -> str:
    """Get the workspace directory path for saving files.

    Use this directory for any files you need to create or store.

    Returns:
        Path to ~/.mcp-servers/file-management/ where files should be saved.
    """
    return str(get_workspace("file-management"))


@mcp.tool()
def write_file(file_path: str, content: str, encoding: str = "utf-8") -> str:
    """
    Write text content to a file. Supports large files that exceed shell input limits.

    Args:
        file_path: Path to the file to write (supports ~ expansion)
        content: Text content to write to the file
        encoding: Character encoding (default: utf-8)

    Returns:
        Success message with file path and size, or error message
    """
    try:
        path = Path(file_path).expanduser().resolve()
        _validate_write_path(path)

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding)

        size = path.stat().st_size
        return f"Successfully wrote {size:,} bytes to {path}"
    except ValueError as e:
        return f"Error: {e}"
    except PermissionError:
        return f"Error: Permission denied: {Path(file_path).expanduser().resolve()}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def write_binary(file_path: str, content_base64: str) -> str:
    """
    Write binary content (base64 encoded) to a file.

    Args:
        file_path: Path to the file to write (supports ~ expansion)
        content_base64: Base64-encoded binary content

    Returns:
        Success message with file path and size, or error message
    """
    try:
        path = Path(file_path).expanduser().resolve()
        _validate_write_path(path)

        path.parent.mkdir(parents=True, exist_ok=True)
        content = base64.b64decode(content_base64)
        path.write_bytes(content)

        size = path.stat().st_size
        return f"Successfully wrote {size:,} bytes to {path}"
    except ValueError as e:
        return f"Error: {e}"
    except PermissionError:
        return f"Error: Permission denied: {Path(file_path).expanduser().resolve()}"
    except binascii.Error:
        return "Error: Invalid base64 content"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def append_file(file_path: str, content: str, encoding: str = "utf-8") -> str:
    """
    Append text content to a file. Creates the file if it doesn't exist.

    Args:
        file_path: Path to the file to append to (supports ~ expansion)
        content: Text content to append
        encoding: Character encoding (default: utf-8)

    Returns:
        Success message with file path and new size, or error message
    """
    try:
        path = Path(file_path).expanduser().resolve()
        _validate_write_path(path)

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "a", encoding=encoding) as f:
            f.write(content)

        size = path.stat().st_size
        return f"Successfully appended to {path} (total size: {size:,} bytes)"
    except ValueError as e:
        return f"Error: {e}"
    except PermissionError:
        return f"Error: Permission denied: {Path(file_path).expanduser().resolve()}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    Read text content from a file.

    Args:
        file_path: Path to the file to read (supports ~ expansion)
        encoding: Character encoding (default: utf-8)

    Returns:
        File content, or error message
    """
    try:
        path = Path(file_path).expanduser().resolve()

        # Check file size before reading to prevent memory exhaustion
        if path.exists() and path.stat().st_size > MAX_FILE_SIZE:
            return f"Error: File too large ({path.stat().st_size:,} bytes, max: {MAX_FILE_SIZE:,}): {path}"

        # Let exceptions handle TOCTOU race conditions
        content = path.read_text(encoding=encoding)
        return content
    except FileNotFoundError:
        return f"Error: File not found: {Path(file_path).expanduser().resolve()}"
    except IsADirectoryError:
        return f"Error: Not a file: {Path(file_path).expanduser().resolve()}"
    except PermissionError:
        return f"Error: Permission denied: {Path(file_path).expanduser().resolve()}"
    except UnicodeDecodeError:
        return f"Error: Cannot decode file with encoding '{encoding}'. Try read_binary for binary files."
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def read_binary(file_path: str) -> str:
    """
    Read binary content from a file, returned as base64.

    Args:
        file_path: Path to the file to read (supports ~ expansion)

    Returns:
        Base64-encoded file content, or error message
    """
    try:
        path = Path(file_path).expanduser().resolve()

        # Check file size before reading to prevent memory exhaustion
        if path.exists() and path.stat().st_size > MAX_FILE_SIZE:
            return f"Error: File too large ({path.stat().st_size:,} bytes, max: {MAX_FILE_SIZE:,}): {path}"

        # Let exceptions handle TOCTOU race conditions
        content = path.read_bytes()
        return base64.b64encode(content).decode("ascii")
    except FileNotFoundError:
        return f"Error: File not found: {Path(file_path).expanduser().resolve()}"
    except IsADirectoryError:
        return f"Error: Not a file: {Path(file_path).expanduser().resolve()}"
    except PermissionError:
        return f"Error: Permission denied: {Path(file_path).expanduser().resolve()}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def list_directory(dir_path: str, pattern: str = "*") -> str:
    """
    List files in a directory with optional glob pattern.

    Args:
        dir_path: Path to the directory (supports ~ expansion)
        pattern: Glob pattern to filter files (default: *)

    Returns:
        List of files/directories, or error message
    """
    try:
        path = Path(dir_path).expanduser().resolve()

        if not path.exists():
            return f"Error: Directory not found: {path}"
        if not path.is_dir():
            return f"Error: Not a directory: {path}"

        entries = sorted(path.glob(pattern))
        if not entries:
            return f"No files matching '{pattern}' in {path}"

        lines = []
        for entry in entries:
            if entry.is_file():
                size = entry.stat().st_size
                lines.append(f"{entry.name} ({size:,} bytes)")
            else:
                lines.append(f"{entry.name}/")

        return "\n".join(lines)
    except PermissionError:
        return f"Error: Permission denied: {Path(dir_path).expanduser().resolve()}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def delete_file(file_path: str) -> str:
    """
    Delete a file.

    Args:
        file_path: Path to the file to delete (supports ~ expansion)

    Returns:
        Success message, or error message
    """
    try:
        path = Path(file_path).expanduser().resolve()
        _validate_write_path(path)

        if not path.exists():
            return f"Error: File not found: {path}"
        if not path.is_file():
            return f"Error: Not a file: {path}"

        path.unlink()
        return f"Successfully deleted: {path}"
    except ValueError as e:
        return f"Error: {e}"
    except PermissionError:
        return f"Error: Permission denied: {Path(file_path).expanduser().resolve()}"
    except Exception as e:
        return f"Error: {e}"
