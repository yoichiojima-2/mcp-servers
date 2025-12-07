"""
HTML to PPTX conversion tools.

Inspired by the Anthropic PPTX skill's html2pptx workflow, this module
provides functionality to convert HTML slides into PowerPoint presentations.
"""

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from . import mcp


@dataclass
class TextRun:
    """A run of text with formatting."""
    text: str
    bold: bool = False
    italic: bool = False
    underline: bool = False
    font_size: int | None = None
    font_color: str | None = None
    font_name: str | None = None


@dataclass
class Paragraph:
    """A paragraph containing text runs."""
    runs: list[TextRun]
    alignment: str = "left"
    level: int = 0  # For list items


@dataclass
class SlideElement:
    """An element on a slide."""
    element_type: str  # "textbox", "shape", "image", "list"
    left: float
    top: float
    width: float
    height: float
    paragraphs: list[Paragraph] | None = None
    background_color: str | None = None
    border_color: str | None = None
    image_path: str | None = None
    list_items: list[str] | None = None


@dataclass
class SlideDefinition:
    """Definition of a slide from HTML."""
    title: str | None = None
    elements: list[SlideElement] = None

    def __post_init__(self):
        if self.elements is None:
            self.elements = []


class SimpleHTMLParser(HTMLParser):
    """Parse simple HTML for slide content."""

    def __init__(self):
        super().__init__()
        self.slides: list[SlideDefinition] = []
        self.current_slide: SlideDefinition | None = None
        self.current_element: SlideElement | None = None
        self.current_paragraph: Paragraph | None = None
        self.current_run: TextRun | None = None
        self.tag_stack: list[str] = []
        self.current_text = ""
        self.in_list = False
        self.list_items: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.tag_stack.append(tag)

        if tag == "slide":
            self.current_slide = SlideDefinition()
            if "title" in attrs_dict:
                self.current_slide.title = attrs_dict["title"]

        elif tag == "div" and self.current_slide:
            # Parse position from style
            style = attrs_dict.get("style", "")
            left, top, width, height = self._parse_position(style)
            bg_color = self._parse_color(style, "background-color")
            border_color = self._parse_color(style, "border-color")

            self.current_element = SlideElement(
                element_type="textbox",
                left=left,
                top=top,
                width=width,
                height=height,
                background_color=bg_color,
                border_color=border_color,
                paragraphs=[],
            )

        elif tag in ("p", "h1", "h2", "h3", "h4", "h5", "h6"):
            style = attrs_dict.get("style", "")
            align = "left"
            if "text-align: center" in style:
                align = "center"
            elif "text-align: right" in style:
                align = "right"

            self.current_paragraph = Paragraph(runs=[], alignment=align)

            # Set default font size based on heading level
            if tag == "h1":
                self.current_run = TextRun(text="", bold=True, font_size=44)
            elif tag == "h2":
                self.current_run = TextRun(text="", bold=True, font_size=32)
            elif tag == "h3":
                self.current_run = TextRun(text="", bold=True, font_size=28)
            elif tag in ("h4", "h5", "h6"):
                self.current_run = TextRun(text="", bold=True, font_size=24)
            else:
                self.current_run = TextRun(text="", font_size=18)

        elif tag in ("ul", "ol"):
            self.in_list = True
            self.list_items = []

        elif tag == "li" and self.in_list:
            self.current_text = ""

        elif tag == "b" or tag == "strong":
            if self.current_run:
                self.current_run.bold = True

        elif tag == "i" or tag == "em":
            if self.current_run:
                self.current_run.italic = True

        elif tag == "u":
            if self.current_run:
                self.current_run.underline = True

        elif tag == "span":
            style = attrs_dict.get("style", "")
            color = self._parse_color(style, "color")
            if color and self.current_run:
                self.current_run.font_color = color

        elif tag == "img" and self.current_slide:
            src = attrs_dict.get("src", "")
            style = attrs_dict.get("style", "")
            left, top, width, height = self._parse_position(style)

            img_element = SlideElement(
                element_type="image",
                left=left,
                top=top,
                width=width,
                height=height,
                image_path=src,
            )
            self.current_slide.elements.append(img_element)

    def handle_endtag(self, tag):
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()

        if tag == "slide" and self.current_slide:
            self.slides.append(self.current_slide)
            self.current_slide = None

        elif tag == "div" and self.current_element:
            if self.current_slide:
                self.current_slide.elements.append(self.current_element)
            self.current_element = None

        elif tag in ("p", "h1", "h2", "h3", "h4", "h5", "h6"):
            if self.current_run and self.current_paragraph:
                self.current_run.text = self.current_text.strip()
                if self.current_run.text:
                    self.current_paragraph.runs.append(self.current_run)

            if self.current_paragraph and self.current_element:
                if self.current_paragraph.runs:
                    self.current_element.paragraphs.append(self.current_paragraph)

            self.current_paragraph = None
            self.current_run = None
            self.current_text = ""

        elif tag in ("ul", "ol"):
            if self.list_items and self.current_element:
                self.current_element.element_type = "list"
                self.current_element.list_items = self.list_items
            self.in_list = False
            self.list_items = []

        elif tag == "li" and self.in_list:
            self.list_items.append(self.current_text.strip())
            self.current_text = ""

    def handle_data(self, data):
        if self.current_run:
            self.current_text += data
        elif self.in_list:
            self.current_text += data

    def _parse_position(self, style: str) -> tuple[float, float, float, float]:
        """Parse position values from CSS style."""
        left = self._extract_pt(style, "left") / 72  # Convert pt to inches
        top = self._extract_pt(style, "top") / 72
        width = self._extract_pt(style, "width") / 72
        height = self._extract_pt(style, "height") / 72

        # Default values if not found
        return (
            left if left else 1.0,
            top if top else 1.0,
            width if width else 4.0,
            height if height else 1.0,
        )

    def _extract_pt(self, style: str, prop: str) -> float:
        """Extract a point value from CSS."""
        # Match patterns like "left: 100pt" or "left:100pt"
        pattern = rf"{prop}\s*:\s*(\d+(?:\.\d+)?)\s*pt"
        match = re.search(pattern, style)
        if match:
            return float(match.group(1))
        return 0.0

    def _parse_color(self, style: str, prop: str) -> str | None:
        """Extract a color value from CSS."""
        # Match hex colors like "#FF0000" or "FF0000"
        pattern = rf"{prop}\s*:\s*#?([0-9A-Fa-f]{{6}})"
        match = re.search(pattern, style)
        if match:
            return match.group(1).upper()
        return None


