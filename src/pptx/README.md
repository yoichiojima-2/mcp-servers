# PPTX MCP Server

An MCP server for PowerPoint presentation creation and analysis, using Marp for professional-quality output.

## Features

### Marp-Based Presentation Creation (Recommended)
- Create professionally-designed presentations from Markdown
- 6 distinctive themes with bold aesthetic directions
- Simple syntax: write Markdown, get beautiful PPTX
- Requires Node.js v18+ and a browser (Chrome/Edge/Firefox)

### Reading & Analysis
- Get presentation metadata and structure
- Extract text from all slides
- Get detailed shape information
- Read speaker notes

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

## Available Tools

### Marp Tools (Recommended for New Presentations)

| Tool | Description |
|------|-------------|
| `marp_create_presentation` | Create PPTX from Markdown with a theme |
| `marp_create_presentation_from_file` | Create PPTX from a Markdown file |
| `marp_check_requirements` | Check Node.js and browser availability |

> **Note:** Theme listing and details are provided by the frontend-design MCP server (`design_list_themes`, `design_get_theme`).

### Reading & Analysis

| Tool | Description |
|------|-------------|
| `get_presentation_info` | Get presentation metadata and structure |
| `extract_text` | Extract all text from a presentation |
| `get_slide_shapes` | Get detailed information about shapes on a slide |
| `get_slide_notes` | Get speaker notes from slides |
| `get_slide_export_instructions` | Get instructions for exporting a slide as image |

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
