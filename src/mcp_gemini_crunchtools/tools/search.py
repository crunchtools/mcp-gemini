"""Web search tool using Gemini with Google Search grounding."""

from typing import Any

from google.genai import types

from ..client import get_client
from .query import _resolve_model


async def gemini_search(
    query: str,
    model: str = "flash",
) -> dict[str, Any]:
    """Search the web using Gemini with Google Search grounding.

    Args:
        query: The search query.
        model: Model to use.

    Returns:
        Search results with grounding.
    """
    client = get_client()
    model_name = _resolve_model(model)

    config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
    )

    response = client.generate_content(
        model=model_name, contents=[query], config=config,
    )

    return {"response": response.text, "model": model_name, "query": query}
