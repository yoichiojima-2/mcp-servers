"""Tests for shared CLI utilities."""

import argparse

import pytest

from core import create_arg_parser, parse_args, validate_port


class TestValidatePort:
    """Tests for validate_port function."""

    def test_valid_port(self):
        """Test valid port numbers."""
        assert validate_port("8000") == 8000
        assert validate_port("1") == 1
        assert validate_port("65535") == 65535

    def test_port_out_of_range_low(self):
        """Test port below valid range."""
        with pytest.raises(argparse.ArgumentTypeError, match="must be between 1 and 65535"):
            validate_port("0")

    def test_port_out_of_range_high(self):
        """Test port above valid range."""
        with pytest.raises(argparse.ArgumentTypeError, match="must be between 1 and 65535"):
            validate_port("65536")

    def test_invalid_port_string(self):
        """Test non-integer port value."""
        with pytest.raises(argparse.ArgumentTypeError, match="not a valid integer"):
            validate_port("abc")

    def test_negative_port(self):
        """Test negative port number."""
        with pytest.raises(argparse.ArgumentTypeError, match="must be between 1 and 65535"):
            validate_port("-1")


class TestCreateArgParser:
    """Tests for create_arg_parser function."""

    def test_defaults(self):
        """Test default argument values."""
        parser = create_arg_parser("test-server", 8000)
        args = parser.parse_args([])

        assert args.transport == "stdio"
        assert args.host == "0.0.0.0"
        assert args.port == 8000
        assert args.allow_origin == "*"

    def test_cli_arguments(self):
        """Test CLI argument parsing."""
        parser = create_arg_parser("test-server", 8000)
        args = parser.parse_args(
            [
                "--transport",
                "sse",
                "--host",
                "127.0.0.1",
                "--port",
                "9000",
                "--allow-origin",
                "http://localhost:3000",
            ]
        )

        assert args.transport == "sse"
        assert args.host == "127.0.0.1"
        assert args.port == 9000
        assert args.allow_origin == "http://localhost:3000"

    def test_env_variables_as_defaults(self, monkeypatch):
        """Test environment variables are used as defaults."""
        monkeypatch.setenv("TRANSPORT", "sse")
        monkeypatch.setenv("HOST", "localhost")
        monkeypatch.setenv("PORT", "9999")
        monkeypatch.setenv("ALLOW_ORIGIN", "https://example.com")

        parser = create_arg_parser("test-server", 8000)
        args = parser.parse_args([])

        assert args.transport == "sse"
        assert args.host == "localhost"
        assert args.port == 9999
        assert args.allow_origin == "https://example.com"

    def test_cli_overrides_env(self, monkeypatch):
        """Test CLI arguments override environment variables."""
        monkeypatch.setenv("TRANSPORT", "sse")
        monkeypatch.setenv("PORT", "9999")

        parser = create_arg_parser("test-server", 8000)
        args = parser.parse_args(["--transport", "stdio", "--port", "8080"])

        assert args.transport == "stdio"
        assert args.port == 8080

    def test_transport_choices(self):
        """Test valid transport choices."""
        parser = create_arg_parser("test-server", 8000)

        # Valid choices
        for transport in ["stdio", "sse", "streamable-http"]:
            args = parser.parse_args(["--transport", transport])
            assert args.transport == transport

        # Invalid choice
        with pytest.raises(SystemExit):
            parser.parse_args(["--transport", "invalid"])

    def test_port_range_validation(self):
        """Test port validation through argparse."""
        parser = create_arg_parser("test-server", 8000)

        # Valid port
        args = parser.parse_args(["--port", "8080"])
        assert args.port == 8080

        # Invalid port (out of range)
        with pytest.raises(SystemExit):
            parser.parse_args(["--port", "0"])

        with pytest.raises(SystemExit):
            parser.parse_args(["--port", "70000"])

    def test_invalid_port_env_var(self, monkeypatch):
        """Test invalid PORT environment variable."""
        monkeypatch.setenv("PORT", "not_a_number")

        with pytest.raises(SystemExit):
            create_arg_parser("test-server", 8000)


class TestParseArgs:
    """Tests for parse_args function."""

    def test_parse_args_returns_namespace(self, monkeypatch):
        """Test parse_args returns proper namespace."""
        # Clear any env vars that might interfere
        monkeypatch.delenv("TRANSPORT", raising=False)
        monkeypatch.delenv("HOST", raising=False)
        monkeypatch.delenv("PORT", raising=False)
        monkeypatch.delenv("ALLOW_ORIGIN", raising=False)

        # Mock sys.argv
        monkeypatch.setattr("sys.argv", ["test"])

        args = parse_args("test-server", 8000)

        assert isinstance(args, argparse.Namespace)
        assert hasattr(args, "transport")
        assert hasattr(args, "host")
        assert hasattr(args, "port")
        assert hasattr(args, "allow_origin")
