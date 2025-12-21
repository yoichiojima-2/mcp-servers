"""Tests for skill loader."""

from pathlib import Path

import pytest

from skills.core import SkillLoader


@pytest.fixture
def loader():
    return SkillLoader()


def test_load_metadata_hello_world(loader: SkillLoader, skills_dir: Path):
    """Test loading metadata from hello-world skill."""
    skill_path = skills_dir / "hello-world"
    metadata = loader.load_metadata(skill_path)

    assert metadata is not None
    assert metadata.name == "hello-world"
    assert "example skill" in metadata.description.lower()


def test_load_content_hello_world(loader: SkillLoader, skills_dir: Path):
    """Test loading content from hello-world skill."""
    skill_path = skills_dir / "hello-world"
    content = loader.load_content(skill_path)

    assert content is not None
    assert "Hello World Skill" in content.instructions
    assert content.base_path == skill_path.resolve()


def test_load_skill_full(loader: SkillLoader, skills_dir: Path):
    """Test loading complete skill."""
    skill_path = skills_dir / "hello-world"
    skill = loader.load_skill(skill_path)

    assert skill is not None
    assert skill.metadata.name == "hello-world"
    assert skill.content is not None


def test_load_metadata_invalid_dir(loader: SkillLoader, tmp_path: Path):
    """Test loading metadata from directory without SKILL.md."""
    metadata = loader.load_metadata(tmp_path)
    assert metadata is None


def test_discover_scripts(loader: SkillLoader, skills_dir: Path):
    """Test that scripts/ directory is discovered as resources."""
    skill_path = skills_dir / "code-review"
    content = loader.load_content(skill_path)

    assert "scripts/analyze_complexity.py" in content.resources
    assert "scripts/check_style.py" in content.resources
