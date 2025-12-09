"""Tests for frontend_design prompts."""

import pytest
from fastmcp import Client

from frontend_design import mcp


class TestDesignPrompts:
    """Tests for design prompts."""

    @pytest.mark.asyncio
    async def test_design_thinking_prompt(self):
        """Test design_thinking prompt is available and has content."""
        async with Client(mcp) as client:
            res = await client.get_prompt("design_thinking", {})
            assert res.messages[0].content.text
            assert "Design Thinking" in res.messages[0].content.text

    @pytest.mark.asyncio
    async def test_color_strategy_prompt(self):
        """Test color_strategy prompt is available and has content."""
        async with Client(mcp) as client:
            res = await client.get_prompt("color_strategy", {})
            assert res.messages[0].content.text
            assert "Color Strategy" in res.messages[0].content.text

    @pytest.mark.asyncio
    async def test_typography_principles_prompt(self):
        """Test typography_principles prompt is available and has content."""
        async with Client(mcp) as client:
            res = await client.get_prompt("typography_principles", {})
            assert res.messages[0].content.text
            assert "Typography" in res.messages[0].content.text

    @pytest.mark.asyncio
    async def test_layout_principles_prompt(self):
        """Test layout_principles prompt is available and has content."""
        async with Client(mcp) as client:
            res = await client.get_prompt("layout_principles", {})
            assert res.messages[0].content.text
            assert "Layout" in res.messages[0].content.text

    @pytest.mark.asyncio
    async def test_visual_elements_prompt(self):
        """Test visual_elements prompt is available and has content."""
        async with Client(mcp) as client:
            res = await client.get_prompt("visual_elements", {})
            assert res.messages[0].content.text
            assert "Visual Elements" in res.messages[0].content.text

    @pytest.mark.asyncio
    async def test_presentation_workflow_prompt(self):
        """Test presentation_workflow prompt is available and has content."""
        async with Client(mcp) as client:
            res = await client.get_prompt("presentation_workflow", {})
            assert res.messages[0].content.text
            assert "Presentation" in res.messages[0].content.text
            assert "marp_create_presentation" in res.messages[0].content.text

    @pytest.mark.asyncio
    async def test_design_for_documents_prompt(self):
        """Test design_for_documents prompt is available and has content."""
        async with Client(mcp) as client:
            res = await client.get_prompt("design_for_documents", {})
            assert res.messages[0].content.text
            assert "Document" in res.messages[0].content.text


class TestPromptContent:
    """Tests for prompt content quality."""

    @pytest.mark.asyncio
    async def test_design_thinking_has_anti_patterns(self):
        """Design thinking prompt should include anti-patterns guidance."""
        async with Client(mcp) as client:
            res = await client.get_prompt("design_thinking", {})
            text = res.messages[0].content.text
            assert "Anti-Patterns" in text
            assert "Never Do" in text

    @pytest.mark.asyncio
    async def test_color_strategy_has_contrast_info(self):
        """Color strategy prompt should include contrast requirements."""
        async with Client(mcp) as client:
            res = await client.get_prompt("color_strategy", {})
            text = res.messages[0].content.text
            assert "contrast" in text.lower()
            assert "4.5:1" in text  # WCAG requirement

    @pytest.mark.asyncio
    async def test_typography_has_web_safe_fonts(self):
        """Typography prompt should mention web-safe fonts."""
        async with Client(mcp) as client:
            res = await client.get_prompt("typography_principles", {})
            text = res.messages[0].content.text
            assert "Georgia" in text
            assert "Verdana" in text
            assert "Impact" in text
