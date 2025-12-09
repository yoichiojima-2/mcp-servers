"""Tests for frontend_design themes module."""

from frontend_design.themes import (
    PALETTES,
    THEMES,
    get_palette,
    get_theme,
    get_theme_colors,
    get_theme_css,
    list_palettes,
    list_themes,
)


class TestThemes:
    """Tests for theme functions."""

    def test_list_themes_returns_all_themes(self):
        """list_themes should return all defined themes."""
        themes = list_themes()
        assert len(themes) == len(THEMES)
        assert "noir" in themes
        assert "brutalist" in themes
        assert "organic" in themes
        assert "neon" in themes
        assert "minimal" in themes
        assert "retro" in themes

    def test_list_themes_includes_required_fields(self):
        """Each theme should have required fields."""
        themes = list_themes()
        for name, theme in themes.items():
            assert "name" in theme, f"Theme {name} missing 'name'"
            assert "aesthetic" in theme, f"Theme {name} missing 'aesthetic'"
            assert "description" in theme, f"Theme {name} missing 'description'"

    def test_get_theme_returns_theme_data(self):
        """get_theme should return full theme data."""
        theme = get_theme("noir")
        assert theme is not None
        assert theme["name"] == "Noir"
        assert "colors" in theme
        assert "fonts" in theme
        assert "marp_css" in theme

    def test_get_theme_returns_none_for_unknown(self):
        """get_theme should return None for unknown themes."""
        theme = get_theme("nonexistent")
        assert theme is None

    def test_get_theme_css_returns_css(self):
        """get_theme_css should return Marp CSS string."""
        css = get_theme_css("brutalist")
        assert css is not None
        assert "@theme brutalist" in css
        assert "section" in css

    def test_get_theme_css_returns_none_for_unknown(self):
        """get_theme_css should return None for unknown themes."""
        css = get_theme_css("nonexistent")
        assert css is None

    def test_get_theme_colors_returns_color_dict(self):
        """get_theme_colors should return color dictionary."""
        colors = get_theme_colors("neon")
        assert colors is not None
        assert "background" in colors
        assert "text" in colors
        assert "primary" in colors

    def test_get_theme_colors_returns_none_for_unknown(self):
        """get_theme_colors should return None for unknown themes."""
        colors = get_theme_colors("nonexistent")
        assert colors is None

    def test_theme_colors_are_valid_hex(self):
        """Theme colors should be valid hex codes."""
        for name in THEMES:
            colors = get_theme_colors(name)
            assert colors is not None
            for color_name, color_value in colors.items():
                assert color_value.startswith("#"), f"{name}.{color_name} should start with #"
                assert len(color_value) == 7, f"{name}.{color_name} should be 7 chars (#RRGGBB)"

    def test_theme_marp_css_is_valid(self):
        """Theme CSS should contain valid Marp directives."""
        for name in THEMES:
            theme = get_theme(name)
            css = theme["marp_css"]
            assert f"@theme {name}" in css, f"Theme {name} CSS missing @theme directive"
            assert "section" in css, f"Theme {name} CSS missing section styles"


class TestPalettes:
    """Tests for palette functions."""

    def test_list_palettes_returns_all_palettes(self):
        """list_palettes should return all defined palettes."""
        palettes = list_palettes()
        assert len(palettes) == len(PALETTES)

    def test_list_palettes_includes_required_fields(self):
        """Each palette should have required fields."""
        palettes = list_palettes()
        for name, palette in palettes.items():
            assert "name" in palette, f"Palette {name} missing 'name'"
            assert "description" in palette, f"Palette {name} missing 'description'"
            assert "colors" in palette, f"Palette {name} missing 'colors'"

    def test_get_palette_returns_palette_data(self):
        """get_palette should return palette data."""
        palette = get_palette("classic_blue")
        assert palette is not None
        assert "name" in palette
        assert "colors" in palette
        assert isinstance(palette["colors"], list)

    def test_get_palette_returns_none_for_unknown(self):
        """get_palette should return None for unknown palettes."""
        palette = get_palette("nonexistent")
        assert palette is None

    def test_palette_colors_are_valid_hex(self):
        """Palette colors should be valid hex codes."""
        for name in PALETTES:
            palette = get_palette(name)
            assert palette is not None
            for color in palette["colors"]:
                assert color.startswith("#"), f"{name} color {color} should start with #"
                assert len(color) == 7, f"{name} color {color} should be 7 chars (#RRGGBB)"


class TestThemeFonts:
    """Tests for theme font definitions."""

    def test_themes_have_fonts(self):
        """All themes should have font definitions."""
        for name in THEMES:
            theme = get_theme(name)
            assert "fonts" in theme, f"Theme {name} missing fonts"
            assert "heading" in theme["fonts"], f"Theme {name} missing heading font"
            assert "body" in theme["fonts"], f"Theme {name} missing body font"

    def test_heading_fonts_are_distinctive(self):
        """Heading fonts should not use Inter or Roboto (the most generic)."""
        # Arial can be intentional for brutalist/minimal themes
        very_generic = {"inter", "roboto"}
        for name in THEMES:
            theme = get_theme(name)
            heading = theme["fonts"]["heading"].lower()
            for generic in very_generic:
                assert generic not in heading, f"Theme {name} heading uses {generic}"
