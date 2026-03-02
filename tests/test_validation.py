"""Input validation tests for models.py validators."""

import pytest

from mcp_gemini_crunchtools.models import (
    VALID_ASPECT_RATIOS,
    VALID_IMAGE_SIZES,
    validate_aspect_ratio,
    validate_file_path,
    validate_image_size,
)


class TestValidateFilePath:
    """Tests for validate_file_path."""

    def test_absolute_path_accepted(self) -> None:
        assert validate_file_path("/home/user/file.txt") == "/home/user/file.txt"

    def test_root_path_accepted(self) -> None:
        assert validate_file_path("/file.txt") == "/file.txt"

    def test_relative_path_rejected(self) -> None:
        with pytest.raises(ValueError, match="absolute path"):
            validate_file_path("relative/path.txt")

    def test_dot_path_rejected(self) -> None:
        with pytest.raises(ValueError, match="absolute path"):
            validate_file_path("./file.txt")

    def test_empty_string_rejected(self) -> None:
        with pytest.raises(ValueError, match="absolute path"):
            validate_file_path("")


class TestValidateFileExists:
    """Tests for validate_file_exists."""

    def test_nonexistent_file_rejected(self) -> None:
        from mcp_gemini_crunchtools.models import validate_file_exists

        with pytest.raises(ValueError, match="File not found"):
            validate_file_exists("/nonexistent/path/file.txt")

    def test_relative_path_rejected(self) -> None:
        from mcp_gemini_crunchtools.models import validate_file_exists

        with pytest.raises(ValueError, match="absolute path"):
            validate_file_exists("relative/file.txt")


class TestValidateAspectRatio:
    """Tests for validate_aspect_ratio."""

    @pytest.mark.parametrize("ratio", sorted(VALID_ASPECT_RATIOS))
    def test_valid_ratios_accepted(self, ratio: str) -> None:
        assert validate_aspect_ratio(ratio) == ratio

    def test_invalid_ratio_rejected(self) -> None:
        with pytest.raises(ValueError, match="Invalid aspect_ratio"):
            validate_aspect_ratio("5:3")

    def test_empty_ratio_rejected(self) -> None:
        with pytest.raises(ValueError, match="Invalid aspect_ratio"):
            validate_aspect_ratio("")

    def test_nonsense_rejected(self) -> None:
        with pytest.raises(ValueError, match="Invalid aspect_ratio"):
            validate_aspect_ratio("widescreen")


class TestValidateImageSize:
    """Tests for validate_image_size."""

    @pytest.mark.parametrize("size", sorted(VALID_IMAGE_SIZES))
    def test_valid_sizes_accepted(self, size: str) -> None:
        assert validate_image_size(size) == size

    def test_invalid_size_rejected(self) -> None:
        with pytest.raises(ValueError, match="Invalid image_size"):
            validate_image_size("8K")

    def test_lowercase_rejected(self) -> None:
        with pytest.raises(ValueError, match="Invalid image_size"):
            validate_image_size("2k")

    def test_empty_rejected(self) -> None:
        with pytest.raises(ValueError, match="Invalid image_size"):
            validate_image_size("")
