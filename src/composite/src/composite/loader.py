"""Server loader module for dynamically loading and registering MCP servers."""

import copy
import importlib
import sys
from pathlib import Path
from typing import Any, Dict

from fastmcp import FastMCP

from .config import ServerConfig


class ServerLoader:
    """Dynamically load and register MCP servers."""

    def __init__(self, repo_root: Path):
        """Initialize the server loader.

        Args:
            repo_root: Root directory of the repository containing server modules
        """
        self.repo_root = repo_root
        self.loaded_servers: Dict[str, Any] = {}

    def add_server_to_path(self, module_name: str) -> Path:
        """add server's src directory to python path

        security note: paths are added to sys.path which persists globally.
        ensure module_name comes from trusted configuration only.

        Args:
            module_name: name of the server module

        Returns:
            path to the server's src directory

        Raises:
            FileNotFoundError: if server src directory doesn't exist
            ValueError: if path escapes repository root
        """
        server_src = self.repo_root / module_name / "src"

        # validate path doesn't escape repo_root (security)
        try:
            server_src_resolved = server_src.resolve()
            repo_root_resolved = self.repo_root.resolve()
            if not str(server_src_resolved).startswith(str(repo_root_resolved)):
                raise ValueError(f"invalid module path '{module_name}': path escapes repository root")
        except (OSError, RuntimeError) as e:
            raise ValueError(f"invalid module path '{module_name}': {e}")

        if not server_src.exists():
            raise FileNotFoundError(
                f"server source directory not found: {server_src}\n"
                f"expected structure: {self.repo_root}/{module_name}/src/"
            )

        # add to python path if not already present
        server_src_str = str(server_src)
        if server_src_str not in sys.path:
            sys.path.insert(0, server_src_str)

        return server_src

    def load_server_module(self, server_config: ServerConfig) -> Any:
        """Dynamically import and return server's mcp instance.

        Args:
            server_config: Configuration for the server to load

        Returns:
            The server's FastMCP instance

        Raises:
            ModuleNotFoundError: If server module cannot be imported
            AttributeError: If module doesn't have 'mcp' attribute
            ValueError: If mcp instance is invalid
        """
        module_name = server_config.module

        # Add server to Python path
        try:
            self.add_server_to_path(module_name)
        except FileNotFoundError as e:
            raise ModuleNotFoundError(
                f"Failed to load server '{server_config.name}': {e}\n"
                f"Solution: Ensure the server exists at {self.repo_root}/{module_name}/src/"
            )

        # Import the module - try __init__ first, fall back to server module
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                f"Failed to import server '{server_config.name}': {e}\n"
                f"Solution: Ensure dependencies are installed with: uv sync"
            )

        # Get mcp instance - check both __init__ and server modules
        mcp_instance = None
        if hasattr(module, "mcp"):
            mcp_instance = module.mcp
        else:
            # Try importing from server module
            try:
                server_module = importlib.import_module(f"{module_name}.server")
                if hasattr(server_module, "mcp"):
                    mcp_instance = server_module.mcp
            except (ModuleNotFoundError, AttributeError):
                pass

        if mcp_instance is None:
            raise AttributeError(
                f"Server module '{module_name}' does not have 'mcp' attribute.\n"
                f"Expected: {module_name}/__init__.py or {module_name}/server.py "
                f"should contain 'mcp = FastMCP(...)'"
            )

        # Validate mcp instance
        if not self.validate_server_module(mcp_instance):
            raise ValueError(
                f"Server '{server_config.name}' has invalid mcp instance.\n"
                f"Expected: FastMCP instance with _tool_manager attribute"
            )

        self.loaded_servers[server_config.name] = mcp_instance
        return mcp_instance

    def validate_server_module(self, mcp_instance: Any) -> bool:
        """Validate the loaded module has required attributes.

        Args:
            mcp_instance: The FastMCP instance to validate

        Returns:
            True if valid, False otherwise
        """
        # Check if it's a FastMCP instance with required attributes
        return (
            isinstance(mcp_instance, FastMCP)
            and hasattr(mcp_instance, "_tool_manager")
            and hasattr(mcp_instance._tool_manager, "_tools")
        )

    def register_tools(self, source_mcp: Any, target_mcp: FastMCP, prefix: str) -> int:
        """copy tools from source to target mcp with prefix

        note: accesses private _tool_manager._tools attribute as fastmcp
        does not provide a public api for tool registration copying

        Args:
            source_mcp: source fastmcp instance to copy tools from
            target_mcp: target fastmcp instance to register tools to
            prefix: prefix to add to tool names (e.g., 'dify' -> 'dify_tool_name')

        Returns:
            number of tools registered

        Raises:
            ValueError: if tool name collision is detected
        """
        if not hasattr(source_mcp, "_tool_manager"):
            return 0

        tool_manager = source_mcp._tool_manager
        if not hasattr(tool_manager, "_tools"):
            return 0

        tools = tool_manager._tools
        count = 0

        for tool_key, tool_obj in tools.items():
            # create prefixed tool name
            prefixed_name = f"{prefix}_{tool_obj.name}"

            # check for collision
            if prefixed_name in target_mcp._tool_manager._tools:
                raise ValueError(
                    f"tool name collision: '{prefixed_name}' already exists\n"
                    f"cannot register tool from '{prefix}' server"
                )

            # create a deep copy of the tool object and update its name
            # this ensures the registry key matches the tool's name attribute
            # deepcopy is used to avoid sharing nested mutable state
            tool_copy = copy.deepcopy(tool_obj)
            tool_copy.name = prefixed_name

            # register tool copy in target mcp
            target_mcp._tool_manager._tools[prefixed_name] = tool_copy

            count += 1

        return count

    def register_prompts(self, source_mcp: Any, target_mcp: FastMCP, prefix: str) -> int:
        """copy prompts from source to target mcp with prefix

        note: accesses private _prompt_manager._prompts attribute as fastmcp
        does not provide a public api for prompt registration copying

        Args:
            source_mcp: source fastmcp instance to copy prompts from
            target_mcp: target fastmcp instance to register prompts to
            prefix: prefix to add to prompt names

        Returns:
            number of prompts registered

        Raises:
            ValueError: if prompt name collision is detected
        """
        if not hasattr(source_mcp, "_prompt_manager"):
            return 0

        prompt_manager = source_mcp._prompt_manager
        if not hasattr(prompt_manager, "_prompts"):
            return 0

        prompts = prompt_manager._prompts
        count = 0

        for prompt_key, prompt_obj in prompts.items():
            # create prefixed prompt name
            prefixed_name = f"{prefix}_{prompt_obj.name}"

            # check for collision
            if prefixed_name in target_mcp._prompt_manager._prompts:
                raise ValueError(
                    f"prompt name collision: '{prefixed_name}' already exists\n"
                    f"cannot register prompt from '{prefix}' server"
                )

            # create a deep copy of the prompt object and update its name
            # this ensures the registry key matches the prompt's name attribute
            # deepcopy is used to avoid sharing nested mutable state
            prompt_copy = copy.deepcopy(prompt_obj)
            prompt_copy.name = prefixed_name

            # register prompt copy in target mcp
            target_mcp._prompt_manager._prompts[prefixed_name] = prompt_copy

            count += 1

        return count
