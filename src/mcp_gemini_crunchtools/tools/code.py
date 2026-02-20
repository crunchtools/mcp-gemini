"""Code execution tool using Gemini's code execution capability."""

from typing import Any

from google.genai import types

from ..client import get_client
from .query import _resolve_model


async def gemini_run_code(
    prompt: str,
    data: str | None = None,
    model: str = "flash",
) -> dict[str, Any]:
    """Execute code using Gemini's built-in code execution.

    Gemini can write and run Python code to answer questions,
    perform calculations, or process data.

    Args:
        prompt: Description of what code to write and run.
        data: Optional data to process.
        model: Model to use.

    Returns:
        Code execution results.
    """
    client = get_client()
    model_name = _resolve_model(model)

    full_prompt = prompt
    if data:
        full_prompt = f"{prompt}\n\nData:\n{data}"

    config = types.GenerateContentConfig(
        tools=[types.Tool(code_execution=types.ToolCodeExecution())],
    )

    response = client.generate_content(
        model=model_name, contents=[full_prompt], config=config,
    )

    return {"response": response.text, "model": model_name}
