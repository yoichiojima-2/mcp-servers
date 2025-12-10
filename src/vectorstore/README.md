# vectorstore

MCP server for ChromaDB vector store operations.

## Features

- **Collection Management**: Create, list, delete, and inspect collections
- **Document CRUD**: Add, get, update, upsert, and delete documents
- **Similarity Search**: Query with filters, metadata, and distance scores
- **Persistent Storage**: Data survives server restarts

## Tools

| Tool | Description |
|------|-------------|
| `create_collection` | Create a new collection with optional metadata |
| `list_collections` | List all collections |
| `delete_collection` | Delete a collection |
| `get_collection_info` | Get collection details (count, metadata) |
| `add_documents` | Add documents with optional metadata and IDs |
| `get_documents` | Get documents by IDs or filters |
| `update_documents` | Update existing documents |
| `upsert_documents` | Add or update documents |
| `delete_documents` | Delete documents by IDs or filter |
| `query` | Similarity search with filters and distance scores |

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `CHROMA_PATH` | No | Path for persistent storage (default: `./chroma_data`) |
| `EMBEDDING_TYPE` | No | `openai` (default) or `default` for ChromaDB embeddings |
| `OPENAI_API_KEY` | Yes* | Required when using OpenAI embeddings |
| `OPENAI_EMBEDDING_MODEL` | No | Model to use (default: `text-embedding-3-small`) |

*Not required when using `EMBEDDING_TYPE=default`.

## Embedding Models

Available OpenAI models:
- `text-embedding-3-small` (1536 dimensions, cost-effective) - **Default**
- `text-embedding-3-large` (3072 dimensions, best quality)
- `text-embedding-ada-002` (1536 dimensions, legacy)

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

## Usage

```bash
export OPENAI_API_KEY="sk-..."
uv run python -m vectorstore
```

See [server guide](../../docs/server-guide.md) for common CLI options.
