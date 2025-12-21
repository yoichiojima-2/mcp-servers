"""MCP prompts for skills."""

# Note: Prompts registration is currently disabled.
# Skills are exposed through tools (list_skills, load_skill) instead.
# Dynamic prompt registration at import time causes issues with the lazy registry pattern.
#
# To enable prompts, register them after the registry is initialized:
#
# def register_skill_prompts():
#     registry = get_registry()
#     for metadata in registry.list_skills():
#         @mcp.prompt(name=metadata.name, description=metadata.description)
#         def skill_prompt(skill_name=metadata.name):
#             skill = registry.get_skill(skill_name)
#             if skill and skill.content:
#                 return skill.content.instructions
#             return f"Skill '{skill_name}' not found."
