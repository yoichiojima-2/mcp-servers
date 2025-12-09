import subprocess

from . import mcp


@mcp.tool()
def shell(command: str) -> str:
    """
    Execute a shell command and return the output.

    WARNING: This tool executes arbitrary shell commands with full shell capabilities
    including pipes, redirects, and variable expansion. Only use with trusted input.

    Args:
        command: Shell command to execute

    Returns:
        Command output including exit code, stdout, and stderr
    """
    res = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )

    parts = [f"**exit code**: {res.returncode}"]

    if res.stdout:
        parts.append(f"**stdout**:\n{res.stdout}")

    if res.stderr:
        parts.append(f"**stderr**:\n{res.stderr}")

    return "\n\n".join(parts)
