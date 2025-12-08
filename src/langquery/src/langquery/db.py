"""Database management for query history."""

from pathlib import Path
from threading import Lock
from typing import Optional

import duckdb

# Configuration constants
MAX_RESULT_SIZE = 1024 * 1024  # Maximum size for cached results (1MB)
MAX_HISTORY_SIZE = 100  # Maximum number of queries to keep in history
CLEANUP_FREQUENCY = 10  # Run cleanup every N queries


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
            limit: Maximum number of results (1-1000)

        Returns:
            Matching queries as markdown table
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
                WHERE query ILIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                [f"%{search_term}%", limit],
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
            count_result = conn.execute("SELECT COUNT(*) FROM query_history").fetchone()
            count = count_result[0] if count_result else 0

            conn.execute("DELETE FROM query_history")

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
