"""configuration module for composite mcp server"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml


@dataclass
class ServerConfig:
    """Configuration for a single server in the composite."""

    name: str
    module: str
    prefix: str
    enabled: bool = True
    has_lifespan: bool = False
    description: str = ""

    def __post_init__(self):
        """Validate server configuration."""
        if not self.name:
            raise ValueError("Server name cannot be empty")
        if not self.module:
            raise ValueError("Server module cannot be empty")
        if not self.prefix:
            raise ValueError("Server prefix cannot be empty")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServerConfig":
        """Create ServerConfig from dictionary."""
        required_fields = ["name", "module", "prefix"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field '{field}' in server configuration")

        return cls(
            name=data["name"],
            module=data["module"],
            prefix=data["prefix"],
            enabled=data.get("enabled", True),
            has_lifespan=data.get("has_lifespan", False),
            description=data.get("description", ""),
        )


@dataclass
class CompositeConfig:
    """configuration for the composite mcp server"""

    servers: List[ServerConfig]

    @classmethod
    def from_yaml(cls, config_path: Path) -> "CompositeConfig":
        """Load configuration from YAML file.

        Args:
            config_path: Path to the YAML configuration file

        Returns:
            CompositeConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If YAML is invalid or missing required fields
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        # check file size to prevent yaml bomb attacks (max 1mb)
        file_size = config_path.stat().st_size
        max_size = 1024 * 1024  # 1mb
        if file_size > max_size:
            raise ValueError(
                f"configuration file too large: {file_size} bytes "
                f"(max {max_size} bytes)\n"
                f"this prevents yaml bomb resource exhaustion attacks"
            )

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"invalid yaml syntax in {config_path}: {e}")

        if not isinstance(data, dict):
            raise ValueError("Configuration file must contain a YAML object")

        if "servers" not in data:
            raise ValueError("Configuration must contain 'servers' key")

        servers_data = data["servers"]
        if not isinstance(servers_data, list):
            raise ValueError("'servers' must be a list")

        # Parse server configurations
        servers = []
        for i, server_data in enumerate(servers_data):
            if not isinstance(server_data, dict):
                raise ValueError(f"Server at index {i} must be an object")
            try:
                servers.append(ServerConfig.from_dict(server_data))
            except ValueError as e:
                raise ValueError(f"Error in server at index {i}: {e}")

        # create config
        config = cls(servers=servers)

        # Validate configuration
        config.validate()

        return config

    def validate(self):
        """Validate the configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        # Check for duplicate server names
        server_names = [s.name for s in self.servers]
        duplicate_names = [name for name in server_names if server_names.count(name) > 1]
        if duplicate_names:
            raise ValueError(f"Duplicate server names found: {', '.join(set(duplicate_names))}")

        # Check for duplicate prefixes among enabled servers
        enabled_prefixes = [s.prefix for s in self.servers if s.enabled]
        duplicate_prefixes = [prefix for prefix in enabled_prefixes if enabled_prefixes.count(prefix) > 1]
        if duplicate_prefixes:
            raise ValueError(
                f"Duplicate prefixes found among enabled servers: "
                f"{', '.join(set(duplicate_prefixes))}\n"
                f"Each enabled server must have a unique prefix."
            )

    def get_enabled_servers(self) -> List[ServerConfig]:
        """Get list of enabled servers.

        Returns:
            List of ServerConfig instances with enabled=True
        """
        return [s for s in self.servers if s.enabled]
