"""MCP server for Claude skills discovery and loading."""

import logging
import os
from pathlib import Path

import frontmatter
import yaml
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

logger = logging.getLogger(__name__)

mcp = FastMCP(os.getenv("NAME", "skills"))

# In-memory skill cache
_skills: dict[str, dict] = {}


def _expand_path(path_str: str) -> Path:
    """Expand ~ and resolve path."""
    return Path(path_str).expanduser().resolve()


def _load_skill_from_path(skill_path: Path) -> dict | None:
    """Load a skill from a directory containing SKILL.md."""
    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        logger.warning(f"No SKILL.md found in {skill_path}")
        return None

    try:
        post = frontmatter.load(skill_file)
        name = post.get("name")
        description = post.get("description")

        if not name or not description:
            logger.warning(f"Skill at {skill_path} missing name or description")
            return None

        # Discover resources (scripts and extra markdown files)
        resources = []
        scripts_dir = skill_path / "scripts"
        if scripts_dir.exists():
            for f in scripts_dir.rglob("*"):
                if f.is_file() and not f.is_symlink():
                    resources.append(str(f.relative_to(skill_path)))

        for md in skill_path.glob("*.md"):
            if md.name != "SKILL.md" and not md.is_symlink():
                resources.append(md.name)

        return {
            "name": name,
            "description": description,
            "instructions": post.content,
            "base_path": str(skill_path),
            "resources": sorted(resources),
        }
    except Exception as e:
        logger.warning(f"Error loading skill from {skill_path}: {e}")
        return None


def _load_config() -> list[str]:
    """Load skill paths from config file."""
    config_path = os.getenv("SKILLS_CONFIG")
    if config_path:
        config_file = Path(config_path).expanduser()
    else:
        config_file = Path.cwd() / "skills.yaml"

    if not config_file.exists():
        logger.info(f"No config file at {config_file}, no skills loaded")
        return []

    try:
        with open(config_file) as f:
            config = yaml.safe_load(f) or {}
        return config.get("skills", [])
    except Exception as e:
        logger.warning(f"Error loading config from {config_file}: {e}")
        return []


def load_skills() -> None:
    """Load all skills from config."""
    global _skills
    _skills.clear()

    paths = _load_config()
    for path_str in paths:
        skill_path = _expand_path(path_str)
        if not skill_path.exists():
            logger.warning(f"Skill path does not exist: {skill_path}")
            continue

        skill = _load_skill_from_path(skill_path)
        if skill:
            _skills[skill["name"]] = skill
            logger.debug(f"Loaded skill: {skill['name']}")

    logger.info(f"Loaded {len(_skills)} skills")


def get_skills() -> dict[str, dict]:
    """Get all loaded skills."""
    if not _skills:
        load_skills()
    return _skills


from . import server, tools  # noqa: F401, E402

__all__ = ["mcp", "get_skills", "load_skills"]
