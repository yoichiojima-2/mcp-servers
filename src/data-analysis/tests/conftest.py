"""Test configuration and fixtures for data-analysis tests."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def reset_history_db():
    """Reset global database between tests for isolation.

    This fixture ensures each test has its own isolated database
    to prevent test interference and flaky tests.
    """
    import data_analysis.db as db_module

    # Store original database instance
    original_db = db_module._history_db

    # Create temporary directory for test database
    with tempfile.TemporaryDirectory() as tmpdir:
        # Reset global database to use temp directory
        with db_module._lock:
            db_module._history_db = db_module.HistoryDB(db_path=str(Path(tmpdir) / "test.db"))

        try:
            yield
        finally:
            # Restore original database before tempdir is deleted
            # This prevents _history_db from pointing to a deleted directory
            with db_module._lock:
                db_module._history_db = original_db
