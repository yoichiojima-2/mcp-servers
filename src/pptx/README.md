# pptx

MCP server for PowerPoint presentation creation and analysis, using Marp for professional-quality output.

## Features

### Marp-Based Creation (Recommended)
- Create presentations from Markdown with professional themes
- 6 distinctive themes: `noir`, `brutalist`, `organic`, `neon`, `minimal`, `retro`
- Requires Node.js v18+ and a browser (Chrome/Edge/Firefox)

### Reading & Analysis
- Get presentation metadata and structure
- Extract text from all slides
- Get detailed shape information
- Read speaker notes
- Export slides as images (requires LibreOffice)

## Tools

| Tool | Description |
|------|-------------|
| `marp_create_presentation` | Create PPTX from Markdown with a theme |
| `marp_create_presentation_from_file` | Create PPTX from a Markdown file |
| `marp_check_requirements` | Check Node.js and browser availability |
| `get_presentation_info` | Get presentation metadata and structure |
| `extract_text` | Extract all text from a presentation |
| `get_slide_shapes` | Get shape details for a slide |
| `get_slide_notes` | Get speaker notes |
| `export_slide_as_image` | Export slides as PNG (requires LibreOffice) |

## Requirements

- Python 3.12+
- Node.js v18+ (for Marp)
- Chrome, Edge, or Firefox (for PPTX export)
- LibreOffice (optional, for slide image export)

## Marp Markdown Syntax

```markdown
---
marp: true
---

<!-- _class: lead -->
# My Presentation
A compelling subtitle

---

## Key Points
- First point
- Second point

---

<!-- _class: invert -->
## Thank You
```

## Security

Marp conversion includes security measures:
- Frontmatter injection protection (blocks `backgroundImage`, `html`, `script`)
- External resource blocking (`url()`, `@import`)
- Path traversal prevention
- 2MB markdown size limit, 60-second timeout

## Usage

```bash
uv run python -m pptx_mcp
```

See [server guide](../../docs/server-guide.md) for common CLI options.

## Module Naming

The module is named `pptx_mcp` (not `pptx`) to avoid a circular import conflict with the `python-pptx` library. When Python imports `from pptx import Presentation`, it needs to find the library, not our module.
