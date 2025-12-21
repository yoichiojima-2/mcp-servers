# Skills MCP Server

MCP server for discovering and loading Claude skills.

## Features

- Discover skills from user and project directories
- Load skill instructions with associated resources
- Lazy-loading: metadata indexed at startup, content loaded on demand
- Priority-based override: project skills override user skills with the same name

## Tools

| Tool | Description |
|------|-------------|
| `list_skills` | List all available skills with name and description |
| `load_skill` | Load a skill's full instructions and resources |

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `SKILLS_USER_DIR` | `~/.skills-as-mcp/skills` | User-level skills directory |
| `SKILLS_PROJECT_DIR` | `./skills` | Project-level skills directory |

## Skill Format

Skills are directories containing a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: my-skill
description: |
  Brief description of when to use this skill.
---

# My Skill

Skill instructions in markdown format.
```

Optional `scripts/` directory contains executable scripts that can be run via bash.

## Requirements

- Python 3.12+
- Dependencies: pydantic, python-frontmatter, pyyaml

## Installation

```bash
cd src/skills
make install
```

## Running

```bash
# stdio transport (default)
uv run python -m skills

# SSE transport
uv run python -m skills --transport sse --port 8005

# With auto-reload
make serve
```

## Testing

```bash
cd src/skills
uv run pytest -v
```
