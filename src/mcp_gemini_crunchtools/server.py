"""FastMCP server setup for Gemini MCP.

This module creates and configures the MCP server with all tools.
"""

import logging
from typing import Any

from fastmcp import FastMCP

from .tools import (
    # Query
    gemini_analyze_code,
    gemini_analyze_text,
    gemini_brainstorm,
    gemini_query,
    gemini_summarize,
    # Image generation
    gemini_generate_image,
    gemini_generate_image_with_input,
    gemini_image_prompt,
    gemini_imagen_generate,
    # Image editing
    gemini_continue_image_edit,
    gemini_end_image_edit,
    gemini_list_image_sessions,
    gemini_start_image_edit,
    # Image analysis
    gemini_analyze_image,
    # Search
    gemini_search,
    # Document
    gemini_analyze_document,
    gemini_extract_tables,
    gemini_summarize_pdf,
    # URL
    gemini_analyze_url,
    gemini_compare_urls,
    gemini_extract_from_url,
    # Video
    gemini_check_video,
    gemini_generate_video,
    # YouTube
    gemini_youtube,
    gemini_youtube_summary,
    # Voice
    gemini_dialogue,
    gemini_list_voices,
    gemini_speak,
    # Research
    gemini_check_research,
    gemini_deep_research,
    gemini_research_followup,
    # Cache
    gemini_create_cache,
    gemini_delete_cache,
    gemini_list_caches,
    gemini_query_cache,
    # Structured
    gemini_extract,
    gemini_structured,
    # Tokens
    gemini_count_tokens,
    # Code
    gemini_run_code,
)

logger = logging.getLogger(__name__)

# Create the FastMCP server
mcp = FastMCP(
    name="mcp-gemini-crunchtools",
    version="0.1.0",
    instructions="MCP server for Google Gemini AI - text, image, video, research, and more",
)


# ============================================================
# Query Tools
# ============================================================


@mcp.tool()
async def gemini_query_tool(
    prompt: str,
    model: str = "flash",
    use_google_search: bool = False,
    system_instruction: str | None = None,
) -> dict[str, Any]:
    """Query Gemini with a prompt. Supports Google Search grounding.

    Args:
        prompt: The prompt to send to Gemini.
        model: Model to use ('pro' or 'flash').
        use_google_search: Ground response with Google Search results.
        system_instruction: Optional system instruction to guide the response.
    """
    return await gemini_query(
        prompt=prompt, model=model,
        use_google_search=use_google_search,
        system_instruction=system_instruction,
    )


@mcp.tool()
async def gemini_brainstorm_tool(
    topic: str,
    context: str | None = None,
    num_ideas: int = 5,
    model: str = "flash",
) -> dict[str, Any]:
    """Brainstorm ideas on a topic using Gemini.

    Args:
        topic: The topic to brainstorm about.
        context: Additional context or constraints.
        num_ideas: Number of ideas to generate.
        model: Model to use.
    """
    return await gemini_brainstorm(
        topic=topic, context=context, num_ideas=num_ideas, model=model,
    )


@mcp.tool()
async def gemini_analyze_code_tool(
    code: str,
    language: str | None = None,
    focus: str = "general",
    model: str = "pro",
) -> dict[str, Any]:
    """Analyze code with Gemini.

    Args:
        code: The code to analyze.
        language: Programming language (auto-detected if not specified).
        focus: Analysis focus (general, security, performance, bugs).
        model: Model to use.
    """
    return await gemini_analyze_code(
        code=code, language=language, focus=focus, model=model,
    )


@mcp.tool()
async def gemini_analyze_text_tool(
    text: str,
    analysis_type: str = "general",
    model: str = "flash",
) -> dict[str, Any]:
    """Analyze text with Gemini.

    Args:
        text: The text to analyze.
        analysis_type: Type of analysis (general, sentiment, tone, summary).
        model: Model to use.
    """
    return await gemini_analyze_text(
        text=text, analysis_type=analysis_type, model=model,
    )


