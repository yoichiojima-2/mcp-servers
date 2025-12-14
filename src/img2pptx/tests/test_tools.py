"""Tests for img2pptx tools."""

from pathlib import Path

import pytest
from pptx import Presentation

from core import SHARED_WORKSPACE, get_workspace

from img2pptx.tools import (
    _create_slide,
    _image_to_base64,
    _validate_image_path,
    _validate_output_path,
)


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


def test_get_workspace_path():
    """Workspace path should be valid directory."""
    path = get_workspace(SHARED_WORKSPACE)
    assert path.exists()
    assert path.is_dir()


def test_image_to_base64(tmp_path):
    """Should convert image to base64 data URL."""
    # Create a minimal PNG (1x1 transparent pixel)
    png_data = bytes(
        [
            0x89,
            0x50,
            0x4E,
            0x47,
            0x0D,
            0x0A,
            0x1A,
            0x0A,  # PNG signature
            0x00,
            0x00,
            0x00,
            0x0D,
            0x49,
            0x48,
            0x44,
            0x52,  # IHDR chunk
            0x00,
            0x00,
            0x00,
            0x01,
            0x00,
            0x00,
            0x00,
            0x01,
            0x08,
            0x06,
            0x00,
            0x00,
            0x00,
            0x1F,
            0x15,
            0xC4,
            0x89,
            0x00,
            0x00,
            0x00,
            0x0A,
            0x49,
            0x44,
            0x41,  # IDAT chunk
            0x54,
            0x78,
            0x9C,
            0x63,
            0x00,
            0x01,
            0x00,
            0x00,
            0x05,
            0x00,
            0x01,
            0x0D,
            0x0A,
            0x2D,
            0xB4,
            0x00,
            0x00,
            0x00,
            0x00,
            0x49,
            0x45,
            0x4E,
            0x44,
            0xAE,  # IEND chunk
            0x42,
            0x60,
            0x82,
        ]
    )
    test_image = tmp_path / "test.png"
    test_image.write_bytes(png_data)

    result = _image_to_base64(test_image)
    assert result.startswith("data:image/png;base64,")


def test_image_to_base64_gif_mime_type(tmp_path):
    """Should use correct MIME type for GIF."""
    # Create minimal GIF
    gif_data = b"GIF89a\x01\x00\x01\x00\x00\x00\x00;\x00\x00\x00\x00\x00\x00"
    test_image = tmp_path / "test.gif"
    test_image.write_bytes(gif_data)

    result = _image_to_base64(test_image)
    assert result.startswith("data:image/gif;base64,")


def test_create_slide_with_content():
    """Should create slide with title and bullets."""
    prs = Presentation()
    content = {
        "title": "Test Title",
        "subtitle": "Test Subtitle",
        "bullets": ["Point 1", "Point 2"],
        "notes": "Test speaker notes",
    }

    _create_slide(prs, content)

    assert len(prs.slides) == 1
    slide = prs.slides[0]
    assert slide.shapes.title.text == "Test Title"


def test_create_slide_empty_content():
    """Should handle empty content gracefully."""
    prs = Presentation()
    content = {"title": "", "subtitle": "", "bullets": [], "notes": ""}

    _create_slide(prs, content)

    assert len(prs.slides) == 1
