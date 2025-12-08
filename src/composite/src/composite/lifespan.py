import importlib
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

from .config import ServerConfig


class LifespanManager:
    def __init__(self, server_configs: List[ServerConfig], repo_root: Path):
        self.server_configs = server_configs
        self.repo_root = repo_root

    def _add_server_to_path(self, module_name: str):
        server_src = self.repo_root / module_name / "src"
        if server_src.exists() and str(server_src) not in sys.path:
            sys.path.insert(0, str(server_src))

    @asynccontextmanager
    async def composite_lifespan(self):
        """combine lifespans from multiple servers"""
        state = {}

        for server_config in self.server_configs:
            if server_config.module == "dify":
                self._add_server_to_path("dify")
                dify_tools = importlib.import_module("dify.tools")
                DifyClient = dify_tools.DifyClient

                client = DifyClient()
                state[server_config.name] = {"client": client}

        try:
            yield state
        finally:
            for server_name, server_state in state.items():
                if "client" in server_state and hasattr(
                    server_state["client"], "close"
                ):
                    await server_state["client"].close()
