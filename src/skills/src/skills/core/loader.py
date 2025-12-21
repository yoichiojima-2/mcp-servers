"""Skill loading and parsing utilities."""

import logging
from pathlib import Path

import frontmatter

from .models import Skill, SkillArgument, SkillContent, SkillMetadata

logger = logging.getLogger(__name__)


class SkillLoader:
    """Loads and parses skill definitions."""

    SKILL_FILE = "SKILL.md"
    SCRIPTS_DIR = "scripts"

    def load_metadata(self, skill_path: Path, source: str = "project") -> SkillMetadata | None:
        """Load only the metadata from a skill directory.

        Args:
            skill_path: Path to skill directory
            source: Source type (builtin, user, project)

        Returns:
            SkillMetadata if valid skill, None otherwise
        """
        skill_file = skill_path / self.SKILL_FILE
        if not skill_file.exists():
            return None

        try:
            post = frontmatter.load(skill_file)
            name = post.get("name")
            description = post.get("description")

            if not name or not description:
                logger.warning(f"Skill at {skill_path} missing name or description")
                return None

            return SkillMetadata(
                name=name,
                description=description,
                source=source,
                path=skill_path.resolve(),
            )
        except Exception as e:
            logger.warning(f"Error loading skill metadata from {skill_path}: {e}")
            return None

    def load_content(self, skill_path: Path) -> SkillContent | None:
        """Load the full content of a skill.

        Args:
            skill_path: Path to skill directory

        Returns:
            SkillContent with instructions and resources, or None if loading fails
        """
        skill_file = skill_path / self.SKILL_FILE
        try:
            post = frontmatter.load(skill_file)

            arguments = []
            if "arguments" in post.metadata:
                for arg in post.metadata["arguments"]:
                    arguments.append(
                        SkillArgument(
                            name=arg["name"],
                            description=arg.get("description", ""),
                            required=arg.get("required", False),
                            default=arg.get("default"),
                        )
                    )

            resources = self._discover_resources(skill_path)

            return SkillContent(
                instructions=post.content,
                base_path=skill_path.resolve(),
                arguments=arguments,
                resources=resources,
            )
        except Exception as e:
            logger.warning(f"Error loading skill content from {skill_path}: {e}")
            return None

    def load_skill(self, skill_path: Path, source: str = "project", load_content: bool = True) -> Skill | None:
        """Load a complete skill from a directory.

        Args:
            skill_path: Path to skill directory
            source: Source type (builtin, user, project)
            load_content: Whether to load full content (lazy loading if False)

        Returns:
            Skill if valid, None otherwise
        """
        metadata = self.load_metadata(skill_path, source)
        if metadata is None:
            return None

        content = self.load_content(skill_path) if load_content else None
        return Skill(metadata=metadata, content=content)

    def _discover_resources(self, skill_path: Path) -> list[str]:
        """Discover resource files including scripts/ and additional markdown files.

        Security: Validates that all paths stay within skill_path to prevent
        path traversal attacks via symlinks.
        """
        resources = []
        resolved_skill_path = skill_path.resolve()

        # Discover scripts
        scripts_dir = skill_path / self.SCRIPTS_DIR
        if scripts_dir.exists():
            for path in scripts_dir.rglob("*"):
                # Skip symlinks and validate path stays within skill directory
                if path.is_symlink():
                    continue
                resolved = path.resolve()
                if not resolved.is_relative_to(resolved_skill_path):
                    logger.warning(f"Skipping path outside skill directory: {path}")
                    continue
                if path.is_file():
                    resources.append(str(path.relative_to(skill_path)))

        # Discover additional markdown files (excluding SKILL.md)
        for md_file in skill_path.glob("*.md"):
            if md_file.is_symlink():
                continue
            if md_file.name != self.SKILL_FILE:
                resources.append(md_file.name)

        return sorted(resources)