@mcp.tool()
async def gemini_summarize_tool(
    content: str,
    format: str = "paragraph",
    length: str = "moderate",
    model: str = "flash",
) -> dict[str, Any]:
    """Summarize content with Gemini.

    Args:
        content: The content to summarize.
        format: Output format (paragraph, bullets, outline).
        length: Summary length (brief, moderate, detailed).
        model: Model to use.
    """
    return await gemini_summarize(
        content=content, format=format, length=length, model=model,
    )


# ============================================================
# Image Generation Tools
# ============================================================


@mcp.tool()
async def gemini_generate_image_tool(
    prompt: str,
    aspect_ratio: str = "1:1",
    image_size: str = "2K",
    style: str | None = None,
    use_google_search: bool = False,
) -> dict[str, Any]:
    """Generate an image from a text prompt using Gemini's native image model.

    Args:
        prompt: Description of the image to generate.
        aspect_ratio: Aspect ratio (1:1, 2:3, 3:2, 3:4, 4:3, 9:16, 16:9, etc).
        image_size: Output size (1K, 2K, 4K).
        style: Optional style modifier (photorealistic, cartoon, watercolor, etc).
        use_google_search: Ground with Google Search results.
    """
    return await gemini_generate_image(
        prompt=prompt, aspect_ratio=aspect_ratio,
        image_size=image_size, style=style,
        use_google_search=use_google_search,
    )


@mcp.tool()
async def gemini_generate_image_with_input_tool(
    prompt: str,
    file_path: str,
    aspect_ratio: str = "1:1",
) -> dict[str, Any]:
    """Generate/edit an image using a local image file as input.

    Upload a local image and give Gemini instructions for how to modify it.
    Use cases: add watermarks, change styles, composite images, etc.

    Args:
        prompt: Instructions for what to do with the input image.
        file_path: Absolute path to a local image file.
        aspect_ratio: Desired aspect ratio for the output.
    """
    return await gemini_generate_image_with_input(
        prompt=prompt, file_path=file_path, aspect_ratio=aspect_ratio,
    )


@mcp.tool()
async def gemini_image_prompt_tool(
    description: str,
    style: str | None = None,
    mood: str | None = None,
    model: str = "flash",
) -> dict[str, Any]:
    """Help craft an effective image generation prompt.

    Args:
        description: What you want the image to show.
        style: Desired art style (photorealistic, cartoon, watercolor, etc).
        mood: Desired mood or atmosphere.
        model: Model to use for prompt crafting.
    """
    return await gemini_image_prompt(
        description=description, style=style, mood=mood, model=model,
    )


@mcp.tool()
async def gemini_imagen_generate_tool(
    prompt: str,
    model: str = "imagen-4.0-generate-001",
    number_of_images: int = 1,
    aspect_ratio: str = "1:1",
) -> dict[str, Any]:
    """Generate images using Google Imagen 4 models.

    Models (sorted by price):
    - imagen-4.0-fast-generate-001 ($0.02/image, fastest)
    - imagen-4.0-generate-001 ($0.04/image, standard)
    - imagen-4.0-ultra-generate-001 ($0.06/image, highest quality)

    Args:
        prompt: Description of the image to generate.
        model: Imagen model to use.
        number_of_images: Number of images to generate (1-4).
        aspect_ratio: Aspect ratio (1:1, 3:4, 4:3, 9:16, 16:9).
    """
    return await gemini_imagen_generate(
        prompt=prompt, model=model,
        number_of_images=number_of_images,
        aspect_ratio=aspect_ratio,
    )


# ============================================================
# Image Editing Tools
# ============================================================


@mcp.tool()
async def gemini_start_image_edit_tool(
    prompt: str,
    file_path: str | None = None,
    use_google_search: bool = False,
) -> dict[str, Any]:
    """Start a multi-turn image editing session.

    Optionally provide an existing image file as the starting point.
    Without file_path, Gemini generates a new image from the prompt.
    Use gemini_continue_image_edit_tool to make further edits.

    Args:
        prompt: Initial prompt (describe image or editing instructions).
        file_path: Optional absolute path to a local image to start from.
        use_google_search: Ground with Google Search results.
    """
    return await gemini_start_image_edit(
        prompt=prompt, file_path=file_path,
        use_google_search=use_google_search,
    )


