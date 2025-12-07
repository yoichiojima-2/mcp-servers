# langquery

An MCP server that allows clients to manipulate table data using natural language. Built with [FastMCP](https://github.com/jlowin/fastmcp) and [DuckDB](https://duckdb.org/).

## Features

- **SQL Query**: Execute DuckDB SQL queries on any data files (CSV, Parquet, JSON, etc.)
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
| `query` | Execute DuckDB SQL and return results as markdown |
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
