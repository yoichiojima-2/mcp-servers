"""Tests for img2pptx tools."""

from pathlib import Path

import pytest

from img2pptx.tools import _validate_image_path, _validate_output_path


def test_validate_output_path_requires_pptx():
    """Output must have .pptx extension."""
    with pytest.raises(ValueError, match="must be .pptx"):
        _validate_output_path(Path("/tmp/test.pdf"))


def test_validate_output_path_forbids_system_dirs():
    """Cannot write to system directories."""
    with pytest.raises(ValueError, match="system directory"):
        _validate_output_path(Path("/etc/passwd.pptx"))


def test_validate_image_path_not_found():
    """Raises FileNotFoundError for missing images."""
    with pytest.raises(FileNotFoundError):
        _validate_image_path(Path("/nonexistent/image.png"))


def test_validate_image_path_bad_extension(tmp_path):
    """Rejects unsupported image formats."""
    bad_file = tmp_path / "test.txt"
    bad_file.write_text("not an image")
    with pytest.raises(ValueError, match="Unsupported format"):
        _validate_image_path(bad_file)
