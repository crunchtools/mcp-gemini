"""Basic import test to verify package structure."""


def test_imports() -> None:
    """Test that core modules can be imported."""
    from mcp_gemini_crunchtools import __version__
    from mcp_gemini_crunchtools.client import GeminiClient

    assert __version__
    assert GeminiClient


def test_server_import() -> None:
    """Test that server module can be imported."""
    from mcp_gemini_crunchtools import server

    assert server
    assert hasattr(server, "mcp")
