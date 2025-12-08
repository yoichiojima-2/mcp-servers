"""
PPTX MCP Tools - PowerPoint presentation creation and manipulation.

Inspired by the Anthropic PPTX skill, this module provides tools for:
- Creating new presentations from scratch
- Reading and analyzing existing presentations
- Modifying slides, text, and shapes
- Working with templates
- OOXML manipulation for advanced editing
"""

import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from . import mcp

# ======================================================
# Presentation Creation
# ======================================================


@mcp.tool()
def create_presentation(
    output_path: str,
    title: str | None = None,
    subtitle: str | None = None,
    aspect_ratio: str = "16:9",
) -> str:
    """
    Create a new PowerPoint presentation.

    Args:
        output_path: Path where the presentation will be saved
        title: Optional title for the title slide
        subtitle: Optional subtitle for the title slide
        aspect_ratio: Slide aspect ratio - "16:9", "4:3", or "16:10"

    Returns:
        Path to the created presentation
    """
    prs = Presentation()

    # Set slide dimensions based on aspect ratio
    if aspect_ratio == "4:3":
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(7.5)
    elif aspect_ratio == "16:10":
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(6.25)
    else:  # 16:9 default
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

    # Add title slide if title is provided
    if title:
        title_slide_layout = prs.slide_layouts[0]  # Title Slide layout
        slide = prs.slides.add_slide(title_slide_layout)

        title_shape = slide.shapes.title
        if title_shape:
            title_shape.text = title

        if subtitle and len(slide.placeholders) > 1:
            subtitle_shape = slide.placeholders[1]
            subtitle_shape.text = subtitle

    path = Path(output_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(path))

    return f"Created presentation: {path}"


@mcp.tool()
def add_slide(
    file_path: str,
    layout: int = 1,
    title: str | None = None,
    content: str | None = None,
) -> str:
    """
    Add a new slide to an existing presentation.

    Args:
        file_path: Path to the PowerPoint file
        layout: Slide layout index (0=Title, 1=Title+Content, 2=Section Header, 5=Blank, 6=Content Only)
        title: Optional title for the slide
        content: Optional content/body text for the slide

    Returns:
        Information about the added slide
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    prs = Presentation(str(path))
    slide_layout = prs.slide_layouts[layout]
    slide = prs.slides.add_slide(slide_layout)

    if title and slide.shapes.title:
        slide.shapes.title.text = title

    if content:
        for shape in slide.placeholders:
            if shape.placeholder_format.idx == 1:  # Content placeholder
                shape.text = content
                break

    prs.save(str(path))
    return f"Added slide {len(prs.slides)} with layout {layout} to: {path}"


@mcp.tool()
def add_text_box(
    file_path: str,
    slide_number: int,
    text: str,
    left: float,
    top: float,
    width: float,
    height: float,
    font_size: int = 18,
    font_name: str = "Arial",
    font_color: str | None = None,
    bold: bool = False,
    italic: bool = False,
    alignment: str = "left",
) -> str:
    """
    Add a text box to a slide.

    Args:
        file_path: Path to the PowerPoint file
        slide_number: Slide number (1-indexed)
        text: Text content
        left: Left position in inches
        top: Top position in inches
        width: Width in inches
        height: Height in inches
        font_size: Font size in points
        font_name: Font name (e.g., "Arial", "Calibri")
        font_color: Hex color code (e.g., "FF0000" for red)
        bold: Whether text should be bold
        italic: Whether text should be italic
        alignment: Text alignment - "left", "center", or "right"

    Returns:
        Confirmation message
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    prs = Presentation(str(path))

    if slide_number < 1 or slide_number > len(prs.slides):
        return f"Error: Slide {slide_number} does not exist. Presentation has {len(prs.slides)} slides."

    slide = prs.slides[slide_number - 1]
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = text

    # Set alignment
    align_map = {
        "left": PP_ALIGN.LEFT,
        "center": PP_ALIGN.CENTER,
        "right": PP_ALIGN.RIGHT,
    }
    p.alignment = align_map.get(alignment, PP_ALIGN.LEFT)

    # Set font properties
    run = p.runs[0]
    run.font.size = Pt(font_size)
    run.font.name = font_name
    run.font.bold = bold
    run.font.italic = italic

    if font_color:
        run.font.color.rgb = RGBColor.from_string(font_color)

    prs.save(str(path))
    return f"Added text box to slide {slide_number}"


