"""
PPTX Analysis Tools - Read-only presentation analysis.

Tools for reading and analyzing existing PowerPoint presentations
without modification.
"""

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from pptx import Presentation

from . import mcp


def _find_libreoffice() -> str | None:
    """Find LibreOffice executable path."""
    # Check common locations
    candidates = [
        "libreoffice",
        "soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/bin/libreoffice",
        "/usr/bin/soffice",
    ]

    for candidate in candidates:
        if shutil.which(candidate):
            return candidate

    # Check macOS application path directly
    macos_path = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
    if macos_path.exists():
        return str(macos_path)

    return None


def _convert_pptx_to_images(pptx_path: Path, output_dir: Path, libreoffice_path: str, total_slides: int) -> list[Path]:
    """Convert PPTX to images using LibreOffice.

    LibreOffice exports directly to PNG format (one file per slide).
    """
    # Create a temporary directory for LibreOffice output
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Export to PNG using LibreOffice
        # --outdir specifies output directory
        # --convert-to png exports each slide as a separate PNG
        cmd = [
            libreoffice_path,
            "--headless",
            "--convert-to",
            "png",
            "--outdir",
            str(temp_path),
            str(pptx_path),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
            )

            if result.returncode != 0:
                raise RuntimeError(f"LibreOffice conversion failed: {result.stderr or result.stdout}")

            # LibreOffice creates files like: filename.png (single image for all slides)
            # or filename-1.png, filename-2.png, etc.
            png_files = sorted(temp_path.glob("*.png"))

            if not png_files:
                raise RuntimeError("LibreOffice did not produce any PNG files")

            # Check for LibreOffice behavior variance
            if len(png_files) == 1 and total_slides > 1:
                raise RuntimeError(
                    f"LibreOffice produced only 1 image for {total_slides} slides. "
                    "Try updating LibreOffice or use get_slide_export_instructions for manual export."
                )

            # Copy files to output directory
            output_files = []
            for i, png_file in enumerate(png_files, 1):
                output_file = output_dir / f"slide_{i}.png"
                shutil.copy2(png_file, output_file)
                output_files.append(output_file)

            return output_files

        except subprocess.TimeoutExpired:
            raise RuntimeError("LibreOffice conversion timed out after 120 seconds")


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

Alternatively, use the export_slide_as_image tool for automatic conversion.
"""


@mcp.tool()
def export_slide_as_image(
    file_path: str,
    slide_number: int | None = None,
    output_path: str | None = None,
) -> str:
    """
    Export a slide (or all slides) from a PowerPoint presentation as PNG image(s).

    Requires LibreOffice to be installed on the system.

    Args:
        file_path: Path to the PowerPoint file
        slide_number: Optional specific slide number (1-indexed). If None, exports all slides.
        output_path: Optional output directory path. If None, creates images next to the input file.

    Returns:
        Path(s) to the exported image file(s), or error message
    """
    # Validate input file
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return f"Error: File not found: {path}"

    # Validate slide number if provided
    prs = Presentation(str(path))
    total_slides = len(prs.slides)

    if slide_number is not None:
        if slide_number < 1 or slide_number > total_slides:
            return f"Error: Slide {slide_number} does not exist. Presentation has {total_slides} slides."

    # Find LibreOffice
    libreoffice = _find_libreoffice()
    if not libreoffice:
        return """Error: LibreOffice is not installed or not found in PATH.

To install LibreOffice:
  macOS: Download from https://www.libreoffice.org/download/download/
  Ubuntu/Debian: sudo apt install libreoffice
  Fedora: sudo dnf install libreoffice
  Windows: Download from https://www.libreoffice.org/download/download/

After installation, try running this tool again."""

    # Determine output directory
    if output_path:
        output_dir = Path(output_path).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = path.parent

    try:
        # Convert all slides to images
        image_files = _convert_pptx_to_images(path, output_dir, libreoffice, total_slides)

        if slide_number is not None:
            # Return only the requested slide
            if slide_number <= len(image_files):
                target_file = image_files[slide_number - 1]
                # Rename to include original filename
                final_name = f"{path.stem}_slide_{slide_number}.png"
                final_path = output_dir / final_name
                target_file.rename(final_path)

                # Clean up other slides (use index to avoid path comparison issues)
                for i, img in enumerate(image_files):
                    if i != slide_number - 1 and img.exists():
                        img.unlink()

                return f"Exported slide {slide_number} to: {final_path}"
            else:
                return f"Error: Slide {slide_number} was not exported. Only {len(image_files)} images were created."
        else:
            # Rename all files to include original filename
            renamed_files = []
            for i, img in enumerate(image_files, 1):
                final_name = f"{path.stem}_slide_{i}.png"
                final_path = output_dir / final_name
                if img.exists():
                    img.rename(final_path)
                    renamed_files.append(str(final_path))

            return f"Exported {len(renamed_files)} slides to:\n" + "\n".join(renamed_files)

    except RuntimeError as e:
        return f"Error during conversion: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"
