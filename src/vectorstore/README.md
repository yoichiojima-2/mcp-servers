# Vectorstore MCP Server

An MCP server for ChromaDB vector store operations.

## Features

- **Collection Management**: Create, list, delete, and inspect collections
- **Document CRUD**: Add, get, update, upsert, and delete documents
- **Similarity Search**: Query with filters, metadata, and distance scores
- **Persistent Storage**: Data survives server restarts

## Installation

```bash
cd vectorstore
uv sync
```

## Usage

### Run as MCP Server

```bash
# SSE transport (default)
uv run python -m vectorstore

# stdio transport
TRANSPORT=stdio uv run python -m vectorstore
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CHROMA_PATH` | `./chroma_data` | Path for persistent storage |
| `EMBEDDING_TYPE` | `openai` | Embedding model type (`default` or `openai`) |
| `OPENAI_API_KEY` | - | OpenAI API key (required when using OpenAI embeddings) |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model to use |
| `NAME` | `vectorstore` | Server name |
| `TRANSPORT` | `sse` | Transport type (`sse` or `stdio`) |
| `HOST` | `0.0.0.0` | Host to bind |
| `PORT` | `8002` | Port to bind |
| `ALLOW_ORIGIN` | `*` | CORS allowed origins |

### Embedding Models

By default, the server uses OpenAI's `text-embedding-3-small` model. You need to set your OpenAI API key:

```bash
export OPENAI_API_KEY=sk-...
uv run python -m vectorstore
```

**Available OpenAI embedding models:**
- `text-embedding-3-small` (1536 dimensions, cost-effective) - **Default**
- `text-embedding-3-large` (3072 dimensions, best quality)
- `text-embedding-ada-002` (1536 dimensions, legacy)

To change the model:
```bash
export OPENAI_EMBEDDING_MODEL=text-embedding-3-large
```

To use ChromaDB's default embeddings instead:
```bash
export EMBEDDING_TYPE=default
```

### Claude Desktop Configuration

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "vectorstore": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/vectorstore", "python", "-m", "vectorstore"],
      "env": {
        "TRANSPORT": "stdio",
        "CHROMA_PATH": "/path/to/chroma_data",
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

**To use a different OpenAI model:**
```json
{
  "mcpServers": {
    "vectorstore": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/vectorstore", "python", "-m", "vectorstore"],
      "env": {
        "TRANSPORT": "stdio",
        "CHROMA_PATH": "/path/to/chroma_data",
        "OPENAI_API_KEY": "sk-...",
        "OPENAI_EMBEDDING_MODEL": "text-embedding-3-large"
      }
    }
  }
}
```

**To use ChromaDB's default embeddings:**
```json
{
  "mcpServers": {
    "vectorstore": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/vectorstore", "python", "-m", "vectorstore"],
      "env": {
        "TRANSPORT": "stdio",
        "CHROMA_PATH": "/path/to/chroma_data",
        "EMBEDDING_TYPE": "default"
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

# Run tests (automatically uses default embeddings for testing)
make test
# or
EMBEDDING_TYPE=default uv run pytest

# Format code
uv run ruff format .
uv run isort .
```

**Note:** Tests use ChromaDB's default embeddings to avoid requiring an OpenAI API key during development.
