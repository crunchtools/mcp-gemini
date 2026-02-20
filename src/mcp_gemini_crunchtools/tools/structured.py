"""Structured output and data extraction tools."""

from typing import Any

from google.genai import types

from ..client import get_client
from .query import _resolve_model


async def gemini_structured(
    prompt: str,
    schema: dict[str, Any] | None = None,
    use_google_search: bool = False,
    model: str = "flash",
) -> dict[str, Any]:
    """Get structured JSON output from Gemini.

    Args:
        prompt: The prompt to generate structured output for.
        schema: Optional JSON schema to constrain the output.
        use_google_search: Ground response with Google Search.
        model: Model to use.

    Returns:
        Structured response.
    """
    client = get_client()
    model_name = _resolve_model(model)

    config_kwargs: dict[str, Any] = {
        "response_mime_type": "application/json",
    }
    if schema:
        config_kwargs["response_schema"] = schema
    if use_google_search:
        config_kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]

    config = types.GenerateContentConfig(**config_kwargs)

    response = client.generate_content(
        model=model_name, contents=[prompt], config=config,
    )

    return {"response": response.text, "model": model_name}


async def gemini_extract(
    text: str,
    extract_type: str = "entities",
    custom_fields: str | None = None,
    model: str = "flash",
) -> dict[str, Any]:
    """Extract structured data from text.

    Args:
        text: Text to extract data from.
        extract_type: Type of extraction (entities, dates, numbers, contacts, custom).
        custom_fields: Comma-separated list of custom fields to extract.
        model: Model to use.

    Returns:
        Extracted data in JSON format.
    """
    prompt = f"Extract {extract_type} from the following text and return as JSON:\n\n{text}"
    if custom_fields:
        prompt += f"\n\nSpecifically extract these fields: {custom_fields}"

    return await gemini_structured(prompt=prompt, model=model)
