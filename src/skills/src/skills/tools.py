"""MCP tools for skill discovery and loading."""

from . import get_registry, mcp


@mcp.tool()
def list_skills() -> list[dict]:
    """List all available skills with their metadata.

    Returns a list of skills, each with:
    - name: Unique skill identifier
    - description: When and why to use this skill

    Use this to discover what skills are available before loading one.
    """
    registry = get_registry()
    skills = registry.list_skills()
    return [{"name": metadata.name, "description": metadata.description} for metadata in skills]


@mcp.tool()
def load_skill(name: str) -> dict:
    """Load a skill's full instructions.

    Args:
        name: The skill name from list_skills()

    Returns:
        - instructions: The skill's markdown instructions
        - base_path: Path for resolving relative file references (scripts/, *.md)
        - resources: List of available resource files (scripts, additional docs)

    Call this when you determine a skill matches the user's request.
    Use bash to execute scripts in base_path/scripts/ as needed.
    """
    registry = get_registry()
    skill = registry.get_skill(name)
    if skill is None:
        return {"error": f"Skill '{name}' not found"}

    if skill.content is None:
        return {"error": f"Skill '{name}' has no content"}

    return {
        "instructions": skill.content.instructions,
        "base_path": str(skill.content.base_path),
        "resources": skill.content.resources,
    }
