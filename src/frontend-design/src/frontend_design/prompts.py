"""
Design prompts for creating distinctive, memorable artifacts.

These prompts guide creation of presentations, documents, and interfaces
that avoid generic "AI slop" aesthetics.
"""

from . import mcp


@mcp.prompt()
def design_thinking() -> str:
    """Core design thinking process - use before creating any visual artifact."""
    return """# Design Thinking

Before creating any visual artifact (presentation, document, interface),
commit to a BOLD aesthetic direction. Both maximalism and refined minimalism
work when executed with intention.

## Questions to Answer First

### 1. Purpose
- What problem does this artifact solve?
- Who is the audience?
- What action should they take after seeing it?

### 2. Tone & Direction
Pick a specific aesthetic direction. Examples:

| Direction | Characteristics |
|-----------|-----------------|
| Brutally Minimal | Extreme whitespace, stark typography, no decoration |
| Maximalist | Rich textures, layered elements, bold colors |
| Retro-Futuristic | Vintage meets modern, nostalgic with a twist |
| Organic/Natural | Warm tones, soft curves, earthy palette |
| Luxury/Refined | Elegant typography, muted sophistication |
| Playful/Toy-like | Bright colors, rounded shapes, fun energy |
| Editorial/Magazine | Strong typography, asymmetric layouts |
| Brutalist/Raw | Exposed structure, bold geometry, industrial |
| Art Deco/Geometric | Symmetry, gold accents, decorative patterns |
| Industrial/Utilitarian | Function-first, technical, grid-based |

### 3. Differentiation
- What makes this UNFORGETTABLE?
- What's the one thing someone will remember?
- How does it stand out from typical AI-generated content?

## Anti-Patterns (Never Do)

- Using Inter, Roboto, or Arial as default
- Purple/blue gradient backgrounds
- Generic stock photo aesthetics
- Cookie-cutter component layouts
- Predictable color schemes
- Playing it safe

## Commit to Your Direction

State your design approach BEFORE creating:

> "This presentation uses a brutalist aesthetic with Impact typography,
> a red/black/white palette, and aggressive geometric shapes to convey
> urgency and importance for a product launch."

This forces intentionality and prevents generic output.
"""


@mcp.prompt()
def color_strategy() -> str:
    """Color palette building and strategy."""
    return """# Color Strategy

Build intentional color palettes that avoid cliched defaults.

## The 60-30-10 Rule

- **60% Dominant**: Background, large areas
- **30% Secondary**: Supporting elements, containers
- **10% Accent**: Calls to action, emphasis, key data

## Breaking Expectations

| Industry | Expected Colors | Unexpected Alternatives |
|----------|-----------------|------------------------|
| Healthcare | Green, blue, white | Warm terracotta, sage, cream |
| Finance | Navy, gold, gray | Deep purple, coral, charcoal |
| Tech | Blue gradients | Neon + dark, brutalist black/white |
| Food | Red, yellow, green | Muted earth tones, sophisticated navy |
| Education | Primary colors | Sophisticated muted palette |

## Palette Building Process

1. **Start with mood**: What emotion should this evoke?
2. **Choose a dominant**: This sets the overall feel
3. **Add complementary**: Creates visual interest
4. **Pick an accent**: For emphasis and action
5. **Test contrast**: Ensure readability

## Example Palettes

### Noir (Dark Editorial)
- Background: #0A0A0A (near black)
- Surface: #141414 (dark gray)
- Text: #E8E8E8 (off-white)
- Accent: #FF3B3B (vibrant red)

### Organic (Natural Warmth)
- Background: #FDFBF7 (warm white)
- Surface: #F5F0E8 (cream)
- Primary: #2D3A2D (forest green)
- Accent: #B8860B (golden brown)

### Neon (Cyberpunk)
- Background: #0D0D1A (deep purple-black)
- Text: #E0E0FF (cool white)
- Primary: #00FFCC (electric cyan)
- Secondary: #FF00AA (hot pink)

### Brutalist (Bold Contrast)
- Background: #F5F5F0 (warm gray)
- Text: #1A1A1A (near black)
- Accent: #0000FF (pure blue)
- Secondary: #FF0000 (pure red)

## Contrast Requirements

- **Normal text**: Minimum 4.5:1 contrast ratio
- **Large text**: Minimum 3:1 contrast ratio
- **Interactive elements**: Clear visual distinction

## Tools for Validation

- Check contrast at: webaim.org/resources/contrastchecker
- Test for color blindness compatibility
- View in grayscale to check hierarchy
"""


