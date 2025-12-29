# Skills MCP Server

MCP server for discovering and loading Claude skills.

## Features

- Simple YAML configuration for skill paths
- Load skill instructions with associated resources

## Tools

| Tool | Description |
|------|-------------|
| `list_skills` | List all available skills with name and description |
| `load_skill` | Load a skill's full instructions and resources |

## Requirements

- Python 3.12+
- Dependencies: python-frontmatter, pyyaml

## Installation

```bash
# From the repository root
uv sync --package skills
```

## Usage

```bash
# stdio transport (default)
uv run python -m skills

# SSE transport
uv run python -m skills --transport sse --port 8014

# With auto-reload
make serve
```

See [server guide](../../docs/server-guide.md) for common CLI options.

## Configuration

Create a `skills.yaml` file:

```yaml
skills:
  - ~/.mcp-servers/skills/my-skill
  - ./skills/project-skill
  - /absolute/path/to/skill
```

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `SKILLS_CONFIG` | - | Path to skills config file (required to load skills) |

Copy `skills.yaml.example` to `skills.yaml` and add your skill paths.

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

**Skill name rules:** Names must contain only lowercase letters, numbers, and hyphens (e.g., `my-skill`, `code-review`).

Optional `scripts/` directory contains executable scripts that can be run via bash.

## Testing

```bash
cd src/skills
uv run pytest -v
```
