"""Google Gemini API client wrapper.

This module provides a shared client instance for the google-genai SDK.
All tools should use get_client() to access the Gemini API.
"""

import logging
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types

from .config import get_config
from .errors import GeminiApiError, RateLimitError

logger = logging.getLogger(__name__)


class GeminiClient:
    """Wrapper around google-genai Client.

    Provides a single shared client instance and convenience methods
    for common Gemini operations with proper error handling.
    """

    def __init__(self) -> None:
        """Initialize the Gemini client."""
        config = get_config()
        self._client = genai.Client(api_key=config.api_key)
        self._config = config

    @property
    def client(self) -> genai.Client:
        """Get the underlying google-genai Client."""
        return self._client

    @property
    def output_dir(self) -> Path:
        """Get the output directory for generated files."""
        return self._config.output_dir

    def generate_content(
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
            return self._client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
        except Exception as e:
            _handle_genai_error(e)

    def generate_images(
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
            return self._client.models.generate_images(
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

    def upload_file(self, file_path: str) -> Any:
        """Upload a file to Gemini for use in generation.

        Args:
            file_path: Path to the file to upload.

        Returns:
            The uploaded file reference.

        Raises:
            GeminiApiError: On upload errors.
        """
        try:
            return self._client.files.upload(file=file_path)
        except Exception as e:
            _handle_genai_error(e)

    def count_tokens(self, model: str, contents: Any) -> Any:
        """Count tokens in content.

        Args:
            model: Model to count tokens for.
            contents: Content to count.

        Returns:
            Token count response.
        """
        try:
            return self._client.models.count_tokens(
                model=model,
                contents=contents,
            )
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


# Global client instance
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
