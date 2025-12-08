import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from .config import CompositeConfig
from .lifespan import LifespanManager
from .loader import ServerLoader

_mcp = None


def get_mcp():
    """lazy initialization of mcp server"""
    global _mcp
    if _mcp is not None:
        return _mcp

    repo_root = Path(__file__).parent.parent.parent.parent

    config_path = os.getenv("COMPOSITE_CONFIG_PATH")
    if not config_path:
        for candidate in [
            Path.cwd() / "composite-config.yaml",
            Path(__file__).parent.parent.parent / "composite-config.yaml",
        ]:
            if candidate.exists():
                config_path = str(candidate)
                break

    if not config_path:
        raise RuntimeError(
            "No configuration file found.\n"
            "Create composite-config.yaml in current directory "
            "or set COMPOSITE_CONFIG_PATH environment variable.\n"
            f"Example config: {Path(__file__).parent.parent.parent}/composite-config.yaml"
        )

    config = CompositeConfig.from_yaml(Path(config_path))
    loader = ServerLoader(repo_root)

    loaded_modules = {}
    for server_config in config.get_enabled_servers():
        try:
            mcp_module = loader.load_server_module(server_config)
            loaded_modules[server_config.name] = {
                "mcp": mcp_module,
                "config": server_config,
            }
        except Exception as e:
            raise RuntimeError(
                f"Failed to load server '{server_config.name}': {e}\n"
                f"Cannot start composite server with missing servers."
            ) from e

    lifespan_servers = [s for s in config.get_enabled_servers() if s.has_lifespan]
    lifespan_manager = LifespanManager(lifespan_servers, repo_root) if lifespan_servers else None

    @asynccontextmanager
    async def composite_lifespan():
        if lifespan_manager:
            async with lifespan_manager.composite_lifespan() as state:
                yield state
        else:
            yield {}

    server_names = [s.name for s in config.get_enabled_servers()]
    _mcp = FastMCP(f"Composite: {' + '.join(server_names)}", lifespan=composite_lifespan)

    for server_name, module_info in loaded_modules.items():
        source_mcp = module_info["mcp"]
        server_config = module_info["config"]

        tools_count = loader.register_tools(source_mcp, _mcp, server_config.prefix)
        prompts_count = loader.register_prompts(source_mcp, _mcp, server_config.prefix)

        print(f"loaded '{server_name}': {tools_count} tools, {prompts_count} prompts")

    return _mcp


def serve():
    """start mcp server"""
    mcp_instance = get_mcp()

    cors_middleware = Middleware(
        CORSMiddleware,
        allow_origins=[os.getenv("ALLOW_ORIGIN", "*")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    transport = os.getenv("TRANSPORT", "stdio")

    if transport == "stdio":
        mcp_instance.run(transport="stdio")
    else:
        mcp_instance.run(
            transport=transport,
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", 8000)),
            middleware=[cors_middleware],
        )
