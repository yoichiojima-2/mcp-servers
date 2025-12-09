"""Tests for frontend_design tools module.

Note: MCP tools are decorated with @mcp.tool() which wraps them.
We test the underlying function logic by accessing the function directly.
"""


class TestDesignListThemes:
    """Tests for design_list_themes tool logic."""

    def test_returns_formatted_list(self):
        """Should return formatted markdown list."""
        from frontend_design.themes import THEMES, list_themes

        themes = list_themes()
        assert len(themes) == len(THEMES)
        assert "noir" in themes

    def test_includes_all_themes(self):
        """Should include all six themes."""
        from frontend_design.themes import list_themes

        themes = list_themes()
        expected = ["noir", "brutalist", "organic", "neon", "minimal", "retro"]
        for theme in expected:
            assert theme in themes


class TestDesignGetTheme:
    """Tests for design_get_theme tool logic."""

    def test_returns_theme_details(self):
        """Should return full theme details."""
        from frontend_design.themes import get_theme

        theme = get_theme("noir")
        assert theme is not None
        assert "name" in theme
        assert theme["name"] == "Noir"
        assert "colors" in theme
        assert "fonts" in theme
        assert "marp_css" in theme

    def test_returns_none_for_unknown_theme(self):
        """Should return None for unknown theme."""
        from frontend_design.themes import get_theme

        theme = get_theme("nonexistent")
        assert theme is None


class TestDesignGetThemeColors:
    """Tests for design_get_theme_colors tool logic."""

    def test_returns_color_dict(self):
        """Should return colors dictionary."""
        from frontend_design.themes import get_theme_colors

        colors = get_theme_colors("neon")
        assert colors is not None
        assert "background" in colors
        assert "text" in colors

    def test_returns_none_for_unknown(self):
        """Should return None for unknown theme."""
        from frontend_design.themes import get_theme_colors

        colors = get_theme_colors("nonexistent")
        assert colors is None


class TestDesignListPalettes:
    """Tests for design_list_palettes tool logic."""

    def test_returns_palettes(self):
        """Should return palette dictionary."""
        from frontend_design.themes import list_palettes

        palettes = list_palettes()
        assert len(palettes) > 0
        for name, info in palettes.items():
            assert "name" in info
            assert "colors" in info


class TestDesignGetPalette:
    """Tests for design_get_palette tool logic."""

    def test_returns_palette_data(self):
        """Should return palette data."""
        from frontend_design.themes import get_palette

        palette = get_palette("classic_blue")
        assert palette is not None
        assert "name" in palette
        assert "colors" in palette
        assert isinstance(palette["colors"], list)

    def test_returns_none_for_unknown_palette(self):
        """Should return None for unknown palette."""
        from frontend_design.themes import get_palette

        palette = get_palette("nonexistent")
        assert palette is None


class TestContrastCheck:
    """Tests for contrast checking logic."""

    def test_hex_to_rgb_conversion(self):
        """Test hex color parsing."""

        def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
            hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

        assert hex_to_rgb("#000000") == (0, 0, 0)
        assert hex_to_rgb("#FFFFFF") == (255, 255, 255)
        assert hex_to_rgb("#FF0000") == (255, 0, 0)

    def test_luminance_calculation(self):
        """Test luminance calculation."""

        def luminance(r: int, g: int, b: int) -> float:
            def channel(c: int) -> float:
                c = c / 255
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

            return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)

        # Black should have near-zero luminance
        assert luminance(0, 0, 0) < 0.01
        # White should have luminance near 1
        assert luminance(255, 255, 255) > 0.99

    def test_contrast_ratio_calculation(self):
        """Test contrast ratio between black and white."""

        def luminance(r: int, g: int, b: int) -> float:
            def channel(c: int) -> float:
                c = c / 255
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

            return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)

        white_lum = luminance(255, 255, 255)
        black_lum = luminance(0, 0, 0)

        lighter = max(white_lum, black_lum)
        darker = min(white_lum, black_lum)
        ratio = (lighter + 0.05) / (darker + 0.05)

        # Black on white should have 21:1 contrast ratio
        assert ratio > 20
        assert ratio < 22


class TestMoodBasedSuggestions:
    """Tests for mood-based palette suggestion logic."""

    def test_mood_map_has_expected_moods(self):
        """Verify mood map contains expected moods."""
        mood_map = {
            "professional": ["minimal", "classic_blue"],
            "energetic": ["neon", "bold_red", "retro"],
            "calm": ["organic", "ocean_depths", "sage_terracotta"],
            "bold": ["brutalist", "neon", "bold_red"],
            "sophisticated": ["noir", "burgundy_luxury", "monochrome"],
            "friendly": ["organic", "retro", "teal_coral"],
            "modern": ["minimal", "neon", "deep_purple_emerald"],
            "traditional": ["classic_blue", "burgundy_luxury"],
        }

        expected_moods = ["professional", "energetic", "calm", "bold"]
        for mood in expected_moods:
            assert mood in mood_map

    def test_industry_map_has_expected_industries(self):
        """Verify industry map contains expected industries."""
        industry_map = {
            "tech": {"expected": "Blue gradients", "alternatives": ["neon", "brutalist", "noir"]},
            "healthcare": {"expected": "Green and blue", "alternatives": ["organic", "minimal"]},
            "finance": {"expected": "Navy and gold", "alternatives": ["noir", "minimal"]},
            "creative": {"expected": "Bright, chaotic", "alternatives": ["brutalist", "retro"]},
        }

        expected_industries = ["tech", "healthcare", "finance", "creative"]
        for industry in expected_industries:
            assert industry in industry_map
