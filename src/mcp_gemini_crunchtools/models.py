"""Pydantic input validation models.

This module defines validation models for tool inputs.
All user-provided values are validated before being used.
"""

import os

VALID_ASPECT_RATIOS = frozenset({
    "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9",
})

VALID_IMAGE_SIZES = frozenset({"1K", "2K", "4K"})

VALID_IMAGEN_MODELS = frozenset({
    "imagen-4.0-generate-001",
    "imagen-4.0-ultra-generate-001",
    "imagen-4.0-fast-generate-001",
})

VALID_TEXT_MODELS = frozenset({
    "pro", "flash",
    "gemini-3-pro-preview", "gemini-3-flash-preview",
})

# Max file sizes
MAX_IMAGE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB
MAX_DOCUMENT_SIZE_BYTES = 100 * 1024 * 1024  # 100MB


def validate_file_path(file_path: str) -> str:
    """Validate a file path is absolute.

    Args:
        file_path: The file path to validate.

    Returns:
        The validated file path.

    Raises:
        ValueError: If the path is not absolute.
    """
    if not os.path.isabs(file_path):
        msg = "file_path must be an absolute path"
        raise ValueError(msg)
    return file_path


def validate_file_exists(file_path: str) -> str:
    """Validate file exists on disk.

    Args:
        file_path: The file path to validate.

    Returns:
        The validated file path.

    Raises:
        ValueError: If the path is not absolute or file doesn't exist.
    """
    file_path = validate_file_path(file_path)
    if not os.path.isfile(file_path):
        msg = f"File not found: {file_path}"
        raise ValueError(msg)
    return file_path


def validate_aspect_ratio(aspect_ratio: str) -> str:
    """Validate an aspect ratio string.

    Args:
        aspect_ratio: The aspect ratio to validate.

    Returns:
        The validated aspect ratio.

    Raises:
        ValueError: If the aspect ratio is not valid.
    """
    if aspect_ratio not in VALID_ASPECT_RATIOS:
        msg = f"Invalid aspect_ratio '{aspect_ratio}'. Valid: {sorted(VALID_ASPECT_RATIOS)}"
        raise ValueError(msg)
    return aspect_ratio


def validate_image_size(image_size: str) -> str:
    """Validate an image size string.

    Args:
        image_size: The image size to validate.

    Returns:
        The validated image size.

    Raises:
        ValueError: If the image size is not valid.
    """
    if image_size not in VALID_IMAGE_SIZES:
        msg = f"Invalid image_size '{image_size}'. Valid: {sorted(VALID_IMAGE_SIZES)}"
        raise ValueError(msg)
    return image_size
