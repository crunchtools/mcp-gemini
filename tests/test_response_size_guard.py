"""Tests for the response-size guard's HTTP-library handling.

These exercise the guard against real response objects, which no other test in
this suite does: the rest mock the SDK, so the hook and its stream wrapper were
never executed and a break in them could not fail CI. That is how google-genai
3.0 -- which swapped its required HTTP library from ``httpx`` to ``httpx2`` --
shipped to production with every tool returning
"Attempted to call a sync close on an async stream".

The guard is parametrised over every flavour installed, so whichever one the SDK
requires is the one under test.
"""

import importlib

import pytest

from mcp_gemini_crunchtools import client as client_module
from mcp_gemini_crunchtools.client import _reject_oversized
from mcp_gemini_crunchtools.errors import GeminiApiError

FLAVOURS = ["httpx", "httpx2"]


def _flavour(name: str):
    """The HTTP library ``name``, or skip if this environment lacks it."""
    return pytest.importorskip(name, reason=f"{name} is not installed")


@pytest.mark.parametrize("name", FLAVOURS)
class TestGuardSurvivesEveryHttpxFlavour:
    """The wrapper must satisfy the isinstance check of the library that made it."""

    def test_response_closes_after_the_guard_wraps_it(self, name: str) -> None:
        flavour = _flavour(name)
        response = flavour.Response(200, content=b"body")

        _reject_oversized(response)
        response.read()

        # close() is where the library checks the stream against its OWN
        # SyncByteStream. A wrapper built on the other flavour's base raises
        # RuntimeError here, which is the production failure this guards.
        response.close()
        assert response.is_closed

    def test_the_wrapper_is_the_flavours_own_stream_type(self, name: str) -> None:
        flavour = _flavour(name)
        response = flavour.Response(200, content=b"body")

        _reject_oversized(response)

        assert isinstance(response.stream, flavour.SyncByteStream)

    def test_body_still_reaches_the_caller_intact(self, name: str) -> None:
        flavour = _flavour(name)
        response = flavour.Response(200, content=b"the body, unchanged")

        _reject_oversized(response)

        assert response.read() == b"the body, unchanged"

    def test_a_declared_oversize_body_is_refused_before_it_is_read(self, name: str) -> None:
        flavour = _flavour(name)
        too_big = client_module.MAX_RESPONSE_SIZE_BYTES + 1
        response = flavour.Response(200, headers={"content-length": str(too_big)}, content=b"")

        with pytest.raises(GeminiApiError, match="too large"):
            _reject_oversized(response)

    def test_an_undeclared_oversize_body_is_refused_while_it_is_read(
        self, name: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """No Content-Length is the case the stream wrapper exists for.

        An iterator body is how that happens: the library cannot know the
        length in advance, so it sends no Content-Length and the header check
        above has nothing to act on.
        """
        flavour = _flavour(name)
        monkeypatch.setattr(client_module, "MAX_RESPONSE_SIZE_BYTES", 8)
        response = flavour.Response(200, content=iter([b"01234", b"56789"]))
        assert "content-length" not in response.headers

        _reject_oversized(response)

        with pytest.raises(GeminiApiError, match="too large"):
            response.read()


def test_every_flavour_gets_its_own_cached_wrapper_class() -> None:
    """One cache serves both libraries; a shared class would break one of them."""
    installed = [n for n in FLAVOURS if importlib.util.find_spec(n) is not None]
    if len(installed) < 2:
        pytest.skip("needs more than one httpx flavour installed to be meaningful")

    classes = []
    for name in installed:
        flavour = importlib.import_module(name)
        response = flavour.Response(200, content=b"body")
        _reject_oversized(response)
        classes.append(type(response.stream))

    assert len({id(c) for c in classes}) == len(installed)
    for name, cls in zip(installed, classes, strict=True):
        assert issubclass(cls, importlib.import_module(name).SyncByteStream)


def test_the_wrapper_class_is_built_once_per_flavour() -> None:
    """Rebuilding the class per response would make every response a new type."""
    flavour = _flavour("httpx")

    seen = set()
    for _ in range(3):
        response = flavour.Response(200, content=b"body")
        _reject_oversized(response)
        seen.add(type(response.stream))

    assert len(seen) == 1


class TestAnHttpLibraryWithNoStreamBaseIsRefused:
    """A body that cannot be counted is refused, not passed through uncapped.

    The constitution caps responses at 100MB. Without the library's own
    ``SyncByteStream`` there is no way to count a body that arrives with no
    declared size, so the call fails rather than silently losing the cap.
    """

    def test_a_body_that_cannot_be_bounded_raises(self) -> None:
        flavour = _flavour("httpx")
        response = flavour.Response(200, content=iter([b"body"]))

        with pytest.MonkeyPatch.context() as patched:
            patched.delattr(flavour, "SyncByteStream")
            with pytest.raises(GeminiApiError, match="no SyncByteStream"):
                _reject_oversized(response)

    def test_a_declared_oversize_body_is_refused_first(self) -> None:
        """The header check runs before the wrapper, so it is unaffected."""
        flavour = _flavour("httpx")
        too_big = client_module.MAX_RESPONSE_SIZE_BYTES + 1
        response = flavour.Response(200, headers={"content-length": str(too_big)}, content=b"")

        with pytest.MonkeyPatch.context() as patched:
            patched.delattr(flavour, "SyncByteStream")
            with pytest.raises(GeminiApiError, match="too large"):
                _reject_oversized(response)
