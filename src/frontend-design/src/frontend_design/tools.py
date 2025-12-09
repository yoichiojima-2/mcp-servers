"""
MCP tools for design-related operations.

Provides tools for listing themes, getting palettes, and suggesting colors.
"""

import json

from . import mcp
from .themes import PALETTES, THEMES, get_palette, get_theme, get_theme_colors, list_palettes, list_themes


@mcp.tool()
def design_list_themes() -> str:
    """
    List all available design themes.

    Each theme provides colors, fonts, and Marp CSS for presentations.

    Returns:
        Formatted list of themes with descriptions
    """
    themes = list_themes()
    result = ["# Available Design Themes\n"]

    for name, info in themes.items():
        result.append(f"## {info['name']} (`{name}`)")
        result.append(f"**Aesthetic**: {info['aesthetic']}")
        result.append(f"{info['description']}\n")

    return "\n".join(result)


@mcp.tool()
def design_get_theme(theme_name: str) -> str:
    """
    Get full details for a specific theme.

    Args:
        theme_name: Name of the theme (e.g., "noir", "brutalist")

    Returns:
        Theme details including colors, fonts, and CSS
    """
    theme = get_theme(theme_name)
    if not theme:
        available = ", ".join(THEMES.keys())
        return f"Error: Unknown theme '{theme_name}'. Available: {available}"

    result = [
        f"# {theme['name']} Theme",
        f"\n**Aesthetic**: {theme['aesthetic']}",
        f"\n{theme['description']}",
        "\n## Colors",
    ]

    for color_name, color_value in theme["colors"].items():
        result.append(f"- **{color_name}**: `{color_value}`")

    result.append("\n## Fonts")
    result.append(f"- **Heading**: {theme['fonts']['heading']}")
    result.append(f"- **Body**: {theme['fonts']['body']}")

    result.append("\n## Marp CSS")
    result.append("```css")
    result.append(theme["marp_css"])
    result.append("```")

    return "\n".join(result)


@mcp.tool()
def design_get_theme_colors(theme_name: str, format: str = "hex") -> str:
    """
    Get just the color palette for a theme.

    Args:
        theme_name: Name of the theme
        format: Output format - "hex", "json", or "css"

    Returns:
        Color palette in requested format
    """
    colors = get_theme_colors(theme_name)
    if not colors:
        available = ", ".join(THEMES.keys())
        return f"Error: Unknown theme '{theme_name}'. Available: {available}"

    if format == "json":
        return json.dumps(colors, indent=2)
    elif format == "css":
        lines = [":root {"]
        for name, value in colors.items():
            css_name = name.replace("_", "-")
            lines.append(f"  --color-{css_name}: {value};")
        lines.append("}")
        return "\n".join(lines)
    else:  # hex
        return "\n".join(f"{name}: {value}" for name, value in colors.items())


@mcp.tool()
def design_list_palettes() -> str:
    """
    List all available color palettes.

    Palettes are simpler than full themes - just colors for quick use.

    Returns:
        Formatted list of color palettes
    """
    palettes = list_palettes()
    result = ["# Available Color Palettes\n"]

    for name, info in palettes.items():
        colors = " → ".join(info["colors"])
        result.append(f"## {info['name']} (`{name}`)")
        result.append(f"{info['description']}")
        result.append(f"Colors: {colors}\n")

    return "\n".join(result)


@mcp.tool()
def design_get_palette(palette_name: str, format: str = "hex") -> str:
    """
    Get a specific color palette.

    Args:
        palette_name: Name of the palette
        format: Output format - "hex", "json", or "css"

    Returns:
        Color palette in requested format
    """
    palette = get_palette(palette_name)
    if not palette:
        available = ", ".join(PALETTES.keys())
        return f"Error: Unknown palette '{palette_name}'. Available: {available}"

    colors = palette["colors"]

    if format == "json":
        return json.dumps({"name": palette["name"], "colors": colors}, indent=2)
    elif format == "css":
        lines = [":root {"]
        for i, color in enumerate(colors):
            lines.append(f"  --palette-{i + 1}: {color};")
        lines.append("}")
        return "\n".join(lines)
    else:  # hex
        return "\n".join(colors)


