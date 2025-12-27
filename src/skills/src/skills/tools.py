"""MCP tools for skill discovery and loading."""

import subprocess
import sys
from pathlib import Path

from . import get_skills, mcp

# Script execution timeout in seconds
SCRIPT_TIMEOUT = 30


@mcp.tool()
def list_skills() -> list[dict]:
    """List all available skills.

    Returns a list of skills, each with:
    - name: Unique skill identifier
    - description: When and why to use this skill

    Use this to discover what skills are available before loading one.
    """
    skills = get_skills()
    return [{"name": s["name"], "description": s["description"]} for s in skills.values()]


@mcp.tool()
def load_skill(name: str) -> dict:
    """Load a skill's full instructions.

    Args:
        name: The skill name from list_skills()

    Returns:
        - instructions: The skill's markdown instructions
        - base_path: Path for resolving relative file references
        - resources: List of available resource files (scripts, docs)

    Call this when you determine a skill matches the user's request.
    """
    skills = get_skills()
    skill = skills.get(name)

    if skill is None:
        return {"error": f"Skill '{name}' not found"}

    return {
        "instructions": skill["instructions"],
        "base_path": skill["base_path"],
        "resources": skill["resources"],
    }


@mcp.tool()
def run_skill_script(
    skill_name: str,
    script_name: str,
    args: list[str] | None = None,
    input_data: str | None = None,
) -> dict:
    """Run a script from a loaded skill.

    Args:
        skill_name: The skill name from list_skills()
        script_name: Script path relative to skill (e.g., "scripts/analyze.py")
        args: Optional command-line arguments to pass to the script
        input_data: Optional data to pass to the script via stdin

    Returns:
        - stdout: Script's standard output
        - stderr: Script's standard error
        - returncode: Exit code (0 = success)

    Security: Scripts must be in the skill's resources list. Execution times out
    after 30 seconds.
    """
    skills = get_skills()
    skill = skills.get(skill_name)

    if skill is None:
        return {"error": f"Skill '{skill_name}' not found"}

    # Validate script is in the skill's resources
    if script_name not in skill["resources"]:
        return {
            "error": f"Script '{script_name}' not found in skill '{skill_name}'. "
            f"Available resources: {skill['resources']}"
        }

    # Build the full script path
    base_path = Path(skill["base_path"])
    script_path = base_path / script_name

    # Security: verify the resolved path stays within the skill directory
    resolved_script = script_path.resolve()
    resolved_base = base_path.resolve()
    if not resolved_script.is_relative_to(resolved_base):
        return {"error": "Script path escapes skill directory"}

    if not resolved_script.exists():
        return {"error": f"Script file not found: {script_name}"}

    # Build command
    cmd = [sys.executable, str(resolved_script)]
    if args:
        cmd.extend(args)

    try:
        result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            timeout=SCRIPT_TIMEOUT,
            cwd=str(resolved_base),
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Script execution timed out after {SCRIPT_TIMEOUT} seconds"}
    except OSError as e:
        return {"error": f"Failed to execute script: {e}"}
