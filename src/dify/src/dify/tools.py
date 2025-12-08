"""Dify MCP tools for managing agents, workflows, and knowledge bases."""

import os
from typing import Any, Literal

import httpx
import yaml
from fastmcp import Context
from fastmcp.exceptions import ToolError


class DifyClient:
    """Client for interacting with Dify API."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        console_api_key: str | None = None,
        console_base_url: str | None = None,
    ):
        """Initialize Dify client.

        Args:
            api_key: Service API key for app interactions (app-level operations)
            base_url: Base URL for service API (default: https://api.dify.ai/v1)
            console_api_key: Console API key for workspace operations (admin operations)
            console_base_url: Base URL for console API (default: https://api.dify.ai)
        """
        self.api_key = (api_key or os.getenv("DIFY_API_KEY") or "").strip() or None
        self.base_url = (
            base_url or os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1")
        ).rstrip("/")

        # Console API for admin operations (import/export DSL, manage apps)
        self.console_api_key = (
            console_api_key or os.getenv("DIFY_CONSOLE_API_KEY") or ""
        ).strip() or None
        self.console_base_url = (
            console_base_url
            or os.getenv("DIFY_CONSOLE_BASE_URL", "https://api.dify.ai")
        ).rstrip("/")

        # Reusable HTTP client for better performance
        self._http_client = httpx.AsyncClient(timeout=60.0)

    async def close(self):
        """Close the HTTP client."""
        await self._http_client.aclose()

    def _get_headers(self, use_console: bool = False) -> dict[str, str]:
        """Get headers for API requests.

        Args:
            use_console: Whether to use console API credentials

        Returns:
            Headers dictionary with authorization
        """
        api_key = self.console_api_key if use_console else self.api_key
        if not api_key:
            raise ToolError(
                f"{'DIFY_CONSOLE_API_KEY' if use_console else 'DIFY_API_KEY'} not configured"
            )

        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        use_console: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make an HTTP request to Dify API.

        Args:
            method: HTTP method
            endpoint: API endpoint
            use_console: Whether to use console API
            **kwargs: Additional arguments for httpx

        Returns:
            Response JSON data
        """
        base_url = self.console_base_url if use_console else self.base_url
        url = f"{base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers(use_console)

        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        try:
            response = await self._http_client.request(
                method, url, headers=headers, **kwargs
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            raise ToolError(
                f"Dify API error ({e.response.status_code}): {error_detail}"
            ) from e
        except httpx.HTTPError as e:
            raise ToolError(f"Request failed: {str(e)}") from e


async def chat_message(
    ctx: Context,
    query: str,
    user: str = "default-user",
    conversation_id: str | None = None,
    inputs: dict[str, Any] | None = None,
    response_mode: Literal["blocking", "streaming"] = "blocking",
    files: list[dict[str, str]] | None = None,
) -> str:
    """Send a chat message to a Dify chatbot application.

    Use this for conversational interactions with Dify agents. Supports conversation
    history, file uploads, and custom variables.

    Args:
        ctx: FastMCP context
        query: User's message/question
        user: Unique user identifier (for tracking conversations)
        conversation_id: Optional conversation ID to continue existing chat
        inputs: Dictionary of input variables for the application
        response_mode: "blocking" (wait for full response) or "streaming"
        files: List of file objects with "type" and "transfer_method" keys

    Returns:
        Assistant's response text
    """
    if not query.strip():
        raise ToolError("Query cannot be empty")

    client = ctx.request_context.lifespan_state["client"]

    payload: dict[str, Any] = {
        "query": query,
        "user": user,
        "response_mode": response_mode,
    }

    if conversation_id:
        payload["conversation_id"] = conversation_id
    if inputs:
        payload["inputs"] = inputs
    if files:
        payload["files"] = files

    result = await client._request("POST", "chat-messages", json=payload)

    if response_mode == "blocking":
        return result.get("answer", "")
    else:
        return f"Streaming response initiated. Task ID: {result.get('task_id')}"


async def run_workflow(
    ctx: Context,
    inputs: dict[str, Any],
    user: str = "default-user",
    response_mode: Literal["blocking", "streaming"] = "blocking",
    files: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Execute a Dify workflow application.

    Workflows are designed for automation tasks without conversation context.
    Great for translation, summarization, data processing, etc.

    Args:
        ctx: FastMCP context
        inputs: Input variables defined in the workflow
        user: Unique user identifier
        response_mode: "blocking" or "streaming"
        files: List of file objects for processing

    Returns:
        Workflow execution results including outputs and metadata
    """
    client = ctx.request_context.lifespan_state["client"]

    payload: dict[str, Any] = {
        "inputs": inputs,
        "user": user,
        "response_mode": response_mode,
    }

    if files:
        payload["files"] = files

    result = await client._request("POST", "workflows/run", json=payload)
    return result


async def get_conversation_messages(
    ctx: Context,
    conversation_id: str,
    user: str = "default-user",
    first_id: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Get message history from a conversation.

    Args:
        ctx: FastMCP context
        conversation_id: Conversation identifier
        user: User identifier
        first_id: ID of first message for pagination
        limit: Number of messages to retrieve (default: 20)

    Returns:
        List of message objects with content, role, and metadata
    """
    client = ctx.request_context.lifespan_state["client"]

    params: dict[str, Any] = {
        "user": user,
        "conversation_id": conversation_id,
        "limit": limit,
    }

    if first_id:
        params["first_id"] = first_id

    result = await client._request("GET", "messages", params=params)
    return result.get("data", [])


async def create_dataset(
    ctx: Context,
    name: str,
    description: str | None = None,
    permission: Literal["only_me", "all_team_members"] = "only_me",
    indexing_technique: Literal["high_quality", "economy"] = "high_quality",
    embedding_model: str | None = None,
    embedding_model_provider: str | None = None,
    retrieval_model: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a new knowledge base (dataset) in Dify.

    Knowledge bases store documents that can be retrieved by agents for RAG
    (Retrieval-Augmented Generation).

    Args:
        ctx: FastMCP context
        name: Dataset name
        description: Optional description
        permission: Access control ("only_me" or "all_team_members")
        indexing_technique: "high_quality" (vector) or "economy" (keyword)
        embedding_model: Model name for embeddings
        embedding_model_provider: Provider name (e.g., "openai")
        retrieval_model: Retrieval configuration dict

    Returns:
        Dataset object with id, name, and configuration
    """
    client = ctx.request_context.lifespan_state["client"]

    payload: dict[str, Any] = {
        "name": name,
        "permission": permission,
        "indexing_technique": indexing_technique,
    }

    if description:
        payload["description"] = description
    if embedding_model:
        payload["embedding_model"] = embedding_model
    if embedding_model_provider:
        payload["embedding_model_provider"] = embedding_model_provider
    if retrieval_model:
        payload["retrieval_model"] = retrieval_model

    result = await client._request("POST", "datasets", json=payload, use_console=True)
    return result


async def upload_document_by_text(
    ctx: Context,
    dataset_id: str,
    name: str,
    text: str,
    indexing_technique: Literal["high_quality", "economy"] = "high_quality",
    process_rule: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Upload a text document to a knowledge base.

    Args:
        ctx: FastMCP context
        dataset_id: Target dataset ID
        name: Document name
        text: Document content
        indexing_technique: "high_quality" or "economy"
        process_rule: Processing rules (segmentation, etc.)

    Returns:
        Document object with id, status, and indexing info
    """
    if not text.strip():
        raise ToolError("Document text cannot be empty")
    if not name.strip():
        raise ToolError("Document name cannot be empty")

    client = ctx.request_context.lifespan_state["client"]

    payload: dict[str, Any] = {
        "name": name,
        "text": text,
        "indexing_technique": indexing_technique,
        "process_rule": process_rule or {"mode": "automatic"},
    }

    result = await client._request(
        "POST",
        f"datasets/{dataset_id}/document/create-by-text",
        json=payload,
        use_console=True,
    )
    return result


async def list_documents(
    ctx: Context,
    dataset_id: str,
    page: int = 1,
    limit: int = 20,
    keyword: str | None = None,
) -> dict[str, Any]:
    """List documents in a knowledge base.

    Args:
        ctx: FastMCP context
        dataset_id: Dataset ID
        page: Page number (1-indexed)
        limit: Documents per page
        keyword: Optional search keyword

    Returns:
        Paginated list of documents with metadata
    """
    client = ctx.request_context.lifespan_state["client"]

    params: dict[str, Any] = {
        "page": page,
        "limit": limit,
    }

    if keyword:
        params["keyword"] = keyword

    result = await client._request(
        "GET",
        f"datasets/{dataset_id}/documents",
        params=params,
        use_console=True,
    )
    return result


async def import_dsl_workflow(
    ctx: Context,
    dsl_content: str | None = None,
    dsl_url: str | None = None,
    name: str | None = None,
    description: str | None = None,
    icon: str | None = None,
    icon_background: str | None = None,
) -> dict[str, Any]:
    """Import a Dify workflow from DSL (YAML).

    This creates a new application by importing a DSL file. You can provide
    either the YAML content directly or a URL to fetch it from.

    Note: Requires DIFY_CONSOLE_API_KEY to be configured.

    Args:
        ctx: FastMCP context
        dsl_content: YAML content of the DSL file
        dsl_url: URL to fetch DSL from
        name: Override app name
        description: Override description
        icon: Icon emoji
        icon_background: Icon background color

    Returns:
        Import result with app_id and status
    """
    if not dsl_content and not dsl_url:
        raise ToolError("Either dsl_content or dsl_url must be provided")

    client = ctx.request_context.lifespan_state["client"]

    payload: dict[str, Any] = {}

    if dsl_content:
        # Validate YAML
        try:
            yaml.safe_load(dsl_content)
        except yaml.YAMLError as e:
            raise ToolError(f"Invalid YAML content: {e}") from e

        payload["mode"] = "yaml-content"
        payload["yaml_content"] = dsl_content
    elif dsl_url:
        payload["mode"] = "url"
        payload["url"] = dsl_url

    if name:
        payload["name"] = name
    if description:
        payload["description"] = description
    if icon:
        payload["icon"] = icon
        payload["icon_type"] = "emoji"
    if icon_background:
        payload["icon_background"] = icon_background

    result = await client._request(
        "POST",
        "console/api/apps/imports",
        json=payload,
        use_console=True,
    )
    return result


async def export_dsl_workflow(
    ctx: Context,
    app_id: str,
    include_secret: bool = False,
) -> str:
    """Export a Dify application as DSL (YAML).

    Downloads the complete workflow configuration including nodes, edges,
    variables, and model settings.

    Note: Requires DIFY_CONSOLE_API_KEY to be configured.

    Args:
        ctx: FastMCP context
        app_id: Application ID to export
        include_secret: Whether to include API keys and secrets

    Returns:
        YAML content of the application DSL
    """
    client = ctx.request_context.lifespan_state["client"]

    params = {"include_secret": "true" if include_secret else "false"}

    # Note: This endpoint returns YAML directly, not JSON
    base_url = client.console_base_url
    url = f"{base_url}/console/api/apps/{app_id}/export"
    headers = client._get_headers(use_console=True)

    try:
        response = await client._http_client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        raise ToolError(
            f"Export failed ({e.response.status_code}): {e.response.text}"
        ) from e
    except httpx.HTTPError as e:
        raise ToolError(f"Export request failed: {str(e)}") from e


async def generate_workflow_dsl(
    ctx: Context,
    description: str,
    app_type: Literal["chatbot", "agent", "workflow", "chatflow"] = "workflow",
    enable_knowledge_base: bool = False,
    tools: list[str] | None = None,
) -> str:
    """Generate a Dify workflow DSL from a natural language description.

    This is a helper tool that creates a basic DSL template based on your
    requirements. You can then customize it further before importing.

    Args:
        ctx: FastMCP context
        description: Description of the workflow/agent you want to create
        app_type: Type of application (chatbot, agent, workflow, chatflow)
        enable_knowledge_base: Whether to include knowledge retrieval
        tools: List of tools to enable (e.g., ["google_search", "wikipedia"])

    Returns:
        Generated YAML DSL content
    """
    # Basic template structure
    template: dict[str, Any] = {
        "version": "0.1.5",
        "kind": "app",
        "app": {
            "name": description[:50],
            "description": description,
            "mode": app_type if app_type != "chatbot" else "advanced-chat",
            "icon": "🤖",
            "icon_background": "#FFEAD5",
        },
    }

    if app_type in ["workflow", "chatflow"]:
        # Workflow structure
        template["app"]["model_config"] = {
            "model": {
                "provider": "openai",
                "name": "gpt-4",
                "mode": "chat",
                "completion_params": {},
            }
        }

        template["app"]["workflow"] = {
            "graph": {
                "nodes": [
                    {
                        "id": "start",
                        "type": "start",
                        "data": {
                            "title": "Start",
                            "variables": [
                                {
                                    "variable": "input",
                                    "type": "text-input",
                                    "label": "Input",
                                    "required": True,
                                }
                            ],
                        },
                    },
                    {
                        "id": "llm",
                        "type": "llm",
                        "data": {
                            "title": "LLM",
                            "model": {"provider": "openai", "name": "gpt-4"},
                            "prompt_template": [
                                {"role": "system", "text": description},
                                {"role": "user", "text": "{{#start.input#}}"},
                            ],
                        },
                    },
                    {
                        "id": "end",
                        "type": "end",
                        "data": {
                            "title": "End",
                            "outputs": [
                                {
                                    "variable": "result",
                                    "value_selector": ["llm", "text"],
                                }
                            ],
                        },
                    },
                ],
                "edges": [
                    {"source": "start", "target": "llm"},
                    {"source": "llm", "target": "end"},
                ],
            }
        }

        if enable_knowledge_base:
            # Add knowledge retrieval node
            knowledge_node = {
                "id": "knowledge",
                "type": "knowledge-retrieval",
                "data": {
                    "title": "Knowledge Retrieval",
                    "query_variable_selector": ["start", "input"],
                    "retrieval_mode": "single",
                },
            }
            template["app"]["workflow"]["graph"]["nodes"].insert(1, knowledge_node)
            template["app"]["workflow"]["graph"]["edges"] = [
                {"source": "start", "target": "knowledge"},
                {"source": "knowledge", "target": "llm"},
                {"source": "llm", "target": "end"},
            ]

    return yaml.dump(template, sort_keys=False, allow_unicode=True)
