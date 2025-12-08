"""Database management for query history."""

import os
import time
from pathlib import Path
from typing import Optional

import duckdb


class HistoryDB:
    """Manages query history in a persistent DuckDB database."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the history database.

        Args:
            db_path: Path to the database file. Defaults to workspace/langquery_history.db
        """
        if db_path is None:
            workspace = Path("workspace")
            workspace.mkdir(exist_ok=True)
            db_path = str(workspace / "langquery_history.db")

        self.db_path = db_path
        self._init_schema()

    def _init_schema(self):
        """Initialize the database schema."""
        with duckdb.connect(self.db_path) as conn:
            conn.execute("""
                CREATE SEQUENCE IF NOT EXISTS query_history_id_seq START 1
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id INTEGER PRIMARY KEY DEFAULT nextval('query_history_id_seq'),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    query TEXT NOT NULL,
                    result TEXT,
                    execution_time_ms DOUBLE,
                    row_count INTEGER,
                    error TEXT,
                    success BOOLEAN
                )
            """)

    def log_query(
        self,
        query: str,
        result: Optional[str] = None,
        execution_time_ms: Optional[float] = None,
        row_count: Optional[int] = None,
        error: Optional[str] = None,
        success: bool = True,
    ):
        """Log a query to the history.

        Args:
            query: The SQL query executed
            result: Query result as text
            execution_time_ms: Execution time in milliseconds
            row_count: Number of rows returned
            error: Error message if query failed
            success: Whether the query succeeded
        """
        with duckdb.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO query_history (query, result, execution_time_ms, row_count, error, success)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                [query, result, execution_time_ms, row_count, error, success],
            )

            # Keep only the last 100 queries
            conn.execute("""
                DELETE FROM query_history
                WHERE id NOT IN (
                    SELECT id FROM query_history
                    ORDER BY timestamp DESC
                    LIMIT 100
                )
            """)

    def get_history(self, limit: int = 20) -> str:
        """Get recent query history.

        Args:
            limit: Maximum number of queries to return

        Returns:
            Query history as markdown table
        """
        with duckdb.connect(self.db_path) as conn:
            result = conn.execute(
                """
                SELECT
                    id,
                    timestamp,
                    query,
                    execution_time_ms,
                    row_count,
                    success
                FROM query_history
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                [limit],
            ).fetchdf()

            if result.empty:
                return "No query history found."

            return result.to_markdown(index=False)

    def get_query_result(self, query_id: int) -> str:
        """Get the cached result of a previous query.

        Args:
            query_id: The ID of the query from history

        Returns:
            The cached result or error message
        """
        with duckdb.connect(self.db_path) as conn:
            result = conn.execute(
                """
                SELECT query, result, error, success
                FROM query_history
                WHERE id = ?
            """,
                [query_id],
            ).fetchone()

            if result is None:
                return f"Query ID {query_id} not found in history."

            query, cached_result, error, success = result

            if not success:
                return f"Query failed with error:\n{error}\n\nQuery was:\n{query}"

            if cached_result is None:
                return f"No cached result for query ID {query_id}."

            return cached_result

    def search_history(self, search_term: str, limit: int = 10) -> str:
        """Search query history by query text.

        Args:
            search_term: Term to search for in queries
            limit: Maximum number of results

        Returns:
            Matching queries as markdown table
        """
        with duckdb.connect(self.db_path) as conn:
            result = conn.execute(
                """
                SELECT
                    id,
                    timestamp,
                    query,
                    execution_time_ms,
                    row_count,
                    success
                FROM query_history
                WHERE query ILIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                [f"%{search_term}%", limit],
            ).fetchdf()

            if result.empty:
                return f"No queries found matching '{search_term}'."

            return result.to_markdown(index=False)


# Global instance
_history_db: Optional[HistoryDB] = None


def get_history_db() -> HistoryDB:
    """Get or create the global history database instance."""
    global _history_db
    if _history_db is None:
        _history_db = HistoryDB()
    return _history_db
