# data-analysis

MCP server for data analysis using SQL queries on tabular data. Built with [DuckDB](https://duckdb.org/).

## Features

- **SQL Query**: Execute DuckDB SQL queries on any data files (CSV, Parquet, JSON, etc.)
- **Query History**: Automatic logging of all queries with results, execution time, and error tracking
- **Result Caching**: Retrieve results from previous queries without re-execution
- **Math Operations**: Basic arithmetic tools (add, sub, mul, div)

## Tools

| Tool | Description |
|------|-------------|
| `query` | Execute DuckDB SQL and return results as markdown |
| `get_query_history` | View recent query history with execution metrics |
| `get_cached_result` | Retrieve cached result from a previous query by ID |
| `search_query_history` | Search query history by query text |
| `clear_query_history` | Clear all query history |
| `add`, `sub`, `mul`, `div` | Basic arithmetic operations |
| `get_data_analysis_prompt` | Get a pre-built data analysis prompt |

## Requirements

- Python 3.12+
- DuckDB

## Installation

```bash
# From the repository root
uv sync --package data-analysis
```

## Usage

```bash
# Run with stdio (default)
uv run python -m data_analysis

# Run with SSE transport
uv run python -m data_analysis --transport sse --port 8002
```

See [server guide](../../docs/server-guide.md) for common CLI options.

## Example

Query a CSV file:

```sql
SELECT * FROM 'data.csv' LIMIT 10
```

## Query History

All queries are automatically logged to `~/.mcp-servers/workspace/data_analysis_history.db` with:
- Query text and timestamp
- Execution time and row count
- Full query results (cached)
- Error messages for failed queries

Use the `get_workspace_path()` tool to get the workspace directory path.

**Security Note**: Query history logs all SQL queries with their full results. Avoid querying sensitive data.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_ANALYSIS_MAX_RESULT_SIZE` | 1MB | Maximum size for cached results |
| `DATA_ANALYSIS_MAX_HISTORY_SIZE` | 100 | Maximum queries to keep in history |
| `DATA_ANALYSIS_CLEANUP_FREQUENCY` | 10 | Run cleanup every N queries |

## Testing

```bash
cd src/data-analysis
uv run pytest -v
```
