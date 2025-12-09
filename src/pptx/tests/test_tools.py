import tempfile
from pathlib import Path

import pytest
from fastmcp import Client

from pptx_server.tools import mcp


@pytest.fixture
def temp_pptx():
    """Create a temporary pptx file path for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test.pptx"


@pytest.mark.asyncio
async def test_create_presentation(temp_pptx):
    async with Client(mcp) as client:
        res = await client.call_tool(
            "create_presentation",
            {
                "output_path": str(temp_pptx),
                "title": "Test Presentation",
                "subtitle": "Test Subtitle",
            },
        )
        assert "Created presentation" in res.content[0].text
        assert temp_pptx.exists()


@pytest.mark.asyncio
async def test_add_slide(temp_pptx):
    async with Client(mcp) as client:
        # First create a presentation
        await client.call_tool(
            "create_presentation",
            {"output_path": str(temp_pptx), "title": "Test"},
        )
        # Then add a slide
        res = await client.call_tool(
            "add_slide",
            {
                "file_path": str(temp_pptx),
                "layout": 1,
                "title": "New Slide",
                "content": "Some content",
            },
        )
        assert "Added slide" in res.content[0].text


@pytest.mark.asyncio
async def test_get_presentation_info(temp_pptx):
    async with Client(mcp) as client:
        # Create a presentation
        await client.call_tool(
            "create_presentation",
            {"output_path": str(temp_pptx), "title": "Info Test"},
        )
        # Get info
        res = await client.call_tool(
            "get_presentation_info",
            {"file_path": str(temp_pptx)},
        )
        assert "Slides:" in res.content[0].text
        assert "Dimensions:" in res.content[0].text


@pytest.mark.asyncio
async def test_extract_text(temp_pptx):
    async with Client(mcp) as client:
        # Create a presentation with content
        await client.call_tool(
            "create_presentation",
            {"output_path": str(temp_pptx), "title": "Text Test"},
        )
        # Extract text
        res = await client.call_tool(
            "extract_text",
            {"file_path": str(temp_pptx)},
        )
        assert "Slide 1" in res.content[0].text


@pytest.mark.asyncio
async def test_add_text_box(temp_pptx):
    async with Client(mcp) as client:
        # Create a presentation
        await client.call_tool(
            "create_presentation",
            {"output_path": str(temp_pptx), "title": "TextBox Test"},
        )
        # Add text box
        res = await client.call_tool(
            "add_text_box",
            {
                "file_path": str(temp_pptx),
                "slide_number": 1,
                "text": "Hello World",
                "left": 1.0,
                "top": 1.0,
                "width": 3.0,
                "height": 1.0,
            },
        )
        assert "Added text box" in res.content[0].text


@pytest.mark.asyncio
async def test_add_shape(temp_pptx):
    async with Client(mcp) as client:
        # Create a presentation
        await client.call_tool(
            "create_presentation",
            {"output_path": str(temp_pptx), "title": "Shape Test"},
        )
        # Add shape
        res = await client.call_tool(
            "add_shape",
            {
                "file_path": str(temp_pptx),
                "slide_number": 1,
                "shape_type": "rectangle",
                "left": 1.0,
                "top": 1.0,
                "width": 2.0,
                "height": 1.0,
                "fill_color": "4472C4",
            },
        )
        assert "Added rectangle shape" in res.content[0].text


@pytest.mark.asyncio
async def test_add_table(temp_pptx):
    async with Client(mcp) as client:
        # Create a presentation
        await client.call_tool(
            "create_presentation",
            {"output_path": str(temp_pptx), "title": "Table Test"},
        )
        # Add table
        res = await client.call_tool(
            "add_table",
            {
                "file_path": str(temp_pptx),
                "slide_number": 1,
                "data": [["Header 1", "Header 2"], ["Row 1", "Data 1"]],
                "left": 1.0,
                "top": 2.0,
                "width": 6.0,
                "height": 2.0,
            },
        )
        assert "Added 2x2 table" in res.content[0].text


@pytest.mark.asyncio
async def test_get_slide_shapes(temp_pptx):
    async with Client(mcp) as client:
        # Create a presentation
        await client.call_tool(
            "create_presentation",
            {"output_path": str(temp_pptx), "title": "Shapes Test"},
        )
        # Get shapes
        res = await client.call_tool(
            "get_slide_shapes",
            {"file_path": str(temp_pptx), "slide_number": 1},
        )
        # Should return JSON array
        assert "[" in res.content[0].text


# ======================================================
# Marp Tests
# ======================================================


# Note: Theme listing tests are in frontend-design server
# marp_list_themes and marp_get_theme_css were moved to design_list_themes/design_get_theme


@pytest.mark.asyncio
async def test_marp_check_requirements():
    async with Client(mcp) as client:
        res = await client.call_tool("marp_check_requirements", {})
        text = res.content[0].text
        # Should check for Node.js
        assert "Node.js" in text


@pytest.mark.asyncio
async def test_marp_create_presentation_invalid_theme():
    """Test that invalid theme names are rejected."""
    async with Client(mcp) as client:
        res = await client.call_tool(
            "marp_create_presentation",
            {
                "markdown": "# Test",
                "output_path": "/tmp/test.pptx",
                "theme": "nonexistent_theme",
            },
        )
        text = res.content[0].text
        assert "Error" in text or "Unknown theme" in text


@pytest.mark.asyncio
async def test_marp_create_presentation_from_file_not_found():
    """Test that missing files return error."""
    async with Client(mcp) as client:
        res = await client.call_tool(
            "marp_create_presentation_from_file",
            {
                "markdown_file": "/nonexistent/path/to/file.md",
                "output_path": "/tmp/test.pptx",
            },
        )
        text = res.content[0].text
        assert "Error" in text or "not found" in text


# Test validation functions directly
def test_marp_path_validation():
    """Test that forbidden paths are rejected."""
    from pathlib import Path

    from pptx_server.marp import _validate_output_path

    # Should raise for system directories
    with pytest.raises(ValueError, match="system directory"):
        _validate_output_path(Path("/etc/passwd.pptx"))

    with pytest.raises(ValueError, match="system directory"):
        _validate_output_path(Path("/usr/bin/test.pptx"))


def test_marp_extension_validation():
    """Test that non-.pptx extensions are rejected."""
    from pathlib import Path

    from pptx_server.marp import _validate_output_path

    # Should raise for wrong extension
    with pytest.raises(ValueError, match=".pptx extension"):
        _validate_output_path(Path("/tmp/test.pdf"))

    with pytest.raises(ValueError, match=".pptx extension"):
        _validate_output_path(Path("/tmp/test.exe"))

    with pytest.raises(ValueError, match=".pptx extension"):
        _validate_output_path(Path("/tmp/test"))


def test_marp_markdown_size_validation():
    """Test that oversized markdown is rejected (limit: 2MB)."""
    from pptx_server.marp import convert_markdown_to_pptx, MAX_MARKDOWN_SIZE

    # Verify the limit is 2MB
    assert MAX_MARKDOWN_SIZE == 2_000_000

    # Create oversized content
    huge_content = "x" * (MAX_MARKDOWN_SIZE + 1)

    with pytest.raises(ValueError, match="too large"):
        convert_markdown_to_pptx(huge_content, "/tmp/test.pptx")


def test_marp_frontmatter_sanitization():
    """Test that dangerous frontmatter keys are removed."""
    from pptx_server.marp import _sanitize_frontmatter

    # Test that backgroundImage with url() is removed
    malicious_md = """---
