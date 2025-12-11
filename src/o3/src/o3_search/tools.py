import os
from functools import lru_cache

from fastmcp.exceptions import ToolError
from openai import OpenAI

from . import mcp

DEFAULT_MODEL = "o3"


@lru_cache(maxsize=1)
def get_client() -> OpenAI:
    """Get cached OpenAI client instance."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ToolError("OPENAI_API_KEY environment variable is not set")
    return OpenAI(api_key=api_key.strip())


@mcp.tool(name="o3")
def o3_search(query: str) -> str:
    """
    An AI agent with advanced web search capabilities.
    Useful for finding the latest information, troubleshooting errors, and discussing ideas or design challenges.
    Supports natural language queries.

    Args:
        query: Ask questions, search for information, or consult about complex problems in English.

    Returns:
        Response from o3 with web search results and analysis.
    """
    client = get_client()
    model = os.getenv("O3_MODEL", DEFAULT_MODEL)

    try:
        response = client.responses.create(
            model=model,
            tools=[{"type": "web_search_preview"}],
            input=query,
        )
        return response.output_text
    except Exception as e:
        raise ToolError(f"OpenAI API error: {e}") from e
