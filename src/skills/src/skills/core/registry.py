"""Skill registry for discovery and management."""

import logging
from pathlib import Path

from .loader import SkillLoader
from .models import Skill, SkillMetadata

logger = logging.getLogger(__name__)


class SkillRegistry:
    """Registry for discovering and managing skills."""

    def __init__(self, skill_paths: list[Path] | None = None):
        """Initialize registry with skill directory paths.

        Args:
            skill_paths: List of paths to search for skills (in priority order).
                         Later paths override earlier ones for same skill name.
        """
        self._skill_paths = skill_paths or []
        self._skills: dict[str, SkillMetadata] = {}
        self._loader = SkillLoader()

    def discover(self) -> None:
        """Scan directories and index all valid skills."""
        self._skills.clear()

        for path in self._skill_paths:
            if not path.exists():
                logger.debug(f"Skill path does not exist: {path}")
                continue

            source = self._infer_source(path)

            for skill_dir in path.iterdir():
                if not skill_dir.is_dir():
                    continue

                metadata = self._loader.load_metadata(skill_dir, source)
                if metadata:
                    if metadata.name in self._skills:
                        logger.debug(f"Skill '{metadata.name}' overridden by {skill_dir}")
                    self._skills[metadata.name] = metadata

        logger.info(f"Discovered {len(self._skills)} skills")

    def list_skills(self) -> list[SkillMetadata]:
        """Return metadata for all discovered skills."""
        return list(self._skills.values())

    def get_skill(self, name: str) -> Skill | None:
        """Get full skill by name (lazy-loads content and tools).

        Args:
            name: Skill name

        Returns:
            Full Skill with content and tools, or None if not found
        """
        metadata = self._skills.get(name)
        if metadata is None:
            return None

        return self._loader.load_skill(metadata.path, metadata.source, load_content=True)

    def get_metadata(self, name: str) -> SkillMetadata | None:
        """Get skill metadata by name."""
        return self._skills.get(name)

    def refresh(self) -> None:
        """Re-scan directories for skill changes."""
        self.discover()

    @property
    def skill_count(self) -> int:
        """Return number of discovered skills."""
        return len(self._skills)

    @property
    def skill_names(self) -> list[str]:
        """Return list of all skill names."""
        return list(self._skills.keys())

    def _infer_source(self, path: Path) -> str:
        """Infer source type from path."""
        path_str = str(path)
        if "builtin" in path_str or "site-packages" in path_str:
            return "builtin"
        elif str(Path.home()) in path_str:
            return "user"
        return "project"
