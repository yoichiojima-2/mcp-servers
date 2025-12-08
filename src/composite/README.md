# mcp composite server

a bundled mcp server that aggregates multiple mcp backend servers into a single container. all dependencies are packaged together for simple deployment with no proxy overhead.

## features

- **single container**: all servers bundled into one deployment unit
- **no network overhead**: direct in-process communication
- **simpler deployment**: just one container to manage
- **tool namespacing**: prefixes prevent naming conflicts
- **single endpoint**: dify sees one url, all tools available

## architecture comparison

### composite approach (this server)
```
dify → composite:8000 (all servers bundled)
```

**pros:**
- single container
- no network overhead
- simpler deployment
- no latency penalty

**cons:**
- large image (~1.5gb)
- slow builds (~10+ min)
- monolithic scaling
- must rebuild to change backend configuration

### proxy approach (alternative)
```
dify → proxy:8000 → browser:8007
                  → pdf:8008
                  → xlsx:8004
                  → ...
```

**pros:**
- tiny proxy image (~200mb vs 1.5gb composite)
- fast builds (~1 min proxy, backends build in parallel)
- independent scaling
- selective deployment (only run backends you need)
- runtime reconfiguration without rebuilding

**cons:**
- requires all backend containers running
- network hop adds latency (~5-10ms)
- more complex orchestration (n+1 containers)

## installation

```bash
cd src/composite
uv sync
```

## quick start with docker

### 1. configure environment variables

```bash
cp .env.example .env
# edit .env with your api keys
```

### 2. configure backends

edit `composite-config.yaml` to enable/disable backends:

```yaml
backends:
  - name: browser
    url: http://browser:8007/sse
    enabled: true  # set to false to disable

  - name: dify
    url: http://dify:8001/sse
    enabled: true
```

### 3. build and run

```bash
docker compose up -d
```

the composite server will be available at: **http://localhost:8000/sse**

## configuration

### composite-config.yaml

```yaml
backends:
  - name: browser           # unique identifier
    url: http://browser:8007/sse  # backend sse endpoint
    prefix: browser        # tool name prefix
    enabled: true          # enable/disable
    description: browser automation
```

**configuration fields:**
- `name`: unique backend identifier
- `url`: backend server sse endpoint (use docker service names)
- `prefix`: prepended to tool names (e.g., `browser_navigate`)
- `enabled`: set to false to disable without removing config
- `description`: human-readable description (optional)

### environment variables

**composite configuration:**
- `COMPOSITE_CONFIG_PATH`: path to yaml config (default: ./composite-config.yaml)
- `HOST`: server host (default: 0.0.0.0)
- `PORT`: server port (default: 8000)

**backend-specific** (see individual server docs):
- `DIFY_API_KEY`, `DIFY_CONSOLE_API_KEY`: required if dify enabled
- `OPENAI_API_KEY`: required if vectorstore enabled
- `BROWSER_TIMEOUT`, `NAVIGATION_TIMEOUT`: optional browser config

## usage

### standalone (no docker)

```bash
# start backend servers first
cd src/browser && TRANSPORT=sse PORT=8007 uv run python -m browser &
cd src/pdf && TRANSPORT=sse PORT=8008 uv run python -m pdf &
# ...

# start composite server
cd src/composite
COMPOSITE_CONFIG_PATH=./composite-config.yaml uv run python -m composite
```

### docker compose

```bash
# start all services
docker compose up -d

# view logs
docker compose logs -f composite

# stop services
docker compose down
```

### connect to dify

in dify configuration:
- **url**: `http://localhost:8000/sse`
- **transport**: sse

## port allocation

see [../../DOCKER_PORTS.md](../../DOCKER_PORTS.md) for complete port assignments:

- composite: 8000
- vectorstore: 8002
- pptx: 8003
- xlsx: 8004
- docx: 8005
- langquery: 8006
- browser: 8007
- pdf: 8008

## selective deployment

disable backends you don't need:

```yaml
# composite-config.yaml - enable only browser and pdf
backends:
  - name: browser
    enabled: true

  - name: pdf
    enabled: true

  - name: xlsx
    enabled: false  # disabled

  - name: docx
    enabled: false  # disabled
```

then in docker-compose.yml, comment out unused services:

```bash
# only start composite and enabled backends
docker compose up -d composite browser pdf
```

## troubleshooting

### error: connection refused to backend

check if backend service is running:
```bash
docker compose ps
docker compose logs browser  # check specific backend
```

ensure backend urls in `composite-config.yaml` use docker service names (not localhost).

### error: no configuration file found

set `COMPOSITE_CONFIG_PATH` environment variable:
```bash
export COMPOSITE_CONFIG_PATH=/path/to/composite-config.yaml
```

### tools not appearing in dify

1. check composite logs: `docker compose logs composite`
2. verify backend is enabled in config
3. test backend directly: `curl http://localhost:8007/sse` (adjust port)
4. ensure backend has `TRANSPORT=sse` environment variable

### slow build times

the composite server bundles all dependencies, resulting in:
- large docker image (~1.5gb)
- slow builds (~10+ min)

if this is problematic, consider using the proxy server approach instead for faster iteration.

## comparison with proxy

| feature | composite | proxy |
|---------|-----------|-------|
| image size | ~1.5gb | ~200mb |
| build time | ~10 min | ~1 min |
| containers | 1 | n+1 |
| latency | none | +5-10ms |
| scaling | monolithic | independent |
| deployment | simple | complex |

**use composite when:**
- you want simplest deployment
- latency is critical
- you always need all servers
- you're primarily targeting dify

**use proxy when:**
- you need independent scaling
- you want fast builds
- you only need subset of servers
- you have multiple clients with different needs

## testing

```bash
uv run pytest
```

## development

the composite server bundles all backend dependencies. key components:

- `src/composite/server.py`: main composite server logic
- `composite-config.yaml`: backend configuration
- `Dockerfile`: lightweight container setup
- `docker-compose.yml`: orchestrates composite + backends

## architecture notes

**how tool routing works:**

1. client calls `browser_navigate`
2. composite identifies prefix `browser` → routes to browser backend
3. strips prefix: `navigate`
4. forwards to `http://browser:8007/sse` with method `tools/call` and name `navigate`
5. backend processes request
6. composite returns result to client

**why sse only:**

backends must expose sse endpoints because:
- dify requires sse transport
- http makes routing simpler than stdio
- containers communicate over network

**connection pooling:**

composite maintains persistent httpx client for efficient backend communication. connections are reused across requests.
