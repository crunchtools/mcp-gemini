# Baseline Specification: mcp-gemini-crunchtools

> **Spec ID:** 000-baseline
> **Status:** Implemented
> **Version:** 0.3.0

## Overview

mcp-gemini-crunchtools is a secure MCP server for the Google Gemini AI API. It provides 39 tools across 15 categories for text generation, image generation/editing/analysis, web search, document analysis, URL analysis, video generation, YouTube analysis, voice synthesis, deep research, content caching, structured output, token counting, and code execution.

---

## Tool Inventory

### Query (5 tools)

| Tool | SDK Method | Description |
|------|-----------|-------------|
| `gemini_query` | `generate_content` | General-purpose query with optional Google Search grounding |
| `gemini_brainstorm` | `generate_content` | Generate creative ideas on a topic |
| `gemini_analyze_code` | `generate_content` | Analyze code for security, performance, bugs |
| `gemini_analyze_text` | `generate_content` | Analyze text for sentiment, tone, content |
| `gemini_summarize` | `generate_content` | Summarize content in various formats |

### Image Generation (4 tools)

| Tool | SDK Method | Description |
|------|-----------|-------------|
| `gemini_generate_image` | `generate_content` | Generate images from text (native Gemini) |
| `gemini_generate_image_with_input` | `generate_content` | Edit/modify existing images |
| `gemini_image_prompt` | `generate_content` | Craft effective image generation prompts |
| `gemini_imagen_generate` | `generate_images` | Generate images via Imagen 4 models |

### Image Editing (4 tools)

| Tool | SDK Method | Description |
|------|-----------|-------------|
| `gemini_start_image_edit` | `create_chat` | Start multi-turn image editing session |
| `gemini_continue_image_edit` | `chat.send_message` | Continue editing in active session |
| `gemini_end_image_edit` | — | End session and free resources |
| `gemini_list_image_sessions` | — | List active editing sessions |

### Image Analysis (1 tool)

| Tool | SDK Method | Description |
|------|-----------|-------------|
| `gemini_analyze_image` | `generate_content` | Analyze and describe local image files |

### Search (1 tool)

| Tool | SDK Method | Description |
|------|-----------|-------------|
| `gemini_search` | `generate_content` | Web search with Google Search grounding |

### Document (3 tools)

| Tool | SDK Method | Description |
|------|-----------|-------------|
| `gemini_analyze_document` | `generate_content` + `upload_file` | Analyze PDFs, DOCX, TXT, etc. |
| `gemini_summarize_pdf` | (delegates to analyze_document) | Summarize PDF documents |
| `gemini_extract_tables` | (delegates to analyze_document) | Extract tables from documents |

### URL (3 tools)

| Tool | SDK Method | Description |
|------|-----------|-------------|
| `gemini_analyze_url` | `generate_content` | Analyze one or more URLs |
| `gemini_compare_urls` | (delegates to analyze_url) | Compare two URLs |
| `gemini_extract_from_url` | (delegates to analyze_url) | Extract specific data from a URL |

### Video (2 tools)

| Tool | SDK Method | Description |
|------|-----------|-------------|
| `gemini_generate_video` | `generate_videos` | Generate video using Veo |
| `gemini_check_video` | `get_videos_operation` | Check video generation status |

### YouTube (2 tools)

| Tool | SDK Method | Description |
|------|-----------|-------------|
| `gemini_youtube` | `generate_content` | Analyze YouTube videos |
| `gemini_youtube_summary` | (delegates to youtube) | Summarize YouTube videos |

### Voice (3 tools)

| Tool | SDK Method | Description |
|------|-----------|-------------|
| `gemini_speak` | `generate_content` (TTS) | Convert text to speech |
| `gemini_dialogue` | `generate_content` (TTS) | Generate multi-voice dialogue |
| `gemini_list_voices` | — | List available voice names |

### Research (3 tools)

