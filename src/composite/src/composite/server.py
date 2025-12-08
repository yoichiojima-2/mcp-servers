"""MCP Composite Server - Aggregates multiple backend MCP servers into a single endpoint."""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any

import httpx
import uvicorn
import yaml
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import (
    CallToolResult,
    GetPromptResult,
    ListPromptsResult,
    ListToolsResult,
    TextContent,
    Tool,
)
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_config() -> dict[str, Any]:
    """Load composite configuration from YAML file."""
    config_path = os.getenv("COMPOSITE_CONFIG_PATH")

    if not config_path:
        # Try default locations
        candidates = [
            Path.cwd() / "composite-config.yaml",
            Path(__file__).parent.parent.parent / "composite-config.yaml",
        ]
        for candidate in candidates:
            if candidate.exists():
                config_path = str(candidate)
                break

    if not config_path or not Path(config_path).exists():
        raise FileNotFoundError(
            "No configuration file found. Set COMPOSITE_CONFIG_PATH or create composite-config.yaml"
        )

    with open(config_path) as f:
        return yaml.safe_load(f)


class MCPComposite:
    """Composite server that aggregates multiple MCP backend servers."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.backends = {
            backend["name"]: backend
            for backend in config["backends"]
            if backend.get("enabled", True)
        }
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.server = Server("mcp-composite")

        # Register handlers
        self.server.list_tools()(self.list_tools)
        self.server.call_tool()(self.call_tool)
        self.server.list_prompts()(self.list_prompts)
        self.server.get_prompt()(self.get_prompt)

    async def _fetch_from_backend(
        self, backend_name: str, method: str, params: dict[str, Any] | None = None
    ) -> Any:
        """Make MCP request to a backend server."""
        backend = self.backends[backend_name]
        url = backend["url"]

        # Construct MCP JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1,
        }

        try:
            response = await self.http_client.post(url, json=request)
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                raise Exception(f"Backend error: {result['error']}")

            return result.get("result", {})
        except Exception as e:
            raise Exception(f"Failed to fetch from {backend_name}: {e}")

    async def list_tools(self) -> ListToolsResult:
        """Aggregate tools from all backends."""
        all_tools = []

        for backend_name, backend in self.backends.items():
            try:
                result = await self._fetch_from_backend(backend_name, "tools/list")
                prefix = backend.get("prefix", backend_name)

                for tool in result.get("tools", []):
                    # Prefix the tool name
                    tool["name"] = f"{prefix}_{tool['name']}"
                    all_tools.append(Tool(**tool))
            except Exception as e:
                logger.warning(f"Failed to fetch tools from {backend_name}: {e}")

        return ListToolsResult(tools=all_tools)

    async def call_tool(
        self, name: str, arguments: dict[str, Any]
    ) -> CallToolResult:
        """Route tool call to appropriate backend."""
        # Find which backend owns this tool
        for backend_name, backend in self.backends.items():
            prefix = backend.get("prefix", backend_name)
            if name.startswith(f"{prefix}_"):
                # Remove prefix and call backend
                original_name = name[len(prefix) + 1 :]

                try:
                    result = await self._fetch_from_backend(
                        backend_name,
                        "tools/call",
                        {"name": original_name, "arguments": arguments},
                    )

                    # Convert result to CallToolResult format
                    content = result.get("content", [])
                    if isinstance(content, list):
                        content = [
                            TextContent(type="text", text=str(c)) for c in content
                        ]
                    else:
                        content = [TextContent(type="text", text=str(content))]

                    return CallToolResult(content=content)
                except Exception as e:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Error: {e}")],
                        isError=True,
                    )

        return CallToolResult(
            content=[TextContent(type="text", text=f"Tool not found: {name}")],
            isError=True,
        )

    async def list_prompts(self) -> ListPromptsResult:
        """Aggregate prompts from all backends."""
        all_prompts = []

        for backend_name, backend in self.backends.items():
            try:
                result = await self._fetch_from_backend(backend_name, "prompts/list")
                prefix = backend.get("prefix", backend_name)

                for prompt in result.get("prompts", []):
                    # Prefix the prompt name
                    prompt["name"] = f"{prefix}_{prompt['name']}"
                    all_prompts.append(prompt)
            except Exception as e:
                logger.warning(f"Failed to fetch prompts from {backend_name}: {e}")

        return ListPromptsResult(prompts=all_prompts)

    async def get_prompt(
        self, name: str, arguments: dict[str, Any] | None = None
    ) -> GetPromptResult:
        """Route prompt request to appropriate backend."""
        for backend_name, backend in self.backends.items():
            prefix = backend.get("prefix", backend_name)
            if name.startswith(f"{prefix}_"):
                original_name = name[len(prefix) + 1 :]

                try:
                    result = await self._fetch_from_backend(
                        backend_name,
                        "prompts/get",
                        {"name": original_name, "arguments": arguments or {}},
                    )
                    return GetPromptResult(**result)
                except Exception as e:
                    raise Exception(f"Failed to get prompt: {e}")

        raise Exception(f"Prompt not found: {name}")

    async def cleanup(self):
        """Cleanup resources."""
        await self.http_client.aclose()


async def _run_server():
    """Run the MCP composite server."""
    config = load_config()
    composite = MCPComposite(config)

    # Get transport configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    logger.info("Starting MCP Composite Server")
    logger.info(f"Backends: {', '.join(composite.backends.keys())}")
    logger.info(f"Listening on {host}:{port}/sse")

    try:
        # Create SSE transport
        sse = SseServerTransport("/messages")

        # Create CORS middleware
        cors_middleware = Middleware(
            CORSMiddleware,
            allow_origins=[os.getenv("ALLOW_ORIGIN", "*")],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Create Starlette app
        app = Starlette(
            routes=[Mount("/", app=sse.get_asgi_app(composite.server))],
            middleware=[cors_middleware],
        )

        # Run with uvicorn
        await uvicorn.Server(
            uvicorn.Config(app, host=host, port=port, log_level="info")
        ).serve()
    finally:
        await composite.cleanup()


def serve():
    """Start MCP server."""
    asyncio.run(_run_server())
