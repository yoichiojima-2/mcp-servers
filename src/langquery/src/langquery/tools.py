import subprocess
import time

import duckdb

from . import mcp
from .db import get_history_db

# ======================================================
# core
# ======================================================


@mcp.tool()
def shell(command: str) -> str:
    """execute a shell command and return the output"""
    res = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )
    output = res.stdout

    if err := res.stderr:
        output = f"**stdout**: {output}\n\n**stderr**: {err}"

    return output


@mcp.tool()
def query(sql: str) -> str:
    """execute a duckdb sql query and return the result as text."""
    history_db = get_history_db()
    start_time = time.time()

    try:
        db = duckdb.connect(database=":memory:")
        result_df = db.execute(sql).fetchdf()
        execution_time_ms = (time.time() - start_time) * 1000

        result_text = result_df.to_markdown(index=False)
        row_count = len(result_df)

        # Log successful query
        history_db.log_query(
            query=sql,
            result=result_text,
            execution_time_ms=execution_time_ms,
            row_count=row_count,
            success=True,
        )

        return result_text
    except Exception as e:
        execution_time_ms = (time.time() - start_time) * 1000
        error_msg = str(e)

        # Log failed query, but don't mask the original error if logging fails
        try:
            history_db.log_query(
                query=sql,
                execution_time_ms=execution_time_ms,
                error=error_msg,
                success=False,
            )
        except Exception:
            # Logging failed, but we still want to raise the original query error
            pass

        raise


@mcp.tool()
def get_query_history(limit: int = 20) -> str:
    """get recent query history with execution metrics.

    Args:
        limit: maximum number of queries to return (default: 20)

    Returns:
        query history as a markdown table
    """
    history_db = get_history_db()
    return history_db.get_history(limit)


@mcp.tool()
def get_cached_result(query_id: int) -> str:
    """retrieve the cached result from a previous query.

    Args:
        query_id: the ID of the query from history

    Returns:
        the cached query result
    """
    history_db = get_history_db()
    return history_db.get_query_result(query_id)


@mcp.tool()
def search_query_history(search_term: str, limit: int = 10) -> str:
    """search query history by query text.

    Args:
        search_term: term to search for in query text
        limit: maximum number of results (default: 10)

    Returns:
        matching queries as a markdown table
    """
    history_db = get_history_db()
    return history_db.search_history(search_term, limit)


@mcp.tool()
def clear_query_history() -> str:
    """clear all query history.

    WARNING: This will permanently delete all logged queries and cached results.

    Returns:
        success message with count of deleted queries
    """
    history_db = get_history_db()
    return history_db.clear_history()


# ======================================================
# basic math operations
# ======================================================


@mcp.tool()
def add(a: int | float, b: int | float) -> int | float:
    """add numbers"""
    return a + b


@mcp.tool()
def sub(a: int | float, b: int | float) -> int | float:
    """sub numbers"""
    return a - b


@mcp.tool()
def mul(a: int | float, b: int | float) -> int | float:
    """multiply numbers"""
    return a * b


@mcp.tool()
def div(a: int | float, b: int | float) -> float:
    """divide numbers"""
    return a / b