def parse_html_slides(html: str) -> list[SlideDefinition]:
    """Parse HTML content into slide definitions."""
    parser = SimpleHTMLParser()
    parser.feed(html)
    return parser.slides


def create_presentation_from_html(slides: list[SlideDefinition], aspect_ratio: str = "16:9") -> Presentation:
    """Create a PowerPoint presentation from slide definitions."""
    prs = Presentation()

    # Set slide dimensions
    if aspect_ratio == "4:3":
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(7.5)
    elif aspect_ratio == "16:10":
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(6.25)
    else:  # 16:9
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

    for slide_def in slides:
        # Use blank layout
        slide_layout = prs.slide_layouts[6] if len(prs.slide_layouts) > 6 else prs.slide_layouts[0]
        slide = prs.slides.add_slide(slide_layout)

        # Add title if present
        if slide_def.title:
            title_box = slide.shapes.add_textbox(
                Inches(0.5), Inches(0.3), Inches(12), Inches(0.8)
            )
            tf = title_box.text_frame
            p = tf.paragraphs[0]
            p.text = slide_def.title
            p.font.size = Pt(36)
            p.font.bold = True

        # Add elements
        for element in slide_def.elements:
            if element.element_type == "textbox" and element.paragraphs:
                shape = slide.shapes.add_textbox(
                    Inches(element.left),
                    Inches(element.top),
                    Inches(element.width),
                    Inches(element.height),
                )

                if element.background_color:
                    shape.fill.solid()
                    shape.fill.fore_color.rgb = RGBColor.from_string(element.background_color)

                tf = shape.text_frame
                tf.word_wrap = True

                for i, para in enumerate(element.paragraphs):
                    if i == 0:
                        p = tf.paragraphs[0]
                    else:
                        p = tf.add_paragraph()

                    # Set alignment
                    align_map = {
                        "left": PP_ALIGN.LEFT,
                        "center": PP_ALIGN.CENTER,
                        "right": PP_ALIGN.RIGHT,
                    }
                    p.alignment = align_map.get(para.alignment, PP_ALIGN.LEFT)

                    for run_def in para.runs:
                        run = p.add_run()
                        run.text = run_def.text
                        run.font.bold = run_def.bold
                        run.font.italic = run_def.italic
                        run.font.underline = run_def.underline

                        if run_def.font_size:
                            run.font.size = Pt(run_def.font_size)
                        if run_def.font_color:
                            run.font.color.rgb = RGBColor.from_string(run_def.font_color)
                        if run_def.font_name:
                            run.font.name = run_def.font_name

            elif element.element_type == "list" and element.list_items:
                shape = slide.shapes.add_textbox(
                    Inches(element.left),
                    Inches(element.top),
                    Inches(element.width),
                    Inches(element.height),
                )
                tf = shape.text_frame
                tf.word_wrap = True

                for i, item in enumerate(element.list_items):
                    if i == 0:
                        p = tf.paragraphs[0]
                    else:
                        p = tf.add_paragraph()

                    p.text = f"• {item}"
                    p.font.size = Pt(18)
                    p.level = 0

            elif element.element_type == "image" and element.image_path:
                img_path = Path(element.image_path).expanduser().resolve()
                if img_path.exists():
                    slide.shapes.add_picture(
                        str(img_path),
                        Inches(element.left),
                        Inches(element.top),
                        width=Inches(element.width) if element.width else None,
                        height=Inches(element.height) if element.height else None,
                    )

    return prs