@mcp.tool()
def add_shape(
    file_path: str,
    slide_number: int,
    shape_type: str,
    left: float,
    top: float,
    width: float,
    height: float,
    fill_color: str | None = None,
    line_color: str | None = None,
    line_width: float = 1.0,
    text: str | None = None,
) -> str:
    """
    Add a shape to a slide.

    Args:
        file_path: Path to the PowerPoint file
        slide_number: Slide number (1-indexed)
        shape_type: Shape type - "rectangle", "rounded_rectangle", "oval", "triangle", "arrow_right"
        left: Left position in inches
        top: Top position in inches
        width: Width in inches
        height: Height in inches
        fill_color: Fill color as hex (e.g., "4472C4")
        line_color: Line/border color as hex
        line_width: Line width in points
        text: Optional text to add inside the shape

    Returns:
        Confirmation message
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    shape_map = {
        "rectangle": MSO_SHAPE.RECTANGLE,
        "rounded_rectangle": MSO_SHAPE.ROUNDED_RECTANGLE,
        "oval": MSO_SHAPE.OVAL,
        "triangle": MSO_SHAPE.ISOSCELES_TRIANGLE,
        "arrow_right": MSO_SHAPE.RIGHT_ARROW,
    }

    if shape_type not in shape_map:
        return f"Error: Unknown shape type '{shape_type}'. Available: {list(shape_map.keys())}"

    prs = Presentation(str(path))

    if slide_number < 1 or slide_number > len(prs.slides):
        return f"Error: Slide {slide_number} does not exist."

    slide = prs.slides[slide_number - 1]
    shape = slide.shapes.add_shape(
        shape_map[shape_type],
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(height),
    )

    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor.from_string(fill_color)

    if line_color:
        shape.line.color.rgb = RGBColor.from_string(line_color)
        shape.line.width = Pt(line_width)

    if text:
        shape.text = text
        shape.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        shape.text_frame.paragraphs[0].font.size = Pt(14)

    prs.save(str(path))
    return f"Added {shape_type} shape to slide {slide_number}"


@mcp.tool()
def add_image(
    file_path: str,
    slide_number: int,
    image_path: str,
    left: float,
    top: float,
    width: float | None = None,
    height: float | None = None,
) -> str:
    """
    Add an image to a slide.

    Args:
        file_path: Path to the PowerPoint file
        slide_number: Slide number (1-indexed)
        image_path: Path to the image file
        left: Left position in inches
        top: Top position in inches
        width: Optional width in inches (maintains aspect ratio if height not specified)
        height: Optional height in inches

    Returns:
        Confirmation message
    """
    path = Path(file_path).expanduser().resolve()
    img_path = Path(image_path).expanduser().resolve()

    if not path.exists():
        return f"Error: Presentation not found: {path}"
    if not img_path.exists():
        return f"Error: Image not found: {img_path}"

    prs = Presentation(str(path))

    if slide_number < 1 or slide_number > len(prs.slides):
        return f"Error: Slide {slide_number} does not exist."

    slide = prs.slides[slide_number - 1]

    if width:
        slide.shapes.add_picture(
            str(img_path),
            Inches(left),
            Inches(top),
            width=Inches(width),
            height=Inches(height) if height else None,
        )
    else:
        slide.shapes.add_picture(str(img_path), Inches(left), Inches(top))

    prs.save(str(path))
    return f"Added image to slide {slide_number}"


@mcp.tool()
def add_table(
    file_path: str,
    slide_number: int,
    data: list[list[str]],
    left: float,
    top: float,
    width: float,
    height: float,
    header_color: str | None = "4472C4",
) -> str:
    """
    Add a table to a slide.

    Args:
        file_path: Path to the PowerPoint file
        slide_number: Slide number (1-indexed)
        data: 2D list of strings representing table data (first row is header)
        left: Left position in inches
        top: Top position in inches
        width: Width in inches
        height: Height in inches
        header_color: Header row background color as hex

    Returns:
        Confirmation message
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    if not data or not data[0]:
        return "Error: Table data cannot be empty"

    prs = Presentation(str(path))

    if slide_number < 1 or slide_number > len(prs.slides):
        return f"Error: Slide {slide_number} does not exist."

    slide = prs.slides[slide_number - 1]

    rows = len(data)
    cols = len(data[0])

    table_shape = slide.shapes.add_table(rows, cols, Inches(left), Inches(top), Inches(width), Inches(height))
    table = table_shape.table

    # Fill in data
    for i, row in enumerate(data):
        for j, cell_text in enumerate(row):
            cell = table.cell(i, j)
            cell.text = str(cell_text)

            # Style header row
            if i == 0 and header_color:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor.from_string(header_color)
                for paragraph in cell.text_frame.paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)

    prs.save(str(path))
    return f"Added {rows}x{cols} table to slide {slide_number}"


