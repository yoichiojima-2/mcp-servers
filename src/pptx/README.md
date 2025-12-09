# PPTX MCP Server

An MCP server for PowerPoint presentation creation and manipulation, inspired by the [Anthropic PPTX skill](https://github.com/anthropics/skills).

## Features

### Marp-Based Presentation Creation (Recommended)
- Create professionally-designed presentations from Markdown
- 6 distinctive themes with bold aesthetic directions
- Simple syntax: write Markdown, get beautiful PPTX
- Requires Node.js v18+ and a browser (Chrome/Edge/Firefox)

### Presentation Creation (Low-Level)
- Create new presentations with custom aspect ratios (16:9, 4:3, 16:10)
- Add slides with various layouts
- Add text boxes, shapes, images, and tables
- Set speaker notes

### Reading & Analysis
- Get presentation metadata and structure
- Extract text from all slides
- Get detailed shape information
- Read speaker notes

### Slide Manipulation
- Delete, duplicate, and reorder slides
- Apply templates to existing presentations

### HTML to PPTX Conversion
- Convert HTML with custom `<slide>` markup to PowerPoint
- Support for headings, paragraphs, lists, and formatted text
- Position elements with CSS-like syntax

### OOXML Operations (Advanced)
- Unpack PPTX files to edit XML directly
- Pack directories back into PPTX files
- Edit slide XML using XPath

## Installation

```bash
cd src/pptx
uv sync
```

For Marp features (recommended):
```bash
# Install Node.js v18+ from https://nodejs.org/
# Marp CLI is installed automatically via npx on first use
```

## Usage

### Run as MCP Server (stdio)

```bash
uv run python -m pptx_server
```

### Run as HTTP Server

```bash
TRANSPORT=sse PORT=8002 uv run python -m pptx_server
```

### Claude Code Configuration

Add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "pptx": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-servers/src/pptx", "python", "-m", "pptx_server"]
    }
  }
}
```

## Creating Presentations with Marp (Recommended)

Write slides in Markdown and convert to professionally-designed PPTX:

```markdown
---
marp: true
---

<!-- _class: lead -->
# My Presentation
A compelling subtitle

---

## Key Points

- First important point
- Second important point
- Third important point

---

<!-- _class: invert -->
## Thank You

Contact: hello@example.com
```

### Available Themes

Themes are provided by the **frontend-design** MCP server. Use `design_list_themes()` to see all options.

Available themes: `noir`, `brutalist`, `organic`, `neon`, `minimal`, `retro`

### Marp Tools

| Tool | Description |
|------|-------------|
| `marp_create_presentation` | Create PPTX from Markdown with a theme |
| `marp_create_presentation_from_file` | Create PPTX from a Markdown file |
| `marp_check_requirements` | Check if Node.js and browser are available |

For theme details, use `design_list_themes()` and `design_get_theme()` from the frontend-design server.

## All Available Tools

### Marp Tools (Recommended for New Presentations)

| Tool | Description |
|------|-------------|
| `marp_create_presentation` | Create PPTX from Markdown with a theme |
| `marp_create_presentation_from_file` | Create PPTX from a Markdown file |
| `marp_check_requirements` | Check Node.js and browser availability |

> **Note:** Theme listing and details are provided by the frontend-design MCP server (`design_list_themes`, `design_get_theme`).

### Presentation Creation (Low-Level)

| Tool | Description |
|------|-------------|
| `create_presentation` | Create a new PowerPoint presentation |
| `add_slide` | Add a new slide to a presentation |
| `add_text_box` | Add a text box to a slide |
| `add_shape` | Add a shape (rectangle, oval, etc.) to a slide |
| `add_image` | Add an image to a slide |
| `add_table` | Add a table to a slide |

### Reading & Analysis

| Tool | Description |
|------|-------------|
| `get_presentation_info` | Get presentation metadata and structure |
| `extract_text` | Extract all text from a presentation |
| `get_slide_shapes` | Get detailed information about shapes on a slide |
| `get_slide_notes` | Get speaker notes from slides |

### Slide Manipulation

| Tool | Description |
|------|-------------|
| `delete_slide` | Delete a slide from a presentation |
| `duplicate_slide` | Duplicate a slide |
| `reorder_slides` | Reorder slides in a presentation |
| `apply_template` | Apply a template's design to a presentation |
| `set_slide_notes` | Set speaker notes for a slide |

### HTML to PPTX

| Tool | Description |
|------|-------------|
| `html_to_pptx` | Convert HTML slides to PowerPoint |
| `html_file_to_pptx` | Convert an HTML file to PowerPoint |
| `validate_html_for_pptx` | Validate HTML for PPTX conversion |

### OOXML Operations (Advanced)

| Tool | Description |
|------|-------------|
| `unpack_pptx` | Unpack PPTX to view/edit XML |
| `pack_pptx` | Pack directory back into PPTX |
| `edit_slide_xml` | Edit slide XML directly using XPath |
| `export_slide_as_image` | Export a slide as an image |

## HTML to PPTX Format

For pixel-perfect control over positioning:

```html
<slide title="My Slide">
  <div style="left: 50pt; top: 100pt; width: 600pt; height: 300pt;">
    <h1 style="text-align: center;">Heading</h1>
    <p>Paragraph text with <b>bold</b> and <i>italic</i>.</p>
    <ul>
      <li>Bullet point 1</li>
      <li>Bullet point 2</li>
    </ul>
  </div>
</slide>
```

### Supported HTML Elements

- `<slide title="...">` - Container for each slide
- `<div style="...">` - Positioned container (use pt units)
- `<h1>`-`<h6>` - Headings with automatic sizing
- `<p>` - Paragraphs
- `<ul>/<ol>` with `<li>` - Lists
- `<b>`, `<i>`, `<u>` - Text formatting
- `<span style="color: #RRGGBB">` - Colored text
- `<img src="path" style="...">` - Images

## Dependencies

- `python-pptx` - PowerPoint file manipulation
- `fastmcp` - MCP server framework
- `lxml` - XML processing
- `pillow` - Image handling
- `frontend-design` - Workspace package for theme definitions

For Marp features:
- Node.js v18+ with npx
- Chrome, Edge, or Firefox (for PPTX export)

## Security Considerations

### Marp Conversion

The Marp conversion includes several security measures:

**Protected:**
- **Frontmatter injection**: Dangerous keys like `backgroundImage`, `html`, `script` are stripped
- **External resources**: `url()` and `@import` in style blocks are blocked
- **Multi-line attacks**: Both single-line and multi-line YAML blocks are sanitized
- **Path traversal**: System directories (`/etc`, `/usr`, etc.) are blocked
- **File extension**: Only `.pptx` output is allowed
- **Resource limits**: 2MB markdown size limit, 60-second timeout

**User responsibility:**
- **Inline HTML in markdown content**: HTML tags like `<style>`, `<script>` within the markdown body (not frontmatter) are NOT sanitized. Review presentations before sharing if markdown comes from untrusted sources.

### Recommendations

When processing markdown from untrusted sources:
1. Review the generated presentation before distribution
2. Consider running Marp with `--html false` if HTML is not needed (requires custom integration)
