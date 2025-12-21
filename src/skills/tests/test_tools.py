"""Tests for skills MCP tools."""

from pathlib import Path

import pytest

import skills
from skills import mcp


def get_tool(name: str):
    """Get a tool function by name."""
    return mcp._tool_manager._tools[name].fn


@pytest.fixture(autouse=True)
def setup_registry(monkeypatch, fixtures_dir: Path):
    """Configure registry to use test fixtures."""
    # Reset the module-level registry
    skills._registry = None

    # Patch get_skill_paths to return fixtures directory
    monkeypatch.setattr("skills.config.get_skill_paths", lambda: [fixtures_dir])


def test_list_skills():
    """Test listing available skills."""
    list_skills = get_tool("list_skills")
    result = list_skills()
    assert isinstance(result, list)
    assert len(result) >= 1
    names = [s["name"] for s in result]
    assert "hello-world" in names


def test_load_skill_success():
    """Test loading an existing skill."""
    load_skill = get_tool("load_skill")
    result = load_skill("hello-world")
    assert "error" not in result
    assert "instructions" in result
    assert "Hello World Skill" in result["instructions"]


def test_load_skill_not_found():
    """Test loading a non-existent skill."""
    load_skill = get_tool("load_skill")
    result = load_skill("nonexistent")
    assert "error" in result
    assert "not found" in result["error"]


def test_load_skill_with_resources():
    """Test loading a skill with resources."""
    load_skill = get_tool("load_skill")
    result = load_skill("code-review")
    assert "error" not in result
    assert "resources" in result
    assert "scripts/analyze_complexity.py" in result["resources"]
