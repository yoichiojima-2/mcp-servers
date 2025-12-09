from . import mcp


@mcp.prompt()
def pptx_workflow_overview() -> str:
    """Decision tree for PPTX workflows - choosing the right approach."""
    return """# PPTX Workflow Overview

## Choosing Your Workflow

### Creating New Presentation (RECOMMENDED)
→ Use **Marp** workflow - Markdown to PPTX with professional themes
- Write slides in simple Markdown syntax
- Choose from distinctive, professionally-designed themes
- Themes: `noir`, `brutalist`, `organic`, `neon`, `minimal`, `retro`
- Use `marp_create_presentation()` tool
- See `pptx_marp_workflow()` prompt for details

### Reading and Analyzing Content
- **Text extraction**: `markitdown path-to-file.pptx` - Convert to markdown
- **Raw XML access**: Unpack with `python ooxml/scripts/unpack.py` for comments, speaker notes, layouts, animations

### Creating Presentation with Pixel-Perfect Control
→ Use **html2pptx** workflow (when you need precise positioning)
- Create HTML slides with proper dimensions (720pt × 405pt for 16:9)
- Convert to PowerPoint with accurate positioning
- See `pptx_html2pptx()` prompt for details

### Creating Presentation from Existing Template
→ Use **template workflow**
- Extract template text and create visual thumbnails
- Analyze template inventory
- Duplicate, reorder, delete slides
- Replace placeholder text
- See `pptx_template_workflow()` prompt for details

### Editing Existing Presentation
→ Use **OOXML editing** workflow
- Unpack presentation to XML
- Edit XML files (primarily slide{N}.xml)
- Validate immediately after each edit
- Pack final presentation
- See `pptx_ooxml_editing()` prompt for details

## Key File Structures (Unpacked PPTX)
- `ppt/presentation.xml` - Main presentation metadata
- `ppt/slides/slide{N}.xml` - Individual slide contents
- `ppt/notesSlides/notesSlide{N}.xml` - Speaker notes
- `ppt/comments/modernComment_*.xml` - Comments
- `ppt/slideLayouts/` - Layout templates
- `ppt/slideMasters/` - Master slide templates
- `ppt/theme/` - Theme and styling
- `ppt/media/` - Images and media
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
def pptx_html2pptx() -> str:
    """HTML to PowerPoint creation workflow and design principles."""
    return """# Creating PowerPoint with html2pptx

## Design Principles (CRITICAL)

**Before creating any presentation**, analyze the content and choose design elements:

1. **Consider the subject matter**: What tone, industry, or mood does it suggest?
2. **Check for branding**: Consider company/organization brand colors
3. **Match palette to content**: Select colors that reflect the subject
4. **State your approach**: Explain design choices before writing code

**Requirements**:
- ✅ State your content-informed design approach BEFORE writing code
- ✅ Use web-safe fonts only: Arial, Helvetica, Times New Roman, Georgia, Courier New, Verdana, Tahoma, Trebuchet MS, Impact
- ✅ Create clear visual hierarchy through size, weight, and color
- ✅ Ensure readability: strong contrast, appropriately sized text, clean alignment
- ✅ Be consistent: repeat patterns, spacing, visual language

## Color Palette Selection

**Think beyond defaults**:
- Topic, industry, mood, energy level, target audience
- Be adventurous - healthcare doesn't have to be green, finance doesn't have to be navy
- Pick 3-5 colors that work together
- Ensure contrast for readability

**Example palettes** (for inspiration):
1. Classic Blue: #1C2833, #2E4053, #AAB7B8, #F4F6F6
2. Teal & Coral: #5EA8A7, #277884, #FE4447, #FFFFFF
3. Bold Red: #C0392B, #E74C3C, #F39C12, #F1C40F, #2ECC71
4. Burgundy Luxury: #5D1D2E, #951233, #C15937, #997929
5. Deep Purple & Emerald: #B165FB, #181B24, #40695B, #FFFFFF
6. Sage & Terracotta: #87A96B, #E07A5F, #F4F1DE, #2C2C2C

## Layout Tips

