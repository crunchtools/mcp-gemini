"""A slow Gemini call must not block the event loop.

The SDK is synchronous. Called inline from an async tool, one slow
generation froze the server for every other caller, down to ``initialize``.
"""

import asyncio
import gc
import threading
import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from mcp_gemini_crunchtools.client import (
    HTTP_TIMEOUT_MS,
    MAX_RESPONSE_SIZE_BYTES,
    GeminiClient,
    _reject_oversized,
)
from mcp_gemini_crunchtools.errors import GeminiApiError

SDK_PATHS = {
    "generate_content": ("models", "generate_content"),
    "generate_images": ("models", "generate_images"),
    "count_tokens": ("models", "count_tokens"),
    "upload_file": ("files", "upload"),
    "create_cache": ("caches", "create"),
    "list_caches": ("caches", "list"),
    "delete_cache": ("caches", "delete"),
    "generate_videos": ("models", "generate_videos"),
    "get_videos_operation": ("operations", "get_videos_operation"),
}
CALL_ARGS: dict[str, dict[str, Any]] = {
    "generate_content": {"model": "m", "contents": ["x"], "config": None},
    "generate_images": {"model": "m", "prompt": "x", "config": None},
    "count_tokens": {"model": "m", "contents": ["x"]},
    "upload_file": {"file_path": "doc.pdf"},
    "create_cache": {"model": "m", "config": None},
    "list_caches": {},
    "delete_cache": {"name": "caches/x"},
    "generate_videos": {"model": "m", "prompt": "x"},
    "get_videos_operation": {"name": "operations/x"},
}

# Where a wrapper renames an argument on its way to the SDK.
SDK_KWARGS: dict[str, dict[str, Any]] = {"upload_file": {"file": "doc.pdf"}}


@pytest.mark.parametrize("method", sorted(SDK_PATHS))
async def test_slow_sdk_call_leaves_loop_responsive(method: str) -> None:
    client = GeminiClient()
    calls: list[dict[str, Any]] = []
    result = ["done"]

    def slow_sdk(**kwargs: Any) -> list[str]:
        calls.append(kwargs)
        time.sleep(0.5)
        return result

    group, name = SDK_PATHS[method]
    setattr(getattr(client.client, group), name, slow_sdk)

    started = time.monotonic()
    call = asyncio.create_task(getattr(client, method)(**CALL_ARGS[method]))
    await asyncio.sleep(0.05)
    ticked_at = time.monotonic() - started

    returned = await call
    assert ticked_at < 0.3
    assert calls == [SDK_KWARGS.get(method, CALL_ARGS[method])]
    if method != "delete_cache":
        assert returned == result


def test_sdk_client_carries_timeout_and_size_limit() -> None:
    options = GeminiClient().client._api_client._http_options
    assert options.timeout == HTTP_TIMEOUT_MS
    assert _reject_oversized in options.client_args["event_hooks"]["response"]
    # The size limit counts wire bytes, so it only bounds what the SDK reads
    # while responses arrive uncompressed.
    assert options.headers["Accept-Encoding"] == "identity"


def test_oversized_response_is_refused() -> None:
    big = httpx.Response(200, headers={"content-length": str(MAX_RESPONSE_SIZE_BYTES + 1)})
    with pytest.raises(GeminiApiError):
        _reject_oversized(big)
    _reject_oversized(httpx.Response(200, headers={"content-length": "10"}))


def test_oversized_body_without_content_length_is_refused() -> None:
    chunk = b"x" * (1024 * 1024)
    chunks = (chunk for _ in range(MAX_RESPONSE_SIZE_BYTES // len(chunk) + 2))
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
    client.create_cache.assert_not_called()


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


async def test_list_caches_drains_the_paging_iterator() -> None:
    client = GeminiClient()
    client.client.caches.list = lambda: (f"cache-{n}" for n in range(3))
    assert await client.list_caches() == ["cache-0", "cache-1", "cache-2"]


async def test_abandoned_turn_that_fails_releases_the_session() -> None:
    from mcp_gemini_crunchtools.tools import image_edit

    running = threading.Event()
    release = threading.Event()

    def send_message(contents: list[str]) -> MagicMock:
        if contents == ["a"]:
            running.set()
            release.wait(5)
            raise RuntimeError("upstream failed")
        return MagicMock(candidates=[])

    lock = asyncio.Lock()
    image_edit._sessions["edit-z"] = {
        "chat": MagicMock(send_message=send_message),
        "lock": lock,
        "last_active": time.time(),
        "turn_count": 1,
        "images": [],
    }
    unretrieved: list[Any] = []
    asyncio.get_running_loop().set_exception_handler(lambda _, ctx: unretrieved.append(ctx))

    first = asyncio.create_task(image_edit.gemini_continue_image_edit("edit-z", "a"))
    await asyncio.to_thread(running.wait, 5)
    first.cancel()
    release.set()

    await image_edit.gemini_continue_image_edit("edit-z", "b")
    assert not lock.locked()
    gc.collect()
    await asyncio.sleep(0)
    assert unretrieved == []


async def test_failed_turn_reaches_its_awaiter() -> None:
    from mcp_gemini_crunchtools.tools import image_edit

    def send_message(_: list[str]) -> MagicMock:
        raise RuntimeError("upstream failed")

    lock = asyncio.Lock()
    image_edit._sessions["edit-w"] = {
        "chat": MagicMock(send_message=send_message),
        "lock": lock,
        "last_active": time.time(),
        "turn_count": 1,
        "images": [],
    }
    with pytest.raises(GeminiApiError, match="upstream failed"):
        await image_edit.gemini_continue_image_edit("edit-w", "a")
    assert not lock.locked()


async def test_create_cache_puts_contents_in_the_config() -> None:
    from mcp_gemini_crunchtools.tools.cache import gemini_create_cache

    client = MagicMock(create_cache=AsyncMock(return_value=MagicMock()))
    with patch("mcp_gemini_crunchtools.tools.cache.get_client", return_value=client):
        await gemini_create_cache(content="cache me", system_instruction="be brief")
    config = client.create_cache.await_args.kwargs["config"]
    assert config.contents
    assert config.system_instruction
