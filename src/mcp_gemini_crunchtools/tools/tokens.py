"""Token counting tool."""

from typing import Any

from ..client import get_client
from .query import _resolve_model


async def gemini_count_tokens(
    content: str,
    model: str = "flash",
) -> dict[str, Any]:
    """Count the number of tokens in content.

    Args:
        content: The text content to count tokens for.
        model: Model to count tokens for.

    Returns:
        Token count.
    """
    client = get_client()
    model_name = _resolve_model(model)

    response = client.count_tokens(model=model_name, contents=[content])

    return {
        "total_tokens": response.total_tokens if response else 0,
        "model": model_name,
    }