**For slides with charts or tables**:
- **Two-column layout (PREFERRED)**: Header spanning full width, then columns (40%/60% split)
- **Full-slide layout**: Let content take up entire slide for maximum impact
- **NEVER vertically stack**: Don't place charts/tables below text in single column

## Workflow

1. **MANDATORY**: Read `html2pptx.md` completely (no range limits) for syntax and formatting rules
2. Create HTML file for each slide (720pt × 405pt for 16:9)
   - Use `<p>`, `<h1>`-`<h6>`, `<ul>`, `<ol>` for text
   - Use `class="placeholder"` for chart/table areas
   - **CRITICAL**: Rasterize gradients/icons as PNG using Sharp first
3. Create JavaScript file using `html2pptx.js` library
   - Use `html2pptx()` function
   - Add charts/tables to placeholders via PptxGenJS API
   - Save with `pptx.writeFile()`
4. **Visual validation**: Generate thumbnails and inspect
   - `python scripts/thumbnail.py output.pptx workspace/thumbnails --cols 4`
   - Check for: text cutoff, overlap, positioning, contrast issues
   - Adjust HTML and regenerate until correct

## Visual Details Options

**Typography**: Extreme size contrast, all-caps headers, monospace for data
**Geometric**: Diagonal dividers, asymmetric columns, rotated text
**Borders**: Thick single-color, L-shaped, corner brackets
**Backgrounds**: Solid color blocks, split backgrounds, edge-to-edge bands
**Charts**: Monochrome with accent color, horizontal bars, minimal gridlines
"""


@mcp.prompt()
def pptx_ooxml_editing() -> str:
    """OOXML-based editing workflow for existing presentations."""
    return """# Editing Existing PowerPoint (OOXML)

## Workflow

1. **MANDATORY**: Read `ooxml.md` completely (~500 lines, no range limits)
   - Detailed guidance on OOXML structure and editing
2. **Unpack**: `python ooxml/scripts/unpack.py <office_file> <output_dir>`
3. **Edit XML**: Primarily `ppt/slides/slide{N}.xml` and related files
4. **CRITICAL - Validate**: After EACH edit, validate before proceeding
   - `python ooxml/scripts/validate.py <dir> --original <file>`
   - Fix any validation errors immediately
5. **Pack**: `python ooxml/scripts/pack.py <input_directory> <office_file>`

## Key XML Files

**Slides**: `ppt/slides/slide1.xml`, `slide2.xml`, etc.
**Notes**: `ppt/notesSlides/notesSlide1.xml`, etc.
**Comments**: `ppt/comments/modernComment_*.xml`
**Layouts**: `ppt/slideLayouts/` - Layout templates
**Masters**: `ppt/slideMasters/` - Master slide templates
**Theme**: `ppt/theme/theme1.xml` - Colors and fonts

## Typography and Color Extraction

**When emulating a design**:
1. Read theme: `ppt/theme/theme1.xml` for `<a:clrScheme>` and `<a:fontScheme>`
2. Sample slide: `ppt/slides/slide1.xml` for actual font usage (`<a:rPr>`)
3. Search patterns: Use grep for color (`<a:solidFill>`, `<a:srgbClr>`) and fonts

## Converting to Images

**Two-step process**:
1. Convert to PDF: `soffice --headless --convert-to pdf template.pptx`
2. Convert PDF to JPEG: `pdftoppm -jpeg -r 150 template.pdf slide`
   - Creates `slide-1.jpg`, `slide-2.jpg`, etc.
   - Options: `-f N` (first page), `-l N` (last page), `-r 150` (resolution)
"""


@mcp.prompt()
def pptx_template_workflow() -> str:
    """Using existing templates to create new presentations."""
    return """# Creating PowerPoint Using Templates

## Workflow

### 1. Extract Template Text and Create Thumbnails
```bash
# Extract text
python -m markitdown template.pptx > template-content.md

# Create thumbnail grids (for visual analysis)
python scripts/thumbnail.py template.pptx
```

Read `template-content.md` completely (no range limits)

### 2. Analyze Template and Save Inventory

**Visual Analysis**: Review thumbnail grids for layouts, design patterns, structure

