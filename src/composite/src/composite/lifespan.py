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
        """add server's src directory to python path

        security note: paths are added to sys.path which persists globally.
        ensure module_name comes from trusted configuration only.
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

        if server_src.exists() and str(server_src) not in sys.path:
            sys.path.insert(0, str(server_src))

    @asynccontextmanager
    async def composite_lifespan(self):
        """combine lifespans from multiple servers

        servers must export an app_lifespan() function in their server module
        that yields a dict of state to be passed to the lifespan context
        """
        state = {}
        cleanup_contexts = []

        for server_config in self.server_configs:
            try:
                self._add_server_to_path(server_config.module)
                server_module = importlib.import_module(f"{server_config.module}.server")

                # check if server has app_lifespan function
                if not hasattr(server_module, "app_lifespan"):
                    continue

                app_lifespan = server_module.app_lifespan

                # enter the lifespan context
                ctx = app_lifespan()
                server_state = await ctx.__aenter__()

                # store state and context for cleanup
                state[server_config.name] = server_state
                cleanup_contexts.append((server_config.name, ctx))

            except Exception as e:
                # cleanup any already-initialized contexts
                for cleanup_name, ctx in reversed(cleanup_contexts):
                    try:
                        await ctx.__aexit__(None, None, None)
                    except Exception as cleanup_error:
                        print(f"warning: failed to cleanup '{cleanup_name}' after init error: {cleanup_error}")
                raise RuntimeError(f"failed to initialize lifespan for server '{server_config.name}': {e}") from e

        try:
            yield state
        finally:
            # cleanup in reverse order
            for name, ctx in reversed(cleanup_contexts):
                try:
                    await ctx.__aexit__(None, None, None)
                except Exception as e:
                    print(f"warning: error cleaning up lifespan for '{name}': {e}")
