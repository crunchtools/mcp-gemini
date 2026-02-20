"""Query tools for general text interaction with Gemini."""

from typing import Any

from google.genai import types

from ..client import get_client

# Model name mapping
# Using latest stable Gemini 2.5 models
MODEL_MAP: dict[str, str] = {
    "pro": "gemini-2.5-pro",
    "flash": "gemini-2.5-flash",
}


def _resolve_model(model: str) -> str:
    """Resolve a model shorthand to a full model name."""
    return MODEL_MAP.get(model, model)


async def gemini_query(
    prompt: str,
    model: str = "flash",
    use_google_search: bool = False,
    system_instruction: str | None = None,
) -> dict[str, Any]:
    """General-purpose query to Gemini.

    Args:
        prompt: The prompt to send.
        model: Model to use ('pro' or 'flash', or full model name).
        use_google_search: Ground response with Google Search results.
        system_instruction: Optional system instruction.

    Returns:
        Response text and metadata.
    """
    client = get_client()
    model_name = _resolve_model(model)

    config_kwargs: dict[str, Any] = {}
    if use_google_search:
        config_kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction

    config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

    response = client.generate_content(
        model=model_name, contents=[prompt], config=config,
    )
    return {"response": response.text, "model": model_name}


async def gemini_brainstorm(
    topic: str,
    context: str | None = None,
    num_ideas: int = 5,
    model: str = "flash",
) -> dict[str, Any]:
    """Brainstorm ideas on a topic.

    Args:
        topic: The topic to brainstorm about.
        context: Additional context or constraints.
        num_ideas: Number of ideas to generate.
        model: Model to use.

    Returns:
        Brainstorming results.
    """
    client = get_client()
    model_name = _resolve_model(model)

    prompt = f"Brainstorm {num_ideas} creative ideas about: {topic}"
    if context:
        prompt += f"\n\nContext: {context}"

    response = client.generate_content(model=model_name, contents=[prompt])
    return {"response": response.text, "model": model_name, "topic": topic}


async def gemini_analyze_code(
    code: str,
    language: str | None = None,
    focus: str = "general",
    model: str = "pro",
) -> dict[str, Any]:
    """Analyze code with Gemini.

    Args:
        code: The code to analyze.
        language: Programming language.
        focus: Analysis focus (general, security, performance, bugs).
        model: Model to use.

    Returns:
        Code analysis results.
    """
    client = get_client()
    model_name = _resolve_model(model)

    prompt = f"Analyze the following code"
    if language:
        prompt += f" ({language})"
    prompt += f" with focus on {focus}:\n\n```\n{code}\n```"

    response = client.generate_content(model=model_name, contents=[prompt])
    return {"response": response.text, "model": model_name, "focus": focus}


async def gemini_analyze_text(
    text: str,
    analysis_type: str = "general",
    model: str = "flash",
) -> dict[str, Any]:
    """Analyze text with Gemini.

    Args:
        text: The text to analyze.
        analysis_type: Type of analysis (general, sentiment, tone, summary).
        model: Model to use.

    Returns:
        Text analysis results.
    """
    client = get_client()
    model_name = _resolve_model(model)

    prompt = f"Perform {analysis_type} analysis on the following text:\n\n{text}"

    response = client.generate_content(model=model_name, contents=[prompt])
    return {"response": response.text, "model": model_name, "analysis_type": analysis_type}


async def gemini_summarize(
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

    Returns:
        Summary results.
    """
    client = get_client()
    model_name = _resolve_model(model)

    prompt = (
        f"Summarize the following content in {format} format. "
        f"Length: {length}.\n\n{content}"
    )

    response = client.generate_content(model=model_name, contents=[prompt])
    return {"response": response.text, "model": model_name, "format": format}