# ======================================================
# Reading & Analysis
# ======================================================


@mcp.tool()
def get_presentation_info(file_path: str) -> str:
    """
    Get information about a PowerPoint presentation.

    Args:
        file_path: Path to the PowerPoint file

    Returns:
        Presentation metadata and structure information
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    prs = Presentation(str(path))

    width_inches = prs.slide_width.inches
    height_inches = prs.slide_height.inches

    # Determine aspect ratio
    ratio = width_inches / height_inches
    if abs(ratio - 16 / 9) < 0.01:
        aspect = "16:9"
    elif abs(ratio - 4 / 3) < 0.01:
        aspect = "4:3"
    elif abs(ratio - 16 / 10) < 0.01:
        aspect = "16:10"
    else:
        aspect = f"{ratio:.2f}:1"

    info = [
        f"File: {path.name}",
        f"Slides: {len(prs.slides)}",
        f'Dimensions: {width_inches:.2f}" x {height_inches:.2f}"',
        f"Aspect Ratio: {aspect}",
        f"Slide Layouts: {len(prs.slide_layouts)}",
        "",
        "Slide Summary:",
    ]

    for i, slide in enumerate(prs.slides, 1):
        title = ""
        if slide.shapes.title:
            title = slide.shapes.title.text[:50]
        shape_count = len(slide.shapes)
        info.append(f"  Slide {i}: {shape_count} shapes - {title or '(no title)'}")

    return "\n".join(info)


@mcp.tool()
def extract_text(file_path: str, slide_numbers: str | None = None) -> str:
    """
    Extract all text from a PowerPoint presentation.

    Args:
        file_path: Path to the PowerPoint file
        slide_numbers: Optional comma-separated slide numbers (e.g., "1,3,5")

    Returns:
        Extracted text organized by slide
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    prs = Presentation(str(path))

    # Parse slide numbers if provided
    target_slides = None
    if slide_numbers:
        target_slides = set(int(s.strip()) for s in slide_numbers.split(","))

    results = []
    for i, slide in enumerate(prs.slides, 1):
        if target_slides and i not in target_slides:
            continue

        slide_text = [f"--- Slide {i} ---"]

        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    text = paragraph.text.strip()
                    if text:
                        slide_text.append(text)

        if len(slide_text) > 1:
            results.append("\n".join(slide_text))
        else:
            results.append(f"--- Slide {i} ---\n(no text)")

    return "\n\n".join(results)


