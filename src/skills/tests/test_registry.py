"""Tests for skill registry."""

from pathlib import Path

import pytest

from skills.core import SkillRegistry


@pytest.fixture
def registry(skills_dir: Path):
    reg = SkillRegistry([skills_dir])
    reg.discover()
    return reg


def test_discover_skills(registry: SkillRegistry):
    """Test skill discovery."""
    assert registry.skill_count >= 1
    assert "hello-world" in registry.skill_names


def test_list_skills(registry: SkillRegistry):
    """Test listing all skills."""
    skills = registry.list_skills()
    assert len(skills) >= 1
    skill_names = [s.name for s in skills]
    assert "hello-world" in skill_names


def test_get_skill(registry: SkillRegistry):
    """Test getting a full skill."""
    skill = registry.get_skill("hello-world")
    assert skill is not None
    assert skill.metadata.name == "hello-world"
    assert skill.content is not None


def test_get_skill_not_found(registry: SkillRegistry):
    """Test getting a non-existent skill."""
    skill = registry.get_skill("nonexistent")
    assert skill is None


def test_get_metadata(registry: SkillRegistry):
    """Test getting skill metadata."""
    metadata = registry.get_metadata("hello-world")
    assert metadata is not None
    assert metadata.name == "hello-world"


def test_refresh(registry: SkillRegistry):
    """Test registry refresh."""
    initial_count = registry.skill_count
    registry.refresh()
    assert registry.skill_count == initial_count


def test_empty_registry():
    """Test registry with no skill paths."""
    registry = SkillRegistry([])
    registry.discover()
    assert registry.skill_count == 0


def test_nonexistent_path():
    """Test registry with non-existent path."""
    registry = SkillRegistry([Path("/nonexistent/path")])
    registry.discover()
    assert registry.skill_count == 0
