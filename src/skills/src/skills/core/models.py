"""Data models for skills."""

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field


class SkillArgument(BaseModel):
    """Optional argument for skill parameterization."""

    name: str
    description: str
    required: bool = False
    default: Any = None


class SkillMetadata(BaseModel):
    """Lightweight metadata for skill discovery (always loaded)."""

    name: str = Field(..., pattern=r"^[a-z0-9-]+$", max_length=64)
    description: str = Field(..., max_length=1024)
    source: Literal["builtin", "user", "project"] = "project"
    path: Path

    model_config = {"frozen": True}


class SkillContent(BaseModel):
    """Full skill content (loaded on-demand)."""

    instructions: str
    base_path: Path
    arguments: list[SkillArgument] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)


class Skill(BaseModel):
    """Complete skill representation."""

    metadata: SkillMetadata
    content: SkillContent | None = None
