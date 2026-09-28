"""A slow Gemini call must not block the event loop.

The SDK is synchronous. Called inline from an async tool, one slow
generation froze the server for every other caller, down to ``initialize``.
"""

import asyncio
import threading
import time
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest

from mcp_gemini_crunchtools.client import (
    HTTP_TIMEOUT_MS,
    MAX_RESPONSE_SIZE,
    GeminiClient,
    _reject_oversized,
)
from mcp_gemini_crunchtools.errors import GeminiApiError

SDK_PATHS = {
    "generate_content": ("models", "generate_content"),
    "generate_images": ("models", "generate_images"),
    "count_tokens": ("models", "count_tokens"),
    "upload_file": ("files", "upload"),
}
CALL_ARGS: dict[str, dict[str, Any]] = {
    "generate_content": {"model": "m", "contents": ["x"]},
    "generate_images": {"model": "m", "prompt": "x"},
    "count_tokens": {"model": "m", "contents": ["x"]},
    "upload_file": {"file_path": "doc.pdf"},
}


@pytest.mark.parametrize("method", sorted(SDK_PATHS))
async def test_slow_sdk_call_leaves_loop_responsive(method: str) -> None:
    client = GeminiClient()
    received: dict[str, Any] = {}

    def slow_sdk(**kwargs: Any) -> str:
        received.update(kwargs)
        time.sleep(0.5)
        return "done"

    group, name = SDK_PATHS[method]
    setattr(getattr(client.client, group), name, slow_sdk)

    started = time.monotonic()
    call = asyncio.create_task(getattr(client, method)(**CALL_ARGS[method]))
    await asyncio.sleep(0.05)
    ticked_at = time.monotonic() - started

    assert await call == "done"
    assert ticked_at < 0.3
    assert received


def test_sdk_client_carries_timeout_and_size_limit() -> None:
    options = GeminiClient().client._api_client._http_options
    assert options.timeout == HTTP_TIMEOUT_MS
    assert _reject_oversized in options.client_args["event_hooks"]["response"]


def test_oversized_response_is_refused() -> None:
    big = httpx.Response(200, headers={"content-length": str(MAX_RESPONSE_SIZE + 1)})
    with pytest.raises(GeminiApiError):
        _reject_oversized(big)
    _reject_oversized(httpx.Response(200, headers={"content-length": "10"}))


def test_oversized_body_without_content_length_is_refused() -> None:
    chunk = b"x" * (1024 * 1024)
    chunks = (chunk for _ in range(MAX_RESPONSE_SIZE // len(chunk) + 2))
    with (
        httpx.Client(
            transport=httpx.MockTransport(lambda _: httpx.Response(200, content=chunks)),
            event_hooks={"response": [_reject_oversized]},
        ) as http,
        pytest.raises(GeminiApiError),
    ):
        http.get("https://example.invalid/")


async def test_oversized_cache_upload_is_refused_before_upload(tmp_path: Any) -> None:
    from mcp_gemini_crunchtools.models import MAX_DOCUMENT_SIZE_BYTES
    from mcp_gemini_crunchtools.tools.cache import gemini_create_cache

    big = tmp_path / "big.pdf"
    big.write_bytes(b"x")
    client = MagicMock()
    with (
        patch("mcp_gemini_crunchtools.tools.cache.get_client", return_value=client),
        patch(
            "mcp_gemini_crunchtools.models.os.path.getsize",
            return_value=MAX_DOCUMENT_SIZE_BYTES + 1,
        ),
        pytest.raises(ValueError, match="too large"),
    ):
        await gemini_create_cache(display_name="d", file_path=str(big))
    client.upload_file.assert_not_called()
    client.client.caches.create.assert_not_called()


async def test_turns_in_one_edit_session_do_not_overlap() -> None:
    from mcp_gemini_crunchtools.tools import image_edit

    active = 0
    peak = 0

    def send_message(_: Any) -> MagicMock:
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        time.sleep(0.1)
        active -= 1
        return MagicMock(candidates=[])

    chat = MagicMock(send_message=send_message)
    image_edit._sessions["edit-x"] = {
        "chat": chat,
        "lock": asyncio.Lock(),
        "last_active": time.time(),
        "turn_count": 1,
        "images": [],
    }

    await asyncio.gather(
        image_edit.gemini_continue_image_edit("edit-x", "a"),
        image_edit.gemini_continue_image_edit("edit-x", "b"),
    )
    assert peak == 1


async def test_cancelled_turn_holds_the_session_until_its_worker_finishes() -> None:
    from mcp_gemini_crunchtools.tools import image_edit

    first_running = threading.Event()
    release_first = threading.Event()
    order: list[str] = []

    def send_message(contents: list[str]) -> MagicMock:
        if contents == ["a"]:
            first_running.set()
            release_first.wait(5)
        order.append(contents[0])
        return MagicMock(candidates=[])

    image_edit._sessions["edit-y"] = {
        "chat": MagicMock(send_message=send_message),
        "lock": asyncio.Lock(),
        "last_active": time.time(),
        "turn_count": 1,
        "images": [],
    }

    first = asyncio.create_task(image_edit.gemini_continue_image_edit("edit-y", "a"))
    await asyncio.to_thread(first_running.wait, 5)
    first.cancel()
    second = asyncio.create_task(image_edit.gemini_continue_image_edit("edit-y", "b"))
    await asyncio.sleep(0.1)
    assert order == []

    release_first.set()
    await second
    assert order == ["a", "b"]
    assert first.cancelled()
