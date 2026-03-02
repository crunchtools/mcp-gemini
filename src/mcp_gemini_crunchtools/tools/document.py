"""Document analysis tools."""

import os
from typing import Any

from ..client import get_client
from ..models import MAX_DOCUMENT_SIZE_BYTES, validate_file_exists
from .query import _resolve_model


async def gemini_analyze_document(
    file_path: str,
    question: str = "Analyze this document and provide a summary.",
    model: str = "flash",
) -> dict[str, Any]:
    """Analyze a document (PDF, DOCX, TXT, etc.).

    For files over 20MB, uses the Gemini Files API for upload.

    Args:
        file_path: Absolute path to the document.
        question: Question or instruction about the document.
        model: Model to use.

    Returns:
        Analysis results.
    """
    file_path = validate_file_exists(file_path)
    client = get_client()
    model_name = _resolve_model(model)

    file_size = os.path.getsize(file_path)
    if file_size > MAX_DOCUMENT_SIZE_BYTES:
        msg = f"File too large ({file_size} bytes). Max: {MAX_DOCUMENT_SIZE_BYTES} bytes."
        raise ValueError(msg)

    uploaded_file = client.upload_file(file_path)
    response = client.generate_content(
        model=model_name, contents=[question, uploaded_file],
    )

    return {
        "response": response.text,
        "model": model_name,
        "file_path": file_path,
    }


async def gemini_summarize_pdf(
    file_path: str,
    style: str = "concise",
    model: str = "flash",
) -> dict[str, Any]:
    """Summarize a PDF document.

    Args:
        file_path: Absolute path to the PDF.
        style: Summary style (concise, detailed, executive).
        model: Model to use.

    Returns:
        Summary results.
    """
    prompt = f"Summarize this PDF document in a {style} style."
    return await gemini_analyze_document(
        file_path=file_path, question=prompt, model=model,
    )


async def gemini_extract_tables(
    file_path: str,
    output_format: str = "markdown",
    model: str = "flash",
) -> dict[str, Any]:
    """Extract tables from a document.

    Args:
        file_path: Absolute path to the document.
        output_format: Output format (markdown, csv, json).
        model: Model to use.

    Returns:
        Extracted tables.
    """
    prompt = (
        f"Extract all tables from this document and format them as {output_format}. "
        "Preserve the structure and data accurately."
    )
    return await gemini_analyze_document(
        file_path=file_path, question=prompt, model=model,
    )