@mcp.prompt()
def typography_principles() -> str:
    """Typography selection and hierarchy."""
    return """# Typography Principles

Typography is the most important design element. Distinctive type choices
immediately separate memorable designs from generic AI output.

## Font Pairing Strategy

Pair a **display font** (headings) with a **body font** (content):

| Display | Body | Aesthetic |
|---------|------|-----------|
| Georgia | Verdana | Classic editorial |
| Impact | Trebuchet MS | Bold statements |
| Times New Roman | Arial | Traditional professional |
| Courier New | Arial | Technical/code-focused |

## Web-Safe Fonts with Character

Avoid defaulting to Inter, Roboto, or system fonts. These web-safe
options have more personality:

### Serif (Classic, Editorial)
- **Georgia** - Elegant, readable, excellent for body text
- **Times New Roman** - Traditional, authoritative
- **Palatino** - Refined, literary feel

### Sans-Serif (Modern, Clean)
- **Trebuchet MS** - Friendly, distinctive
- **Verdana** - Highly readable, slightly wide
- **Tahoma** - Compact, professional

### Display (Headlines Only)
- **Impact** - Bold statements, all-caps works well
- **Arial Black** - Heavy, attention-grabbing

### Monospace (Data, Code)
- **Courier New** - Technical, typewriter feel
- **Consolas** - Modern monospace

## Hierarchy Through Size

Create dramatic contrast between heading levels:

| Element | Size | Weight | Spacing |
|---------|------|--------|---------|
| H1 | 48-72pt | Bold | Tight (-0.02em) |
| H2 | 32-40pt | Bold | Normal |
| H3 | 24-28pt | SemiBold | Normal |
| Body | 16-20pt | Regular | Relaxed (1.6-1.8 line-height) |
| Caption | 12-14pt | Regular | Relaxed |

## Typography Treatments

### Headlines
- Extreme size (3-4x body text)
- All-caps with letter-spacing for impact
- Tight line-height for multi-line headings

### Body Text
- Generous line-height (1.6-1.8)
- Optimal line length (45-75 characters)
- Left-aligned for readability

### Emphasis
- **Bold** for importance
- *Italic* for terms and quotes
- Accent color for key data
- Background color blocks for call-outs

### Numbers & Data
- Monospace fonts for tables
- Oversized numbers for key metrics
- Tabular figures for alignment
"""


@mcp.prompt()
def layout_principles() -> str:
    """Layout, spacing, and composition principles."""
    return """# Layout Principles

Strong layouts create visual hierarchy and guide the eye through content.

## Core Concepts

### Alignment
- Use a consistent grid (4, 8, or 12 columns)
- Align elements to create invisible lines
- Break alignment intentionally for emphasis

### Proximity
- Group related items together
- Use whitespace to separate unrelated elements
- Distance implies relationship

### Contrast
- Size contrast creates hierarchy
- Color contrast draws attention
- Weight contrast organizes information

## Layout Patterns

### Z-Pattern (Scanning)
Best for: Landing pages, simple presentations
```
[Logo/Title]............[Nav/Action]
            ↘
       [Main Content]
            ↘
[Call-to-Action]..........[Secondary]
```

### F-Pattern (Reading)
Best for: Text-heavy content, documentation
```
[Header spans full width-----------------]
[Important content starts here]
[Continues with key points]
[Then detailed content below]
```

### Asymmetric Split
Best for: Impact, visual interest
```
[60% Content Area     | 40% Visual/Accent]
[Major information    | Supporting image ]
[Detailed text        | or graphic      ]
```

## Presentation Layouts

### Title Slide
- Center-weighted or left-aligned
- Generous vertical space
- Clear hierarchy: Title > Subtitle > Attribution

### Content Slides
- **Never** vertically stack chart below text
- Two-column preferred for data + context
- Leave breathing room (padding)

### Data Slides
- Let charts/tables take center stage
- Minimal surrounding text
- Clear labels on data, not in legends

## Spacing Guidelines

### Macro Spacing (Between Sections)
- Use consistent multiples (e.g., 24px, 48px, 96px)
- More space = more importance
- Asymmetric spacing creates interest

### Micro Spacing (Within Elements)
- Consistent padding in containers
- Text needs breathing room
- Icons need space from text

## Visual Balance

### Symmetrical
- Formal, stable, traditional
- Good for: corporate, institutional

### Asymmetrical
- Dynamic, modern, energetic
- Good for: creative, startups, marketing

### Radial
- Focus on center point
- Good for: single key message
"""


@mcp.prompt()
def visual_elements() -> str:
    """Visual elements, accents, and decorative treatments."""
    return """# Visual Elements

Distinctive visual details separate memorable designs from generic output.

## Geometric Accents

### Lines & Dividers
- Thick accent lines (4-8pt) as section dividers
- L-shaped borders (top+left or bottom+right)
- Underline accents beneath headings

### Shapes
- Corner brackets instead of full frames
- Diagonal dividers for dynamic layouts
- Circles/ovals for image frames
- Triangular corner accents

### Patterns (Use Sparingly)
- Subtle grid backgrounds
- Diagonal stripes in accent areas
- Dot patterns for texture

## Background Treatments

### Solid Blocks
- Color blocks occupying 40-60% of canvas
- Creates clear content zones
- High contrast with text area

### Split Backgrounds
- Diagonal: Dynamic, modern
- Vertical: Two distinct areas
- Horizontal: Clear hierarchy

### Gradients (If Used)
- Subtle, not aggressive
- Vertical or diagonal only
- Single hue variations, not rainbow

## Border & Frame Treatments

| Style | Effect | Use For |
|-------|--------|---------|
| Heavy single-side | Bold, modern | Section emphasis |
| Double-line | Refined, editorial | Pull quotes |
| Corner brackets | Minimal, elegant | Image frames |
| Full border | Contained, traditional | Cards, callouts |

## Data Visualization Style

### Charts
- Monochrome with single accent for key data
- Minimal or no gridlines
- Direct labels on data points
- Horizontal bars > vertical bars

### Tables
- Clear header distinction
- Alternating rows for readability
- Accent color for key rows/columns
- Generous cell padding

### Numbers
- Oversized for key metrics (2-3x body)
- Monospace for alignment
- Accent color for emphasis

## Shadows & Depth

### Subtle (Preferred)
- Soft, diffused shadows
- Low offset, high blur
- Creates gentle lift

### Bold (Statement)
- Hard-edged shadows
- High offset
- Creates dramatic depth

### None (Flat)
- Clean, modern look
- Relies on color/space for depth
- Works with brutalist aesthetic

## Motion & Transitions (Digital)

- Staggered reveals (animation-delay)
- Subtle hover states
- Purposeful, not decorative
- One well-orchestrated animation > many small ones
"""


