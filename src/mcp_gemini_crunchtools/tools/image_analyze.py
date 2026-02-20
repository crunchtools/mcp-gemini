"""Image analysis tool."""

from typing import Any

from PIL import Image

from ..client import get_client
from ..models import validate_file_exists
from .query import _resolve_model


async def gemini_analyze_image(
    image_path: str,
    query: str = "Describe this image in detail.",
    model: str = "flash",
) -> dict[str, Any]:
    """Analyze and describe a local image file.

    Args:
        image_path: Absolute path to the image file.
        query: Question or instruction about the image.
        model: Model to use ('pro' or 'flash').

    Returns:
        Analysis results.
    """
    image_path = validate_file_exists(image_path)
    client = get_client()
    model_name = _resolve_model(model)

    img = Image.open(image_path)

    response = client.generate_content(
        model=model_name, contents=[query, img],
    )

    return {
        "response": response.text,
        "model": model_name,
        "image_path": image_path,
    }
