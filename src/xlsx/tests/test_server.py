"""Tests for xlsx server configuration."""

import os
from unittest.mock import patch

import pytest

from core import validate_port
from xlsx.server import DEFAULT_PORT


def parse_args():
    """Import parse_args for testing - wraps core's parse_args."""
    from core import parse_args as core_parse_args

    return core_parse_args("xlsx", DEFAULT_PORT)


class TestParseArgs:
    """Tests for parse_args function."""

    def test_defaults(self):
        """Test default argument values."""
        with patch("sys.argv", ["server.py"]):
            args = parse_args()
            assert args.transport == "stdio"
            assert args.host == "0.0.0.0"
            assert args.port == DEFAULT_PORT
            assert args.allow_origin == "*"

    def test_cli_arguments(self):
        """Test CLI arguments are parsed correctly."""
        with patch("sys.argv", ["server.py", "--transport", "sse", "--port", "9000", "--host", "127.0.0.1"]):
            args = parse_args()
            assert args.transport == "sse"
            assert args.port == 9000
            assert args.host == "127.0.0.1"

    def test_env_variables_as_defaults(self):
        """Test environment variables are used as defaults."""
        with patch.dict(os.environ, {"TRANSPORT": "sse", "PORT": "9999", "HOST": "localhost"}):
            with patch("sys.argv", ["server.py"]):
                args = parse_args()
                assert args.transport == "sse"
                assert args.port == 9999
                assert args.host == "localhost"

    def test_cli_overrides_env(self):
        """Test CLI arguments override environment variables."""
        with patch.dict(os.environ, {"TRANSPORT": "stdio", "PORT": "9999"}):
            with patch("sys.argv", ["server.py", "--transport", "sse", "--port", "8080"]):
                args = parse_args()
                assert args.transport == "sse"
                assert args.port == 8080

    def test_transport_choices(self):
        """Test transport argument only accepts valid choices."""
        with patch("sys.argv", ["server.py", "--transport", "invalid"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_allow_origin(self):
        """Test allow-origin argument."""
        with patch("sys.argv", ["server.py", "--allow-origin", "https://example.com"]):
            args = parse_args()
            assert args.allow_origin == "https://example.com"

    def test_port_range_validation(self):
        """Test port must be within valid range."""
        with patch("sys.argv", ["server.py", "--port", "70000"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_port_invalid_value(self):
        """Test port rejects non-integer values."""
        with patch("sys.argv", ["server.py", "--port", "abc"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_invalid_port_env_var(self):
        """Test invalid PORT environment variable causes exit."""
        with patch.dict(os.environ, {"PORT": "not_a_number"}, clear=False):
            with patch("sys.argv", ["server.py"]):
                with pytest.raises(SystemExit):
                    parse_args()


class TestValidatePort:
    """Tests for validate_port function."""

    def test_valid_port(self):
        """Test valid port values."""
        assert validate_port("8080") == 8080
        assert validate_port("1") == 1
        assert validate_port("65535") == 65535

    def test_port_out_of_range(self):
        """Test port outside valid range raises error."""
        import argparse

        with pytest.raises(argparse.ArgumentTypeError):
            validate_port("0")
        with pytest.raises(argparse.ArgumentTypeError):
            validate_port("65536")

    def test_invalid_port_string(self):
        """Test non-numeric port raises error."""
        import argparse

        with pytest.raises(argparse.ArgumentTypeError):
            validate_port("abc")
