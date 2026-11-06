"""Secure configuration handling.

This module handles all configuration including the sensitive API key.
The key is stored as a SecretStr to prevent accidental logging.
"""

import logging
import os
from pathlib import Path

from pydantic import SecretStr

from .errors import ConfigurationError, register_secret

logger = logging.getLogger(__name__)


class Config:
    """Secure configuration handling.

    The API key is stored as a SecretStr and should only be accessed
    via the api_key property when actually needed for API calls.
    """

    def __init__(self) -> None:
        """Initialize configuration from environment variables.

        Raises:
            ConfigurationError: If required environment variables are missing.
        """
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            key_file = os.environ.get("GEMINI_API_KEY_FILE")
            if not key_file:
                raise ConfigurationError(
                    "GEMINI_API_KEY or GEMINI_API_KEY_FILE environment variable "
                    "required. Get a key at https://aistudio.google.com/apikey"
                )
            api_key = self._read_key_file(Path(key_file).expanduser())

        self._api_key = SecretStr(api_key)
        register_secret(api_key)  # redact from GeminiApiError messages

        self._output_dir = Path(
            os.environ.get(
                "GEMINI_OUTPUT_DIR",
                "~/.config/mcp-gemini-crunchtools/output",
            )
        ).expanduser()
        self._output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Configuration loaded successfully")

    @staticmethod
    def _read_key_file(path: Path) -> str:
        """Read the API key from a file; errors name the path, never the contents."""
        try:
            api_key = path.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeDecodeError) as exc:
            raise ConfigurationError(
                f"Cannot read GEMINI_API_KEY_FILE at {path} "
                "(set GEMINI_API_KEY or point GEMINI_API_KEY_FILE at a readable file)"
            ) from exc
        if not api_key:
            raise ConfigurationError(
                f"GEMINI_API_KEY_FILE at {path} is empty "
                "(set GEMINI_API_KEY or point GEMINI_API_KEY_FILE at a file containing the key)"
            )
        return api_key

    @property
    def api_key(self) -> str:
        """Get API key value for API calls.

        Use sparingly - only when making actual API calls.
        """
        return self._api_key.get_secret_value()

    @property
    def output_dir(self) -> Path:
        """Output directory for generated files."""
        return self._output_dir

    def __repr__(self) -> str:
        """Safe repr that never exposes the API key."""
        return f"Config(api_key=***, output_dir={self._output_dir})"

    def __str__(self) -> str:
        """Safe str that never exposes the API key."""
        return self.__repr__()


_config: Config | None = None


def get_config() -> Config:
    """Get the global configuration instance.

    This function lazily initializes the configuration on first call.
    Subsequent calls return the same instance.

    Returns:
        The global Config instance.

    Raises:
        ConfigurationError: If configuration is invalid.
    """
    global _config
    if _config is None:
        _config = Config()
    return _config
