# o3

MCP server for deep research using OpenAI o3 with web search capabilities.

## Features

- Web search powered by OpenAI o3
- Natural language queries for research and planning
- Latest information retrieval
- Error troubleshooting assistance
- Design and architecture consulting

## Tools

| Tool | Description |
|------|-------------|
| `o3` | AI agent with web search for research and problem-solving |

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key with o3 access |
| `O3_MODEL` | No | Model to use (default: `o3`) |

## Usage

```bash
export OPENAI_API_KEY="your-api-key"
uv run python -m o3_search
```

See [server guide](../../docs/server-guide.md) for common CLI options.
