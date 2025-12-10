"""Tests for nano-banana image generation tools."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestValidateOutputPath:
    """Tests for _validate_output_path function."""

    def test_valid_png_path(self, tmp_path):
        from nano_banana.tools import _validate_output_path

        output = tmp_path / "test.png"
        _validate_output_path(output)  # Should not raise

    def test_valid_jpg_path(self, tmp_path):
        from nano_banana.tools import _validate_output_path

        output = tmp_path / "test.jpg"
        _validate_output_path(output)  # Should not raise

    def test_invalid_extension(self, tmp_path):
        from nano_banana.tools import _validate_output_path

        output = tmp_path / "test.txt"
        with pytest.raises(ValueError, match="must have image extension"):
            _validate_output_path(output)

    def test_forbidden_path(self):
        from nano_banana.tools import _validate_output_path

        output = Path("/etc/test.png")
        with pytest.raises(ValueError, match="Cannot write to system directory"):
            _validate_output_path(output)

    def test_creates_parent_directory(self, tmp_path):
        from nano_banana.tools import _validate_output_path

        output = tmp_path / "subdir" / "test.png"
        _validate_output_path(output)
        assert output.parent.exists()


class TestLoadImage:
    """Tests for _load_image function."""

    def test_file_not_found(self):
        from nano_banana.tools import _load_image

        with pytest.raises(FileNotFoundError):
            _load_image("/nonexistent/image.png")

    def test_unsupported_format(self, tmp_path):
        from nano_banana.tools import _load_image

        invalid_file = tmp_path / "test.bmp"
        invalid_file.write_bytes(b"fake image data")

        with pytest.raises(ValueError, match="Unsupported image format"):
            _load_image(str(invalid_file))


class TestGenerateImageImpl:
    """Tests for _generate_image_impl function."""

    def test_missing_api_key(self, tmp_path, monkeypatch):
        from nano_banana.tools import _generate_image_impl

        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

        result = _generate_image_impl(
            prompt="test prompt",
            output_path=str(tmp_path / "test.png"),
        )

        assert "Error" in result
        assert "API_KEY" in result or "environment variable" in result

    def test_invalid_model(self, tmp_path, monkeypatch):
        from nano_banana.tools import _generate_image_impl

        monkeypatch.setenv("GEMINI_API_KEY", "test-key")

        result = _generate_image_impl(
            prompt="test prompt",
            output_path=str(tmp_path / "test.png"),
            model="invalid_model",
        )

        assert "Error" in result
        assert "Unknown model" in result

    @patch("nano_banana.tools._get_client")
    @patch("nano_banana.tools._save_image_from_response")
    def test_successful_generation(self, mock_save, mock_get_client, tmp_path):
        from nano_banana.tools import _generate_image_impl

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_client.models.generate_content.return_value = mock_response

        output_path = tmp_path / "output.png"
        mock_save.return_value = str(output_path)

        result = _generate_image_impl(
            prompt="A test image",
            output_path=str(output_path),
        )

        assert "Generated image saved to" in result
        mock_client.models.generate_content.assert_called_once()


class TestGenerateSlideAssetImpl:
    """Tests for _generate_slide_asset_impl function."""

    def test_invalid_asset_type(self, tmp_path, monkeypatch):
        from nano_banana.tools import _generate_slide_asset_impl

        monkeypatch.setenv("GEMINI_API_KEY", "test-key")

        result = _generate_slide_asset_impl(
            asset_type="invalid_type",
            description="test",
            output_path=str(tmp_path / "test.png"),
        )

        assert "Error" in result
        assert "Unknown asset type" in result

    def test_invalid_theme(self, tmp_path, monkeypatch):
        from nano_banana.tools import _generate_slide_asset_impl

        monkeypatch.setenv("GEMINI_API_KEY", "test-key")

        result = _generate_slide_asset_impl(
            asset_type="icon",
            description="test",
            output_path=str(tmp_path / "test.png"),
            theme="invalid_theme",
        )

        assert "Error" in result
        assert "Unknown theme" in result


class TestImageToBase64Impl:
    """Tests for _image_to_base64_impl function."""

    def test_file_not_found(self):
        from nano_banana.tools import _image_to_base64_impl

        result = _image_to_base64_impl("/nonexistent/image.png")
        assert "Error" in result
        assert "not found" in result

    def test_unsupported_format(self, tmp_path):
        from nano_banana.tools import _image_to_base64_impl

        invalid_file = tmp_path / "test.bmp"
        invalid_file.write_bytes(b"fake data")

        result = _image_to_base64_impl(str(invalid_file))
        assert "Error" in result
        assert "Unsupported" in result

    def test_successful_conversion(self, tmp_path):
        from nano_banana.tools import _image_to_base64_impl

        # Create a minimal valid PNG
        png_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
            b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )

        png_file = tmp_path / "test.png"
        png_file.write_bytes(png_data)

        result = _image_to_base64_impl(str(png_file))

        assert result.startswith("data:image/png;base64,")
        assert "iVBOR" in result  # PNG base64 signature


class TestFuseImagesImpl:
    """Tests for _fuse_images_impl function."""

    def test_too_few_images(self, tmp_path, monkeypatch):
        from nano_banana.tools import _fuse_images_impl

        monkeypatch.setenv("GEMINI_API_KEY", "test-key")

        result = _fuse_images_impl(
            image_paths=[str(tmp_path / "single.png")],
            prompt="test",
            output_path=str(tmp_path / "output.png"),
        )

        assert "Error" in result
        assert "At least 2 images" in result

    def test_too_many_images(self, tmp_path, monkeypatch):
        from nano_banana.tools import _fuse_images_impl

        monkeypatch.setenv("GEMINI_API_KEY", "test-key")

        result = _fuse_images_impl(
            image_paths=[str(tmp_path / f"img{i}.png") for i in range(6)],
            prompt="test",
            output_path=str(tmp_path / "output.png"),
        )

        assert "Error" in result
        assert "Maximum 5" in result
