import pytest

from browser import tools


@pytest.fixture(autouse=True)
def reset_browser_state():
    """Reset global browser state before each test."""
    # Reset global state before each test
    tools._browser = None
    tools._page = None
    tools._playwright = None
    yield
    # Cleanup after test (in case browser was opened)
    tools._browser = None
    tools._page = None
    tools._playwright = None
