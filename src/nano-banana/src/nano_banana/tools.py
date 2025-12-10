"""
Nano Banana image generation tools.

Provides AI image generation using Google Gemini's Nano Banana models:
- gemini-2.5-flash-image (Nano Banana): Fast, efficient image generation
- gemini-3-pro-image-preview (Nano Banana Pro): Higher quality, up to 4K resolution
"""

import base64
import os
from io import BytesIO
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image

from . import mcp

# Constants
MAX_IMAGE_SIZE = 20_000_000  # 20MB limit for input images
ALLOWED_EXTENSIONS = frozenset([".png", ".jpg", ".jpeg", ".webp", ".gif"])
# Forbidden system directories (include /private/* for macOS compatibility)
FORBIDDEN_PATHS = frozenset(
    [
        "/bin",
        "/sbin",
        "/usr",
        "/etc",
        "/sys",
        "/proc",
        "/root",
        "/private/bin",
        "/private/etc",
    ]
)

# Model configuration
MODELS = {
    "flash": "gemini-2.5-flash-image",
    "pro": "gemini-3-pro-image-preview",
}
DEFAULT_MODEL = "flash"

# Asset-specific prompt templates
ASSET_PROMPTS = {
    "icon": "A simple, clean icon representing {desc}. Flat design, single color with subtle gradient, "
    "centered composition, transparent-friendly, suitable for presentations.",
    "background": "An abstract background pattern for {desc}. Subtle, not distracting, professional, "
    "suitable as a presentation slide background. {theme_style}",
    "diagram": "A clear conceptual diagram showing {desc}. Simple shapes, clear labels if needed, "
    "professional infographic style, easy to understand at a glance.",
    "illustration": "A stylized illustration of {desc}. Modern, professional, suitable for business "
    "presentations. Clean lines, cohesive color palette.",
    "hero": "A striking hero image for {desc}. High impact, professional, suitable for a presentation "
    "title slide. {theme_style}",
    "photo": "A photorealistic image of {desc}. High quality, professional lighting, suitable for "
    "business presentations.",
}

THEME_STYLES = {
    "modern": "Contemporary SaaS aesthetic with soft gradients and rounded shapes.",
    "minimal": "Minimalist design with lots of whitespace and simple geometric forms.",
    "dark": "Dark color scheme with light accents, moody and professional.",
    "vibrant": "Bold, saturated colors with high contrast and energy.",
    "corporate": "Conservative, professional palette with blues and grays.",
}


