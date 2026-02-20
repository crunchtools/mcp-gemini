"""YouTube analysis tools."""

from typing import Any

from google.genai import types

from ..client import get_client
from .query import _resolve_model


async def gemini_youtube(
    url: str,
    question: str = "Analyze this video and provide key insights.",
    model: str = "flash",
) -> dict[str, Any]:
    """Analyze a YouTube video.

    Args:
        url: YouTube video URL.
        question: Question or instruction about the video.
        model: Model to use.

    Returns:
        Analysis results.
    """
    client = get_client()
    model_name = _resolve_model(model)

    config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
    )

    prompt = f"{question}\n\nYouTube URL: {url}"

    response = client.generate_content(
        model=model_name, contents=[prompt], config=config,
    )

    return {"response": response.text, "model": model_name, "url": url}


async def gemini_youtube_summary(
    url: str,
    style: str = "concise",
    model: str = "flash",
) -> dict[str, Any]:
    """Summarize a YouTube video.

    Args:
        url: YouTube video URL.
        style: Summary style (concise, detailed, bullet_points).
        model: Model to use.

    Returns:
        Summary results.
    """
    prompt = (
        f"Provide a {style} summary of this YouTube video, "
        "including the main topics, key points, and conclusions."
    )
    return await gemini_youtube(url=url, question=prompt, model=model)
