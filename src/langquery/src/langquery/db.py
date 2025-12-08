"""Database management for query history."""

import os
import sys
from pathlib import Path
from threading import Lock
from typing import Optional

import duckdb


def _get_env_int(name: str, default: int, min_value: int = 1) -> int:
    """Get and validate integer environment variable.

    Args:
        name: Environment variable name
        default: Default value if not set or invalid
        min_value: Minimum allowed value

    Returns:
        Validated integer value
    """
    try:
        value = int(os.getenv(name, default))
        if value < min_value:
            raise ValueError(f"Must be >= {min_value}")
        return value
    except (ValueError, TypeError) as e:
        print(
            f"Warning: Invalid {name}='{os.getenv(name)}' ({e}), using default {default}",
            file=sys.stderr,
        )
        return default


# Configuration constants (configurable via environment variables)
MAX_RESULT_SIZE = _get_env_int("LANGQUERY_MAX_RESULT_SIZE", 1024 * 1024)  # Default: 1MB
MAX_HISTORY_SIZE = _get_env_int("LANGQUERY_MAX_HISTORY_SIZE", 100)  # Default: 100 queries
CLEANUP_FREQUENCY = _get_env_int("LANGQUERY_CLEANUP_FREQUENCY", 10)  # Default: every 10 queries


class HistoryDB:
    """Manages query history in a persistent DuckDB database."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the history database.

        Args:
            db_path: Path to the database file. Defaults to workspace/langquery_history.db

        Raises:
            OSError: If workspace directory cannot be created
        """
        if db_path is None:
            workspace = Path("workspace")
            try:
                workspace.mkdir(exist_ok=True)
            except OSError as e:
                raise OSError(
                    f"Failed to create workspace directory at {workspace.absolute()}: {e}"
                ) from e
            db_path = str(workspace / "langquery_history.db")

        self.db_path = db_path
        self._query_count = 0  # Track queries for cleanup optimization
        self._counter_lock = Lock()  # Lock for thread-safe counter increment
        self._cleanup_in_progress = False  # Flag to prevent concurrent cleanup
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
            # Add index on timestamp for better query performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_query_history_timestamp
                ON query_history(timestamp)
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
            result: Query result as text (truncated if > 1MB)
            execution_time_ms: Execution time in milliseconds
            row_count: Number of rows returned
            error: Error message if query failed
            success: Whether the query succeeded
        """
        # Truncate large results to prevent memory issues
        if result and len(result) > MAX_RESULT_SIZE:
            result = result[:MAX_RESULT_SIZE] + "\n... (truncated)"

        # Insert query in its own transaction
        with duckdb.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO query_history (query, result, execution_time_ms, row_count, error, success)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                [query, result, execution_time_ms, row_count, error, success],
            )

        # Thread-safe counter increment and cleanup check
        should_cleanup = False
        with self._counter_lock:
            self._query_count += 1
            if self._query_count % CLEANUP_FREQUENCY == 0 and not self._cleanup_in_progress:
                self._cleanup_in_progress = True
                should_cleanup = True

        # Run cleanup in separate transaction to avoid rolling back the insert
        if should_cleanup:
            try:
                with duckdb.connect(self.db_path) as conn:
                    # Double-check: verify cleanup is still needed
                    # This prevents race where multiple threads think they should cleanup
                    count = conn.execute("SELECT COUNT(*) FROM query_history").fetchone()[0]
                    if count > MAX_HISTORY_SIZE:
                        # Keep only the last MAX_HISTORY_SIZE queries
                        # Use ID-based deletion which leverages primary key index
                        conn.execute(
                            """
                            DELETE FROM query_history
                            WHERE id < (
                                SELECT MIN(id) FROM (
                                    SELECT id FROM query_history
                                    ORDER BY id DESC
                                    LIMIT ?
                                )
                            )
                        """,
                            [MAX_HISTORY_SIZE],
                        )
            finally:
                # Always reset cleanup flag
                with self._counter_lock:
                    self._cleanup_in_progress = False

    def get_history(self, limit: int = 20) -> str:
        """Get recent query history.

        Args:
            limit: Maximum number of queries to return (1-1000)

        Returns:
            Query history as markdown table
        """
        # Validate limit parameter
        if limit < 1 or limit > 1000:
            return "Error: limit must be between 1 and 1000"

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
                ORDER BY id DESC
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
            search_term: Term to search for in queries (% and _ are treated as literals)
            limit: Maximum number of results (1-1000)

        Returns:
            Matching queries as markdown table
        """
        # Validate limit parameter
        if limit < 1 or limit > 1000:
            return "Error: limit must be between 1 and 1000"

        # Escape SQL LIKE wildcards so they're treated as literal characters
        # Note: Parameterized queries prevent SQL injection; this is only for LIKE pattern matching
        escaped_term = search_term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

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
                WHERE query ILIKE ? ESCAPE '\\'
                ORDER BY id DESC
                LIMIT ?
            """,
                [f"%{escaped_term}%", limit],
            ).fetchdf()

            if result.empty:
                return f"No queries found matching '{search_term}'."

            return result.to_markdown(index=False)

    def clear_history(self) -> str:
        """Clear all query history.

        Returns:
            Success message with count of deleted queries
        """
        with duckdb.connect(self.db_path) as conn:
            # Use DELETE...RETURNING to get count in single query
            # RETURNING returns one row per deleted row, so we count the results
            result = conn.execute("DELETE FROM query_history RETURNING id").fetchall()
            count = len(result)

            # Thread-safe counter reset
            with self._counter_lock:
                self._query_count = 0

            return f"Cleared {count} queries from history."


# Global instance with thread-safe initialization
_history_db: Optional[HistoryDB] = None
_lock = Lock()


def get_history_db() -> HistoryDB:
    """Get or create the global history database instance.

    Thread-safe singleton pattern using double-checked locking.

    Returns:
        HistoryDB: The global history database instance
    """
    global _history_db
    if _history_db is None:
        with _lock:
            if _history_db is None:
                _history_db = HistoryDB()
    return _history_db
