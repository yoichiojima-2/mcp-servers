"""MCP tools for skill discovery and loading."""

from . import get_skills, mcp


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
