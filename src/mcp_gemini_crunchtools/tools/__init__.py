"""Tool implementations for mcp-gemini-crunchtools.

All tool functions are imported here for convenient access from server.py.
"""

from .cache import (
    gemini_create_cache,
    gemini_delete_cache,
    gemini_list_caches,
    gemini_query_cache,
)
from .code import gemini_run_code
from .document import (
    gemini_analyze_document,
    gemini_extract_tables,
    gemini_summarize_pdf,
)
from .image_analyze import gemini_analyze_image
from .image_edit import (
    gemini_continue_image_edit,
    gemini_end_image_edit,
    gemini_list_image_sessions,
    gemini_start_image_edit,
)
from .image_gen import (
    gemini_generate_image,
    gemini_generate_image_with_input,
    gemini_image_prompt,
    gemini_imagen_generate,
)
from .query import (
    gemini_analyze_code,
    gemini_analyze_text,
    gemini_brainstorm,
    gemini_query,
    gemini_summarize,
)
from .research import (
    gemini_check_research,
    gemini_deep_research,
    gemini_research_followup,
)
from .search import gemini_search
from .structured import gemini_extract, gemini_structured
from .tokens import gemini_count_tokens
from .url import (
    gemini_analyze_url,
    gemini_compare_urls,
    gemini_extract_from_url,
)
from .video import gemini_check_video, gemini_generate_video
from .voice import gemini_dialogue, gemini_list_voices, gemini_speak
from .youtube import gemini_youtube, gemini_youtube_summary

__all__ = [
    "gemini_analyze_code",
    "gemini_analyze_document",
    "gemini_analyze_image",
    "gemini_analyze_text",
    "gemini_analyze_url",
    "gemini_brainstorm",
    "gemini_check_research",
    "gemini_check_video",
    "gemini_compare_urls",
    "gemini_continue_image_edit",
    "gemini_count_tokens",
    "gemini_create_cache",
    "gemini_deep_research",
    "gemini_delete_cache",
    "gemini_dialogue",
    "gemini_end_image_edit",
    "gemini_extract",
    "gemini_extract_from_url",
    "gemini_extract_tables",
    "gemini_generate_image",
    "gemini_generate_image_with_input",
    "gemini_generate_video",
    "gemini_image_prompt",
    "gemini_imagen_generate",
    "gemini_list_caches",
    "gemini_list_image_sessions",
    "gemini_list_voices",
    "gemini_query",
    "gemini_query_cache",
    "gemini_research_followup",
    "gemini_run_code",
    "gemini_search",
    "gemini_speak",
    "gemini_start_image_edit",
    "gemini_structured",
    "gemini_summarize",
    "gemini_summarize_pdf",
    "gemini_youtube",
    "gemini_youtube_summary",
]
