"""Tool implementations for mcp-gemini-crunchtools.

All tool functions are imported here for convenient access from server.py.
"""

# Query tools
from .query import (
    gemini_analyze_code,
    gemini_analyze_text,
    gemini_brainstorm,
    gemini_query,
    gemini_summarize,
)

# Image generation tools
from .image_gen import (
    gemini_generate_image,
    gemini_generate_image_with_input,
    gemini_image_prompt,
    gemini_imagen_generate,
)

# Image editing tools
from .image_edit import (
    gemini_continue_image_edit,
    gemini_end_image_edit,
    gemini_list_image_sessions,
    gemini_start_image_edit,
)

# Image analysis tools
from .image_analyze import gemini_analyze_image

# Search tools
from .search import gemini_search

# Document tools
from .document import (
    gemini_analyze_document,
    gemini_extract_tables,
    gemini_summarize_pdf,
)

# URL tools
from .url import (
    gemini_analyze_url,
    gemini_compare_urls,
    gemini_extract_from_url,
)

# Video tools
from .video import gemini_check_video, gemini_generate_video

# YouTube tools
from .youtube import gemini_youtube, gemini_youtube_summary

# Voice tools
from .voice import gemini_dialogue, gemini_list_voices, gemini_speak

# Research tools
from .research import (
    gemini_check_research,
    gemini_deep_research,
    gemini_research_followup,
)

# Cache tools
from .cache import (
    gemini_create_cache,
    gemini_delete_cache,
    gemini_list_caches,
    gemini_query_cache,
)

# Structured output tools
from .structured import gemini_extract, gemini_structured

# Token tools
from .tokens import gemini_count_tokens

# Code tools
from .code import gemini_run_code

__all__ = [
    # Query
    "gemini_query",
    "gemini_brainstorm",
    "gemini_analyze_code",
    "gemini_analyze_text",
    "gemini_summarize",
    # Image generation
    "gemini_generate_image",
    "gemini_generate_image_with_input",
    "gemini_image_prompt",
    "gemini_imagen_generate",
    # Image editing
    "gemini_start_image_edit",
    "gemini_continue_image_edit",
    "gemini_end_image_edit",
    "gemini_list_image_sessions",
    # Image analysis
    "gemini_analyze_image",
    # Search
    "gemini_search",
    # Document
    "gemini_analyze_document",
    "gemini_summarize_pdf",
    "gemini_extract_tables",
    # URL
    "gemini_analyze_url",
    "gemini_compare_urls",
    "gemini_extract_from_url",
    # Video
    "gemini_generate_video",
    "gemini_check_video",
    # YouTube
    "gemini_youtube",
    "gemini_youtube_summary",
    # Voice
    "gemini_speak",
    "gemini_dialogue",
    "gemini_list_voices",
    # Research
    "gemini_deep_research",
    "gemini_check_research",
    "gemini_research_followup",
    # Cache
    "gemini_create_cache",
    "gemini_query_cache",
    "gemini_list_caches",
    "gemini_delete_cache",
    # Structured
    "gemini_structured",
    "gemini_extract",
    # Tokens
    "gemini_count_tokens",
    # Code
    "gemini_run_code",
]
