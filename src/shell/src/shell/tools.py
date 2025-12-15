import os
import shlex
import subprocess

from core import WORKSPACE, get_workspace

from . import mcp

DEFAULT_TIMEOUT = 300  # 5 minutes

# Allowlist of permitted commands (comma-separated via environment variable)
# If not set or empty, all commands are allowed (use with caution)
ALLOWED_COMMANDS = os.getenv("ALLOWED_COMMANDS", "").strip()


def _get_allowed_commands() -> set[str] | None:
    """Get the set of allowed commands, or None if all commands are allowed."""
    if not ALLOWED_COMMANDS:
        return None
    return {cmd.strip() for cmd in ALLOWED_COMMANDS.split(",") if cmd.strip()}


def _validate_command(command: str) -> tuple[list[str], str | None]:
    """Validate command against allowlist and parse it.

    Returns (tokens, error) where:
    - tokens: parsed command tokens (empty list if invalid)
    - error: error message if invalid, None if valid
    """
    try:
        tokens = shlex.split(command)
        if not tokens:
            return [], "Empty command"
    except ValueError as e:
        return [], f"Failed to parse command: {e}"

    allowed = _get_allowed_commands()
    if allowed is None:
        return tokens, None  # All commands allowed

    base_cmd = os.path.basename(tokens[0])
    if base_cmd not in allowed:
        return [], f"Command '{base_cmd}' is not in the allowlist. Allowed: {', '.join(sorted(allowed))}"

    return tokens, None


@mcp.tool()
def get_workspace_path() -> str:
    """Get the workspace directory path for saving files.

    Use this directory for any files created by shell commands.

    Returns:
        Path to ~/.mcp-servers/workspace/ where files should be saved.
    """
    return str(get_workspace(WORKSPACE))


@mcp.tool()
def shell(command: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Execute a shell command and return the output.

    Commands are validated against an allowlist if ALLOWED_COMMANDS is set.
    The allowlist contains base command names (e.g., "ls", "git", "python").
    Commands run in the workspace directory.

    Args:
        command: Shell command to execute
        timeout: Maximum execution time in seconds (default: 300)

    Returns:
        Command output including exit code, stdout, and stderr
    """
    # Validate and parse command
    tokens, error = _validate_command(command)
    if error:
        return f"Error: {error}"

    workspace = get_workspace(WORKSPACE)

    try:
        res = subprocess.run(
            tokens,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=workspace,
        )

        parts = [f"**exit code**: {res.returncode}"]

        if res.stdout:
            parts.append(f"**stdout**:\n{res.stdout.rstrip()}")

        if res.stderr:
            parts.append(f"**stderr**:\n{res.stderr.rstrip()}")

        return "\n\n".join(parts)
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds"
    except subprocess.SubprocessError as e:
        return f"Error: Subprocess failed: {e}"
    except Exception as e:
        return f"Error: {e}"
