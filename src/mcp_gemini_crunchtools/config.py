"""Secure configuration handling.

This module handles all configuration including the sensitive API key.
The key is stored as a SecretStr to prevent accidental logging.
"""

import logging
import os
from pathlib import Path

from pydantic import SecretStr

from .errors import ConfigurationError

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
            raise ConfigurationError(
                "GEMINI_API_KEY environment variable required. "
                "Get one at https://aistudio.google.com/apikey"
            )

        self._api_key = SecretStr(api_key)

        self._output_dir = Path(
            os.environ.get(
                "GEMINI_OUTPUT_DIR",
                "~/.config/mcp-gemini-crunchtools/output",
            )
        ).expanduser()
        self._output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Configuration loaded successfully")

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
