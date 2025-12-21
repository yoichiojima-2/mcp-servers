"""MCP prompts for skills.

Note: Dynamic prompt registration is disabled because skills are discovered
lazily at runtime. Skills are exposed through tools (list_skills, load_skill)
which provide a more flexible interface for on-demand skill loading.
"""
