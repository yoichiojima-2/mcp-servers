import subprocess

from . import mcp

DEFAULT_TIMEOUT = 300  # 5 minutes


@mcp.tool()
def shell(command: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """
    Execute a shell command and return the output.

    WARNING: This tool executes arbitrary shell commands with full shell capabilities
    including pipes, redirects, and variable expansion. Only use with trusted input.

    Args:
        command: Shell command to execute
        timeout: Maximum execution time in seconds (default: 300)

    Returns:
        Command output including exit code, stdout, and stderr
    """
    try:
        res = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
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
