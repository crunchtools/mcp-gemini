"""Error safety tests for mcp-gemini-crunchtools.

Verifies that sensitive data (API keys) is never leaked through
error messages, config repr, or exception strings.
"""

import os
from unittest.mock import patch

import pytest

from mcp_gemini_crunchtools.errors import GeminiApiError


class TestGeminiApiErrorSanitization:
    """GeminiApiError must scrub API keys from messages."""

    def test_api_key_scrubbed_from_message(self) -> None:
        test_key = "AIzaSyTestKey12345"
        with patch.dict(os.environ, {"GEMINI_API_KEY": test_key}):
            err = GeminiApiError(f"Request failed with key {test_key} in URL")
            assert test_key not in str(err)
            assert "***" in str(err)

    def test_message_without_key_unchanged(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": "AIzaSyTest"}):
            err = GeminiApiError("Generic API failure")
            assert "Generic API failure" in str(err)

    def test_empty_key_no_crash(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            err = GeminiApiError("Some error")
            assert "Some error" in str(err)


class TestConfigSafety:
    """Config must never expose the API key in repr or str."""

    def test_repr_hides_key(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": "AIzaSySecretKey999"}):
            from mcp_gemini_crunchtools.config import Config

            cfg = Config()
            assert "AIzaSySecretKey999" not in repr(cfg)
            assert "***" in repr(cfg)

    def test_str_hides_key(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": "AIzaSySecretKey999"}):
            from mcp_gemini_crunchtools.config import Config

            cfg = Config()
            assert "AIzaSySecretKey999" not in str(cfg)

    def test_missing_key_raises_configuration_error(self) -> None:
        from mcp_gemini_crunchtools.config import Config
        from mcp_gemini_crunchtools.errors import ConfigurationError

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("GEMINI_API_KEY", None)
            with pytest.raises(ConfigurationError, match="GEMINI_API_KEY"):
                Config()

    def test_api_key_accessible_via_property(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": "AIzaSyPropertyTest"}):
            from mcp_gemini_crunchtools.config import Config

            cfg = Config()
            assert cfg.api_key == "AIzaSyPropertyTest"
