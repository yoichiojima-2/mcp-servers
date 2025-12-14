# img2pptx MCP Server

Convert slide images (e.g., from nano-banana) to editable PowerPoint presentations using OpenAI GPT-5.2 vision.

## Features

- **Image to PPTX**: Convert slide images to editable PowerPoint
- **Multi-slide support**: Combine multiple images into one presentation
- **GPT-5.2 extraction**: Uses vision AI to extract text, structure, and speaker notes

## Tools

### `get_workspace_path`
Get the shared workspace directory path.

### `image_to_pptx`
Convert a single slide image to PPTX.

| Parameter | Type | Description |
|-----------|------|-------------|
| `image_path` | string | Path to the slide image |
| `output_path` | string | Path for the output PPTX |

### `images_to_pptx`
Convert multiple slide images to a single PPTX.

| Parameter | Type | Description |
|-----------|------|-------------|
| `image_paths` | list[string] | Paths to slide images (in order) |
| `output_path` | string | Path for the output PPTX |

## Requirements

- Python 3.12+
- OpenAI API key with GPT-5.2 access

## Installation

```bash
cd src/img2pptx
uv sync
```

## Configuration

Set your OpenAI API key:

```bash
export OPENAI_API_KEY=your-api-key
```

## Usage

```bash
uv run fastmcp run server.py
```

## Testing

```bash
uv run pytest -v
```
