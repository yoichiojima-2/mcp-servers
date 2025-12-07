# ChromaDB MCP Server

An MCP server for ChromaDB vector store operations.

## Features

- **Collection Management**: Create, list, delete, and inspect collections
- **Document CRUD**: Add, get, update, upsert, and delete documents
- **Similarity Search**: Query with filters, metadata, and distance scores
- **Persistent Storage**: Data survives server restarts

## Installation

```bash
cd chroma
uv sync
```

## Usage

### Run as MCP Server

```bash
# SSE transport (default)
uv run python -m chroma

# stdio transport
TRANSPORT=stdio uv run python -m chroma
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CHROMA_PATH` | `./chroma_data` | Path for persistent storage |
| `NAME` | `chroma` | Server name |
| `TRANSPORT` | `sse` | Transport type (`sse` or `stdio`) |
| `HOST` | `0.0.0.0` | Host to bind |
| `PORT` | `8002` | Port to bind |
| `ALLOW_ORIGIN` | `*` | CORS allowed origins |

### Claude Desktop Configuration

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "chroma": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/chroma", "python", "-m", "chroma"],
      "env": {
        "TRANSPORT": "stdio",
        "CHROMA_PATH": "/path/to/chroma_data"
      }
    }
  }
}
```

## Tools

### Collection Management

| Tool | Description |
|------|-------------|
| `create_collection` | Create a new collection with optional metadata |
| `list_collections` | List all collections |
| `delete_collection` | Delete a collection |
| `get_collection_info` | Get collection details (count, metadata) |

### Document CRUD

| Tool | Description |
|------|-------------|
| `add_documents` | Add documents with optional metadata and IDs |
| `get_documents` | Get documents by IDs or filters |
| `update_documents` | Update existing documents |
| `upsert_documents` | Add or update documents |
| `delete_documents` | Delete documents by IDs or filter |

### Query

| Tool | Description |
|------|-------------|
| `query` | Similarity search with filters and distance scores |

## Filter Syntax

### Metadata Filters (`where`)

```json
{"category": "science"}
{"$and": [{"category": "science"}, {"year": {"$gte": 2020}}]}
```

### Document Filters (`where_document`)

```json
{"$contains": "keyword"}
```

## Development

```bash
# Install dev dependencies
uv sync

# Run tests
uv run pytest

# Format code
uv run ruff format .
uv run isort .
```