Create `template-inventory.md`:
```markdown
# Template Inventory Analysis
**Total Slides: [count]**
**IMPORTANT: Slides are 0-indexed (first slide = 0, last = count-1)**

## [Category Name]
- Slide 0: [Layout code] - Description/purpose
- Slide 1: [Layout code] - Description/purpose
[... EVERY slide listed individually ...]
```

**Using thumbnails**: Identify layout patterns, image placeholders, design consistency

### 3. Create Presentation Outline

**CRITICAL - Match Layout to Content**:
- Single-column: Unified narrative or single topic
- Two-column: ONLY for exactly 2 distinct items
- Three-column: ONLY for exactly 3 distinct items
- Image + text: ONLY when you have actual images
- Quote layouts: ONLY for actual quotes with attribution
- Count content pieces BEFORE selecting layout
- Don't force content into mismatched layouts

Save `outline.md` with template mapping:
```python
# Template slides to use (0-based indexing)
# WARNING: Verify indices within range! 73 slides = indices 0-72
template_mapping = [
    0,   # Title/Cover
    34,  # Title and body
    34,  # Duplicate for second slide
    50,  # Quote
    54,  # Closing + Text
]
```

### 4. Rearrange Slides
```bash
python scripts/rearrange.py template.pptx working.pptx 0,34,34,50,52
```

### 5. Extract ALL Text Inventory
```bash
python scripts/inventory.py working.pptx text-inventory.json
```

Read `text-inventory.json` completely (no range limits)

**Inventory structure**:
- Slides: "slide-0", "slide-1", etc.
- Shapes: Ordered visually as "shape-0", "shape-1"
- Placeholder types: TITLE, CENTER_TITLE, SUBTITLE, BODY, OBJECT, or null
- Properties: Only non-default values included

### 6. Generate Replacement Text

**CRITICAL**:
- First verify which shapes exist in inventory
- Validation shows errors for non-existent shapes/slides
- ALL shapes cleared unless you provide "paragraphs"
- Don't include "paragraphs" for shapes you want to clear
- When `bullet: true`, DON'T include bullet symbols in text
- Include paragraph properties from original inventory

**Essential formatting**:
- Headers/titles: `"bold": true`
- List items: `"bullet": true, "level": 0`
- Preserve alignment: `"alignment": "CENTER"`
- Colors: `"color": "FF0000"` or `"theme_color": "DARK_1"`

Example paragraphs:
```json
"paragraphs": [
  {
    "text": "New title",
    "alignment": "CENTER",
    "bold": true
  },
  {
    "text": "Bullet point without symbol",
    "bullet": true,
    "level": 0
  }
]
```

Save to `replacement-text.json`

### 7. Apply Replacements
```bash
python scripts/replace.py working.pptx replacement-text.json output.pptx
```

Validates shapes exist and applies formatting automatically

## Creating Thumbnail Grids

```bash
# Basic usage
python scripts/thumbnail.py template.pptx

# Custom options
python scripts/thumbnail.py template.pptx workspace/analysis --cols 4
```

**Features**:
- Default: 5 columns, max 30 slides per grid
- Range: 3-6 columns
- Zero-indexed slide labels
"""


@mcp.prompt()
def pptx_design_principles() -> str:
    """Design principles for presentations - references frontend-design server."""
    return """# PPTX Design Principles

For comprehensive design guidance, use the **frontend-design** MCP server.

## Design Prompts (via frontend-design)
- `design_thinking` - Purpose, audience, and differentiation strategy
- `color_strategy` - Building intentional color palettes
- `typography_principles` - Distinctive font choices and hierarchy
- `layout_principles` - Visual structure and composition
- `design_for_presentations` - Presentation-specific guidance

## Design Tools (via frontend-design)
- `design_list_themes()` - View available themes with aesthetics
- `design_get_theme(name)` - Get full theme details (colors, fonts, CSS)
- `design_suggest_palette(mood, industry)` - Get palette recommendations
- `design_check_contrast(fg, bg)` - Verify WCAG accessibility

For theme details and design guidance, query the frontend-design server.
"""
