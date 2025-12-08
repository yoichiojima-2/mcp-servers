# Using OpenAI Embeddings with Vectorstore

This guide shows how to use OpenAI's embedding models with the vectorstore MCP server.

## Setup

1. Get your OpenAI API key from https://platform.openai.com/api-keys

2. Set environment variables:
```bash
export OPENAI_API_KEY=sk-...
export EMBEDDING_TYPE=openai
export OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

3. Install dependencies:
```bash
cd vectorstore
uv sync
```

## Running with OpenAI Embeddings

### Local Development
```bash
cd vectorstore
export EMBEDDING_TYPE=openai
export OPENAI_API_KEY=sk-...
uv run python -m vectorstore
```

### Docker
```bash
cd vectorstore
export EMBEDDING_TYPE=openai
export OPENAI_API_KEY=sk-...
docker compose up
```

### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "vectorstore": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/vectorstore", "python", "-m", "vectorstore"],
      "env": {
        "TRANSPORT": "stdio",
        "CHROMA_PATH": "/path/to/chroma_data",
        "EMBEDDING_TYPE": "openai",
        "OPENAI_API_KEY": "sk-...",
        "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small"
      }
    }
  }
}
```

## Embedding Model Options

### text-embedding-3-small (Recommended)
- **Dimensions:** 1536
- **Cost:** $0.02 / 1M tokens
- **Best for:** Cost-effective general purpose embeddings
```bash
export OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### text-embedding-3-large
- **Dimensions:** 3072
- **Cost:** $0.13 / 1M tokens
- **Best for:** High-quality embeddings, maximum accuracy
```bash
export OPENAI_EMBEDDING_MODEL=text-embedding-3-large
```

### text-embedding-ada-002 (Legacy)
- **Dimensions:** 1536
- **Cost:** $0.10 / 1M tokens
- **Best for:** Legacy compatibility
```bash
export OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
```

## Usage Example

Once configured, use the vectorstore tools as normal. The only difference is that documents will be embedded using OpenAI's models instead of ChromaDB's default:

```python
# Create a collection (with OpenAI embeddings)
create_collection(name="my_docs")

# Add documents (will be embedded with OpenAI)
add_documents(
    collection="my_docs",
    documents=[
        "OpenAI provides powerful embedding models",
        "Vector databases enable semantic search"
    ]
)

# Query (query will also be embedded with OpenAI)
query(
    collection="my_docs",
    query_texts=["What are embeddings?"],
    n_results=5
)
```

## Important Notes

1. **API Key Security:** Never commit your OpenAI API key to version control
2. **Cost:** OpenAI embeddings have per-token costs. Monitor your usage
3. **Rate Limits:** OpenAI has rate limits. For large batches, implement retry logic
4. **Consistency:** Once a collection is created with a specific embedding model, continue using the same model for queries to ensure consistent results

## Switching Between Embedding Models

To switch back to default embeddings:
```bash
export EMBEDDING_TYPE=default
# or simply unset it
unset EMBEDDING_TYPE
```

**Note:** Collections created with OpenAI embeddings should continue to use OpenAI embeddings. Mixing embedding types within a collection will produce incorrect similarity results.
