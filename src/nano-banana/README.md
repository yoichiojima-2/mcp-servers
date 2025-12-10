# nano-banana

MCP server for AI image generation using Google Gemini's Nano Banana models.

## Features

- **Text-to-Image**: Generate images from text descriptions
- **Image Editing**: Modify existing images with text prompts
- **Slide Assets**: Create presentation-ready graphics (icons, backgrounds, diagrams)
- **Image Fusion**: Combine multiple images based on instructions
- **Base64 Export**: Convert images for embedding in HTML/Markdown

## Tools

| Tool | Description |
|------|-------------|
| `generate_image` | Generate image from text description |
| `edit_image` | Edit existing image based on instructions |
| `generate_slide_asset` | Create presentation-ready graphics |
| `fuse_images` | Combine 2-5 images based on instructions |
| `image_to_base64` | Convert image to base64 for embedding |

## Models

| Model | ID | Best For |
|-------|-----|----------|
| flash | `gemini-2.5-flash-image` | Fast iteration, drafts |
| pro | `gemini-3-pro-image-preview` | Final assets, up to 4K resolution |

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `GOOGLE_API_KEY` | No | Alternative API key env var |

Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).

## Usage

```bash
export GEMINI_API_KEY="your-api-key"
uv run python -m nano_banana
```

See [server guide](../../docs/server-guide.md) for common CLI options.