@mcp.tool()
def design_suggest_palette(
    mood: str | None = None,
    industry: str | None = None,
) -> str:
    """
    Suggest color palettes based on mood or industry.

    Args:
        mood: Desired mood (e.g., "professional", "energetic", "calm", "bold")
        industry: Industry context (e.g., "tech", "healthcare", "finance", "creative")

    Returns:
        Suggested palettes with explanations
    """
    # Mood-based suggestions
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

    # Industry-based suggestions (breaking stereotypes)
    industry_map = {
        "tech": {
            "expected": "Blue gradients",
            "alternatives": ["neon", "brutalist", "noir"],
            "reason": "Stand out from the sea of blue tech sites",
        },
        "healthcare": {
            "expected": "Green and blue",
            "alternatives": ["organic", "minimal", "sage_terracotta"],
            "reason": "Warm, approachable feels more human",
        },
        "finance": {
            "expected": "Navy and gold",
            "alternatives": ["noir", "minimal", "deep_purple_emerald"],
            "reason": "Modern finance can be bold and innovative",
        },
        "creative": {
            "expected": "Bright, chaotic",
            "alternatives": ["brutalist", "retro", "neon"],
            "reason": "Distinctive aesthetics show creative capability",
        },
        "education": {
            "expected": "Primary colors",
            "alternatives": ["organic", "minimal", "teal_coral"],
            "reason": "Sophisticated palettes work for adult learners",
        },
        "food": {
            "expected": "Red and yellow",
            "alternatives": ["organic", "sage_terracotta", "burgundy_luxury"],
            "reason": "Earthy, natural tones feel more authentic",
        },
    }

    result = ["# Palette Suggestions\n"]

    if mood and mood.lower() in mood_map:
        result.append(f"## Based on mood: {mood}")
        for theme_name in mood_map[mood.lower()]:
            if theme_name in THEMES:
                theme = THEMES[theme_name]
                result.append(f"- **{theme['name']}**: {theme['description']}")
            elif theme_name in PALETTES:
                palette = PALETTES[theme_name]
                result.append(f"- **{palette['name']}**: {palette['description']}")
        result.append("")

    if industry and industry.lower() in industry_map:
        info = industry_map[industry.lower()]
        result.append(f"## Based on industry: {industry}")
        result.append(f"**Expected/clichéd**: {info['expected']}")
        result.append(f"**Why break the mold**: {info['reason']}")
        result.append("\n**Suggested alternatives**:")
        for theme_name in info["alternatives"]:
            if theme_name in THEMES:
                theme = THEMES[theme_name]
                result.append(f"- **{theme['name']}**: {theme['description']}")
        result.append("")

    if not mood and not industry:
        result.append("Provide a `mood` or `industry` to get tailored suggestions.")
        result.append("\n**Available moods**: " + ", ".join(mood_map.keys()))
        result.append("**Available industries**: " + ", ".join(industry_map.keys()))

    return "\n".join(result)


@mcp.tool()
def design_check_contrast(
    foreground: str,
    background: str,
) -> str:
    """
    Check color contrast ratio for accessibility.

    Args:
        foreground: Text color (hex, e.g., "#FFFFFF")
        background: Background color (hex, e.g., "#000000")

    Returns:
        Contrast ratio and WCAG compliance level
    """

    def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def luminance(r: int, g: int, b: int) -> float:
        def channel(c: int) -> float:
            c = c / 255
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)

    try:
        fg_rgb = hex_to_rgb(foreground)
        bg_rgb = hex_to_rgb(background)
    except (ValueError, IndexError):
        return "Error: Invalid hex color format. Use #RRGGBB format."

    fg_lum = luminance(*fg_rgb)
    bg_lum = luminance(*bg_rgb)

    lighter = max(fg_lum, bg_lum)
    darker = min(fg_lum, bg_lum)
    ratio = (lighter + 0.05) / (darker + 0.05)

    # WCAG levels
    if ratio >= 7:
        level = "AAA (Enhanced)"
        status = "Excellent"
    elif ratio >= 4.5:
        level = "AA (Normal text)"
        status = "Good"
    elif ratio >= 3:
        level = "AA (Large text only)"
        status = "Limited"
    else:
        level = "Fails WCAG"
        status = "Poor"

    return f"""# Contrast Check

**Foreground**: {foreground}
**Background**: {background}

**Contrast Ratio**: {ratio:.2f}:1
**WCAG Level**: {level}
**Status**: {status}

## Guidelines
- Normal text (< 18pt): Needs 4.5:1 minimum
- Large text (≥ 18pt or 14pt bold): Needs 3:1 minimum
- Enhanced accessibility (AAA): Needs 7:1

## Recommendation
{"This combination is accessible for all text sizes." if ratio >= 4.5 else "Consider using a lighter foreground or darker background for better readability." if ratio < 4.5 else ""}
"""
