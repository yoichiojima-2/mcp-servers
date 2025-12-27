"""Tests for skills MCP tools."""

from pathlib import Path

import pytest

import skills
from skills import mcp


def get_tool(name: str):
    """Get a tool function by name."""
    return mcp._tool_manager._tools[name].fn


@pytest.fixture(autouse=True)
def setup_skills(monkeypatch, fixtures_dir: Path):
    """Configure skills to use test fixtures."""
    # Reset the module-level skills cache
    skills._skills = {}

    # Point to test fixtures config
    config_file = fixtures_dir / "skills.yaml"
    monkeypatch.setenv("SKILLS_CONFIG", str(config_file))

    # Change to fixtures dir so relative paths work
    monkeypatch.chdir(fixtures_dir)


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


def test_run_skill_script_success():
    """Test running a skill script successfully."""
    run_skill_script = get_tool("run_skill_script")
    result = run_skill_script(
        skill_name="code-review",
        script_name="scripts/analyze_complexity.py",
        input_data="def hello():\n    pass\n",
    )
    assert "error" not in result
    assert result["returncode"] == 0
    assert "total_lines" in result["stdout"]
    assert "functions" in result["stdout"]


def test_run_skill_script_with_args():
    """Test running a skill script with arguments."""
    run_skill_script = get_tool("run_skill_script")
    result = run_skill_script(
        skill_name="code-review",
        script_name="scripts/analyze_complexity.py",
        args=["--language", "javascript"],
        input_data="function hello() {}\n",
    )
    assert "error" not in result
    assert result["returncode"] == 0
    assert "javascript" in result["stdout"]


def test_run_skill_script_skill_not_found():
    """Test running a script from a non-existent skill."""
    run_skill_script = get_tool("run_skill_script")
    result = run_skill_script(
        skill_name="nonexistent",
        script_name="scripts/test.py",
    )
    assert "error" in result
    assert "not found" in result["error"]


def test_run_skill_script_script_not_in_resources():
    """Test running a script not in the skill's resources."""
    run_skill_script = get_tool("run_skill_script")
    result = run_skill_script(
        skill_name="code-review",
        script_name="scripts/nonexistent.py",
    )
    assert "error" in result
    assert "not found in skill" in result["error"]
    assert "Available resources" in result["error"]


def test_run_skill_script_hello_world_no_scripts():
    """Test running a script on a skill without scripts."""
    run_skill_script = get_tool("run_skill_script")
    result = run_skill_script(
        skill_name="hello-world",
        script_name="scripts/test.py",
    )
    assert "error" in result
    assert "not found in skill" in result["error"]
