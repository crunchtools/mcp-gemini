"""Multi-turn image editing session tools."""

import time
import uuid
from typing import Any

from google.genai import types
from PIL import Image

from ..client import get_client
from ..errors import ImageGenerationError, SessionNotFoundError
from ..models import validate_file_exists
from .._image_utils import (
    extract_image_from_response,
    extract_text_from_response,
    save_generated_image,
)

# In-memory session store
_sessions: dict[str, dict[str, Any]] = {}
SESSION_TIMEOUT_SECONDS = 3600  # 1 hour


def _cleanup_stale_sessions() -> None:
    """Remove sessions older than timeout."""
    now = time.time()
    stale = [
        sid for sid, s in _sessions.items()
        if now - s["last_active"] > SESSION_TIMEOUT_SECONDS
    ]
    for sid in stale:
        del _sessions[sid]


async def gemini_start_image_edit(
    prompt: str,
    file_path: str | None = None,
    use_google_search: bool = False,
) -> dict[str, Any]:
    """Start a multi-turn image editing session.

    Optionally provide an existing image file as the starting point.
    Without a file_path, Gemini generates a new image from the prompt.

    Args:
        prompt: Initial prompt (describe the image or editing instructions).
        file_path: Optional absolute path to a local image to start from.
        use_google_search: Ground with Google Search results.

    Returns:
        Session ID, path to the generated image, and text response.
    """
    _cleanup_stale_sessions()
    client = get_client()

    session_id = f"edit-{uuid.uuid4().hex[:12]}"

    config_kwargs: dict[str, Any] = {
        "response_modalities": ["TEXT", "IMAGE"],
    }
    if use_google_search:
        config_kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]

    config = types.GenerateContentConfig(**config_kwargs)
    chat = client.create_chat(model="gemini-2.0-flash-exp", config=config)

    # Build initial message
    contents: list[Any] = [prompt]
    if file_path:
        file_path = validate_file_exists(file_path)
        contents.append(Image.open(file_path))

    response = chat.send_message(contents)

    image_data = extract_image_from_response(response)
    output_path = None
    if image_data:
        output_path = save_generated_image(
            image_data[0], client.output_dir, prefix="edit_start",
        )

    text = extract_text_from_response(response)

    _sessions[session_id] = {
        "chat": chat,
        "last_active": time.time(),
        "turn_count": 1,
        "images": [str(output_path)] if output_path else [],
    }

    return {
        "session_id": session_id,
        "image_path": str(output_path) if output_path else None,
        "text": text,
        "turn_count": 1,
    }


async def gemini_continue_image_edit(
    session_id: str,
    prompt: str,
) -> dict[str, Any]:
    """Continue editing in an active session.

    Args:
        session_id: The session ID returned from gemini_start_image_edit.
        prompt: Editing instructions (e.g., "make the sky bluer").

    Returns:
        Path to the updated image and text response.
    """
    _cleanup_stale_sessions()

    if session_id not in _sessions:
        raise SessionNotFoundError(session_id)

    session = _sessions[session_id]
    chat = session["chat"]

    response = chat.send_message([prompt])

    image_data = extract_image_from_response(response)
    output_path = None
    if image_data:
        client = get_client()
        output_path = save_generated_image(
            image_data[0], client.output_dir, prefix="edit_continue",
        )
        session["images"].append(str(output_path))

    text = extract_text_from_response(response)
    session["last_active"] = time.time()
    session["turn_count"] += 1

    return {
        "session_id": session_id,
        "image_path": str(output_path) if output_path else None,
        "text": text,
        "turn_count": session["turn_count"],
    }


async def gemini_end_image_edit(
    session_id: str,
) -> dict[str, Any]:
    """End an image editing session and free resources.

    Args:
        session_id: The session ID to end.

    Returns:
        Summary of the session.
    """
    if session_id not in _sessions:
        raise SessionNotFoundError(session_id)

    session = _sessions.pop(session_id)
    return {
        "session_id": session_id,
        "status": "ended",
        "total_turns": session["turn_count"],
        "images_generated": session["images"],
    }


async def gemini_list_image_sessions() -> dict[str, Any]:
    """List all active image editing sessions.

    Returns:
        List of active sessions with metadata.
    """
    _cleanup_stale_sessions()

    sessions = []
    for sid, session in _sessions.items():
        sessions.append({
            "session_id": sid,
            "turn_count": session["turn_count"],
            "image_count": len(session["images"]),
            "last_active_seconds_ago": int(time.time() - session["last_active"]),
        })

    return {"sessions": sessions, "count": len(sessions)}
