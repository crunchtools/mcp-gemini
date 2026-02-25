"""MCP Gemini CrunchTools - MCP server for Google Gemini AI.

A security-focused MCP server for Google Gemini AI capabilities
including text, image, video, research, and more.

Usage:
    # Run directly
    mcp-gemini-crunchtools

    # Or with Python module
    python -m mcp_gemini_crunchtools

    # With uvx
    uvx mcp-gemini-crunchtools

Environment Variables:
    GEMINI_API_KEY: Required. Google Gemini API key.
    GEMINI_OUTPUT_DIR: Optional. Directory for generated files.

Example with Claude Code:
    claude mcp add mcp-gemini-crunchtools \\
        --env GEMINI_API_KEY=your_key_here \\
        -- uvx mcp-gemini-crunchtools
"""

import argparse
import logging
import sys

from .server import mcp

__version__ = "0.1.0"
__all__ = ["main", "mcp"]


def main() -> None:
    """Main entry point for the MCP server.

    CRITICAL: Forces all logging to stderr to prevent corruption
    of the MCP stdio JSON-RPC transport on stdout.
    """
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.WARNING,
        format="%(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(description="MCP server for Google Gemini AI")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to for HTTP transports (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to for HTTP transports (default: 8000)",
    )
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport=args.transport, host=args.host, port=args.port)
