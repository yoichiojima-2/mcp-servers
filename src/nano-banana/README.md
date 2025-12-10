# nano-banana MCP Server

MCP server for AI image generation using Google Gemini's Nano Banana models.

## Features

- **Text-to-Image**: Generate images from text descriptions
- **Image Editing**: Modify existing images with text prompts
- **Slide Assets**: Create presentation-ready graphics (icons, backgrounds, diagrams)
- **Image Fusion**: Combine multiple images based on instructions
- **Base64 Export**: Convert images for embedding in HTML/Markdown

## Tools

### `generate_image`
Generate an image from a text description.

**Parameters:**
- `prompt` (str): Text description of the image to generate
- `output_path` (str): Path for the output image file (.png, .jpg, .webp)
- `model` (str, optional): Model to use - "flash" (faster) or "pro" (higher quality). Default: "flash"
- `style` (str, optional): Style modifier (e.g., "flat design", "3D render", "watercolor")

### `edit_image`
Edit an existing image based on text instructions.

**Parameters:**
- `image_path` (str): Path to the input image to edit
- `prompt` (str): Instructions for how to modify the image
- `output_path` (str): Path for the output edited image
- `model` (str, optional): Model to use - "flash" or "pro". Default: "flash"

### `generate_slide_asset`
Generate presentation-ready graphics optimized for slides.

**Parameters:**
- `asset_type` (str): Type of asset - "icon", "background", "diagram", "illustration", "hero", "photo"
- `description` (str): What the asset should depict
- `output_path` (str): Path for the output image
- `theme` (str, optional): Visual theme - "modern", "minimal", "dark", "vibrant", "corporate". Default: "modern"
- `model` (str, optional): Model to use - "flash" or "pro". Default: "flash"

### `fuse_images`
Combine multiple images based on instructions.

**Parameters:**
- `image_paths` (list[str]): List of paths to input images (2-5 images)
- `prompt` (str): Instructions for how to combine the images
- `output_path` (str): Path for the output combined image
- `model` (str, optional): Model to use - "flash" or "pro". Default: "pro"

### `image_to_base64`
Convert an image file to base64 string for embedding.

**Parameters:**
- `image_path` (str): Path to the image file

## Requirements

- Python 3.12+
- Google Gemini API key

## Installation

Set your API key:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).

## Usage

### Run the server

```bash
uv run python -m nano_banana
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | (required) | Google Gemini API key |
| `GOOGLE_API_KEY` | - | Alternative API key env var |
| `NAME` | `nano-banana` | Server name |
| `TRANSPORT` | `stdio` | Transport protocol (`sse` or `stdio`) |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8010` | Server port |
| `ALLOW_ORIGIN` | `*` | CORS allowed origins |

## Models

| Model | ID | Best For |
|-------|-----|----------|
| flash | `gemini-2.5-flash-image` | Fast iteration, drafts |
| pro | `gemini-2.5-pro` | Final assets, complex compositions |

## Testing

```bash
uv run pytest -v
```