@mcp.tool()
async def gemini_continue_image_edit_tool(
    session_id: str,
    prompt: str,
) -> dict[str, Any]:
    """Continue editing in an active image session.

    Args:
        session_id: The session ID from gemini_start_image_edit.
        prompt: Editing instructions (e.g., "make the sky bluer").
    """
    return await gemini_continue_image_edit(
        session_id=session_id, prompt=prompt,
    )


@mcp.tool()
async def gemini_end_image_edit_tool(
    session_id: str,
) -> dict[str, Any]:
    """End an image editing session and free resources.

    Args:
        session_id: The session ID to end.
    """
    return await gemini_end_image_edit(session_id=session_id)


@mcp.tool()
async def gemini_list_image_sessions_tool() -> dict[str, Any]:
    """List all active image editing sessions."""
    return await gemini_list_image_sessions()


# ============================================================
# Image Analysis Tools
# ============================================================


@mcp.tool()
async def gemini_analyze_image_tool(
    image_path: str,
    query: str = "Describe this image in detail.",
    model: str = "flash",
) -> dict[str, Any]:
    """Analyze and describe a local image file.

    Args:
        image_path: Absolute path to the image file.
        query: Question or instruction about the image.
        model: Model to use ('pro' or 'flash').
    """
    return await gemini_analyze_image(
        image_path=image_path, query=query, model=model,
    )


# ============================================================
# Search Tools
# ============================================================


@mcp.tool()
async def gemini_search_tool(
    query: str,
    model: str = "flash",
) -> dict[str, Any]:
    """Search the web using Gemini with Google Search grounding.

    Args:
        query: The search query.
        model: Model to use.
    """
    return await gemini_search(query=query, model=model)


# ============================================================
# Document Tools
# ============================================================


@mcp.tool()
async def gemini_analyze_document_tool(
    file_path: str,
    question: str = "Analyze this document and provide a summary.",
    model: str = "flash",
) -> dict[str, Any]:
    """Analyze a document (PDF, DOCX, TXT, etc.).

    Args:
        file_path: Absolute path to the document.
        question: Question or instruction about the document.
        model: Model to use.
    """
    return await gemini_analyze_document(
        file_path=file_path, question=question, model=model,
    )


@mcp.tool()
async def gemini_summarize_pdf_tool(
    file_path: str,
    style: str = "concise",
    model: str = "flash",
) -> dict[str, Any]:
    """Summarize a PDF document.

    Args:
        file_path: Absolute path to the PDF.
        style: Summary style (concise, detailed, executive).
        model: Model to use.
    """
    return await gemini_summarize_pdf(
        file_path=file_path, style=style, model=model,
    )


@mcp.tool()
async def gemini_extract_tables_tool(
    file_path: str,
    output_format: str = "markdown",
    model: str = "flash",
) -> dict[str, Any]:
    """Extract tables from a document.

    Args:
        file_path: Absolute path to the document.
        output_format: Output format (markdown, csv, json).
        model: Model to use.
    """
    return await gemini_extract_tables(
        file_path=file_path, output_format=output_format, model=model,
    )


# ============================================================
# URL Tools
# ============================================================


@mcp.tool()
async def gemini_analyze_url_tool(
    urls: list[str],
    question: str = "Analyze the content of these URLs.",
    use_google_search: bool = True,
    model: str = "flash",
) -> dict[str, Any]:
    """Analyze one or more URLs.

    Args:
        urls: List of URLs to analyze (1-20).
        question: Question or instruction about the URL content.
        use_google_search: Use Google Search grounding.
        model: Model to use.
    """
    return await gemini_analyze_url(
        urls=urls, question=question,
        use_google_search=use_google_search, model=model,
    )


@mcp.tool()
async def gemini_compare_urls_tool(
    url1: str,
    url2: str,
    aspect: str = "content",
    model: str = "flash",
) -> dict[str, Any]:
    """Compare two URLs.

    Args:
        url1: First URL.
        url2: Second URL.
        aspect: What to compare (content, design, sentiment, features).
        model: Model to use.
    """
    return await gemini_compare_urls(
        url1=url1, url2=url2, aspect=aspect, model=model,
    )


