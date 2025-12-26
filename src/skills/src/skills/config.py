"""Configuration for skills server."""

import os
from pathlib import Path


def get_skill_paths() -> list[Path]:
    """Return skill paths in priority order (later overrides earlier)."""
    paths = []

    # User skills directory
    user_dir = os.getenv("SKILLS_USER_DIR", str(Path.home() / ".mcp-servers" / "skills"))
    paths.append(Path(user_dir))

    # Project skills directory
    project_dir = os.getenv("SKILLS_PROJECT_DIR", str(Path.cwd() / "skills"))
    paths.append(Path(project_dir))

    return paths
