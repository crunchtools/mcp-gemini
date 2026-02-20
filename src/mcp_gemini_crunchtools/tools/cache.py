"""Content caching tools."""

from typing import Any

from google.genai import types

from ..client import get_client
from ..models import validate_file_exists
from .query import _resolve_model


async def gemini_create_cache(
    file_path: str | None = None,
    content: str | None = None,
    display_name: str = "mcp-cache",
    system_instruction: str | None = None,
    ttl_minutes: int = 60,
    model: str = "flash",
) -> dict[str, Any]:
    """Create a content cache for repeated queries.

    Upload content once and query it multiple times without re-sending.

    Args:
        file_path: Path to a file to cache.
        content: Text content to cache (alternative to file_path).
        display_name: Human-readable name for the cache.
        system_instruction: System instruction for queries against this cache.
        ttl_minutes: Time-to-live in minutes (default 60).
        model: Model to use.

    Returns:
        Cache name/ID and metadata.
    """
    client = get_client()
    model_name = _resolve_model(model)

    contents: list[Any] = []
    if file_path:
        file_path = validate_file_exists(file_path)
        uploaded_file = client.upload_file(file_path)
        contents.append(uploaded_file)
    elif content:
        contents.append(content)
    else:
        msg = "Either file_path or content must be provided."
        raise ValueError(msg)

    cache_config: dict[str, Any] = {
        "model": model_name,
        "contents": contents,
        "config": types.CreateCachedContentConfig(
            display_name=display_name,
            ttl=f"{ttl_minutes * 60}s",
        ),
    }
    if system_instruction:
        cache_config["config"].system_instruction = system_instruction

    cache = client.client.caches.create(**cache_config)

    return {
        "cache_name": cache.name,
        "display_name": display_name,
        "model": model_name,
        "ttl_minutes": ttl_minutes,
    }


async def gemini_query_cache(
    cache_name: str,
    question: str,
) -> dict[str, Any]:
    """Query content in a cache.

    Args:
        cache_name: The cache name from gemini_create_cache.
        question: Question to ask about the cached content.

    Returns:
        Response from the cached content.
    """
    client = get_client()

    config = types.GenerateContentConfig(
        cached_content=cache_name,
    )

    response = client.generate_content(
        model="gemini-1.5-flash",
        contents=[question],
        config=config,
    )

    return {
        "response": response.text,
        "cache_name": cache_name,
    }


async def gemini_list_caches() -> dict[str, Any]:
    """List all active content caches.

    Returns:
        List of active caches.
    """
    client = get_client()
    caches_list = list(client.client.caches.list())

    result = []
    for cache in caches_list:
        result.append({
            "name": cache.name,
            "display_name": cache.display_name,
            "model": cache.model,
            "create_time": str(cache.create_time) if cache.create_time else None,
            "expire_time": str(cache.expire_time) if cache.expire_time else None,
        })

    return {"caches": result, "count": len(result)}


async def gemini_delete_cache(
    cache_name: str,
) -> dict[str, Any]:
    """Delete a content cache.

    Args:
        cache_name: The cache name to delete.

    Returns:
        Deletion confirmation.
    """
    client = get_client()
    client.client.caches.delete(name=cache_name)

    return {"cache_name": cache_name, "status": "deleted"}