@mcp.prompt()
def design_for_presentations() -> str:
    """Specific guidance for presentation design."""
    return """# Presentation Design

Create presentations that command attention and communicate clearly.

## Slide Types & Their Purpose

### Title Slide
- Maximum impact, minimum text
- Clear hierarchy: Title > Subtitle > Attribution
- Set the visual tone for the entire deck

### Section Dividers
- Pause and reset attention
- Often inverted colors (dark if deck is light)
- Large section number or title

### Content Slides
- One idea per slide
- Support the spoken word, don't replace it
- Visual > Text when possible

### Data Slides
- Let the data be the hero
- Minimal chrome and decoration
- Clear callouts for key insights

### Closing Slide
- Call to action or key takeaway
- Contact information if relevant
- Thank you (optional, often unnecessary)

## Content Guidelines

### Text
- **6x6 Rule**: Max 6 bullets, max 6 words each
- Headlines as takeaways, not topics
- Sentence case preferred over ALL CAPS body

### Images
- Full-bleed for impact
- Consistent treatment (all photos or all illustrations)
- High quality, no pixelation

### Data
- One chart per slide
- Call out the insight, not just the data
- Simplify: remove non-essential elements

## Layout Templates

### Left-Heavy
```
[Large Title/Stat  ]  [Supporting]
[Main content      ]  [Visual   ]
[Continues here    ]  [Element  ]
```

### Center Stage
```
        [Title]
   [Main Visual/Stat]
     [Supporting text]
```

### Two Column
```
[Heading spans full width------]
[Point A     ]  [Point B      ]
[Details     ]  [Details      ]
```

## Transition Strategy

- Consistent throughout deck
- Simple is better (cut, fade)
- Never: spinning, bouncing, flying
- Build reveals for complex info

## Theme Selection Guide

| Theme | Best For | Avoid For |
|-------|----------|-----------|
| noir | Tech, premium, cinematic | Children, healthcare |
| brutalist | Design, architecture | Conservative finance |
| organic | Wellness, sustainability | Tech startups |
| neon | Gaming, innovation | Traditional business |
| minimal | Professional, content-heavy | Creative agencies |
| retro | Creative, fun campaigns | Serious topics |
"""


@mcp.prompt()
def design_for_documents() -> str:
    """Specific guidance for document design."""
    return """# Document Design

Create documents that are readable, scannable, and visually engaging.

## Document Types

### Reports
- Clear section hierarchy
- Executive summary upfront
- Data visualizations support narrative
- Consistent header styling

### Proposals
- Professional, polished look
- Clear value proposition
- Easy to scan for decision-makers
- Strong closing/CTA

### Technical Documentation
- Function over form
- Excellent readability
- Clear code/example formatting
- Consistent navigation

## Typography for Documents

### Body Text
- 11-12pt for print, 14-16px for screen
- Line height: 1.5-1.7
- Line length: 60-75 characters optimal
- Left-aligned (not justified)

### Headings
- Clear hierarchy (H1 > H2 > H3)
- Consistent spacing above/below
- Consider numbering for long docs

### Special Elements
- Pull quotes: Larger, accent color
- Callouts: Bordered or background boxes
- Lists: Consistent bullet/number style

## Page Layout

### Margins
- Generous margins (1-1.5 inches)
- Inside margin wider for bound docs
- Consistent throughout

### Headers/Footers
- Minimal, functional
- Page numbers always
- Document title or section optional

### Columns
- Single column for long reads
- Two columns for newsletters
- Never more than three

## Visual Elements

### Color Use
- Accent color for headings/links
- Limit to 2-3 colors total
- Ensure print-friendly

### Images & Figures
- Captioned with figure numbers
- Consistent sizing/treatment
- Referenced in text

### Tables
- Clear header row
- Adequate cell padding
- Zebra striping for long tables

## Consistency Checklist

- [ ] Same fonts throughout
- [ ] Consistent spacing between sections
- [ ] Matching heading styles
- [ ] Aligned margins and indents
- [ ] Coherent color usage
- [ ] Uniform image treatment
"""
