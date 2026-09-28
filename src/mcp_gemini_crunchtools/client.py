"""Google Gemini API client wrapper.

This module provides a shared client instance for the google-genai SDK.
All tools should use get_client() to access the Gemini API.
"""

import asyncio
import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import httpx
from google import genai
from google.genai import types

from .config import get_config
from .errors import GeminiApiError, RateLimitError

logger = logging.getLogger(__name__)

# google-genai's HTTP layer has no timeout by default, so a stalled request
# holds its worker thread forever. Bounded here so a hang ends as an error.
HTTP_TIMEOUT_MS = 300_000
# Generated images arrive inline as base64, so this is sized for those.
MAX_RESPONSE_SIZE = 100 * 1024 * 1024


class _BoundedStream(httpx.SyncByteStream):
    """Counts body bytes as they are read, for responses with no Content-Length."""

    def __init__(self, inner: Any) -> None:
        self._inner = inner

    def __iter__(self) -> Iterator[bytes]:
        total = 0
        for chunk in self._inner:
            total += len(chunk)
            if total > MAX_RESPONSE_SIZE:
                raise GeminiApiError("Response too large")
            yield chunk

    def close(self) -> None:
        self._inner.close()


def _reject_oversized(response: httpx.Response) -> None:
    """httpx response hook: runs before the body is read, so it can bound it."""
    content_length = response.headers.get("content-length")
    if content_length and int(content_length) > MAX_RESPONSE_SIZE:
        raise GeminiApiError("Response too large")
    response.stream = _BoundedStream(response.stream)


class GeminiClient:
    """Wrapper around google-genai Client.

    Provides a single shared client instance and convenience methods
    for common Gemini operations with proper error handling.

    The network methods are async and run the SDK's synchronous call in a
    worker thread. Called inline from an async tool, one slow generation
    blocked the event loop, and with it every other request, down to
    ``initialize``: the server stopped answering anyone until it returned.
    """

    def __init__(self) -> None:
        """Initialize the Gemini client."""
        config = get_config()
        self._client = genai.Client(
            api_key=config.api_key,
            http_options=types.HttpOptions(
                timeout=HTTP_TIMEOUT_MS,
                # Uncompressed, so the bytes the size limit counts are the
                # bytes the SDK reads; a gzip body could expand past it.
                headers={"Accept-Encoding": "identity"},
                client_args={"event_hooks": {"response": [_reject_oversized]}},
            ),
        )
        self._config = config

    @property
    def client(self) -> genai.Client:
        """Get the underlying google-genai Client."""
        return self._client

    @property
    def output_dir(self) -> Path:
        """Get the output directory for generated files."""
        return self._config.output_dir

    async def generate_content(
        self,
        model: str,
        contents: Any,
        config: types.GenerateContentConfig | None = None,
    ) -> Any:
        """Generate content with error handling.

        Args:
            model: Model name to use.
            contents: Content to send to the model.
            config: Optional generation config.

        Returns:
            The generate content response.

        Raises:
            GeminiApiError: On API errors.
            RateLimitError: On rate limiting.
        """
        try:
            return await asyncio.to_thread(
                self._client.models.generate_content,
                model=model,
                contents=contents,
                config=config,
            )
        except Exception as e:
            _handle_genai_error(e)

    async def generate_images(
        self,
        model: str,
        prompt: str,
        config: types.GenerateImagesConfig | None = None,
    ) -> Any:
        """Generate images via Imagen with error handling.

        Args:
            model: Imagen model name.
            prompt: Image generation prompt.
            config: Optional image generation config.

        Returns:
            The generate images response.

        Raises:
            GeminiApiError: On API errors.
            RateLimitError: On rate limiting.
        """
        try:
            return await asyncio.to_thread(
                self._client.models.generate_images,
                model=model,
                prompt=prompt,
                config=config,
            )
        except Exception as e:
            _handle_genai_error(e)

    def create_chat(
        self,
        model: str,
        config: types.GenerateContentConfig | None = None,
    ) -> Any:
        """Create a chat session for multi-turn interactions.

        Args:
            model: Model name to use.
            config: Optional generation config.

        Returns:
            A chat session object.
        """
        return self._client.chats.create(model=model, config=config)

    async def upload_file(self, file_path: str) -> Any:
        """Upload a file to Gemini for use in generation.

        Args:
            file_path: Path to the file to upload.

        Returns:
            The uploaded file reference.

        Raises:
            GeminiApiError: On upload errors.
        """
        try:
            return await asyncio.to_thread(self._client.files.upload, file=file_path)
        except Exception as e:
            _handle_genai_error(e)

    async def count_tokens(self, model: str, contents: Any) -> Any:
        """Count tokens in content.

        Args:
            model: Model to count tokens for.
            contents: Content to count.

        Returns:
            Token count response.
        """
        try:
            return await asyncio.to_thread(
                self._client.models.count_tokens,
                model=model,
                contents=contents,
            )
        except Exception as e:
            _handle_genai_error(e)

    async def create_cache(self, model: str, config: types.CreateCachedContentConfig) -> Any:
        """Create a content cache.

        Args:
            model: Model the cache is bound to.
            config: The contents to cache, plus display name, TTL and
                system instruction.

        Returns:
            The SDK's CachedContent; its ``name`` identifies the cache.

        Raises:
            GeminiApiError: On API errors.
        """
        try:
            return await asyncio.to_thread(self._client.caches.create, model=model, config=config)
        except Exception as e:
            _handle_genai_error(e)

    async def list_caches(self) -> list[Any]:
        """List content caches, paging through the SDK iterator in the worker.

        Raises:
            GeminiApiError: On API errors.
        """
        try:
            return await asyncio.to_thread(lambda: list(self._client.caches.list()))
        except Exception as e:
            _handle_genai_error(e)
            raise

    async def delete_cache(self, name: str) -> None:
        """Delete a content cache.

        Raises:
            GeminiApiError: On API errors.
        """
        try:
            await asyncio.to_thread(self._client.caches.delete, name=name)
        except Exception as e:
            _handle_genai_error(e)

    async def generate_videos(self, model: str, prompt: str) -> Any:
        """Start a Veo video generation operation.

        Raises:
            GeminiApiError: On API errors.
        """
        try:
            return await asyncio.to_thread(
                self._client.models.generate_videos, model=model, prompt=prompt
            )
        except Exception as e:
            _handle_genai_error(e)

    async def get_videos_operation(self, name: str) -> Any:
        """Poll a video generation operation.

        Raises:
            GeminiApiError: On API errors.
        """
        operations: Any = self._client.operations
        try:
            return await asyncio.to_thread(operations.get_videos_operation, name=name)
        except Exception as e:
            _handle_genai_error(e)


def _handle_genai_error(e: Exception) -> None:
    """Convert google-genai exceptions to UserError subclasses.

    Args:
        e: The exception from the google-genai SDK.

    Raises:
        RateLimitError: On rate limiting (429).
        GeminiApiError: On all other API errors.
    """
    error_msg = str(e)
    if "429" in error_msg or "quota" in error_msg.lower():
        raise RateLimitError(f"Rate limit exceeded: {error_msg}") from e
    raise GeminiApiError(error_msg) from e


_client: GeminiClient | None = None


def get_client() -> GeminiClient:
    """Get the global Gemini client instance.

    Returns:
        The global GeminiClient instance.
    """
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client
