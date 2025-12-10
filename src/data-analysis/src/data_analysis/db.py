"""Database management for query history."""

import os
import re
import sys
from pathlib import Path
from threading import Lock
from typing import Optional

import duckdb


def _get_env_int(name: str, default: int, min_value: int = 1, max_value: Optional[int] = None) -> int:
    """Get and validate integer environment variable.

    Args:
        name: Environment variable name
        default: Default value if not set or invalid
        min_value: Minimum allowed value
        max_value: Maximum allowed value (optional)

    Returns:
        Validated integer value
    """
    try:
        value = int(os.getenv(name, default))
        if value < min_value:
            raise ValueError(f"Must be >= {min_value}")
        if max_value is not None and value > max_value:
            raise ValueError(f"Must be <= {max_value}")
        return value
    except ValueError as e:
        print(
            f"Warning: Invalid {name}='{os.getenv(name)}' ({e}), using default {default}",
            file=sys.stderr,
        )
        return default


# Configuration constants (configurable via environment variables)
MAX_RESULT_SIZE = _get_env_int(
    "DATA_ANALYSIS_MAX_RESULT_SIZE", 1024 * 1024, min_value=1024, max_value=10 * 1024 * 1024
)  # Default: 1MB, min 1KB, max 10MB
MAX_HISTORY_SIZE = _get_env_int(
    "DATA_ANALYSIS_MAX_HISTORY_SIZE", 100, min_value=1, max_value=10000
)  # Default: 100 queries, min 1, max 10k
CLEANUP_FREQUENCY = _get_env_int(
    "DATA_ANALYSIS_CLEANUP_FREQUENCY", 10, min_value=1, max_value=1000
)  # Default: every 10 queries, min 1 (prevents division by zero), max 1000


