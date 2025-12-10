from . import mcp


@mcp.prompt()
def pptx_workflow_overview() -> str:
    """Decision tree for PPTX workflows."""
    return """# PPTX Workflow Overview

## Creating New Presentations

Use **Marp workflow** - Markdown to PPTX with professional themes

- Write slides in simple Markdown syntax
- Choose from distinctive, professionally-designed themes
- Themes: `noir`, `brutalist`, `organic`, `neon`, `minimal`, `retro`
- Use `marp_create_presentation()` tool
- See `pptx_marp_workflow()` prompt for details

## Reading and Analyzing Existing Presentations

- `get_presentation_info(file_path)` - Get metadata and structure
- `extract_text(file_path)` - Extract all text content
- `get_slide_shapes(file_path, slide_number)` - Detailed shape info
- `get_slide_notes(file_path)` - Get speaker notes
- `export_slide_as_image(file_path, slide_number, output_path)` - Create thumbnails

See `pptx_analysis_tools()` prompt for details.

## Design Resources

For comprehensive design guidance, use the **frontend-design** MCP server:

- `design_list_themes()` - View available themes with aesthetics
- `design_get_theme(name)` - Get full theme details (colors, fonts, CSS)
- `design_suggest_palette(mood, industry)` - Get palette recommendations
- `design_check_contrast(fg, bg)` - Verify WCAG accessibility
"""


@mcp.prompt()
def pptx_marp_workflow() -> str:
    """Marp-based Markdown to PPTX workflow - the recommended approach."""
    return """# Creating PowerPoint with Marp (RECOMMENDED)

Marp converts Markdown to professionally-designed PPTX with distinctive themes
that avoid generic AI aesthetics.

## Available Themes

Each theme has a bold, intentional design direction:

| Theme | Aesthetic | Best For |
|-------|-----------|----------|
| `noir` | Editorial/Film Noir, high-contrast dark | Tech, cinema, premium brands |
| `brutalist` | Raw, bold, Swiss typography | Design, architecture, statements |
| `organic` | Warm, natural, earthy | Wellness, sustainability, lifestyle |
| `neon` | Cyberpunk, glowing accents | Gaming, tech startups, innovation |
| `minimal` | Swiss/Minimalist, refined | Professional, content-heavy |
| `retro` | 70s/80s nostalgic, geometric | Creative, fun, distinctive |

## Quick Start

Use `marp_create_presentation()` with Markdown:

```markdown
---
marp: true
---

<!-- _class: lead -->
# Presentation Title
Subtitle goes here

---

## First Topic

- Key point one
- Key point two
- Key point three

---

<!-- _class: invert -->
## Questions?

Contact: email@example.com
```

## Markdown Syntax

### Slide Separators
- Use `---` to separate slides
- First `---` ends the frontmatter

### Slide Classes
- `<!-- _class: lead -->` - Title/hero slides (centered, larger text)
- `<!-- _class: invert -->` - Inverted colors for accent slides

### Content Elements
- `# H1` through `###### H6` - Headings
- `- item` or `* item` - Bullet lists
- `1. item` - Numbered lists
- `**bold**` and `*italic*` - Text formatting
- `> quote` - Blockquotes
- `` `code` `` - Inline code
- `![alt](image.png)` - Images
- Tables with `|` syntax

## Requirements

- Node.js v18+ (for npx/marp-cli)
- A browser (Chrome, Edge, or Firefox) for PPTX export
- Use `marp_check_requirements()` to verify setup

## Workflow

1. Check requirements: `marp_check_requirements()`
2. List themes: `design_list_themes()` (from frontend-design server)
3. Create presentation: `marp_create_presentation(markdown, output_path, theme)`

For design principles and theme details, see the frontend-design server prompts.
"""


@mcp.prompt()
def pptx_analysis_tools() -> str:
    """Tools for analyzing existing presentations."""
    return """# Analyzing Existing Presentations

## Available Tools

### get_presentation_info(file_path)
Get metadata about a presentation:
- Number of slides
- Dimensions and aspect ratio
- Slide summary with titles and shape counts

### extract_text(file_path, slide_numbers?)
Extract all text content:
- Organized by slide
- Optional: specify slide numbers (e.g., "1,3,5")

### get_slide_shapes(file_path, slide_number)
Get JSON details about shapes on a slide:
- Shape type, position, dimensions
- Text content (if applicable)
- Image presence

### get_slide_notes(file_path, slide_number?)
Get speaker notes:
- Specific slide or all slides
- Returns formatted text

### export_slide_as_image(file_path, slide_number, output_path, width?)
Create slide thumbnail:
- Placeholder image (use LibreOffice for full render)
- Maintains aspect ratio
- Default width: 1920px

## Usage Examples

```python
# Get presentation overview
get_presentation_info("/path/to/slides.pptx")

# Extract text from specific slides
extract_text("/path/to/slides.pptx", "1,3,5")

# Get shape details for slide 2
get_slide_shapes("/path/to/slides.pptx", 2)

# Get all speaker notes
get_slide_notes("/path/to/slides.pptx")
```
"""
