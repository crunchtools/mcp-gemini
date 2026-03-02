"""Image utility functions for saving and processing generated images."""

import io
import uuid
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


def save_generated_image(
    image_data: bytes,
    output_dir: Path,
    prefix: str = "gemini",
) -> Path:
    """Save image bytes to disk, return the file path.

    Args:
        image_data: Raw image bytes.
        output_dir: Directory to save the image in.
        prefix: Filename prefix.

    Returns:
        Path to the saved image file.
    """
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    filename = f"{prefix}_{timestamp}_{unique_id}.png"
    output_path = output_dir / filename

    img = Image.open(io.BytesIO(image_data))
    img.save(output_path, format="PNG")

    return output_path


def extract_text_from_response(response: object) -> str:
    """Extract text content from a Gemini response.

    Args:
        response: A Gemini generate_content response.

    Returns:
        Concatenated text from all text parts, or empty string.
    """
    texts: list[str] = []
    if hasattr(response, "candidates") and response.candidates:
        for candidate in response.candidates:
            if hasattr(candidate, "content") and candidate.content:
                for part in candidate.content.parts:
                    if hasattr(part, "text") and part.text:
                        texts.append(part.text)
    return "\n".join(texts)


def extract_image_from_response(response: object) -> tuple[bytes, str] | None:
    """Extract the first image from a Gemini response.

    Args:
        response: A Gemini generate_content response.

    Returns:
        Tuple of (image_bytes, mime_type) or None if no image found.
    """
    if hasattr(response, "candidates") and response.candidates:
        for candidate in response.candidates:
            if hasattr(candidate, "content") and candidate.content:
                for part in candidate.content.parts:
                    if hasattr(part, "inline_data") and part.inline_data:
                        return (
                            part.inline_data.data,
                            part.inline_data.mime_type or "image/png",
                        )
    return None