@mcp.tool()
async def gemini_extract_from_url_tool(
    url: str,
    data_type: str = "text",
    custom_fields: str | None = None,
    model: str = "flash",
) -> dict[str, Any]:
    """Extract specific data from a URL.

    Args:
        url: URL to extract data from.
        data_type: Type of data (text, links, images, structured).
        custom_fields: Comma-separated list of custom fields to extract.
        model: Model to use.
    """
    return await gemini_extract_from_url(
        url=url, data_type=data_type,
        custom_fields=custom_fields, model=model,
    )


# ============================================================
# Video Tools
# ============================================================


@mcp.tool()
async def gemini_generate_video_tool(
    prompt: str,
    aspect_ratio: str = "16:9",
    negative_prompt: str | None = None,
) -> dict[str, Any]:
    """Generate a video using Veo. Returns an operation ID to poll.

    Args:
        prompt: Description of the video to generate.
        aspect_ratio: Video aspect ratio.
        negative_prompt: What to avoid in the video.
    """
    return await gemini_generate_video(
        prompt=prompt, aspect_ratio=aspect_ratio,
        negative_prompt=negative_prompt,
    )


@mcp.tool()
async def gemini_check_video_tool(
    operation_name: str,
) -> dict[str, Any]:
    """Check the status of a video generation operation.

    Args:
        operation_name: The operation name from gemini_generate_video.
    """
    return await gemini_check_video(operation_name=operation_name)


# ============================================================
# YouTube Tools
# ============================================================


@mcp.tool()
async def gemini_youtube_tool(
    url: str,
    question: str = "Analyze this video and provide key insights.",
    model: str = "flash",
) -> dict[str, Any]:
    """Analyze a YouTube video.

    Args:
        url: YouTube video URL.
        question: Question or instruction about the video.
        model: Model to use.
    """
    return await gemini_youtube(url=url, question=question, model=model)


@mcp.tool()
async def gemini_youtube_summary_tool(
    url: str,
    style: str = "concise",
    model: str = "flash",
) -> dict[str, Any]:
    """Summarize a YouTube video.

    Args:
        url: YouTube video URL.
        style: Summary style (concise, detailed, bullet_points).
        model: Model to use.
    """
    return await gemini_youtube_summary(url=url, style=style, model=model)


# ============================================================
# Voice Tools
# ============================================================


@mcp.tool()
async def gemini_speak_tool(
    text: str,
    voice: str = "Kore",
) -> dict[str, Any]:
    """Convert text to speech.

    Args:
        text: Text to convert to speech.
        voice: Voice name (Zephyr, Puck, Charon, Kore, Fenrir, Leda, Orus, Aoede).
    """
    return await gemini_speak(text=text, voice=voice)


@mcp.tool()
async def gemini_dialogue_tool(
    text: str,
    voice1: str = "Kore",
    voice2: str = "Puck",
) -> dict[str, Any]:
    """Generate multi-voice dialogue audio.

    Args:
        text: Dialogue text with speaker labels.
        voice1: First voice name.
        voice2: Second voice name.
    """
    return await gemini_dialogue(text=text, voice1=voice1, voice2=voice2)


@mcp.tool()
async def gemini_list_voices_tool() -> dict[str, Any]:
    """List available voices for text-to-speech."""
    return await gemini_list_voices()


# ============================================================
# Research Tools
# ============================================================


@mcp.tool()
async def gemini_deep_research_tool(
    query: str,
) -> dict[str, Any]:
    """Start a deep research task using a specialized Gemini model.

    Performs multi-step web research to answer complex questions.

    Args:
        query: The research question or topic.
    """
    return await gemini_deep_research(query=query)


@mcp.tool()
async def gemini_check_research_tool(
    research_id: str,
) -> dict[str, Any]:
    """Check the status of a deep research operation.

    Args:
        research_id: The research ID from gemini_deep_research.
    """
    return await gemini_check_research(research_id=research_id)


