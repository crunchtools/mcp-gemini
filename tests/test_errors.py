"""Error safety tests for mcp-gemini-crunchtools.

Verifies that sensitive data (API keys) is never leaked through
error messages, config repr, or exception strings.
"""

import os
from pathlib import Path
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

    def test_key_from_file_only(self, tmp_path: Path) -> None:
        from mcp_gemini_crunchtools.config import Config

        key_file = tmp_path / "api-key"
        key_file.write_text("AIzaSyFileKey\n")
        with patch.dict(os.environ, {"GEMINI_API_KEY_FILE": str(key_file)}, clear=True):
            assert Config().api_key == "AIzaSyFileKey"

    def test_env_wins_over_file(self, tmp_path: Path) -> None:
        from mcp_gemini_crunchtools.config import Config

        key_file = tmp_path / "api-key"
        key_file.write_text("AIzaSyFileKey")
        env = {"GEMINI_API_KEY": "AIzaSyEnvKey", "GEMINI_API_KEY_FILE": str(key_file)}
        with patch.dict(os.environ, env, clear=True):
            assert Config().api_key == "AIzaSyEnvKey"

    def test_neither_set_names_both_options(self) -> None:
        from mcp_gemini_crunchtools.config import Config
        from mcp_gemini_crunchtools.errors import ConfigurationError

        with patch.dict(os.environ, {}, clear=True), pytest.raises(ConfigurationError) as exc:
            Config()
        assert "GEMINI_API_KEY_FILE" in str(exc.value)
        assert "GEMINI_API_KEY" in str(exc.value)

    def test_missing_and_empty_file_raise_without_contents(self, tmp_path: Path) -> None:
        from mcp_gemini_crunchtools.config import Config
        from mcp_gemini_crunchtools.errors import ConfigurationError

        missing = tmp_path / "nope"
        with (
            patch.dict(os.environ, {"GEMINI_API_KEY_FILE": str(missing)}, clear=True),
            pytest.raises(ConfigurationError, match="nope"),
        ):
            Config()
        empty = tmp_path / "empty"
        empty.write_text("  \n")
        with (
            patch.dict(os.environ, {"GEMINI_API_KEY_FILE": str(empty)}, clear=True),
            pytest.raises(ConfigurationError, match="empty"),
        ):
            Config()

    def test_file_sourced_key_redacted_from_api_error(self, tmp_path: Path) -> None:
        from mcp_gemini_crunchtools.config import Config

        file_key = "AIzaSyFileKey777"
        key_file = tmp_path / "api-key"
        key_file.write_text(file_key)
        with patch.dict(os.environ, {"GEMINI_API_KEY_FILE": str(key_file)}, clear=True):
            Config()
        with patch.dict(os.environ, {}, clear=True):
            err = GeminiApiError(f"bad request ?key={file_key}")
        assert file_key not in str(err)
        assert "***" in str(err)

    def test_api_key_accessible_via_property(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": "AIzaSyPropertyTest"}):
            from mcp_gemini_crunchtools.config import Config

            cfg = Config()
            assert cfg.api_key == "AIzaSyPropertyTest"
