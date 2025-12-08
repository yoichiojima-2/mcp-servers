"""Server loader module for dynamically loading and registering MCP servers."""

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
        """Add server's src directory to Python path.

        Args:
            module_name: Name of the server module

        Returns:
            Path to the server's src directory

        Raises:
            FileNotFoundError: If server src directory doesn't exist
        """
        server_src = self.repo_root / module_name / "src"
        if not server_src.exists():
            raise FileNotFoundError(
                f"Server source directory not found: {server_src}\n"
                f"Expected structure: {self.repo_root}/{module_name}/src/"
            )

        # Add to Python path if not already present
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

        # Import the module
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                f"Failed to import server '{server_config.name}': {e}\n"
                f"Solution: Ensure dependencies are installed with: uv sync"
            )

        # Get mcp instance
        if not hasattr(module, "mcp"):
            raise AttributeError(
                f"Server module '{module_name}' does not have 'mcp' attribute.\n"
                f"Expected: {module_name}/__init__.py should contain 'mcp = FastMCP(...)'"
            )

        mcp_instance = module.mcp

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

    def register_tools(
        self, source_mcp: Any, target_mcp: FastMCP, prefix: str
    ) -> int:
        """Copy tools from source to target MCP with prefix.

        Args:
            source_mcp: Source FastMCP instance to copy tools from
            target_mcp: Target FastMCP instance to register tools to
            prefix: Prefix to add to tool names (e.g., 'dify' -> 'dify_tool_name')

        Returns:
            Number of tools registered
        """
        if not hasattr(source_mcp, "_tool_manager"):
            return 0

        tool_manager = source_mcp._tool_manager
        if not hasattr(tool_manager, "_tools"):
            return 0

        tools = tool_manager._tools
        count = 0

        for tool_key, tool_obj in tools.items():
            # Create prefixed tool name
            prefixed_name = f"{prefix}_{tool_obj.name}"

            # Register tool in target MCP
            target_mcp._tool_manager._tools[prefixed_name] = tool_obj

            count += 1

        return count

    def register_prompts(
        self, source_mcp: Any, target_mcp: FastMCP, prefix: str
    ) -> int:
        """Copy prompts from source to target MCP with prefix.

        Args:
            source_mcp: Source FastMCP instance to copy prompts from
            target_mcp: Target FastMCP instance to register prompts to
            prefix: Prefix to add to prompt names

        Returns:
            Number of prompts registered
        """
        if not hasattr(source_mcp, "_prompt_manager"):
            return 0

        prompt_manager = source_mcp._prompt_manager
        if not hasattr(prompt_manager, "_prompts"):
            return 0

        prompts = prompt_manager._prompts
        count = 0

        for prompt_key, prompt_obj in prompts.items():
            # Create prefixed prompt name
            prefixed_name = f"{prefix}_{prompt_obj.name}"

            # Register prompt in target MCP
            target_mcp._prompt_manager._prompts[prefixed_name] = prompt_obj

            count += 1

        return count
