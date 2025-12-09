"""
PPTX Analysis Tools - Read-only presentation analysis.

Tools for reading and analyzing existing PowerPoint presentations
without modification.
"""

import json
from pathlib import Path

from pptx import Presentation

from . import mcp


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
    total_slides = len(prs.slides)

    # Parse and validate slide numbers if provided
    target_slides = None
    if slide_numbers:
        try:
            target_slides = set(int(s.strip()) for s in slide_numbers.split(","))
            invalid = [n for n in target_slides if n < 1 or n > total_slides]
            if invalid:
                return f"Error: Invalid slide number(s): {invalid}. Presentation has {total_slides} slides."
        except ValueError:
            return "Error: slide_numbers must be comma-separated integers (e.g., '1,3,5')"

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
        return f"Error: Slide {slide_number} does not exist. Presentation has {len(prs.slides)} slides."

    slide = prs.slides[slide_number - 1]
    shapes_info = []

    # EMU to inches conversion factor
    EMU_PER_INCH = 914400

    for shape in slide.shapes:
        info = {
            "name": shape.name,
            "shape_type": str(shape.shape_type),
            "left": shape.left / EMU_PER_INCH,
            "top": shape.top / EMU_PER_INCH,
            "width": shape.width / EMU_PER_INCH,
            "height": shape.height / EMU_PER_INCH,
        }

        if shape.has_text_frame:
            info["text"] = shape.text_frame.text[:100]

        if hasattr(shape, "image"):
            info["has_image"] = True

        shapes_info.append(info)

    return json.dumps(shapes_info, indent=2)


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
    total_slides = len(prs.slides)

    # Validate slide_number if provided
    if slide_number is not None:
        if slide_number < 1 or slide_number > total_slides:
            return f"Error: Slide {slide_number} does not exist. Presentation has {total_slides} slides."

    results = []

    if slide_number is not None:
        # Single slide
        slide = prs.slides[slide_number - 1]
        if slide.has_notes_slide:
            notes_text = slide.notes_slide.notes_text_frame.text
            results.append(f"--- Slide {slide_number} Notes ---\n{notes_text}")
        else:
            results.append(f"--- Slide {slide_number} Notes ---\n(no notes)")
    else:
        # All slides
        for i, slide in enumerate(prs.slides, 1):
            if slide.has_notes_slide:
                notes_text = slide.notes_slide.notes_text_frame.text
                results.append(f"--- Slide {i} Notes ---\n{notes_text}")
            else:
                results.append(f"--- Slide {i} Notes ---\n(no notes)")

    return "\n\n".join(results)


@mcp.tool()
def get_slide_export_instructions(file_path: str, slide_number: int) -> str:
    """
    Get instructions for exporting a slide as an image.

    Note: python-pptx cannot render slides as images. This tool provides
    instructions for using external tools like LibreOffice.

    Args:
        file_path: Path to the PowerPoint file
        slide_number: Slide number (1-indexed)

    Returns:
        Instructions for exporting the slide using external tools
    """
    path = Path(file_path).expanduser().resolve()

    if not path.exists():
        return f"Error: File not found: {path}"

    prs = Presentation(str(path))
    total_slides = len(prs.slides)

    if slide_number < 1 or slide_number > total_slides:
        return f"Error: Slide {slide_number} does not exist. Presentation has {total_slides} slides."

    return f"""To export slide {slide_number} from {path.name}:

Using LibreOffice (recommended):
  libreoffice --headless --convert-to png --outdir /output/dir "{path}"

This exports ALL slides as PNG files. For slide {slide_number}, look for:
  {path.stem}-{slide_number}.png

Using soffice (macOS):
  /Applications/LibreOffice.app/Contents/MacOS/soffice --headless --convert-to png "{path}"

Note: LibreOffice exports all slides. To get a specific slide only,
you can use the pdf export first, then convert:
  libreoffice --headless --convert-to pdf "{path}"
  # Then use a PDF tool to extract and convert page {slide_number}
"""