def _get_client() -> genai.Client:
    """Get configured Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable required")
    return genai.Client(api_key=api_key)


def _validate_output_path(path: Path) -> None:
    """Validate output path is safe to write to.

    Args:
        path: Path to validate (must already be resolved via expanduser().resolve())
    """
    # Path must be resolved before calling this function to prevent traversal attacks
    resolved_path = str(path.resolve())

    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Output file must have image extension {ALLOWED_EXTENSIONS}, got: {path.suffix}")

    for forbidden in FORBIDDEN_PATHS:
        if resolved_path.startswith(forbidden + "/"):
            raise ValueError(f"Cannot write to system directory: {forbidden}")

    if not path.parent.exists():
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise ValueError(f"Permission denied: cannot create {path.parent}")


def _save_image_from_response(response, output_path: Path) -> str | None:
    """Extract and save image from Gemini response."""
    if not response.candidates or not response.candidates[0].content.parts:
        return None

    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            image_data = BytesIO(part.inline_data.data)
            img = Image.open(image_data)
            img.save(output_path)
            return str(output_path)

    return None


def _load_image(image_path: str) -> Image.Image:
    """Load and validate an image file."""
    path = Path(image_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")

    if path.stat().st_size > MAX_IMAGE_SIZE:
        raise ValueError(f"Image file too large (max {MAX_IMAGE_SIZE // 1_000_000}MB)")

    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported image format: {path.suffix}")

    return Image.open(path)


# ======================================================
# Core Logic Functions (for testing)
# ======================================================


def _generate_image_impl(
    prompt: str,
    output_path: str,
    model: str = "flash",
    style: str | None = None,
) -> str:
    """Implementation of generate_image."""
    try:
        client = _get_client()

        if model not in MODELS:
            return f"Error: Unknown model '{model}'. Available: {list(MODELS.keys())}"

        output = Path(output_path).expanduser().resolve()
        _validate_output_path(output)

        full_prompt = f"{prompt}. Style: {style}" if style else prompt

        response = client.models.generate_content(
            model=MODELS[model],
            contents=full_prompt,
            config=types.GenerateContentConfig(response_modalities=["image", "text"]),
        )

        saved_path = _save_image_from_response(response, output)

        if saved_path:
            return f"Generated image saved to: {saved_path}"
        else:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "text") and part.text:
                    return f"Model response: {part.text}"
            return "Error: No image generated. Try a different prompt."

    except Exception as e:
        return f"Error generating image: {e}"


def _edit_image_impl(
    image_path: str,
    prompt: str,
    output_path: str,
    model: str = "flash",
) -> str:
    """Implementation of edit_image."""
    try:
        client = _get_client()

        if model not in MODELS:
            return f"Error: Unknown model '{model}'. Available: {list(MODELS.keys())}"

        img = _load_image(image_path)
        output = Path(output_path).expanduser().resolve()
        _validate_output_path(output)

        response = client.models.generate_content(
            model=MODELS[model],
            contents=[prompt, img],
            config=types.GenerateContentConfig(response_modalities=["image", "text"]),
        )

        saved_path = _save_image_from_response(response, output)

        if saved_path:
            return f"Edited image saved to: {saved_path}"
        else:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "text") and part.text:
                    return f"Model response: {part.text}"
            return "Error: No image generated. Try a different prompt."

    except Exception as e:
        return f"Error editing image: {e}"


def _generate_slide_asset_impl(
    asset_type: str,
    description: str,
    output_path: str,
    theme: str = "modern",
    model: str = "flash",
) -> str:
    """Implementation of generate_slide_asset."""
    try:
        if asset_type not in ASSET_PROMPTS:
            return f"Error: Unknown asset type '{asset_type}'. Available: {list(ASSET_PROMPTS.keys())}"

        if theme not in THEME_STYLES:
            return f"Error: Unknown theme '{theme}'. Available: {list(THEME_STYLES.keys())}"

        prompt_template = ASSET_PROMPTS[asset_type]
        theme_style = THEME_STYLES[theme]

        full_prompt = prompt_template.format(desc=description, theme_style=theme_style)

        return _generate_image_impl(
            prompt=full_prompt,
            output_path=output_path,
            model=model,
        )

    except Exception as e:
        return f"Error generating slide asset: {e}"


def _fuse_images_impl(
    image_paths: list[str],
    prompt: str,
    output_path: str,
    model: str = "pro",
) -> str:
    """Implementation of fuse_images."""
    try:
        if len(image_paths) < 2:
            return "Error: At least 2 images required for fusion"
        if len(image_paths) > 5:
            return "Error: Maximum 5 images supported"

        client = _get_client()

        if model not in MODELS:
            return f"Error: Unknown model '{model}'. Available: {list(MODELS.keys())}"

        images = [_load_image(p) for p in image_paths]
        output = Path(output_path).expanduser().resolve()
        _validate_output_path(output)

        contents = [prompt] + images

        response = client.models.generate_content(
            model=MODELS[model],
            contents=contents,
            config=types.GenerateContentConfig(response_modalities=["image", "text"]),
        )

        saved_path = _save_image_from_response(response, output)

        if saved_path:
            return f"Fused image saved to: {saved_path}"
        else:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "text") and part.text:
                    return f"Model response: {part.text}"
            return "Error: No image generated. Try a different prompt."

    except Exception as e:
        return f"Error fusing images: {e}"


def _image_to_base64_impl(image_path: str) -> str:
    """Implementation of image_to_base64."""
    try:
        path = Path(image_path).expanduser().resolve()

        if not path.exists():
            return f"Error: Image file not found: {path}"

        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            return f"Error: Unsupported image format: {path.suffix}"

        mime_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }

        mime_type = mime_types.get(path.suffix.lower(), "image/png")

        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")

        return f"data:{mime_type};base64,{encoded}"

    except Exception as e:
        return f"Error converting image to base64: {e}"


# ======================================================
# MCP Tools (thin wrappers around implementation)
# ======================================================


@mcp.tool()
def generate_image(
    prompt: str,
    output_path: str,
    model: str = "flash",
    style: str | None = None,
) -> str:
    """
    Generate an image from a text description.

    Creates high-quality images using Google Gemini's Nano Banana models.
    Excellent for presentation graphics, diagrams, icons, and illustrations.

    Args:
        prompt: Text description of the image to generate.
                Be specific about style, composition, colors, and mood.
                Example: "A minimalist icon of a rocket ship, flat design, blue gradient"
        output_path: Path for the output image file (.png, .jpg, .webp)
        model: Model to use:
               - "flash": Faster, good for iteration (default)
               - "pro": Higher quality, better for final assets
        style: Optional style modifier to append to prompt.
               Examples: "flat design", "3D render", "watercolor", "photorealistic"

    Returns:
        Path to the generated image file, or error message

    Example:
        generate_image(
            prompt="Modern tech company logo with abstract geometric shapes",
            output_path="~/presentations/logo.png",
            style="minimalist vector art"
        )
    """
    return _generate_image_impl(prompt, output_path, model, style)


@mcp.tool()
def edit_image(
    image_path: str,
    prompt: str,
    output_path: str,
    model: str = "flash",
) -> str:
    """
    Edit an existing image based on text instructions.

    Modify images by adding, removing, or changing elements.
    Useful for customizing stock images or refining generated images.

    Args:
        image_path: Path to the input image to edit
        prompt: Instructions for how to modify the image.
                Example: "Add a sunset background", "Remove the text", "Change color to blue"
        output_path: Path for the output edited image
        model: Model to use ("flash" or "pro")

    Returns:
        Path to the edited image file, or error message

    Example:
        edit_image(
            image_path="~/images/chart.png",
            prompt="Add a professional dark background and subtle grid lines",
            output_path="~/presentations/chart_styled.png"
        )
    """
    return _edit_image_impl(image_path, prompt, output_path, model)


@mcp.tool()
def generate_slide_asset(
    asset_type: str,
    description: str,
    output_path: str,
    theme: str = "modern",
    model: str = "flash",
) -> str:
    """
    Generate presentation-ready graphics optimized for slides.

    Creates assets specifically designed for professional presentations:
    icons, backgrounds, diagrams, illustrations, and decorative elements.

    Args:
        asset_type: Type of asset to generate:
                    - "icon": Simple, clear icons (e.g., for bullet points)
                    - "background": Full-slide backgrounds
                    - "diagram": Conceptual diagrams and flowcharts
                    - "illustration": Decorative illustrations
                    - "hero": Large hero images for title slides
                    - "photo": Photorealistic images
        description: What the asset should depict.
                     Example: "teamwork and collaboration", "data flowing through systems"
        output_path: Path for the output image
        theme: Visual theme to match presentation style:
               - "modern": Clean, gradient accents, tech-forward
               - "minimal": Simple, lots of whitespace
               - "dark": Dark backgrounds, light elements
               - "vibrant": Bold colors, high contrast
               - "corporate": Professional, subdued colors
        model: Model to use ("flash" or "pro")

    Returns:
        Path to the generated asset, or error message

    Example:
        generate_slide_asset(
            asset_type="icon",
            description="artificial intelligence and machine learning",
            output_path="~/presentations/ai_icon.png",
            theme="modern"
        )
    """
    return _generate_slide_asset_impl(asset_type, description, output_path, theme, model)


@mcp.tool()
def fuse_images(
    image_paths: list[str],
    prompt: str,
    output_path: str,
    model: str = "pro",
) -> str:
    """
    Combine multiple images based on instructions.

    Useful for creating composite images, applying styles from reference images,
    or merging visual elements from different sources.

    Args:
        image_paths: List of paths to input images (2-5 images)
        prompt: Instructions for how to combine the images.
                Example: "Combine these into a cohesive collage",
                         "Apply the style of the first image to the second"
        output_path: Path for the output combined image
        model: Model to use ("flash" or "pro", defaults to "pro" for better quality)

    Returns:
        Path to the fused image, or error message

    Example:
        fuse_images(
            image_paths=["~/images/style_ref.png", "~/images/content.png"],
            prompt="Apply the color palette and visual style of the first image to the second",
            output_path="~/presentations/styled_image.png"
        )
    """
    return _fuse_images_impl(image_paths, prompt, output_path, model)


@mcp.tool()
def image_to_base64(image_path: str) -> str:
    """
    Convert an image file to base64 string.

    Useful for embedding images in HTML, Markdown, or other formats
    that support inline base64 images.

    Args:
        image_path: Path to the image file

    Returns:
        Base64-encoded string with data URI prefix, or error message

    Example:
        image_to_base64("~/presentations/logo.png")
        # Returns: "data:image/png;base64,iVBORw0KGgo..."
    """
    return _image_to_base64_impl(image_path)