class HistoryDB:
    """Manages query history in a persistent DuckDB database."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the history database.

        Args:
            db_path: Path to the database file. Defaults to $DATA_ANALYSIS_WORKSPACE/data_analysis_history.db
                     or workspace/data_analysis_history.db if DATA_ANALYSIS_WORKSPACE is not set

        Raises:
            OSError: If workspace directory cannot be created
        """
        if db_path is None:
            workspace_dir = os.getenv("DATA_ANALYSIS_WORKSPACE", "workspace")
            workspace = Path(workspace_dir)
            try:
                # Create workspace directory with secure permissions (owner-only access)
                workspace.mkdir(parents=True, exist_ok=True, mode=0o700)
            except OSError as e:
                raise OSError(f"Failed to create workspace directory at {workspace.absolute()}: {e}") from e
            db_path = str(workspace / "data_analysis_history.db")

        self.db_path = db_path
        self._counter_lock = Lock()  # Lock for thread-safe counter increment
        self._cleanup_in_progress = False  # Flag to prevent concurrent cleanup
        self._init_schema()

        # Set secure permissions on database file (owner-only read/write)
        # This is critical since the DB contains query results with potentially sensitive data
        try:
            os.chmod(self.db_path, 0o600)
        except OSError:
            # If chmod fails (e.g., on some filesystems), log but don't fail
            # The directory-level permissions provide some protection
            pass

        # Initialize counter from database to prevent drift after restart/clear
        with duckdb.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM query_history").fetchone()[0]
            self._query_count = count

    def _init_schema(self):
        """Initialize the database schema."""
        with duckdb.connect(self.db_path) as conn:
            conn.execute("""
                CREATE SEQUENCE IF NOT EXISTS query_history_id_seq START 1
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id INTEGER PRIMARY KEY DEFAULT nextval('query_history_id_seq'),
                    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    query TEXT NOT NULL,
                    result TEXT,
                    execution_time_ms DOUBLE,
                    row_count INTEGER,
                    error TEXT,
                    success BOOLEAN
                )
            """)
            # Create indexes for better query performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_query_history_timestamp ON query_history(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_query_history_query ON query_history(query)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_query_history_success ON query_history(success)
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
            # Try to find the last complete line/row before MAX_RESULT_SIZE
            # to avoid breaking markdown table formatting mid-row
            truncated = result[:MAX_RESULT_SIZE]
            last_newline = truncated.rfind("\n")
            if last_newline > 0:
                # Truncate at last complete line
                truncated = result[:last_newline]
            result = truncated + "\n\n... (result truncated due to size limit)"

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
        with self._counter_lock:
            self._query_count += 1
            if self._query_count % CLEANUP_FREQUENCY == 0 and not self._cleanup_in_progress:
                self._cleanup_in_progress = True
                should_cleanup = True
            else:
                should_cleanup = False

        # Run cleanup in separate transaction to avoid rolling back the insert
        if should_cleanup:
            try:
                with duckdb.connect(self.db_path) as conn:
                    # Keep only the last MAX_HISTORY_SIZE queries
                    # Use ID-based deletion which leverages primary key index
                    # This operation is idempotent - safe if multiple threads execute it
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
        # Validate query_id parameter
        if query_id < 1:
            return f"Error: query_id must be a positive integer (got {query_id})"

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
                # Sanitize error message to avoid leaking sensitive information
                # Remove file paths, internal database details, etc.
                sanitized_error = self._sanitize_error(error) if error else "Unknown error"
                return f"Query failed with error:\n{sanitized_error}\n\nQuery was:\n{query}"

            if cached_result is None:
                return f"No cached result for query ID {query_id}."

            return cached_result

    def _sanitize_error(self, error: str) -> str:
        """Sanitize error messages to prevent information leakage.

        Args:
            error: Original error message

        Returns:
            Sanitized error message
        """
        # Remove file paths - handle multiple formats:
        # - Unix absolute paths: /path/to/file (must start with / followed by letters/numbers)
        # - Windows absolute paths: C:\path\to\file
        # - UNC paths: \\server\share\file
        # - file:// URLs: file:///path/to/file
        # - Relative paths with spaces: ./my dir/file
        error = re.sub(r"file:///[^\s]+", "[path]", error)  # file:// URLs
        error = re.sub(r"\\\\[^\s]+", "[path]", error)  # UNC paths
        error = re.sub(r"/[a-zA-Z0-9_\-\.][^\s]*", "[path]", error)  # Unix paths (requires alphanumeric after /)
        error = re.sub(r"[A-Z]:\\[^\s]+", "[path]", error)  # Windows paths
        error = re.sub(r"\./[^\s]+", "[path]", error)  # Relative paths
        error = re.sub(r"\.\./[^\s]+", "[path]", error)  # Parent directory paths

        # Remove line numbers and column references that might expose internals
        error = re.sub(r"line \d+", "line [redacted]", error, flags=re.IGNORECASE)
        error = re.sub(r"column \d+", "column [redacted]", error, flags=re.IGNORECASE)

        # Keep only the main error message, remove stack traces
        lines = error.split("\n")
        if lines:
            # Return first meaningful line
            return lines[0]

        return error

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
            # Use explicit transaction for atomicity
            conn.execute("BEGIN TRANSACTION")
            try:
                # Get count before deleting for performance
                # More efficient than RETURNING which creates a result set for each deleted row
                count = conn.execute("SELECT COUNT(*) FROM query_history").fetchone()[0]

                # Delete all history
                conn.execute("DELETE FROM query_history")

                # Reset the sequence to start from 1 again
                # This prevents ID gaps and potential sequence exhaustion over time
                # DuckDB doesn't support ALTER SEQUENCE RESTART, so we drop and recreate
                conn.execute("DROP SEQUENCE IF EXISTS query_history_id_seq")
                conn.execute("CREATE SEQUENCE query_history_id_seq START 1")

                conn.execute("COMMIT")
            except Exception:
                conn.execute("ROLLBACK")
                raise

        # Thread-safe counter reset (outside DB transaction)
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
