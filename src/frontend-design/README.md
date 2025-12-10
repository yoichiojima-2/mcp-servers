# frontend-design

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

| Tool | Description |
|------|-------------|
| `design_list_themes` | List all available themes |
| `design_get_theme` | Get full theme details (colors, fonts, Marp CSS) |
| `design_get_theme_colors` | Get colors in hex, JSON, or CSS format |
| `design_list_palettes` | List all color palettes |
| `design_get_palette` | Get specific palette |
| `design_suggest_palette` | Suggest palette based on mood/industry |
| `design_check_contrast` | Check WCAG contrast ratio |

## Prompts

- `design_thinking` - Purpose, audience, and differentiation strategy
- `color_strategy` - Building intentional color palettes
- `typography_principles` - Distinctive font choices and hierarchy
- `layout_principles` - Visual structure and composition
- `visual_elements` - Shapes, borders, and decorative elements
- `design_for_presentations` - Presentation-specific guidance
- `design_for_documents` - Document design guidance

## Usage

### As MCP Server

```bash
uv run python -m frontend_design
```

### As Workspace Dependency

```toml
# In your pyproject.toml
[project]
dependencies = ["frontend-design"]

[tool.uv.sources]
frontend-design = { workspace = true }
```

```python
from frontend_design.themes import get_theme, list_themes
themes = list_themes()
theme = get_theme("noir")
```

See [server guide](../../docs/server-guide.md) for common CLI options.
