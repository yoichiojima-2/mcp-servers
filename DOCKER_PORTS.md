# Docker Port Assignments

This document tracks port assignments for all MCP servers to prevent conflicts when running multiple containers.

## Port Allocation Table

| Server       | Port | URL                           | Notes                                    |
|--------------|------|-------------------------------|------------------------------------------|
| dify         | 8001 | http://localhost:8001/sse     | Dify AI platform integration             |
| vectorstore  | 8002 | http://localhost:8002/sse     | Vector database operations               |
| pptx         | 8003 | http://localhost:8003/sse     | PowerPoint operations                    |
| xlsx         | 8004 | http://localhost:8004/sse     | Spreadsheet operations                   |
| docx         | 8005 | http://localhost:8005/sse     | Word document operations                 |
| langquery    | 8006 | http://localhost:8006/sse     | Language query operations                |
| browser      | 8007 | http://localhost:8007/sse     | Browser automation (Playwright)          |
| pdf          | 8008 | http://localhost:8008/sse     | PDF manipulation and extraction          |
| **composite**| **8000** | **http://localhost:8000/sse** | **Lightweight proxy routing to backends** |

## Usage Notes

### Running Individual Servers

Each server can run independently on its assigned port:

```bash
cd src/<server-name>
docker compose up -d
```

### Running Composite Server

The composite server is a lightweight HTTP proxy that routes requests to independent backend containers:

```bash
cd src/composite
docker compose up -d
```

**Benefits:**
- Fast builds (lightweight proxy, <1 min)
- Independent backend scaling
- Enable/disable backends via YAML config
- Microservices architecture

### For Dify Integration

Edit `src/composite/composite-config.yaml` to enable/disable backends:
- Run: `cd src/composite && docker compose up -d`
- Connect Dify to: `http://localhost:8000/sse`

The composite server will route requests to the appropriate backend based on tool name prefixes.

### Port Conflict Prevention

**Scenario 1**: Running composite + individual servers
- The composite server in `src/composite/docker-compose.yml` starts all backends automatically
- Backend services are on an internal Docker network, not exposed to host
- Only the composite proxy is exposed on port 8000

**Scenario 2**: Running individual backend servers standalone
- ✓ DO: Run any combination of individual servers (no conflicts)
- Example: `browser` (8007) + `pdf` (8008) + `xlsx` (8004)

**Scenario 3**: Testing locally vs Docker
- ✓ DO: Change docker-compose port mappings if running local dev on same port
- Example: Change `"8000:8000"` to `"8010:8000"` to avoid conflict with local port 8000

## Changing Ports

To change a server's external port, edit its `docker-compose.yml`:

```yaml
ports:
  - "9000:8000"  # External:Internal
  # Now accessible at http://localhost:9000/sse
```

The internal port (right side) should not be changed without also updating the Dockerfile ENV variables.
