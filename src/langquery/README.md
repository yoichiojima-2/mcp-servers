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