@mcp.tool()
async def gemini_research_followup_tool(
    research_id: str,
    question: str,
) -> dict[str, Any]:
    """Ask a follow-up question about completed research.

    Args:
        research_id: The research ID from a previous research operation.
        question: Follow-up question.
    """
    return await gemini_research_followup(
        research_id=research_id, question=question,
    )


# ============================================================
# Cache Tools
# ============================================================


@mcp.tool()
async def gemini_create_cache_tool(
    file_path: str | None = None,
    content: str | None = None,
    display_name: str = "mcp-cache",
    system_instruction: str | None = None,
    ttl_minutes: int = 60,
    model: str = "flash",
) -> dict[str, Any]:
    """Create a content cache for repeated queries.

    Upload content once and query it multiple times without re-sending.

    Args:
        file_path: Path to a file to cache.
        content: Text content to cache (alternative to file_path).
        display_name: Human-readable name for the cache.
        system_instruction: System instruction for queries against this cache.
        ttl_minutes: Time-to-live in minutes (default 60).
        model: Model to use.
    """
    return await gemini_create_cache(
        file_path=file_path, content=content,
        display_name=display_name,
        system_instruction=system_instruction,
        ttl_minutes=ttl_minutes, model=model,
    )


@mcp.tool()
async def gemini_query_cache_tool(
    cache_name: str,
    question: str,
) -> dict[str, Any]:
    """Query content in a cache.

    Args:
        cache_name: The cache name from gemini_create_cache.
        question: Question to ask about the cached content.
    """
    return await gemini_query_cache(
        cache_name=cache_name, question=question,
    )


@mcp.tool()
async def gemini_list_caches_tool() -> dict[str, Any]:
    """List all active content caches."""
    return await gemini_list_caches()


@mcp.tool()
async def gemini_delete_cache_tool(
    cache_name: str,
) -> dict[str, Any]:
    """Delete a content cache.

    Args:
        cache_name: The cache name to delete.
    """
    return await gemini_delete_cache(cache_name=cache_name)


# ============================================================
# Structured Output Tools
# ============================================================


@mcp.tool()
async def gemini_structured_tool(
    prompt: str,
    schema: dict[str, Any] | None = None,
    use_google_search: bool = False,
    model: str = "flash",
) -> dict[str, Any]:
    """Get structured JSON output from Gemini.

    Args:
        prompt: The prompt to generate structured output for.
        schema: Optional JSON schema to constrain the output.
        use_google_search: Ground response with Google Search.
        model: Model to use.
    """
    return await gemini_structured(
        prompt=prompt, schema=schema,
        use_google_search=use_google_search, model=model,
    )


@mcp.tool()
async def gemini_extract_tool(
    text: str,
    extract_type: str = "entities",
    custom_fields: str | None = None,
    model: str = "flash",
) -> dict[str, Any]:
    """Extract structured data from text.

    Args:
        text: Text to extract data from.
        extract_type: Type (entities, dates, numbers, contacts, custom).
        custom_fields: Comma-separated list of custom fields to extract.
        model: Model to use.
    """
    return await gemini_extract(
        text=text, extract_type=extract_type,
        custom_fields=custom_fields, model=model,
    )


# ============================================================
# Token Tools
# ============================================================


@mcp.tool()
async def gemini_count_tokens_tool(
    content: str,
    model: str = "flash",
) -> dict[str, Any]:
    """Count the number of tokens in content.

    Args:
        content: The text content to count tokens for.
        model: Model to count tokens for.
    """
    return await gemini_count_tokens(content=content, model=model)


# ============================================================
# Code Execution Tools
# ============================================================


@mcp.tool()
async def gemini_run_code_tool(
    prompt: str,
    data: str | None = None,
    model: str = "flash",
) -> dict[str, Any]:
    """Execute code using Gemini's built-in code execution.

    Gemini writes and runs Python code to answer questions,
    perform calculations, or process data.

    Args:
        prompt: Description of what code to write and run.
        data: Optional data to process.
        model: Model to use.
    """
    return await gemini_run_code(prompt=prompt, data=data, model=model)
