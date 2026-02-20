"""URL analysis tools."""

from typing import Any

from google.genai import types

from ..client import get_client
from .query import _resolve_model


async def gemini_analyze_url(
    urls: list[str],
    question: str = "Analyze the content of these URLs.",
    use_google_search: bool = True,
    model: str = "flash",
) -> dict[str, Any]:
    """Analyze one or more URLs.

    Args:
        urls: List of URLs to analyze (1-20).
        question: Question or instruction about the URL content.
        use_google_search: Use Google Search grounding.
        model: Model to use.

    Returns:
        Analysis results.
    """
    client = get_client()
    model_name = _resolve_model(model)

    url_list = "\n".join(f"- {url}" for url in urls)
    prompt = f"{question}\n\nURLs:\n{url_list}"

    config_kwargs: dict[str, Any] = {}
    if use_google_search:
        config_kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]

    config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

    response = client.generate_content(
        model=model_name, contents=[prompt], config=config,
    )

    return {"response": response.text, "model": model_name, "urls": urls}


async def gemini_compare_urls(
    url1: str,
    url2: str,
    aspect: str = "content",
    model: str = "flash",
) -> dict[str, Any]:
    """Compare two URLs.

    Args:
        url1: First URL to compare.
        url2: Second URL to compare.
        aspect: What to compare (content, design, sentiment, features).
        model: Model to use.

    Returns:
        Comparison results.
    """
    prompt = (
        f"Compare these two URLs focusing on {aspect}:\n"
        f"1. {url1}\n2. {url2}\n\n"
        "Provide a detailed comparison highlighting similarities and differences."
    )
    return await gemini_analyze_url(
        urls=[url1, url2], question=prompt, model=model,
    )


async def gemini_extract_from_url(
    url: str,
    data_type: str = "text",
    custom_fields: str | None = None,
    model: str = "flash",
) -> dict[str, Any]:
    """Extract specific data from a URL.

    Args:
        url: URL to extract data from.
        data_type: Type of data to extract (text, links, images, structured).
        custom_fields: Comma-separated list of custom fields to extract.
        model: Model to use.

    Returns:
        Extracted data.
    """
    prompt = f"Extract {data_type} data from this URL: {url}"
    if custom_fields:
        prompt += f"\n\nSpecifically extract these fields: {custom_fields}"

    return await gemini_analyze_url(
        urls=[url], question=prompt, model=model,
    )