@mcp.tool()
def get_slide_shapes(file_path: str, slide_number: int) -> str:
    """
    Get detailed information about all shapes on a slide.

    Args:
        file_path: Path to the PowerPoint file
        slide_number: Slide number (1-indexed)

    Returns:
        JSON-formatted shape information
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    prs = Presentation(str(path))

    if slide_number < 1 or slide_number > len(prs.slides):
        return f"Error: Slide {slide_number} does not exist."

    slide = prs.slides[slide_number - 1]
    shapes_info = []

    for shape in slide.shapes:
        info = {
            "name": shape.name,
            "shape_type": str(shape.shape_type),
            "left": shape.left.inches if shape.left else 0,
            "top": shape.top.inches if shape.top else 0,
            "width": shape.width.inches if shape.width else 0,
            "height": shape.height.inches if shape.height else 0,
        }

        if shape.has_text_frame:
            info["text"] = shape.text_frame.text[:100]

        if hasattr(shape, "image"):
            info["has_image"] = True

        shapes_info.append(info)

    return json.dumps(shapes_info, indent=2)


# ======================================================
# Slide Manipulation
# ======================================================


@mcp.tool()
def delete_slide(file_path: str, slide_number: int) -> str:
    """
    Delete a slide from a presentation.

    Args:
        file_path: Path to the PowerPoint file
        slide_number: Slide number to delete (1-indexed)

    Returns:
        Confirmation message
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    prs = Presentation(str(path))

    if slide_number < 1 or slide_number > len(prs.slides):
        return f"Error: Slide {slide_number} does not exist."

    # Get the slide ID
    slide_id = prs.slides._sldIdLst[slide_number - 1].rId
    prs.part.drop_rel(slide_id)
    del prs.slides._sldIdLst[slide_number - 1]

    prs.save(str(path))
    return f"Deleted slide {slide_number}. Presentation now has {len(prs.slides)} slides."


@mcp.tool()
def duplicate_slide(file_path: str, slide_number: int) -> str:
    """
    Duplicate a slide in a presentation.

    Args:
        file_path: Path to the PowerPoint file
        slide_number: Slide number to duplicate (1-indexed)

    Returns:
        Confirmation message
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    prs = Presentation(str(path))

    if slide_number < 1 or slide_number > len(prs.slides):
        return f"Error: Slide {slide_number} does not exist."

    source_slide = prs.slides[slide_number - 1]

    # Add a new slide with the same layout
    slide_layout = source_slide.slide_layout
    new_slide = prs.slides.add_slide(slide_layout)

    # Copy shapes (basic implementation)
    for shape in source_slide.shapes:
        if shape.has_text_frame:
            # Add text box
            new_shape = new_slide.shapes.add_textbox(shape.left, shape.top, shape.width, shape.height)
            new_shape.text_frame.text = shape.text_frame.text

    prs.save(str(path))
    return f"Duplicated slide {slide_number}. New slide is #{len(prs.slides)}."


@mcp.tool()
def reorder_slides(file_path: str, new_order: list[int]) -> str:
    """
    Reorder slides in a presentation.

    Args:
        file_path: Path to the PowerPoint file
        new_order: List of slide numbers in desired order (1-indexed)

    Returns:
        Confirmation message
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    prs = Presentation(str(path))
    num_slides = len(prs.slides)

    # Validate new_order
    if sorted(new_order) != list(range(1, num_slides + 1)):
        return f"Error: new_order must contain all slide numbers 1 to {num_slides}"

    # Convert to 0-indexed
    new_order_0indexed = [i - 1 for i in new_order]

    # Create a copy of the slide ID list
    old_sldIdLst = list(prs.slides._sldIdLst)

    # Clear and rebuild in new order
    prs.slides._sldIdLst.clear()
    for idx in new_order_0indexed:
        prs.slides._sldIdLst.append(old_sldIdLst[idx])

    prs.save(str(path))
    return f"Reordered {num_slides} slides successfully."


# ======================================================
# Template Operations
# ======================================================


