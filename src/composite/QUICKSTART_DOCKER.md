# Composite MCP Server - Docker Quick Start

Get all MCP servers running with a single Docker container and one URL for Dify.

## Prerequisites

- Docker and Docker Compose installed
- API keys for enabled servers (Dify, OpenAI if vectorstore is enabled)

## Setup (3 steps)

### 1. Configure Environment Variables

```bash
cd src/composite
cp .env.docker.example .env
```

Edit `.env` and add your API keys:
```bash
DIFY_API_KEY=sk-your-dify-key-here
DIFY_CONSOLE_API_KEY=your-console-key-here
OPENAI_API_KEY=sk-your-openai-key-here  # if vectorstore enabled
```

### 2. Choose Which Servers to Enable

Edit `composite-config.yaml` to control which MCP servers are included:

```yaml
servers:
  - name: browser
    enabled: true   # ✓ Include browser automation

  - name: pdf
    enabled: true   # ✓ Include PDF tools

  - name: xlsx
    enabled: false  # ✗ Skip Excel tools
```

**Default configuration**: `dify` + `browser` enabled

### 3. Build and Run

```bash
docker compose up -d
```

The server will be available at: **http://localhost:8000/sse**

## Connect to Dify

In your Dify configuration, add an MCP server connection:

- **URL**: `http://localhost:8000/sse`
- **Transport**: SSE

You'll now have access to all enabled MCP tools through this single endpoint!

## Verify It's Working

Check the logs:
```bash
docker compose logs -f
```

You should see:
```
loaded 'browser': X tools, Y prompts
loaded 'dify': X tools, Y prompts
Starting MCP server 'Composite: browser + dify' with transport 'sse'
```

## Common Operations

### Stop the server
```bash
docker compose down
```

### Restart after config changes
```bash
docker compose restart
```

### View logs
```bash
docker compose logs -f
```

### Rebuild after Dockerfile changes
```bash
docker compose up -d --build
```

## Enable/Disable Servers Without Rebuilding

Just edit `composite-config.yaml` and restart:

```bash
# 1. Edit composite-config.yaml (change enabled: true/false)
# 2. Restart
docker compose restart
```

No rebuild needed! The Docker image includes all servers.

## Troubleshooting

### Container won't start
```bash
# Check logs for errors
docker compose logs

# Common issues:
# - Missing API keys in .env
# - Port 8000 already in use
# - Invalid composite-config.yaml syntax
```

### Port conflict
If port 8000 is in use, edit `docker-compose.yml`:
```yaml
ports:
  - "9000:8000"  # Use external port 9000
```

Then access at `http://localhost:9000/sse`

### "Server failed to load" error
Check that the enabled server's dependencies are satisfied:
- `dify`: Requires DIFY_API_KEY
- `vectorstore`: Requires OPENAI_API_KEY
- All others: No API keys needed

## Next Steps

- See [README.md](README.md) for detailed configuration options
- See [../../DOCKER_PORTS.md](../../DOCKER_PORTS.md) for port assignments
- See individual server docs in `src/*/README.md` for server-specific features
