"""Test configuration and fixtures."""

import pytest_asyncio


@pytest_asyncio.fixture(scope="function")
async def mock_context():
    """Create a mock FastMCP context for testing."""
    from dify.tools import DifyClient

    client = DifyClient(
        api_key="test-api-key",
        base_url="https://test.dify.ai/v1",
        console_api_key="test-console-key",
        console_base_url="https://test.dify.ai",
    )

    class MockRequestContext:
        def __init__(self):
            self.lifespan_state = {"client": client}

    class MockContext:
        def __init__(self):
            self.request_context = MockRequestContext()

    ctx = MockContext()
    yield ctx
    # Clean up the HTTP client
    await client.close()