@mcp.tool()
def apply_template(source_path: str, template_path: str, output_path: str) -> str:
    """
    Apply a template's design to an existing presentation.

    Args:
        source_path: Path to the source PowerPoint file
        template_path: Path to the template PowerPoint file
        output_path: Path for the output file

    Returns:
        Path to the new presentation
    """
    src = Path(source_path).expanduser().resolve()
    tmpl = Path(template_path).expanduser().resolve()
    out = Path(output_path).expanduser().resolve()

    if not src.exists():
        return f"Error: Source file not found: {src}"
    if not tmpl.exists():
        return f"Error: Template file not found: {tmpl}"

    # Copy template as base
    shutil.copy(tmpl, out)

    # Open both presentations
    template_prs = Presentation(str(out))
    source_prs = Presentation(str(src))

    # Remove template slides (keeping layouts)
    while len(template_prs.slides) > 0:
        slide_id = template_prs.slides._sldIdLst[0].rId
        template_prs.part.drop_rel(slide_id)
        del template_prs.slides._sldIdLst[0]

    # Add content from source using template layouts
    for slide in source_prs.slides:
        # Use a compatible layout from template
        layout_idx = min(1, len(template_prs.slide_layouts) - 1)
        new_slide = template_prs.slides.add_slide(template_prs.slide_layouts[layout_idx])

        # Copy text content
        for shape in slide.shapes:
            if shape.has_text_frame and shape.text_frame.text.strip():
                tb = new_slide.shapes.add_textbox(shape.left, shape.top, shape.width, shape.height)
                tb.text_frame.text = shape.text_frame.text

    template_prs.save(str(out))
    return f"Applied template and saved to: {out}"


# ======================================================
# OOXML Operations (Advanced)
# ======================================================


@mcp.tool()
def unpack_pptx(file_path: str, output_dir: str) -> str:
    """
    Unpack a PPTX file to view/edit its XML structure.

    PPTX files are ZIP archives containing XML files. This tool extracts
    them for advanced editing.

    Args:
        file_path: Path to the PowerPoint file
        output_dir: Directory to extract files to

    Returns:
        List of extracted files
    """
    path = Path(file_path).expanduser().resolve()
    out_dir = Path(output_dir).expanduser().resolve()

    if not path.exists():
        return f"Error: File not found: {path}"

    out_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(path, "r") as zf:
        zf.extractall(out_dir)

    # List key files
    key_files = []
    for root, dirs, files in os.walk(out_dir):
        for f in files:
            if f.endswith(".xml"):
                rel_path = os.path.relpath(os.path.join(root, f), out_dir)
                key_files.append(rel_path)

    return f"Unpacked to {out_dir}\n\nKey XML files:\n" + "\n".join(key_files[:20])


@mcp.tool()
def pack_pptx(source_dir: str, output_path: str) -> str:
    """
    Pack a directory back into a PPTX file.

    After editing XML files from an unpacked PPTX, use this to
    recreate the presentation file.

    Args:
        source_dir: Directory containing unpacked PPTX contents
        output_path: Path for the output PPTX file

    Returns:
        Path to the created file
    """
    src_dir = Path(source_dir).expanduser().resolve()
    out_path = Path(output_path).expanduser().resolve()

    if not src_dir.exists():
        return f"Error: Source directory not found: {src_dir}"

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(src_dir)
                zf.write(file_path, arcname)

    return f"Packed to: {out_path}"