@mcp.tool()
def html_to_pptx(html: str, output_path: str, aspect_ratio: str = "16:9") -> str:
    """
    Convert HTML slides to a PowerPoint presentation.

    The HTML should use a custom format with <slide> tags:

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

    Supported elements:
    - <slide title="..."> - Container for each slide
    - <div style="..."> - Positioned container (use pt units)
    - <h1>-<h6> - Headings with automatic sizing
    - <p> - Paragraphs
    - <ul>/<ol> with <li> - Lists
    - <b>, <i>, <u> - Text formatting
    - <span style="color: #RRGGBB"> - Colored text
    - <img src="path" style="..."> - Images

    Args:
        html: HTML content with slide definitions
        output_path: Path for the output PPTX file
        aspect_ratio: Slide aspect ratio - "16:9", "4:3", or "16:10"

    Returns:
        Path to the created presentation
    """
    out_path = Path(output_path).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    slides = parse_html_slides(html)

    if not slides:
        return "Error: No <slide> elements found in HTML"

    prs = create_presentation_from_html(slides, aspect_ratio)
    prs.save(str(out_path))

    return f"Created presentation with {len(slides)} slides: {out_path}"


@mcp.tool()
def html_file_to_pptx(html_path: str, output_path: str, aspect_ratio: str = "16:9") -> str:
    """
    Convert an HTML file to a PowerPoint presentation.

    Args:
        html_path: Path to the HTML file
        output_path: Path for the output PPTX file
        aspect_ratio: Slide aspect ratio - "16:9", "4:3", or "16:10"

    Returns:
        Path to the created presentation
    """
    html_file = Path(html_path).expanduser().resolve()
    if not html_file.exists():
        return f"Error: HTML file not found: {html_file}"

    html_content = html_file.read_text(encoding="utf-8")
    return html_to_pptx(html_content, output_path, aspect_ratio)


@mcp.tool()
def validate_html_for_pptx(html: str) -> str:
    """
    Validate HTML content for PPTX conversion.

    Checks for common issues that could cause problems during conversion.

    Args:
        html: HTML content to validate

    Returns:
        Validation report with warnings and errors
    """
    issues = []
    warnings = []

    # Check for <slide> tags
    if "<slide" not in html:
        issues.append("No <slide> elements found")

    # Check for text not in proper tags
    parser = SimpleHTMLParser()
    parser.feed(html)

    if not parser.slides:
        issues.append("No valid slides parsed from HTML")
    else:
        for i, slide in enumerate(parser.slides, 1):
            if not slide.elements:
                warnings.append(f"Slide {i} has no elements")

            for j, elem in enumerate(slide.elements):
                if elem.element_type == "textbox" and not elem.paragraphs:
                    warnings.append(f"Slide {i}, element {j+1}: textbox has no text")

    # Check for unsupported CSS
    if "gradient" in html.lower():
        warnings.append("CSS gradients are not supported - use PNG images instead")

    if "transform" in html.lower():
        warnings.append("CSS transforms are not supported")

    report = ["HTML Validation Report", "=" * 40, ""]

    if issues:
        report.append("ERRORS:")
        for issue in issues:
            report.append(f"  - {issue}")
        report.append("")

    if warnings:
        report.append("WARNINGS:")
        for warning in warnings:
            report.append(f"  - {warning}")
        report.append("")

    if not issues and not warnings:
        report.append("No issues found!")
        report.append(f"Found {len(parser.slides)} valid slide(s)")

    return "\n".join(report)