| Tool | SDK Method | Description |
|------|-----------|-------------|
| `gemini_deep_research` | `generate_content` | Perform multi-step web research |
| `gemini_check_research` | — | Check research operation status |
| `gemini_research_followup` | `generate_content` | Ask follow-up questions |

### Cache (4 tools)

| Tool | SDK Method | Description |
|------|-----------|-------------|
| `gemini_create_cache` | `caches.create` | Create content cache for repeated queries |
| `gemini_query_cache` | `generate_content` | Query cached content |
| `gemini_list_caches` | `caches.list` | List all active caches |
| `gemini_delete_cache` | `caches.delete` | Delete a cache |

### Structured Output (2 tools)

| Tool | SDK Method | Description |
|------|-----------|-------------|
| `gemini_structured` | `generate_content` | Get structured JSON output |
| `gemini_extract` | (delegates to structured) | Extract structured data from text |

### Token (1 tool)

| Tool | SDK Method | Description |
|------|-----------|-------------|
| `gemini_count_tokens` | `count_tokens` | Count tokens in content |

### Code Execution (1 tool)

| Tool | SDK Method | Description |
|------|-----------|-------------|
| `gemini_run_code` | `generate_content` | Execute Python code via Gemini |

---

## Security Architecture

### Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `GEMINI_API_KEY` | Yes | — | Google Gemini API key |
| `GEMINI_OUTPUT_DIR` | No | `~/.config/mcp-gemini-crunchtools/output` | Generated file output |

### Error Hierarchy

```
UserError (base)
├── ConfigurationError
├── GeminiApiError (sanitizes API key from messages)
├── ImageGenerationError
├── ImageTooLargeError
├── FileNotFoundSafeError
├── InvalidFilePathError
├── SessionNotFoundError
├── RateLimitError
├── ValidationError
├── VideoGenerationError
├── ResearchError
└── CacheError
```

### Input Validation Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `VALID_ASPECT_RATIOS` | 10 values | Image aspect ratios |
| `VALID_IMAGE_SIZES` | 1K, 2K, 4K | Image output sizes |
| `VALID_IMAGEN_MODELS` | 3 models | Imagen 4 model names |
| `VALID_TEXT_MODELS` | 4 models | Text model shorthands |
| `MAX_IMAGE_SIZE_BYTES` | 20MB | Image upload limit |
| `MAX_DOCUMENT_SIZE_BYTES` | 100MB | Document upload limit |

---

## Module Structure

```
src/mcp_gemini_crunchtools/
├── __init__.py          # Entry point, argparse (stdio/sse/streamable-http)
├── __main__.py          # python -m entry point
├── _image_utils.py      # Image save/extract helpers
├── client.py            # google-genai SDK wrapper
├── config.py            # SecretStr config, output dir
├── errors.py            # Safe error hierarchy
├── models.py            # Input validation functions
├── server.py            # FastMCP tool registrations (39 tools)
└── tools/
    ├── __init__.py      # Re-exports all 39 functions
    ├── cache.py         # create, query, list, delete
    ├── code.py          # run_code
    ├── document.py      # analyze, summarize_pdf, extract_tables
    ├── image_analyze.py # analyze_image
    ├── image_edit.py    # start, continue, end, list_sessions
    ├── image_gen.py     # generate, with_input, prompt, imagen
    ├── query.py         # query, brainstorm, analyze_code/text, summarize
    ├── research.py      # deep_research, check, followup
    ├── search.py        # search
    ├── structured.py    # structured, extract
    ├── tokens.py        # count_tokens
    ├── url.py           # analyze, compare, extract_from
    ├── video.py         # generate, check
    ├── voice.py         # speak, dialogue, list_voices
    └── youtube.py       # youtube, youtube_summary
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-02-20 | Initial release: 39 tools |
| 0.1.1 | 2026-02-20 | Version sync fix |
| 0.3.0 | 2026-03-02 | v2 governance, comprehensive tests, gourmand, pre-commit |
