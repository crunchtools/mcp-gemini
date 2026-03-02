"""Shared test fixtures for mcp-gemini-crunchtools.

Provides singleton reset and mock helpers for google-genai SDK.
"""

import os
from typing import Any
from unittest.mock import MagicMock

import pytest

os.environ.setdefault("GEMINI_API_KEY", "test-key-for-pytest")


@pytest.fixture(autouse=True)
def _reset_client_singleton() -> None:
    """Reset global singletons between tests to prevent state leakage."""
    from mcp_gemini_crunchtools import client, config

    client._client = None
    config._config = None

    from mcp_gemini_crunchtools.tools.image_edit import _sessions

    _sessions.clear()

    from mcp_gemini_crunchtools.tools.research import _research_ops

    _research_ops.clear()


def mock_generate_response(text: str = "mock response") -> MagicMock:
    """Create a mock generate_content response with text.

    Args:
        text: The text content for the response.

    Returns:
        A MagicMock mimicking a Gemini generate_content response.
    """
    part = MagicMock()
    part.text = text
    part.inline_data = None

    candidate = MagicMock()
    candidate.content.parts = [part]

    response = MagicMock()
    response.text = text
    response.candidates = [candidate]
    return response


def mock_image_response(
    text: str = "image description",
    image_bytes: bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100,
    mime_type: str = "image/png",
) -> MagicMock:
    """Create a mock response containing both text and image data.

    Args:
        text: Text content for the response.
        image_bytes: Raw image bytes.
        mime_type: MIME type of the image.

    Returns:
        A MagicMock with text and inline_data parts.
    """
    text_part = MagicMock()
    text_part.text = text
    text_part.inline_data = None

    image_part = MagicMock()
    image_part.text = None
    image_part.inline_data = MagicMock()
    image_part.inline_data.data = image_bytes
    image_part.inline_data.mime_type = mime_type

    candidate = MagicMock()
    candidate.content.parts = [text_part, image_part]

    response = MagicMock()
    response.text = text
    response.candidates = [candidate]
    return response


def mock_audio_response(
    audio_bytes: bytes = b"fake-audio-data",
) -> MagicMock:
    """Create a mock response containing audio data.

    Args:
        audio_bytes: Raw audio bytes.

    Returns:
        A MagicMock with inline_data audio part.
    """
    audio_part = MagicMock()
    audio_part.text = None
    audio_part.inline_data = MagicMock()
    audio_part.inline_data.data = audio_bytes

    candidate = MagicMock()
    candidate.content.parts = [audio_part]

    response = MagicMock()
    response.text = None
    response.candidates = [candidate]
    return response


def mock_gemini_client(**overrides: Any) -> MagicMock:
    """Create a fully mocked GeminiClient.

    Args:
        **overrides: Override specific methods or attributes on the mock client.

    Returns:
        A MagicMock mimicking GeminiClient with default behaviors.
    """
    import tempfile
    from pathlib import Path

    mock_client = MagicMock()
    mock_client.generate_content.return_value = mock_generate_response()
    mock_client.generate_images.return_value = None
    mock_client.create_chat.return_value = MagicMock()
    mock_client.upload_file.return_value = MagicMock()
    mock_token_count = 100
    mock_client.count_tokens.return_value = MagicMock(total_tokens=mock_token_count)
    mock_client.output_dir = Path(tempfile.mkdtemp())

    mock_client.client = MagicMock()
    mock_client.client.caches.create.return_value = MagicMock(name="test-cache")
    mock_client.client.caches.list.return_value = []
    mock_client.client.caches.delete.return_value = None
    mock_client.client.models.generate_videos.return_value = MagicMock(name="op-123")

    for attr, value in overrides.items():
        setattr(mock_client, attr, value)

    return mock_client
