# MCP Gemini CrunchTools

A secure MCP (Model Context Protocol) server for Google Gemini AI - text, image, video, research, and more.

## Overview

This MCP server is designed to be:

- **Secure by default** - Comprehensive threat modeling, input validation, and API key protection
- **No third-party services** - Runs locally via stdio, your API key never leaves your machine
- **Cross-platform** - Works on Linux, macOS, and Windows
- **Automatically updated** - GitHub Actions monitor for CVEs and update dependencies
- **Containerized** - Available at `quay.io/crunchtools/mcp-gemini` built on [Hummingbird Python](https://quay.io/repository/hummingbird/python) base image

## Naming Convention

| Component | Name |
|-----------|------|
| GitHub repo | [crunchtools/mcp-gemini](https://github.com/crunchtools/mcp-gemini) |
| Container | `quay.io/crunchtools/mcp-gemini` |
| Python package (PyPI) | `mcp-gemini-crunchtools` |
| CLI command | `mcp-gemini-crunchtools` |
| Module import | `mcp_gemini_crunchtools` |

## Why Hummingbird?

The container image is built on the [Hummingbird Python base image](https://quay.io/repository/hummingbird/python) from [Project Hummingbird](https://github.com/hummingbird-project), which provides:

- **Minimal CVE exposure** - Hummingbird images are built with a minimal package set, dramatically reducing the attack surface compared to general-purpose images
- **Regular updates** - Security patches are applied promptly, keeping CVE counts low
- **Optimized for Python** - Pre-configured Python environment with uv package manager for fast, reproducible builds
- **Production-ready** - Designed for production workloads with proper signal handling and non-root user defaults

This means your MCP server runs in a hardened environment with fewer vulnerabilities than typical Python container images.

## Features

### Query Tools (5 tools)
- `gemini_query` - Query Gemini with optional Google Search grounding
- `gemini_brainstorm` - Generate creative ideas on a topic
- `gemini_analyze_code` - Analyze code for security, performance, bugs
- `gemini_analyze_text` - Analyze text for sentiment, tone, content
- `gemini_summarize` - Summarize content in various formats

### Image Generation (4 tools)
- `gemini_generate_image` - Generate images from text prompts (native Gemini)
- `gemini_generate_image_with_input` - Edit/modify existing images
- `gemini_image_prompt` - Craft effective image generation prompts
- `gemini_imagen_generate` - Generate images using Google Imagen 4 models

### Image Editing (4 tools)
- `gemini_start_image_edit` - Start a multi-turn image editing session
- `gemini_continue_image_edit` - Continue editing in an active session
- `gemini_end_image_edit` - End an image editing session
- `gemini_list_image_sessions` - List all active editing sessions

### Image Analysis (1 tool)
- `gemini_analyze_image` - Analyze and describe local image files

### Search Tools (1 tool)
- `gemini_search` - Web search using Gemini with Google Search grounding

### Document Tools (3 tools)
- `gemini_analyze_document` - Analyze PDFs, DOCX, TXT, etc.
- `gemini_summarize_pdf` - Summarize PDF documents
- `gemini_extract_tables` - Extract tables from documents

### URL Tools (3 tools)
- `gemini_analyze_url` - Analyze one or more URLs
- `gemini_compare_urls` - Compare two URLs
- `gemini_extract_from_url` - Extract specific data from a URL

### Video Tools (2 tools)
- `gemini_generate_video` - Generate videos using Veo
- `gemini_check_video` - Check video generation status

### YouTube Tools (2 tools)
- `gemini_youtube` - Analyze YouTube videos
- `gemini_youtube_summary` - Summarize YouTube videos

### Voice Tools (3 tools)
- `gemini_speak` - Convert text to speech
- `gemini_dialogue` - Generate multi-voice dialogue audio
- `gemini_list_voices` - List available voices

### Research Tools (3 tools)
- `gemini_deep_research` - Perform multi-step web research
- `gemini_check_research` - Check research operation status
- `gemini_research_followup` - Ask follow-up questions

### Cache Tools (4 tools)
- `gemini_create_cache` - Create content cache for repeated queries
- `gemini_query_cache` - Query cached content
- `gemini_list_caches` - List all active caches
- `gemini_delete_cache` - Delete a cache

### Structured Output Tools (2 tools)
- `gemini_structured` - Get structured JSON output
- `gemini_extract` - Extract structured data from text

### Token Tools (1 tool)
- `gemini_count_tokens` - Count tokens in content

### Code Execution Tools (1 tool)
- `gemini_run_code` - Execute Python code via Gemini

**Total: 39 tools**

## Installation

### With uvx (Recommended)

```bash
uvx mcp-gemini-crunchtools
```

### With pip

```bash
pip install mcp-gemini-crunchtools
```

### With Container

```bash
podman run -e GEMINI_API_KEY=your_key \
    quay.io/crunchtools/mcp-gemini
```

## Configuration

### Creating a Google Gemini API Key

1. **Navigate to Google AI Studio**
   - Go to https://aistudio.google.com/apikey
   - Sign in with your Google account

2. **Create API Key**
   - Click "Get API key" or "Create API key"
   - Select a Google Cloud project or create a new one
   - Click "Create API key in new project" (or select existing project)

3. **Copy Your API Key**
   - **IMPORTANT: Copy the API key immediately** - store it securely!
   - The key starts with `AI...` (e.g., `AIzaSy...`)

### Add to Claude Code

```bash
claude mcp add mcp-gemini-crunchtools \
    --env GEMINI_API_KEY=your_api_key_here \
    -- uvx mcp-gemini-crunchtools
```

Or for the container version:

```bash
claude mcp add mcp-gemini-crunchtools \
    --env GEMINI_API_KEY=your_api_key_here \
    -- podman run -i --rm -e GEMINI_API_KEY quay.io/crunchtools/mcp-gemini
```

### Optional: Set Output Directory

For generated images, audio, and videos:

```bash
claude mcp add mcp-gemini-crunchtools \
    --env GEMINI_API_KEY=your_api_key_here \
    --env GEMINI_OUTPUT_DIR=$HOME/.config/mcp-gemini-crunchtools/output \
    -- uvx mcp-gemini-crunchtools
```

## Usage Examples

### Query with Google Search

```
User: What are the latest developments in quantum computing?
Assistant: [calls gemini_query with use_google_search=true]
```

### Generate an Image

```
User: Generate a photorealistic image of a sunset over mountains
Assistant: [calls gemini_generate_image with prompt and style]
```

### Analyze a PDF Document

```
User: Analyze this research paper at /path/to/paper.pdf
Assistant: [calls gemini_analyze_document with file_path]
```

### Summarize a YouTube Video

```
User: Summarize this YouTube video: https://youtube.com/watch?v=...
Assistant: [calls gemini_youtube_summary with url]
```

### Deep Research

```
User: Research the environmental impact of electric vehicles
Assistant: [calls gemini_deep_research then gemini_check_research]
```

### Code Analysis

```
User: Analyze this Python code for security issues
Assistant: [calls gemini_analyze_code with focus="security"]
```

## Security

This server was designed with security as a primary concern. See [SECURITY.md](SECURITY.md) for:

- Threat model and attack vectors
- Defense in depth architecture
- API key handling best practices
- Input validation rules
- Audit logging

### Key Security Features

1. **API Key Protection**
   - Stored as SecretStr (never accidentally logged)
   - Environment variable only (never in files or args)
   - Sanitized from all error messages

2. **Input Validation**
   - Pydantic models for all inputs
   - File path validation
   - URL validation
   - Strict format validation

3. **API Hardening**
   - Hardcoded API base URL (prevents SSRF)
   - TLS certificate validation
   - Request timeouts
   - Response size limits

4. **Automated CVE Scanning**
   - GitHub Actions scan dependencies weekly
   - Automatic PRs for security updates
   - Dependabot alerts enabled

## Development

### Setup

```bash
git clone https://github.com/crunchtools/mcp-gemini.git
cd mcp-gemini
uv sync
```

### Run Tests

```bash
uv run pytest
```

### Lint and Type Check

```bash
uv run ruff check src tests
uv run mypy src
```

### Build Container

```bash
podman build -t mcp-gemini .
```

## License

AGPL-3.0-or-later

## Contributing

Contributions welcome! Please read SECURITY.md before submitting security-related changes.

## Links

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Google AI Studio](https://aistudio.google.com/)
- [FastMCP Documentation](https://gofastmcp.com/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [crunchtools.com](https://crunchtools.com)