@mcp.tool()
def edit_slide_xml(
    file_path: str,
    slide_number: int,
    xpath: str,
    new_value: str,
) -> str:
    """
    Edit slide XML directly using XPath (advanced).

    This allows low-level editing of slide content that may not be
    accessible through the standard API.

    Args:
        file_path: Path to the PowerPoint file
        slide_number: Slide number (1-indexed)
        xpath: XPath expression to find element
        new_value: New text value to set

    Returns:
        Confirmation or error message
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    # Work with a temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Extract
        with zipfile.ZipFile(path, "r") as zf:
            zf.extractall(tmpdir)

        # Find and edit slide XML
        slide_path = Path(tmpdir) / "ppt" / "slides" / f"slide{slide_number}.xml"
        if not slide_path.exists():
            return f"Error: Slide {slide_number} not found in archive"

        # Parse XML
        namespaces = {
            "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
            "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
            "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
        }

        tree = ET.parse(slide_path)
        root = tree.getroot()

        # Find elements matching xpath
        try:
            elements = root.findall(xpath, namespaces)
            if not elements:
                return f"No elements found matching: {xpath}"

            for elem in elements:
                elem.text = new_value

            tree.write(slide_path, xml_declaration=True, encoding="UTF-8")
        except Exception as e:
            return f"Error editing XML: {e}"

        # Repack
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root_dir, dirs, files in os.walk(tmpdir):
                for file in files:
                    file_path_full = Path(root_dir) / file
                    arcname = file_path_full.relative_to(tmpdir)
                    zf.write(file_path_full, arcname)

    return f"Updated {len(elements)} element(s) in slide {slide_number}"


@mcp.tool()
def get_slide_notes(file_path: str, slide_number: int | None = None) -> str:
    """
    Get speaker notes from slides.

    Args:
        file_path: Path to the PowerPoint file
        slide_number: Optional specific slide number (1-indexed). If None, gets all notes.

    Returns:
        Speaker notes text
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    prs = Presentation(str(path))
    results = []

    slides_to_check = [prs.slides[slide_number - 1]] if slide_number else prs.slides

    for i, slide in enumerate(slides_to_check, slide_number or 1):
        if slide.has_notes_slide:
            notes_slide = slide.notes_slide
            notes_text = notes_slide.notes_text_frame.text
            results.append(f"--- Slide {i} Notes ---\n{notes_text}")
        else:
            results.append(f"--- Slide {i} Notes ---\n(no notes)")

    return "\n\n".join(results)


@mcp.tool()
def set_slide_notes(file_path: str, slide_number: int, notes: str) -> str:
    """
    Set speaker notes for a slide.

    Args:
        file_path: Path to the PowerPoint file
        slide_number: Slide number (1-indexed)
        notes: Notes text to set

    Returns:
        Confirmation message
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    prs = Presentation(str(path))

    if slide_number < 1 or slide_number > len(prs.slides):
        return f"Error: Slide {slide_number} does not exist."

    slide = prs.slides[slide_number - 1]
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = notes

    prs.save(str(path))
    return f"Set notes for slide {slide_number}"


@mcp.tool()
def export_slide_as_image(
    file_path: str,
    slide_number: int,
    output_path: str,
    width: int = 1920,
) -> str:
    """
    Export a slide as an image (requires unpacking and reading embedded images).

    Note: This creates a thumbnail-like representation, not a full render.
    For full rendering, use LibreOffice or similar tools.

    Args:
        file_path: Path to the PowerPoint file
        slide_number: Slide number (1-indexed)
        output_path: Path for the output image
        width: Image width in pixels

    Returns:
        Path to the created image or instructions for full rendering
    """
    path = Path(file_path).expanduser().resolve()
    out_path = Path(output_path).expanduser().resolve()

    if not path.exists():
        return f"Error: File not found: {path}"

    # Create a simple placeholder image
    prs = Presentation(str(path))

    if slide_number < 1 or slide_number > len(prs.slides):
        return f"Error: Slide {slide_number} does not exist."

    # Calculate height based on aspect ratio
    aspect_ratio = prs.slide_height.inches / prs.slide_width.inches
    height = int(width * aspect_ratio)

    # Create image with slide text
    img = Image.new("RGB", (width, height), color=(255, 255, 255))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path))

    return (
        f"Created placeholder image: {out_path}\n\n"
        f"For full slide rendering, use:\n"
        f"  libreoffice --headless --convert-to png {path}"
    )
