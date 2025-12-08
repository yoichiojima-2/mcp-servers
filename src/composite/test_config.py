import tempfile
from pathlib import Path

import pytest

from composite.config import CompositeConfig, ServerConfig


def test_server_config_from_dict():
    data = {"name": "test", "module": "test_module", "prefix": "test"}
    config = ServerConfig.from_dict(data)
    assert config.name == "test"
    assert config.module == "test_module"
    assert config.prefix == "test"
    assert config.enabled is True
    assert config.has_lifespan is False


def test_server_config_validation():
    with pytest.raises(ValueError, match="Missing required field 'name'"):
        ServerConfig.from_dict({"module": "test", "prefix": "test"})


def test_composite_config_from_yaml():
    yaml_content = """
servers:
  - name: server1
    module: module1
    prefix: s1
    enabled: true
  - name: server2
    module: module2
    prefix: s2
    enabled: false
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        f.flush()
        config_path = Path(f.name)

    try:
        config = CompositeConfig.from_yaml(config_path)
        assert len(config.servers) == 2
        assert config.servers[0].name == "server1"
        assert config.servers[1].name == "server2"
    finally:
        config_path.unlink()


def test_get_enabled_servers():
    yaml_content = """
servers:
  - name: server1
    module: module1
    prefix: s1
    enabled: true
  - name: server2
    module: module2
    prefix: s2
    enabled: false
  - name: server3
    module: module3
    prefix: s3
    enabled: true
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        f.flush()
        config_path = Path(f.name)

    try:
        config = CompositeConfig.from_yaml(config_path)
        enabled = config.get_enabled_servers()
        assert len(enabled) == 2
        assert enabled[0].name == "server1"
        assert enabled[1].name == "server3"
    finally:
        config_path.unlink()


def test_duplicate_prefix_validation():
    yaml_content = """
servers:
  - name: server1
    module: module1
    prefix: same
    enabled: true
  - name: server2
    module: module2
    prefix: same
    enabled: true
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        f.flush()
        config_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Duplicate prefixes"):
            CompositeConfig.from_yaml(config_path)
    finally:
        config_path.unlink()


def test_duplicate_server_names():
    yaml_content = """
servers:
  - name: same
    module: module1
    prefix: s1
  - name: same
    module: module2
    prefix: s2
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        f.flush()
        config_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Duplicate server names"):
            CompositeConfig.from_yaml(config_path)
    finally:
        config_path.unlink()


def test_missing_config_file():
    with pytest.raises(FileNotFoundError):
        CompositeConfig.from_yaml(Path("/nonexistent/config.yaml"))


def test_yaml_size_limit():
    """test that yaml files larger than 1mb are rejected"""
    # create a large yaml file (>1mb) with valid structure
    server_entry = """  - name: server{i}
    module: module{i}
    prefix: prefix{i}
    enabled: true
"""
    # create enough entries to exceed 1mb
    large_yaml = "servers:\n" + "".join(server_entry.format(i=i) for i in range(15000))

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(large_yaml)
        f.flush()
        config_path = Path(f.name)

    try:
        # verify file is over 1mb
        assert config_path.stat().st_size > 1024 * 1024

        with pytest.raises(ValueError, match="configuration file too large"):
            CompositeConfig.from_yaml(config_path)
    finally:
        config_path.unlink()
