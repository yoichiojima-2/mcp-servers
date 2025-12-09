# Frontend Design MCP Server

MCP server providing design principles, themes, and color palettes for composable use across other MCP servers.

## Features

- **Design Prompts**: Comprehensive design guidance for presentations, documents, and web interfaces
- **Theme System**: Six distinctive themes with colors, fonts, and Marp CSS
- **Color Palettes**: Ready-to-use color palettes with mood/industry suggestions
- **Accessibility**: WCAG contrast checking tool

## Themes

| Theme | Aesthetic | Best For |
|-------|-----------|----------|
| `noir` | Editorial/Film Noir, high-contrast dark | Tech, cinema, premium brands |
| `brutalist` | Raw, bold, Swiss typography | Design, architecture, statements |
| `organic` | Warm, natural, earthy | Wellness, sustainability, lifestyle |
| `neon` | Cyberpunk, glowing accents | Gaming, tech startups, innovation |
| `minimal` | Swiss/Minimalist, refined | Professional, content-heavy |
| `retro` | 70s/80s nostalgic, geometric | Creative, fun, distinctive |

## Tools

### `design_list_themes()`
List all available themes with descriptions.

### `design_get_theme(theme_name)`
Get full theme details including colors, fonts, and Marp CSS.

### `design_get_theme_colors(theme_name, format)`
Get color palette in hex, JSON, or CSS variable format.

### `design_list_palettes()`
List all available color palettes.

### `design_get_palette(palette_name, format)`
Get specific palette in hex, JSON, or CSS format.

### `design_suggest_palette(mood, industry)`
Get palette suggestions based on mood or industry context.

### `design_check_contrast(foreground, background)`
Check WCAG contrast ratio between two colors.

## Prompts

- `design_thinking` - Purpose, audience, and differentiation strategy
- `color_strategy` - Building intentional color palettes
- `typography_principles` - Distinctive font choices and hierarchy
- `layout_principles` - Visual structure and composition
- `visual_elements` - Shapes, borders, and decorative elements
- `design_for_presentations` - Presentation-specific guidance
- `design_for_documents` - Document design guidance

## Requirements

- Python 3.12+
- FastMCP

## Installation

This server is designed to be used as a workspace dependency:

```toml
# In your pyproject.toml
[project]
dependencies = [
    "frontend-design",
]

[tool.uv.sources]
frontend-design = { workspace = true }
```

## Usage

Import themes in your code:

```python
from frontend_design.themes import get_theme, get_theme_css, list_themes

# Get available themes
themes = list_themes()

# Get a specific theme
theme = get_theme("noir")
colors = theme["colors"]
fonts = theme["fonts"]
css = theme["marp_css"]
```

## Testing

```bash
cd src/frontend-design
uv run pytest -v
```
