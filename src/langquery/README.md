# langquery

An MCP server that allows clients to manipulate table data using natural language. Built with [FastMCP](https://github.com/jlowin/fastmcp) and [DuckDB](https://duckdb.org/).

## Features

- **SQL Query**: Execute DuckDB SQL queries on any data files (CSV, Parquet, JSON, etc.)
- **Query History**: Automatic logging of all queries with results, execution time, and error tracking
- **Result Caching**: Retrieve results from previous queries without re-execution
- **Shell Commands**: Run shell commands for file operations and data preparation
- **Math Operations**: Basic arithmetic tools (add, sub, mul, div)
- **Prompts**: Pre-built prompt for data analysis workflows

## Installation

```bash
uv sync
```

## Usage

### Run the server

```bash
uv run python -m langquery
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NAME` | `langquery` | Server name |
| `TRANSPORT` | `sse` | Transport protocol (`sse` or `stdio`) |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `ALLOW_ORIGIN` | `*` | CORS allowed origins |

### Docker

```bash
docker compose up
```

## Tools

| Tool | Description |
|------|-------------|
| `query` | Execute DuckDB SQL and return results as markdown (automatically logged to history) |
| `get_query_history` | View recent query history with execution metrics (default: last 20 queries) |
| `get_cached_result` | Retrieve cached result from a previous query by ID |
| `search_query_history` | Search query history by query text |
| `clear_query_history` | Clear all query history (WARNING: permanently deletes all logged queries) |
| `shell` | Execute shell commands |
| `add` | Add two numbers |
| `sub` | Subtract two numbers |
| `mul` | Multiply two numbers |
| `div` | Divide two numbers |
| `get_langquery_prompt` | Get a pre-built data analysis prompt |

## Example

Query a CSV file:

```sql
SELECT * FROM 'workspace/data.csv' LIMIT 10
```

## Query History

All queries are automatically logged to `workspace/langquery_history.db` with:
- Query text and timestamp
- Execution time and row count
- Full query results (cached)
- Error messages for failed queries

The history database automatically keeps only the last 100 queries to manage storage.

### Using Query History

View recent queries:
```python
get_query_history(limit=20)
```

Retrieve a cached result without re-executing:
```python
get_cached_result(query_id=42)
```

Search for specific queries:
```python
search_query_history(search_term="sales", limit=10)
```

Clear all history:
```python
clear_query_history()
```

### Security Considerations

**IMPORTANT:** Query history logs all SQL queries with their full results. Be aware of the following:

- **Sensitive Data**: Queries containing passwords, API keys, tokens, or PII (Personally Identifiable Information) will be logged in plaintext
- **Data Exposure**: Query results are cached and stored unencrypted in `workspace/langquery_history.db`
- **Storage Location**: The history database file is stored locally and persists between sessions

**Best Practices:**
1. **Avoid sensitive data in queries** - Don't use hardcoded credentials or PII in WHERE clauses
2. **Regular cleanup** - Use `clear_query_history()` to remove sensitive data after use
3. **Access control** - Ensure the workspace directory has appropriate file permissions
4. **Consider encryption** - For production use with sensitive data, consider encrypting the workspace directory
5. **Review logs** - Periodically review history to ensure no sensitive data is being logged

**Storage Management:**
- Results over 1MB are automatically truncated to prevent memory issues
- History is automatically cleaned to keep last 100 queries
- Manual cleanup available via `clear_query_history()` tool

### Migration and Compatibility

**Existing Installations:**
- Query history is a new feature that does not affect existing langquery functionality
- The history database is created automatically on first use in the `workspace/` directory
- No changes required to existing queries - all queries are automatically logged
- Existing queries will start appearing in history immediately after upgrade
- No migration or data conversion needed

**Performance Impact:**
- Minimal overhead: ~1-2ms per query for logging
- Cleanup runs every 10 queries (configurable) with negligible impact
- Cached results improve performance for repeated queries
- Database file grows up to ~10-50MB depending on query volume (auto-cleaned to 100 queries by default)

**Disabling History:**
If you need to disable history logging for specific use cases, you can clear it regularly with `clear_query_history()` or configure a smaller `LANGQUERY_MAX_HISTORY_SIZE`.

### Configuration

The query history feature can be configured via environment variables:

| Variable | Default | Min | Max | Description |
|----------|---------|-----|-----|-------------|
| `LANGQUERY_WORKSPACE` | `workspace` | - | - | Directory for storing the history database file |
| `LANGQUERY_MAX_RESULT_SIZE` | `1048576` (1MB) | 1KB | 10MB | Maximum size for cached query results in bytes |
| `LANGQUERY_MAX_HISTORY_SIZE` | `100` | 1 | 10,000 | Maximum number of queries to keep in history |
| `LANGQUERY_CLEANUP_FREQUENCY` | `10` | 1 | 1,000 | Run cleanup every N queries |

Example:
```bash
export LANGQUERY_MAX_HISTORY_SIZE=200
export LANGQUERY_CLEANUP_FREQUENCY=20
uv run python -m langquery
```

### Multi-Process Limitations

**WARNING:** The query history feature uses a file-based DuckDB database which is designed for single-process access. Running multiple langquery server instances concurrently that share the same workspace directory may lead to database corruption or locking issues.

**Recommendations:**
- **Single Process**: Use one langquery server instance per workspace directory
- **Separate Workspaces**: If running multiple instances, use different workspace directories for each
- **Process Coordination**: If multi-process access is required, consider implementing external coordination (e.g., file locks) or use a client-server database

The implementation is thread-safe within a single process but does not support concurrent access from multiple processes.