marp: true
theme: minimal
backgroundImage: url(https://evil.com/track.png)
---

# Safe Content
"""
    sanitized = _sanitize_frontmatter(malicious_md)
    assert "backgroundImage" not in sanitized
    assert "evil.com" not in sanitized
    assert "marp: true" in sanitized
    assert "theme: minimal" in sanitized

    # Test that arbitrary keys are removed
    injection_md = """---
marp: true
html: true
script: console.log('xss')
---

# Content
"""
    sanitized = _sanitize_frontmatter(injection_md)
    assert "html:" not in sanitized
    assert "script:" not in sanitized
    assert "marp: true" in sanitized


def test_marp_frontmatter_allows_safe_keys():
    """Test that safe frontmatter keys are preserved."""
    from pptx_server.marp import _sanitize_frontmatter

    safe_md = """---
marp: true
theme: noir
paginate: true
header: My Header
footer: My Footer
title: Presentation Title
author: Test Author
headingDivider: 2
---

# Content
"""
    sanitized = _sanitize_frontmatter(safe_md)
    assert "marp: true" in sanitized
    assert "theme: noir" in sanitized
    assert "paginate: true" in sanitized
    assert "header: My Header" in sanitized
    assert "footer: My Footer" in sanitized
    assert "title: Presentation Title" in sanitized
    assert "author: Test Author" in sanitized
    assert "headingDivider: 2" in sanitized


def test_marp_frontmatter_blocks_url_in_style():
    """Test that url() in style is blocked."""
    from pptx_server.marp import _sanitize_frontmatter

    style_injection = """---
marp: true
style: |
  section { background-image: url(https://evil.com/track.png); }
---

# Content
"""
    sanitized = _sanitize_frontmatter(style_injection)
    assert "url(" not in sanitized
    assert "evil.com" not in sanitized


def test_marp_frontmatter_blocks_multiline_style():
    """Test that multi-line style blocks with dangerous content are blocked."""
    from pptx_server.marp import _sanitize_frontmatter

    # Test multi-line style block with url()
    multiline_injection = """---
marp: true
theme: minimal
style: |
  section {
    color: red;
  }
  .special {
    background-image: url(https://evil.com/track.png);
  }
---

# Content
"""
    sanitized = _sanitize_frontmatter(multiline_injection)
    assert "url(" not in sanitized
    assert "evil.com" not in sanitized
    # Theme should still be present
    assert "theme: minimal" in sanitized

    # Test multi-line style block with @import
    import_injection = """---
marp: true
style: >
  @import url('https://evil.com/malicious.css');
  section { color: blue; }
---

# Content
"""
    sanitized = _sanitize_frontmatter(import_injection)
    assert "@import" not in sanitized
    assert "evil.com" not in sanitized


def test_marp_frontmatter_blocks_import():
    """Test that @import in style is blocked."""
    from pptx_server.marp import _sanitize_frontmatter

    import_injection = """---
marp: true
style: |
  @import url('https://evil.com/malicious.css');
---

# Content
"""
    sanitized = _sanitize_frontmatter(import_injection)
    # The style line with @import should be removed entirely
    assert "@import" not in sanitized
    assert "evil.com" not in sanitized


def test_marp_no_frontmatter_passthrough():
    """Test that markdown without frontmatter passes through unchanged."""
    from pptx_server.marp import _sanitize_frontmatter

    no_frontmatter = """# Simple Markdown

No frontmatter here.

- Item 1
- Item 2
"""
    sanitized = _sanitize_frontmatter(no_frontmatter)
    assert sanitized == no_frontmatter


def test_marp_command_construction():
    """Test that marp-cli command is constructed correctly (mocked)."""
    from unittest.mock import MagicMock, patch

    from pptx_server.marp import convert_markdown_to_pptx

    markdown = """---
marp: true
---

# Test Slide
"""
    mock_run = MagicMock()
    mock_run.return_value.returncode = 0

    with (
        patch("pptx_server.marp.subprocess.run", mock_run),
        patch("pathlib.Path.exists", return_value=True),
    ):
        try:
            convert_markdown_to_pptx(markdown, "/tmp/test_output.pptx", "minimal")
        except RuntimeError:
            pass  # May fail if file doesn't exist after mock

    # Verify subprocess.run was called
    assert mock_run.called
    call_args = mock_run.call_args

    # Verify command structure
    cmd = call_args[0][0]
    assert "npx" in cmd
    assert "@marp-team/marp-cli" in cmd
    assert "--pptx" in cmd
    assert "--theme" in cmd
    assert "--allow-local-files" in cmd
    assert "-o" in cmd

    # Verify timeout was set
    assert call_args[1].get("timeout") == 60
